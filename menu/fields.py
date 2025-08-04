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
        Smart image processing with auto-conversion and resizing.
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
                
                # Smart optimization based on image characteristics
                optimized_image = self._smart_optimize_image(file._file, original_name)
                
                # Replace the file content with optimized version
                file._file = optimized_image
                
                # Always use JPG for maximum compatibility and simplicity
                base_name = os.path.splitext(original_name)[0]
                file.name = f"{base_name}.jpg"
                
            except Exception as e:
                logger.error(f"Error processing menu image: {e}")
                raise ValidationError(f"Error processing image: {e}")
        
        return file
    
    def _smart_optimize_image(self, image_file, original_name):
        """
        Smart image optimization with format conversion and intelligent resizing.
        """
        from PIL import Image, ExifTags
        import io
        from django.core.files.base import ContentFile
        
        # Open and analyze the image
        with Image.open(image_file) as img:
            # Auto-rotate based on EXIF data (common issue with phone photos)
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif is not None and orientation in exif:
                        if exif[orientation] == 3:
                            img = img.rotate(180, expand=True)
                        elif exif[orientation] == 6:
                            img = img.rotate(270, expand=True)
                        elif exif[orientation] == 8:
                            img = img.rotate(90, expand=True)
            except (AttributeError, KeyError, TypeError):
                pass  # No EXIF data or orientation info
            
            # Get original dimensions and file size estimate
            original_width, original_height = img.size
            original_mode = img.mode
            
            # Smart resizing logic based on image characteristics
            max_width, max_height, quality = self._determine_optimal_size_and_quality(
                original_width, original_height, original_name, image_file
            )
            
            # Resize if needed (maintain aspect ratio)
            if original_width > max_width or original_height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convert to RGB for JPG (no transparency support, but simpler)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as JPG with optimal settings
            output = io.BytesIO()
            
            # JPG settings for maximum compatibility and efficiency
            jpg_options = {
                'format': 'JPEG',
                'quality': quality,
                'optimize': True,
                'progressive': True,  # Progressive loading
            }
            
            img.save(output, **jpg_options)
            output.seek(0)
            
            return ContentFile(output.getvalue())
    
    def _determine_optimal_size_and_quality(self, width, height, filename, file_obj):
        """
        Determine optimal size and quality based on image source and characteristics.
        """
        # Estimate if this is likely a phone photo (very large dimensions)
        is_likely_phone_photo = width > 2000 or height > 2000
        
        # Estimate if this is likely an AI-generated image (specific aspect ratios, moderate size)
        is_likely_ai_image = (
            (width == height) or  # Square (common AI output)
            (abs(width/height - 16/9) < 0.1) or  # 16:9 aspect ratio
            (abs(width/height - 4/3) < 0.1)   # 4:3 aspect ratio
        ) and width >= 512
        
        # Get file size estimate
        file_size = getattr(file_obj, 'size', 0) if hasattr(file_obj, 'size') else 0
        is_large_file = file_size > 1024 * 1024  # > 1MB
        
        # Smart sizing decisions
        if is_likely_phone_photo or is_large_file:
            # Aggressive resizing for phone photos and large files
            max_width = 800
            max_height = 600
            quality = 80  # Good quality, smaller file
            
        elif is_likely_ai_image:
            # Moderate resizing for AI images, maintain quality
            max_width = 1000
            max_height = 800
            quality = 85  # Higher quality for AI-generated content
            
        elif width <= 800 and height <= 600:
            # Small images - minimal processing
            max_width = width
            max_height = height
            quality = 90  # High quality for already small images
            
        else:
            # Default case - moderate optimization
            max_width = 1000
            max_height = 800
            quality = 85
        
        return max_width, max_height, quality


class MenuImageFormField(forms.ImageField):
    """
    Custom form field for menu item image uploads with JPG conversion.
    """
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', 
            'Upload an image of your menu item. All images will be automatically '
            'converted to optimized JPG format for fast loading. '
            'File picker shows JPG files only, but PNG/WebP are also accepted and will be converted. Maximum size: 5MB.'
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
            'accept': 'image/jpeg,image/jpg',  # Only JPG files in file picker
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
            'accept': 'image/jpeg,image/jpg',  # Only JPG files in file picker
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