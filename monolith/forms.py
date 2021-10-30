import wtforms as f
from flask_wtf import FlaskForm
from wtforms.fields.core import SelectMultipleField
from wtforms.validators import DataRequired, InputRequired
from wtforms.fields.html5 import DateTimeLocalField
from wtforms import SubmitField, DateField
from flask_wtf.file import FileField, FileAllowed


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
    location = f.StringField('location', validators=[DataRequired()])
    display = ['email', 'firstname', 'lastname', 'password', 'dateofbirth', 'location']


class UserDelForm(FlaskForm):
    firstname = f.StringField('firstname', validators=[DataRequired()])
    display = ['firstname']


class MessageForm(FlaskForm):
    text_area = f.TextAreaField('Insert message text')
    delivery_date = DateTimeLocalField('Delivery Date', validators=[InputRequired()], format='%Y-%m-%dT%H:%M')
    image_file = FileField('Image', validators=[FileAllowed(['jpg','png'])])
    users_list = SelectMultipleField('Select recipients', id='users_list')
    submit_button= SubmitField('Save')
    submit_button2= SubmitField('Send')
    display = ['text_area', 'delivery_date', 'image_file', 'users_list', 'submit_button', 'submit_button2']


class SearchRecipientForm(FlaskForm):
    search_recipient = f.StringField('Search Recipient')
    display = ['search_recipient']


class AddRecipientForm(FlaskForm):
    search_recipient = f.SelectMultipleField('none')
    display = ['add_recipient']
