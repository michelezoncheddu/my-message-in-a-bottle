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
    '''Returns the application singleton.'''
    global _APP
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
        _APP = app
    return _APP


@celery.task
def send_messages():
    '''Reads from the DB all the pending messages with expired delivery date,
       and makes them available for the recipient.
    '''
    app = lazy_init()
    with app.app_context():
        messages = db.session.query(Message).filter(
            ~Message.is_delivered,
            ~Message.is_draft,
            Message.delivery_date <= datetime.now(),
            Message.access.op('&')(Access.SENDER.value)  # Message not deleted with the bonus.
        )

        for message in messages:
            message.is_delivered = True
            db.session.commit()
            # Send notification to the recipient.
            notify.delay(message.get_recipient(), 'You received a new message!')

    return 'Delivered'


@celery.task
def notify(user_id, message):
    '''Sends an email containing <message> to the user
       identified with <user_id>, if present and active.
    '''
    app = lazy_init()
    with app.app_context():
        user = User.query.filter_by(id=user_id).first()
        if user is None or not user.is_active:
            return 'Email not sent'

        send_email(user.email, message)
    return 'Email sent'


@celery.task
def lottery():
    '''Increases the bonus of a random user
       and sends a notification for that.
    '''
    app = lazy_init()
    with app.app_context():
        n_users = int(User.query.count())
        random_n = random.randint(0, n_users+1)
        random_user = User.query.filter_by(id=random_n).first()
        if random_user is None or not random_user.is_active:
            lottery.delay()
            return 'Redoing lottery'

        random_user.bonus += 1
        db.session.commit()
        message = 'Congratulations, you won a bonus deletion!'
        notify.delay(random_user.id, message)

    return 'Lottery done'


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    '''Registers the periodic tasks.'''
    seconds_in_a = {
        'minute': 60,
        'month': 60*60*24*30
    }
    sender.add_periodic_task(5 * seconds_in_a['minute'], send_messages.s(), name='send_messages')
    sender.add_periodic_task(seconds_in_a['month'], lottery.s(), name='lottery')
