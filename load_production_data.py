#!/usr/bin/env python
"""
Load production data directly using Django ORM
This script recreates all the local data in the production database
"""
import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from core.models import BusinessInfo
from menu.models import Category, MenuItem
from staff.models import Employee
from admin_interface.models import Theme
from django.contrib.auth.models import User

def main():
    print("🚀 Loading production data based on local setup...")
    print("=" * 60)
    
    # Business Info
    print("Setting up business information...")
    business_info, created = BusinessInfo.objects.get_or_create(
        name="White Raven Pourhouse",
        defaults={
            'tagline': 'Artisan Coffee & Community Hub',
            'description': 'A cozy neighborhood coffee shop serving exceptional coffee, fresh pastries, and fostering community connections in the heart of Felton, California.',
            'address': '123 Main Street, Felton, CA 95018',
            'phone': '(831) 555-BREW',
            'email': 'hello@whiteravenpourhouse.com',
            'hours_monday': '6:00 AM - 6:00 PM',
            'hours_tuesday': '6:00 AM - 6:00 PM',
            'hours_wednesday': '6:00 AM - 6:00 PM',
            'hours_thursday': '6:00 AM - 6:00 PM',
            'hours_friday': '6:00 AM - 8:00 PM',
            'hours_saturday': '7:00 AM - 8:00 PM',
            'hours_sunday': '7:00 AM - 6:00 PM',
            'website': 'https://whiteravenpourhouse.com',
            'instagram': '@whiteravenpourhouse',
            'facebook': 'White Raven Pourhouse',
        }
    )
    print(f"✓ Business info: {business_info.name}")
    
    # Admin Theme
    print("Setting up admin theme...")
    Theme.objects.all().delete()  # Remove any existing themes
    theme = Theme.objects.create(
        name='White Raven Theme',
        active=True,
        title='White Raven Pourhouse Admin',
        title_color='#2c1810',
        title_visible=True,
        logo_color='#2c1810',
        logo_visible=True,
        env_name='Production',
        env_visible_in_header=True,
        env_color='#8B4513',
        
        # Coffee-inspired colors
        css_header_color='#2c1810',
        css_header_text_color='#f5f5dc',
        css_header_link_color='#daa520',
        css_header_link_hover_color='#ffd700',
        
        css_module_caption_color='#4a3429',
        css_module_text_color='#f5f5dc',
        
        css_generic_link_color='#8B4513',
        css_generic_link_hover_color='#a0522d',
        
        css_save_button_bg_color='#228B22',
        css_save_button_bg_hover_color='#32CD32',
        css_save_button_text_color='#ffffff',
        
        css_delete_button_bg_color='#DC143C',
        css_delete_button_bg_hover_color='#FF6347',
        css_delete_button_text_color='#ffffff',
        
        list_filter_dropdown=True,
        related_modal=True,
    )
    print(f"✓ Admin theme: {theme.name}")
    
    # Categories
    print("Setting up menu categories...")
    categories_data = [
        ('Signature Coffee', 'Our house-roasted specialty coffee drinks', 1),
        ('Espresso Bar', 'Classic espresso-based beverages', 2),
        ('Cold Brew & Iced', 'Refreshing cold coffee beverages', 3),
        ('Tea & Alternative', 'Premium teas and non-coffee beverages', 4),
        ('Fresh Pastries', 'Daily-baked pastries and treats', 5),
        ('Light Meals', 'Sandwiches, salads, and light fare', 6),
    ]
    
    categories = {}
    for name, desc, order in categories_data:
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={
                'description': desc,
                'display_order': order,
                'is_active': True
            }
        )
        categories[name] = category
        print(f"✓ Category: {name}")
    
    # Menu Items
    print("Setting up menu items...")
    menu_items_data = [
        # Signature Coffee
        ('White Raven Blend', 'Our signature house blend with notes of chocolate and caramel', '4.50', 'Signature Coffee', True, True),
        ('Single Origin Ethiopian', 'Bright and fruity with floral notes', '5.25', 'Signature Coffee', True, True),
        ('Dark Roast Pour Over', 'Rich and bold, perfect for dark roast lovers', '4.75', 'Signature Coffee', True, False),
        
        # Espresso Bar
        ('Espresso', 'Classic double shot', '2.75', 'Espresso Bar', True, False),
        ('Cappuccino', 'Perfect balance of espresso, steamed milk, and foam', '4.25', 'Espresso Bar', True, True),
        ('Latte', 'Smooth espresso with steamed milk', '4.75', 'Espresso Bar', True, False),
        ('Mocha', 'Espresso with chocolate and steamed milk', '5.25', 'Espresso Bar', True, False),
        ('Caramel Macchiato', 'Vanilla-flavored latte with caramel drizzle', '5.50', 'Espresso Bar', True, False),
        
        # Cold Brew & Iced
        ('Cold Brew', 'Smooth, low-acid cold-steeped coffee', '4.25', 'Cold Brew & Iced', True, True),
        ('Iced Latte', 'Espresso over ice with cold milk', '4.75', 'Cold Brew & Iced', True, False),
        ('Nitro Cold Brew', 'Cold brew infused with nitrogen for creamy texture', '5.00', 'Cold Brew & Iced', True, False),
        
        # Tea & Alternative
        ('Earl Grey', 'Classic bergamot-scented black tea', '3.25', 'Tea & Alternative', True, False),
        ('Chamomile', 'Soothing herbal tea', '3.25', 'Tea & Alternative', True, False),
        ('Hot Chocolate', 'Rich Belgian chocolate with steamed milk', '4.25', 'Tea & Alternative', True, False),
        
        # Fresh Pastries
        ('Croissant', 'Buttery, flaky French pastry', '3.50', 'Fresh Pastries', True, False),
        ('Blueberry Muffin', 'Fresh blueberries in tender muffin', '3.75', 'Fresh Pastries', True, False),
        ('Chocolate Chip Cookie', 'Classic homemade cookie', '2.50', 'Fresh Pastries', True, False),
        
        # Light Meals
        ('Avocado Toast', 'Fresh avocado on artisan bread with sea salt', '8.50', 'Light Meals', True, True),
        ('Turkey & Swiss Sandwich', 'Sliced turkey, Swiss cheese, lettuce, tomato on sourdough', '9.75', 'Light Meals', True, False),
        ('Caesar Salad', 'Crisp romaine, parmesan, croutons, Caesar dressing', '8.25', 'Light Meals', True, False),
    ]
    
    for name, desc, price, cat_name, available, featured in menu_items_data:
        item, created = MenuItem.objects.get_or_create(
            name=name,
            category=categories[cat_name],
            defaults={
                'description': desc,
                'price': Decimal(price),
                'available': available,
                'is_featured': featured,
            }
        )
        print(f"✓ Menu item: {name}")
    
    # Staff (Employee model is more complex, so we'll skip this for now)
    print("Skipping staff setup - Employee model requires more detailed setup...")
    print("✓ Staff setup can be done manually in admin interface")
    
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
    
    print("=" * 60)
    print("✅ Production data loaded successfully!")
    print("\nAdmin Access:")
    print("URL: https://whiteraven.onrender.com/admin/")
    print("Username: admin")
    print("Password: WRaven2024!")
    print("\nPublic Site: https://whiteraven.onrender.com/")

if __name__ == '__main__':
    main()