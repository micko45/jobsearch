import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pickle
p_file = "./pikle.pk"
loaded = pickle.load(open(p_file, 'rb'))

def authMailHtml():
    port = 465
    username = "ultima@mickostock.xyz"
    password = "Letmein_namecheap"
    smtp_server = "mail.privateemail.com"
    context = ssl.create_default_context()
    sender_email = "ultima@mickostock.xyz"
    receiver_email = "mickostock@gmail.com"

    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message['From'] = "ultima@mickostock.xyz"
    message['To'] = 'mickostock@gmail.com'

    text = """\
    Hi,
    How are you?
    Real Python has many great tutorials:
    www.realpython.com"""
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(loaded, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

authMailHtml()
