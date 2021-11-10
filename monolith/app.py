import os, time

from flask import Flask

from datetime import date, datetime

from monolith.auth import login_manager
from monolith.database import User, Message, db
from monolith.views import blueprints
import bleach

allowed_tags_sum = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'iframe', 'span', 'hr', 'src', 'class','font','u']
allowed_attrs_sum = {'*': ['class','style','color'],
                        'a': ['href', 'rel'],
                        'img': ['src', 'alt','data-filename','style']}

os.environ['TZ'] = 'Europe/Rome'
time.tzset()


def create_app():
    app = Flask(__name__)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../mmiab.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CKEDITOR_SERVE_LOCAL'] = True

    def jBleach(value):
        return bleach.clean(value, tags=allowed_tags_sum, attributes=allowed_attrs_sum, strip=True)

    app.jinja_env.filters['jBleach'] = jBleach

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # Create a first admin user
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'admin@test.com')
        user = q.first()
        if user is None:
            example = User()
            example.firstname = 'admin'
            example.lastname = 'admin'
            example.email = 'admin@test.com'
            example.date_of_birth = date(2020, 10, 5)
            example.location = 'Pisa'
            example.profile_pic = 'static/profile/default.png'
            example.is_admin = True
            example.is_banned = False
            example.set_password('Admin1@')
            db.session.add(example)
            db.session.commit()

            example = User()
            example.firstname = 'sender'
            example.lastname = 'sender'
            example.email = 's@test.com'
            example.date_of_birth = date(2020, 10, 5)
            example.location = 'Pisa'
            example.profile_pic = 'static/profile/default.png'
            example.is_admin = False
            example.is_banned = False
            example.set_password('Sender1@')
            db.session.add(example)
            db.session.commit()

            example = User()
            example.firstname = 'recipient'
            example.lastname = 'recipient'
            example.email = 'r@test.com'
            example.date_of_birth = date(2020, 10, 5)
            example.location = 'Pisa'
            example.profile_pic = 'static/profile/default.png'
            example.is_admin = False
            example.is_banned = False
            example.set_password('Recipient1@')
            db.session.add(example)
            db.session.commit()


        # Getting the dummy message if any
        m = db.session.query(Message).filter(Message.sender_id == 2 and Message.recipient_id==1)
        message = m.first()

        # Creating dummy messages
        if message is None:
            example = Message()
            example.sender_id = 2
            example.recipient_id = 1
            example.text = 'hello by 1'
            now = datetime.now()
            example.delivery_date = now
            example.last_update_date = now
            example.is_draft = False
            example.is_delivered = True
            db.session.add(example)

            example = Message()
            example.sender_id = 2
            example.recipient_id = 1
            example.text = 'draft by 2'
            now = datetime.now()
            example.delivery_date = now
            example.last_update_date = now
            example.is_draft = True
            db.session.add(example)
            db.session.commit()

    return app


app = create_app()


if __name__ == '__main__':
    app.run()
