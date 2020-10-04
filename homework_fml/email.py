import os
from email.message import EmailMessage
from smtplib import SMTP_SSL
from typing import Optional

import dkim
from sentry_sdk import start_span


def _create_message(to, subject, plaintext_body, html_body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["EMAIL_SENDER"]
    msg["To"] = to

    msg.set_content(plaintext_body)
    if html_body is not None:
        msg.add_alternative(html_body, subtype="html")

    return msg


# I'm too poor for actual email hosting, so the mails are received by improvmx.com
# and forwarded to my personal email. As for sending, this is done by a small trick
# – I use my personal email provider to send the mail with the From header set to
# @homework-f.ml. That works, but some clients treat it as untrustworthy, so I add
# a DKIM signature to prove it is still sent by owner of the "impersonated" domain
def _sign_message(msg):
    msg["DKIM-Signature"] = (
        dkim.sign(
            message=msg.as_bytes(),
            selector=os.environ["DKIM_SELECTOR"].encode(),
            domain=os.environ["DKIM_DOMAIN"].encode(),
            privkey=os.environ["DKIM_PRIVKEY"].encode(),
            include_headers=["Subject", "From", "To"],
        )
        .decode()
        .lstrip("DKIM-Signature:")
        .strip()
        .replace("\r\n", "")
    )


def _send_message(msg):
    s = SMTP_SSL(os.environ["SMTP_SERVER"])
    s.login(os.environ["SMTP_LOGIN"], os.environ["SMTP_PWD"])
    s.send_message(msg)
    s.quit()


def send_mail(
    to: str, subject: str, plaintext_body: str, html_body: Optional[str] = None,
) -> None:
    """Send an email, optionally with multipart HTML body.

    :param to: Address to send the email to.
    :param subject: Subject of the message.
    :param plaintext_body: Plain text version of the email body.
    :param html_body: Optional; If included, the message will be multipart/alternative.
    :rtype: None
    """

    with start_span(op="email", description="Send an email"):
        msg = _create_message(to, subject, plaintext_body, html_body)
        _sign_message(msg)
        with start_span(op="smtp", description="Send the message"):
            _send_message(msg)
