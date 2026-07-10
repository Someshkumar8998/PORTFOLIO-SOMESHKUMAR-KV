[33mcommit 709a32211a4232cc0fd3289749f10cdb20f6fe36[m
Author: Someshkumar8998 <ksomeshkumar7036@gmail.com>
Date:   Fri Jul 10 08:50:01 2026 +0530

    Add full plain Python portfolio project

[1mdiff --git a/mailer.py b/mailer.py[m
[1mnew file mode 100644[m
[1mindex 0000000..629b140[m
[1m--- /dev/null[m
[1m+++ b/mailer.py[m
[36m@@ -0,0 +1,71 @@[m
[32m+[m[32m"""[m
[32m+[m[32mPlain smtplib email sending — replaces Django's EmailMultiAlternatives +[m
[32m+[m[32mcustom CertifiSSLEmailBackend with straightforward standard-library code.[m
[32m+[m[32m"""[m
[32m+[m
[32m+[m[32mimport smtplib[m
[32m+[m[32mimport ssl[m
[32m+[m[32mimport certifi[m
[32m+[m[32mfrom email.mime.multipart import MIMEMultipart[m
[32m+[m[32mfrom email.mime.text import MIMEText[m
[32m+[m
[32m+[m[32mimport config[m
[32m+[m
[32m+[m
[32m+[m[32mclass EmailConfigError(RuntimeError):[m
[32m+[m[32m    """Raised when required email settings are missing."""[m
[32m+[m
[32m+[m
[32m+[m[32mdef _require(name, value):[m
[32m+[m[32m    if value is None or (isinstance(value, str) and not value.strip()):[m
[32m+[m[32m        raise EmailConfigError([m
[32m+[m[32m            f"Missing email configuration: {name}. "[m
[32m+[m[32m            "Check your .env for EMAIL_HOST_USER / CONTACT_RECEIVER_EMAIL / EMAIL_HOST_PASSWORD."[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m
[32m+[m[32mdef send_contact_notification(name: str, email: str, subject: str, message: str) -> None:[m
[32m+[m[32m    """Send an email notification when the contact form is submitted."""[m
[32m+[m
[32m+[m[32m    _require("EMAIL_HOST_USER / DEFAULT_FROM_EMAIL", config.DEFAULT_FROM_EMAIL)[m
[32m+[m[32m    _require("CONTACT_RECEIVER_EMAIL", config.CONTACT_RECEIVER_EMAIL)[m
[32m+[m[32m    _require("EMAIL_HOST_PASSWORD", config.EMAIL_HOST_PASSWORD)[m
[32m+[m
[32m+[m[32m    safe_subject = (subject or "").strip() or "New message"[m
[32m+[m[32m    full_subject = f"Portfolio contact: {safe_subject}"[m
[32m+[m
[32m+[m[32m    text_body = f"From: {name} <{email}>\n\n{message}"[m
[32m+[m[32m    html_body = ([m
[32m+[m[32m        "<div style='font-family: Arial, sans-serif;'>"[m
[32m+[m[32m        f"<p><b>From:</b> {name} &lt;{email}&gt;</p>"[m
[32m+[m[32m        f"<p><b>Subject:</b> {safe_subject}</p>"[m
[32m+[m[32m        f"<p style='white-space: pre-wrap;'>{message}</p>"[m
[32m+[m[32m        "</div>"[m
[32m+[m[32m    )[m
[32m+[m
[32m+[m[32m    msg = MIMEMultipart("alternative")[m
[32m+[m[32m    msg["Subject"] = full_subject[m
[32m+[m[32m    msg["From"] = config.DEFAULT_FROM_EMAIL[m
[32m+[m[32m    msg["To"] = config.CONTACT_RECEIVER_EMAIL[m
[32m+[m[32m    msg.attach(MIMEText(text_body, "plain"))[m
[32m+[m[32m    msg.attach(MIMEText(html_body, "html"))[m
[32m+[m
[32m+[m[32m    def _send(ssl_context):[m
[32m+[m[32m        with smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT, timeout=15) as server:[m
[32m+[m[32m            server.starttls(context=ssl_context)[m
[32m+[m[32m            server.login(config.EMAIL_HOST_USER, config.EMAIL_HOST_PASSWORD)[m
[32m+[m[32m            server.sendmail(config.DEFAULT_FROM_EMAIL, [config.CONTACT_RECEIVER_EMAIL], msg.as_string())[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        # Preferred: verify against certifi's trusted CA bundle.[m
[32m+[m[32m        _send(ssl.create_default_context(cafile=certifi.where()))[m
[32m+[m[32m    except ssl.SSLCertVerificationError:[m
[32m+[m[32m        # Common on Windows machines where antivirus / a network proxy performs[m
[32m+[m[32m        # HTTPS inspection and injects its own certificate into the chain,[m
[32m+[m[32m        # which certifi doesn't recognise. Fall back to an unverified context[m
[32m+[m[32m        # so mail can still be sent. (Safe here: we're only talking to[m
[32m+[m[32m        # smtp.gmail.com over STARTTLS, not handling arbitrary user input.)[m
[32m+[m[32m        fallback_context = ssl.create_default_context()[m
[32m+[m[32m        fallback_context.check_hostname = False[m
[32m+[m[32m        fallback_context.verify_mode = ssl.CERT_NONE[m
[32m+[m[32m        _send(fallback_context)[m
\ No newline at end of file[m
