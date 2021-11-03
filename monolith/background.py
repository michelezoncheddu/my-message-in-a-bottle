from celery import Celery
import os, time

from datetime import datetime,timezone

from monolith.database import User, db, Message

BACKEND = BROKER = 'redis://localhost:6379/0'

celery = Celery(__name__, broker=BROKER,backend=BACKEND)

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
 
    message=None
    with app.app_context():
        _message=db.session.query(Message).filter(Message.is_delivered == False, 
                                                 Message.delivery_date <= datetime.now())                                                 
        for message in _message:                                    
            message.is_delivered=True
            print("Message sent")
            db.session.commit() 
            notify.delay(message.get_recipient())    
    return 'delivered'

@celery.task
def notify(id):    
    print('Send notification to: '+str(id))
    return 'done'


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, do_task.s(), name='add every 10')
