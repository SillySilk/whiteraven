#!/usr/bin/env python
import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from menu.models import Category, MenuItem

# Create menu categories based on the real White Raven DoorDash menu
categories_data = [
    {
        "name": "House Coffee",
        "description": "Our signature house coffee blends",
        "order": 1
    },
    {
        "name": "Espresso Drinks", 
        "description": "Classic espresso-based beverages",
        "order": 2
    },
    {
        "name": "Specialty Coffee",
        "description": "Unique coffee creations and cold brews", 
        "order": 3
    }
]

print("Creating White Raven menu categories...")
categories = {}
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data["name"],
        defaults={
            "description": cat_data["description"],
            "order": cat_data["order"]
        }
    )
    categories[cat_data["name"]] = category
    if created:
        print(f"+ Created category: {category.name}")
    else:
        print(f"- Category already exists: {category.name}")

# Real White Raven menu items from DoorDash
menu_items_data = [
    # House Coffee
    {
        "name": "House (20 Oz)",
        "description": "House coffee typically includes our signature blend",
        "price": Decimal("3.00"),
        "category": "House Coffee",
        "featured": True,
        "temperature": "hot",
        "size": "large",
        "contains_caffeine": True,
        "preparation_time": 2
    },
    
    # Cafe Au Lait variations
    {
        "name": "Cafe Au Lait (12 Oz)",
        "description": "Classic French coffee with steamed milk",
        "price": Decimal("3.50"),
        "category": "House Coffee",
        "temperature": "hot",
        "size": "small",
        "contains_caffeine": True,
        "preparation_time": 3
    },
    {
        "name": "Cafe Au Lait (16 Oz)",
        "description": "Classic French coffee with steamed milk",
        "price": Decimal("3.75"),
        "category": "House Coffee",
        "temperature": "hot",
        "size": "medium",
        "contains_caffeine": True,
        "preparation_time": 3
    },
    {
        "name": "Cafe Au Lait (20 Oz)",
        "description": "Classic French coffee with steamed milk",
        "price": Decimal("4.25"),
        "category": "House Coffee",
        "temperature": "hot",
        "size": "large",
        "contains_caffeine": True,
        "preparation_time": 3
    },
    
    # Mocha Au Lait variations
    {
        "name": "Mocha Au Lait (12 Oz)",
        "description": "Coffee with chocolate and steamed milk",
        "price": Decimal("3.75"),
        "category": "House Coffee",
        "temperature": "hot",
        "size": "small",
        "contains_caffeine": True,
        "preparation_time": 4
    },
    {
        "name": "Mocha Au Lait (16 Oz)",
        "description": "Coffee with chocolate and steamed milk",
        "price": Decimal("4.00"),
        "category": "House Coffee",
        "temperature": "hot",
        "size": "medium",
        "contains_caffeine": True,
        "preparation_time": 4
    },
    {
        "name": "Mocha Au Lait (20 Oz)",
        "description": "Coffee with chocolate and steamed milk",
        "price": Decimal("4.25"),
        "category": "House Coffee",
        "temperature": "hot",
        "size": "large",
        "contains_caffeine": True,
        "preparation_time": 4
    },
    
    # Espresso Drinks
    {
        "name": "Mocha (12 Oz)",
        "description": "Rich chocolate espresso drink",
        "price": Decimal("5.00"),
        "category": "Espresso Drinks",
        "featured": True,
        "temperature": "hot",
        "size": "small",
        "contains_caffeine": True,
        "preparation_time": 4
    },
    {
        "name": "Mocha (16 Oz)",
        "description": "Rich chocolate espresso drink",
        "price": Decimal("5.50"),
        "category": "Espresso Drinks",
        "temperature": "hot",
        "size": "medium",
        "contains_caffeine": True,
        "preparation_time": 4
    },
    {
        "name": "Mocha (20 Oz)",
        "description": "Rich chocolate espresso drink",
        "price": Decimal("6.00"),
        "category": "Espresso Drinks",
        "temperature": "hot",
        "size": "large",
        "contains_caffeine": True,
        "preparation_time": 4
    },
    {
        "name": "Cappuccino",
        "description": "Traditional espresso with steamed milk foam",
        "price": Decimal("4.00"),
        "category": "Espresso Drinks",
        "featured": True,
        "temperature": "hot",
        "size": "medium",
        "contains_caffeine": True,
        "preparation_time": 4
    },
    
    # Specialty Coffee
    {
        "name": "Jumpstart (12 Oz)",
        "description": "House with a shot",
        "price": Decimal("3.75"),
        "category": "Specialty Coffee",
        "temperature": "hot",
        "size": "small",
        "contains_caffeine": True,
        "preparation_time": 2
    },
    {
        "name": "Jumpstart (16 Oz)",
        "description": "House with a shot",
        "price": Decimal("4.25"),
        "category": "Specialty Coffee",
        "temperature": "hot",
        "size": "medium",
        "contains_caffeine": True,
        "preparation_time": 2
    },
    {
        "name": "Jumpstart (20 Oz)",
        "description": "House with a shot",
        "price": Decimal("4.75"),
        "category": "Specialty Coffee",
        "temperature": "hot",
        "size": "large",
        "contains_caffeine": True,
        "preparation_time": 2
    },
    {
        "name": "Cold Brew (Toddy) (12 Oz)",
        "description": "Smooth cold-brewed coffee",
        "price": Decimal("4.00"),
        "category": "Specialty Coffee",
        "featured": True,
        "temperature": "cold",
        "size": "small",
        "contains_caffeine": True,
        "preparation_time": 2
    },
    {
        "name": "Cold Brew (Toddy) (16 Oz)",
        "description": "Smooth cold-brewed coffee",
        "price": Decimal("4.50"),
        "category": "Specialty Coffee",
        "temperature": "cold",
        "size": "medium",
        "contains_caffeine": True,
        "preparation_time": 2
    },
    {
        "name": "Cold Brew (Toddy) (20 Oz)",
        "description": "Smooth cold-brewed coffee",
        "price": Decimal("5.00"),
        "category": "Specialty Coffee",
        "temperature": "cold",
        "size": "large",
        "contains_caffeine": True,
        "preparation_time": 2
    },
    {
        "name": "The Scotsman (12 Oz)",
        "description": "Specialty Scottish-inspired coffee blend",
        "price": Decimal("4.75"),
        "category": "Specialty Coffee",
        "temperature": "hot",
        "size": "small",
        "contains_caffeine": True,
        "preparation_time": 3
    },
    {
        "name": "The Scotsman (16 Oz)",
        "description": "Specialty Scottish-inspired coffee blend",
        "price": Decimal("5.25"),
        "category": "Specialty Coffee",
        "temperature": "hot",
        "size": "medium",
        "contains_caffeine": True,
        "preparation_time": 3
    },
    {
        "name": "The Scotsman (20 Oz)",
        "description": "Specialty Scottish-inspired coffee blend",
        "price": Decimal("5.75"),
        "category": "Specialty Coffee",
        "temperature": "hot",
        "size": "large",
        "contains_caffeine": True,
        "preparation_time": 3
    }
]

print("\nCreating White Raven menu items...")
items_created = 0
items_existing = 0

for item_data in menu_items_data:
    category_name = item_data.pop("category")
    category = categories[category_name]
    
    menu_item, created = MenuItem.objects.get_or_create(
        name=item_data["name"],
        category=category,
        defaults=item_data
    )
    
    if created:
        print(f"+ Created menu item: {menu_item.name} (${menu_item.price}) in {category_name}")
        items_created += 1
    else:
        print(f"- Menu item already exists: {menu_item.name}")
        items_existing += 1

print(f"\n=== White Raven Menu Data Creation Complete ===")
print(f"Categories: {len(categories_data)} total")
print(f"Menu Items: {items_created} created, {items_existing} already existed")
print(f"Featured Items: {MenuItem.objects.filter(featured=True).count()}")
print(f"Available Items: {MenuItem.objects.filter(available=True).count()}")

# Display category summary
print(f"\n=== White Raven Category Summary ===")
for category in Category.objects.all().order_by('order'):
    item_count = category.menuitem_set.filter(available=True).count()
    print(f"{category.name}: {item_count} active items")

print(f"\n=== Price Range ===")
min_price = MenuItem.objects.filter(available=True).order_by('price').first()
max_price = MenuItem.objects.filter(available=True).order_by('-price').first()
if min_price and max_price:
    print(f"Price range: ${min_price.price} - ${max_price.price}")

print(f"\nReal White Raven menu data loaded successfully!")