#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from django.test import Client
from django.urls import reverse

# Test the home view
client = Client()
response = client.get('/')

print(f"Status Code: {response.status_code}")
print(f"Content Type: {response.get('Content-Type', 'Unknown')}")
print(f"Content Length: {len(response.content)}")
print("\n--- RESPONSE CONTENT ---")
print(response.content.decode('utf-8')[:1000])  # First 1000 characters
print("--- END CONTENT ---")

# Test if templates directory exists
import os
templates_dir = os.path.join(os.getcwd(), 'templates', 'core')
print(f"\nTemplates directory exists: {os.path.exists(templates_dir)}")
home_template = os.path.join(templates_dir, 'home.html')
print(f"Home template exists: {os.path.exists(home_template)}")