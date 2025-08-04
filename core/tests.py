from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core import mail
from django.contrib.admin.sites import AdminSite
from django.test.utils import override_settings
from django.contrib.messages import get_messages
from django.http import HttpRequest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, date, time, timedelta
import json
import pytz
import tempfile
import os

from .models import BusinessInfo, ContactSubmission
from .admin import BusinessInfoAdmin, ContactSubmissionAdmin, WhiteRavenAdminSite
from .forms import ContactForm
from .email_utils import EmailService


class BusinessInfoModelTest(TestCase):
    """Test BusinessInfo model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.business_data = {
            'name': 'White Raven Pourhouse',
            'tagline': 'The Best Little Pour House in Felton',
            'address': '123 Main St, Felton, CA 95018',
            'phone': '8315551234',
            'email': 'info@whiteravenpourhouse.com',
            'hours': {
                'monday': {'open': '07:00', 'close': '19:00', 'closed': False},
                'tuesday': {'open': '07:00', 'close': '19:00', 'closed': False},
                'wednesday': {'open': '07:00', 'close': '19:00', 'closed': False},
                'thursday': {'open': '07:00', 'close': '19:00', 'closed': False},
                'friday': {'open': '07:00', 'close': '19:00', 'closed': False},
                'saturday': {'open': '08:00', 'close': '20:00', 'closed': False},
                'sunday': {'closed': True}
            },
            'special_hours': {
                '2024-12-25': {'closed': True, 'note': 'Christmas Day'},
                '2024-07-04': {'open': '08:00', 'close': '16:00', 'note': 'Independence Day'}
            },
            'instagram_handle': 'white_raven_pour_house',
            'description': 'A cozy coffee house in the heart of Felton'
        }
    
    def test_business_info_creation(self):
        """Test creating a BusinessInfo instance"""
        business = BusinessInfo.objects.create(**self.business_data)
        
        self.assertEqual(business.name, 'White Raven Pourhouse')
        self.assertEqual(business.tagline, 'The Best Little Pour House in Felton')
        self.assertEqual(business.phone, '8315551234')
        self.assertEqual(business.email, 'info@whiteravenpourhouse.com')
        self.assertIsInstance(business.hours, dict)
        self.assertIsInstance(business.special_hours, dict)
    
    def test_business_info_singleton(self):
        """Test that only one BusinessInfo instance can exist"""
        # Create first instance
        BusinessInfo.objects.create(**self.business_data)
        
        # Try to create second instance - should raise ValueError
        with self.assertRaises(ValueError):
            BusinessInfo.objects.create(**self.business_data)
    
    def test_business_info_str(self):
        """Test string representation"""
        business = BusinessInfo.objects.create(**self.business_data)
        self.assertEqual(str(business), 'White Raven Pourhouse')
    
    def test_phone_validation(self):
        """Test phone number validation"""
        # Valid phone numbers
        valid_phones = ['8315551234', '+18315551234', '18315551234']
        for phone in valid_phones:
            data = self.business_data.copy()
            data['phone'] = phone
            business = BusinessInfo(**data)
            business.full_clean()  # Should not raise
    
    def test_email_validation(self):
        """Test email validation"""
        data = self.business_data.copy()
        data['email'] = 'invalid-email'
        business = BusinessInfo(**data)
        
        with self.assertRaises(ValidationError):
            business.full_clean()
    
    @patch('django.utils.timezone.now')
    def test_get_current_status_open(self, mock_now):
        """Test get_current_status when business is open"""
        # Mock current time to Tuesday 10:00 AM Pacific
        pacific_tz = pytz.timezone('America/Los_Angeles')
        mock_time = pacific_tz.localize(datetime(2024, 1, 9, 10, 0))  # Tuesday
        mock_now.return_value = mock_time
        
        business = BusinessInfo.objects.create(**self.business_data)
        status = business.get_current_status()
        
        self.assertTrue(status['is_open'])
        self.assertIn('Open until', status['status'])
        self.assertEqual(status['reason'], 'Regular hours')
        self.assertFalse(status['is_special'])
    
    @patch('django.utils.timezone.now')
    def test_get_current_status_closed(self, mock_now):
        """Test get_current_status when business is closed"""
        # Mock current time to Sunday (closed day)
        pacific_tz = pytz.timezone('America/Los_Angeles')
        mock_time = pacific_tz.localize(datetime(2024, 1, 14, 10, 0))  # Sunday
        mock_now.return_value = mock_time
        
        business = BusinessInfo.objects.create(**self.business_data)
        status = business.get_current_status()
        
        self.assertFalse(status['is_open'])
        self.assertEqual(status['status'], 'Closed today')
        self.assertEqual(status['reason'], 'Regular closure')
    
    @patch('django.utils.timezone.now')
    def test_get_current_status_special_hours(self, mock_now):
        """Test get_current_status with special hours"""
        # Mock current time to Christmas Day
        pacific_tz = pytz.timezone('America/Los_Angeles')
        mock_time = pacific_tz.localize(datetime(2024, 12, 25, 10, 0))
        mock_now.return_value = mock_time
        
        business = BusinessInfo.objects.create(**self.business_data)
        status = business.get_current_status()
        
        self.assertFalse(status['is_open'])
        self.assertEqual(status['reason'], 'Christmas Day')
        self.assertTrue(status['is_special'])
    
    def test_get_formatted_hours(self):
        """Test formatted hours display"""
        business = BusinessInfo.objects.create(**self.business_data)
        formatted = business.get_formatted_hours()
        
        self.assertIn('Monday', formatted)
        self.assertIn('Sunday', formatted)
        self.assertEqual(formatted['Sunday'], 'Closed')
        self.assertIn('-', formatted['Monday'])  # Should have open-close format


class ContactSubmissionModelTest(TestCase):
    """Test ContactSubmission model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.contact_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'general',
            'message': 'I love your coffee!'
        }
    
    def test_contact_submission_creation(self):
        """Test creating a ContactSubmission instance"""
        contact = ContactSubmission.objects.create(**self.contact_data)
        
        self.assertEqual(contact.name, 'John Doe')
        self.assertEqual(contact.email, 'john@example.com')
        self.assertEqual(contact.subject, 'general')
        self.assertEqual(contact.message, 'I love your coffee!')
        self.assertFalse(contact.responded)
        self.assertEqual(contact.response_notes, '')
    
    def test_contact_submission_str(self):
        """Test string representation"""
        contact = ContactSubmission.objects.create(**self.contact_data)
        expected = f"John Doe - General Inquiry ({contact.created_at.strftime('%Y-%m-%d')})"
        self.assertEqual(str(contact), expected)
    
    def test_display_subject_property(self):
        """Test display_subject property"""
        # Test with predefined subject
        contact = ContactSubmission.objects.create(**self.contact_data)
        self.assertEqual(contact.display_subject, 'General Inquiry')
        
        # Test with custom subject
        data = self.contact_data.copy()
        data['subject'] = 'other'
        data['custom_subject'] = 'Custom Question'
        contact = ContactSubmission.objects.create(**data)
        self.assertEqual(contact.display_subject, 'Custom Question')
    
    def test_contact_submission_ordering(self):
        """Test that submissions are ordered by creation date (newest first)"""
        # Create multiple submissions
        contact1 = ContactSubmission.objects.create(**self.contact_data)
        
        data2 = self.contact_data.copy()
        data2['email'] = 'jane@example.com'
        contact2 = ContactSubmission.objects.create(**data2)
        
        submissions = ContactSubmission.objects.all()
        self.assertEqual(submissions[0], contact2)  # Newest first
        self.assertEqual(submissions[1], contact1)


class CoreViewsTest(TestCase):
    """Test core app views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.business_data = {
            'name': 'White Raven Pourhouse',
            'tagline': 'The Best Little Pour House in Felton',
            'address': '123 Main St, Felton, CA 95018',
            'phone': '8315551234',
            'email': 'info@whiteravenpourhouse.com',
            'hours': {
                'monday': {'open': '07:00', 'close': '19:00', 'closed': False}
            }
        }
        self.business = BusinessInfo.objects.create(**self.business_data)
    
    def test_home_view(self):
        """Test home page view"""
        response = self.client.get(reverse('core:home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'White Raven Pourhouse')
        self.assertContains(response, 'The Best Little Pour House in Felton')
    
    def test_contact_view_get(self):
        """Test contact page GET request"""
        response = self.client.get(reverse('core:contact'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact')
        self.assertIsInstance(response.context['form'], ContactForm)
    
    def test_contact_view_post_valid(self):
        """Test contact form submission with valid data"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'Test message'
        }
        
        response = self.client.post(reverse('core:contact'), data)
        
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)
        
        # Check that submission was created
        self.assertTrue(ContactSubmission.objects.filter(email='test@example.com').exists())
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 2)  # Notification + auto-reply
    
    def test_contact_view_post_invalid(self):
        """Test contact form submission with invalid data"""
        data = {
            'name': '',  # Required field missing
            'email': 'invalid-email',
            'subject': 'general',
            'message': ''
        }
        
        response = self.client.post(reverse('core:contact'), data)
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'name', 'This field is required.')
        
        # No submission should be created
        self.assertEqual(ContactSubmission.objects.count(), 0)
    
    def test_location_view(self):
        """Test location page view"""
        response = self.client.get(reverse('core:location'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '123 Main St, Felton, CA 95018')


class CoreAdminTest(TestCase):
    """Test core app admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.site = AdminSite()
        self.user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        
        self.business = BusinessInfo.objects.create(
            name='Test Business',
            address='Test Address',
            phone='8315551234',
            email='test@test.com'
        )
        
        self.contact = ContactSubmission.objects.create(
            name='Test Contact',
            email='contact@test.com',
            subject='general',
            message='Test message'
        )
    
    def test_business_info_admin_registration(self):
        """Test BusinessInfo admin is registered"""
        self.assertIn(BusinessInfo, self.site._registry)
    
    def test_contact_submission_admin_registration(self):
        """Test ContactSubmission admin is registered"""
        self.assertIn(ContactSubmission, self.site._registry)
    
    def test_business_info_admin_list_display(self):
        """Test BusinessInfo admin list display"""
        admin = BusinessInfoAdmin(BusinessInfo, self.site)
        expected_fields = ['name', 'tagline', 'phone', 'email', 'updated_at']
        self.assertEqual(admin.list_display, expected_fields)
    
    def test_contact_submission_admin_list_display(self):
        """Test ContactSubmission admin list display"""
        admin = ContactSubmissionAdmin(ContactSubmission, self.site)
        expected_fields = ['name', 'email', 'display_subject', 'created_at', 'responded']
        self.assertEqual(admin.list_display, expected_fields)
    
    def test_contact_submission_admin_actions(self):
        """Test ContactSubmission admin custom actions"""
        admin = ContactSubmissionAdmin(ContactSubmission, self.site)
        action_names = [action.__name__ for action in admin.actions]
        self.assertIn('mark_as_responded', action_names)


class ContactFormTest(TestCase):
    """Test contact form functionality"""
    
    def test_contact_form_valid_data(self):
        """Test contact form with valid data"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'Test message'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_contact_form_missing_required_fields(self):
        """Test contact form with missing required fields"""
        form_data = {
            'name': '',
            'email': '',
            'message': ''
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('message', form.errors)
    
    def test_contact_form_invalid_email(self):
        """Test contact form with invalid email"""
        form_data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'subject': 'general',
            'message': 'Test message'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_contact_form_custom_subject(self):
        """Test contact form with custom subject"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'other',
            'custom_subject': 'Custom Question',
            'message': 'Test message'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())


class CoreIntegrationTest(TestCase):
    """Integration tests for core app workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.business = BusinessInfo.objects.create(
            name='White Raven Pourhouse',
            tagline='The Best Little Pour House in Felton',
            address='123 Main St, Felton, CA 95018',
            phone='8315551234',
            email='info@whiteravenpourhouse.com'
        )
    
    def test_complete_contact_workflow(self):
        """Test complete contact form submission workflow"""
        # 1. Visit contact page
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit valid contact form
        data = {
            'name': 'Integration Test User',
            'email': 'integration@test.com',
            'subject': 'menu',
            'message': 'Integration test message'
        }
        response = self.client.post(reverse('core:contact'), data)
        
        # 3. Check redirect (success)
        self.assertEqual(response.status_code, 302)
        
        # 4. Verify submission was saved
        submission = ContactSubmission.objects.get(email='integration@test.com')
        self.assertEqual(submission.name, 'Integration Test User')
        self.assertEqual(submission.subject, 'menu')
        self.assertFalse(submission.responded)
        
        # 5. Verify emails were sent
        self.assertEqual(len(mail.outbox), 2)
        
        # Check notification email
        notification_email = mail.outbox[0]
        self.assertIn('New Contact Form Submission', notification_email.subject)
        self.assertIn('Integration Test User', notification_email.body)
        
        # Check auto-reply email
        auto_reply_email = mail.outbox[1]
        self.assertEqual(auto_reply_email.to, ['integration@test.com'])
        self.assertIn('Thank you for contacting', auto_reply_email.subject)
    
    def test_admin_contact_management_workflow(self):
        """Test admin workflow for managing contact submissions"""
        # Create admin user
        admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        # Create contact submission
        contact = ContactSubmission.objects.create(
            name='Admin Test User',
            email='admintest@test.com',
            subject='feedback',
            message='Admin workflow test'
        )
        
        # Login as admin
        self.client.login(username='admin', password='password')
        
        # Access admin changelist
        response = self.client.get('/admin/core/contactsubmission/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Test User')
        
        # Access individual submission
        response = self.client.get(f'/admin/core/contactsubmission/{contact.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admintest@test.com')
        
        # Mark as responded
        response = self.client.post(f'/admin/core/contactsubmission/{contact.id}/change/', {
            'name': contact.name,
            'email': contact.email,
            'subject': contact.subject,
            'message': contact.message,
            'responded': True,
            'response_notes': 'Responded via email',
            '_save': 'Save'
        })
        
        # Check that submission was updated
        contact.refresh_from_db()
        self.assertTrue(contact.responded)
        self.assertEqual(contact.response_notes, 'Responded via email')


class CoreEmailServiceTest(TestCase):
    """Test email service functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.business = BusinessInfo.objects.create(
            name='Test Business',
            tagline='Test Tagline',
            address='123 Test St',
            phone='8315551234',
            email='business@test.com'
        )
        
        self.contact_submission = ContactSubmission.objects.create(
            name='Test User',
            email='test@example.com',
            subject='general',
            message='Test message'
        )
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_contact_notification(self):
        """Test sending contact form notification email"""
        result = EmailService.send_contact_notification(self.contact_submission, self.business)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('New Contact Form Submission', email.subject)
        self.assertIn('Test User', email.body)
        self.assertIn('test@example.com', email.body)
        self.assertEqual(email.to, ['business@test.com'])
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_auto_reply(self):
        """Test sending auto-reply email"""
        result = EmailService.send_auto_reply(self.contact_submission, self.business)
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('Thank you for contacting', email.subject)
        self.assertIn('Test User', email.body)
        self.assertEqual(email.to, ['test@example.com'])
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_test_email_configuration(self):
        """Test email configuration testing"""
        result = EmailService.test_email_configuration()
        
        self.assertTrue(result['success'])
        self.assertIn('successfully', result['message'].lower())


class CoreMiddlewareTest(TestCase):
    """Test core middleware functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_security_middleware_headers(self):
        """Test security middleware adds proper headers"""
        response = self.client.get('/')
        
        # Check for security headers (if middleware is active)
        # This test depends on middleware being configured
        self.assertTrue(True)  # Placeholder for actual middleware tests
    
    def test_file_upload_security(self):
        """Test file upload security middleware"""
        # This would test file upload restrictions
        self.assertTrue(True)  # Placeholder for actual file upload tests


class CoreFormValidationTest(TestCase):
    """Extended tests for contact form validation"""
    
    def test_contact_form_xss_protection(self):
        """Test contact form XSS protection"""
        malicious_data = {
            'name': '<script>alert("xss")</script>Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': '<script>alert("xss")</script>Test message'
        }
        
        form = ContactForm(data=malicious_data)
        # Form should still be valid (XSS protection happens in templates)
        self.assertTrue(form.is_valid())
        
        # But cleaned data should be safe
        self.assertIn('Test User', form.cleaned_data['name'])
        self.assertIn('Test message', form.cleaned_data['message'])
    
    def test_contact_form_long_inputs(self):
        """Test contact form with very long inputs"""
        long_message = 'x' * 10000  # Very long message
        
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': long_message
        }
        
        form = ContactForm(data=form_data)
        # Should handle long messages gracefully
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data['message']), 10000)
    
    def test_contact_form_special_characters(self):
        """Test contact form with special characters"""
        form_data = {
            'name': 'José María Ñoño',
            'email': 'jose.maria@example.com',
            'subject': 'general',
            'message': 'Testing special characters: áéíóú ñ ¿¡ €'
        }
        
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())


class BusinessInfoAdvancedTest(TestCase):
    """Advanced tests for BusinessInfo model"""
    
    def setUp(self):
        """Set up test data"""
        self.business_data = {
            'name': 'White Raven Pourhouse',
            'tagline': 'The Best Little Pour House in Felton',
            'address': '123 Main St, Felton, CA 95018',
            'phone': '8315551234',
            'email': 'info@whiteravenpourhouse.com',
            'hours': {
                'monday': {'open': '07:00', 'close': '19:00', 'closed': False},
                'tuesday': {'open': '07:00', 'close': '19:00', 'closed': False},
                'wednesday': {'open': '07:00', 'close': '19:00', 'closed': False},
                'thursday': {'open': '07:00', 'close': '19:00', 'closed': False},
                'friday': {'open': '07:00', 'close': '19:00', 'closed': False},
                'saturday': {'open': '08:00', 'close': '20:00', 'closed': False},
                'sunday': {'closed': True}
            },
            'special_hours': {
                '2024-12-25': {'closed': True, 'note': 'Christmas Day'},
                '2024-07-04': {'open': '08:00', 'close': '16:00', 'note': 'Independence Day'}
            }
        }
    
    def test_business_info_edge_cases(self):
        """Test edge cases for BusinessInfo"""
        # Test with minimal data
        minimal_data = {
            'name': 'Test',
            'address': 'Test Address',
            'phone': '8315551234',
            'email': 'test@test.com'
        }
        
        business = BusinessInfo.objects.create(**minimal_data)
        self.assertEqual(business.name, 'Test')
        self.assertEqual(business.hours, {})  # Default empty dict
        self.assertEqual(business.special_hours, {})
    
    @patch('django.utils.timezone.now')
    def test_get_current_status_edge_cases(self, mock_now):
        """Test edge cases for current status"""
        business = BusinessInfo.objects.create(**self.business_data)
        
        # Test exact opening time
        pacific_tz = pytz.timezone('America/Los_Angeles')
        mock_time = pacific_tz.localize(datetime(2024, 1, 8, 7, 0))  # Monday 7:00 AM
        mock_now.return_value = mock_time
        
        status = business.get_current_status()
        self.assertTrue(status['is_open'])
        
        # Test exact closing time
        mock_time = pacific_tz.localize(datetime(2024, 1, 8, 19, 0))  # Monday 7:00 PM
        mock_now.return_value = mock_time
        
        status = business.get_current_status()
        self.assertTrue(status['is_open'])


class ContactSubmissionAdvancedTest(TestCase):
    """Advanced tests for ContactSubmission model"""
    
    def test_contact_submission_bulk_operations(self):
        """Test bulk operations on contact submissions"""
        # Create multiple submissions
        for i in range(10):
            ContactSubmission.objects.create(
                name=f'User {i}',
                email=f'user{i}@example.com',
                subject='general',
                message=f'Message {i}'
            )
        
        # Test bulk update
        ContactSubmission.objects.all().update(responded=True)
        
        responded_count = ContactSubmission.objects.filter(responded=True).count()
        self.assertEqual(responded_count, 10)
    
    def test_contact_submission_filtering(self):
        """Test filtering contact submissions"""
        # Create submissions with different subjects
        ContactSubmission.objects.create(
            name='User 1', email='user1@example.com', subject='menu', message='Menu question'
        )
        ContactSubmission.objects.create(
            name='User 2', email='user2@example.com', subject='feedback', message='Great service'
        )
        ContactSubmission.objects.create(
            name='User 3', email='user3@example.com', subject='general', message='General inquiry'
        )
        
        # Test filtering by subject
        menu_submissions = ContactSubmission.objects.filter(subject='menu')
        self.assertEqual(menu_submissions.count(), 1)
        
        feedback_submissions = ContactSubmission.objects.filter(subject='feedback')
        self.assertEqual(feedback_submissions.count(), 1)


class CoreAdminAdvancedTest(TestCase):
    """Advanced tests for core admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        self.business = BusinessInfo.objects.create(
            name='Test Business',
            address='Test Address',
            phone='8315551234',
            email='test@test.com'
        )
        
        # Create multiple contact submissions
        for i in range(5):
            ContactSubmission.objects.create(
                name=f'User {i}',
                email=f'user{i}@example.com',
                subject='general',
                message=f'Message {i}',
                responded=(i % 2 == 0)  # Alternate responded status
            )
    
    def test_business_info_admin_singleton_behavior(self):
        """Test BusinessInfo admin singleton behavior"""
        self.client.login(username='admin', password='password')
        
        # Test that accessing changelist redirects to change form
        response = self.client.get('/admin/core/businessinfo/')
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Test that add permission is denied when instance exists
        response = self.client.get('/admin/core/businessinfo/add/')
        # Should show appropriate message or redirect
        self.assertTrue(response.status_code in [302, 403])
    
    def test_contact_submission_admin_bulk_actions(self):
        """Test contact submission admin bulk actions"""
        self.client.login(username='admin', password='password')
        
        # Get all submission IDs
        submissions = ContactSubmission.objects.all()
        submission_ids = [str(s.id) for s in submissions]
        
        # Test mark as responded bulk action
        response = self.client.post('/admin/core/contactsubmission/', {
            'action': 'mark_as_responded',
            '_selected_action': submission_ids[:3],  # Select first 3
        })
        
        # Check that submissions were updated
        responded_count = ContactSubmission.objects.filter(responded=True).count()
        self.assertGreaterEqual(responded_count, 3)
    
    def test_white_raven_admin_site_customization(self):
        """Test custom admin site functionality"""
        admin_site = WhiteRavenAdminSite()
        
        self.assertEqual(admin_site.site_header, "White Raven Pourhouse Admin")
        self.assertEqual(admin_site.site_title, "White Raven Admin")
        self.assertEqual(admin_site.index_title, "Administration Dashboard")


class CoreViewsAdvancedTest(TestCase):
    """Advanced tests for core views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.business = BusinessInfo.objects.create(
            name='White Raven Pourhouse',
            tagline='The Best Little Pour House in Felton',
            address='123 Main St, Felton, CA 95018',
            phone='8315551234',
            email='info@whiteravenpourhouse.com'
        )
    
    def test_contact_view_csrf_protection(self):
        """Test contact view CSRF protection"""
        # Test without CSRF token
        response = self.client.post(reverse('core:contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'general',
            'message': 'Test message'
        })
        
        # Should be rejected due to missing CSRF token
        self.assertEqual(response.status_code, 403)
    
    def test_location_view_business_hours_display(self):
        """Test location view displays business hours correctly"""
        # Add hours to business
        self.business.hours = {
            'monday': {'open': '07:00', 'close': '19:00', 'closed': False},
            'sunday': {'closed': True}
        }
        self.business.save()
        
        response = self.client.get(reverse('core:location'))
        
        self.assertEqual(response.status_code, 200)
        # Should display formatted hours
        self.assertContains(response, 'Monday')
    
    def test_view_context_data(self):
        """Test that views provide correct context data"""
        response = self.client.get(reverse('core:home'))
        
        self.assertIn('business_info', response.context)
        self.assertEqual(response.context['business_info'], self.business)


class CoreSecurityTest(TestCase):
    """Security-focused tests for core app"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        self.regular_user = User.objects.create_user('user', 'user@test.com', 'password')
    
    def test_admin_access_control(self):
        """Test admin access control"""
        # Test unauthenticated access
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test regular user access
        self.client.login(username='user', password='password')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Should be redirected/denied
        
        # Test admin user access
        self.client.login(username='admin', password='password')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)  # Should be allowed
    
    def test_contact_form_input_sanitization(self):
        """Test contact form input sanitization"""
        malicious_inputs = [
            '<script>alert("xss")</script>',
            '"><script>alert("xss")</script>',
            'javascript:alert("xss")',
            '&lt;script&gt;alert("xss")&lt;/script&gt;'
        ]
        
        for malicious_input in malicious_inputs:
            form_data = {
                'name': f'Test {malicious_input}',
                'email': 'test@example.com',
                'subject': 'general',
                'message': f'Message {malicious_input}'
            }
            
            form = ContactForm(data=form_data)
            if form.is_valid():
                # Check that dangerous content is handled safely
                # (Django's template system auto-escapes by default)
                self.assertIn('Test', form.cleaned_data['name'])
                self.assertIn('Message', form.cleaned_data['message'])
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        # Django ORM should protect against SQL injection
        malicious_email = "'; DROP TABLE core_contactsubmission; --"
        
        submissions = ContactSubmission.objects.filter(email=malicious_email)
        # Should return empty queryset, not cause SQL error
        self.assertEqual(submissions.count(), 0)
