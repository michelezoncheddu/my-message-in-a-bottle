import os, smtplib, ssl

from werkzeug.utils import secure_filename

from datetime import date

# UTILS FOR FORM CHECKS
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
SPECIAL_CHARACTERS = '@#$%&*-_/'
ALLOWED_EMAILS = {'@test.com',
                  '@hotmail.com',
                  '@hotmail.it',
                  '@outlook.com',
                  '@outlook.it',
                  '@gmail.com',
                  '@gmail.it',
                  '@yahoo.com',
                  '@yahoo.it' ,
                  '@studenti.unipi.it',
                  '@di.unipi.it'
                }


def save_image(file, path):
    '''Utility function to save attachments (messages) or profile pics (users).'''
    filename = secure_filename(file.filename)
    file.save(os.path.join(path, filename))
    return filename


def allowed_file(filename):
    '''Utility function to check if attachments have a valid format.'''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_password(password):
    '''Utility function to check proper password's format.'''
    # check length
    if len(password) < 5 or len(password) > 25:
        return False
    # check if upper cases
    elif not any(el.isupper() for el in password):
        return False
    # check if numbers
    elif not any(el.isdigit() for el in password):
        return False
    # check if special characters
    elif not any(el in SPECIAL_CHARACTERS for el in password):
        return False
    return True


def allowed_email(email):
    '''Utility function to check proper format of the email field.'''
    for e in ALLOWED_EMAILS:
        if str(email).endswith(e):
            return True
    return False


def allowed_birth_date(birth_date):
    '''Utility function to check validity of birth date.'''
    if birth_date > date.today():
        return False
    return True


def get_argument(request, arg, type):
    '''Utility function to retrieve an argument and checking its type.'''
    try:
        return request.args.get(arg, type=type)
    except:
        return None


def send_email(email, message):
    '''Utility function to send email notification for the application.'''
    password = None
    with open('token.txt') as f:
        password = f.readline()

    smtp_server = 'smtp-relay.sendinblue.com'
    port = 465
    sender_email = 'emanuele.albertosi@gmail.com'
    receiver_email = email
    message = f'''\
    Subject: MyMessageInABottle - Notification

    {message}'''

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port,context=context) as server:
        #server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
