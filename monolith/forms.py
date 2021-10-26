import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Regexp
from wtforms import DateField, Form
from flask_wtf.file import FileField, FileRequired, FileAllowed



class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    dateofbirth = f.DateField('dateofbirth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'dateofbirth']

class UserDelForm(FlaskForm):
    firstname = f.StringField('firstname', validators=[DataRequired()])
    display = ['firstname']

class MessageForm(FlaskForm):
    text_area = f.TextAreaField('Insert message text', validators=[DataRequired()])
    sender_id = f.IntegerField('Sender Id', validators=[DataRequired()])
    #recipient_id = f.IntegerField('Recipient Id', validators=[DataRequired()])
    delivery_date = f.DateField('Delivery Date', format='%d/%m/%Y')
    #image_file = FileField('Image',validators=[FileAllowed(['jpg','png'])]) 
    image_file = FileField('Image') 
    display = ['text_area','sender_id', 'delivery_date','image_file']    

class SearchRecipientForm(FlaskForm):
    search_recipient = f.StringField('Search Recipient', validators=[DataRequired()])
    display = ['search_recipient']
