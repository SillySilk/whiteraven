"""
Template tags and filters for menu item image handling.
"""

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.templatetags.static import static

register = template.Library()


@register.filter
def image_url(menu_item, size='card'):
    """
    Get optimized image URL for a menu item.
    
    Usage: {{ menu_item|image_url:"thumbnail" }}
    
    Args:
        menu_item: MenuItem instance
        size: str, image size ('thumbnail', 'card', 'detail', 'original')
        
    Returns:
        str: Image URL or placeholder icon URL
    """
    if not menu_item:
        return ''
    
    # Try to get the optimized image URL
    display_url = menu_item.get_display_image_url(size)
    
    if display_url:
        return display_url
    
    # Return placeholder icon if no image
    return static('menu/images/placeholder.svg')


@register.filter
def responsive_image_urls(menu_item):
    """
    Get all available image URLs for responsive display.
    
    Usage: {{ menu_item|responsive_image_urls }}
    
    Returns:
        dict: Dictionary with all available image URLs
    """
    if not menu_item:
        return {}
    
    return menu_item.get_image_urls()


@register.simple_tag
def menu_image(menu_item, size='card', css_class='', alt_text='', lazy_load=True):
    """
    Render an optimized image tag for a menu item.
    
    Usage: {% menu_image menu_item "thumbnail" "img-fluid rounded" "Delicious coffee" %}
    
    Args:
        menu_item: MenuItem instance
        size: str, image size preference
        css_class: str, CSS classes to add
        alt_text: str, alternative text (defaults to menu item name)
        lazy_load: bool, whether to add lazy loading
        
    Returns:
        str: HTML img tag
    """
    if not menu_item:
        return ''
    
    # Get image URL
    img_url = menu_item.get_display_image_url(size)
    has_real_image = menu_item.has_image()
    
    # Default alt text
    if not alt_text:
        alt_text = f"Image of {menu_item.name}"
    
    # Build CSS classes
    classes = ['menu-item-image']
    if css_class:
        classes.append(css_class)
    if not has_real_image:
        classes.append('placeholder-image')
    
    # Handle missing image
    if not img_url:
        return format_html(
            '<div class="menu-image-placeholder {}" title="{}">',
            ' '.join(classes),
            alt_text
        ) + format_html(
            '<i class="bi bi-image fs-2 text-muted"></i>'
            '<span class="sr-only">{}</span>'
            '</div>',
            alt_text
        )
    
    # Build img tag attributes
    img_attrs = {
        'src': img_url,
        'alt': alt_text,
        'class': ' '.join(classes),
    }
    
    if lazy_load:
        img_attrs['loading'] = 'lazy'
    
    # Add responsive image sources if available
    image_urls = menu_item.get_image_urls()
    
    if len(image_urls) > 1:
        # Create srcset for responsive images
        srcset_parts = []
        
        # Define size mappings for srcset
        size_mappings = {
            'thumbnail': '150w',
            'card': '400w', 
            'detail': '800w',
        }
        
        for img_size, url in image_urls.items():
            if img_size in size_mappings and img_size != 'original':
                srcset_parts.append(f"{url} {size_mappings[img_size]}")
        
        if srcset_parts:
            img_attrs['srcset'] = ', '.join(srcset_parts)
            
            # Add sizes attribute for responsive behavior
            if size == 'thumbnail':
                img_attrs['sizes'] = '(max-width: 768px) 150px, 150px'
            elif size == 'card':
                img_attrs['sizes'] = '(max-width: 768px) 100vw, (max-width: 1200px) 400px, 400px'
            else:
                img_attrs['sizes'] = '(max-width: 768px) 100vw, 800px'
    
    # Build the img tag
    attrs_str = ' '.join([f'{k}="{v}"' for k, v in img_attrs.items()])
    return mark_safe(f'<img {attrs_str}>')


@register.simple_tag
def picture_element(menu_item, sizes=None, css_class='', alt_text='', lazy_load=True):
    """
    Render a picture element with multiple sources for optimal performance.
    
    Usage: {% picture_element menu_item "thumbnail,card" "img-fluid" "Coffee image" %}
    
    Args:
        menu_item: MenuItem instance
        sizes: str, comma-separated list of sizes to include
        css_class: str, CSS classes to add
        alt_text: str, alternative text
        lazy_load: bool, whether to add lazy loading
        
    Returns:
        str: HTML picture element
    """
    if not menu_item:
        return ''
    
    # Parse sizes
    if sizes:
        size_list = [s.strip() for s in sizes.split(',')]
    else:
        size_list = ['thumbnail', 'card', 'detail']
    
    # Get all available image URLs
    image_urls = menu_item.get_image_urls()
    
    if not image_urls:
        # Return placeholder
        return format_html(
            '<div class="menu-image-placeholder {}" title="{}">',
            css_class,
            alt_text or f"Image of {menu_item.name}"
        ) + format_html(
            '<i class="bi bi-image fs-2 text-muted"></i>'
            '</div>'
        )
    
    # Build picture element
    sources = []
    
    # WebP sources (if we add WebP support in the future)
    # for size in reversed(size_list):
    #     if f"{size}_webp" in image_urls:
    #         sources.append(f'<source srcset="{image_urls[f"{size}_webp"]}" type="image/webp">')
    
    # JPEG sources
    for size in reversed(size_list):
        if size in image_urls:
            media_query = ''
            if size == 'thumbnail':
                media_query = ' media="(max-width: 576px)"'
            elif size == 'card':
                media_query = ' media="(max-width: 992px)"'
            
            sources.append(f'<source srcset="{image_urls[size]}"{media_query}>')
    
    # Fallback img
    fallback_url = image_urls.get('card') or image_urls.get('detail') or next(iter(image_urls.values()))
    
    img_attrs = {
        'src': fallback_url,
        'alt': alt_text or f"Image of {menu_item.name}",
        'class': f"menu-item-image {css_class}".strip(),
    }
    
    if lazy_load:
        img_attrs['loading'] = 'lazy'
    
    img_attrs_str = ' '.join([f'{k}="{v}"' for k, v in img_attrs.items()])
    
    picture_html = f'<picture>{"".join(sources)}<img {img_attrs_str}></picture>'
    
    return mark_safe(picture_html)


@register.inclusion_tag('menu/tags/image_gallery.html')
def menu_image_gallery(menu_item, show_thumbnails=True):
    """
    Render an image gallery for a menu item (if multiple sizes available).
    
    Usage: {% menu_image_gallery menu_item %}
    """
    image_urls = menu_item.get_image_urls() if menu_item else {}
    
    return {
        'menu_item': menu_item,
        'image_urls': image_urls,
        'show_thumbnails': show_thumbnails,
        'has_images': bool(image_urls),
    }


@register.filter
def has_optimized_images(menu_item):
    """
    Check if a menu item has optimized images (multiple sizes).
    
    Usage: {% if menu_item|has_optimized_images %}
    """
    if not menu_item:
        return False
    
    image_urls = menu_item.get_image_urls()
    return len(image_urls) > 1


@register.filter  
def image_file_size(menu_item):
    """
    Get the file size of the menu item's image.
    
    Usage: {{ menu_item|image_file_size }}
    """
    if not menu_item or not menu_item.image:
        return 0
    
    try:
        return menu_item.image.size
    except (OSError, ValueError):
        return 0


@register.filter
def format_file_size(bytes_size):
    """
    Format file size in human-readable format.
    
    Usage: {{ file_size|format_file_size }}
    """
    if not bytes_size:
        return '0 B'
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    
    return f"{bytes_size:.1f} TB"


@register.simple_tag
def image_placeholder_url(size='card'):
    """
    Get URL for a placeholder image.
    
    Usage: {% image_placeholder_url "thumbnail" %}
    """
    return static(f'menu/images/placeholder-{size}.svg')


@register.simple_tag  
def lazy_image(menu_item, size='card', css_class='', alt_text=''):
    """
    Render a lazy-loaded image with loading spinner.
    
    Usage: {% lazy_image menu_item "card" "img-fluid" %}
    """
    img_url = menu_item.get_display_image_url(size) if menu_item else None
    
    if not img_url:
        return mark_safe(f'<div class="image-placeholder {css_class}"><i class="bi bi-image"></i></div>')
    
    return format_html(
        '<div class="lazy-image-container {}">'
        '<img data-src="{}" alt="{}" class="lazy-image {}" loading="lazy">'
        '<div class="loading-spinner"><div class="spinner-border" role="status"></div></div>'
        '</div>',
        css_class,
        img_url,
        alt_text or f"Image of {menu_item.name}",
        css_class
    )