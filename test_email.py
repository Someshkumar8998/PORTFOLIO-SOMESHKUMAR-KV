"""
Standalone email test — run this directly to check your .env email settings
without going through the browser at all.

Usage:
    python test_email.py
"""

import config
import mailer

print("Checking configuration loaded from .env ...")
print(f"  EMAIL_HOST_USER       = {config.EMAIL_HOST_USER!r}")
print(f"  DEFAULT_FROM_EMAIL     = {config.DEFAULT_FROM_EMAIL!r}")
print(f"  CONTACT_RECEIVER_EMAIL = {config.CONTACT_RECEIVER_EMAIL!r}")
pw = config.EMAIL_HOST_PASSWORD
print(f"  EMAIL_HOST_PASSWORD    = {'(set, length ' + str(len(pw)) + ')' if pw else '(NOT SET)'}")
print()

if not config.EMAIL_HOST_USER or config.EMAIL_HOST_USER == "youractualgmail@gmail.com":
    print("PROBLEM: EMAIL_HOST_USER is missing or still the placeholder value.")
    print("Fix: open .env and set it to your real Gmail address.")
    raise SystemExit(1)

if not config.EMAIL_HOST_PASSWORD:
    print("PROBLEM: EMAIL_HOST_PASSWORD is missing.")
    print("Fix: open .env and set it to your 16-character Gmail App Password (no spaces).")
    raise SystemExit(1)

if not config.CONTACT_RECEIVER_EMAIL or config.CONTACT_RECEIVER_EMAIL == "youractualgmail@gmail.com":
    print("PROBLEM: CONTACT_RECEIVER_EMAIL is missing or still the placeholder value.")
    print("Fix: open .env and set it to the address that should receive messages.")
    raise SystemExit(1)

print("Config looks OK. Attempting to send a real test email now...")
print()

try:
    mailer.send_contact_notification(
        name="Test Script",
        email="test@example.com",
        subject="Test email from test_email.py",
        message="If you're reading this in your inbox, email sending works!",
    )
    print("SUCCESS: email sent. Check your inbox (and spam folder).")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
    print()
    print("Common causes:")
    print("  - Using your normal Gmail password instead of an App Password")
    print("  - 2-Step Verification not enabled on the Gmail account")
    print("  - Extra spaces left in the App Password in .env")
    print("  - .env file was actually saved as .env.txt (check with: dir -Force)")