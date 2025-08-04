# White Raven Pourhouse - Deployment Checklist

Use this checklist to ensure a successful deployment to PythonAnywhere.

## Pre-Deployment Checklist

### ✅ Code Preparation
- [ ] All code committed to version control (Git)
- [ ] requirements-production.txt file is current
- [ ] Database migrations are created and tested
- [ ] Static files are properly configured
- [ ] Security settings are production-ready
- [ ] Debug mode is disabled in production settings

### ✅ PythonAnywhere Account Setup
- [ ] PythonAnywhere account created and verified
- [ ] Billing information set up (if using paid plan)
- [ ] Domain name purchased (if using custom domain)

### ✅ Environment Configuration
- [ ] Secret key generated for production
- [ ] Database credentials prepared
- [ ] Email account configured (Gmail app password)
- [ ] Admin email address configured
- [ ] All environment variables documented

## Deployment Process Checklist

### ✅ Step 1: Upload Code
- [ ] Code uploaded to PythonAnywhere (via Git or file upload)
- [ ] Code is in `/home/yourusername/white-raven-pourhouse/`
- [ ] File permissions are correct

### ✅ Step 2: Database Setup
- [ ] MySQL database created: `yourusername$whiteravenpourhouse`
- [ ] Database password set and documented
- [ ] Database connection tested

### ✅ Step 3: Virtual Environment
- [ ] Python 3.11 virtual environment created
- [ ] Virtual environment path: `/home/yourusername/.virtualenvs/white-raven-env`
- [ ] Requirements installed in virtual environment
- [ ] Virtual environment activated successfully

### ✅ Step 4: Environment Variables
- [ ] `SECRET_KEY` set (unique for production)
- [ ] `PRODUCTION=True` set
- [ ] `DEBUG=False` set
- [ ] `ALLOWED_HOSTS` configured with domain(s)
- [ ] Database variables set (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST)
- [ ] Email variables set (EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, etc.)
- [ ] File path variables set (STATIC_ROOT, MEDIA_ROOT)
- [ ] Admin email set (ADMIN_EMAIL)

### ✅ Step 5: Directory Structure
- [ ] Static directory created: `/home/yourusername/static/`
- [ ] Media directory created: `/home/yourusername/media/`
- [ ] Media subdirectories created: `/home/yourusername/media/menu/`
- [ ] Media subdirectories created: `/home/yourusername/media/uploads/`
- [ ] Proper permissions set (755 for directories)

### ✅ Step 6: Django Setup
- [ ] Database migrations run successfully
- [ ] Static files collected
- [ ] Superuser account created
- [ ] Admin groups and permissions configured
- [ ] Management commands tested

### ✅ Step 7: Web App Configuration
- [ ] Source code path set: `/home/yourusername/white-raven-pourhouse`
- [ ] Working directory set: `/home/yourusername/white-raven-pourhouse`
- [ ] Python version set to 3.11
- [ ] Virtual environment path configured
- [ ] WSGI file configured correctly

### ✅ Step 8: Static and Media Files
- [ ] Static files mapping: URL `/static/` → Path `/home/yourusername/static/`
- [ ] Media files mapping: URL `/media/` → Path `/home/yourusername/media/`
- [ ] Static files accessible via browser
- [ ] Media file uploads working

### ✅ Step 9: Web App Deployment
- [ ] Web app reloaded
- [ ] No errors in error log
- [ ] Website loads successfully
- [ ] All pages accessible

## Post-Deployment Testing Checklist

### ✅ Basic Functionality
- [ ] Homepage loads correctly
- [ ] Navigation menu works
- [ ] All pages accessible (menu, contact, location)
- [ ] Responsive design works on mobile
- [ ] No broken links

### ✅ Admin Interface
- [ ] Admin login works at `/admin/`
- [ ] Dashboard displays correctly
- [ ] Menu items can be added/edited
- [ ] Business information can be updated
- [ ] Image uploads work correctly

### ✅ Contact Form
- [ ] Contact form displays correctly
- [ ] Form validation works
- [ ] Form submission succeeds
- [ ] Email notifications sent
- [ ] Auto-reply emails sent
- [ ] Contact submissions appear in admin

### ✅ Menu Functionality
- [ ] Menu page displays all categories
- [ ] Menu items show correctly
- [ ] Images display properly
- [ ] Prices formatted correctly
- [ ] Available/unavailable items handled correctly

### ✅ Email System
- [ ] Contact form emails delivered
- [ ] Auto-reply emails sent
- [ ] Error notification emails working
- [ ] Email templates render correctly
- [ ] No email delivery errors in logs

### ✅ Security Features
- [ ] HTTPS working correctly
- [ ] Admin requires authentication
- [ ] CSRF protection active
- [ ] File upload security working
- [ ] Rate limiting functional
- [ ] Security headers present

### ✅ Performance
- [ ] Page load times acceptable (< 3 seconds)
- [ ] Images load quickly
- [ ] Static files served efficiently
- [ ] Database queries optimized

## Domain Configuration Checklist (If Using Custom Domain)

### ✅ DNS Configuration
- [ ] Domain purchased and accessible
- [ ] DNS records configured:
  - [ ] A record: `@` → PythonAnywhere IP
  - [ ] CNAME record: `www` → `yourusername.pythonanywhere.com`
- [ ] DNS propagation complete (24-48 hours)

### ✅ PythonAnywhere Domain Setup
- [ ] Custom domain added in Web tab
- [ ] Domain verification completed
- [ ] SSL certificate issued
- [ ] ALLOWED_HOSTS updated with domain
- [ ] Domain redirects working

## Troubleshooting Checklist

### ✅ If Site Doesn't Load
- [ ] Check error log in PythonAnywhere Web tab
- [ ] Verify WSGI file syntax
- [ ] Check environment variables
- [ ] Confirm virtual environment activation
- [ ] Review file paths and permissions

### ✅ If Admin Doesn't Work
- [ ] Verify admin URL (`/admin/` not `/admin`)
- [ ] Check superuser credentials
- [ ] Confirm database connection
- [ ] Review static files configuration

### ✅ If Email Doesn't Work
- [ ] Test email configuration with management command
- [ ] Verify Gmail app password
- [ ] Check email environment variables
- [ ] Review email backend settings

### ✅ If Images Don't Upload
- [ ] Check media files mapping
- [ ] Verify directory permissions
- [ ] Test file upload limits
- [ ] Review image processing settings

## Go-Live Checklist

### ✅ Final Preparations
- [ ] All testing completed successfully
- [ ] Backup procedures tested
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Team trained on admin interface

### ✅ Launch
- [ ] Site announcement prepared
- [ ] Social media updated with new website
- [ ] Business cards/materials updated
- [ ] Google My Business updated
- [ ] Instagram bio link updated

### ✅ Post-Launch
- [ ] Monitor error logs for 48 hours
- [ ] Verify all functionality working
- [ ] Check contact form submissions
- [ ] Monitor site performance
- [ ] Schedule first backup

## Emergency Rollback Checklist

### ✅ If Issues Arise
- [ ] Document the issue
- [ ] Check recent changes
- [ ] Review error logs
- [ ] Consider rollback options:
  - [ ] Revert code changes
  - [ ] Restore database backup
  - [ ] Reset environment variables
- [ ] Test rollback before applying
- [ ] Notify stakeholders of issues

## Documentation Checklist

### ✅ Maintain Records
- [ ] Environment variables documented securely
- [ ] Database credentials stored safely
- [ ] Email account information accessible
- [ ] Domain registrar details recorded
- [ ] PythonAnywhere account information secured
- [ ] Backup procedures documented
- [ ] Emergency contact information available

---

**Note**: Replace `yourusername` with your actual PythonAnywhere username throughout this checklist.

Print this checklist and check off items as you complete them to ensure nothing is missed during deployment.