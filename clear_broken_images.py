#!/usr/bin/env python
"""
Clear broken image references from database to force fresh uploads to Cloudinary
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from core.models import BusinessInfo, SiteTheme
from menu.models import MenuItem

def clear_broken_images():
    print("🧹 Clearing broken image references from database...")
    print("=" * 60)
    
    # Clear BusinessInfo images
    print("📋 Clearing BusinessInfo images...")
    business_infos = BusinessInfo.objects.all()
    for business_info in business_infos:
        if business_info.hero_image:
            print(f"   Removing broken hero image: {business_info.hero_image.name}")
            business_info.hero_image = None
            business_info.save()
    
    # Clear SiteTheme images
    print("🎨 Clearing SiteTheme images...")
    site_themes = SiteTheme.objects.all()
    for theme in site_themes:
        if theme.menu_decoration_image:
            print(f"   Removing broken menu decoration image: {theme.menu_decoration_image.name}")
            theme.menu_decoration_image = None
            theme.save()
    
    # Clear MenuItem images
    print("☕ Clearing MenuItem images...")
    menu_items = MenuItem.objects.all()
    cleared_items = 0
    for item in menu_items:
        if item.image:
            print(f"   Removing broken image for '{item.name}': {item.image.name}")
            item.image = None
            item.save()
            cleared_items += 1
    
    print()
    print("=" * 60)
    print("✅ Image cleanup completed!")
    print()
    print(f"🗑️  Cleared {cleared_items} menu item images")
    print("📸 All image fields are now empty and ready for fresh uploads")
    print()
    print("🎯 Next steps:")
    print("   1. Go to /site-images/ to upload hero and decoration images")
    print("   2. Go to /admin/ to upload menu item images")
    print("   3. New uploads will go directly to Cloudinary")
    print("   4. Images will persist across all future deployments")
    print()
    print("🔗 Upload URLs:")
    print("   • Site Images: https://whiteraven.onrender.com/site-images/")
    print("   • Admin: https://whiteraven.onrender.com/admin/")

if __name__ == '__main__':
    clear_broken_images()