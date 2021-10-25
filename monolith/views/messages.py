from flask import Blueprint, redirect, render_template, request

from monolith.database import User, Message, db
from monolith.forms import UserForm,UserDelForm,MessageForm

#from flask_login import current_user

messages = Blueprint('messages', __name__)


@messages.route('/messages')
def _messages():
    _messages = db.session.query(Message)
    return render_template("messages.html", messages=_messages)

@messages.route('/write_message', methods=['POST','GET'])
def write_message():

    form = MessageForm()
    if request.method == 'POST':
        for recipient in form.recipient_id.data:
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
