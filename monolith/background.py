from datetime import datetime
import random


from celery import Celery

from monolith.database import User, db, Message

from .access import Access
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
        _APP = app
    return _APP


@celery.task
def do_task():
    app = lazy_init()
    print('I am checking your stuff')
    with app.app_context():
        messages = db.session.query(Message).filter(
            ~Message.is_delivered,
            ~Message.is_draft,
            Message.delivery_date <= datetime.now(),
            Message.access.op('&')(Access.SENDER.value)
        )

        for message in messages:
            message.is_delivered = True
            print('Message sent')
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
            return 'notDone'

        send_email(user.email, message)
        return 'Email sent'


@celery.task
def do_lottery():
    app = lazy_init()
    with app.app_context():
        rowCount = int(User.query.count())
        randomNum = int(random.randint(0, rowCount+1))
        randomUser = User.query.filter_by(id=randomNum).first()
        if not (randomUser is not None and randomUser.is_active):
            do_lottery.delay()
            return 'Non Estratto: ripeto estrazione'
        message = '''Complimenti, hai vinto la lotteria di questo mese!
            Collegati per ritirare il premio'''
        notify.delay(randomUser.id, message)
        randomUser.bonus += 1
        db.session.commit()
        return 'Estratto'


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10, do_task.s(), name='add every 10')
    #REALE
    sender.add_periodic_task(60*60*24*30, do_lottery.s(), name='lottery extraction')
    #TEST
    #sender.add_periodic_task(10000, do_lottery.s(), name='lottery extraction')
