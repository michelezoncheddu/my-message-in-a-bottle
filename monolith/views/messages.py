from flask import Blueprint, redirect, render_template, request,session, url_for
from flask_login import current_user
from sqlalchemy import or_, and_
from sqlalchemy.sql.expression import false

from ..access import Access
from ..auth import login_required

from monolith.database import Message, db, User
from monolith.forms import MessageForm, SearchRecipientForm


messages = Blueprint('messages', __name__)


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


@messages.route('/message/<int:id>', methods=['GET', 'DELETE'])
@login_required
def message(id):
    #TODO: Catch exception instead of if.
    _message = db.session.query(Message).filter(Message.id==id).first()

    if _message is None:
        return {'msg': 'message not found'}, 404

    # Check authorization.
    is_sender = _message.sender_id == current_user.get_id()
    is_recipient = _message.recipient_id == current_user.get_id()

    if (not is_sender or not is_recipient
        or (is_sender and not _message.access & Access.SENDER.value)
        or (is_recipient and not _message.access & Access.RECIPIENT.value)
    ):
        return {'msg': 'unauthorized'}, 401

    if request.method == 'GET':
        return render_template('message.html', message=_message)
    
    # DELETE for the point of view of the current user.
    if is_sender:
        _message.access -= Access.SENDER.value
    if is_recipient:
        _message.access -= Access.RECIPIENT.value
    db.session.commit()
    return {'msg': 'message deleted'}, 200


@messages.route('/create_message', methods=['POST','GET'])
#@login_required
def create_message():
    form = MessageForm()
    if request.method == 'POST':
        #for recipient in form.recipient_id.data:
        new_message=Message()
        if request.form['submit_button'] == 'Draft':
            is_draft = True
            new_message.recipient_id = 0
        else:
            is_draft = False
            #recipient_list=[]
            #new_message.recipient_id=form.recipient_id.data   
            mydata={"text":form.text_area.data,
                     "delivery_date":form.delivery_date.data,
                     "sender_id":form.sender_id.data}
            session['mydata'] = mydata         
            return redirect(url_for('messages.add_recipient', mydata=mydata))
            
        #print(form.image_file.data)
        
        new_message.text=form.text_area.data
        new_message.delivery_date= form.delivery_date.data
        new_message.attachment=None
        new_message.is_draft= is_draft
        new_message.is_delivered=False
        new_message.sender_id=form.sender_id.data
        #new_message.attachment=request.form['image_file']
        db.session.add(new_message) 
        db.session.commit() 

        return redirect('/messages')    

    elif request.method == 'GET':
        return render_template("create_message.html", form=form) 
    else:
        raise RuntimeError('This should not happen!')   


@messages.route('/messages/draft')
def messages_draft():
    messages_draft = Message.query.filter_by(is_draft = True)
    return render_template("messages.html", messages=messages_draft)


@messages.route('/messages/sent')
def messages_sent():
    messages_sent = Message.query.filter_by(is_draft = False, is_valid = True )
    return render_template("messages.html", messages=messages_sent)    


@messages.route('/messages')
def _messages():
    _messages = db.session.query(Message)
    return render_template("messages.html", messages=_messages)


@messages.route('/add_recipient', methods=['POST','GET'])
#@login_required
def add_recipient():
    form = SearchRecipientForm()
    if request.method == 'POST':
        to_search=form.search_recipient.data
        print('To search: '+to_search)
        recipient = User.query.filter_by(firstname = to_search).all()
        print(recipient[0].firstname)
        pass
    if request.method == 'GET': 
        mydata=session['mydata']
        print('print cookie:'+mydata['delivery_date'])
        return render_template("search_recipient.html", form=form)
