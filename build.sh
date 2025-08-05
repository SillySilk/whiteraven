#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Load production data (only if database is empty)
python load_production_data_corrected.py

# Ensure admin user is created and working
python create_admin.py

# Debug theme system to ensure colors are working
python debug_theme_production.py

# Convert static asset files
python manage.py collectstatic --no-input