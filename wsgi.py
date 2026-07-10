"""
WSGI entry point for production servers (e.g. gunicorn).
Usage: gunicorn wsgi:application
"""

from app import application  # noqa: F401

# Vercel's @vercel/python WSGI runtime looks for a variable named `app` by
# convention (Flask-style). Expose an alias so it's found regardless of
# which name it expects.
app = application