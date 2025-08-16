#!/usr/bin/env python
"""
Test Cloudinary configuration and connection
"""
import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

def test_cloudinary_connection():
    print("🔍 Testing Cloudinary Configuration...")
    print("=" * 50)
    
    # Test environment variables
    print("📋 Environment Variables:")
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'NOT SET')
    api_key = os.environ.get('CLOUDINARY_API_KEY', 'NOT SET')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', 'NOT SET')
    production = os.environ.get('PRODUCTION', 'NOT SET')
    
    print(f"   CLOUDINARY_CLOUD_NAME: {cloud_name}")
    print(f"   CLOUDINARY_API_KEY: {api_key}")
    print(f"   CLOUDINARY_API_SECRET: {'SET' if api_secret != 'NOT SET' else 'NOT SET'}")
    print(f"   PRODUCTION: {production}")
    print()
    
    # Test Django settings
    print("⚙️  Django Settings:")
    from django.conf import settings
    
    try:
        storage_backend = getattr(settings, 'DEFAULT_FILE_STORAGE', 'NOT SET')
        print(f"   DEFAULT_FILE_STORAGE: {storage_backend}")
        
        cloudinary_config = getattr(settings, 'CLOUDINARY_STORAGE', {})
        print(f"   CLOUDINARY_STORAGE: {cloudinary_config}")
        
        media_url = getattr(settings, 'MEDIA_URL', 'NOT SET')
        print(f"   MEDIA_URL: {media_url}")
        print()
        
    except Exception as e:
        print(f"   ❌ Error reading settings: {e}")
        print()
    
    # Test Cloudinary import and connection
    print("☁️  Cloudinary Connection Test:")
    try:
        import cloudinary
        import cloudinary.api
        
        # Test API connection
        result = cloudinary.api.ping()
        print(f"   ✅ Cloudinary API ping successful: {result}")
        
        # Test configuration
        config = cloudinary.config()
        print(f"   ✅ Cloud name: {config.cloud_name}")
        print(f"   ✅ API key: {config.api_key}")
        print(f"   ✅ Secure: {config.secure}")
        print()
        
    except Exception as e:
        print(f"   ❌ Cloudinary connection failed: {e}")
        print()
    
    # Test actual storage
    print("💾 Storage Backend Test:")
    try:
        from django.core.files.storage import default_storage
        storage_class = default_storage.__class__.__name__
        print(f"   Current storage class: {storage_class}")
        
        if 'Cloudinary' in storage_class:
            print("   ✅ Using Cloudinary storage!")
        else:
            print("   ⚠️  Using local file storage")
            
    except Exception as e:
        print(f"   ❌ Storage test failed: {e}")
    
    print()
    print("=" * 50)
    print("🎯 Summary:")
    
    if production == 'True' and cloud_name != 'NOT SET':
        print("   Configuration looks correct for production")
        print("   If images are still not persisting, check:")
        print("   1. Render environment variables are saved")
        print("   2. Deployment completed successfully")
        print("   3. Try uploading a new image to test")
    else:
        print("   ⚠️  Configuration issues detected")
        print("   1. Ensure PRODUCTION=True in Render")
        print("   2. Ensure all Cloudinary variables are set")

if __name__ == '__main__':
    test_cloudinary_connection()