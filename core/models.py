from django.db import models
from django.core.validators import RegexValidator
from colorfield.fields import ColorField

class BusinessInfo(models.Model):
    """
    Store basic business information for White Raven Pourhouse.
    Singleton model - only one instance should exist.
    """
    name = models.CharField(
        max_length=100, 
        default="White Raven Pourhouse",
        help_text="Business name"
    )
    tagline = models.CharField(
        max_length=200, 
        default="The Best Little Pour House in Felton",
        help_text="Business tagline or slogan"
    )
    address = models.TextField(
        help_text="Full business address including city, state, zip"
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=20, 
        help_text="Contact phone number"
    )
    
    email = models.EmailField(
        help_text="Business contact email"
    )
    
    # Store operating hours as JSON for flexibility
    hours = models.JSONField(
        default=dict,
        help_text="Operating hours by day of week. Format: {'monday': {'open': '07:00', 'close': '19:00', 'closed': false}, ...}",
        blank=True
    )
    
    # Store special hours (holidays, temporary closures, etc.)
    special_hours = models.JSONField(
        default=dict,
        help_text="Special hours for specific dates. Format: {'2024-12-25': {'closed': true, 'note': 'Christmas Day'}, '2024-07-04': {'open': '08:00', 'close': '16:00', 'note': 'Independence Day - Limited Hours'}}",
        blank=True
    )
    
    instagram_handle = models.CharField(
        max_length=50,
        blank=True,
        help_text="Instagram username (without @)"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Brief description of the business for the homepage"
    )
    
    hero_image = models.ImageField(
        upload_to='',
        blank=True,
        null=True,
        help_text="Hero image for the homepage (recommended size: 1200x600px)"
    )
    
    about_image = models.ImageField(
        upload_to='',
        blank=True,
        null=True,
        help_text="Image for the About page story section (recommended size: 600x400px)"
    )
    
    location_image = models.ImageField(
        upload_to='',
        blank=True,
        null=True,
        help_text="Image for the Location page header (recommended size: 600x400px)"
    )
    
    # Social Media Links
    facebook_url = models.URLField(
        blank=True,
        help_text="Full Facebook page URL (e.g., https://facebook.com/whiteravenpourhouse)"
    )
    
    instagram_url = models.URLField(
        blank=True,
        help_text="Full Instagram page URL (e.g., https://instagram.com/white_raven_pour_house)"
    )
    
    # Marketing Content
    meta_description = models.TextField(
        default="White Raven Pourhouse - The Best Little Pour House in Felton. Serving exceptional coffee and creating memorable experiences in Felton, CA.",
        help_text="SEO meta description for the website"
    )
    
    welcome_message = models.TextField(
        blank=True,
        help_text="Welcome message for homepage (falls back to default if empty)"
    )
    
    footer_tagline = models.CharField(
        max_length=200,
        default="Made with ❤ in Felton, CA",
        help_text="Tagline shown in website footer"
    )
    
    copyright_text = models.CharField(
        max_length=200,
        default="White Raven Pourhouse",
        help_text="Business name for copyright notice"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Business Information"
        verbose_name_plural = "Business Information"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Ensure only one BusinessInfo instance exists"""
        if not self.pk and BusinessInfo.objects.exists():
            # If trying to create a new instance when one already exists
            raise ValueError("Only one BusinessInfo instance is allowed")
        super().save(*args, **kwargs)
    
    def get_current_status(self):
        """
        Get current business status (open/closed) based on current time in Pacific timezone.
        Returns dict with status info including open/closed, next change time, and any special notes.
        """
        from django.utils import timezone
        from datetime import datetime, time
        import pytz
        
        # Get current time in Pacific timezone
        pacific_tz = pytz.timezone('America/Los_Angeles')
        now = timezone.now().astimezone(pacific_tz)
        current_date = now.date()
        current_time = now.time()
        current_day = now.strftime('%A').lower()
        
        # Check for special hours first (holidays, special events, etc.)
        date_str = current_date.strftime('%Y-%m-%d')
        if self.special_hours and date_str in self.special_hours:
            special_info = self.special_hours[date_str]
            if special_info.get('closed', False):
                return {
                    'is_open': False,
                    'status': 'Closed',
                    'reason': special_info.get('note', 'Special closure'),
                    'next_change': self._get_next_opening(now),
                    'is_special': True
                }
            else:
                # Special hours for today
                try:
                    open_time = datetime.strptime(special_info['open'], '%H:%M').time()
                    close_time = datetime.strptime(special_info['close'], '%H:%M').time()
                    
                    if open_time <= current_time <= close_time:
                        return {
                            'is_open': True,
                            'status': f"Open until {self._format_time(close_time)}",
                            'reason': special_info.get('note', 'Special hours'),
                            'next_change': self._combine_date_time(current_date, close_time),
                            'is_special': True
                        }
                    else:
                        return {
                            'is_open': False,
                            'status': f"Closed - Opens at {self._format_time(open_time)}",
                            'reason': special_info.get('note', 'Special hours'),
                            'next_change': self._combine_date_time(current_date, open_time) if current_time < open_time else self._get_next_opening(now),
                            'is_special': True
                        }
                except (ValueError, KeyError):
                    pass
        
        # Check regular hours
        if not self.hours or current_day not in self.hours:
            return {
                'is_open': False,
                'status': 'Hours not available',
                'reason': 'Business hours not configured',
                'next_change': None,
                'is_special': False
            }
        
        day_hours = self.hours[current_day]
        
        if day_hours.get('closed', True):
            return {
                'is_open': False,
                'status': 'Closed today',
                'reason': 'Regular closure',
                'next_change': self._get_next_opening(now),
                'is_special': False
            }
        
        try:
            open_time = datetime.strptime(day_hours['open'], '%H:%M').time()
            close_time = datetime.strptime(day_hours['close'], '%H:%M').time()
            
            if open_time <= current_time <= close_time:
                return {
                    'is_open': True,
                    'status': f"Open until {self._format_time(close_time)}",
                    'reason': 'Regular hours',
                    'next_change': self._combine_date_time(current_date, close_time),
                    'is_special': False
                }
            elif current_time < open_time:
                return {
                    'is_open': False,
                    'status': f"Closed - Opens at {self._format_time(open_time)}",
                    'reason': 'Before opening time',
                    'next_change': self._combine_date_time(current_date, open_time),
                    'is_special': False
                }
            else:
                return {
                    'is_open': False,
                    'status': f"Closed - Opens at {self._get_next_opening_time()}",
                    'reason': 'After closing time',
                    'next_change': self._get_next_opening(now),
                    'is_special': False
                }
        except (ValueError, KeyError):
            return {
                'is_open': False,
                'status': 'Hours not available',
                'reason': 'Invalid hours configuration',
                'next_change': None,
                'is_special': False
            }
    
    def _combine_date_time(self, date, time):
        """Combine date and time into datetime object in Pacific timezone"""
        import pytz
        from datetime import datetime
        
        pacific_tz = pytz.timezone('America/Los_Angeles')
        dt = datetime.combine(date, time)
        return pacific_tz.localize(dt)
    
    def _get_next_opening(self, current_datetime):
        """Get the next opening time starting from current datetime"""
        from datetime import timedelta, datetime
        import pytz
        
        pacific_tz = pytz.timezone('America/Los_Angeles')
        
        # Check next 7 days
        for i in range(1, 8):
            check_date = (current_datetime + timedelta(days=i)).date()
            check_day = check_date.strftime('%A').lower()
            date_str = check_date.strftime('%Y-%m-%d')
            
            # Check special hours first
            if self.special_hours and date_str in self.special_hours:
                special_info = self.special_hours[date_str]
                if not special_info.get('closed', False) and 'open' in special_info:
                    try:
                        open_time = datetime.strptime(special_info['open'], '%H:%M').time()
                        return self._combine_date_time(check_date, open_time)
                    except (ValueError, KeyError):
                        continue
            
            # Check regular hours
            elif self.hours and check_day in self.hours:
                day_hours = self.hours[check_day]
                if not day_hours.get('closed', True) and 'open' in day_hours:
                    try:
                        open_time = datetime.strptime(day_hours['open'], '%H:%M').time()
                        return self._combine_date_time(check_date, open_time)
                    except (ValueError, KeyError):
                        continue
        
        return None
    
    def _get_next_opening_time(self):
        """Get next opening time as formatted string"""
        from django.utils import timezone
        import pytz
        
        pacific_tz = pytz.timezone('America/Los_Angeles')
        now = timezone.now().astimezone(pacific_tz)
        next_opening = self._get_next_opening(now)
        
        if next_opening:
            if next_opening.date() == now.date() + timezone.timedelta(days=1):
                return f"tomorrow at {self._format_time(next_opening.time())}"
            else:
                return f"{next_opening.strftime('%A')} at {self._format_time(next_opening.time())}"
        
        return "when hours are available"
    
    def _format_time(self, time_obj):
        """
        Format time object for display, handling cross-platform compatibility.
        """
        import platform
        
        # Use different format string based on platform
        if platform.system() == 'Windows':
            # Windows doesn't support %-I, use %#I instead
            return time_obj.strftime('%#I:%M %p')
        else:
            # Unix-like systems support %-I
            return time_obj.strftime('%-I:%M %p')
    
    def get_formatted_hours(self):
        """
        Get formatted hours for display, including special hours.
        Returns dict with day names as keys and formatted hour strings as values.
        """
        from datetime import datetime, date, timedelta
        
        formatted_hours = {}
        days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_names = {
            'monday': 'Monday',
            'tuesday': 'Tuesday', 
            'wednesday': 'Wednesday',
            'thursday': 'Thursday',
            'friday': 'Friday',
            'saturday': 'Saturday',
            'sunday': 'Sunday'
        }
        
        # Get current date to check for special hours in the upcoming week
        today = date.today()
        
        for i, day in enumerate(days_order):
            day_name = day_names[day]
            check_date = today + timedelta(days=(i - today.weekday()) % 7)
            date_str = check_date.strftime('%Y-%m-%d')
            
            # Check for special hours on this date
            if self.special_hours and date_str in self.special_hours:
                special_info = self.special_hours[date_str]
                if special_info.get('closed', False):
                    formatted_hours[day_name] = f"Closed - {special_info.get('note', 'Special closure')}"
                else:
                    try:
                        open_time_obj = datetime.strptime(special_info['open'], '%H:%M').time()
                        close_time_obj = datetime.strptime(special_info['close'], '%H:%M').time()
                        open_time = self._format_time(open_time_obj)
                        close_time = self._format_time(close_time_obj)
                        note = f" ({special_info.get('note', 'Special hours')})" if special_info.get('note') else ""
                        formatted_hours[day_name] = f"{open_time} - {close_time}{note}"
                    except (ValueError, KeyError):
                        formatted_hours[day_name] = f"Special hours - {special_info.get('note', 'See note')}"
            
            # Use regular hours
            elif self.hours and day in self.hours:
                day_info = self.hours[day]
                if day_info.get('closed', True):
                    formatted_hours[day_name] = 'Closed'
                else:
                    try:
                        open_time_obj = datetime.strptime(day_info['open'], '%H:%M').time()
                        close_time_obj = datetime.strptime(day_info['close'], '%H:%M').time()
                        open_time = self._format_time(open_time_obj)
                        close_time = self._format_time(close_time_obj)
                        formatted_hours[day_name] = f"{open_time} - {close_time}"
                    except (ValueError, KeyError):
                        formatted_hours[day_name] = 'Hours not available'
            else:
                formatted_hours[day_name] = 'Hours not set'
        
        return formatted_hours


class ContactSubmission(models.Model):
    """
    Store contact form submissions from website visitors.
    """
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('menu', 'Menu Question'),
        ('hours', 'Hours/Location'),
        ('event', 'Event/Catering'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(
        max_length=100,
        help_text="Visitor's full name"
    )
    
    email = models.EmailField(
        help_text="Visitor's email address"
    )
    
    subject = models.CharField(
        max_length=50,
        choices=SUBJECT_CHOICES,
        default='general',
        help_text="Subject category for the inquiry"
    )
    
    custom_subject = models.CharField(
        max_length=200,
        blank=True,
        help_text="Custom subject line if 'Other' is selected"
    )
    
    message = models.TextField(
        help_text="The visitor's message or inquiry"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the form was submitted"
    )
    
    responded = models.BooleanField(
        default=False,
        help_text="Mark as True when you've responded to this inquiry"
    )
    
    response_notes = models.TextField(
        blank=True,
        help_text="Internal notes about the response or follow-up"
    )
    
    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        ordering = ['-created_at']  # Most recent first
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%Y-%m-%d')})"
    
    @property
    def display_subject(self):
        """Return appropriate subject for display"""
        if self.subject == 'other' and self.custom_subject:
            return self.custom_subject
        return self.get_subject_display()


class SiteTheme(models.Model):
    """
    Site-wide theme customization model.
    Singleton model - only one active theme at a time.
    """
    name = models.CharField(
        max_length=100,
        default="White Raven Theme",
        help_text="Theme name for identification"
    )
    
    # Primary colors
    primary_color = ColorField(
        default='#6f4f28',  # Coffee brown
        help_text="Primary brand color (used for buttons, links)"
    )
    
    secondary_color = ColorField(
        default='#8b7355',  # Lighter brown
        help_text="Secondary color (used for accents, hover states)"
    )
    
    accent_color = ColorField(
        default='#d4af37',  # Gold
        help_text="Accent color (used for highlights, CTAs)"
    )
    
    # Text colors
    text_color = ColorField(
        default='#2c3e50',  # Dark gray-blue
        help_text="Main text color"
    )
    
    text_light = ColorField(
        default='#6c757d',  # Bootstrap gray
        help_text="Light text color (for descriptions, captions)"
    )
    
    # Background colors
    background_color = ColorField(
        default='#ffffff',  # White
        help_text="Main background color"
    )
    
    background_secondary = ColorField(
        default='#f8f9fa',  # Light gray
        help_text="Secondary background (for sections, cards)"
    )
    
    # Navigation colors
    navbar_bg = ColorField(
        default='#ffffff',  # White
        help_text="Navigation bar background color"
    )
    
    navbar_text = ColorField(
        default='#2c3e50',  # Dark gray-blue
        help_text="Navigation bar text color"
    )
    
    navbar_hover = ColorField(
        default='#6f4f28',  # Coffee brown
        help_text="Navigation bar hover color"
    )
    
    # Button colors
    button_primary_bg = ColorField(
        default='#6f4f28',  # Coffee brown
        help_text="Primary button background"
    )
    
    button_primary_text = ColorField(
        default='#ffffff',  # White
        help_text="Primary button text color"
    )
    
    button_secondary_bg = ColorField(
        default='#8b7355',  # Lighter brown
        help_text="Secondary button background"
    )
    
    button_secondary_text = ColorField(
        default='#ffffff',  # White
        help_text="Secondary button text color"
    )
    
    # Menu page decoration image
    menu_decoration_image = models.ImageField(
        upload_to='',
        blank=True,
        null=True,
        help_text="Decorative image for menu page (replaces the white stats box). Recommended size: 400x300px"
    )
    
    menu_decoration_alt_text = models.CharField(
        max_length=200,
        blank=True,
        default="White Raven Pourhouse decoration",
        help_text="Alt text for the menu decoration image (for accessibility)"
    )
    
    # Footer colors
    footer_bg = ColorField(
        default='#2c3e50',  # Dark gray-blue
        help_text="Footer background color"
    )
    
    footer_text = ColorField(
        default='#ffffff',  # White
        help_text="Footer text color"
    )
    
    footer_link = ColorField(
        default='#d4af37',  # Gold
        help_text="Footer link color"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this theme is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Theme"
        verbose_name_plural = "Site Themes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} {'(Active)' if self.is_active else ''}"
    
    def save(self, *args, **kwargs):
        """Ensure only one active theme exists"""
        if self.is_active:
            # Deactivate all other themes
            SiteTheme.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_theme(cls):
        """Get the currently active theme or create default if none exists"""
        active_theme = cls.objects.filter(is_active=True).first()
        if not active_theme:
            # Create default theme
            active_theme = cls.objects.create(
                name="Default White Raven Theme",
                is_active=True
            )
        return active_theme
    
    def get_css_variables(self):
        """Return CSS custom properties for this theme"""
        return {
            '--theme-primary': self.primary_color,
            '--theme-secondary': self.secondary_color,
            '--theme-accent': self.accent_color,
            '--theme-text': self.text_color,
            '--theme-text-light': self.text_light,
            '--theme-bg': self.background_color,
            '--theme-bg-secondary': self.background_secondary,
            '--theme-navbar-bg': self.navbar_bg,
            '--theme-navbar-text': self.navbar_text,
            '--theme-navbar-hover': self.navbar_hover,
            '--theme-btn-primary-bg': self.button_primary_bg,
            '--theme-btn-primary-text': self.button_primary_text,
            '--theme-btn-secondary-bg': self.button_secondary_bg,
            '--theme-btn-secondary-text': self.button_secondary_text,
            '--theme-footer-bg': self.footer_bg,
            '--theme-footer-text': self.footer_text,
            '--theme-footer-link': self.footer_link,
        }