from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    date_of_birth = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id
    
    # get firstname
    def get_firstname(self):
        return self.firstname

    # get surname
    def get_surname(self):
        return self.lastname
    
    #get password hash
    def get_password_hash(self):
        return self.password
    
    # get email
    def get_email(self):
        return self.email


class Message(db.Model):

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.Unicode(128),nullable=False)
    delivery_date = db.Column(db.DateTime)
    is_draft = db.Column(db.Boolean, default=True)
    last_update_date = db.Column(db.DateTime)
    is_valid = db.Column(db.Boolean, default=True)
    is_delivered = db.Column(db.Boolean, default=False)
    attachment = db.Column(db.LargeBinary, default=None)

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

    def get_id(self):
        return self.id
    
    # get sender_id
    def get_sender(self):
        return self.sender_id

    # get recipient_id
    def get_recipient(self):
        return self.recipient_id
    
    # get text
    def get_text(self):
        return self.text

    # get delivery_date
    def get_delivery_date(self):
        return self.delivery_date

    # get if draft
    def is_draft(self):
        return self.is_draft 

    # get last update date
    def get_last_update_date(self):
        return self.last_update_date

    # get is_valid
    def is_valid(self):
        return self.is_valid
    
    # Set message as deleted.
    def set_as_invalid(self):
        self.is_valid = False

    # get is_delivered
    def is_delivered(self):
        return self.is_delivered

    # get attachement
    def get_attachement(self):
        return self.attachment
