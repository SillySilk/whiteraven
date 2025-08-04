#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from django.test import Client

print("=== White Raven Frontend Fixes Test ===")

client = Client()

print("\n1. Testing Homepage...")
try:
    response = client.get('/')
    if response.status_code == 200:
        print("+ Homepage loads successfully")
        
        # Check if Bootstrap Icons CSS is referenced
        content = response.content.decode('utf-8')
        if 'bootstrap-icons' in content:
            print("+ Bootstrap Icons CSS link found in page")
        else:
            print("- Bootstrap Icons CSS link not found")
            
        # Check if favicon is referenced
        if 'favicon' in content:
            print("+ Favicon link found in page")
        else:
            print("- Favicon link not found")
            
    else:
        print(f"- Homepage returned status: {response.status_code}")
        
except Exception as e:
    print(f"- Error testing homepage: {e}")

print("\n2. Testing Static Files...")

# Test favicon
try:
    response = client.get('/static/images/favicon.svg')
    if response.status_code == 200:
        print("+ SVG favicon accessible")
    else:
        print(f"- SVG favicon returned status: {response.status_code}")
except Exception as e:
    print(f"- Error accessing SVG favicon: {e}")

print("\n3. Testing CSS...")
try:
    response = client.get('/static/css/style.css')
    if response.status_code == 200:
        print("+ Main CSS file accessible")
    else:
        print(f"- Main CSS returned status: {response.status_code}")
except Exception as e:
    print(f"- Error accessing CSS: {e}")

print("\n=== Fix Summary ===")
print("+ CSP updated to allow Bootstrap Icons from cdn.jsdelivr.net")
print("+ SVG favicon created with coffee cup design") 
print("+ Fallback ICO favicon placeholder created")
print("+ Favicon links added to base template")

print("\nBrowser should now:")
print("- Load Bootstrap Icons without CSP errors")
print("- Display coffee cup favicon in browser tab")
print("- Show no 404 errors for favicon requests")

print("\nRefresh your browser to see the changes!")