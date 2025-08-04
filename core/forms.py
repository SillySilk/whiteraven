from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from .models import ContactSubmission

class ContactForm(forms.ModelForm):
    """
    Enhanced contact form for website visitors to submit inquiries with comprehensive validation
    """
    
    # Add honeypot field for spam prevention (hidden from users)
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="Do not fill this field"
    )
    
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'subject', 'custom_subject', 'message']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes and attributes to form fields
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your full name',
            'required': True,
            'maxlength': '100',
            'autocomplete': 'name'
        })
        
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'required': True,
            'type': 'email',
            'autocomplete': 'email'
        })
        
        self.fields['subject'].widget.attrs.update({
            'class': 'form-select',
            'required': True
        })
        
        self.fields['custom_subject'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Please specify your subject',
            'style': 'display: none;',  # Hidden by default, shown via JavaScript
            'maxlength': '200'
        })
        
        self.fields['message'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Tell us how we can help you...',
            'rows': 5,
            'required': True,
            'maxlength': '2000'
        })
        
        # Update field labels
        self.fields['name'].label = 'Full Name'
        self.fields['email'].label = 'Email Address'
        self.fields['subject'].label = 'Subject'
        self.fields['custom_subject'].label = 'Custom Subject'
        self.fields['message'].label = 'Message'
        
        # Set field help text
        self.fields['name'].help_text = 'Enter your full name (required)'
        self.fields['email'].help_text = 'We\'ll use this to respond to your inquiry'
        self.fields['message'].help_text = 'Maximum 2000 characters. Please be as detailed as possible.'
        
        # Make custom_subject not required initially
        self.fields['custom_subject'].required = False
        
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise ValidationError("Name is required.")
        
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters long.")
        
        # Check for valid name characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
            raise ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes.")
        
        # Prevent obvious spam patterns
        spam_patterns = ['test', 'aaa', '111', 'xxx']
        if any(pattern in name.lower() for pattern in spam_patterns) and len(name) <= 5:
            raise ValidationError("Please enter a valid name.")
        
        return name
    
    def clean_email(self):
        """Enhanced email validation"""
        email = self.cleaned_data.get('email', '').strip().lower()
        
        if not email:
            raise ValidationError("Email address is required.")
        
        # Use Django's built-in email validator
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Please enter a valid email address.")
        
        # Additional checks for common email issues
        if email.count('@') != 1:
            raise ValidationError("Email address must contain exactly one @ symbol.")
        
        local_part, domain = email.split('@')
        
        # Check for suspicious patterns
        if not local_part or not domain:
            raise ValidationError("Please enter a valid email address.")
        
        # Block obvious test/spam emails (but allow example.com for testing)
        spam_domains = ['test.com', 'fake.com', 'spam.com']
        if domain in spam_domains:
            raise ValidationError("Please use a valid email address.")
        
        return email
    
    def clean_message(self):
        """Validate message content"""
        message = self.cleaned_data.get('message', '').strip()
        
        if not message:
            raise ValidationError("Message is required.")
        
        if len(message) < 10:
            raise ValidationError("Message must be at least 10 characters long.")
        
        if len(message) > 2000:
            raise ValidationError("Message cannot exceed 2000 characters.")
        
        # Check for spam patterns
        spam_keywords = ['buy now', 'click here', 'free money', 'earn fast', 'guaranteed', 'no obligation']
        message_lower = message.lower()
        spam_count = sum(1 for keyword in spam_keywords if keyword in message_lower)
        
        if spam_count >= 2:
            raise ValidationError("Your message appears to contain spam content. Please revise your message.")
        
        # Check for excessive repetition
        words = message.split()
        if len(words) > 5:
            word_counts = {}
            for word in words:
                if len(word) > 3:  # Only check longer words
                    word_counts[word.lower()] = word_counts.get(word.lower(), 0) + 1
            
            # If any word appears more than 30% of the time, it's likely spam
            max_repetition = max(word_counts.values()) if word_counts else 0
            if max_repetition > len(words) * 0.3:
                raise ValidationError("Please avoid excessive repetition in your message.")
        
        return message
    
    def clean_custom_subject(self):
        """Validate custom subject when provided"""
        custom_subject = self.cleaned_data.get('custom_subject', '').strip()
        
        if custom_subject and len(custom_subject) < 3:
            raise ValidationError("Custom subject must be at least 3 characters long.")
        
        return custom_subject
    
    def clean_honeypot(self):
        """Check honeypot field for spam bots"""
        honeypot = self.cleaned_data.get('honeypot')
        
        if honeypot:
            raise ValidationError("Spam detected. Please try again.")
        
        return honeypot
    
    def clean(self):
        """
        Custom validation to ensure custom_subject is provided when subject is 'other'
        and additional cross-field validation
        """
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        custom_subject = cleaned_data.get('custom_subject')
        name = cleaned_data.get('name', '')
        email = cleaned_data.get('email', '')
        message = cleaned_data.get('message', '')
        
        # Validate custom subject requirement
        if subject == 'other' and not custom_subject:
            raise ValidationError(
                "Please provide a custom subject when selecting 'Other'."
            )
        
        # Cross-field spam detection
        if name and email and message:
            # Check if name appears to be same as email local part (common spam pattern)
            if '@' in email:
                email_local = email.split('@')[0].lower()
                name_clean = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
                if name_clean == email_local and len(name_clean) > 0:
                    # This could be legitimate, so just flag for review rather than block
                    pass
            
            # Check for identical or very similar name and message (spam pattern)
            if name.lower().strip() == message.lower().strip():
                raise ValidationError("Name and message cannot be identical.")
        
        return cleaned_data