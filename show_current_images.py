#!/usr/bin/env python
"""
Show all current image references in the database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from core.models import BusinessInfo, SiteTheme
from menu.models import MenuItem

def show_current_images():
    print("🔍 Current Image References in Database")
    print("=" * 60)
    
    # BusinessInfo images
    print("📋 BusinessInfo (Hero Images):")
    business_infos = BusinessInfo.objects.all()
    for business_info in business_infos:
        if business_info.hero_image:
            print(f"   ✅ Hero Image: {business_info.hero_image.name}")
            print(f"      URL: {business_info.hero_image.url}")
        else:
            print("   ❌ No hero image set")
    
    if not business_infos.exists():
        print("   ❌ No BusinessInfo records found")
    print()
    
    # SiteTheme images
    print("🎨 SiteTheme (Menu Decoration Images):")
    site_themes = SiteTheme.objects.all()
    for theme in site_themes:
        if theme.menu_decoration_image:
            print(f"   ✅ Menu Decoration: {theme.menu_decoration_image.name}")
            print(f"      URL: {theme.menu_decoration_image.url}")
        else:
            print("   ❌ No menu decoration image set")
    
    if not site_themes.exists():
        print("   ❌ No SiteTheme records found")
    print()
    
    # MenuItem images
    print("☕ MenuItem Images:")
    menu_items = MenuItem.objects.all()
    items_with_images = 0
    
    for item in menu_items:
        if item.image:
            print(f"   ✅ {item.name}: {item.image.name}")
            print(f"      URL: {item.image.url}")
            items_with_images += 1
    
    items_without_images = menu_items.count() - items_with_images
    
    print(f"\n   📊 Summary: {items_with_images} items with images, {items_without_images} without")
    
    if items_with_images == 0:
        print("   ❌ No menu item images found")
    print()
    
    # Storage backend info
    print("💾 Storage Configuration:")
    from django.conf import settings
    from django.core.files.storage import default_storage
    
    production = os.environ.get('PRODUCTION', 'False')
    storage_class = default_storage.__class__.__name__
    
    print(f"   PRODUCTION: {production}")
    print(f"   Storage Backend: {storage_class}")
    
    if hasattr(settings, 'DEFAULT_FILE_STORAGE'):
        print(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    
    if hasattr(settings, 'CLOUDINARY_STORAGE'):
        cloudinary_config = settings.CLOUDINARY_STORAGE
        print(f"   Cloudinary Cloud: {cloudinary_config.get('CLOUD_NAME', 'NOT SET')}")
    
    print()
    print("=" * 60)
    print("🎯 Upload Locations:")
    print("   • Site Images Manager: /site-images/")
    print("   • Django Admin: /admin/")
    print("   • Menu Items: /admin/menu/menuitem/")

if __name__ == '__main__':
    show_current_images()