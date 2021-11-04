from celery import Celery
import os, time

from datetime import datetime

from monolith.database import User, db, Message

from .utils import send_email

BACKEND = BROKER = 'redis://localhost:6379/0'

celery = Celery(__name__, broker=BROKER, backend=BACKEND)

os.environ['TZ'] = 'Europe/Rome'
time.tzset()
_APP = None


@celery.task
def do_task():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP

    print("I am checking your stuff")
    with app.app_context():
        messages = db.session.query(Message).filter(
            Message.is_delivered == False,
            Message.delivery_date <= datetime.now()
        )

        for message in messages:                                    
            message.is_delivered = True
            print("Message sent")
            db.session.commit()
            # Send notification to the recipient.
            notify.delay(message.get_recipient(), 'You received a new message!')

    return 'delivered'


@celery.task
def notify(id, message):
    user = User.query.filter_by(id=id).first()
    if not (user is not None and user.is_active):
        return
    
    send_email(user.email, message)
    return 'done'


@celery.task
def lottery():
    pass


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, do_task.s(), name='add every 10')
    sender.add_periodic_task(60*60*24*30, lottery.s(), name='lottery extraction')
