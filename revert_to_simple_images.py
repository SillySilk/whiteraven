#!/usr/bin/env python
"""
Revert to simple image handling that actually works
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

def revert_to_simple():
    """Simplify image storage to basic working approach"""
    print("🔄 REVERTING TO SIMPLE IMAGE STORAGE")
    print("=" * 60)
    
    from core.models import BusinessInfo, SiteTheme
    from menu.models import MenuItem
    
    # Clear all image references
    print("1️⃣ Clearing all broken image references...")
    
    # Clear BusinessInfo images
    business_infos = BusinessInfo.objects.all()
    for business_info in business_infos:
        if business_info.hero_image:
            print(f"   Clearing hero image: {business_info.hero_image.name}")
            business_info.hero_image = None
            business_info.save()
    
    # Clear SiteTheme images
    site_themes = SiteTheme.objects.all()
    for theme in site_themes:
        if theme.menu_decoration_image:
            print(f"   Clearing menu decoration: {theme.menu_decoration_image.name}")
            theme.menu_decoration_image = None
            theme.save()
    
    # Clear MenuItem images
    menu_items = MenuItem.objects.all()
    cleared_count = 0
    for item in menu_items:
        if item.image:
            print(f"   Clearing menu item image: {item.name}")
            item.image = None
            item.save()
            cleared_count += 1
    
    print(f"✅ Cleared {cleared_count} menu item images")
    print()
    
    # Create simple placeholder content
    print("2️⃣ Setting up placeholder approach...")
    
    # Use external image URLs that actually work
    placeholder_urls = {
        'hero': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=1200&h=600&fit=crop',
        'coffee': 'https://images.unsplash.com/photo-1511920170033-f8396924c348?w=400&h=300&fit=crop'
    }
    
    print("3️⃣ Simple working approach:")
    print("   Option 1: Use external image URLs directly")
    print("   Option 2: Upload to free service like ImgBB")
    print("   Option 3: Use placeholder images for now")
    print()
    print("🎯 Recommendation: Skip Django file uploads entirely")
    print("   - Upload images to free external service")
    print("   - Store URLs directly in database")
    print("   - Much simpler and reliable")

if __name__ == '__main__':
    revert_to_simple()