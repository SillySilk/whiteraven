"""
Email utilities for White Raven Pourhouse website.
Handles email sending with templates, proper error handling, and spam prevention.
"""

import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

# Rate limiting for email sending
class EmailRateLimiter:
    """Simple rate limiter to prevent email spam"""
    
    @staticmethod
    def is_rate_limited(email_address, limit_type='contact', max_attempts=3, window_minutes=60):
        """
        Check if an email address has exceeded rate limits
        
        Args:
            email_address: Email to check
            limit_type: Type of email ('contact', 'notification')
            max_attempts: Maximum attempts in time window
            window_minutes: Time window in minutes
            
        Returns:
            bool: True if rate limited, False if allowed
        """
        cache_key = f"email_rate_limit_{limit_type}_{email_address}"
        
        # Get current attempts from cache
        attempts = cache.get(cache_key, [])
        now = timezone.now()
        
        # Remove old attempts outside the window
        cutoff = now - timedelta(minutes=window_minutes)
        attempts = [attempt for attempt in attempts if attempt > cutoff]
        
        # Check if we've exceeded the limit
        if len(attempts) >= max_attempts:
            logger.warning(f"Rate limit exceeded for {email_address} on {limit_type}")
            return True
        
        # Add current attempt and update cache
        attempts.append(now)
        cache.set(cache_key, attempts, timeout=window_minutes * 60)
        
        return False


class EmailService:
    """
    Service class for handling all email operations with templates and error handling.
    """
    
    @staticmethod
    def send_contact_notification(contact_submission, business_info=None):
        """
        Send email notification to business owner when a contact form is submitted.
        
        Args:
            contact_submission: ContactSubmission instance
            business_info: BusinessInfo instance (optional)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Check rate limiting for notifications
            if EmailRateLimiter.is_rate_limited(
                contact_submission.email, 
                'notification', 
                max_attempts=5, 
                window_minutes=60
            ):
                logger.warning(f"Rate limit exceeded for contact notification from {contact_submission.email}")
                return False
            
            # Prepare template context
            context = {
                'contact': contact_submission,
                'business_info': business_info,
                'submission_time': contact_submission.created_at,
            }
            
            # Render email templates
            html_content = render_to_string('emails/contact_notification.html', context)
            text_content = render_to_string('emails/contact_notification.txt', context)
            
            # Prepare email
            subject = f"{settings.EMAIL_SUBJECT_PREFIX}New Contact: {contact_submission.display_subject}"
            
            # Determine recipient
            recipient_email = None
            if business_info and business_info.email:
                recipient_email = business_info.email
            elif settings.ADMINS:
                recipient_email = settings.ADMINS[0][1]  # First admin email
            
            if not recipient_email:
                logger.warning("No recipient email configured for contact notifications")
                return False
            
            # Validate recipient email
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(recipient_email)
            except ValidationError:
                logger.error(f"Invalid recipient email address: {recipient_email}")
                return False
            
            # Create and send email with timeout
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
                reply_to=[contact_submission.email]  # Allow direct reply to customer
            )
            email.attach_alternative(html_content, "text/html")
            
            # Add custom headers for better email handling
            email.extra_headers.update({
                'X-Contact-Submission-ID': str(contact_submission.id),
                'X-Contact-Subject': contact_submission.display_subject,
                'X-Contact-Source': 'White Raven Pourhouse Website',
            })
            
            email.send()
            logger.info(f"Contact notification sent for submission {contact_submission.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send contact notification: {str(e)}")
            return False
    
    @staticmethod
    def send_contact_auto_reply(contact_submission, business_info=None):
        """
        Send auto-reply confirmation email to customer who submitted contact form.
        
        Args:
            contact_submission: ContactSubmission instance
            business_info: BusinessInfo instance (optional)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Check rate limiting for auto-replies
            if EmailRateLimiter.is_rate_limited(
                contact_submission.email, 
                'auto_reply', 
                max_attempts=3, 
                window_minutes=30
            ):
                logger.warning(f"Rate limit exceeded for auto-reply to {contact_submission.email}")
                return False
            
            # Validate customer email
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(contact_submission.email)
            except ValidationError:
                logger.error(f"Invalid customer email address: {contact_submission.email}")
                return False
            # Format business hours for display if available
            formatted_hours = {}
            if business_info and business_info.hours:
                days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                day_names = {
                    'monday': 'Monday', 'tuesday': 'Tuesday', 'wednesday': 'Wednesday',
                    'thursday': 'Thursday', 'friday': 'Friday', 'saturday': 'Saturday', 'sunday': 'Sunday'
                }
                
                for day in days_order:
                    day_info = business_info.hours.get(day, {})
                    if day_info.get('closed', True):
                        formatted_hours[day_names[day]] = 'Closed'
                    else:
                        try:
                            open_time = datetime.strptime(day_info['open'], '%H:%M').strftime('%-I:%M %p')
                            close_time = datetime.strptime(day_info['close'], '%H:%M').strftime('%-I:%M %p')
                            formatted_hours[day_names[day]] = f"{open_time} - {close_time}"
                        except (ValueError, KeyError):
                            formatted_hours[day_names[day]] = 'Hours not available'
            
            # Prepare template context
            context = {
                'contact': contact_submission,
                'business_info': business_info,
                'formatted_hours': formatted_hours,
            }
            
            # Render email templates
            html_content = render_to_string('emails/contact_auto_reply.html', context)
            text_content = render_to_string('emails/contact_auto_reply.txt', context)
            
            # Prepare email
            subject = f"{settings.EMAIL_SUBJECT_PREFIX}Thank you for contacting us!"
            
            # Create and send email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[contact_submission.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            email.send()
            logger.info(f"Auto-reply sent for contact submission {contact_submission.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send contact auto-reply: {str(e)}")
            return False
    
    @staticmethod
    def send_admin_notification(subject, message, level='info'):
        """
        Send notification email to site administrators.
        
        Args:
            subject: Email subject
            message: Email message
            level: Notification level ('info', 'warning', 'error')
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            if not settings.ADMINS:
                logger.warning("No administrators configured for notifications")
                return False
            
            # Add level prefix to subject
            level_prefix = {
                'info': 'INFO',
                'warning': 'WARNING', 
                'error': 'ERROR'
            }.get(level, 'NOTIFICATION')
            
            full_subject = f"{settings.EMAIL_SUBJECT_PREFIX}[{level_prefix}] {subject}"
            
            mail_admins(
                subject=full_subject,
                message=message,
                fail_silently=False
            )
            
            logger.info(f"Admin notification sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send admin notification: {str(e)}")
            return False
    
    @staticmethod
    def test_email_configuration():
        """
        Test email configuration by sending a test email to admins.
        
        Returns:
            dict: Result with 'success' bool and 'message' string
        """
        try:
            if not settings.ADMINS:
                return {
                    'success': False,
                    'message': 'No administrators configured for testing'
                }
            
            test_message = f"""
            This is a test email from White Raven Pourhouse website.
            
            Email configuration test performed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Email backend: {settings.EMAIL_BACKEND}
            From email: {settings.DEFAULT_FROM_EMAIL}
            
            If you receive this email, your email configuration is working correctly.
            """
            
            success = EmailService.send_admin_notification(
                subject="Email Configuration Test",
                message=test_message,
                level='info'
            )
            
            if success:
                return {
                    'success': True,
                    'message': 'Test email sent successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to send test email'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Email test failed: {str(e)}'
            }