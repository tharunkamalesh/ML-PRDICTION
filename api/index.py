"""
Vercel Serverless Function entry point for HealthAI Flask backend.
Exports the WSGI application instance 'app' for Vercel Python runtime.
"""

import os
import sys

# Ensure repository root and backend directory are in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.app import app

# Vercel looks for the WSGI/ASGI application callable named 'app'
__all__ = ["app"]
