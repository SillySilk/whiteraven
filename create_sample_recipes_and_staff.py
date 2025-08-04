#!/usr/bin/env python
import os
import django
from decimal import Decimal
from datetime import date, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from menu.models import MenuItem, Recipe
from staff.models import Employee
from django.contrib.auth.models import User

# Create sample recipes for the menu items
print("Creating sample recipes for menu items...")

recipes_data = [
    {
        "menu_item": "House (20 Oz)",
        "ingredients": "20 oz White Raven signature blend coffee\nHot water (200°F)\nOptional: cream, sugar",
        "instructions": "1. Grind coffee beans to medium-coarse\n2. Measure 2.5 tbsp ground coffee\n3. Brew using drip method with 200°F water\n4. Serve hot in 20 oz cup\n5. Offer cream and sugar on the side",
        "prep_time": 3,
        "difficulty": "easy",
        "equipment_needed": "Coffee grinder, drip coffee maker, 20 oz cup",
        "yield_quantity": "1 serving (20 oz)",
        "notes": "Our signature house blend. Maintain consistent water temperature for best extraction."
    },
    {
        "menu_item": "Cappuccino",
        "ingredients": "2 shots espresso\n6 oz whole milk\nCinnamon for dusting",
        "instructions": "1. Pull 2 shots of espresso into cappuccino cup\n2. Steam milk to 150°F with microfoam\n3. Pour steamed milk into espresso, maintaining foam layer\n4. Dust lightly with cinnamon\n5. Serve immediately",
        "prep_time": 4,
        "difficulty": "medium",
        "equipment_needed": "Espresso machine, milk steamer, cappuccino cup",
        "yield_quantity": "1 serving (8 oz)",
        "notes": "Traditional 1:1:1 ratio of espresso, steamed milk, and foam. Milk should be creamy and sweet."
    },
    {
        "menu_item": "Cold Brew (Toddy) (16 Oz)",
        "ingredients": "16 oz cold brew concentrate\nCold filtered water\nIce\nOptional: cream, simple syrup",
        "instructions": "1. Fill 16 oz cup with ice\n2. Add cold brew concentrate (dilute 1:1 with water if needed)\n3. Top with cold filtered water\n4. Stir gently\n5. Serve with cream and syrup on the side",
        "prep_time": 2,
        "difficulty": "easy",
        "equipment_needed": "16 oz cup, bar spoon",
        "yield_quantity": "1 serving (16 oz)",
        "notes": "Cold brew should be smooth and naturally sweet. Adjust concentration based on customer preference."
    },
    {
        "menu_item": "Mocha (16 Oz)",
        "ingredients": "2 shots espresso\n12 oz steamed milk\n2 tbsp chocolate syrup\nWhipped cream\nChocolate shavings",
        "instructions": "1. Pull 2 shots espresso into 16 oz cup\n2. Add chocolate syrup and stir\n3. Steam milk to 150°F\n4. Pour steamed milk, leaving room for whipped cream\n5. Top with whipped cream and chocolate shavings",
        "prep_time": 5,
        "difficulty": "medium",
        "equipment_needed": "Espresso machine, milk steamer, 16 oz cup, whisk",
        "yield_quantity": "1 serving (16 oz)",
        "notes": "Balance coffee and chocolate flavors. Use high-quality chocolate syrup for best taste."
    },
    {
        "menu_item": "The Scotsman (16 Oz)",
        "ingredients": "16 oz Scottish blend coffee\nHot water (200°F)\n1 tsp brown sugar\nSplash of cream",
        "instructions": "1. Grind Scottish blend coffee to medium\n2. Brew strong using French press method\n3. Add brown sugar while hot and stir\n4. Add splash of cream\n5. Serve in 16 oz mug",
        "prep_time": 6,
        "difficulty": "medium",
        "equipment_needed": "French press, coffee grinder, 16 oz mug",
        "yield_quantity": "1 serving (16 oz)",
        "notes": "Traditional Scottish coffee preparation. Let steep for 4 minutes for full flavor extraction."
    }
]

recipes_created = 0
recipes_existing = 0

for recipe_data in recipes_data:
    menu_item_name = recipe_data.pop("menu_item")
    try:
        menu_item = MenuItem.objects.filter(name=menu_item_name).first()
        if not menu_item:
            print(f"! Menu item not found: {menu_item_name}")
            continue
        
        recipe, created = Recipe.objects.get_or_create(
            menu_item=menu_item,
            defaults=recipe_data
        )
        if created:
            print(f"+ Created recipe for: {menu_item.name}")
            recipes_created += 1
        else:
            print(f"- Recipe already exists for: {menu_item.name}")
            recipes_existing += 1
    except MenuItem.DoesNotExist:
        print(f"! Menu item not found: {menu_item_name}")

print(f"\n=== Sample Staff Creation ===")

# Create sample staff members
staff_data = [
    {
        "username": "sarah_manager",
        "email": "sarah@whiteravenpourhouse.com",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "phone": "8315551234",
        "emergency_contact_name": "Mike Johnson",
        "emergency_contact_phone": "8315555678",
        "role": "manager",
        "hire_date": date.today() - timedelta(days=365),
        "hourly_wage": Decimal("18.50"),
        "can_open": True,
        "can_close": True,
        "can_handle_cash": True
    },
    {
        "username": "alex_barista",
        "email": "alex@whiteravenpourhouse.com",
        "first_name": "Alex",
        "last_name": "Chen",
        "phone": "8315551357",
        "emergency_contact_name": "Lisa Chen",
        "emergency_contact_phone": "8315552468",
        "role": "barista",
        "hire_date": date.today() - timedelta(days=180),
        "hourly_wage": Decimal("16.00"),
        "can_open": True,
        "can_close": False,
        "can_handle_cash": True
    },
    {
        "username": "jamie_parttime",
        "email": "jamie@whiteravenpourhouse.com",
        "first_name": "Jamie",
        "last_name": "Rodriguez",
        "phone": "8315559876",
        "emergency_contact_name": "Maria Rodriguez",
        "emergency_contact_phone": "8315551357",
        "role": "part_time",
        "hire_date": date.today() - timedelta(days=60),
        "hourly_wage": Decimal("15.50"),
        "can_open": False,
        "can_close": False,
        "can_handle_cash": True
    }
]

staff_created = 0
staff_existing = 0

for staff_info in staff_data:
    username = staff_info.pop("username")
    email = staff_info.pop("email")
    first_name = staff_info.pop("first_name")
    last_name = staff_info.pop("last_name")
    
    # Create or get Django user
    user, user_created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "is_active": True
        }
    )
    
    if user_created:
        user.set_password("temp123!")  # Temporary password
        user.save()
    
    # Create or get Employee
    employee, emp_created = Employee.objects.get_or_create(
        user=user,
        defaults=staff_info
    )
    
    if emp_created:
        print(f"+ Created employee: {user.get_full_name()} ({employee.get_role_display()})")
        staff_created += 1
    else:
        print(f"- Employee already exists: {user.get_full_name()}")
        staff_existing += 1

print(f"\n=== Task 21 Completion Summary ===")
print(f"Recipes: {recipes_created} created, {recipes_existing} already existed")
print(f"Staff: {staff_created} created, {staff_existing} already existed")
print(f"Total Recipes in system: {Recipe.objects.count()}")
print(f"Total Staff in system: {Employee.objects.count()}")
print(f"Total Active Staff: {Employee.objects.filter(employment_status='active').count()}")

print(f"\n=== Staff Summary ===")
for employee in Employee.objects.all():
    print(f"{employee.user.get_full_name()} - {employee.get_role_display()} (${employee.hourly_wage}/hr)")
    permissions = []
    if employee.can_open: permissions.append("Open")
    if employee.can_close: permissions.append("Close") 
    if employee.can_handle_cash: permissions.append("Cash")
    print(f"  Permissions: {', '.join(permissions) if permissions else 'None'}")

print(f"\nTask 21 - Create Initial Content and Data: COMPLETE!")