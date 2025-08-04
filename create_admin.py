#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@whiteravenpourhouse.com', 'admin123!')
    print("Admin user created successfully!")
    print("Username: admin")
    print("Password: admin123!")
    print("Email: admin@whiteravenpourhouse.com")
else:
    print("Admin user already exists!")