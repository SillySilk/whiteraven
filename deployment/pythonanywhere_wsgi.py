"""
WSGI configuration for White Raven Pourhouse on PythonAnywhere.

This file is specifically configured for PythonAnywhere hosting.
Replace the default WSGI file in PythonAnywhere with this configuration.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Add your project directory to the Python path
# Replace 'yourusername' with your actual PythonAnywhere username
path = '/home/yourusername/white-raven-pourhouse'
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application

# Configure environment for production
os.environ.setdefault('PRODUCTION', 'True')

# Get the WSGI application
application = get_wsgi_application()

# Optional: Add middleware for better error handling in production
try:
    from whitenoise import WhiteNoise
    # WhiteNoise middleware for static files (if needed)
    application = WhiteNoise(application)
    # Add static files directory
    application.add_files('/home/yourusername/static', prefix='/static/')
except ImportError:
    # WhiteNoise not available, PythonAnywhere handles static files
    pass

# Log startup information
import logging
logger = logging.getLogger(__name__)
logger.info("White Raven Pourhouse WSGI application started successfully")