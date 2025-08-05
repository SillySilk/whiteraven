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
from admin_interface.models import Theme
from core.theme_context import site_theme, admin_theme_colors

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
    
    # Check Admin Theme
    print("2. Admin Theme Status:")
    admin_themes = Theme.objects.all()
    active_admin_theme = Theme.objects.filter(active=True).first()
    
    print(f"   Total Admin Theme objects: {admin_themes.count()}")
    if active_admin_theme:
        print(f"   ✅ Active admin theme: {active_admin_theme.name}")
        print(f"   Header colors:")
        print(f"     Background: {active_admin_theme.css_header_background_color}")
        print(f"     Text: {active_admin_theme.css_header_text_color}")
        print(f"     Links: {active_admin_theme.css_header_link_color}")
    else:
        print("   ❌ No active Admin Theme found")
    
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
    
    # Test admin theme context
    try:
        admin_context = admin_theme_colors(request)
        theme_colors = admin_context.get('theme_colors', {})
        
        if theme_colors:
            print(f"   ✅ Admin theme context working")
            print(f"   Theme colors: {len(theme_colors)} colors")
            print(f"     Primary: {theme_colors.get('primary', 'N/A')}")
            print(f"     Button: {theme_colors.get('button_bg', 'N/A')}")
        else:
            print("   ❌ Admin theme context returning empty")
    except Exception as e:
        print(f"   ❌ Admin theme context error: {e}")
    
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
    print("If no active Admin Theme:")
    print("   python manage.py shell -c \"from admin_interface.models import Theme; Theme.objects.update(active=False); Theme.objects.first().update(active=True) if Theme.objects.exists() else None\"")
    print()
    print("To force regenerate CSS:")
    print("   python manage.py collectstatic --clear --noinput")

if __name__ == '__main__':
    debug_production_theme()