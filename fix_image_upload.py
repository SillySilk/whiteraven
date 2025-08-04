#!/usr/bin/env python
"""
Fix image upload issues by simplifying validation and testing the process.
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from menu.models import MenuItem
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
import io

def test_image_upload():
    """
    Test the image upload process with a simple test image.
    """
    print("=== Testing Image Upload Process ===")
    
    # Create a simple test image
    print("1. Creating test image...")
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG', quality=85)
    img_io.seek(0)
    
    # Create uploaded file
    test_image = SimpleUploadedFile(
        name='test-coffee.jpg',
        content=img_io.getvalue(),
        content_type='image/jpeg'
    )
    
    print(f"   - Image size: {len(test_image.read())} bytes")
    print(f"   - Content type: {test_image.content_type}")
    print(f"   - File name: {test_image.name}")
    test_image.seek(0)  # Reset file pointer
    
    # Try to create/update a menu item with image
    print("\n2. Testing menu item creation with image...")
    try:
        # Get or create a test menu item
        from menu.models import Category
        category, _ = Category.objects.get_or_create(
            name="Test Category",
            defaults={'description': 'Test category for image upload'}
        )
        
        menu_item, created = MenuItem.objects.get_or_create(
            name="Test Coffee Item",
            defaults={
                'description': 'Test item for image upload',
                'price': 4.95,
                'category': category,
            }
        )
        
        print(f"   - Menu item: {'Created' if created else 'Found existing'}")
        
        # Try to add the image
        print("\n3. Attempting to add image to menu item...")
        menu_item.image = test_image
        menu_item.save()
        
        print("   ✅ SUCCESS: Image uploaded successfully!")
        print(f"   - Image path: {menu_item.image.name}")
        print(f"   - Image URL: {menu_item.image.url}")
        
        # Test image methods
        print("\n4. Testing image methods...")
        print(f"   - Has image: {menu_item.has_image()}")
        print(f"   - Display URL: {menu_item.get_display_image_url()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def simplify_image_validation():
    """
    Create a simplified version of image validation that's less strict.
    """
    print("\n=== Creating Simplified Image Validation ===")
    
    simplified_validate = """
def validate_image_simple(image_file):
    '''
    Simplified image validation - less strict but still secure.
    '''
    try:
        from PIL import Image
        import os
        
        # Basic file size check (5MB max)
        if hasattr(image_file, 'size') and image_file.size > 5 * 1024 * 1024:
            return False, "Image file too large. Maximum size is 5MB."
        
        # Check file extension
        if hasattr(image_file, 'name'):
            ext = os.path.splitext(image_file.name.lower())[1]
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                return False, f"Unsupported file extension. Allowed: .jpg, .jpeg, .png, .webp"
        
        # Try to open and verify the image
        try:
            with Image.open(image_file) as img:
                img.verify()
                image_file.seek(0)  # Reset file pointer
                
            with Image.open(image_file) as img:
                # Check format
                if img.format not in ['JPEG', 'PNG', 'WEBP']:
                    return False, f"Unsupported image format. Allowed: JPEG, PNG, WEBP"
        except Exception as e:
            return False, "Invalid or corrupted image file."
            
        image_file.seek(0)  # Reset file pointer
        return True, None
        
    except Exception as e:
        return False, f"Error validating image: {e}"
"""
    
    print("Created simplified validation function.")
    return simplified_validate

def check_admin_theme_public_usage():
    """
    Check if django-admin-interface can be used for public website theming.
    """
    print("\n=== Checking Admin Theme Public Usage ===")
    
    try:
        from admin_interface.models import Theme
        
        # Get the current theme
        active_theme = Theme.objects.filter(active=True).first()
        
        if active_theme:
            print(f"✅ Found active theme: {active_theme.name}")
            print(f"   - Header background: {active_theme.css_header_background_color}")
            print(f"   - Module text: {active_theme.css_module_text_color}")
            print(f"   - Generic link: {active_theme.css_generic_link_color}")
            
            # Check if theme colors can be accessed in templates
            print("\n📋 Admin Interface Theme Scope:")
            print("   ❌ Admin themes only affect Django admin interface")
            print("   ❌ Cannot directly style public website")
            print("   ✅ Colors can be extracted for use in public CSS")
            
            # Show how to use theme colors in public site
            usage_example = f"""
<!-- In your base template -->
<style>
:root {{
    --admin-primary: {active_theme.css_header_background_color};
    --admin-text: {active_theme.css_module_text_color};
    --admin-link: {active_theme.css_generic_link_color};
}}

/* Use in public site styles */
.navbar {{
    background-color: var(--admin-primary);
}}

.content-text {{
    color: var(--admin-text);
}}

.links {{
    color: var(--admin-link);
}}
</style>
            """
            
            print("\n💡 Solution: Create context processor to pass theme colors to public templates")
            return active_theme
        else:
            print("❌ No active theme found")
            return None
            
    except Exception as e:
        print(f"❌ Error checking theme: {e}")
        return None

def create_theme_context_processor():
    """
    Create a context processor to pass admin theme colors to public templates.
    """
    print("\n=== Creating Theme Context Processor ===")
    
    context_processor_code = '''
"""
Context processor to make admin theme colors available to public templates.
"""

def admin_theme_colors(request):
    """
    Add admin interface theme colors to template context.
    """
    try:
        from admin_interface.models import Theme
        
        active_theme = Theme.objects.filter(active=True).first()
        
        if active_theme:
            return {
                'theme_colors': {
                    'primary': active_theme.css_header_background_color,
                    'primary_text': active_theme.css_header_text_color,
                    'content_bg': active_theme.css_module_background_color,
                    'content_text': active_theme.css_module_text_color,
                    'link_color': active_theme.css_generic_link_color,
                    'link_hover': active_theme.css_generic_link_hover_color,
                    'button_bg': active_theme.css_save_button_background_color,
                    'button_text': active_theme.css_save_button_text_color,
                }
            }
    except Exception:
        pass
    
    # Fallback colors if no theme or error
    return {
        'theme_colors': {
            'primary': '#2E5A3B',
            'primary_text': '#FFFFFF', 
            'content_bg': '#FFFFFF',
            'content_text': '#2C2C2C',
            'link_color': '#2E5A3B',
            'link_hover': '#1A3B24',
            'button_bg': '#2E5A3B',
            'button_text': '#FFFFFF',
        }
    }
'''
    
    # Write the context processor
    with open('core/theme_context.py', 'w') as f:
        f.write(context_processor_code)
    
    print("✅ Created theme context processor at core/theme_context.py")
    
    settings_addition = '''
# Add to TEMPLATES context_processors in settings.py:
'core.theme_context.admin_theme_colors',
'''
    
    print("📋 Next step: Add to settings.py TEMPLATES context_processors:")
    print(settings_addition)
    
    template_usage = '''
<!-- Usage in templates -->
<style>
:root {
    --primary-color: {{ theme_colors.primary }};
    --primary-text: {{ theme_colors.primary_text }};
    --content-bg: {{ theme_colors.content_bg }};
    --content-text: {{ theme_colors.content_text }};
    --link-color: {{ theme_colors.link_color }};
    --link-hover: {{ theme_colors.link_hover }};
}

/* Apply to your CSS */
body { 
    background: var(--content-bg); 
    color: var(--content-text); 
}
.navbar { 
    background: var(--primary-color); 
    color: var(--primary-text); 
}
a { 
    color: var(--link-color); 
}
a:hover { 
    color: var(--link-hover); 
}
</style>
'''
    
    print("\n📋 Template usage example:")
    print(template_usage)

if __name__ == "__main__":
    print("White Raven Pourhouse - Image Upload & Theme Diagnostic Tool")
    print("=" * 60)
    
    # Test 1: Image upload process
    image_success = test_image_upload()
    
    # Test 2: Check admin theme for public usage
    active_theme = check_admin_theme_public_usage()
    
    # Test 3: Create context processor for theme integration
    if active_theme:
        create_theme_context_processor()
    
    # Test 4: Create simplified validation if needed
    if not image_success:
        print("\n🔧 Creating simplified image validation...")
        simplified_validate = simplify_image_validation()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"✅ Image Upload: {'Working' if image_success else 'Needs fix'}")
    print(f"✅ Admin Theme: {'Found' if active_theme else 'Not found'}")
    print("📋 Next Steps:")
    
    if not image_success:
        print("   1. Apply simplified image validation")
        print("   2. Test image upload in admin")
    
    if active_theme:
        print("   3. Add theme context processor to settings")
        print("   4. Update public templates to use theme colors")
        print("   5. Test public website with admin theme colors")
    
    print("\n🎯 Goal: Sync admin theme colors with public website for consistency")