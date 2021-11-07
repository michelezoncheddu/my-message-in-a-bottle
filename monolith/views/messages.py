import bleach
import json
from flask import Blueprint, redirect, render_template, request, abort
from flask_login import current_user
from better_profanity import profanity

from .users import get_users

from ..access import Access
from ..auth import login_required
from ..background import notify
from ..utils import get_argument, save_image

from monolith.database import User, Message, BlackList, db
from monolith.forms import MessageForm


messages = Blueprint('messages', __name__)

allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                'h1', 'h2', 'h3', 'img', 'video','p', 'div', 'iframe', 'br', 'span', 'hr', 'src', 'class','font','u']

allowed_attrs = {'*': ['class','style','color'],
                 'a': ['href', 'rel'],
                 'img': ['src', 'alt','data-filename','style']}


# profanity filter ('en' only)
profanity.load_censor_words()

ATTACHMENTS_PATH = 'monolith/static'

# utility function for checking if recipient has sender on blacklist
def is_blocked(recipient):
    recipient_id = (db.session.query(User).filter(User.id == recipient).first()).id
    # get list of blocked users ids
    _blocked_users = [r.id_blocked for r in db.session.query(BlackList.id_blocked).filter(BlackList.id_user == recipient_id)]
    if current_user.id in _blocked_users:
        return True
    else:
        return False

# utility function for censoring bad language in received messages
def filter_language(_message):
    censored_message = {}

    # censorship
    _message.text = profanity.censor(_message.text)
    censored_message.update({'recipient_id': _message.recipient_id, 'delivery_date': _message.delivery_date, 'text': _message.text})

    return censored_message

def retrieve_message(message_id):
    _message = db.session.query(Message).filter(Message.id==message_id).first()
    error='<h3>Wrong data provided!</h3><br/>Message not found'
    if _message is None:
        return render_template('/error.html', error=error), 404
    return _message


def is_sender_or_recipient(message, user_id):
    is_sender = message.sender_id == user_id
    is_recipient = message.recipient_id == user_id

    if (not (is_sender or is_recipient)
        or (is_sender and not message.access & Access.SENDER.value)
        or (is_recipient and (not message.access & Access.RECIPIENT.value
                              or message.is_draft
                              or not message.is_delivered)
           )
       ):
       error='<h3>Wrong data provided!</h3><br/>Forbidden'
       return render_template('/error.html', error=error), 403
    

@messages.route('/schedule')
@login_required
def schedule():
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
    # Retrieve user <id>
    id = current_user.get_id()
    
    # Retrieve sent messages of user <id>
    sent_messages = db.session.query(Message).filter(
        Message.sender_id==id,
        Message.access.op('&')(Access.SENDER.value), 
        ~Message.is_draft,
        Message.is_delivered
    )
    
    # Retrieve received messages of user <id>
    received_messages = db.session.query(Message).filter(
        Message.recipient_id==id,
        Message.access.op('&')(Access.RECIPIENT.value),
        Message.is_delivered
    )
    
    # Retrieve draft messages of user <id>
    draft_messages = db.session.query(Message).filter(
        Message.sender_id==id,
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
    # TODO: Catch exception instead of if.
    _message = retrieve_message(message_id)
    user_id = current_user.get_id()
    try:
        is_sender_or_recipient(_message, user_id)
    except:
        error='Not found!'
        return render_template('/error.html', error=error), 404
        

    _message_aux = _message
    # if language filter on
    if current_user.has_language_filter:
        _message_aux = filter_language(_message)

    if request.method == 'GET':
        if _message.get_recipient() == user_id and not _message.is_draft and not _message.is_read and _message.is_delivered:
           #print("INVIO LETTURA MESSAGGIO: "+str(_message.get_sender()),flush=True)
           notify.delay(_message.get_sender(), 'Your message has been read!')
           _message.is_read = True
           db.session.commit()
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

''' 
    Manage the creation, reply, and the forward of messages and drafts

    GET: Creates the form for editing/writing a message.
         If <draft_id> is specified, the corresponding draft is loaded.
         If <forw_id> is specified, the corresponding message is loaded.
         If <reply_id> is specified, the corresponding recipient is loaded.   
    POST: Takes the input from the form, creates a new Message object and save it on DB:
          As draft if the <save button> is clicked, as message to send otherwise.

'''
@messages.route('/create_message', methods=['GET', 'POST'])
@login_required
def create_message():
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
                    message.recipient_id = 0  # TODO: put the first recipient in the list.
                    db.session.commit() 

                # Create new draft.
                else:
                    new_message = Message()
                    new_message.text = clean_text
                    new_message.delivery_date = form.delivery_date.data
                    new_message.sender_id = user_id
                    new_message.recipient_id = 0  # TODO: put the first recipient in the list.
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
            #form.image_file.data = message.get_attachement()  # TODO: doesn't work

        elif forw_id is not None:
            message = retrieve_message(forw_id)
            is_sender_or_recipient(message, user_id)

            # draft or scheduled message
            if message.is_draft or not message.is_delivered:
                error = '<h3>Error!</h3><br/> you can\'t forward this message!'
                
                # Forbidden
                return render_template('/error.html', error=error), 403

            form.text_area.data = f'Forwarded: {message.get_text()}'
            #form.image_file.data = message.get_attachement()  # TODO: doesn't work

        elif reply_id is not None:
            message = retrieve_message(reply_id)
            is_sender_or_recipient(message, user_id)

            if message.is_draft or not message.is_delivered:
                error = '<h3>Error!</h3><br/> you can\'t reply this message!'
                
                # Forbidden
                return render_template('/error.html', error=error), 403

            form.text_area.data = 'Reply: '
            form.users_list.choices = [(message.get_sender(), message.get_sender())]  # TODO: write email of sender
        
        return render_template('create_message.html', form=form)


@messages.route('/calendar')
@login_required
def calendar():
    id = current_user.get_id()
    
    sent_messages = db.session.query(Message).filter(
        Message.sender_id==id,
        Message.access.op('&')(Access.SENDER.value), 
        ~Message.is_draft,
        Message.is_delivered
    )
    
    received_messages = db.session.query(Message).filter(
        Message.recipient_id==id,
        Message.access.op('&')(Access.RECIPIENT.value),
        Message.is_delivered
    )

    sent_messages = [
        {
            'time': str(message.delivery_date),
            'cls': 'bg-orange-alt',
            'desc': message.recipient_id,
            'msg_id': message.id
        } for message in sent_messages
    ]

    received_messages = [
        {
            'time': str(message.delivery_date),
            'cls': 'bg-sky-blue-alt',
            'desc': message.sender_id,
            'msg_id': message.id
        } for message in received_messages
    ]
    
    return render_template(
        'calendar.html',
        data=json.dumps(sent_messages + received_messages),
    )
