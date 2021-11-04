import smtplib, ssl

password = None
with open('token.txt') as f:
    password = f.readline()

smtp_server = "smtp-relay.sendinblue.com"
port = 465
sender_email = "m.zoncheddu@studenti.unipi.it"
receiver_email = 'emanuele_albertosi@hotmail.com'

message = """\
Subject: MyMessageInABottle - Notification

You received a new message!"""


context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
