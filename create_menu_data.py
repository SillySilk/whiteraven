#!/usr/bin/env python
import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from menu.models import Category, MenuItem

# Create menu categories
categories_data = [
    {
        "name": "Coffee",
        "description": "Freshly roasted coffee drinks made with locally sourced beans",
        "order": 1
    },
    {
        "name": "Tea & Specialty Drinks", 
        "description": "Premium teas and unique specialty beverages",
        "order": 2
    },
    {
        "name": "Food",
        "description": "Fresh pastries, sandwiches, and light meals", 
        "order": 3
    },
    {
        "name": "Desserts",
        "description": "Sweet treats and decadent desserts",
        "order": 4
    }
]

print("Creating menu categories...")
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
        print(f"✓ Created category: {category.name}")
    else:
        print(f"• Category already exists: {category.name}")

# Create sample menu items
menu_items_data = [
    # Coffee
    {
        "name": "White Raven Blend",
        "description": "Our signature house blend featuring dark roasted beans with notes of chocolate and caramel. Rich, full-bodied, and perfectly balanced.",
        "price": Decimal("4.95"),
        "category": "Coffee",
        "featured": True,
        "temperature": "both",
        "size": "medium",
        "contains_caffeine": True,
        "dietary_notes": "Vegan friendly with plant milk options",
        "preparation_time": 3
    },
    {
        "name": "Espresso",
        "description": "Classic Italian espresso shot. Bold, concentrated coffee with a rich crema. Perfect on its own or as the base for other drinks.",
        "price": Decimal("3.25"),
        "category": "Coffee",
        "temperature": "hot",
        "size": "small",
        "contains_caffeine": True,
        "preparation_time": 2
    },
    {
        "name": "Cappuccino",
        "description": "Traditional Italian cappuccino with equal parts espresso, steamed milk, and milk foam. Dusted with cinnamon.",
        "price": Decimal("5.25"),
        "category": "Coffee",
        "temperature": "hot",
        "size": "medium",
        "contains_caffeine": True,
        "dietary_notes": "Available with oat, almond, or soy milk",
        "preparation_time": 4
    },
    {
        "name": "Cold Brew",
        "description": "Smooth, naturally sweet cold brew coffee steeped for 18 hours. Served over ice with optional cream.",
        "price": Decimal("4.75"),
        "category": "Coffee",
        "temperature": "cold",
        "size": "large",
        "contains_caffeine": True,
        "preparation_time": 2
    },
    
    # Tea & Specialty Drinks
    {
        "name": "Chai Latte",
        "description": "Aromatic blend of black tea, cinnamon, cardamom, cloves, and ginger with steamed milk. Warming and comforting.",
        "price": Decimal("5.50"),
        "category": "Tea & Specialty Drinks",
        "temperature": "both",
        "size": "medium",
        "contains_caffeine": True,
        "dietary_notes": "Available with plant milk",
        "preparation_time": 5
    },
    {
        "name": "Matcha Latte",
        "description": "Premium ceremonial grade matcha whisked with steamed milk. Earthy, smooth, and naturally energizing.",
        "price": Decimal("6.25"),
        "category": "Tea & Specialty Drinks",
        "featured": True,
        "temperature": "both",
        "size": "medium",
        "contains_caffeine": True,
        "dietary_notes": "Naturally sweet, vegan options available",
        "preparation_time": 6
    },
    {
        "name": "Herbal Tea Selection",
        "description": "Choice of chamomile, peppermint, lemon ginger, or hibiscus. Caffeine-free and soothing.",
        "price": Decimal("3.95"),
        "category": "Tea & Specialty Drinks",
        "temperature": "hot",
        "size": "medium",
        "contains_caffeine": False,
        "dietary_notes": "Naturally caffeine-free, vegan",
        "preparation_time": 4
    },
    
    # Food
    {
        "name": "Avocado Toast",
        "description": "Fresh avocado mashed with lime, sea salt, and red pepper flakes on artisan sourdough. Topped with everything bagel seasoning.",
        "price": Decimal("8.95"),
        "category": "Food",
        "temperature": "room",
        "size": "one_size",
        "featured": True,
        "dietary_notes": "Vegan, contains gluten",
        "calories": 320,
        "preparation_time": 5
    },
    {
        "name": "Turkey & Swiss Croissant",
        "description": "Buttery croissant filled with roasted turkey, Swiss cheese, mixed greens, and Dijon mustard.",
        "price": Decimal("9.75"),
        "category": "Food",
        "temperature": "room",
        "size": "one_size",
        "dietary_notes": "Contains gluten, dairy",
        "calories": 485,
        "preparation_time": 3
    },
    {
        "name": "Fresh Fruit Bowl",
        "description": "Seasonal fresh fruit medley with berries, grapes, and melon. Served with honey yogurt dip.",
        "price": Decimal("7.25"),
        "category": "Food",
        "temperature": "cold",
        "size": "one_size",
        "dietary_notes": "Vegetarian, gluten-free",
        "calories": 185,
        "preparation_time": 2
    },
    
    # Desserts
    {
        "name": "Chocolate Chip Cookie",
        "description": "Warm, freshly baked chocolate chip cookie made with premium butter and dark chocolate chips.",
        "price": Decimal("3.50"),
        "category": "Desserts",
        "temperature": "room",
        "size": "one_size",
        "dietary_notes": "Contains gluten, dairy, eggs",
        "calories": 285,
        "preparation_time": 1
    },
    {
        "name": "Lemon Blueberry Scone",
        "description": "Buttery scone studded with fresh blueberries and bright lemon zest. Served with clotted cream.",
        "price": Decimal("4.25"),
        "category": "Desserts",
        "temperature": "room",
        "size": "one_size",
        "dietary_notes": "Contains gluten, dairy, eggs",
        "calories": 340,
        "preparation_time": 2
    },
    {
        "name": "Vegan Chocolate Brownie",
        "description": "Rich, fudgy brownie made without dairy or eggs. Topped with a dusting of powdered sugar.",
        "price": Decimal("4.95"),
        "category": "Desserts",
        "temperature": "room",
        "size": "one_size",
        "featured": True,
        "dietary_notes": "Vegan, contains gluten",
        "calories": 295,
        "preparation_time": 1
    }
]

print("\nCreating menu items...")
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
        print(f"✓ Created menu item: {menu_item.name} (${menu_item.price}) in {category_name}")
        items_created += 1
    else:
        print(f"• Menu item already exists: {menu_item.name}")
        items_existing += 1

print(f"\n=== Menu Data Creation Complete ===")
print(f"Categories: {len(categories_data)} total")
print(f"Menu Items: {items_created} created, {items_existing} already existed")
print(f"Featured Items: {MenuItem.objects.filter(featured=True).count()}")
print(f"Available Items: {MenuItem.objects.filter(available=True).count()}")

# Display category summary
print(f"\n=== Category Summary ===")
for category in Category.objects.all().order_by('order'):
    item_count = category.menuitem_set.filter(available=True).count()
    print(f"{category.name}: {item_count} active items")