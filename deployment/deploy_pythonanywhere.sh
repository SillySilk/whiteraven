#!/bin/bash

# White Raven Pourhouse - PythonAnywhere Deployment Script
# Run this script in your PythonAnywhere Bash console after uploading your code

set -e  # Exit on any error

echo "==========================================="
echo "White Raven Pourhouse Deployment Script"
echo "==========================================="

# Configuration variables - UPDATE THESE
USERNAME="yourusername"  # Replace with your PythonAnywhere username
PROJECT_DIR="/home/$USERNAME/white-raven-pourhouse"
VENV_PATH="/home/$USERNAME/.virtualenvs/white-raven-env"
STATIC_DIR="/home/$USERNAME/static"
MEDIA_DIR="/home/$USERNAME/media"

echo "Deploying for user: $USERNAME"
echo "Project directory: $PROJECT_DIR"

# Check if we're in the project directory
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Make sure you're in the project root directory."
    echo "Current directory: $(pwd)"
    echo "Expected directory: $PROJECT_DIR"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv $VENV_PATH
fi

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV_PATH/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install production requirements
echo "Installing production requirements..."
if [ -f "requirements-production.txt" ]; then
    pip install -r requirements-production.txt
else
    echo "Warning: requirements-production.txt not found, installing from requirements.txt"
    pip install -r requirements.txt
fi

# Create necessary directories
echo "Creating static and media directories..."
mkdir -p $STATIC_DIR
mkdir -p $MEDIA_DIR
mkdir -p $MEDIA_DIR/menu
mkdir -p $MEDIA_DIR/uploads

# Set proper permissions
chmod 755 $STATIC_DIR
chmod 755 $MEDIA_DIR
chmod 755 $MEDIA_DIR/menu
chmod 755 $MEDIA_DIR/uploads

# Check environment variables
echo "Checking environment variables..."
if [ -z "$SECRET_KEY" ]; then
    echo "Warning: SECRET_KEY environment variable not set"
fi
if [ -z "$DB_PASSWORD" ]; then
    echo "Warning: DB_PASSWORD environment variable not set"
fi
if [ -z "$PRODUCTION" ]; then
    echo "Warning: PRODUCTION environment variable not set - defaulting to True"
    export PRODUCTION=True
fi

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
read -p "Do you want to create a superuser account? (y/n): " create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    echo "Creating superuser account..."
    python manage.py createsuperuser
fi

# Setup admin groups and permissions
echo "Setting up admin groups and permissions..."
python manage.py setup_admin_groups

# Test email configuration (optional)
read -p "Do you want to test email configuration? (y/n): " test_email
if [ "$test_email" = "y" ] || [ "$test_email" = "Y" ]; then
    echo "Testing email configuration..."
    python manage.py test_email
fi

# Run security check
echo "Running security check..."
python manage.py security_check

echo "==========================================="
echo "Deployment completed successfully!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Configure your PythonAnywhere web app:"
echo "   - Source code: $PROJECT_DIR"
echo "   - Working directory: $PROJECT_DIR"
echo "   - WSGI file: $PROJECT_DIR/white_raven_pourhouse/wsgi.py"
echo "   - Python version: 3.11"
echo ""
echo "2. Set environment variables in PythonAnywhere web app configuration:"
echo "   - Copy values from .env.pythonanywhere file"
echo "   - Set PRODUCTION=True"
echo "   - Set SECRET_KEY (generate a new one)"
echo "   - Set database credentials"
echo "   - Set email configuration"
echo ""
echo "3. Configure static files mapping in PythonAnywhere:"
echo "   - URL: /static/"
echo "   - Path: $STATIC_DIR"
echo ""
echo "4. Configure media files mapping in PythonAnywhere:"
echo "   - URL: /media/"
echo "   - Path: $MEDIA_DIR"
echo ""
echo "5. Reload your web app in PythonAnywhere dashboard"
echo ""
echo "Your website will be available at: https://$USERNAME.pythonanywhere.com"
echo "Admin interface: https://$USERNAME.pythonanywhere.com/admin/"
echo ""
echo "For troubleshooting, check the error log in PythonAnywhere dashboard."