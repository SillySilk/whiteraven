#!/usr/bin/env python
"""
Test the theme system to ensure colors are being applied correctly
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from core.models import SiteTheme, BusinessInfo
from admin_interface.models import Theme

def test_theme_system():
    print("🎨 Testing White Raven Theme System...")
    print("=" * 50)
    
    # Test SiteTheme
    print("1. Testing SiteTheme model:")
    site_theme = SiteTheme.get_active_theme()
    if site_theme:
        print(f"   ✓ Active site theme: {site_theme.name}")
        print(f"   ✓ Primary color: {site_theme.primary_color}")
        print(f"   ✓ Secondary color: {site_theme.secondary_color}")
        print(f"   ✓ Accent color: {site_theme.accent_color}")
        
        # Test CSS variables generation
        css_vars = site_theme.get_css_variables()
        print(f"   ✓ Generated {len(css_vars)} CSS variables:")
        for var_name, var_value in list(css_vars.items())[:5]:
            print(f"     {var_name}: {var_value}")
        if len(css_vars) > 5:
            print(f"     ... and {len(css_vars) - 5} more")
    else:
        print("   ❌ No active site theme found")
    
    print()
    
    # Test Admin Theme
    print("2. Testing Admin Theme:")
    admin_theme = Theme.objects.filter(active=True).first()
    if admin_theme:
        print(f"   ✓ Active admin theme: {admin_theme.name}")
        print(f"   ✓ Header background: {admin_theme.css_header_background_color}")
        print(f"   ✓ Header text: {admin_theme.css_header_text_color}")
        print(f"   ✓ Save button: {admin_theme.css_save_button_background_color}")
    else:
        print("   ❌ No active admin theme found")
    
    print()
    
    # Test BusinessInfo
    print("3. Testing BusinessInfo:")
    business_info = BusinessInfo.objects.first()
    if business_info:
        print(f"   ✓ Business name: {business_info.name}")
        print(f"   ✓ Tagline: {business_info.tagline}")
        print(f"   ✓ Phone: {business_info.phone}")
        print(f"   ✓ Email: {business_info.email}")
        
        # Test hours
        if business_info.hours:
            print(f"   ✓ Hours configured for {len(business_info.hours)} days")
            # Show Monday hours as example
            if 'monday' in business_info.hours:
                monday = business_info.hours['monday']
                if monday.get('closed', True):
                    print("     Monday: Closed")
                else:
                    print(f"     Monday: {monday.get('open', 'N/A')} - {monday.get('close', 'N/A')}")
        else:
            print("   ❌ No hours configured")
            
        # Test social media
        if business_info.instagram_url:
            print(f"   ✓ Instagram: {business_info.instagram_url}")
        if business_info.facebook_url:
            print(f"   ✓ Facebook: {business_info.facebook_url}")
            
    else:
        print("   ❌ No business info found")
    
    print()
    
    # Test context processors
    print("4. Testing Context Processors:")
    from core.theme_context import site_theme, admin_theme_colors, business_info as business_context
    
    # Mock request object
    class MockRequest:
        pass
    
    request = MockRequest()
    
    # Test site theme context
    site_context = site_theme(request)
    if site_context.get('site_theme_vars'):
        print(f"   ✓ Site theme context processor working ({len(site_context['site_theme_vars'])} variables)")
    else:
        print("   ❌ Site theme context processor not working")
    
    # Test admin theme context
    admin_context = admin_theme_colors(request)
    if admin_context.get('theme_colors'):
        print(f"   ✓ Admin theme context processor working")
        print(f"     Primary: {admin_context['theme_colors']['primary']}")
    else:
        print("   ❌ Admin theme context processor not working")
    
    # Test business context
    business_ctx = business_context(request)
    if business_ctx.get('business_info'):
        print(f"   ✓ Business info context processor working")
    else:
        print("   ❌ Business info context processor not working")
    
    print()
    print("=" * 50)
    print("✅ Theme system test completed!")
    print("\nTo apply theme on the website:")
    print("1. Ensure context processors are in TEMPLATES settings")
    print("2. Restart Django server to load new CSS")
    print("3. Visit the site to see theme colors applied")

if __name__ == '__main__':
    test_theme_system()