#!/usr/bin/env python
"""
Export data from local database to fixtures that can be loaded in production
"""
import os
import django
import json
from django.core import serializers

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from core.models import BusinessInfo
from menu.models import Category, MenuItem
from staff.models import StaffMember
from admin_interface.models import Theme

def export_data():
    """Export all relevant data to JSON fixtures"""
    print("🔄 Exporting local database data...")
    
    # Export business info
    business_data = serializers.serialize('json', BusinessInfo.objects.all(), indent=2)
    with open('fixtures/business_info.json', 'w') as f:
        f.write(business_data)
    print(f"✓ Exported {BusinessInfo.objects.count()} business info records")
    
    # Export categories
    category_data = serializers.serialize('json', Category.objects.all(), indent=2)
    with open('fixtures/categories.json', 'w') as f:
        f.write(category_data)
    print(f"✓ Exported {Category.objects.count()} categories")
    
    # Export menu items
    menu_data = serializers.serialize('json', MenuItem.objects.all(), indent=2)
    with open('fixtures/menu_items.json', 'w') as f:
        f.write(menu_data)
    print(f"✓ Exported {MenuItem.objects.count()} menu items")
    
    # Export staff
    staff_data = serializers.serialize('json', StaffMember.objects.all(), indent=2)
    with open('fixtures/staff.json', 'w') as f:
        f.write(staff_data)
    print(f"✓ Exported {StaffMember.objects.count()} staff members")
    
    # Export admin themes
    theme_data = serializers.serialize('json', Theme.objects.all(), indent=2)
    with open('fixtures/admin_themes.json', 'w') as f:
        f.write(theme_data)
    print(f"✓ Exported {Theme.objects.count()} admin themes")
    
    print("\n✅ All data exported to fixtures/ directory")
    print("These fixtures can now be loaded in production!")

if __name__ == '__main__':
    # Create fixtures directory if it doesn't exist
    os.makedirs('fixtures', exist_ok=True)
    export_data()