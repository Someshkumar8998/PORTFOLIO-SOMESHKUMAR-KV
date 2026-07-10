"""
WSGI entry point for production servers (e.g. gunicorn) and Vercel.
Usage (gunicorn): gunicorn wsgi:application
Vercel's Python runtime specifically looks for a variable named `app`.
"""

from app import application

# Vercel requires the WSGI callable to be exposed as `app`
app = application