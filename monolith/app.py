from flask import Flask

from datetime import datetime

from monolith.auth import login_manager
from monolith.database import User, Message, db
from monolith.views import blueprints


def create_app():
    app = Flask(__name__)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../mmiab.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'example@example.com')
        user = q.first()
        if user is None:
            example = User()
            example.firstname = 'Admin'
            example.lastname = 'Admin'
            example.email = 'example@example.com'
            example.dateofbirth = datetime(2020, 10, 5)
            example.profile_pic = "static/profile/default.png"
            example.is_admin = True
            example.set_password('admin')
            db.session.add(example)
            db.session.commit()

        # getting the dummy message if any
        m = db.session.query(Message).filter(Message.sender_id == 1 and Message.recipient_id==1)
        message = m.first()
        
        # creating dummy messages
        if message is None:
            for i in range(3):
                example = Message()
                example.sender_id = 1
                example.recipient_id = 1
                example.text = f"message from 1 to 1 n.{i+1}"
                now = datetime.now()
                example.delivery_date = now
                example.last_update_date = now
                example.is_draft = False
                db.session.add(example)
                db.session.commit()

            for i in range(3):
                example = Message()
                example.sender_id = 2
                example.recipient_id = 2
                example.text = f"message from 2 to 2 n.{i+1}"
                now = datetime.now()
                example.delivery_date = now
                example.last_update_date = now
                example.is_draft = False
                db.session.add(example)
                db.session.commit()

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
