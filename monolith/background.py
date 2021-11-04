from celery import Celery

from datetime import datetime

from monolith.database import User, db, Message

from .utils import send_email

BACKEND = BROKER = 'redis://localhost:6379/0'

celery = Celery(__name__, broker=BROKER, backend=BACKEND)

_APP = None


def lazy_init():
    global _APP
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP
    return app


@celery.task
def do_task():
    app = lazy_init()
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
    app = lazy_init()
    with app.app_context():
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
