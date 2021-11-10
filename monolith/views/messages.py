import bleach
import json
from flask import Blueprint, redirect, render_template, request, abort
from flask_login import current_user
from better_profanity import profanity

from .users import get_users

from ..access import Access
from ..auth import login_required
from ..background import notify
from ..utils import get_argument

from monolith.database import User, Message, BlackList, db
from monolith.forms import MessageForm


messages = Blueprint('messages', __name__)

allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                'h1', 'h2', 'h3', 'img', 'video','p', 'div', 'iframe',
                'br', 'span', 'hr', 'src', 'class','font','u']

allowed_attrs = {'*': ['class','style','color'],
                 'a': ['href', 'rel'],
                 'img': ['src', 'alt','data-filename','style']}


# profanity filter ('en' only)
profanity.load_censor_words()


ATTACHMENTS_PATH = 'monolith/static'


@messages.errorhandler(404)
def page_not_found(error):
    '''Custom error handler for 404 Not Found error.'''
    return render_template('/error.html', error=error), 404


def is_blocked(recipient):
    '''Utility function for checking if recipient has sender on blacklist.'''
    recipient_id = (db.session.query(User).filter(User.id == recipient).first()).id
    # get list of blocked users ids
    _blocked_users = [r.id_blocked for r in db.session.query(BlackList.id_blocked).filter(BlackList.id_user == recipient_id)]
    return current_user.id in _blocked_users


def filter_language(_message):
    '''Utility function for censoring bad language in received messages.'''
    return {
        'text': profanity.censor(_message.text),  # Censorship.
        'delivery_date': _message.delivery_date,
        'recipient_id': _message.recipient_id,
        'sender': _message.sender,
        'recipient': _message.recipient,
        'is_draft': _message.is_draft,
        'is_delivered': _message.is_delivered
    }


def retrieve_message(message_id):
    '''Utility function for retrieving a message with a message id.'''
    _message = db.session.query(Message).filter(Message.id == message_id).first()
    if _message is None:
        error = 'Message not found!'
        abort(404, error)
    return _message


def is_sender_or_recipient(message, user_id):
    '''Utility function for checking if the current user
       is allowed to read the message.
    '''
    is_sender = message.sender_id == user_id
    is_recipient = message.recipient_id == user_id

    '''The recipient can access the message if:
       - it has the access rights for the message, and
       - the message is not a draft, and
       - the message is delivered or the recipient is the sender.
    '''
    recipient_authorized = (
        message.access & Access.RECIPIENT.value
        and not message.is_draft
        and (message.is_delivered or is_sender)
    )

    if (not (is_sender or is_recipient)
        or (is_sender and not message.access & Access.SENDER.value)
        or (is_recipient and not recipient_authorized)
       ):
        error = 'Message not found!'
        abort(404, error)


@messages.route('/schedule')
@login_required
def schedule():
    '''Display the list of user's messages scheduled to be sent.

       GET: show the list of messages
    '''
    # Retrieve user <id>
    id = current_user.get_id()

    # Retrieve scheduled messages of user <id> that will be sent in the future
    scheduled_messages = db.session.query(Message).filter(
        Message.sender_id==id,
        Message.access.op('&')(Access.SENDER.value),
        ~Message.is_draft,
        ~Message.is_delivered
    )

    return render_template('schedule.html', scheduled_messages=scheduled_messages)


@messages.route('/mailbox')
@login_required
def mailbox():
    '''Manage the user's sent and received messages, aswell as the drafts.

       GET: display the list of drafts, sent and received messages
       POST: perform an action on drafts and messages
             if <message> in <sent_messages> AND <To> button is clicked: display information about the recipient
             if <message> in <received_messages> AND <From> button is clicked: display information about the sender
             if <message> in <draft_messages>
             if <Edit> button is clicked: allows to edit the message text, delivery_date and recipients
             if <View> button is clicked: display the message information
    '''
    # Retrieve user <id>
    id = current_user.get_id()

    # Retrieve sent messages of user <id>
    sent_messages = db.session.query(Message).filter(
        Message.sender_id == id,
        Message.access.op('&')(Access.SENDER.value),
        ~Message.is_draft,
        Message.is_delivered
    )

    # Retrieve received messages of user <id>
    received_messages = db.session.query(Message).filter(
        Message.recipient_id == id,
        Message.access.op('&')(Access.RECIPIENT.value),
        Message.is_delivered
    )

    # Retrieve draft messages of user <id>
    draft_messages = db.session.query(Message).filter(
        Message.sender_id == id,
        Message.access.op('&')(Access.SENDER.value),
        Message.is_draft
    )

    return render_template('mailbox.html', sent_messages=sent_messages,
                                           received_messages=received_messages,
                                           draft_messages=draft_messages
    )


@messages.route('/message/<int:message_id>', methods=['GET', 'DELETE'])
@login_required
def message(message_id):
    '''Allows the user to read a specific message by id.

       GET: display the content of a specific message by id (censored if language_filter is ON)
       DELETE: delete the message from the caller point of view
    '''
    _message = retrieve_message(message_id)
    user_id = current_user.get_id()
    is_sender_or_recipient(_message, user_id)

    if request.method == 'GET':
        if _message.get_recipient() == user_id and not _message.is_draft and not _message.is_read and _message.is_delivered:
            notify.delay(_message.get_sender(), 'Your message has been read!')
            _message.is_read = True
            db.session.commit()

        _message_aux = _message
        if current_user.has_language_filter:
            _message_aux = filter_language(_message)

        return render_template('message.html', user=current_user, message=_message_aux)

    # Delete scheduled message using bonus
    if not _message.is_draft and not _message.is_delivered and current_user.bonus > 0:
        user = db.session.query(User).filter(User.id==user_id).first()
        user.bonus -= 1
        _message.access -= Access.SENDER.value
        db.session.commit()
        return render_template('/schedule')

    # DELETE for the point of view of the current user.
    if _message.sender_id == user_id:
        _message.access -= Access.SENDER.value
    if _message.recipient_id == user_id:
        _message.access -= Access.RECIPIENT.value
    db.session.commit()
    message='<h3>Message deleted!</h3><br/>'
    return render_template('/error.html', error=message), 200


@messages.route('/create_message', methods=['GET', 'POST'])
@login_required
def create_message():
    '''Manage the creation, reply, and the forward of messages and drafts.

       GET: Creates the form for editing/writing a message.
            If <draft_id> is specified, the corresponding draft is loaded.
            If <forw_id> is specified, the corresponding message is loaded.
            If <reply_id> is specified, the corresponding recipient is loaded.
       POST: Takes the input from the form, creates a new Message object and save it on DB:
             As draft if the <save button> is clicked, as message to send otherwise.
    '''
    form = MessageForm()
    user_id = current_user.get_id()

    if request.method == 'POST':
        error = None
        # Save the choices of recipients.
        form.users_list.choices = form.users_list.data
        if form.validate_on_submit():
            clean_text = bleach.clean(form.text_area.data, tags=allowed_tags, strip=True,
                attributes=allowed_attrs, protocols=['data'], styles='background-color'
            )

            # Save draft.
            if form.save_button.data:
                # Update old draft.
                if form.message_id_hidden.data > 0:
                    message = retrieve_message(form.message_id_hidden.data)
                    message.text = clean_text
                    message.delivery_date = form.delivery_date.data
                    message.sender_id = user_id
                    message.recipient_id = 0
                    db.session.commit()

                # Create new draft.
                else:
                    new_message = Message()
                    new_message.text = clean_text
                    new_message.delivery_date = form.delivery_date.data
                    new_message.sender_id = user_id
                    new_message.recipient_id = 0
                    db.session.add(new_message)
                    db.session.commit()

            # Send.
            else:
                for recipient in form.users_list.data:
                    if is_blocked(recipient):
                        continue

                    # send new message from draft to first recipient
                    if form.message_id_hidden.data > 0:
                        message = retrieve_message(form.message_id_hidden.data)
                        message.is_draft = False
                        message.text = clean_text
                        message.delivery_date = form.delivery_date.data
                        message.sender_id = user_id
                        message.recipient_id = recipient
                        form.message_id_hidden.data = -1
                        db.session.commit()
                    else:
                        # send new message [from draft] to [other] recipients
                        new_message = Message()
                        new_message.text = clean_text
                        new_message.delivery_date = form.delivery_date.data
                        new_message.is_draft = False
                        new_message.sender_id = user_id
                        new_message.recipient_id = recipient
                        db.session.add(new_message)
                        db.session.commit()

            return redirect('/mailbox')

        else:
            error = '''
                <h3>Wrong data provided!</h3><br/>
                Rules:<br/>  
                    1. Delivery date must be in the future!<br/>
                    2. Recipient field can\'t be empty!
                '''
            # Conflict
            return render_template('/error.html', error=error), 409
    # GET
    else:
        form.users_list.choices = [
            (user.get_id(), user.get_email()) for user in get_users()
        ]
        selected = None

        draft_id = get_argument(request, 'draft_id', int)
        forw_id = get_argument(request, 'forw_id', int)
        reply_id = get_argument(request, 'reply_id', int)

        if draft_id is not None:
            message = retrieve_message(draft_id)
            is_sender_or_recipient(message, user_id)

            if not message.is_draft:
                error = '<h3>Error!</h3><br/> The message is not a draft!'
                # Forbidden
                return render_template('/error.html', error=error),403

            form.message_id_hidden.data = message.get_id()
            form.text_area.data = message.get_text()
            form.delivery_date.data = message.get_delivery_date()

        elif forw_id is not None:
            message = retrieve_message(forw_id)
            is_sender_or_recipient(message, user_id)

            # draft or scheduled message
            if message.is_draft or not message.is_delivered:
                error = '<h3>Error!</h3><br/> you can\'t forward this message!'

                # Forbidden
                return render_template('/error.html', error=error), 403

            form.text_area.data = f'Forwarded: {message.get_text()}'

        elif reply_id is not None:
            message = retrieve_message(reply_id)
            is_sender_or_recipient(message, user_id)

            if message.is_draft or not message.is_delivered:
                error = '<h3>Error!</h3><br/> you can\'t reply this message!'

                # Forbidden
                return render_template('/error.html', error=error), 403

            form.text_area.data = 'Reply: '
            selected = message.get_sender()

        return render_template('create_message.html', form=form, selected=selected)


@messages.route('/calendar')
@login_required
def calendar():
    '''Display a calendar with the messages scheduled to be sent in each day.

       GET: show the calendar template
    '''
    id = current_user.get_id()

    sent_messages = db.session.query(Message).filter(
        Message.sender_id == id,
        Message.access.op('&')(Access.SENDER.value),
        ~Message.is_draft,
        Message.is_delivered
    )

    received_messages = db.session.query(Message).filter(
        Message.recipient_id == id,
        Message.access.op('&')(Access.RECIPIENT.value),
        Message.is_delivered
    )

    sent_messages = [
        {
            'time': str(message.delivery_date),
            'cls': 'bg-orange-alt',
            'desc': f'To {message.recipient.firstname} {message.recipient.lastname}',
            'msg_id': message.id
        } for message in sent_messages
    ]

    received_messages = [
        {
            'time': str(message.delivery_date),
            'cls': 'bg-sky-blue-alt',
            'desc': f'From {message.sender.firstname} {message.sender.lastname}',
            'msg_id': message.id
        } for message in received_messages
    ]

    return render_template(
        'calendar.html',
        data=json.dumps(sent_messages + received_messages),
    )
