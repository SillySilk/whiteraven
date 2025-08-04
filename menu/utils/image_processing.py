"""
Image processing utilities for menu item photos.

This module provides functions for:
- Automatic image resizing and optimization
- Image validation
- Placeholder image generation
- Web-optimized image format conversion
"""

import os
import io
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Image processing settings
MENU_IMAGE_SIZES = {
    'thumbnail': (150, 150),
    'card': (400, 300),
    'detail': (800, 600),
}

PLACEHOLDER_COLORS = [
    '#E3F2FD',  # Light Blue
    '#F3E5F5',  # Light Purple
    '#E8F5E8',  # Light Green
    '#FFF3E0',  # Light Orange
    '#FCE4EC',  # Light Pink
    '#F1F8E9',  # Light Lime
]

ALLOWED_FORMATS = ['JPEG', 'PNG', 'WEBP']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
QUALITY_SETTINGS = {
    'JPEG': 85,
    'WEBP': 85,
    'PNG': None,  # PNG uses lossless compression
}


def validate_image(image_file):
    """
    Enhanced validation for uploaded image files with security checks.
    
    Args:
        image_file: Django UploadedFile object or file-like object
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        from django.conf import settings
        import os
        
        # Check file size against settings
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', MAX_FILE_SIZE)
        if hasattr(image_file, 'size') and image_file.size > max_size:
            return False, f"Image file too large. Maximum size is {max_size // (1024*1024)}MB."
        
        # Check file extension against blocked list
        if hasattr(image_file, 'name'):
            ext = os.path.splitext(image_file.name.lower())[1]
            blocked_extensions = getattr(settings, 'BLOCKED_EXTENSIONS', [])
            if ext in blocked_extensions:
                return False, f"File type {ext} is not allowed for security reasons."
            
            # Check against allowed image extensions
            allowed_extensions = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', ALLOWED_FORMATS)
            if ext and ext not in [f'.{fmt.lower()}' for fmt in allowed_extensions]:
                return False, f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}"
        
        # Check MIME type against allowed types
        if hasattr(image_file, 'content_type'):
            allowed_mime_types = getattr(settings, 'ALLOWED_MIME_TYPES', [])
            if allowed_mime_types and image_file.content_type not in allowed_mime_types:
                return False, f"Unsupported MIME type: {image_file.content_type}"
        
        # Validate image file integrity
        try:
            with Image.open(image_file) as img:
                # Verify the image can be opened
                img.verify()
                
                # Reset and re-open for additional checks
                image_file.seek(0)
                
                with Image.open(image_file) as img2:
                    # Check image format
                    if img2.format not in ALLOWED_FORMATS:
                        return False, f"Unsupported image format. Allowed formats: {', '.join(ALLOWED_FORMATS)}"
                    
                    # Check image dimensions (prevent zip bombs)
                    width, height = img2.size
                    max_dimension = 4096  # Reasonable maximum
                    if width > max_dimension or height > max_dimension:
                        return False, f"Image dimensions too large. Maximum: {max_dimension}x{max_dimension} pixels."
                    
                    # Check for potential issues with image mode
                    if img2.mode not in ('RGB', 'RGBA', 'L', 'P'):
                        return False, f"Unsupported image mode: {img2.mode}"
                    
                    # Additional security: check for embedded data/metadata that could be malicious
                    # This is a basic check - more sophisticated tools would be needed for thorough scanning
                    if hasattr(img2, 'info') and img2.info:
                        # Check for suspicious metadata
                        suspicious_keys = ['Software', 'Comment', 'XMP', 'ICC_PROFILE']
                        for key in suspicious_keys:
                            if key in img2.info:
                                value = str(img2.info[key])
                                if any(pattern in value.lower() for pattern in ['script', 'javascript', 'eval', 'exec']):
                                    logger.warning(f"Suspicious metadata found in image: {key}={value}")
                                    return False, "Image contains potentially malicious metadata."
        
        except Exception as e:
            logger.error(f"Image validation error: {e}")
            return False, "Invalid or corrupted image file."
        
        # Reset file pointer for further processing
        image_file.seek(0)
        
        return True, None
        
    except Exception as e:
        logger.error(f"Error during image validation: {e}")
        return False, "Error validating image file."


def optimize_image(image_file, max_size=(800, 600), quality=85, format='JPEG'):
    """
    Optimize and resize image for web delivery.
    
    Args:
        image_file: Django UploadedFile or file-like object
        max_size: tuple of (width, height) for maximum dimensions
        quality: int, compression quality (1-100)
        format: str, output format ('JPEG', 'PNG', 'WEBP')
        
    Returns:
        ContentFile: Optimized image as Django ContentFile
    """
    try:
        with Image.open(image_file) as img:
            # Convert to RGB if necessary (for JPEG output)
            if format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif format in ('PNG', 'WEBP') and img.mode not in ('RGBA', 'RGB'):
                img = img.convert('RGBA')
            
            # Calculate new size maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Create output buffer
            output_buffer = io.BytesIO()
            
            # Save with appropriate settings
            save_kwargs = {'format': format}
            if format in QUALITY_SETTINGS and QUALITY_SETTINGS[format] is not None:
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            
            img.save(output_buffer, **save_kwargs)
            output_buffer.seek(0)
            
            return ContentFile(output_buffer.getvalue())
            
    except Exception as e:
        logger.error(f"Error optimizing image: {e}")
        raise


def create_multiple_sizes(image_file, base_name):
    """
    Create multiple optimized sizes of an image.
    
    Args:
        image_file: Django UploadedFile or file-like object
        base_name: str, base filename without extension
        
    Returns:
        dict: Dictionary with size names as keys and file paths as values
    """
    results = {}
    
    try:
        for size_name, dimensions in MENU_IMAGE_SIZES.items():
            # Optimize image for this size
            optimized_image = optimize_image(
                image_file, 
                max_size=dimensions,
                quality=QUALITY_SETTINGS['JPEG'],
                format='JPEG'
            )
            
            # Generate filename
            filename = f"{base_name}_{size_name}.jpg"
            
            # Save the optimized image
            saved_path = default_storage.save(f"menu/{filename}", optimized_image)
            results[size_name] = saved_path
            
            # Reset file pointer for next iteration
            image_file.seek(0)
            
    except Exception as e:
        logger.error(f"Error creating multiple image sizes: {e}")
        # Clean up any successfully created files
        for path in results.values():
            try:
                default_storage.delete(path)
            except:
                pass
        raise
    
    return results


def generate_placeholder_image(text, size=(400, 300), color_index=0):
    """
    Generate a placeholder image with text.
    
    Args:
        text: str, text to display on placeholder
        size: tuple, (width, height) of image
        color_index: int, index for background color selection
        
    Returns:
        ContentFile: Generated placeholder image
    """
    try:
        # Select background color
        bg_color = PLACEHOLDER_COLORS[color_index % len(PLACEHOLDER_COLORS)]
        text_color = '#666666'
        
        # Create image
        img = Image.new('RGB', size, bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fall back to default
        try:
            # Try to find a font file (this might not exist on all systems)
            font_size = min(size) // 8
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            # Fall back to default font
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        if font:
            # Get text dimensions
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position to center text
            x = (size[0] - text_width) // 2
            y = (size[1] - text_height) // 2
            
            # Draw text
            draw.text((x, y), text, fill=text_color, font=font)
        
        # Add decorative elements
        # Draw a subtle border
        border_color = '#DDDDDD'
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=border_color, width=2)
        
        # Add a coffee cup icon (simple representation)
        icon_size = min(size) // 6
        icon_x = size[0] // 2 - icon_size // 2
        icon_y = size[1] // 4
        
        # Simple coffee cup shape
        cup_color = '#8D6E63'
        draw.ellipse([
            icon_x, icon_y + icon_size // 3,
            icon_x + icon_size, icon_y + icon_size
        ], fill=cup_color)
        
        # Cup handle
        handle_size = icon_size // 4
        draw.arc([
            icon_x + icon_size - handle_size//2, 
            icon_y + icon_size // 2,
            icon_x + icon_size + handle_size, 
            icon_y + icon_size - handle_size//2
        ], start=270, end=90, fill=cup_color, width=3)
        
        # Save to buffer
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='JPEG', quality=90)
        output_buffer.seek(0)
        
        return ContentFile(output_buffer.getvalue())
        
    except Exception as e:
        logger.error(f"Error generating placeholder image: {e}")
        # Return a very simple fallback
        img = Image.new('RGB', size, '#F5F5F5')
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='JPEG', quality=90)
        output_buffer.seek(0)
        return ContentFile(output_buffer.getvalue())


def get_image_upload_path(instance, filename):
    """
    Generate upload path for menu item images.
    
    Args:
        instance: MenuItem model instance
        filename: Original filename
        
    Returns:
        str: Upload path
    """
    # Get file extension
    ext = os.path.splitext(filename)[1].lower()
    
    # Generate new filename based on menu item
    if instance.slug:
        base_name = instance.slug
    else:
        # Fallback to cleaned name
        import re
        base_name = re.sub(r'[^\w\-]', '', instance.name.lower().replace(' ', '-'))
    
    return f"menu/{base_name}{ext}"


def cleanup_old_images(old_image_path):
    """
    Clean up old image files when a new image is uploaded.
    
    Args:
        old_image_path: str, path to the old image file
    """
    if old_image_path:
        try:
            # Delete the main image
            if default_storage.exists(old_image_path):
                default_storage.delete(old_image_path)
            
            # Try to delete associated sized images
            base_path = os.path.splitext(old_image_path)[0]
            for size_name in MENU_IMAGE_SIZES.keys():
                sized_path = f"{base_path}_{size_name}.jpg"
                if default_storage.exists(sized_path):
                    default_storage.delete(sized_path)
                    
        except Exception as e:
            logger.warning(f"Could not clean up old image files: {e}")


def get_responsive_image_urls(image_field):
    """
    Get URLs for different sizes of an image for responsive display.
    
    Args:
        image_field: Django ImageField
        
    Returns:
        dict: Dictionary with size names as keys and URLs as values
    """
    if not image_field:
        return {}
    
    urls = {'original': image_field.url}
    
    # Check if sized versions exist
    base_path = os.path.splitext(image_field.name)[0]
    for size_name in MENU_IMAGE_SIZES.keys():
        sized_path = f"{base_path}_{size_name}.jpg"
        if default_storage.exists(sized_path):
            urls[size_name] = default_storage.url(sized_path)
    
    return urls


def ensure_placeholder_exists(menu_item):
    """
    Ensure a menu item has a placeholder image if no real image exists.
    
    Args:
        menu_item: MenuItem model instance
        
    Returns:
        bool: True if placeholder was created/exists, False otherwise
    """
    if menu_item.image:
        return True
        
    try:
        # Generate placeholder
        placeholder_text = menu_item.name[:20] + ('...' if len(menu_item.name) > 20 else '')
        
        # Use category order as color index for variety
        color_index = menu_item.category.order if menu_item.category else 0
        
        placeholder_image = generate_placeholder_image(
            text=placeholder_text,
            size=MENU_IMAGE_SIZES['card'],
            color_index=color_index
        )
        
        # Save placeholder
        filename = f"placeholder_{menu_item.slug or menu_item.id}.jpg"
        placeholder_path = default_storage.save(f"menu/placeholders/{filename}", placeholder_image)
        
        # Update menu item (note: this should be done carefully to avoid recursion)
        menu_item.image.name = placeholder_path
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating placeholder for menu item {menu_item.id}: {e}")
        return False