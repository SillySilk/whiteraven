from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime
import json
import os

from .models import BusinessInfo, ContactSubmission, SiteTheme
from .forms import ContactForm
from .email_utils import EmailService
from menu.models import MenuItem


def home(request):
    """
    Homepage view displaying business info, featured menu items, and welcome content
    """
    try:
        business_info = BusinessInfo.objects.first()
    except BusinessInfo.DoesNotExist:
        business_info = None
    
    # Get featured menu items for homepage display
    featured_items = MenuItem.objects.filter(
        featured=True, 
        available=True
    ).select_related('category')[:6]  # Limit to 6 featured items
    
    # Get current business status using enhanced method
    is_open = False
    current_status = "Hours not available"
    status_details = {}
    
    if business_info:
        status_details = business_info.get_current_status()
        is_open = status_details.get('is_open', False)
        current_status = status_details.get('status', 'Hours not available')
    
    context = {
        'business_info': business_info,
        'featured_items': featured_items,
        'is_open': is_open,
        'current_status': current_status,
        'status_details': status_details,
        'page_title': 'Home',
    }
    
    return render(request, 'core/home.html', context)


def location(request):
    """
    Location page view displaying address, hours, and map information
    """
    try:
        business_info = BusinessInfo.objects.first()
    except BusinessInfo.DoesNotExist:
        business_info = None
    
    # Format hours for display using enhanced method
    formatted_hours = {}
    current_status_info = {}
    
    if business_info:
        formatted_hours = business_info.get_formatted_hours()
        current_status_info = business_info.get_current_status()
    
    context = {
        'business_info': business_info,
        'formatted_hours': formatted_hours,
        'current_status_info': current_status_info,
        'page_title': 'Location & Hours',
    }
    
    return render(request, 'core/location.html', context)


def contact(request):
    """
    Enhanced contact page view with comprehensive form submission handling
    """
    try:
        business_info = BusinessInfo.objects.first()
    except BusinessInfo.DoesNotExist:
        business_info = None
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Save the contact submission
                contact_submission = form.save()
                
                # Log the successful submission
                import logging
                logger = logging.getLogger('core.views')
                logger.info(f"Contact form submitted by {contact_submission.name} ({contact_submission.email})")
                
                # Send email notifications using the EmailService
                email_results = {
                    'notification_sent': False,
                    'auto_reply_sent': False,
                    'errors': []
                }
                
                try:
                    # Send notification to business owner
                    email_results['notification_sent'] = EmailService.send_contact_notification(
                        contact_submission, business_info
                    )
                    
                    if email_results['notification_sent']:
                        logger.info(f"Contact notification sent for submission {contact_submission.id}")
                    else:
                        logger.warning(f"Failed to send contact notification for submission {contact_submission.id}")
                        email_results['errors'].append("Failed to send notification to business owner")
                    
                except Exception as e:
                    logger.error(f"Error sending contact notification: {str(e)}")
                    email_results['errors'].append(f"Notification error: {str(e)}")
                
                try:
                    # Send auto-reply to customer
                    email_results['auto_reply_sent'] = EmailService.send_contact_auto_reply(
                        contact_submission, business_info
                    )
                    
                    if email_results['auto_reply_sent']:
                        logger.info(f"Auto-reply sent for submission {contact_submission.id}")
                    else:
                        logger.warning(f"Failed to send auto-reply for submission {contact_submission.id}")
                        email_results['errors'].append("Failed to send confirmation email to customer")
                    
                except Exception as e:
                    logger.error(f"Error sending auto-reply: {str(e)}")
                    email_results['errors'].append(f"Auto-reply error: {str(e)}")
                
                # Determine success message based on email results
                if email_results['notification_sent'] and email_results['auto_reply_sent']:
                    success_message = (
                        f"Thank you for your message, {contact_submission.name}! "
                        "We've received your inquiry and sent you a confirmation email. "
                        "We'll get back to you as soon as possible."
                    )
                elif email_results['notification_sent']:
                    success_message = (
                        f"Thank you for your message, {contact_submission.name}! "
                        "We've received your inquiry and will get back to you as soon as possible."
                    )
                else:
                    success_message = (
                        f"Thank you for your message, {contact_submission.name}! "
                        "We've received your inquiry. If you don't hear back within 24 hours, "
                        "please call us directly."
                    )
                
                # Show success message and redirect
                messages.success(request, success_message)
                
                # Log any email errors for admin review
                if email_results['errors']:
                    logger.error(f"Email errors for submission {contact_submission.id}: {'; '.join(email_results['errors'])}")
                    
                    # Send admin notification about email failures (if possible)
                    try:
                        EmailService.send_admin_notification(
                            subject="Contact Form Email Delivery Issues",
                            message=f"Contact submission {contact_submission.id} from {contact_submission.name} "
                                   f"had email delivery issues: {'; '.join(email_results['errors'])}",
                            level='warning'
                        )
                    except:
                        pass  # Don't fail if admin notification also fails
                
                return redirect('core:contact')
                
            except Exception as e:
                # Handle database or other submission errors
                logger.error(f"Error saving contact submission: {str(e)}")
                messages.error(
                    request, 
                    "We're sorry, but there was an error processing your message. "
                    "Please try again or contact us directly."
                )
        else:
            # Form has validation errors
            messages.error(
                request,
                "Please correct the errors below and try again."
            )
    else:
        form = ContactForm()
    
    context = {
        'business_info': business_info,
        'form': form,
        'page_title': 'Contact Us',
    }
    
    return render(request, 'core/contact.html', context)


def about(request):
    """
    About page view displaying business story and information
    """
    try:
        business_info = BusinessInfo.objects.first()
    except BusinessInfo.DoesNotExist:
        business_info = None
    
    context = {
        'business_info': business_info,
        'page_title': 'About Us',
    }
    
    return render(request, 'core/about.html', context)


def current_status_api(request):
    """
    API endpoint to get current business status as JSON.
    Used by admin interface and potentially for AJAX updates.
    """
    try:
        business_info = BusinessInfo.objects.first()
        if business_info:
            status_info = business_info.get_current_status()
            return JsonResponse(status_info)
        else:
            return JsonResponse({
                'is_open': False,
                'status': 'Business information not configured',
                'reason': 'No business info found',
                'next_change': None,
                'is_special': False
            })
    except Exception as e:
        return JsonResponse({
            'is_open': False,
            'status': 'Status unavailable',
            'reason': 'Error retrieving status',
            'next_change': None,
            'is_special': False,
            'error': str(e)
        })


def _validate_jpeg_file(uploaded_file):
    """
    Validate that uploaded file is a JPEG image.
    """
    import os
    
    # Check file extension
    if hasattr(uploaded_file, 'name'):
        ext = os.path.splitext(uploaded_file.name.lower())[1]
        if ext not in ['.jpg', '.jpeg']:
            return False
    
    # Check file size (5MB max)
    if hasattr(uploaded_file, 'size') and uploaded_file.size > 5 * 1024 * 1024:
        return False
    
    return True


@staff_member_required
def site_images_manager(request):
    """
    Site Images management page for admin users.
    Allows easy management of all design images (hero, menu decoration, etc.)
    """
    # Get current business info and site theme
    try:
        business_info = BusinessInfo.objects.first()
    except BusinessInfo.DoesNotExist:
        business_info = None
    
    try:
        site_theme = SiteTheme.get_active_theme()
    except Exception:
        site_theme = None
    
    if request.method == 'POST':
        # Handle image uploads
        success_messages = []
        error_messages = []
        
        # Handle hero image upload
        if 'hero_image' in request.FILES:
            uploaded_file = request.FILES['hero_image']
            if business_info:
                old_image = business_info.hero_image
                business_info.hero_image = uploaded_file
                business_info.save()
                success_messages.append("Hero image updated successfully!")
                
                # Delete old image file if it exists
                if old_image:
                    try:
                        old_image.delete(save=False)
                    except:
                        pass
            else:
                error_messages.append("Business information not found. Please set up business info first.")
        
        # Handle menu decoration image upload
        if 'menu_decoration_image' in request.FILES:
            uploaded_file = request.FILES['menu_decoration_image']
            if site_theme:
                old_image = site_theme.menu_decoration_image
                site_theme.menu_decoration_image = uploaded_file
                
                # Update alt text if provided
                alt_text = request.POST.get('menu_decoration_alt_text', '').strip()
                if alt_text:
                    site_theme.menu_decoration_alt_text = alt_text
                
                site_theme.save()
                success_messages.append("Menu decoration image updated successfully!")
                
                # Delete old image file if it exists
                if old_image:
                    try:
                        old_image.delete(save=False)
                    except:
                        pass
            else:
                error_messages.append("Site theme not found. Please set up site theme first.")
        
        # Handle about image upload
        if 'about_image' in request.FILES:
            uploaded_file = request.FILES['about_image']
            if business_info:
                old_image = business_info.about_image
                business_info.about_image = uploaded_file
                business_info.save()
                success_messages.append("About page image updated successfully!")
                
                # Delete old image file if it exists
                if old_image:
                    try:
                        old_image.delete(save=False)
                    except:
                        pass
            else:
                error_messages.append("Business information not found. Please set up business info first.")
        
        # Handle location image upload
        if 'location_image' in request.FILES:
            uploaded_file = request.FILES['location_image']
            if business_info:
                old_image = business_info.location_image
                business_info.location_image = uploaded_file
                business_info.save()
                success_messages.append("Location page image updated successfully!")
                
                # Delete old image file if it exists
                if old_image:
                    try:
                        old_image.delete(save=False)
                    except:
                        pass
            else:
                error_messages.append("Business information not found. Please set up business info first.")
        
        # Handle image deletions
        if request.POST.get('delete_hero_image') == 'true':
            if business_info and business_info.hero_image:
                business_info.hero_image.delete(save=False)
                business_info.hero_image = None
                business_info.save()
                success_messages.append("Hero image removed successfully!")
        
        if request.POST.get('delete_menu_decoration') == 'true':
            if site_theme and site_theme.menu_decoration_image:
                site_theme.menu_decoration_image.delete(save=False)
                site_theme.menu_decoration_image = None
                site_theme.save()
                success_messages.append("Menu decoration image removed successfully!")
        
        if request.POST.get('delete_about_image') == 'true':
            if business_info and business_info.about_image:
                business_info.about_image.delete(save=False)
                business_info.about_image = None
                business_info.save()
                success_messages.append("About page image removed successfully!")
        
        if request.POST.get('delete_location_image') == 'true':
            if business_info and business_info.location_image:
                business_info.location_image.delete(save=False)
                business_info.location_image = None
                business_info.save()
                success_messages.append("Location page image removed successfully!")
        
        # Show messages
        for msg in success_messages:
            messages.success(request, msg)
        for msg in error_messages:
            messages.error(request, msg)
        
        # Redirect to prevent resubmission
        return redirect('core:site_images')
    
    # Collect all site images information
    site_images = []
    
    # Hero Image
    hero_info = {
        'name': 'Hero Image',
        'description': 'Main banner image displayed on the homepage',
        'field_name': 'hero_image',
        'current_image': business_info.hero_image if business_info else None,
        'upload_path': '',
        'recommended_size': '1200x600px',
        'usage': 'Homepage banner, first thing visitors see',
        'delete_field': 'delete_hero_image'
    }
    site_images.append(hero_info)
    
    # Menu Decoration Image
    menu_decoration_info = {
        'name': 'Menu Decoration Image',
        'description': 'Decorative image shown on the menu page',
        'field_name': 'menu_decoration_image',
        'current_image': site_theme.menu_decoration_image if site_theme else None,
        'upload_path': '',
        'recommended_size': '400x300px',
        'usage': 'Menu page decoration, replaces the white stats box',
        'delete_field': 'delete_menu_decoration',
        'alt_text': site_theme.menu_decoration_alt_text if site_theme else '',
        'alt_text_field': 'menu_decoration_alt_text'
    }
    site_images.append(menu_decoration_info)
    
    # About Image
    about_info = {
        'name': 'About Page Image',
        'description': 'Story image displayed on the About page',
        'field_name': 'about_image',
        'current_image': business_info.about_image if business_info else None,
        'upload_path': '',
        'recommended_size': '600x400px',
        'usage': 'About page story section, shows coffee shop atmosphere',
        'delete_field': 'delete_about_image'
    }
    site_images.append(about_info)
    
    # Location Image
    location_info = {
        'name': 'Location Page Image',
        'description': 'Header image displayed on the Location page',
        'field_name': 'location_image',
        'current_image': business_info.location_image if business_info else None,
        'upload_path': '',
        'recommended_size': '600x400px',
        'usage': 'Location page header, showcases the coffee shop exterior or interior',
        'delete_field': 'delete_location_image'
    }
    site_images.append(location_info)
    
    context = {
        'site_images': site_images,
        'business_info': business_info,
        'site_theme': site_theme,
        'page_title': 'Site Images Manager',
    }
    
    return render(request, 'core/site_images_manager.html', context)


@staff_member_required
def debug_database(request):
    """
    Debug view to check what's actually in the remote database
    """
    try:
        business_info = BusinessInfo.objects.first()
    except:
        business_info = None
    
    try:
        site_theme = SiteTheme.get_active_theme()
    except:
        site_theme = None
    
    menu_items = MenuItem.objects.exclude(image='')
    
    context = {
        'business_info': business_info,
        'site_theme': site_theme,
        'menu_items': menu_items,
        'page_title': 'Database Debug',
    }
    
    return render(request, 'core/debug_db.html', context)


@staff_member_required
def bulk_image_upload(request):
    """
    Bulk upload view for menu item images.
    Simply uploads files to media directory - images will work automatically 
    since database already contains the correct filenames.
    """
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('bulk_images')
        success_count = 0
        error_messages = []
        success_messages = []
        
        for uploaded_file in uploaded_files:
            try:
                # Simple file upload - save to media directory
                # Django will handle the file saving automatically
                import os
                from django.core.files.storage import default_storage
                
                filename = uploaded_file.name
                file_path = default_storage.save(filename, uploaded_file)
                
                success_count += 1
                success_messages.append(f"✅ {filename} → Uploaded successfully")
                    
            except Exception as e:
                error_messages.append(f"❌ {uploaded_file.name}: Upload error - {str(e)}")
        
        # Add messages
        if success_count > 0:
            messages.success(request, f"Successfully uploaded {success_count} images!")
            for msg in success_messages:
                messages.success(request, msg)
        
        for error_msg in error_messages:
            messages.warning(request, error_msg)
        
        return redirect('core:bulk_upload')
    
    # GET request - show upload form
    menu_items = MenuItem.objects.all().order_by('category__order', 'name')
    
    context = {
        'menu_items': menu_items,
        'page_title': 'Bulk Image Upload',
    }
    
    return render(request, 'core/bulk_image_upload.html', context)
