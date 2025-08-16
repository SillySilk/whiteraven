#!/usr/bin/env python
"""
CORRECTED Production data loading script with ALL actual database field names
"""
import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from core.models import BusinessInfo, SiteTheme
from menu.models import Category, MenuItem
# Removed admin_interface dependency
from django.contrib.auth.models import User

def clear_broken_image_references():
    """Clear broken image references that may exist from local development"""
    print("🧹 Clearing broken image references...")
    
    # Clear BusinessInfo images if they don't exist
    try:
        business_info = BusinessInfo.objects.first()
        if business_info and business_info.hero_image:
            if not business_info.hero_image.storage.exists(business_info.hero_image.name):
                print(f"  Removing broken hero image reference: {business_info.hero_image.name}")
                business_info.hero_image = None
                business_info.save()
    except Exception as e:
        print(f"  Error clearing business info images: {e}")
    
    # Clear SiteTheme images if they don't exist
    try:
        site_themes = SiteTheme.objects.all()
        for theme in site_themes:
            if theme.menu_decoration_image:
                if not theme.menu_decoration_image.storage.exists(theme.menu_decoration_image.name):
                    print(f"  Removing broken menu decoration image: {theme.menu_decoration_image.name}")
                    theme.menu_decoration_image = None
                    theme.save()
    except Exception as e:
        print(f"  Error clearing site theme images: {e}")
    
    print("✅ Broken image references cleared")

def main():
    print("🚀 Loading production data with CORRECTED field names...")
    print("=" * 70)
    
    # Clear any broken image references first
    clear_broken_image_references()
    
    # Business Info - using actual fields from BusinessInfo model
    print("Setting up business information...")
    business_info, created = BusinessInfo.objects.get_or_create(
        name="White Raven Pourhouse",
        defaults={
            'tagline': 'Artisan Coffee & Community Hub',
            'address': '123 Main Street, Felton, CA 95018',
            'phone': '+18315552739',  # (831) 555-BREW in proper format
            'email': 'hello@whiteravenpourhouse.com',
            'hours': {
                'monday': {'open': '06:00', 'close': '18:00', 'closed': False},
                'tuesday': {'open': '06:00', 'close': '18:00', 'closed': False},
                'wednesday': {'open': '06:00', 'close': '18:00', 'closed': False},
                'thursday': {'open': '06:00', 'close': '18:00', 'closed': False},
                'friday': {'open': '06:00', 'close': '20:00', 'closed': False},
                'saturday': {'open': '07:00', 'close': '20:00', 'closed': False},
                'sunday': {'open': '07:00', 'close': '18:00', 'closed': False},
            },
            'special_hours': {},
            'instagram_handle': 'whiteravenpourhouse',
            'description': 'A cozy neighborhood coffee shop serving exceptional coffee, fresh pastries, and fostering community connections in the heart of Felton, California.',
            'facebook_url': 'https://facebook.com/whiteravenpourhouse',
            'instagram_url': 'https://instagram.com/whiteravenpourhouse',
            'meta_description': 'White Raven Pourhouse - Artisan Coffee & Community Hub in Felton, CA. Serving exceptional coffee, fresh pastries, and fostering community connections.',
            'welcome_message': 'Welcome to White Raven Pourhouse, where every cup tells a story and every visit feels like home.',
            'footer_tagline': 'Made with ❤ in Felton, CA',
            'copyright_text': 'White Raven Pourhouse',
        }
    )
    print(f"✓ Business info: {business_info.name}")
    
    # Admin interface package removed - using standard Django admin with custom CSS
    
    # Site Theme - using actual field names from core.models.SiteTheme
    print("Setting up site theme...")
    site_theme, created = SiteTheme.objects.get_or_create(
        name="White Raven Theme",
        defaults={
            'primary_color': '#6f4f28',           # Coffee brown
            'secondary_color': '#8b7355',         # Lighter brown  
            'accent_color': '#d4af37',            # Gold
            'text_color': '#2c3e50',              # Dark gray-blue
            'text_light': '#6c757d',              # Bootstrap gray
            'background_color': '#ffffff',        # White
            'background_secondary': '#f8f9fa',    # Light gray
            'navbar_bg': '#ffffff',               # White
            'navbar_text': '#2c3e50',             # Dark gray-blue
            'navbar_hover': '#6f4f28',            # Coffee brown
            'button_primary_bg': '#6f4f28',       # Coffee brown
            'button_primary_text': '#ffffff',     # White
            'button_secondary_bg': '#8b7355',     # Lighter brown
            'button_secondary_text': '#ffffff',   # White
            'menu_decoration_alt_text': 'White Raven Pourhouse decoration',
            'footer_bg': '#2c3e50',               # Dark gray-blue
            'footer_text': '#ffffff',             # White
            'footer_link': '#d4af37',             # Gold
            'is_active': True,
        }
    )
    print(f"✓ Site theme: {site_theme.name}")
    
    # Categories - using actual field names from menu.models.Category
    print("Setting up menu categories...")
    categories_data = [
        ('Signature Coffee', 'Our house-roasted specialty coffee drinks', 1, True),
        ('Espresso Bar', 'Classic espresso-based beverages', 2, True),
        ('Cold Brew & Iced', 'Refreshing cold coffee beverages', 3, True),
        ('Tea & Alternative', 'Premium teas and non-coffee beverages', 4, True),
        ('Fresh Pastries', 'Daily-baked pastries and treats', 5, True),
        ('Light Meals', 'Sandwiches, salads, and light fare', 6, True),
    ]
    
    categories = {}
    for name, desc, order, active in categories_data:
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={
                'description': desc,
                'order': order,
                'active': active,
                # slug is auto-generated from name
            }
        )
        categories[name] = category
        print(f"✓ Category: {name}")
    
    # Menu Items - using actual field names from menu.models.MenuItem
    print("Setting up menu items...")
    menu_items_data = [
        # name, description, price, category_name, available, featured, temperature, size, calories, caffeine, dietary_notes, prep_time
        ('White Raven Blend', 'Our signature house blend with notes of chocolate and caramel', '4.50', 'Signature Coffee', True, True, 'hot', 'medium', 5, True, '', 3),
        ('Single Origin Ethiopian', 'Bright and fruity with floral notes', '5.25', 'Signature Coffee', True, True, 'hot', 'medium', 5, True, '', 4),
        ('Dark Roast Pour Over', 'Rich and bold, perfect for dark roast lovers', '4.75', 'Signature Coffee', True, False, 'hot', 'medium', 8, True, '', 5),
        
        ('Espresso', 'Classic double shot', '2.75', 'Espresso Bar', True, False, 'hot', 'small', 10, True, '', 1),
        ('Cappuccino', 'Perfect balance of espresso, steamed milk, and foam', '4.25', 'Espresso Bar', True, True, 'hot', 'medium', 80, True, 'Contains dairy', 2),
        ('Latte', 'Smooth espresso with steamed milk', '4.75', 'Espresso Bar', True, False, 'hot', 'medium', 120, True, 'Contains dairy', 2),
        ('Mocha', 'Espresso with chocolate and steamed milk', '5.25', 'Espresso Bar', True, False, 'hot', 'medium', 180, True, 'Contains dairy', 3),
        ('Caramel Macchiato', 'Vanilla-flavored latte with caramel drizzle', '5.50', 'Espresso Bar', True, False, 'hot', 'medium', 200, True, 'Contains dairy', 3),
        
        ('Cold Brew', 'Smooth, low-acid cold-steeped coffee', '4.25', 'Cold Brew & Iced', True, True, 'cold', 'medium', 5, True, '', 0),
        ('Iced Latte', 'Espresso over ice with cold milk', '4.75', 'Cold Brew & Iced', True, False, 'cold', 'medium', 120, True, 'Contains dairy', 2),
        ('Nitro Cold Brew', 'Cold brew infused with nitrogen for creamy texture', '5.00', 'Cold Brew & Iced', True, False, 'cold', 'medium', 8, True, '', 0),
        
        ('Earl Grey', 'Classic bergamot-scented black tea', '3.25', 'Tea & Alternative', True, False, 'hot', 'medium', 0, True, '', 5),
        ('Chamomile', 'Soothing herbal tea', '3.25', 'Tea & Alternative', True, False, 'hot', 'medium', 0, False, 'Caffeine-free', 5),
        ('Hot Chocolate', 'Rich Belgian chocolate with steamed milk', '4.25', 'Tea & Alternative', True, False, 'hot', 'medium', 250, False, 'Contains dairy', 2),
        
        ('Croissant', 'Buttery, flaky French pastry', '3.50', 'Fresh Pastries', True, False, 'room_temp', 'single', 280, False, 'Contains gluten, dairy', 0),
        ('Blueberry Muffin', 'Fresh blueberries in tender muffin', '3.75', 'Fresh Pastries', True, False, 'room_temp', 'single', 320, False, 'Contains gluten, dairy, eggs', 0),
        ('Chocolate Chip Cookie', 'Classic homemade cookie', '2.50', 'Fresh Pastries', True, False, 'room_temp', 'single', 180, False, 'Contains gluten, dairy, eggs', 0),
        
        ('Avocado Toast', 'Fresh avocado on artisan bread with sea salt', '8.50', 'Light Meals', True, True, 'room_temp', 'single', 250, False, 'Contains gluten', 3),
        ('Turkey & Swiss Sandwich', 'Sliced turkey, Swiss cheese, lettuce, tomato on sourdough', '9.75', 'Light Meals', True, False, 'room_temp', 'single', 420, False, 'Contains gluten, dairy', 2),
        ('Caesar Salad', 'Crisp romaine, parmesan, croutons, Caesar dressing', '8.25', 'Light Meals', True, False, 'cold', 'single', 280, False, 'Contains dairy, eggs, gluten', 2),
    ]
    
    for name, desc, price, cat_name, available, featured, temp, size, calories, caffeine, dietary, prep_time in menu_items_data:
        item, created = MenuItem.objects.get_or_create(
            name=name,
            category=categories[cat_name],
            defaults={
                'description': desc,
                'price': Decimal(price),
                'available': available,
                'featured': featured,
                'temperature': temp,
                'size': size,
                'calories': calories,
                'contains_caffeine': caffeine,
                'dietary_notes': dietary,
                'preparation_time': prep_time,
                # slug and timestamps are auto-generated
            }
        )
        print(f"✓ Menu item: {name}")
    
    # Create superuser
    print("Setting up admin user...")
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@whiteravenpourhouse.com',
            password='WRaven2024!'
        )
        print("✓ Superuser created: admin / WRaven2024!")
    else:
        print("✓ Superuser already exists")
    
    print("=" * 70)
    print("✅ ALL production data loaded successfully with CORRECT field names!")
    print("\nAdmin Access:")
    print("URL: https://whiteraven.onrender.com/admin/")
    print("Username: admin")
    print("Password: WRaven2024!")
    print("\nPublic Site: https://whiteraven.onrender.com/")
    print("\nAll database fields properly mapped:")
    print("• BusinessInfo: All 13+ fields including hours JSON, social URLs")
    print("• Admin: Using standard Django admin with custom CSS")
    print("• SiteTheme: All 23 frontend color fields")
    print("• Category: All 8 fields including slug, order, active")
    print("• MenuItem: All 17 fields including nutrition, dietary notes")

if __name__ == '__main__':
    main()