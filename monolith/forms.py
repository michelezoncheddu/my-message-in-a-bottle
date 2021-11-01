import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, InputRequired
from wtforms.fields.html5 import DateTimeLocalField
from wtforms import SubmitField, DateField, SelectMultipleField, IntegerField
from flask_wtf.file import FileField, FileAllowed
from wtforms.widgets import HiddenInput


class LoginForm(FlaskForm):
    email = f.StringField('Email', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('Email', validators=[DataRequired()])
    firstname = f.StringField('First Name', validators=[DataRequired()])
    lastname = f.StringField('Last Name', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    dateofbirth = DateField('Date of Birth', format='%d/%m/%Y')
    location = f.StringField('Location', validators=[DataRequired()])
    display = ['email', 'firstname', 'lastname', 'password', 'dateofbirth', 'location', 'submit_button']


class UserDelForm(FlaskForm):
    firstname = f.StringField('First Name', validators=[DataRequired()])
    display = ['firstname']


class MessageForm(FlaskForm):
    message_id_hidden = IntegerField(widget=HiddenInput(), default=-1)
    text_area = f.TextAreaField('Write your message here!',id='text')
    delivery_date = DateTimeLocalField('Delivery Date', validators=[InputRequired()], format='%Y-%m-%dT%H:%M')
    users_list = SelectMultipleField('Select recipients', id='users_list')
    submit_button= SubmitField('Save')
    submit_button2= SubmitField('Send')
    display = ['text_area', 'delivery_date', 'users_list']


class SearchRecipientForm(FlaskForm):
    search_recipient = f.StringField('Search Recipient')
    display = ['search_recipient']


class AddRecipientForm(FlaskForm):
    search_recipient = f.SelectMultipleField('none')
    display = ['add_recipient']
