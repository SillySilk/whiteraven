#!/usr/bin/env bash
# Exit on error
set -o errexit

# Set production environment
export PRODUCTION=True

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Load production data (only if database is empty)
python load_production_data_corrected.py

# Ensure admin user is created and working
python create_admin.py

# Convert static asset files
python manage.py collectstatic --no-input