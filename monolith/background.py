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
 
    current_time = datetime.now()
    message=None
    with app.app_context():
        message=db.session.query(Message).filter(Message.is_delivered == False).first()
        if message is not None:
            message.is_delivered=True
            print("MESSAGGIO SPEDITO")
        #message_g=message
            db.session.commit() 
        notify.delay(1)    
    return 'delivered'

@celery.task
def notify(id):    
    print('Notifica inviata a utente'+str(id))
    return 'done'


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, do_task.s(), name='add every 10')
