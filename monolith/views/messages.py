from flask import Blueprint, redirect, render_template, request,session, url_for
from flask_login import current_user
from sqlalchemy import or_, and_

from ..access import Access
from ..auth import login_required
from ..image import save_image

from monolith.database import Message, db,User
from monolith.forms import MessageForm, SearchRecipientForm
import datetime


messages = Blueprint('messages', __name__)

ATTACHMENTS_PATH = 'monolith/images'

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
        #draft button is chosen
        if request.form['submit_button'] == 'Save':
            is_draft = True
            new_message.recipient_id = 0
        elif request.form['submit_button'] == 'Load':
            return redirect('/messages/load_draft')
        #send button is chosen
        else:
            is_draft = False
            #the data from the form is saved to be sent later
            mydata={"text":form.text_area.data,
                     "delivery_date":form.delivery_date.data,
                     "sender_id":form.sender_id.data}
            session['mydata'] = mydata
            #redirects to search_recipient page to choose recipients         
            return redirect(url_for('messages.search_recipient', mydata=mydata))

        #create a draft message
        new_message.text=form.text_area.data
        new_message.delivery_date= form.delivery_date.data
        new_message.attachment=None
        new_message.is_draft= is_draft
        new_message.is_delivered=False
        new_message.sender_id=form.sender_id.data
 
        #check if there's an image; if so the image is saved locally and its path added to db
        file = request.files['image_file']
        if file:
            filename = save_image(file, ATTACHMENTS_PATH)
            new_message.attachment = filename

        db.session.add(new_message) 
        db.session.commit() 

        return redirect('/messages')    

    elif request.method == 'GET':
        #creating cookie for recipients 
        if  session['draft_id']:
            message=Message.query.filter(Message.id==session['draft_id']).first()
            text=message.text
            date=message.delivery_date
            form.text_area.data=text
            form.delivery_date.data=date
        session['chosen_recipient']=[]
        return render_template("create_message.html", form=form) 
    else:
        raise RuntimeError('This should not happen!')   


#list of draft messages
@messages.route('/messages/draft')
def messages_draft():
    messages_draft = Message.query.filter_by(is_draft = True)
    return render_template("messages.html", messages=messages_draft)

#list of sent messages
@messages.route('/messages/sent')
def messages_sent():
    messages_sent = Message.query.filter_by(is_draft = False, is_valid = True )
    return render_template("messages.html", messages=messages_sent)    

@messages.route('/messages')
def _messages():
    _messages = db.session.query(Message)
    return render_template("messages.html", messages=_messages)

#search_recipient page called after hitting the send button on the create_message page
@messages.route('/search_recipient', methods=['POST','GET'])
#@login_required
def search_recipient():
    form = SearchRecipientForm()
    if request.method == 'POST':
        #add multiple recipients for a message
        if (request.form['submit_button'] == 'send') & (session['chosen_recipient']!=[]) :
            return redirect(url_for('messages.send_message'),code=307)
        elif (request.form['submit_button'] == 'send') & (session['chosen_recipient']==[]):
            return redirect ('/search_recipient')
        elif request.form['submit_button'] == 'cancel':
            return redirect ('/')  
        else:    
            #search recipients in the list of users
            to_search=form.search_recipient.data
            found_recipient = User.query.filter(User.firstname.ilike("%{}%".format(to_search))).all()
            if found_recipient == []:
                return redirect('/search_recipient')
            recipient_list=[]
            for rec in found_recipient:
                 recipient_list.append({'id':rec.id,'firstname':rec.firstname})

            session['found_recipient'] =recipient_list
            return redirect(url_for('messages.add_recipient'))
    if request.method == 'GET': 
        #mydata=session['mydata']
        recipients=session['chosen_recipient']
        return render_template("search_recipient.html", form=form,recipients=recipients) 

@messages.route('/add_recipient', methods=['POST','GET'])
def add_recipient():

    '''if session['chosen_recipient'] != '':
        pass
    else:'''
    form = SearchRecipientForm()
    #session['chosen_recipient']=[]   
    if request.method == 'POST':
        chosen_recipients_temp=[]
        for id in request.form['recipient_list']:
         found_recipient = User.query.filter_by(id = id).first()
         chosen_recipients_temp.append({'id':found_recipient.id,'firstname':found_recipient.firstname})

        #chosen_recipients_temp = request.form['recipient_list']

        chosen_recipients =session['chosen_recipient']+chosen_recipients_temp
        session['chosen_recipient'] = chosen_recipients

        return redirect('/search_recipient')
    if request.method == 'GET': 
        return render_template("add_recipient.html",recipients=session['found_recipient']) 

@messages.route('/send_message', methods=['POST'])
def send_message(): 
    if request.method == 'POST':

        text=session['mydata']['text']
        delivery_date=session['mydata']['delivery_date']
        sender_id=session['mydata']['sender_id']
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
            db.session.add(new_message) 
        
        db.session.commit() 
        return redirect('/messages')      


@messages.route('/messages/load_draft', methods=['GET','POST'])
def load_draft():
    if request.method == 'POST':
        draft_id = request.form['draft']
        session['draft_id']=draft_id
        return redirect('/create_message')
        
    if request.method == 'GET':
        if current_user.get_id() == None:
            id = 1
        else:
            id = current_user.get_id()
        draft_list=Message.query.filter(Message.sender_id==id,Message.is_draft==True)
        if draft_list ==[]:
            return {'msg': 'No Saved Messages'}, 404
        return render_template("load_draft.html",draft_list=draft_list)


