import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import DateField, Form


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
    text_area = f.TextAreaField('text_area', validators=[DataRequired()])
    sender_id = f.IntegerField('sender_id', validators=[DataRequired()])
    recipient_id = f.IntegerField('recipient_id', validators=[DataRequired()])
    delivery_date = f.DateField('delivery_date', format='%d/%m/%Y')
    display = ['text_area','sender_id', 'recipient_id', 'delivery_date']    