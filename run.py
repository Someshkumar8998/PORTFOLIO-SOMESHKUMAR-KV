"""
Local development server — pure Python standard library (wsgiref).
Usage: python run.py
"""

from wsgiref.simple_server import make_server

import config
from app import application

if __name__ == "__main__":
    with make_server(config.HOST, config.PORT, application) as httpd:
        print(f"Serving on http://{config.HOST}:{config.PORT}  (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
