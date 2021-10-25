from flask import Blueprint, redirect, render_template, request
from flask_login import current_user

from ..auth import login_required
from monolith.database import User, Message, db
from monolith.forms import UserForm, UserDelForm, MessageForm

messages = Blueprint('messages', __name__)


@messages.route('/mailbox')
@login_required
def mailbox():
    # Retrieve user <id>
    id = current_user.get_id()
    
    # Retrieve sent/received messages of user <id>
    _messages = db.session.query(Message).filter(
        Message.sender_id == id or Message.recipient_id == id
    )
    return render_template("mailbox.html", messages=_messages)


@messages.route('/message/<int:id>', methods=['GET', 'DELETE'])
@login_required
def message(id):
    #TODO: Catch exception instead of if.
    _message = db.session.query(Message).filter(Message.id == id).first()
    
    if _message is None or not _message.is_valid:
        return {'msg': 'message not found'}, 404

    if _message.get_recipient() != current_user.get_id():
        return {'msg': 'unauthorized'}, 401

    if request.method == 'GET':
        return render_template('message.html', message=_message)
    
    # DELETE    
    _message.is_valid = False
    db.session.commit()
    return {'msg': 'message deleted'}, 200


@messages.route('/write_message', methods=['POST', 'GET'])
@login_required
def write_message():
    form = MessageForm()
    if request.method == 'POST':
        #for recipient in form.recipient_id.data:
            new_message=Message()
            new_message.recipient_id=form.recipient
            new_message.text=form.text_area
            new_message.delivery_date=form.delivery_date
            new_message.attachment=None
            new_message.is_draft=True
            new_message.is_delivered=False
            new_message.is_valid=True
            new_message.sender_id=form.sender_id
            db.session.add(new_message) 
            db.session.commit()          
            return redirect('/messages')

    elif request.method == 'GET':
        return render_template("create_message.html", form=form) 
    else:
        raise RuntimeError('This should not happen!')   
