"""
WSGI entry point for production servers (e.g. gunicorn).
Usage: gunicorn wsgi:application
"""

from app import application  # noqa: F401
