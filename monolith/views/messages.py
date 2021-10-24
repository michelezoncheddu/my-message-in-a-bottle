from flask import Blueprint, redirect, render_template, request

from monolith.database import User, Message, db
#from monolith.forms import UserForm,UserDelForm

#from flask_login import current_user

messages = Blueprint('messages', __name__)


@messages.route('/messages')
def _messages():
    _messages = db.session.query(Message)
    return render_template("messages.html", messages=_messages)
