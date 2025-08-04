"""
Django management command to test email configuration.
Usage: python manage.py test_email
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from core.email_utils import EmailService


class Command(BaseCommand):
    help = 'Test email configuration by sending a test email to administrators'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to (overrides admin settings)',
        )

    def handle(self, *args, **options):
        self.stdout.write("Testing email configuration...")
        
        # Display current email settings
        self.stdout.write(f"Email Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
        
        if hasattr(settings, 'EMAIL_HOST'):
            self.stdout.write(f"Email Host: {settings.EMAIL_HOST}")
            self.stdout.write(f"Email Port: {settings.EMAIL_PORT}")
            self.stdout.write(f"Email Use TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
            self.stdout.write(f"Email Use SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
        
        if settings.ADMINS:
            self.stdout.write(f"Administrators: {[admin[1] for admin in settings.ADMINS]}")
        else:
            self.stdout.write(self.style.WARNING("No administrators configured"))
        
        self.stdout.write("-" * 50)
        
        # Override recipient if provided
        if options['to']:
            # Temporarily override ADMINS setting for test
            original_admins = settings.ADMINS
            settings.ADMINS = [('Test User', options['to'])]
            self.stdout.write(f"Sending test email to: {options['to']}")
        
        try:
            # Run email test
            result = EmailService.test_email_configuration()
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f"[SUCCESS] {result['message']}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"[ERROR] {result['message']}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"[ERROR] Email test failed with exception: {str(e)}")
            )
        
        finally:
            # Restore original ADMINS setting if it was overridden
            if options['to']:
                settings.ADMINS = original_admins
        
        self.stdout.write("-" * 50)
        self.stdout.write("Email configuration test completed.")