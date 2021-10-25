from flask import Blueprint, render_template

from monolith.database import Message, db

from flask_login import current_user

messages = Blueprint('messages', __name__)


@messages.route('/mailbox')
def mailbox():
    # check if user is logged in
    if not current_user.is_authenticated:  # TODO: compare with hasattr(id)
        return {"msg": "You must login"}, 401
    
    # retrieve user <id>
    id = current_user.get_id()

    # retrieve sent/received messages of user <id>
    _messages = db.session.query(Message).filter(
        Message.sender_id == id or Message.recipient_id == id)
    
    return render_template("mailbox.html", messages=_messages)