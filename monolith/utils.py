import os, smtplib, ssl

from werkzeug.utils import secure_filename

from datetime import date


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


# utility function for saving attachments (messages) or profile pics (users)
def save_image(file, path):
    filename = secure_filename(file.filename)
    file.save(os.path.join(path, filename))
    return filename


# utility for checking if attachments have a valid format
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# utility for checking proper password
def allowed_password(password):
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


# utility for checking proper format of email field
def allowed_email(email):
    for e in ALLOWED_EMAILS:
        if str(email).endswith(e):
            return True
            
    return False


# utility for checking validity of birth date
def allowed_birth_date(birth_date):
    if birth_date > date.today():
        return False

    return True


'''Utility for retrieving an argument
   and checking its type.
'''
def get_argument(request, arg, type):
    try:
        return request.args.get(arg, type=type)
    except:
        return None


def send_email(email, message):
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
