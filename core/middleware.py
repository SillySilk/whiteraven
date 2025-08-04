"""
Security middleware for White Raven Pourhouse website.

This middleware provides:
- Rate limiting for different types of requests
- Content Security Policy headers
- Additional security headers
- Login attempt monitoring
- Suspicious activity detection
"""

import time
from collections import defaultdict
from django.http import HttpResponse
from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """
    Custom security middleware for rate limiting and additional protection.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # In-memory store for rate limiting (use Redis/Memcached in production)
        self.rate_limit_store = defaultdict(list)
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process incoming requests for security checks."""
        # Get client IP address
        client_ip = self.get_client_ip(request)
        
        # Check rate limits
        if self.is_rate_limited(request, client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}, Path: {request.path}")
            return HttpResponse(
                "Too many requests. Please try again later.",
                status=429,
                content_type="text/plain"
            )
        
        # Log suspicious patterns
        self.check_suspicious_activity(request, client_ip)
        
        return None
    
    def process_response(self, request, response):
        """Add security headers to response."""
        # Add Content Security Policy headers
        if hasattr(settings, 'CSP_DEFAULT_SRC'):
            csp_header = self.build_csp_header()
            response['Content-Security-Policy'] = csp_header
        
        # Add additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = getattr(
            settings, 'SECURE_REFERRER_POLICY', 'strict-origin-when-cross-origin'
        )
        
        # Add Cross-Origin policies for production
        if getattr(settings, 'PRODUCTION', False):
            response['Cross-Origin-Opener-Policy'] = 'same-origin'
            response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        
        return response
    
    def get_client_ip(self, request):
        """Get the real client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def is_rate_limited(self, request, client_ip):
        """Check if the request should be rate limited."""
        current_time = time.time()
        
        # Determine rate limit based on request type
        if request.path.startswith('/admin/login/'):
            limit = getattr(settings, 'RATE_LIMIT_LOGIN', 5)
            window_key = f"login_{client_ip}"
        elif request.path.startswith('/contact/') and request.method == 'POST':
            limit = getattr(settings, 'RATE_LIMIT_CONTACT', 3)
            window_key = f"contact_{client_ip}"
        else:
            limit = getattr(settings, 'RATE_LIMIT_GENERAL', 60)
            window_key = f"general_{client_ip}"
        
        # Use cache for rate limiting (fallback to in-memory if cache unavailable)
        try:
            # Try to use Django cache
            cache_key = f"rate_limit_{window_key}"
            requests = cache.get(cache_key, [])
            
            # Remove old requests (older than 1 minute)
            requests = [req_time for req_time in requests if current_time - req_time < 60]
            
            # Check if limit exceeded
            if len(requests) >= limit:
                return True
            
            # Add current request
            requests.append(current_time)
            cache.set(cache_key, requests, 60)  # Cache for 1 minute
            
        except Exception:
            # Fallback to in-memory store
            requests = self.rate_limit_store[window_key]
            
            # Remove old requests
            requests[:] = [req_time for req_time in requests if current_time - req_time < 60]
            
            # Check if limit exceeded
            if len(requests) >= limit:
                return True
            
            # Add current request
            requests.append(current_time)
        
        return False
    
    def check_suspicious_activity(self, request, client_ip):
        """Check for suspicious activity patterns."""
        # Log potential SQL injection attempts
        suspicious_patterns = [
            'union', 'select', 'drop', 'insert', 'delete', 'update',
            '<script', 'javascript:', 'onload=', 'onerror=',
            '../', '..\\', '/etc/passwd', 'cmd.exe'
        ]
        
        query_string = request.GET.urlencode().lower()
        post_data = ""
        
        if request.method == 'POST' and hasattr(request, 'POST'):
            try:
                post_data = str(request.POST).lower()
            except:
                pass
        
        for pattern in suspicious_patterns:
            if pattern in query_string or pattern in post_data:
                logger.warning(
                    f"Suspicious activity detected from IP {client_ip}: "
                    f"Pattern '{pattern}' found in {request.method} {request.path}"
                )
                break
    
    def build_csp_header(self):
        """Build Content Security Policy header from settings."""
        csp_directives = []
        
        csp_settings = {
            'default-src': getattr(settings, 'CSP_DEFAULT_SRC', ["'self'"]),
            'script-src': getattr(settings, 'CSP_SCRIPT_SRC', ["'self'"]),
            'style-src': getattr(settings, 'CSP_STYLE_SRC', ["'self'"]),
            'img-src': getattr(settings, 'CSP_IMG_SRC', ["'self'"]),
            'font-src': getattr(settings, 'CSP_FONT_SRC', ["'self'"]),
            'connect-src': getattr(settings, 'CSP_CONNECT_SRC', ["'self'"]),
            'frame-ancestors': getattr(settings, 'CSP_FRAME_ANCESTORS', ["'none'"]),
            'base-uri': getattr(settings, 'CSP_BASE_URI', ["'self'"]),
            'form-action': getattr(settings, 'CSP_FORM_ACTION', ["'self'"]),
        }
        
        for directive, sources in csp_settings.items():
            if sources:
                csp_directives.append(f"{directive} {' '.join(sources)}")
        
        return '; '.join(csp_directives)


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts for security monitoring."""
    if request:
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        username = credentials.get('username', 'unknown')
        
        logger.warning(
            f"Failed login attempt for username '{username}' from IP {client_ip}"
        )
        
        # Track failed attempts for account lockout
        cache_key = f"failed_login_{username}"
        failed_attempts = cache.get(cache_key, 0) + 1
        cache.set(cache_key, failed_attempts, 1800)  # 30 minutes
        
        # Log if threshold reached
        threshold = getattr(settings, 'ACCOUNT_LOCKOUT_THRESHOLD', 5)
        if failed_attempts >= threshold:
            logger.error(
                f"Account lockout threshold reached for username '{username}' "
                f"from IP {client_ip}. Attempts: {failed_attempts}"
            )


class FileUploadSecurityMiddleware(MiddlewareMixin):
    """
    Middleware to enhance file upload security.
    """
    
    def process_request(self, request):
        """Check file uploads for security issues."""
        if request.method == 'POST' and request.FILES:
            for field_name, uploaded_file in request.FILES.items():
                if not self.is_safe_upload(uploaded_file):
                    logger.warning(
                        f"Blocked unsafe file upload: {uploaded_file.name} "
                        f"from IP {request.META.get('REMOTE_ADDR', 'unknown')}"
                    )
                    return HttpResponse(
                        "File upload rejected for security reasons.",
                        status=429,
                        content_type="text/plain"
                    )
        
        return None
    
    def is_safe_upload(self, uploaded_file):
        """Check if uploaded file is safe."""
        import os
        
        # Check file size
        max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 5242880)  # 5MB
        if uploaded_file.size > max_size:
            return False
        
        # Check file extension
        name = uploaded_file.name.lower()
        ext = os.path.splitext(name)[1]
        
        # Check against blocked extensions
        blocked_extensions = getattr(settings, 'BLOCKED_EXTENSIONS', [])
        if ext in blocked_extensions:
            return False
        
        # Check against allowed extensions for images
        if hasattr(uploaded_file, 'content_type'):
            allowed_mime_types = getattr(settings, 'ALLOWED_MIME_TYPES', [])
            if allowed_mime_types and uploaded_file.content_type not in allowed_mime_types:
                return False
        
        # Additional checks could include:
        # - File signature validation
        # - Virus scanning (if available)
        # - Content inspection
        
        return True