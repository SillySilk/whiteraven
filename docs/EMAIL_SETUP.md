# Email Configuration Guide

This guide explains how to set up and configure email functionality for the White Raven Pourhouse website.

## Overview

The website includes comprehensive email functionality for:
- Contact form notifications to business owner
- Auto-reply confirmations to customers
- Admin notifications for system events
- Email template system with HTML and text versions

## Email Features

### Contact Form Emails
- **Notification to Business**: When a customer submits the contact form, an email is sent to the business owner
- **Auto-reply to Customer**: Customer receives a confirmation email with business info and hours
- **HTML Templates**: Professional-looking emails with White Raven branding
- **Admin Integration**: Ability to resend notifications from Django admin

### Email Templates
Located in `templates/emails/`:
- `contact_notification.html/txt` - Notification to business owner
- `contact_auto_reply.html/txt` - Confirmation to customer

## Configuration

### Development Setup
In development, emails are displayed in the console for testing:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production Setup

#### 1. Environment Variables
Create a `.env` file (use `.env.template` as reference):

```bash
# Production flag
PRODUCTION=True

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@whiteravenpourhouse.com
ADMIN_EMAIL=admin@whiteravenpourhouse.com
```

#### 2. Gmail Configuration (Recommended)
1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to [Google Account Settings](https://myaccount.google.com/apppasswords)
   - Select "Mail" and your device
   - Use the generated 16-character password as `EMAIL_HOST_PASSWORD`

#### 3. Alternative Email Providers
For other email providers, configure these settings:

**Outlook/Hotmail:**
```bash
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

**SendGrid:**
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

## Testing Email Configuration

### Command Line Testing
```bash
python manage.py test_email
```

### Admin Interface Testing
1. Log into Django admin
2. Go to Business Information
3. Click "Test Email Configuration" button
4. Check for success/error messages

### Testing with Custom Recipient
```bash
python manage.py test_email --to test@example.com
```

## Email Logging

Email events are logged to:
- Console (development)
- `logs/white_raven.log` (production)

Log levels:
- INFO: Successful email sending
- ERROR: Failed email attempts
- WARNING: Configuration issues

## Troubleshooting

### Common Issues

**1. Authentication Error**
- Check username/password credentials
- For Gmail, ensure you're using an App Password
- Verify 2-factor authentication is enabled

**2. Connection Timeout**
- Check EMAIL_HOST and EMAIL_PORT settings
- Verify firewall/network restrictions
- Try alternative ports (465 for SSL)

**3. No Emails Received**
- Check spam/junk folders
- Verify recipient email addresses
- Test with command line tool first

**4. SSL/TLS Errors**
```bash
# Try SSL instead of TLS
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_PORT=465
```

### Debug Steps
1. Run `python manage.py test_email` and check console output
2. Check `logs/white_raven.log` for detailed error messages
3. Verify environment variables are loaded correctly
4. Test with a simple email client using same credentials

## Security Best Practices

1. **App Passwords**: Use app-specific passwords instead of main account passwords
2. **Environment Variables**: Never commit email credentials to version control
3. **HTTPS**: Always use HTTPS in production to protect email data
4. **Rate Limiting**: Consider implementing rate limiting for contact forms

## Email Templates Customization

### Modifying Templates
Edit files in `templates/emails/`:
- HTML version for rich formatting
- Text version for plain email clients

### Template Context Variables
Available in email templates:
- `contact` - ContactSubmission object
- `business_info` - BusinessInfo object
- `formatted_hours` - Formatted business hours

### Adding New Email Types
1. Create new template files in `templates/emails/`
2. Add method to `EmailService` class in `core/email_utils.py`
3. Call from appropriate views or admin actions

## Monitoring and Maintenance

### Regular Tasks
- Monitor email delivery success rates
- Check log files for errors
- Test email configuration monthly
- Update email templates as needed

### Email Analytics
The system tracks:
- Contact form submission counts
- Email sending success/failure rates
- Response tracking in admin interface

## Production Deployment Notes

### PythonAnywhere Specific
- Email works out of the box with proper SMTP configuration
- No additional setup required beyond environment variables
- Monitor quota usage if using high-volume email services

### Environment Variables on PythonAnywhere
1. Go to "Web" tab in PythonAnywhere dashboard
2. Add environment variables in "Environment variables" section
3. Reload web app after changes

## Support

For email configuration issues:
1. Check this documentation first
2. Review Django email documentation
3. Test with email provider's documentation
4. Check server logs for detailed error messages