"""
Context processors for theme and business information.
"""

def admin_theme_colors(request):
    """
    Add admin interface theme colors to template context for public website.
    
    This context processor extracts colors from the active admin theme
    and makes them available to all templates, allowing the public website
    to maintain visual consistency with the admin interface.
    
    Returns:
        dict: Theme colors for use in templates
    """
    try:
        from admin_interface.models import Theme
        
        # Get the active admin theme
        active_theme = Theme.objects.filter(active=True).first()
        
        if active_theme:
            return {
                'theme_colors': {
                    # Primary branding colors
                    'primary': active_theme.css_header_background_color,
                    'primary_text': active_theme.css_header_text_color,
                    'primary_light': active_theme.css_header_link_color,
                    
                    # Content area colors  
                    'content_bg': active_theme.css_module_background_color,
                    'content_text': active_theme.css_module_text_color,
                    'content_selected': active_theme.css_module_background_selected_color,
                    
                    # Link colors
                    'link_color': active_theme.css_generic_link_color,
                    'link_hover': active_theme.css_generic_link_hover_color,
                    'link_active': active_theme.css_generic_link_active_color,
                    
                    # Button colors
                    'button_bg': active_theme.css_save_button_background_color,
                    'button_bg_hover': active_theme.css_save_button_background_hover_color,
                    'button_text': active_theme.css_save_button_text_color,
                    
                    # Environment colors
                    'env_color': active_theme.env_color,
                    'logo_color': active_theme.logo_color,
                    
                    # Theme name for reference
                    'theme_name': active_theme.name,
                }
            }
            
    except Exception as e:
        # Log the error but don't break the site
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not load admin theme colors: {e}")
    
    # Fallback colors matching White Raven Professional theme
    return {
        'theme_colors': {
            'primary': '#2E5A3B',        # Dark forest green
            'primary_text': '#FFFFFF',   # White text
            'primary_light': '#E8F5E8',  # Light green
            'content_bg': '#FFFFFF',     # White background
            'content_text': '#2C2C2C',   # Dark gray text (high contrast)
            'content_selected': '#E8F5E8', # Light green selected
            'link_color': '#2E5A3B',     # Green links
            'link_hover': '#1A3B24',     # Darker green on hover
            'link_active': '#0F2117',    # Very dark green active
            'button_bg': '#2E5A3B',      # Green buttons
            'button_bg_hover': '#1A3B24', # Darker green hover
            'button_text': '#FFFFFF',    # White button text
            'env_color': '#2E5A3B',      # Environment color
            'logo_color': '#FFFFFF',     # Logo color
            'theme_name': 'Default White Raven',
        }
    }


def site_theme(request):
    """
    Make site theme available to all templates.
    """
    try:
        from core.models import SiteTheme
        active_theme = SiteTheme.get_active_theme()
        return {
            'site_theme': active_theme,
            'site_theme_vars': active_theme.get_css_variables()
        }
    except Exception as e:
        # Log the error but don't break the site
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not load site theme: {e}")
        return {
            'site_theme': None,
            'site_theme_vars': {}
        }


def business_info(request):
    """
    Add business information to template context.
    This is separate from the theme context but useful for the website.
    """
    try:
        from core.models import BusinessInfo
        
        business = BusinessInfo.objects.first()
        if business:
            return {
                'business_info': business
            }
    except Exception:
        pass
    
    return {}