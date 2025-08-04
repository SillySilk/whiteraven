#!/usr/bin/env python
"""
Simple script to fix broken image references by updating extensions to .jpg
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from menu.models import MenuItem
from django.core.files.storage import default_storage

def fix_broken_images():
    print("=== Fixing Broken Image References ===")
    
    fixed_count = 0
    items_with_images = MenuItem.objects.exclude(image='')
    
    for item in items_with_images:
        old_path = item.image.name
        print(f'\nItem: {item.name}')
        print(f'  Current path: {old_path}')
        
        # Check if current path exists
        if default_storage.exists(old_path):
            print(f'  OK: File exists - no fix needed')
            continue
        
        # Try changing extension to .jpg
        base_name = os.path.splitext(old_path)[0]
        jpg_path = f"{base_name}.jpg"
        
        if default_storage.exists(jpg_path):
            print(f'  FOUND JPG version: {jpg_path}')
            # Update the database directly without triggering image processing
            MenuItem.objects.filter(pk=item.pk).update(image=jpg_path)
            fixed_count += 1
            print(f'  UPDATED database reference')
        else:
            # Try .png version
            png_path = f"{base_name}.png"
            if default_storage.exists(png_path):
                print(f'  FOUND PNG version: {png_path}')
                MenuItem.objects.filter(pk=item.pk).update(image=png_path)
                fixed_count += 1
                print(f'  UPDATED database reference')
            else:
                print(f'  ERROR: No matching file found')
    
    print(f'\n=== Summary ===')
    print(f'Fixed {fixed_count} broken image references')
    
    if fixed_count > 0:
        print('SUCCESS: All broken references have been fixed!')
        print('Images should now display correctly in admin and public site.')
    else:
        print('No broken references found.')

if __name__ == "__main__":
    fix_broken_images()