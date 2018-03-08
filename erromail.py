import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

 
def sendDevError(mail_subject, mail_msg):
    fromaddr = os.environ.get("FROMADDR")
    toaddr = os.environ.get("TOADDR")
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = mail_subject
 
    body = mail_msg
    msg.attach(MIMEText(body, 'plain'))
 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr,os.environ.get("EMAIL_PASS"))
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
