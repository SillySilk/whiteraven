#!/usr/bin/env python
"""
Simple fix: Use a basic external image hosting approach that actually works
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

def simple_cloudinary_test():
    """Test if we can manually upload to Cloudinary"""
    print("🧪 Testing Manual Cloudinary Upload")
    print("=" * 50)
    
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Create a simple test image in memory
        from PIL import Image
        import io
        
        # Create a simple 100x100 red square
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        print("📤 Attempting direct Cloudinary upload...")
        
        # Try to upload directly to Cloudinary
        result = cloudinary.uploader.upload(
            img_bytes.getvalue(),
            public_id="test_image_from_django",
            resource_type="image"
        )
        
        print("✅ SUCCESS! Cloudinary upload worked!")
        print(f"   URL: {result['secure_url']}")
        print(f"   Public ID: {result['public_id']}")
        
        return True, result['secure_url']
        
    except Exception as e:
        print(f"❌ Cloudinary upload failed: {e}")
        return False, None

def check_django_file_field():
    """Test Django's file field behavior"""
    print("\n🔍 Testing Django File Field Behavior")
    print("=" * 50)
    
    from core.models import BusinessInfo
    from django.core.files.storage import default_storage
    
    print(f"Storage backend: {default_storage.__class__.__name__}")
    print(f"Storage module: {default_storage.__class__.__module__}")
    
    # Check current business info
    business_info = BusinessInfo.objects.first()
    if business_info and business_info.hero_image:
        print(f"Current hero image:")
        print(f"   Name: {business_info.hero_image.name}")
        print(f"   URL: {business_info.hero_image.url}")
        
        # Try to get the actual storage backend for this field
        field_storage = business_info.hero_image.storage
        print(f"Field storage: {field_storage.__class__.__name__}")
    else:
        print("No hero image currently set")

def create_simple_fix():
    """Create a simple, working solution"""
    print("\n🔧 Creating Simple Fix")
    print("=" * 50)
    
    # Test manual upload first
    upload_success, test_url = simple_cloudinary_test()
    
    if upload_success:
        print("✅ Cloudinary connection works!")
        print("💡 The issue is in Django's file field configuration")
        print("\n🎯 Recommendation:")
        print("   1. Upload images manually to Cloudinary dashboard")
        print("   2. Use those URLs directly in database")
        print("   3. Skip Django's file upload system temporarily")
        
        return True
    else:
        print("❌ Cloudinary connection doesn't work")
        print("\n🎯 Alternative approaches:")
        print("   1. Use a simple external service like ImgBB")
        print("   2. Store images in GitHub and serve from there")
        print("   3. Use a basic S3 setup")
        
        return False

if __name__ == '__main__':
    print("🔍 SIMPLE IMAGE STORAGE DIAGNOSTICS")
    print("=" * 60)
    
    check_django_file_field()
    working = create_simple_fix()
    
    print("\n" + "=" * 60)
    if working:
        print("✅ Cloudinary works - Django integration issue")
    else:
        print("❌ Need alternative image hosting solution")