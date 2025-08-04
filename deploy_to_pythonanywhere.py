#!/usr/bin/env python3
"""
Deployment script for White Raven Pourhouse to PythonAnywhere
"""
import os
import requests
import zipfile
import base64
from pathlib import Path

# PythonAnywhere credentials
USERNAME = 'Pourhouse'
TOKEN = 'ce43af1e3154c5bd164ad5dd76fbf88db61161a6'
BASE_URL = f'https://www.pythonanywhere.com/api/v0/user/{USERNAME}'

def create_directory(path):
    """Create directory on PythonAnywhere"""
    response = requests.post(
        f'{BASE_URL}/files/path{path}/',
        headers={'Authorization': f'Token {TOKEN}'}
    )
    return response.status_code

def upload_file(local_path, remote_path):
    """Upload file to PythonAnywhere"""
    try:
        with open(local_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
        
        response = requests.post(
            f'{BASE_URL}/files/path{remote_path}',
            headers={'Authorization': f'Token {TOKEN}'},
            json={'content': content}
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error uploading {local_path}: {e}")
        return False

def create_wsgi_config():
    """Create WSGI configuration file"""
    wsgi_content = '''
import os
import sys

# Add your project directory to sys.path
path = '/home/Pourhouse/whiteraven'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'white_raven_pourhouse.settings'
os.environ['PRODUCTION'] = 'True'

# Database settings
os.environ['DB_NAME'] = 'Pourhouse$whiteraven'
os.environ['DB_USER'] = 'Pourhouse'
os.environ['DB_HOST'] = 'Pourhouse.mysql.pythonanywhere-services.com'

# Static and media settings
os.environ['STATIC_ROOT'] = '/home/Pourhouse/static/'
os.environ['MEDIA_ROOT'] = '/home/Pourhouse/media/'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
'''
    
    response = requests.post(
        f'{BASE_URL}/files/path/var/www/pourhouse_pythonanywhere_com_wsgi.py',
        headers={'Authorization': f'Token {TOKEN}'},
        json={'content': base64.b64encode(wsgi_content.encode()).decode()}
    )
    return response.status_code == 200

def main():
    print("🚀 Starting PythonAnywhere deployment...")
    
    # Create project directories
    print("Creating directories...")
    directories = [
        '/home/Pourhouse/whiteraven',
        '/home/Pourhouse/media',
        '/home/Pourhouse/static',
        '/home/Pourhouse/media/menu',
        '/home/Pourhouse/media/business',
        '/home/Pourhouse/media/admin-interface'
    ]
    
    for directory in directories:
        status = create_directory(directory)
        print(f"  {directory}: {status}")
    
    # Create WSGI config
    print("Creating WSGI config...")
    if create_wsgi_config():
        print("  ✅ WSGI config created")
    else:
        print("  ❌ WSGI config failed")
    
    print("\n📝 Next steps:")
    print("1. Upload project files using git clone or file upload")
    print("2. Create MySQL database: Pourhouse$whiteraven")
    print("3. Install requirements.txt in virtual environment")
    print("4. Run migrations")
    print("5. Configure webapp settings")
    print("6. Your site will be available at: https://Pourhouse.pythonanywhere.com")
    print("\n🔗 Note: You can later link your GoDaddy domain to this webapp")

if __name__ == '__main__':
    main()