from django.core.management.base import BaseCommand
from django.test import RequestFactory, Client
from django.contrib.messages import get_messages
from django.urls import reverse
from core.forms import ContactForm
from core.models import ContactSubmission, BusinessInfo
from core.email_utils import EmailService
import json


class Command(BaseCommand):
    help = 'Test the contact form functionality and validation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-email',
            action='store_true',
            help='Test email sending functionality',
        )
        parser.add_argument(
            '--test-validation',
            action='store_true',
            help='Test form validation',
        )
        parser.add_argument(
            '--test-submission',
            action='store_true',
            help='Test form submission workflow',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Contact Form Functionality'))
        self.stdout.write('=' * 50)

        if options['test_validation'] or not any([options['test_email'], options['test_submission']]):
            self.test_form_validation()

        if options['test_email'] or not any([options['test_validation'], options['test_submission']]):
            self.test_email_functionality()

        if options['test_submission'] or not any([options['test_validation'], options['test_email']]):
            self.test_form_submission()

        self.stdout.write(self.style.SUCCESS('\nAll tests completed!'))

    def test_form_validation(self):
        """Test form validation rules"""
        self.stdout.write('\n1. Testing Form Validation')
        self.stdout.write('-' * 30)

        # Test valid form data
        valid_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'subject': 'general',
            'message': 'This is a test message for the contact form functionality.',
            'honeypot': ''  # Should be empty
        }

        form = ContactForm(data=valid_data)
        if form.is_valid():
            self.stdout.write(self.style.SUCCESS('[PASS] Valid form data passes validation'))
        else:
            self.stdout.write(self.style.ERROR(f'[FAIL] Valid form data failed: {form.errors}'))

        # Test invalid email
        invalid_email_data = valid_data.copy()
        invalid_email_data['email'] = 'invalid-email'
        form = ContactForm(data=invalid_email_data)
        if not form.is_valid() and 'email' in form.errors:
            self.stdout.write(self.style.SUCCESS('[PASS] Invalid email rejected'))
        else:
            self.stdout.write(self.style.ERROR('[FAIL] Invalid email not rejected'))

        # Test spam protection (honeypot)
        spam_data = valid_data.copy()
        spam_data['honeypot'] = 'spam content'
        form = ContactForm(data=spam_data)
        if not form.is_valid() and 'honeypot' in form.errors:
            self.stdout.write(self.style.SUCCESS('[PASS] Honeypot spam protection working'))
        else:
            self.stdout.write(self.style.ERROR('[FAIL] Honeypot spam protection failed'))

        # Test short message
        short_message_data = valid_data.copy()
        short_message_data['message'] = 'Too short'
        form = ContactForm(data=short_message_data)
        if not form.is_valid() and 'message' in form.errors:
            self.stdout.write(self.style.SUCCESS('[PASS] Short message validation working'))
        else:
            self.stdout.write(self.style.ERROR('[FAIL] Short message validation failed'))

        # Test custom subject requirement
        custom_subject_data = valid_data.copy()
        custom_subject_data['subject'] = 'other'
        # Don't provide custom_subject
        form = ContactForm(data=custom_subject_data)
        if not form.is_valid():
            self.stdout.write(self.style.SUCCESS('[PASS] Custom subject requirement working'))
        else:
            self.stdout.write(self.style.ERROR('[FAIL] Custom subject requirement failed'))

    def test_email_functionality(self):
        """Test email sending functionality"""
        self.stdout.write('\n2. Testing Email Functionality')
        self.stdout.write('-' * 30)

        # Test email configuration
        result = EmailService.test_email_configuration()
        if result['success']:
            self.stdout.write(self.style.SUCCESS(f'[PASS] Email configuration test: {result["message"]}'))
        else:
            self.stdout.write(self.style.WARNING(f'[WARN] Email configuration: {result["message"]}'))

        # Create a test contact submission
        try:
            test_submission = ContactSubmission.objects.create(
                name='Test User',
                email='test@example.com',
                subject='general',
                message='This is a test submission for email functionality.'
            )

            # Get business info if available
            try:
                business_info = BusinessInfo.objects.first()
            except BusinessInfo.DoesNotExist:
                business_info = None

            # Test notification email
            notification_sent = EmailService.send_contact_notification(test_submission, business_info)
            if notification_sent:
                self.stdout.write(self.style.SUCCESS('[PASS] Contact notification email sent'))
            else:
                self.stdout.write(self.style.WARNING('[WARN] Contact notification email failed'))

            # Test auto-reply email
            auto_reply_sent = EmailService.send_contact_auto_reply(test_submission, business_info)
            if auto_reply_sent:
                self.stdout.write(self.style.SUCCESS('[PASS] Auto-reply email sent'))
            else:
                self.stdout.write(self.style.WARNING('[WARN] Auto-reply email failed'))

            # Clean up test submission
            test_submission.delete()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[FAIL] Email test failed: {str(e)}'))

    def test_form_submission(self):
        """Test complete form submission workflow"""
        self.stdout.write('\n3. Testing Form Submission Workflow')
        self.stdout.write('-' * 30)

        client = Client()
        
        # Get contact page
        try:
            response = client.get(reverse('core:contact'))
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('[PASS] Contact page loads successfully'))
            else:
                self.stdout.write(self.style.ERROR(f'[FAIL] Contact page failed: {response.status_code}'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[FAIL] Contact page error: {str(e)}'))
            return

        # Test form submission
        form_data = {
            'name': 'Test Customer',
            'email': 'customer@example.com',
            'subject': 'feedback',
            'message': 'This is a test message to verify the contact form submission workflow.',
            'honeypot': ''
        }

        try:
            initial_count = ContactSubmission.objects.count()
            
            response = client.post(reverse('core:contact'), data=form_data)
            
            # Check if submission was created
            final_count = ContactSubmission.objects.count()
            if final_count > initial_count:
                self.stdout.write(self.style.SUCCESS('[PASS] Contact submission saved to database'))
                
                # Get the submitted form
                submission = ContactSubmission.objects.latest('created_at')
                self.stdout.write(f'  - Submission ID: {submission.id}')
                self.stdout.write(f'  - Name: {submission.name}')
                self.stdout.write(f'  - Email: {submission.email}')
                self.stdout.write(f'  - Subject: {submission.display_subject}')
                
                # Clean up test submission
                submission.delete()
            else:
                self.stdout.write(self.style.ERROR('[FAIL] Contact submission not saved'))

            # Check for success redirect
            if response.status_code == 302:
                self.stdout.write(self.style.SUCCESS('[PASS] Form submission redirects correctly'))
            else:
                self.stdout.write(self.style.WARNING(f'[WARN] Unexpected response code: {response.status_code}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[FAIL] Form submission test failed: {str(e)}'))

        # Test invalid form submission
        try:
            invalid_data = form_data.copy()
            invalid_data['email'] = 'invalid-email'
            
            response = client.post(reverse('core:contact'), data=invalid_data)
            
            if response.status_code == 200:  # Should stay on same page with errors
                self.stdout.write(self.style.SUCCESS('[PASS] Invalid form submission handled correctly'))
            else:
                self.stdout.write(self.style.WARNING(f'[WARN] Invalid form handling: {response.status_code}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[FAIL] Invalid form test failed: {str(e)}'))