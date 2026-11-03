"""Vercel entry point for CodeArena. Re-exports the Flask app in app.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app  # noqa: E402,F401  (Vercel looks for `app`)
