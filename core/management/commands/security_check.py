"""
Django management command to check and validate security configuration.

This command helps administrators verify that all security measures are properly configured.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Check security configuration and provide recommendations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--production',
            action='store_true',
            help='Check production-specific security settings',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed security information',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔒 Security Configuration Check')
        )
        self.stdout.write('=' * 50)
        
        issues = []
        warnings = []
        
        # Check basic security settings
        issues.extend(self.check_basic_security())
        
        # Check HTTPS settings
        if options['production']:
            issues.extend(self.check_https_security())
        
        # Check file upload security
        issues.extend(self.check_file_upload_security())
        
        # Check authentication security
        warnings.extend(self.check_authentication_security())
        
        # Check CSRF protection
        issues.extend(self.check_csrf_protection())
        
        # Check admin security
        warnings.extend(self.check_admin_security())
        
        # Report results
        self.report_results(issues, warnings, options['verbose'])

    def check_basic_security(self):
        """Check basic security settings."""
        issues = []
        
        self.stdout.write("\n📋 Basic Security Settings:")
        
        # Check SECRET_KEY
        if settings.SECRET_KEY.startswith('django-insecure'):
            issues.append("SECRET_KEY is using default insecure value")
            self.stdout.write(self.style.ERROR("  ❌ SECRET_KEY is insecure"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ SECRET_KEY is configured"))
        
        # Check DEBUG setting
        if settings.DEBUG:
            if os.environ.get('PRODUCTION') == 'True':
                issues.append("DEBUG is True in production environment")
                self.stdout.write(self.style.ERROR("  ❌ DEBUG is enabled in production"))
            else:
                self.stdout.write(self.style.WARNING("  ⚠️  DEBUG is enabled (development)"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ DEBUG is disabled"))
        
        # Check ALLOWED_HOSTS
        if '*' in settings.ALLOWED_HOSTS:
            issues.append("ALLOWED_HOSTS contains wildcard '*'")
            self.stdout.write(self.style.ERROR("  ❌ ALLOWED_HOSTS allows all hosts"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ ALLOWED_HOSTS is restricted"))
        
        return issues

    def check_https_security(self):
        """Check HTTPS and SSL security settings."""
        issues = []
        
        self.stdout.write("\n🔐 HTTPS Security Settings:")
        
        # Check SSL redirect
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            issues.append("SECURE_SSL_REDIRECT is not enabled")
            self.stdout.write(self.style.ERROR("  ❌ SSL redirect not enabled"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ SSL redirect enabled"))
        
        # Check HSTS
        if not getattr(settings, 'SECURE_HSTS_SECONDS', 0):
            issues.append("SECURE_HSTS_SECONDS is not set")
            self.stdout.write(self.style.ERROR("  ❌ HSTS not configured"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ HSTS configured"))
        
        # Check secure cookies
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
            issues.append("SESSION_COOKIE_SECURE is not enabled")
            self.stdout.write(self.style.ERROR("  ❌ Session cookies not secure"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ Session cookies secure"))
        
        return issues

    def check_file_upload_security(self):
        """Check file upload security settings."""
        issues = []
        
        self.stdout.write("\n📁 File Upload Security:")
        
        # Check file size limits
        max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 0)
        if max_size > 10 * 1024 * 1024:  # 10MB
            issues.append("FILE_UPLOAD_MAX_MEMORY_SIZE is too large")
            self.stdout.write(self.style.WARNING("  ⚠️  Large file upload limit"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ File upload size limited"))
        
        # Check blocked extensions
        blocked = getattr(settings, 'BLOCKED_EXTENSIONS', [])
        if not blocked:
            issues.append("BLOCKED_EXTENSIONS is not configured")
            self.stdout.write(self.style.ERROR("  ❌ No blocked file extensions"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ Dangerous file types blocked"))
        
        # Check allowed MIME types
        allowed_mime = getattr(settings, 'ALLOWED_MIME_TYPES', [])
        if not allowed_mime:
            issues.append("ALLOWED_MIME_TYPES is not configured")
            self.stdout.write(self.style.WARNING("  ⚠️  MIME type filtering not configured"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ MIME type filtering enabled"))
        
        return issues

    def check_authentication_security(self):
        """Check authentication and password security."""
        warnings = []
        
        self.stdout.write("\n🔑 Authentication Security:")
        
        # Check password validators
        validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        if len(validators) < 4:
            warnings.append("Not all password validators are configured")
            self.stdout.write(self.style.WARNING("  ⚠️  Password validation incomplete"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ Password validation configured"))
        
        # Check session timeout
        session_age = getattr(settings, 'SESSION_COOKIE_AGE', 0)
        if session_age > 7200:  # 2 hours
            warnings.append("Session timeout is quite long")
            self.stdout.write(self.style.WARNING("  ⚠️  Long session timeout"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ Session timeout reasonable"))
        
        return warnings

    def check_csrf_protection(self):
        """Check CSRF protection settings."""
        issues = []
        
        self.stdout.write("\n🛡️  CSRF Protection:")
        
        # Check CSRF middleware
        if 'django.middleware.csrf.CsrfViewMiddleware' not in settings.MIDDLEWARE:
            issues.append("CSRF middleware is not installed")
            self.stdout.write(self.style.ERROR("  ❌ CSRF middleware missing"))
        else:
            self.stdout.write(self.style.SUCCESS("  ✅ CSRF middleware installed"))
        
        # Check CSRF cookie settings
        if getattr(settings, 'CSRF_COOKIE_HTTPONLY', False):
            self.stdout.write(self.style.SUCCESS("  ✅ CSRF cookies HTTP-only"))
        else:
            issues.append("CSRF_COOKIE_HTTPONLY is not enabled")
            self.stdout.write(self.style.ERROR("  ❌ CSRF cookies not HTTP-only"))
        
        return issues

    def check_admin_security(self):
        """Check admin interface security."""
        warnings = []
        
        self.stdout.write("\n⚙️  Admin Security:")
        
        # Check for default admin user
        try:
            admin_users = User.objects.filter(is_superuser=True)
            if admin_users.filter(username='admin').exists():
                warnings.append("Default 'admin' user exists")
                self.stdout.write(self.style.WARNING("  ⚠️  Default admin user found"))
            
            # Check for weak passwords (basic check)
            for user in admin_users:
                if user.password.startswith('pbkdf2_sha256$') and len(user.password) < 50:
                    warnings.append(f"User {user.username} may have a weak password")
                    self.stdout.write(self.style.WARNING(f"  ⚠️  {user.username} password may be weak"))
            
            self.stdout.write(self.style.SUCCESS(f"  ✅ {admin_users.count()} admin user(s) found"))
        
        except Exception as e:
            warnings.append(f"Could not check admin users: {e}")
            self.stdout.write(self.style.WARNING("  ⚠️  Could not check admin users"))
        
        return warnings

    def report_results(self, issues, warnings, verbose):
        """Report the security check results."""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("📊 Security Check Results:")
        
        if not issues and not warnings:
            self.stdout.write(self.style.SUCCESS("\n🎉 No security issues found!"))
        else:
            if issues:
                self.stdout.write(self.style.ERROR(f"\n❌ {len(issues)} Critical Issues:"))
                for issue in issues:
                    self.stdout.write(f"   • {issue}")
            
            if warnings:
                self.stdout.write(self.style.WARNING(f"\n⚠️  {len(warnings)} Warnings:"))
                for warning in warnings:
                    self.stdout.write(f"   • {warning}")
        
        if verbose:
            self.stdout.write("\n📋 Security Recommendations:")
            self.stdout.write("   • Regularly update Django and dependencies")
            self.stdout.write("   • Monitor logs for suspicious activity")
            self.stdout.write("   • Use strong, unique passwords for admin accounts")
            self.stdout.write("   • Enable two-factor authentication if available")
            self.stdout.write("   • Regularly backup your database")
            self.stdout.write("   • Monitor file uploads for malicious content")
        
        self.stdout.write("\n" + "=" * 50)