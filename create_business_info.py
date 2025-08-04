#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from core.models import BusinessInfo

# Create business information if it doesn't exist
if not BusinessInfo.objects.exists():
    business_info = BusinessInfo.objects.create(
        name="White Raven Pourhouse",
        tagline="The Best Little Pour House in Felton",
        address="6017 Highway 9, Felton, CA 95018",
        phone="8314359999",
        email="info@whiteravenpourhouse.com",
        instagram_handle="whiteravenpourhouse",
        description="Welcome to White Raven Pourhouse, where exceptional coffee meets warm hospitality in the heart of Felton. We're passionate about serving the finest locally roasted coffee, artisanal beverages, and creating a cozy atmosphere where community gathers.",
        hours={
            "monday": {"open": "07:00", "close": "19:00", "closed": False},
            "tuesday": {"open": "07:00", "close": "19:00", "closed": False},
            "wednesday": {"open": "07:00", "close": "19:00", "closed": False},
            "thursday": {"open": "07:00", "close": "19:00", "closed": False},
            "friday": {"open": "07:00", "close": "20:00", "closed": False},
            "saturday": {"open": "08:00", "close": "20:00", "closed": False},
            "sunday": {"open": "08:00", "close": "18:00", "closed": False}
        },
        special_hours={
            "2024-12-25": {"closed": True, "note": "Christmas Day - Closed"},
            "2024-12-31": {"open": "08:00", "close": "16:00", "note": "New Year's Eve - Limited Hours"},
            "2024-01-01": {"closed": True, "note": "New Year's Day - Closed"},
            "2024-07-04": {"open": "08:00", "close": "16:00", "note": "Independence Day - Limited Hours"},
            "2024-11-28": {"closed": True, "note": "Thanksgiving - Closed"}
        }
    )
    print("Business information created successfully!")
    print(f"Name: {business_info.name}")
    print(f"Tagline: {business_info.tagline}")
    print(f"Address: {business_info.address}")
    print(f"Phone: {business_info.phone}")
    print(f"Email: {business_info.email}")
    print(f"Instagram: @{business_info.instagram_handle}")
else:
    print("Business information already exists!")
    business_info = BusinessInfo.objects.first()
    print(f"Current business: {business_info.name}")