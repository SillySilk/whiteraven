#!/usr/bin/env python
"""
Production setup script for White Raven Pourhouse
Sets up all database content, business info, and admin theme
"""
import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from core.models import BusinessInfo
from menu.models import Category, MenuItem
from staff.models import StaffMember
from django.contrib.auth.models import User
from admin_interface.models import Theme

def setup_business_info():
    """Set up business information"""
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
    
    if created:
        print(f"✓ Created business info: {business_info.name}")
    else:
        print(f"✓ Business info already exists: {business_info.name}")

def setup_admin_theme():
    """Set up the admin interface theme"""
    print("Setting up admin theme...")
    
    # Delete existing themes to avoid conflicts
    Theme.objects.all().delete()
    
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
        
        # Colors inspired by coffee and ravens
        css_header_color='#2c1810',  # Dark coffee brown
        css_header_text_color='#f5f5dc',  # Cream
        css_header_link_color='#daa520',  # Gold
        css_header_link_hover_color='#ffd700',  # Bright gold
        
        css_module_caption_color='#4a3429',  # Medium coffee brown
        css_module_text_color='#f5f5dc',  # Cream
        
        css_generic_link_color='#8B4513',  # Saddle brown
        css_generic_link_hover_color='#a0522d',  # Sienna
        
        css_save_button_bg_color='#228B22',  # Forest green
        css_save_button_bg_hover_color='#32CD32',  # Lime green
        css_save_button_text_color='#ffffff',
        
        css_delete_button_bg_color='#DC143C',  # Crimson
        css_delete_button_bg_hover_color='#FF6347',  # Tomato
        css_delete_button_text_color='#ffffff',
        
        list_filter_dropdown=True,
        related_modal=True,
        
        css='/* Custom CSS for White Raven Pourhouse */\n'
            '.module h2, .module caption, .inline-group h2 {\n'
            '    background: linear-gradient(135deg, #2c1810 0%, #4a3429 100%);\n'
            '    color: #f5f5dc;\n'
            '}\n'
            '.breadcrumbs {\n'
            '    background: #4a3429;\n'
            '    color: #f5f5dc;\n'
            '}\n'
            '.breadcrumbs a {\n'
            '    color: #daa520;\n'
            '}\n'
    )
    
    print(f"✓ Created admin theme: {theme.name}")

def setup_menu_categories():
    """Set up menu categories"""
    print("Setting up menu categories...")
    
    categories_data = [
        {
            'name': 'Signature Coffee',
            'description': 'Our house-roasted specialty coffee drinks',
            'display_order': 1,
            'is_active': True
        },
        {
            'name': 'Espresso Bar',
            'description': 'Classic espresso-based beverages',
            'display_order': 2,
            'is_active': True
        },
        {
            'name': 'Cold Brew & Iced',
            'description': 'Refreshing cold coffee beverages',
            'display_order': 3,
            'is_active': True
        },
        {
            'name': 'Tea & Alternative',
            'description': 'Premium teas and non-coffee beverages',
            'display_order': 4,
            'is_active': True
        },
        {
            'name': 'Fresh Pastries',
            'description': 'Daily-baked pastries and treats',
            'display_order': 5,
            'is_active': True
        },
        {
            'name': 'Light Meals',
            'description': 'Sandwiches, salads, and light fare',
            'display_order': 6,
            'is_active': True
        }
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"✓ Created category: {category.name}")
        else:
            print(f"✓ Category already exists: {category.name}")

def setup_menu_items():
    """Set up menu items"""
    print("Setting up menu items...")
    
    # Get categories
    signature = Category.objects.get(name='Signature Coffee')
    espresso = Category.objects.get(name='Espresso Bar')
    cold_brew = Category.objects.get(name='Cold Brew & Iced')
    tea = Category.objects.get(name='Tea & Alternative')
    pastries = Category.objects.get(name='Fresh Pastries')
    meals = Category.objects.get(name='Light Meals')
    
    menu_items = [
        # Signature Coffee
        {
            'name': 'White Raven Blend',
            'description': 'Our signature house blend with notes of chocolate and caramel',
            'price': Decimal('4.50'),
            'category': signature,
            'available': True,
            'is_featured': True
        },
        {
            'name': 'Single Origin Ethiopian',
            'description': 'Bright and fruity with floral notes',
            'price': Decimal('5.25'),
            'category': signature,
            'available': True,
            'is_featured': True
        },
        {
            'name': 'Dark Roast Pour Over',
            'description': 'Rich and bold, perfect for dark roast lovers',
            'price': Decimal('4.75'),
            'category': signature,
            'available': True
        },
        
        # Espresso Bar
        {
            'name': 'Espresso',
            'description': 'Classic double shot',
            'price': Decimal('2.75'),
            'category': espresso,
            'available': True
        },
        {
            'name': 'Cappuccino',
            'description': 'Perfect balance of espresso, steamed milk, and foam',
            'price': Decimal('4.25'),
            'category': espresso,
            'available': True,
            'is_featured': True
        },
        {
            'name': 'Latte',
            'description': 'Smooth espresso with steamed milk',
            'price': Decimal('4.75'),
            'category': espresso,
            'available': True
        },
        {
            'name': 'Mocha',
            'description': 'Espresso with chocolate and steamed milk',
            'price': Decimal('5.25'),
            'category': espresso,
            'available': True
        },
        {
            'name': 'Caramel Macchiato',
            'description': 'Vanilla-flavored latte with caramel drizzle',
            'price': Decimal('5.50'),
            'category': espresso,
            'available': True
        },
        
        # Cold Brew & Iced
        {
            'name': 'Cold Brew',
            'description': 'Smooth, low-acid cold-steeped coffee',
            'price': Decimal('4.25'),
            'category': cold_brew,
            'available': True,
            'is_featured': True
        },
        {
            'name': 'Iced Latte',
            'description': 'Espresso over ice with cold milk',
            'price': Decimal('4.75'),
            'category': cold_brew,
            'available': True
        },
        {
            'name': 'Nitro Cold Brew',
            'description': 'Cold brew infused with nitrogen for creamy texture',
            'price': Decimal('5.00'),
            'category': cold_brew,
            'available': True
        },
        
        # Tea & Alternative
        {
            'name': 'Earl Grey',
            'description': 'Classic bergamot-scented black tea',
            'price': Decimal('3.25'),
            'category': tea,
            'available': True
        },
        {
            'name': 'Chamomile',
            'description': 'Soothing herbal tea',
            'price': Decimal('3.25'),
            'category': tea,
            'available': True
        },
        {
            'name': 'Hot Chocolate',
            'description': 'Rich Belgian chocolate with steamed milk',
            'price': Decimal('4.25'),
            'category': tea,
            'available': True
        },
        
        # Fresh Pastries
        {
            'name': 'Croissant',
            'description': 'Buttery, flaky French pastry',
            'price': Decimal('3.50'),
            'category': pastries,
            'available': True
        },
        {
            'name': 'Blueberry Muffin',
            'description': 'Fresh blueberries in tender muffin',
            'price': Decimal('3.75'),
            'category': pastries,
            'available': True
        },
        {
            'name': 'Chocolate Chip Cookie',
            'description': 'Classic homemade cookie',
            'price': Decimal('2.50'),
            'category': pastries,
            'available': True
        },
        
        # Light Meals
        {
            'name': 'Avocado Toast',
            'description': 'Fresh avocado on artisan bread with sea salt',
            'price': Decimal('8.50'),
            'category': meals,
            'available': True,
            'is_featured': True
        },
        {
            'name': 'Turkey & Swiss Sandwich',
            'description': 'Sliced turkey, Swiss cheese, lettuce, tomato on sourdough',
            'price': Decimal('9.75'),
            'category': meals,
            'available': True
        },
        {
            'name': 'Caesar Salad',
            'description': 'Crisp romaine, parmesan, croutons, Caesar dressing',
            'price': Decimal('8.25'),
            'category': meals,
            'available': True
        }
    ]
    
    for item_data in menu_items:
        item, created = MenuItem.objects.get_or_create(
            name=item_data['name'],
            category=item_data['category'],
            defaults=item_data
        )
        if created:
            print(f"✓ Created menu item: {item.name}")
        else:
            print(f"✓ Menu item already exists: {item.name}")

def setup_staff():
    """Set up staff members"""
    print("Setting up staff members...")
    
    staff_data = [
        {
            'name': 'Rose Woolf',
            'position': 'Owner & Head Barista',
            'bio': 'Passionate about coffee and community, Rose opened White Raven Pourhouse to create a welcoming space where great coffee meets great conversation.',
            'is_active': True,
            'display_order': 1
        },
        {
            'name': 'Emma Thompson',
            'position': 'Lead Barista',
            'bio': 'With 5 years of experience, Emma specializes in latte art and educating customers about coffee origins.',
            'is_active': True,
            'display_order': 2
        },
        {
            'name': 'Marcus Chen',
            'position': 'Pastry Chef',
            'bio': 'Marcus brings fresh pastries and creative seasonal treats to White Raven every morning.',
            'is_active': True,
            'display_order': 3
        }
    ]
    
    for staff_info in staff_data:
        staff, created = StaffMember.objects.get_or_create(
            name=staff_info['name'],
            defaults=staff_info
        )
        if created:
            print(f"✓ Created staff member: {staff.name}")
        else:
            print(f"✓ Staff member already exists: {staff.name}")

def create_superuser():
    """Create superuser if it doesn't exist"""
    print("Checking for superuser...")
    
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser 'admin'...")
        User.objects.create_superuser(
            username='admin',
            email='admin@whiteravenpourhouse.com',
            password='WRaven2024!'
        )
        print("✓ Superuser created - Username: admin, Password: WRaven2024!")
    else:
        print("✓ Superuser already exists")

def main():
    """Run all setup functions"""
    print("🚀 Setting up White Raven Pourhouse production data...")
    print("=" * 50)
    
    try:
        setup_business_info()
        setup_admin_theme()
        setup_menu_categories()
        setup_menu_items()
        setup_staff()
        create_superuser()
        
        print("=" * 50)
        print("✅ Production setup completed successfully!")
        print("\nNext steps:")
        print("1. Visit your admin at: https://whiteraven.onrender.com/admin/")
        print("2. Login with username: admin, password: WRaven2024!")
        print("3. Upload images for menu items in the admin interface")
        print("4. Test the public site functionality")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        raise

if __name__ == '__main__':
    main()