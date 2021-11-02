from celery import Celery

from datetime import datetime

from monolith.database import User, db, Message

BACKEND = BROKER = 'redis://localhost:6379'

#celery = Celery(__name__, backend=BACKEND, broker=BROKER)
celery = Celery(__name__, broker=BROKER,backend=BACKEND)

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
