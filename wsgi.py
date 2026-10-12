"""
WSGI Entrypoint for Production Web Servers (Gunicorn / Render)
Exposes the Flask WSGI application instance.
"""
import os
import sys

# Ensure backend directory is in Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from backend.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
