#!/usr/bin/env python
"""
White Raven Pourhouse - Add Comprehensive Menu Items
This script adds all the menu items with different sizes based on the provided menu data.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from menu.models import Category, MenuItem

def create_categories():
    """Create menu categories"""
    categories_data = [
        {"name": "House Coffee", "slug": "house-coffee", "description": "Our signature house blends"},
        {"name": "Espresso Drinks", "slug": "espresso-drinks", "description": "Classic espresso-based beverages"},
        {"name": "Tea Drinks", "slug": "tea-drinks", "description": "Premium teas and tea lattes"},
        {"name": "Larry's Famous Chai", "slug": "larrys-chai", "description": "Specialty chai creations"},
        {"name": "Shakes", "slug": "shakes", "description": "Delicious blended beverages"},
        {"name": "Add-Ons & Syrups", "slug": "add-ons", "description": "Customize your drink"},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data["slug"],
            defaults={
                "name": cat_data["name"],
                "description": cat_data["description"],
                "active": True,
                "order": len(categories_data)
            }
        )
        if created:
            print(f"+ Created category: {category.name}")
        else:
            print(f"- Category exists: {category.name}")

def add_menu_items():
    """Add all menu items with sizes and pricing"""
    
    # Get categories
    house_coffee = Category.objects.get(slug="house-coffee")
    espresso = Category.objects.get(slug="espresso-drinks")
    tea = Category.objects.get(slug="tea-drinks")
    chai = Category.objects.get(slug="larrys-chai")
    shakes = Category.objects.get(slug="shakes")
    
    # House Coffee Items
    house_items = [
        {"name": "House", "sizes": {"12oz": 3.00, "16oz": 3.50, "20oz": 4.00}},
        {"name": "Cafe Au Lait", "sizes": {"12oz": 4.25, "16oz": 4.75, "20oz": 5.25}},
        {"name": "Jump Start", "sizes": {"12oz": 4.25, "16oz": 4.75, "20oz": 5.25}},
        {"name": "Teddy Bear", "sizes": {"12oz": 4.50, "16oz": 5.00, "20oz": 5.50}},
        {"name": "The Scotsman", "sizes": {"12oz": 5.25, "16oz": 5.75, "20oz": 6.25}, "description": "Steam & honey, cinnamon stick"},
        {"name": "Add Chocolate", "sizes": {"any": 0.75}, "description": "Add chocolate to any drink"},
    ]
    
    # Espresso Drinks
    espresso_items = [
        {"name": "Latte", "sizes": {"12oz": 5.25, "16oz": 5.75, "20oz": 6.25}},
        {"name": "Mocha", "sizes": {"12oz": 5.75, "16oz": 6.25, "20oz": 6.75}},
        {"name": "White Mocha", "sizes": {"12oz": 5.75, "16oz": 6.25, "20oz": 6.75}},
        {"name": "Red Mocha", "sizes": {"12oz": 5.75, "16oz": 6.25, "20oz": 6.75}},
        {"name": "Espresso", "sizes": {"single": 3.00}, "description": "Single shot of espresso"},
        {"name": "Cappuccino", "sizes": {"12oz": 4.25}},
        {"name": "Macchiato", "sizes": {"12oz": 4.00}},
        {"name": "Cortado", "sizes": {"12oz": 5.75}},
        {"name": "Affogato", "sizes": {"single": 5.00}, "description": "Espresso over vanilla ice cream"},
    ]
    
    # Tea Drinks
    tea_items = [
        {"name": "Hot Tea", "sizes": {"12oz": 3.00, "16oz": 3.25, "20oz": 3.50}},
        {"name": "Iced Tea", "sizes": {"12oz": 3.25, "16oz": 3.75, "20oz": 4.25}},
        {"name": "Tea Latte", "sizes": {"12oz": 4.25, "16oz": 4.75, "20oz": 5.25}},
        {"name": "Matcha Latte", "sizes": {"12oz": 4.75, "16oz": 5.00, "20oz": 5.25}},
    ]
    
    # Larry's Famous Chai
    chai_items = [
        {"name": "House Chai", "sizes": {"16oz": 5.75}},
        {"name": "Soy Maple Chai", "sizes": {"16oz": 6.25}, "description": "House Chai + $0.50"},
        {"name": "Dirty Chai", "sizes": {"16oz": 4.75}, "description": "Chai with espresso shot"},
        {"name": "Iced Soy Chai", "sizes": {"16oz": 5.75}},
        {"name": "Couging", "sizes": {"16oz": 4.00}},
    ]
    
    # Shakes
    shake_items = [
        {"name": "Jammin' Brew", "sizes": {"16oz": 6.00, "20oz": 7.00}},
        {"name": "Chai Shake", "sizes": {"16oz": 6.00, "20oz": 7.00}},
        {"name": "Dream Shake", "sizes": {"16oz": 6.00, "20oz": 7.50}},
        {"name": "Peanut Butter Shake", "sizes": {"16oz": 5.50, "20oz": 6.50}},
    ]
    
    # Function to create menu items
    def create_items(items, category):
        for item_data in items:
            for size, price in item_data["sizes"].items():
                # Create name with size (unless it's a single item)
                if size in ["single", "any"]:
                    name = item_data["name"]
                else:
                    name = f"{item_data['name']} ({size})"
                
                # Create menu item
                menu_item, created = MenuItem.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults={
                        "description": item_data.get("description", f"{item_data['name']} - {size}"),
                        "price": Decimal(str(price)),
                        "available": True,
                        "contains_caffeine": category.slug in ["house-coffee", "espresso-drinks", "larrys-chai"],
                        "temperature": "hot" if category.slug != "shakes" else "cold",
                        "size": "large" if "20oz" in size else "medium" if "16oz" in size else "small",
                        "preparation_time": 3 if category.slug == "tea-drinks" else 5,
                    }
                )
                
                if created:
                    print(f"+ Added: {name} - ${price}")
                else:
                    print(f"- Exists: {name}")
    
    # Create all items
    print("\n=== ADDING HOUSE COFFEE ITEMS ===")
    create_items(house_items, house_coffee)
    
    print("\n=== ADDING ESPRESSO DRINKS ===")
    create_items(espresso_items, espresso)
    
    print("\n=== ADDING TEA DRINKS ===")
    create_items(tea_items, tea)
    
    print("\n=== ADDING LARRY'S FAMOUS CHAI ===")
    create_items(chai_items, chai)
    
    print("\n=== ADDING SHAKES ===")
    create_items(shake_items, shakes)

def add_syrups():
    """Add syrup options as menu items"""
    addons_category = Category.objects.get(slug="add-ons")
    
    syrups = [
        "Almond", "Caramel", "Cherry", "Cinnamon", "Coconut", "Hazelnut",
        "Lemon", "Lime", "Macadamia", "Marshmallow", "Orange", "Peppermint",
        "Raspberry", "Strawberry", "Vanilla"
    ]
    
    sugar_free = ["Caramel", "Hazelnut"]
    
    print("\n=== ADDING SYRUPS ===")
    for syrup in syrups:
        menu_item, created = MenuItem.objects.get_or_create(
            name=f"{syrup} Syrup",
            category=addons_category,
            defaults={
                "description": f"Add {syrup.lower()} flavor to any drink",
                "price": Decimal("0.75"),
                "available": True,
                "contains_caffeine": False,
                "temperature": "room",
                "size": "small",
                "preparation_time": 1,
            }
        )
        if created:
            print(f"+ Added: {syrup} Syrup - $0.75")
        else:
            print(f"- Exists: {syrup} Syrup")
    
    print("\n=== ADDING SUGAR-FREE SYRUPS ===")
    for syrup in sugar_free:
        menu_item, created = MenuItem.objects.get_or_create(
            name=f"{syrup} Syrup (Sugar-Free)",
            category=addons_category,
            defaults={
                "description": f"Sugar-free {syrup.lower()} flavor",
                "price": Decimal("0.75"),
                "available": True,
                "contains_caffeine": False,
                "temperature": "room",
                "size": "small",
                "preparation_time": 1,
                "dietary_notes": "Sugar-free",
            }
        )
        if created:
            print(f"+ Added: {syrup} Syrup (Sugar-Free) - $0.75")
        else:
            print(f"- Exists: {syrup} Syrup (Sugar-Free)")

def main():
    print("WHITE RAVEN POURHOUSE - COMPREHENSIVE MENU SETUP")
    print("=" * 60)
    
    print("\n1. Creating Categories...")
    create_categories()
    
    print("\n2. Adding Menu Items...")
    add_menu_items()
    
    print("\n3. Adding Syrups & Add-ons...")
    add_syrups()
    
    # Final count
    total_items = MenuItem.objects.count()
    total_categories = Category.objects.filter(active=True).count()
    
    print("\n" + "=" * 60)
    print("COMPREHENSIVE MENU SETUP COMPLETE!")
    print(f"Total Categories: {total_categories}")
    print(f"Total Menu Items: {total_items}")
    print("=" * 60)

if __name__ == "__main__":
    main()