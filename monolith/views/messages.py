from flask import Blueprint, render_template
from flask_login import current_user

from monolith.database import Message, db

from ..auth import login_required

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


@messages.route('/message/<int:id>')
@login_required
def message(id):
    _message = db.session.query(Message).filter(Message.id == id).first()

    if _message is None:
        return {'msg': 'message not found'}, 404
    
    return render_template('message.html', message=_message)
