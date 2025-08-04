#!/usr/bin/env python
"""
Update the existing BusinessInfo record with default values for new fields
so Rose can see and edit them in the admin interface.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from core.models import BusinessInfo

def update_business_info():
    """Update the existing BusinessInfo with default values for new fields"""
    
    print("UPDATING BUSINESS INFO WITH NEW EDITABLE FIELDS")
    print("=" * 50)
    
    try:
        business_info = BusinessInfo.objects.first()
        if not business_info:
            print("No existing BusinessInfo found. Creating one...")
            business_info = BusinessInfo.objects.create(
                name="White Raven Pourhouse",
                tagline="The Best Little Pour House in Felton",
                address="123 Main St\nFelton, CA 95018",
                phone="8315551234",
                email="info@whiteravenpourhouse.com"
            )
        
        # Update with new field defaults if they're empty
        updated_fields = []
        
        if not business_info.meta_description or business_info.meta_description == "White Raven Pourhouse - The Best Little Pour House in Felton. Serving exceptional coffee and creating memorable experiences in Felton, CA.":
            # Keep the current default, it's good
            pass
        
        if not business_info.facebook_url:
            business_info.facebook_url = "https://facebook.com/whiteravenpourhouse"
            updated_fields.append("facebook_url")
        
        if not business_info.instagram_url:
            business_info.instagram_url = "https://instagram.com/white_raven_pour_house"
            updated_fields.append("instagram_url")
        
        if not business_info.welcome_message:
            business_info.welcome_message = "Welcome to White Raven Pourhouse, where every cup tells a story and every visit creates memories. We're passionate about serving exceptional coffee and fostering community connections in the heart of Felton."
            updated_fields.append("welcome_message")
        
        if not business_info.footer_tagline or business_info.footer_tagline == "Made with ❤ in Felton, CA":
            # Keep default
            pass
        
        if not business_info.copyright_text or business_info.copyright_text == "White Raven Pourhouse":
            # Keep default
            pass
        
        business_info.save()
        
        print(f"+ Updated BusinessInfo record (ID: {business_info.id})")
        if updated_fields:
            print(f"+ Updated fields: {', '.join(updated_fields)}")
        else:
            print("+ All fields already have values")
        
        print(f"\nCurrent BusinessInfo:")
        print(f"- Name: {business_info.name}")
        print(f"- Tagline: {business_info.tagline}")
        print(f"- Email: {business_info.email}")
        print(f"- Phone: {business_info.phone}")
        print(f"- Facebook: {business_info.facebook_url}")
        print(f"- Instagram: {business_info.instagram_url}")
        print(f"- Hero Image: {'Yes' if business_info.hero_image else 'Not uploaded'}")
        print(f"- Welcome Message: {'Yes' if business_info.welcome_message else 'Not set'}")
        print(f"- Footer Tagline: {business_info.footer_tagline}")
        print(f"- Copyright: {business_info.copyright_text}")
        
        print("\n" + "=" * 50)
        print("SUCCESS! Rose can now edit these fields in the admin:")
        print("1. Hero Image - Upload a beautiful coffee shop photo")
        print("2. Social Media Links - Update Facebook and Instagram URLs")
        print("3. Welcome Message - Customize the homepage greeting")
        print("4. Footer Tagline - Change the footer message")
        print("5. Copyright Text - Update business name for copyright")
        print("6. Meta Description - SEO description for search engines")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error updating BusinessInfo: {e}")
        return False
    
    return True

if __name__ == "__main__":
    update_business_info()