import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateTimeLocalField, DateField
from wtforms import SubmitField, SelectMultipleField, IntegerField
from wtforms.widgets import HiddenInput
from datetime import datetime

from monolith.database import User, db
from .utils import allowed_password, allowed_email, allowed_birth_date

class LoginForm(FlaskForm):
    email = f.StringField('Email', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    display = ['email', 'password']

    def validate_on_submit(self):
        result = super(LoginForm, self).validate()
        email, password = self.email.data, self.password.data
        user = db.session.query(User).filter(User.email==email, User.is_active == True).first()
        # check that user exists in the db and that the password is valid
        if user is None or not user.authenticate(password):
            return [False, "invalid credentials"]
        # check if user is banned
        elif user.is_banned == True:
            return [False, "your account has been permanently banned!"]
        else: 
            return [result, ""]

class UserForm(FlaskForm):
    email = f.StringField('Email', validators=[DataRequired()])
    firstname = f.StringField('First Name', validators=[DataRequired()])
    lastname = f.StringField('Last Name', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth')
    location = f.StringField('Location', validators=[DataRequired()])
    display = ['email', 'firstname', 'lastname', 'password', 'date_of_birth', 'location']

    def validate_on_submit(self):
        result = super(UserForm, self).validate()
        curr_date = datetime.today().date() 

        # check email format is valid
        if not allowed_email(self.email.data):
            return [False, "invalid email format"]
        # check password requirements
        if not allowed_password(self.password.data):
            return [False, "password must be of length between 5 and 25 and contain at least one upper case, one number and one special character!"]
        # check birth date is in the past
        if not allowed_birth_date(self.date_of_birth.data):
            return [False, "date of birth must be in the past"]

        return [result, ""]

        """return self.is_submitted() and self.validate()"""


class UserDelForm(FlaskForm):
    firstname = f.StringField('First Name', validators=[DataRequired()])
    display = ['firstname']


class MessageForm(FlaskForm):
    message_id_hidden = IntegerField(widget=HiddenInput(), default=-1)
    text_area = f.TextAreaField('Write your message here!', id='text')
    delivery_date = DateTimeLocalField('Delivery Date', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    users_list = SelectMultipleField('Select recipients', id='users_list')
    save_button = SubmitField('Save')
    send_button = SubmitField('Send')
    display = ['text_area', 'delivery_date', 'users_list']

    # check that the delivery date chosen isn't before current time
    def validate_on_submit(self):
        if self.delivery_date.data is None or self.delivery_date.data < datetime.now():
            return False
        if (self.send_button.data) and (self.users_list.data == []):
            return False
        
        return True


class SearchRecipientForm(FlaskForm):
    search_recipient = f.StringField('Search Recipient')
    display = ['search_recipient']


class AddRecipientForm(FlaskForm):
    search_recipient = f.SelectMultipleField('none')
    display = ['add_recipient']
