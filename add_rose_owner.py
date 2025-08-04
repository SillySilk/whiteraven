#!/usr/bin/env python
import os
import django
from decimal import Decimal
from datetime import date, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from staff.models import Employee
from django.contrib.auth.models import User

print("Adding Rose Woolf as Owner...")

# Create Rose Woolf as owner
owner_data = {
    "username": "rose_owner",
    "email": "rose@whiteravenpourhouse.com",
    "first_name": "Rose",
    "last_name": "Woolf",
    "phone": "8315550001",
    "emergency_contact_name": "Emergency Contact",
    "emergency_contact_phone": "8315550002",
    "role": "owner",
    "hire_date": date.today() - timedelta(days=1095),  # 3 years ago
    "hourly_wage": Decimal("25.00"),
    "can_open": True,
    "can_close": True,
    "can_handle_cash": True,
    "notes": "Business owner and founder of White Raven Pourhouse"
}

username = owner_data.pop("username")
email = owner_data.pop("email")
first_name = owner_data.pop("first_name")
last_name = owner_data.pop("last_name")

# Create or get Django user
user, user_created = User.objects.get_or_create(
    username=username,
    defaults={
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "is_active": True,
        "is_staff": True,  # Give admin access
        "is_superuser": True  # Full admin privileges
    }
)

if user_created:
    user.set_password("rose123!")  # Owner password
    user.save()
    print(f"+ Created Django user: {user.get_full_name()}")
else:
    print(f"- Django user already exists: {user.get_full_name()}")

# Create or get Employee
employee, emp_created = Employee.objects.get_or_create(
    user=user,
    defaults=owner_data
)

if emp_created:
    print(f"+ Created employee: {user.get_full_name()} ({employee.get_role_display()})")
else:
    print(f"- Employee already exists: {user.get_full_name()}")

print(f"\n=== Updated Staff Summary ===")
for employee in Employee.objects.all().order_by('role'):
    print(f"{employee.user.get_full_name()} - {employee.get_role_display()} (${employee.hourly_wage}/hr)")
    permissions = []
    if employee.can_open: permissions.append("Open")
    if employee.can_close: permissions.append("Close") 
    if employee.can_handle_cash: permissions.append("Cash")
    print(f"  Permissions: {', '.join(permissions) if permissions else 'None'}")
    if employee.user.is_superuser:
        print(f"  Admin Access: Yes")

print(f"\nRose Woolf added as Owner successfully!")
print(f"Login: rose_owner / rose123!")