# White Raven Pourhouse - PythonAnywhere Deployment Guide

This comprehensive guide walks you through deploying the White Raven Pourhouse Django website to PythonAnywhere hosting.

## Prerequisites

- PythonAnywhere account (free tier is sufficient to start)
- White Raven Pourhouse source code
- Basic familiarity with command line operations

## Overview

The deployment process involves:
1. Setting up PythonAnywhere environment
2. Uploading and configuring the application
3. Setting up MySQL database
4. Configuring environment variables
5. Setting up static and media file serving
6. Testing the deployment

## Step 1: Prepare Your PythonAnywhere Account

### 1.1 Create PythonAnywhere Account
- Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
- Choose the free "Beginner" plan to start
- Verify your email address

### 1.2 Access Your Dashboard
- Log in to your PythonAnywhere dashboard
- Familiarize yourself with the main sections: Dashboard, Web, Files, Tasks, Databases, and Consoles

## Step 2: Upload Your Code

### 2.1 Using Git (Recommended)
```bash
# Open a Bash console in PythonAnywhere
cd ~
git clone https://github.com/yourusername/white-raven-pourhouse.git
cd white-raven-pourhouse
```

### 2.2 Using File Upload
- Navigate to Files > Upload a file
- Upload your project as a ZIP file
- Extract in your home directory
- Rename folder to `white-raven-pourhouse`

## Step 3: Set Up MySQL Database

### 3.1 Create Database
1. Go to **Databases** in your PythonAnywhere dashboard
2. Set a MySQL password if you haven't already
3. Create a new database named `yourusername$whiteravenpourhouse`
   - Replace `yourusername` with your actual PythonAnywhere username
4. Note down your database details:
   - Database name: `yourusername$whiteravenpourhouse`
   - Username: `yourusername`
   - Password: (the one you set)
   - Host: `yourusername.mysql.pythonanywhere-services.com`

## Step 4: Configure Environment Variables

### 4.1 Generate Secret Key
```bash
# In PythonAnywhere Bash console
cd ~/white-raven-pourhouse
python3.11 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the generated secret key for use in environment variables.

### 4.2 Set Environment Variables
1. Go to **Web** in your PythonAnywhere dashboard
2. Click on your domain (yourusername.pythonanywhere.com)
3. Scroll down to **Environment variables** section
4. Add the following variables:

```
SECRET_KEY=your-generated-secret-key-here
PRODUCTION=True
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com,whiteravenpourhouse.com
DB_NAME=yourusername$whiteravenpourhouse
DB_USER=yourusername
DB_PASSWORD=your-mysql-password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=noreply@whiteravenpourhouse.com
ADMIN_EMAIL=owner@whiteravenpourhouse.com
STATIC_ROOT=/home/yourusername/static/
MEDIA_ROOT=/home/yourusername/media/
```

Replace all instances of `yourusername` with your actual PythonAnywhere username.

## Step 5: Configure Email

### 5.1 Gmail Setup (Recommended)
1. Enable 2-factor authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for "Mail"
4. Use this 16-character password as `EMAIL_HOST_PASSWORD`
5. Use your full Gmail address as `EMAIL_HOST_USER`

### 5.2 Alternative Email Providers
- Check your email provider's SMTP settings
- Update `EMAIL_HOST` and `EMAIL_PORT` accordingly
- Common ports: 587 (TLS), 465 (SSL)

## Step 6: Run Deployment Script

### 6.1 Make Script Executable and Run
```bash
# In PythonAnywhere Bash console
cd ~/white-raven-pourhouse
chmod +x deployment/deploy_pythonanywhere.sh
./deployment/deploy_pythonanywhere.sh
```

### 6.2 Manual Deployment Steps (Alternative)
If the script doesn't work, follow these manual steps:

```bash
# Create virtual environment
python3.11 -m venv ~/.virtualenvs/white-raven-env
source ~/.virtualenvs/white-raven-env/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements-production.txt

# Create directories
mkdir -p ~/static ~/media/menu ~/media/uploads

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Setup admin groups
python manage.py setup_admin_groups
```

## Step 7: Configure Web App

### 7.1 Basic Web App Configuration
1. Go to **Web** > your domain
2. Set the following paths:
   - **Source code**: `/home/yourusername/white-raven-pourhouse`
   - **Working directory**: `/home/yourusername/white-raven-pourhouse`
   - **Python version**: 3.11
   - **Virtualenv**: `/home/yourusername/.virtualenvs/white-raven-env`

### 7.2 WSGI Configuration
1. Click on the **WSGI configuration file** link
2. Replace the contents with the content from `deployment/pythonanywhere_wsgi.py`
3. Update all instances of `yourusername` with your actual username
4. Save the file

### 7.3 Static Files Configuration
1. In the **Static files** section, add:
   - **URL**: `/static/`
   - **Path**: `/home/yourusername/static/`

### 7.4 Media Files Configuration
1. In the **Static files** section, add another entry:
   - **URL**: `/media/`
   - **Path**: `/home/yourusername/media/`

## Step 8: Deploy and Test

### 8.1 Reload Web App
1. Click the green **"Reload yourusername.pythonanywhere.com"** button
2. Wait for the reload to complete

### 8.2 Test Your Website
1. Visit `https://yourusername.pythonanywhere.com`
2. Check that the homepage loads correctly
3. Test the admin interface at `/admin/`
4. Test the contact form
5. Upload a menu item with an image to test media files

### 8.3 Troubleshooting
If something isn't working:
1. Check the **Error log** in your web app configuration
2. Check the **Server log** for detailed error messages
3. Verify all environment variables are set correctly
4. Ensure file paths use your correct username

## Step 9: Optional - Custom Domain Setup

### 9.1 Domain Configuration
1. Purchase a domain (e.g., whiteravenpourhouse.com)
2. In PythonAnywhere Web tab, add your custom domain
3. Update DNS records at your domain registrar:
   - **CNAME record**: `www` → `yourusername.pythonanywhere.com`
   - **A record**: `@` → PythonAnywhere IP (provided in dashboard)
4. Update `ALLOWED_HOSTS` environment variable to include your domain

### 9.2 SSL Certificate
- SSL certificates are automatically provided by PythonAnywhere
- Your site will be accessible via HTTPS

## Step 10: Post-Deployment Tasks

### 10.1 Content Setup
1. Log in to admin interface
2. Add business information in Core > Business infos
3. Create menu categories and items
4. Add employee information if needed
5. Test contact form functionality

### 10.2 Backup Setup
1. Set up regular database backups
2. Consider backing up uploaded media files
3. Keep environment variables backed up securely

### 10.3 Monitoring
1. Set up email notifications for errors
2. Monitor site performance
3. Check logs regularly for issues

## Maintenance and Updates

### Updating Your Site
```bash
# In PythonAnywhere Bash console
cd ~/white-raven-pourhouse
git pull origin main
source ~/.virtualenvs/white-raven-env/bin/activate
pip install -r requirements-production.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

After updates, reload your web app in the PythonAnywhere dashboard.

### Database Maintenance
```bash
# Backup database
mysqldump -u yourusername -p yourusername$whiteravenpourhouse > backup.sql

# Restore database
mysql -u yourusername -p yourusername$whiteravenpourhouse < backup.sql
```

## Security Considerations

1. **Secret Key**: Always use a unique, strong secret key for production
2. **Database Password**: Use a strong password for your MySQL database
3. **Email Passwords**: Use app passwords, not your main email password
4. **HTTPS**: Always access your site via HTTPS
5. **Admin Access**: Use strong passwords for admin accounts
6. **Regular Updates**: Keep Django and dependencies updated

## Support and Troubleshooting

### Common Issues

1. **Import Errors**: Check that all requirements are installed in virtual environment
2. **Database Connection**: Verify database credentials and that database exists
3. **Static Files Not Loading**: Check static files mapping and STATIC_ROOT path
4. **Email Not Working**: Verify email credentials and SMTP settings
5. **Permission Errors**: Check file permissions in media and static directories

### Getting Help
- PythonAnywhere Documentation: [help.pythonanywhere.com](https://help.pythonanywhere.com)
- Django Documentation: [docs.djangoproject.com](https://docs.djangoproject.com)
- PythonAnywhere Forums: [pythonanywhere.com/forums](https://www.pythonanywhere.com/forums)

## Scaling and Upgrades

As your business grows, consider:
1. Upgrading to a paid PythonAnywhere plan for better performance
2. Adding a custom domain
3. Setting up CDN for faster static file delivery
4. Implementing caching for better performance
5. Adding monitoring and analytics

---

This deployment guide should get your White Raven Pourhouse website running on PythonAnywhere. Remember to test thoroughly and keep your deployment secure with regular updates and strong passwords.