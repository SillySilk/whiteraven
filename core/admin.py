from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
from .models import BusinessInfo, ContactSubmission, SiteTheme
from .email_utils import EmailService

@admin.register(BusinessInfo)
class BusinessInfoAdmin(admin.ModelAdmin):
    """
    Admin interface for managing business information.
    Since this is a singleton model, customize the interface accordingly.
    """
    list_display = ('name', 'tagline', 'phone', 'email', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'tagline', 'description', 'hero_image', 'about_image', 'location_image')
        }),
        ('Contact Details', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Social Media Links', {
            'fields': ('facebook_url', 'instagram_url'),
            'description': 'Full URLs to your social media pages'
        }),
        ('Website Content', {
            'fields': ('welcome_message', 'meta_description'),
            'description': 'Customize homepage content and SEO description'
        }),
        ('Footer & Branding', {
            'fields': ('footer_tagline', 'copyright_text'),
            'description': 'Customize footer text and copyright information'
        }),
        ('Regular Operating Hours', {
            'fields': ('hours',),
            'description': 'Regular weekly hours in JSON format. Example: {"monday": {"open": "07:00", "close": "19:00", "closed": false}}'
        }),
        ('Special Hours & Holidays', {
            'fields': ('special_hours',),
            'description': 'Special hours for holidays or events. Example: {"2024-12-25": {"closed": true, "note": "Christmas Day"}}'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_urls(self):
        """Add custom URLs for email testing"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('test-email/', self.admin_site.admin_view(self.test_email_view), name='core_businessinfo_test_email'),
        ]
        return custom_urls + urls
    
    def test_email_view(self, request):
        """Custom admin view to test email configuration"""
        if request.method == 'POST':
            # Run email test
            result = EmailService.test_email_configuration()
            
            if result['success']:
                self.message_user(
                    request, 
                    f"Email test successful: {result['message']}", 
                    level=messages.SUCCESS
                )
            else:
                self.message_user(
                    request, 
                    f"Email test failed: {result['message']}", 
                    level=messages.ERROR
                )
        
        # Redirect back to business info change view
        try:
            business_info = BusinessInfo.objects.first()
            if business_info:
                from django.shortcuts import redirect
                return redirect('admin:core_businessinfo_change', business_info.pk)
        except BusinessInfo.DoesNotExist:
            pass
        
        from django.shortcuts import redirect
        return redirect('admin:core_businessinfo_changelist')
    
    def has_add_permission(self, request):
        """Only allow adding if no BusinessInfo exists"""
        if BusinessInfo.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of business info"""
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Redirect to edit view if BusinessInfo exists, otherwise show add view"""
        if BusinessInfo.objects.exists():
            business_info = BusinessInfo.objects.first()
            from django.shortcuts import redirect
            return redirect('admin:core_businessinfo_change', business_info.pk)
        return super().changelist_view(request, extra_context)


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing contact form submissions.
    """
    list_display = (
        'name', 
        'email', 
        'display_subject', 
        'created_at', 
        'responded_status',
        'view_message'
    )
    
    list_filter = (
        'subject', 
        'responded', 
        'created_at',
    )
    
    search_fields = ('name', 'email', 'message', 'custom_subject')
    
    readonly_fields = ('created_at', 'display_subject_readonly')
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email')
        }),
        ('Message Details', {
            'fields': ('subject', 'custom_subject', 'display_subject_readonly', 'message')
        }),
        ('Response Tracking', {
            'fields': ('responded', 'response_notes')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    
    # Bulk actions
    actions = ['mark_as_responded', 'mark_as_not_responded', 'export_contact_submissions', 'resend_notifications']
    
    def display_subject(self, obj):
        """Show appropriate subject in list view"""
        return obj.display_subject
    display_subject.short_description = 'Subject'
    
    def display_subject_readonly(self, obj):
        """Read-only field showing the actual subject for the form"""
        return obj.display_subject
    display_subject_readonly.short_description = 'Actual Subject'
    
    def responded_status(self, obj):
        """Show responded status with color coding"""
        if obj.responded:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Responded</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Pending</span>'
            )
    responded_status.short_description = 'Status'
    
    def view_message(self, obj):
        """Truncated message preview"""
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    view_message.short_description = 'Message Preview'
    
    def mark_as_responded(self, request, queryset):
        """Bulk action to mark submissions as responded"""
        updated = queryset.update(responded=True)
        self.message_user(request, f'{updated} submissions marked as responded.')
    mark_as_responded.short_description = "Mark selected submissions as responded"
    
    def mark_as_not_responded(self, request, queryset):
        """Bulk action to mark submissions as not responded"""
        updated = queryset.update(responded=False)
        self.message_user(request, f'{updated} submissions marked as not responded.')
    mark_as_not_responded.short_description = "Mark selected submissions as not responded"
    
    def export_contact_submissions(self, request, queryset):
        """Export contact submissions to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_submissions.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Subject', 'Message', 'Date', 'Responded'])
        
        for submission in queryset:
            writer.writerow([
                submission.name,
                submission.email,
                submission.display_subject,
                submission.message,
                submission.created_at.strftime('%Y-%m-%d %H:%M'),
                'Yes' if submission.responded else 'No'
            ])
        
        return response
    export_contact_submissions.short_description = "Export selected submissions to CSV"
    
    def resend_notifications(self, request, queryset):
        """Resend email notifications for selected contact submissions"""
        success_count = 0
        error_count = 0
        
        try:
            business_info = BusinessInfo.objects.first()
        except BusinessInfo.DoesNotExist:
            business_info = None
        
        for submission in queryset:
            try:
                # Resend notification to business owner
                notification_sent = EmailService.send_contact_notification(
                    submission, business_info
                )
                
                if notification_sent:
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                error_count += 1
        
        if success_count > 0:
            self.message_user(
                request, 
                f'Successfully resent {success_count} email notification(s).',
                level=messages.SUCCESS
            )
        
        if error_count > 0:
            self.message_user(
                request, 
                f'Failed to resend {error_count} email notification(s). Check email configuration.',
                level=messages.ERROR
            )
    
    resend_notifications.short_description = "Resend email notifications for selected submissions"
    
    def has_add_permission(self, request):
        """Prevent manual addition of contact submissions"""
        return False
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(SiteTheme)
class SiteThemeAdmin(admin.ModelAdmin):
    """
    Admin interface for managing site themes.
    """
    list_display = ('name', 'is_active', 'theme_preview', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'theme_preview')
    
    fieldsets = (
        ('Theme Information', {
            'fields': ('name', 'is_active')
        }),
        ('Primary Colors', {
            'fields': ('primary_color', 'secondary_color', 'accent_color'),
            'description': 'Main brand colors used throughout the site'
        }),
        ('Text Colors', {
            'fields': ('text_color', 'text_light'),
            'description': 'Text colors for readability and hierarchy'
        }),
        ('Background Colors', {
            'fields': ('background_color', 'background_secondary'),
            'description': 'Background colors for main content and sections'
        }),
        ('Navigation Colors', {
            'fields': ('navbar_bg', 'navbar_text', 'navbar_hover'),
            'description': 'Navigation bar color scheme'
        }),
        ('Button Colors', {
            'fields': ('button_primary_bg', 'button_primary_text', 'button_secondary_bg', 'button_secondary_text'),
            'description': 'Button styling colors'
        }),
        ('Footer Colors', {
            'fields': ('footer_bg', 'footer_text', 'footer_link'),
            'description': 'Footer color scheme'
        }),
        ('Menu Page Decoration', {
            'fields': ('menu_decoration_image', 'menu_decoration_alt_text'),
            'description': 'Upload a decorative image to replace the white stats box on the menu page'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def theme_preview(self, obj):
        """Show a preview of the theme colors"""
        if obj:
            return format_html(
                '<div style="display: flex; gap: 5px;">'
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;" title="Primary"></div>'
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;" title="Secondary"></div>'
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;" title="Accent"></div>'
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;" title="Text"></div>'
                '</div>',
                obj.primary_color,
                obj.secondary_color,
                obj.accent_color,
                obj.text_color
            )
        return '-'
    theme_preview.short_description = 'Color Preview'
    
    def save_model(self, request, obj, form, change):
        """Ensure only one active theme and show success message"""
        super().save_model(request, obj, form, change)
        
        if obj.is_active:
            self.message_user(
                request,
                f'Theme "{obj.name}" is now active and will be applied to the website.',
                level=messages.SUCCESS
            )
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of active theme"""
        if obj and obj.is_active:
            return False
        return super().has_delete_permission(request, obj)
    
    actions = ['activate_theme', 'duplicate_theme']
    
    def activate_theme(self, request, queryset):
        """Bulk action to activate a theme"""
        if queryset.count() != 1:
            self.message_user(
                request, 
                'Please select exactly one theme to activate.',
                level=messages.ERROR
            )
            return
        
        theme = queryset.first()
        SiteTheme.objects.filter(is_active=True).update(is_active=False)
        theme.is_active = True
        theme.save()
        
        self.message_user(
            request,
            f'Theme "{theme.name}" has been activated.',
            level=messages.SUCCESS
        )
    activate_theme.short_description = "Activate selected theme"
    
    def duplicate_theme(self, request, queryset):
        """Bulk action to duplicate themes"""
        for theme in queryset:
            theme.pk = None
            theme.name = f"{theme.name} (Copy)"
            theme.is_active = False
            theme.save()
        
        count = queryset.count()
        self.message_user(
            request,
            f'Successfully duplicated {count} theme(s).',
            level=messages.SUCCESS
        )
    duplicate_theme.short_description = "Duplicate selected themes"

class WhiteRavenAdminSite(AdminSite):
    """
    Custom Admin Site for White Raven Pourhouse with enhanced dashboard
    """
    site_header = "White Raven Pourhouse Admin"
    site_title = "White Raven Admin"
    index_title = "Administration Dashboard"
    
    def index(self, request, extra_context=None):
        """
        Custom admin index with business metrics
        """
        # Import here to avoid circular imports
        from menu.models import MenuItem, Category
        from staff.models import Employee, Schedule
        
        extra_context = extra_context or {}
        
        # Menu statistics
        menu_stats = {
            'total_items': MenuItem.objects.count(),
            'available_items': MenuItem.objects.filter(available=True).count(),
            'categories': Category.objects.filter(active=True).count(),
        }
        
        # Staff statistics  
        staff_stats = {
            'total_employees': Employee.objects.count(),
            'active_employees': Employee.objects.filter(employment_status='active').count(),
        }
        
        # Schedule statistics (this week)
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        this_week_schedules = Schedule.objects.filter(
            date__gte=week_start,
            date__lte=week_end,
            status__in=['scheduled', 'confirmed', 'completed']
        )
        
        total_hours = sum(schedule.scheduled_hours for schedule in this_week_schedules)
        
        schedule_stats = {
            'this_week_shifts': this_week_schedules.count(),
            'total_hours': round(total_hours, 1),
        }
        
        # Contact form statistics
        contact_stats = {
            'unresponded_count': ContactSubmission.objects.filter(responded=False).count(),
            'total_submissions': ContactSubmission.objects.count(),
        }
        
        # Recent activity (simplified)
        recent_activity = []
        
        # Recent menu items
        recent_menu_items = MenuItem.objects.order_by('-created_at')[:3]
        for item in recent_menu_items:
            recent_activity.append({
                'timestamp': item.created_at,
                'description': f'New menu item added: {item.name}'
            })
        
        # Recent employees
        recent_employees = Employee.objects.order_by('-created_at')[:2]
        for emp in recent_employees:
            recent_activity.append({
                'timestamp': emp.created_at,
                'description': f'New employee added: {emp.user.get_full_name()}'
            })
        
        # Recent contact submissions
        recent_contacts = ContactSubmission.objects.order_by('-created_at')[:3]
        for contact in recent_contacts:
            recent_activity.append({
                'timestamp': contact.created_at,
                'description': f'Contact form submitted by {contact.name}'
            })
        
        # Sort recent activity by timestamp
        recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_activity = recent_activity[:5]  # Limit to 5 most recent
        
        extra_context.update({
            'menu_stats': menu_stats,
            'staff_stats': staff_stats,
            'schedule_stats': schedule_stats,
            'contact_stats': contact_stats,
            'recent_activity': recent_activity,
        })
        
        return super().index(request, extra_context)

# Create custom admin site instance
admin_site = WhiteRavenAdminSite(name='white_raven_admin')

# Register models with custom admin site
admin_site.register(BusinessInfo, BusinessInfoAdmin)
admin_site.register(ContactSubmission, ContactSubmissionAdmin)
admin_site.register(SiteTheme, SiteThemeAdmin)

# Also customize default admin site
admin.site.site_header = "White Raven Pourhouse Admin"
admin.site.site_title = "White Raven Admin"
admin.site.index_title = "Welcome to White Raven Pourhouse Administration"