import os
from mailersend import emails
from dotenv import load_dotenv

from utils.html_formatter import format_email

load_dotenv()

mailer = emails.NewEmail(os.getenv('EMAIL'))

mail_from = {
    "name": "WeAreTyping_",
    "email": "tadima@trial-o65qngk1mwdlwr12.mlsender.net",
}


def send_email(to_email, to_name, token):
    mail_body = {}

    recipients = [
        {
            "name": to_name,
            "email": to_email,
        }
    ]

    mailer.set_mail_from(mail_from, mail_body)
    mailer.set_mail_to(recipients, mail_body)
    mailer.set_subject("Email Verification", mail_body)
    mailer.set_html_content(format_email(token), mail_body)
    mailer.set_plaintext_content("This is the text content", mail_body)

    # using print() will also return status code and data
    mailer.send(mail_body)
