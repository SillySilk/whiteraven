from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from menu.models import MenuItem
import os


class Command(BaseCommand):
    help = 'Fix menu item image paths to match actual files'

    def handle(self, *args, **options):
        self.stdout.write('=== Fixing Menu Item Image Paths ===')
        
        fixed_count = 0
        items_with_images = MenuItem.objects.exclude(image='')
        
        for item in items_with_images:
            old_path = item.image.name
            self.stdout.write(f'\nChecking item: {item.name}')
            self.stdout.write(f'  Current path: {old_path}')
            
            # Check if current path exists
            if default_storage.exists(old_path):
                self.stdout.write(f'  OK: File exists at current path')
                continue
            
            # Try to find the actual file
            base_name = os.path.splitext(os.path.basename(old_path))[0]
            directory = os.path.dirname(old_path)
            
            # Check for various extensions
            possible_extensions = ['.png', '.jpg', '.jpeg', '.webp']
            found_file = None
            
            for ext in possible_extensions:
                test_path = f"{directory}/{base_name}{ext}"
                if default_storage.exists(test_path):
                    found_file = test_path
                    break
            
            if found_file:
                self.stdout.write(f'  FOUND actual file: {found_file}')
                item.image.name = found_file
                item.save(update_fields=['image'])
                fixed_count += 1
                self.stdout.write(f'  UPDATED database path')
            else:
                self.stdout.write(f'  ERROR: No matching file found')
                
                # List actual files in the directory for debugging
                try:
                    actual_files = default_storage.listdir(directory)[1]  # [1] gets files, [0] gets dirs
                    matching_files = [f for f in actual_files if base_name.lower() in f.lower()]
                    if matching_files:
                        self.stdout.write(f'  INFO: Similar files found: {matching_files}')
                except Exception as e:
                    self.stdout.write(f'  WARNING: Error listing directory: {e}')
        
        self.stdout.write(f'\n=== Summary ===')
        self.stdout.write(f'Fixed {fixed_count} image paths')
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {fixed_count} menu item image paths!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No image paths needed fixing.')
            )