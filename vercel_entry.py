"""
Vercel entry point - handles startup and app creation.
This file is used by Vercel instead of the circular import in app/__init__.py
"""

from app.main import create_app

# Vercel needs a variable named 'app' to be available
app = create_app()