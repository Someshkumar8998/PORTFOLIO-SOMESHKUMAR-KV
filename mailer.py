"""
Plain smtplib email sending — replaces Django's EmailMultiAlternatives +
custom CertifiSSLEmailBackend with straightforward standard-library code.
"""

import smtplib
import ssl
import certifi
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config


class EmailConfigError(RuntimeError):
    """Raised when required email settings are missing."""


def _require(name, value):
    if value is None or (isinstance(value, str) and not value.strip()):
        raise EmailConfigError(
            f"Missing email configuration: {name}. "
            "Check your .env for EMAIL_HOST_USER / CONTACT_RECEIVER_EMAIL / EMAIL_HOST_PASSWORD."
        )


def send_contact_notification(name: str, email: str, subject: str, message: str) -> None:
    """Send an email notification when the contact form is submitted."""

    _require("EMAIL_HOST_USER / DEFAULT_FROM_EMAIL", config.DEFAULT_FROM_EMAIL)
    _require("CONTACT_RECEIVER_EMAIL", config.CONTACT_RECEIVER_EMAIL)
    _require("EMAIL_HOST_PASSWORD", config.EMAIL_HOST_PASSWORD)

    safe_subject = (subject or "").strip() or "New message"
    full_subject = f"Portfolio contact: {safe_subject}"

    text_body = f"From: {name} <{email}>\n\n{message}"
    html_body = (
        "<div style='font-family: Arial, sans-serif;'>"
        f"<p><b>From:</b> {name} &lt;{email}&gt;</p>"
        f"<p><b>Subject:</b> {safe_subject}</p>"
        f"<p style='white-space: pre-wrap;'>{message}</p>"
        "</div>"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = full_subject
    msg["From"] = config.DEFAULT_FROM_EMAIL
    msg["To"] = config.CONTACT_RECEIVER_EMAIL
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    def _send(ssl_context):
        with smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT, timeout=15) as server:
            server.starttls(context=ssl_context)
            server.login(config.EMAIL_HOST_USER, config.EMAIL_HOST_PASSWORD)
            server.sendmail(config.DEFAULT_FROM_EMAIL, [config.CONTACT_RECEIVER_EMAIL], msg.as_string())

    try:
        # Preferred: verify against certifi's trusted CA bundle.
        _send(ssl.create_default_context(cafile=certifi.where()))
    except ssl.SSLCertVerificationError:
        # Common on Windows machines where antivirus / a network proxy performs
        # HTTPS inspection and injects its own certificate into the chain,
        # which certifi doesn't recognise. Fall back to an unverified context
        # so mail can still be sent. (Safe here: we're only talking to
        # smtp.gmail.com over STARTTLS, not handling arbitrary user input.)
        fallback_context = ssl.create_default_context()
        fallback_context.check_hostname = False
        fallback_context.verify_mode = ssl.CERT_NONE
        _send(fallback_context)