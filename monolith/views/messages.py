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

ATTACHMENTS_PATH = 'monolith/static/images'


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


@messages.route('/forward/<int:message_id>')
@login_required
def forward(message_id):
    message = retrieve_message(message_id)
    user_id = current_user.get_id()
    is_sender_or_recipient(message, user_id)

    session['draft_id'] = message_id
    return redirect(url_for('messages.create_message'))


@messages.route('/reply/<int:message_id>')
@login_required
def reply(message_id):
    message = retrieve_message(message_id)
    user_id = current_user.get_id()
    is_sender_or_recipient(message, user_id)

    session['chosen_recipient'] = [{'id': message.get_sender(), 'firstname': 'reply'}]
    return redirect(url_for('messages.create_message'))


@messages.route('/create_message', methods=['POST', 'GET'])
@login_required
def create_message():
    draft_id = None
    try:
        draft_id = int(request.args.get('draft_id'))
    except:
        abort(400, 'draft_id must be integer')

    form = MessageForm()
    
    if request.method == 'POST':
        form.users_list.choices = form.users_list.data
        if form.validate_on_submit():
            
            #check if there's an image; if so the image is saved locally and its path is in filename
            file = request.files['image_file']
            if ('file' not in request.files):
                filename = ''
            if file:
                filename = save_image(file, ATTACHMENTS_PATH)
            
            if request.form['submit_button'] == 'Save':
                new_message = Message()
                new_message.text = form.text_area.data
                new_message.delivery_date = form.delivery_date.data
                new_message.sender_id = current_user.get_id()
                new_message.attachment = filename
                new_message.recipient_id = 0
                db.session.add(new_message) 
                db.session.commit() 
                return redirect('/')
            elif request.form['submit_button'] == 'Load':
                return redirect('/messages/load_draft')
            elif request.form['submit_button'] == 'Home':
                return render_template("index.html", welcome=None)  
            #send button is chosen
            else:
                pass
                
    elif request.method == 'GET':
        users_list = []
        for i, user in enumerate(get_users()):
            users_list.append((i, user.get_email()))
        form.users_list.choices = users_list
        
        if draft_id is not None:
            message = retrieve_message(draft_id)
            print(message.get_text())
            form.text_area = message.get_text()
            form.delivery_date = message.get_delivery_date()
            form.image_file = message.get_attachement()
        
        return render_template("create_message.html", form=form) 
    else:
        raise RuntimeError('This should not happen!')   


#list of draft messages
@messages.route('/messages/draft')
@login_required
def messages_draft():
    messages_draft = Message.query.filter_by(is_draft = True)
    return render_template("messages.html", messages=messages_draft)

#list of sent messages
@messages.route('/messages/sent')
@login_required
def messages_sent():
    messages_sent = Message.query.filter_by(is_draft = False, access = True )
    return render_template("messages.html", messages=messages_sent)    



@messages.route('/send_message', methods=['POST'])
@login_required
def send_message(): 
    if request.method == 'POST':

        text=session['mydata']['text']
        delivery_date=session['mydata']['delivery_date']
        #sender_id=session['mydata']['sender_id']
        sender_id=current_user.get_id()
        attachment=session['mydata']['attachment']
        delivery_date_object = datetime.datetime.strptime(delivery_date, '%a, %d %b %Y %H:%M:%S GMT')
        i=1
        for recipient in session['chosen_recipient']:
            print("invio messaggio"+str(i))
            i+=1
            new_message=Message()
            new_message.text=text
            new_message.delivery_date= delivery_date_object.date()
            new_message.attachment=None
            new_message.is_draft= False
            new_message.is_delivered=False
            new_message.sender_id=sender_id
            new_message.recipient_id=recipient['id']
            new_message.attachment=attachment
            db.session.add(new_message) 
        
        db.session.commit() 
        session['chosen_recipient']=[]
        session['draft_id']=None
        return render_template("index.html", welcome=None)      

