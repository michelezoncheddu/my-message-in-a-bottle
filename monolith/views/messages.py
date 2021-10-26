from flask import Blueprint, redirect, render_template, request,session, url_for,jsonify
from flask_login import current_user
from sqlalchemy import or_
import datetime
#import requests

from ..auth import login_required

from monolith.database import Message, db,User
from monolith.forms import AddRecipientForm, MessageForm, SearchRecipientForm

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
            return redirect(url_for('messages.search_recipient', mydata=mydata))
            
        #print(form.image_file.data)
        
        new_message.text=form.text_area.data
        new_message.delivery_date= form.delivery_date.data
        new_message.attachment=None
        new_message.is_draft= is_draft
        new_message.is_delivered=False
        new_message.is_valid=True
        new_message.sender_id=form.sender_id.data
        #new_message.attachment=request.form['image_file']
        db.session.add(new_message) 
        db.session.commit() 

        return redirect('/messages')    

    elif request.method == 'GET':
        #inizializzo il cookie per per i destinatari
        session['chosen_recipient']=[]
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

@messages.route('/search_recipient', methods=['POST','GET'])
#@login_required
def search_recipient():
    form = SearchRecipientForm()
    if request.method == 'POST':
        print(request.form['submit_button'])
        if (request.form['submit_button'] == 'send') & (session['chosen_recipient']!=[]) :
            return redirect(url_for('messages.send_message'),code=307)
        elif (request.form['submit_button'] == 'send') & (session['chosen_recipient']==[]):
            return redirect ('/search_recipient')
        elif request.form['submit_button'] == 'cancel':
            return redirect ('/')  
        else:    
            to_search=form.search_recipient.data
            print('To search: '+to_search)
            found_recipient = User.query.filter_by(firstname = to_search).all()
            print(found_recipient[0].firstname)
            recipient_list=[]
            for rec in found_recipient:
                 recipient_list.append({'id':rec.id,'firstname':rec.firstname})

            session['found_recipient'] =recipient_list
            print(session['found_recipient'])
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
    #session['chosen_recipient']=[]   
    if request.method == 'POST':
        print(request.form['recipient_list'])
        chosen_recipients_temp=[]
        for id in request.form['recipient_list']:
         found_recipient = User.query.filter_by(id = id).first()
         print(found_recipient.firstname)
         chosen_recipients_temp.append({'id':found_recipient.id,'firstname':found_recipient.firstname})

        #chosen_recipients_temp = request.form['recipient_list']
        print("INTERMEDIO: "+str(session['chosen_recipient']))
        print("CHOSEN: "+str(chosen_recipients_temp))
        chosen_recipients =session['chosen_recipient']+chosen_recipients_temp
        session['chosen_recipient'] = chosen_recipients
        print("FINALE: "+str(session['chosen_recipient']))
        return redirect('/search_recipient')
    if request.method == 'GET': 
        print(session['found_recipient'])
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
    else:
        return 404