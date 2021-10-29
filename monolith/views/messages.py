import datetime
import json

from flask import Blueprint, redirect, render_template, request, session, url_for, abort
from flask_login import current_user
from sqlalchemy import or_, and_

from .users import get_users

from ..access import Access
from ..auth import login_required
from ..image import save_image

from monolith.database import Message, db,User
from monolith.forms import MessageForm, SearchRecipientForm


messages = Blueprint('messages', __name__)

ATTACHMENTS_PATH = 'monolith/static'


def retrieve_message(message_id):
    _message = db.session.query(Message).filter(Message.id==message_id).first()
    if _message is None:
        abort(404, 'message not found')
    return _message


def is_sender_or_recipient(message, user_id):
    # Check authorization.
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
    
    # Retrieve sent/received messages of user <id>
    _messages = db.session.query(Message).filter(
        or_(
            and_(Message.sender_id==id, Message.access.op('&')(Access.SENDER.value), ~Message.is_draft), 
            and_(Message.recipient_id==id, Message.access.op('&')(Access.RECIPIENT.value))
        )
    )
    
    return render_template("mailbox.html", messages=_messages, user_id=id)


@messages.route('/message/<int:message_id>', methods=['GET', 'DELETE'])
@login_required
def message(message_id):
    # TODO: Catch exception instead of if.
    _message = retrieve_message(message_id)
    user_id = current_user.get_id()
    is_sender_or_recipient(_message, user_id)

    if request.method == 'GET':
        return render_template('message.html', message=_message)
    
    # DELETE for the point of view of the current user.
    if _message.sender_id == current_user.get_id():
        _message.access -= Access.SENDER.value
    if _message.recipient_id == current_user.get_id():
        _message.access -= Access.RECIPIENT.value
    db.session.commit()
    return {'msg': 'message deleted'}, 200


# -------------------------------------------------------------------
# TODO: TEST WITH THE NEW SEND
@messages.route('/forward/<int:message_id>')
@login_required
def forward(message_id):
    message = retrieve_message(message_id)
    user_id = current_user.get_id()
    is_sender_or_recipient(message, user_id)

    return redirect(url_for('messages.create_message', forw_id=message_id))    
 

@messages.route('/reply/<int:message_id>')
@login_required
def reply(message_id):
    message = retrieve_message(message_id)
    user_id = current_user.get_id()
    is_sender_or_recipient(message, user_id)

    return redirect(url_for('messages.create_message', recipient_id=message.get_sender()))   
# -------------------------------------------------------------------


'''
    Examples of usage:
    - (GET) localhost:5000/create_message
    - (GET) localhost:5000/create_message?draft_id=2
'''
@messages.route('/create_message', methods=['GET', 'POST'])
@login_required
def create_message():
    form = MessageForm()
    
    if request.method == 'POST':
        # Save the choices of recipients.
        form.users_list.choices = form.users_list.data
        
        if form.validate_on_submit():
            filename = ''
            file = form.image_file.data
            if 'image_file' not in request.files:
                filename = ''
            if file:
                filename = form.image_file.data.filename
                file = form.image_file.data
                filename = save_image(file, ATTACHMENTS_PATH)
            
            # Save draft.
            print(form.users_list.data)
            if form.submit_button.data:
                '''
                    TODO: a new message is required only if the draft is not
                          a modification of a previous draft.
                          In that case, just the old draft from the DB needs to be modifed.
                '''
                new_message = Message()
                new_message.text = form.text_area.data
                new_message.delivery_date = form.delivery_date.data  # TODO: check.
                new_message.sender_id = current_user.get_id()
                new_message.attachment = filename
                new_message.recipient_id = 0  # TODO: put the first recipient in the list.
                db.session.add(new_message) 
                db.session.commit() 
                return redirect('messages/draft')

            # Send.
            else:
                for recipient in form.users_list.data:
                    new_message = Message()
                    new_message.text = form.text_area.data
                    new_message.delivery_date = form.delivery_date.data  # TODO: check.
                    new_message.attachment = filename
                    new_message.is_draft = False
                    new_message.is_delivered = True  # TODO: change after Celery.
                    new_message.sender_id = current_user.get_id()
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

        draft_id = None
        forw_id = None
        recipient_id = None
        
        try:
            draft_id = int(request.args.get('draft_id'))
        except:
            pass  # This is safe, draft_id will be ignored.
        
        try:
            forw_id = int(request.args.get('forw_id'))
        except:
            pass  # This is safe, forw_id will be ignored.
        
        try:
            recipient_id = int(request.args.get('recipient_id'))
        except:
            pass  # This is safe, recipient_id will be ignored.


        if draft_id is not None:
            message = retrieve_message(draft_id)
            form.text_area.data = message.get_text()
            form.delivery_date.data = message.get_delivery_date()
            form.image_file.data = message.get_attachement()  # TODO: doesn't work

        if forw_id is not None:
            message = retrieve_message(forw_id)
            form.text_area.data = "Forwarded: " + message.get_text()
            form.image_file.data = message.get_attachement()  # TODO: doesn't work
        
        if recipient_id is not None:
            form.text_area.data = "Reply: "
            form.users_list.choices = [(recipient_id, recipient_id)]
        

        return render_template("create_message.html", form=form)


#list of draft messages
@messages.route('/messages/draft')
@login_required
def messages_draft():
    messages_draft = Message.query.filter_by(is_draft = True)
    return render_template("messages.html", messages=messages_draft)
