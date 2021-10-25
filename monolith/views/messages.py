from flask import Blueprint, redirect, render_template, request
from flask_login import current_user

from ..auth import login_required

from monolith.database import Message, db
from monolith.forms import MessageForm

from sqlalchemy.sql.expression import false

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


@messages.route('/create_message', methods=['POST','GET'])
#@login_required
def create_message():
    form = MessageForm()
    if request.method == 'POST':
        #for recipient in form.recipient_id.data:
        if request.form['submit_button'] == 'Draft':
            is_draft = True
        else:
            is_draft = False

        new_message=Message()
        new_message.recipient_id=form.recipient_id.data
        new_message.text=form.text_area.data
        new_message.delivery_date= form.delivery_date.data
        new_message.attachment=None
        new_message.is_draft= is_draft
        new_message.is_delivered=False
        new_message.is_valid=True
        new_message.sender_id=form.sender_id.data
        db.session.add(new_message) 
        db.session.commit()          
        return redirect('/messages')

    elif request.method == 'GET':
        return render_template("create_message.html", form=form) 
    else:
        raise RuntimeError('This should not happen!')   
    
@messages.route('/messages/draft')
def messages_draft():
    messages_draft = db.session.query(Message)
    for i in messages_draft.filter_by(is_draft = True):
        print(i)
    return render_template("messages.html", messages=messages_draft)

@messages.route('/messages')
def _messages():
    _messages = db.session.query(Message)
    return render_template("messages.html", messages=_messages)