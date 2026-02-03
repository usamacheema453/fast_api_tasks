import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import (
    MAIL_SERVER,
    MAIL_PORT,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM
)

def send_email(to_email: str, subject: str, body: str, html: bool = False):
    msg = MIMEMultipart()
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject

    if html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("email error:", e)
        return False
    
def login_alert_email(user_email, ip, device):
    subject= "New Login Alert"
    body = f"""
    Hello Admin
    A user just logged in.bool

    User Email : {user_email}
    Ip Address: {ip}
    Device: {device}
    Time: System Generated
    If this was not authorized, please investigate.

    Secure System Bot
    """

    return subject, body