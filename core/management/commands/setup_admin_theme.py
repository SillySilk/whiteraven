from django.core.management.base import BaseCommand
from admin_interface.models import Theme


class Command(BaseCommand):
    help = 'Set up admin interface theme with better readability colors'

    def handle(self, *args, **options):
        # Delete existing themes first
        Theme.objects.all().delete()
        
        # Create new theme with improved readability
        theme, created = Theme.objects.get_or_create(
            name='White Raven Professional',
            defaults={
                'active': True,
                'title': 'White Raven Pourhouse Admin',
                'title_color': '#FFFFFF',
                'title_visible': True,
                'logo_visible': True,
                
                # Header colors - professional green theme
                'css_header_background_color': '#2E5A3B',  # Dark forest green
                'css_header_text_color': '#FFFFFF',        # White text
                'css_header_link_color': '#E8F5E8',        # Light green
                'css_header_link_hover_color': '#FFFFFF',  # White on hover
                
                # Module colors - clean and readable
                'css_module_background_color': '#FFFFFF',          # White background
                'css_module_background_selected_color': '#E8F5E8', # Light green selected
                'css_module_text_color': '#2C2C2C',               # Dark gray text (high contrast)
                'css_module_link_color': '#2E5A3B',               # Green links
                'css_module_link_selected_color': '#1A3B24',      # Dark green selected
                'css_module_link_hover_color': '#1A3B24',         # Darker green on hover
                'css_module_rounded_corners': True,
                
                # Generic colors - improved contrast
                'css_generic_link_color': '#2E5A3B',       # Green links
                'css_generic_link_hover_color': '#1A3B24', # Darker green on hover
                'css_generic_link_active_color': '#0F2117', # Very dark green active
                
                # Save button - consistent with theme
                'css_save_button_background_color': '#2E5A3B',     # Green
                'css_save_button_background_hover_color': '#1A3B24', # Darker green
                'css_save_button_text_color': '#FFFFFF',           # White text
                
                # Delete button - appropriate warning color
                'css_delete_button_background_color': '#8B0000',     # Dark red
                'css_delete_button_background_hover_color': '#A52A2A', # Red
                'css_delete_button_text_color': '#FFFFFF',           # White text
                
                # Environment and other settings
                'env_name': 'White Raven',
                'env_visible_in_header': True,
                'env_color': '#2E5A3B',
                'env_visible_in_favicon': False,
                
                # Logo settings
                'logo_color': '#FFFFFF',
                'logo_max_width': 400,
                'logo_max_height': 100,
                
                # UI improvements
                'related_modal_active': True,
                'related_modal_background_color': '#000000',
                'related_modal_background_opacity': '0.3',
                'related_modal_rounded_corners': True,
                'related_modal_close_button_visible': True,
                'recent_actions_visible': True,
                'language_chooser_active': False,
                'language_chooser_control': 'default-select',
                'language_chooser_display': 'code',
                'list_filter_dropdown': False,
                'list_filter_sticky': True,
                'list_filter_highlight': True,
                'list_filter_removal_links': False,
                'form_submit_sticky': False,
                'form_pagination_sticky': True,
                'foldable_apps': True,
                'show_fieldsets_as_tabs': False,
                'show_inlines_as_tabs': False,
                'collapsible_stacked_inlines': True,
                'collapsible_stacked_inlines_collapsed': False,
                'collapsible_tabular_inlines': True,
                'collapsible_tabular_inlines_collapsed': False,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin theme: {theme.name}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Updated existing admin theme: {theme.name}')
            )
            
        self.stdout.write(
            self.style.SUCCESS(
                '\nTheme configured with improved readability:\n'
                '  • Dark text (#2C2C2C) on white backgrounds for maximum contrast\n'
                '  • Professional green color scheme matching coffee shop branding\n'
                '  • High contrast ratios meeting WCAG accessibility guidelines\n'
                '  • Consistent styling across all admin interface elements\n'
                '\nTo customize further, go to Django Admin > Admin Interface > Themes'
            )
        )