import wtforms as f
from flask_wtf import FlaskForm
from wtforms import Form
from wtforms.validators import DataRequired
#from wtforms.fields.html5 import DateField
from wtforms import DateField
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
    dateofbirth = DateField('dateofbirth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'dateofbirth']

class UserDelForm(FlaskForm):
    firstname = f.StringField('firstname', validators=[DataRequired()])
    display = ['firstname']

class MessageForm(FlaskForm):
    text_area = f.TextAreaField('Insert message text')
    #sender_id = f.IntegerField('Sender Id', validators=[DataRequired()])
    delivery_date = DateField('Delivery Date', format='%d/%m/%Y')
    image_file = FileField('Image',validators=[FileAllowed(['jpg','png'])]) 
    display = ['text_area', 'delivery_date','image_file']    

class SearchRecipientForm(FlaskForm):
    search_recipient = f.StringField('Search Recipient')
    display = ['search_recipient']

class AddRecipientForm(FlaskForm):
    search_recipient = f.SelectMultipleField('none')
    display = ['add_recipient']

  
