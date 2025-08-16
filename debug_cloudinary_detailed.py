#!/usr/bin/env python
"""
Detailed Cloudinary debugging to find the exact issue
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

def debug_cloudinary():
    print("🔍 DETAILED CLOUDINARY DEBUGGING")
    print("=" * 60)
    
    # 1. Check environment variables
    print("1️⃣ Environment Variables:")
    env_vars = {
        'PRODUCTION': os.environ.get('PRODUCTION'),
        'CLOUDINARY_CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'CLOUDINARY_API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'CLOUDINARY_API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
    
    for key, value in env_vars.items():
        if key == 'CLOUDINARY_API_SECRET':
            display_value = "SET" if value else "NOT SET"
        else:
            display_value = value if value else "NOT SET"
        print(f"   {key}: {display_value}")
    
    print()
    
    # 2. Check Django settings
    print("2️⃣ Django Settings:")
    from django.conf import settings
    
    production_check = os.environ.get('PRODUCTION') == 'True'
    print(f"   PRODUCTION == 'True': {production_check}")
    
    try:
        default_storage = getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')
        print(f"   DEFAULT_FILE_STORAGE: {default_storage}")
        
        media_url = getattr(settings, 'MEDIA_URL', 'NOT SET')
        print(f"   MEDIA_URL: {media_url}")
        
        cloudinary_storage = getattr(settings, 'CLOUDINARY_STORAGE', {})
        print(f"   CLOUDINARY_STORAGE: {cloudinary_storage}")
        
    except Exception as e:
        print(f"   ❌ Error reading settings: {e}")
    
    print()
    
    # 3. Check actual storage backend
    print("3️⃣ Current Storage Backend:")
    try:
        from django.core.files.storage import default_storage
        
        storage_class = default_storage.__class__
        storage_name = storage_class.__name__
        storage_module = storage_class.__module__
        
        print(f"   Class: {storage_name}")
        print(f"   Module: {storage_module}")
        
        if 'cloudinary' in storage_module.lower():
            print("   ✅ Using Cloudinary storage!")
        else:
            print("   ❌ NOT using Cloudinary storage")
            
    except Exception as e:
        print(f"   ❌ Error checking storage: {e}")
    
    print()
    
    # 4. Test Cloudinary connection
    print("4️⃣ Cloudinary Connection Test:")
    try:
        import cloudinary
        import cloudinary.api
        
        # Check configuration
        config = cloudinary.config()
        print(f"   Cloud Name: {getattr(config, 'cloud_name', 'NOT SET')}")
        print(f"   API Key: {getattr(config, 'api_key', 'NOT SET')}")
        print(f"   Secure: {getattr(config, 'secure', 'NOT SET')}")
        
        # Test API connection
        try:
            result = cloudinary.api.ping()
            print(f"   ✅ API Ping: {result}")
        except Exception as ping_error:
            print(f"   ❌ API Ping Failed: {ping_error}")
            
    except ImportError as e:
        print(f"   ❌ Cloudinary import failed: {e}")
    except Exception as e:
        print(f"   ❌ Cloudinary error: {e}")
    
    print()
    
    # 5. Show the exact issue
    print("5️⃣ Diagnosis:")
    
    if env_vars['PRODUCTION'] != 'True':
        print("   🚨 PRODUCTION is not set to 'True'")
        print("   ➡️ Fix: Set PRODUCTION=True in Render environment variables")
    elif not env_vars['CLOUDINARY_CLOUD_NAME']:
        print("   🚨 CLOUDINARY_CLOUD_NAME is not set")
        print("   ➡️ Fix: Set CLOUDINARY_CLOUD_NAME=dturwm5za in Render")
    elif not env_vars['CLOUDINARY_API_KEY']:
        print("   🚨 CLOUDINARY_API_KEY is not set")
        print("   ➡️ Fix: Set CLOUDINARY_API_KEY=423825422946229 in Render")
    elif not env_vars['CLOUDINARY_API_SECRET']:
        print("   🚨 CLOUDINARY_API_SECRET is not set")
        print("   ➡️ Fix: Set CLOUDINARY_API_SECRET=0PWTYCAylXuGUiKOwhS1eX6rBPY in Render")
    else:
        print("   ✅ Environment variables look correct")
        print("   🔍 Check DEFAULT_FILE_STORAGE and storage backend above")
    
    print()
    print("=" * 60)

if __name__ == '__main__':
    debug_cloudinary()