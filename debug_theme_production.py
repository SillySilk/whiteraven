#!/usr/bin/env python
"""
Debug theme system in production to verify colors are being applied
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from core.models import SiteTheme
# Removed admin_interface dependency
from core.theme_context import site_theme

def debug_production_theme():
    print("🔧 White Raven Theme Debug - Production")
    print("=" * 60)
    
    # Check if SiteTheme exists and is active
    print("1. SiteTheme Status:")
    site_themes = SiteTheme.objects.all()
    active_site_theme = SiteTheme.objects.filter(is_active=True).first()
    
    print(f"   Total SiteTheme objects: {site_themes.count()}")
    if active_site_theme:
        print(f"   ✅ Active theme: {active_site_theme.name}")
        print(f"   Colors:")
        print(f"     Primary: {active_site_theme.primary_color}")
        print(f"     Secondary: {active_site_theme.secondary_color}")
        print(f"     Accent: {active_site_theme.accent_color}")
        print(f"     Navbar BG: {active_site_theme.navbar_bg}")
        print(f"     Button Primary: {active_site_theme.button_primary_bg}")
        
        # Test CSS variable generation
        css_vars = active_site_theme.get_css_variables()
        print(f"   CSS Variables generated: {len(css_vars)}")
        if css_vars:
            print("   Sample variables:")
            for var_name, var_value in list(css_vars.items())[:3]:
                print(f"     {var_name}: {var_value}")
    else:
        print("   ❌ No active SiteTheme found")
        print("   Available themes:")
        for theme in site_themes:
            print(f"     - {theme.name} (active: {theme.is_active})")
    
    print()
    
    # Admin Theme - now using standard Django admin with custom CSS
    print("2. Admin Theme Status:")
    print("   ✅ Using standard Django admin with custom CSS")
    print("   Custom CSS location: static/admin/css/custom_admin.css")
    print()
    
    # Test context processors
    print("3. Context Processor Test:")
    
    class MockRequest:
        pass
    
    request = MockRequest()
    
    # Test site theme context
    try:
        site_context = site_theme(request)
        site_theme_obj = site_context.get('site_theme')
        site_theme_vars = site_context.get('site_theme_vars', {})
        
        if site_theme_obj:
            print(f"   ✅ Site theme context: {site_theme_obj.name}")
            print(f"   CSS variables: {len(site_theme_vars)}")
            if site_theme_vars:
                print("   Sample CSS variables:")
                for var_name, var_value in list(site_theme_vars.items())[:3]:
                    print(f"     {var_name}: {var_value}")
        else:
            print("   ❌ Site theme context returning None")
            print(f"   Context keys: {list(site_context.keys())}")
    except Exception as e:
        print(f"   ❌ Site theme context error: {e}")
    
    # Admin theme now uses standard Django admin with custom CSS
    print("   ✅ Admin theme using standard Django admin CSS")
    
    print()
    
    # CSS Variables that should be available in templates
    print("4. Expected CSS Variables in Templates:")
    expected_vars = [
        '--theme-primary', '--theme-secondary', '--theme-accent',
        '--theme-navbar-bg', '--theme-navbar-text', '--theme-navbar-hover',
        '--theme-btn-primary-bg', '--theme-btn-primary-text',
        '--theme-footer-bg', '--theme-footer-text', '--theme-footer-link'
    ]
    
    if active_site_theme:
        actual_vars = active_site_theme.get_css_variables()
        print("   Variables that should be in HTML:")
        for var in expected_vars:
            value = actual_vars.get(var, 'MISSING')
            status = "✅" if value != 'MISSING' else "❌"
            print(f"   {status} {var}: {value}")
    else:
        print("   ❌ Cannot check - no active theme")
    
    print()
    print("=" * 60)
    print("🎯 Quick Fix Commands:")
    print()
    print("If no active SiteTheme:")
    print("   python manage.py shell -c \"from core.models import SiteTheme; SiteTheme.objects.update(is_active=False); SiteTheme.objects.first().update(is_active=True) if SiteTheme.objects.exists() else None\"")
    print()
    print("Admin theme now uses standard Django admin with custom CSS")
    print()
    print("To force regenerate CSS:")
    print("   python manage.py collectstatic --clear --noinput")

if __name__ == '__main__':
    debug_production_theme()