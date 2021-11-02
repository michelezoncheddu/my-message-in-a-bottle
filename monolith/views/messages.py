from flask import Blueprint, redirect, render_template, request, abort
from flask_login import current_user
from sqlalchemy import or_, and_
import bleach
from better_profanity import profanity
import re

from .users import get_users

from ..access import Access
from ..auth import login_required
from ..image import save_image

from monolith.database import User, Message, BlackList, db
from monolith.forms import MessageForm


messages = Blueprint('messages', __name__)

allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'img', 'video', 'div', 'iframe', 'br', 'span', 'hr', 'src', 'class','font','u']
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
    if _message is None:
        abort(404, 'message not found')
    return _message


def is_sender_or_recipient(message, user_id):
    is_sender = message.sender_id == user_id
    is_recipient = message.recipient_id == user_id

    if (not (is_sender or is_recipient)
        or (is_sender and not message.access & Access.SENDER.value)
        or (is_recipient and not message.access & Access.RECIPIENT.value)
    ):
        abort(401, 'unauthorized')


@messages.route('/mailbox')
@login_required
def mailbox():
    # Retrieve user <id>
    id = current_user.get_id()
    
    # Retrieve sent messages of user <id>
    sent_messages = db.session.query(Message).filter(
        Message.sender_id==id, Message.access.op('&')(Access.SENDER.value), ~Message.is_draft
    )
    
    # Retrieve recieved messages of user <id>
    received_messages = db.session.query(Message).filter(
        Message.recipient_id==id, Message.access.op('&')(Access.RECIPIENT.value)
    )
    
    # Retrieve draft messages of user <id>
    draft_messages = db.session.query(Message).filter(
        Message.sender_id==id, Message.is_draft
    )
    
    return render_template('mailbox.html', sent_messages=sent_messages,
                                           recieved_messages=received_messages,
                                           draft_messages=draft_messages
    )


@messages.route('/message/<int:message_id>', methods=['GET', 'DELETE'])
@login_required
def message(message_id):
    # TODO: Catch exception instead of if.
    _message = retrieve_message(message_id)
    user_id = current_user.get_id()
    is_sender_or_recipient(_message, user_id)

    _message_aux = _message
    # if language filter on
    if (current_user.has_language_filter):
        _message_aux = filter_language(_message)

    if request.method == 'GET':
        return render_template('message.html', message=_message_aux)
    
    # DELETE for the point of view of the current user.
    if _message.sender_id == user_id:
        _message.access -= Access.SENDER.value
    if _message.recipient_id == user_id:
        _message.access -= Access.RECIPIENT.value
    db.session.commit()
    return {'msg': 'message deleted'}, 200

'''
    Examples of usage:
    - (GET) localhost:5000/create_message
    - (GET) localhost:5000/create_message?draft_id=2
'''
@messages.route('/create_message', methods=['GET', 'POST'])
@login_required
def create_message():
    form = MessageForm()
    user_id = current_user.get_id()

    if request.method == 'POST':
        # Save the choices of recipients.
        form.users_list.choices = form.users_list.data
        
        if form.validate_on_submit():
            '''
            filename = ''
            file = form.image_file.data
            if 'image_file' not in request.files:
                filename = ''
            if file:
                filename = form.image_file.data.filename
                file = form.image_file.data
                filename = save_image(file, ATTACHMENTS_PATH)'''
            
            # Save draft.
            print(form.submit_button.data)
            if form.submit_button.data:
                
                if form.message_id_hidden.data>0:
                    message = retrieve_message(form.message_id_hidden.data)
                    message.text = bleach.clean(form.text_area.data,tags=allowed_tags,strip=True,attributes=allowed_attrs,protocols=['data'],styles='background-color')
                    message.delivery_date = form.delivery_date.data
                    message.sender_id = user_id
                    message.recipient_id = 0  # TODO: put the first recipient in the list.
                    db.session.commit() 
                    
                else:
                    new_message = Message()
                    new_message.text = bleach.clean(form.text_area.data,tags=allowed_tags,strip=True,attributes=allowed_attrs,protocols=['data'],styles='background-color')
                    new_message.delivery_date = form.delivery_date.data
                    new_message.sender_id = user_id
                    new_message.recipient_id = 0  # TODO: put the first recipient in the list.
                    db.session.add(new_message) 
                    db.session.commit() 

                return redirect('/mailbox')

            # Send.
            else:
                for recipient in form.users_list.data:
                    # TODO: delegate this to celery
                    # if not blocked : send
                    if (not is_blocked(recipient)):
                        # send new message from draft to first recipient
                        if form.message_id_hidden.data>0:
                            message = retrieve_message(form.message_id_hidden.data)
                            message.is_draft = False
                            message.text = bleach.clean(form.text_area.data,tags=allowed_tags,strip=True,attributes=allowed_attrs,protocols=['data'],styles='background-color')
                            message.delivery_date = form.delivery_date.data
                            message.sender_id = user_id
                            message.recipient_id = recipient
                            form.message_id_hidden.data=-1
                            db.session.commit()
                        else:
                            # send new message [from draft] to [other] recipients 
                            new_message = Message()
                            new_message.text = bleach.clean(form.text_area.data,tags=allowed_tags,strip=True,attributes=allowed_attrs,protocols=['data'],styles='background-color')
                            new_message.delivery_date = form.delivery_date.data
                            new_message.is_draft = False
                            new_message.sender_id = user_id
                            new_message.recipient_id = recipient
                            db.session.add(new_message) 
                            db.session.commit()
                return redirect('/mailbox')

        '''
            This is the case of invalid form.
            TODO: stay on the same form without losing input and show an error message.
        '''
        return redirect('/create_message')
    
    # GET
    else:
        form.users_list.choices = [
            (user.get_id(), user.get_email()) for user in get_users()
        ]

        draft_id, forw_id, reply_id = None, None, None
        # TODO: check if the argument exist, so to avoid try-except.
        try:
            draft_id = int(request.args.get('draft_id'))
        except:
            pass  # This is safe, draft_id will be ignored.
        
        try:
            forw_id = int(request.args.get('forw_id'))
        except:
            pass  # This is safe, forw_id will be ignored.
        
        try:
            reply_id = int(request.args.get('reply_id'))
        except:
            pass  # This is safe, recipient_id will be ignored.

        if draft_id is not None:
            message = retrieve_message(draft_id)
            is_sender_or_recipient(message, user_id)

            if not message.is_draft:
                abort(400, 'not a draft')

            form.message_id_hidden.data = message.get_id()
            form.text_area.data = message.get_text()
            form.delivery_date.data = message.get_delivery_date()
            #form.image_file.data = message.get_attachement()  # TODO: doesn't work

        elif forw_id is not None:
            message = retrieve_message(forw_id)
            is_sender_or_recipient(message, user_id)

            if message.is_draft:
                abort(400, 'you cannot forward a draft')

            form.text_area.data = 'Forwarded: ' + message.get_text()
            #form.image_file.data = message.get_attachement()  # TODO: doesn't work
        
        elif reply_id is not None:
            message = retrieve_message(reply_id)
            is_sender_or_recipient(message, user_id)

            if message.is_draft:
                abort(404, 'you cannot reply to a draft')

            form.text_area.data = 'Reply: '
            form.users_list.choices = [(message.get_sender(), message.get_sender())]
        
        return render_template('create_message.html', form=form)


# List of draft messages.
@messages.route('/messages/draft')
@login_required
def messages_draft():
    messages_draft = Message.query.filter_by(is_draft = True)
    return render_template('mailbox.html', messages=messages_draft)
