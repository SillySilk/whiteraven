"""
Custom form fields and model fields for menu item image handling.
"""

import os
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.core.files.base import ContentFile
from .utils.image_processing import (
    validate_image, 
    optimize_image, 
    get_image_upload_path,
    cleanup_old_images,
    create_multiple_sizes
)
import logging

logger = logging.getLogger(__name__)


class MenuImageField(models.ImageField):
    """
    Custom ImageField for menu items with automatic processing and validation.
    """
    
    def __init__(self, *args, **kwargs):
        # Set default upload path
        kwargs.setdefault('upload_to', get_image_upload_path)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('help_text', 'Upload an image for this menu item. Images will be automatically optimized for web display.')
        
        super().__init__(*args, **kwargs)
    
    def pre_save(self, model_instance, add):
        """
        Process image before saving to database.
        """
        file = super().pre_save(model_instance, add)
        
        if file and hasattr(file, '_file'):
            # Get the original file name for processing
            original_name = getattr(file, 'name', 'menu_item')
            
            try:
                # Validate the image
                is_valid, error_message = validate_image(file._file)
                if not is_valid:
                    raise ValidationError(error_message)
                
                # Optimize the main image
                optimized_image = optimize_image(
                    file._file,
                    max_size=(800, 600),
                    quality=85,
                    format='JPEG'
                )
                
                # Replace the file content with optimized version
                file._file = optimized_image
                
                # Update the name to have .jpg extension
                base_name = os.path.splitext(original_name)[0]
                file.name = f"{base_name}.jpg"
                
            except Exception as e:
                logger.error(f"Error processing menu image: {e}")
                raise ValidationError(f"Error processing image: {e}")
        
        return file


class MenuImageFormField(forms.ImageField):
    """
    Custom form field for menu item image uploads with enhanced validation.
    """
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', 
            'Upload a high-quality image of your menu item. '
            'Supported formats: JPEG, PNG, WebP. Maximum size: 5MB. '
            'Images will be automatically optimized for web display.'
        )
        
        super().__init__(*args, **kwargs)
    
    def clean(self, data, initial=None):
        """
        Validate uploaded image.
        """
        file = super().clean(data, initial)
        
        if file:
            # Validate the image using our custom validation
            is_valid, error_message = validate_image(file)
            if not is_valid:
                raise ValidationError(error_message)
        
        return file
    
    def widget_attrs(self, widget):
        """
        Add HTML attributes to the widget.
        """
        attrs = super().widget_attrs(widget)
        attrs.update({
            'accept': 'image/jpeg,image/png,image/webp',
            'capture': 'camera',  # Allow camera capture on mobile
        })
        return attrs


class MenuImageWidget(forms.ClearableFileInput):
    """
    Custom widget for menu image uploads with preview functionality.
    """
    
    template_name = 'django/forms/widgets/file.html'
    
    def __init__(self, attrs=None):
        default_attrs = {
            'accept': 'image/jpeg,image/png,image/webp',
            'class': 'form-control menu-image-input'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def format_value(self, value):
        """
        Format the value for display.
        """
        if value and hasattr(value, 'url'):
            try:
                return value.url if value else None
            except (ValueError, AttributeError):
                # No file associated with this field
                return None
        return None
    
    class Media:
        css = {}
        js = ()


def validate_image_file_extension(value):
    """
    Validator function for image file extensions.
    """
    import os
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    
    if not ext:
        raise ValidationError('File must have an extension.')
    
    if ext not in valid_extensions:
        raise ValidationError(
            f'Unsupported file extension "{ext}". '
            f'Allowed extensions are: {", ".join(valid_extensions)}'
        )


def validate_image_file_size(value):
    """
    Validator function for image file size.
    """
    max_size = 5 * 1024 * 1024  # 5MB
    
    if value.size > max_size:
        raise ValidationError(
            f'File size too large. Maximum allowed size is {max_size // (1024*1024)}MB. '
            f'Your file is {value.size // (1024*1024)}MB.'
        )