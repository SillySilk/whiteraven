"""
Management command to test image processing functionality.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from menu.models import MenuItem, Category
from menu.utils.image_processing import (
    generate_placeholder_image,
    optimize_image,
    create_multiple_sizes,
    validate_image,
    ensure_placeholder_exists
)
from PIL import Image
import io
import os


class Command(BaseCommand):
    help = 'Test image processing functionality for menu items'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-images',
            action='store_true',
            help='Create test images for testing'
        )
        
        parser.add_argument(
            '--test-placeholders',
            action='store_true',
            help='Test placeholder generation'
        )
        
        parser.add_argument(
            '--test-optimization',
            action='store_true',
            help='Test image optimization'
        )
        
        parser.add_argument(
            '--test-all',
            action='store_true',
            help='Run all tests'
        )
    
    def handle(self, *args, **options):
        if options['test_all']:
            self.test_placeholder_generation()
            self.test_image_optimization()
            self.test_menu_item_image_processing()
        else:
            if options['test_placeholders']:
                self.test_placeholder_generation()
            
            if options['test_optimization']:
                self.test_image_optimization()
            
            if options['create_test_images']:
                self.create_test_images()
    
    def test_placeholder_generation(self):
        """Test placeholder image generation"""
        self.stdout.write(self.style.HTTP_INFO('Testing placeholder generation...'))
        
        try:
            # Test basic placeholder generation
            placeholder = generate_placeholder_image("Test Coffee", size=(400, 300), color_index=0)
            self.stdout.write(self.style.SUCCESS('[OK] Basic placeholder generation works'))
            
            # Test different sizes
            sizes = [(150, 150), (400, 300), (800, 600)]
            for size in sizes:
                placeholder = generate_placeholder_image(f"Test {size[0]}x{size[1]}", size=size)
                self.stdout.write(self.style.SUCCESS(f'[OK] Placeholder generation for {size[0]}x{size[1]} works'))
            
            # Test different color indices
            for i in range(6):
                placeholder = generate_placeholder_image(f"Color {i}", color_index=i)
            self.stdout.write(self.style.SUCCESS('[OK] Different placeholder colors work'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Placeholder generation failed: {e}'))
    
    def test_image_optimization(self):
        """Test image optimization functionality"""
        self.stdout.write(self.style.HTTP_INFO('Testing image optimization...'))
        
        try:
            # Create a test image
            test_image = self.create_test_image(800, 600)
            
            # Test optimization
            optimized = optimize_image(test_image, max_size=(400, 300), quality=85)
            self.stdout.write(self.style.SUCCESS('[OK] Image optimization works'))
            
            # Test validation
            test_image.seek(0)
            is_valid, error = validate_image(test_image)
            if is_valid:
                self.stdout.write(self.style.SUCCESS('[OK] Image validation works'))
            else:
                self.stdout.write(self.style.ERROR(f'[ERROR] Image validation failed: {error}'))
            
            # Test multiple sizes creation (would need a saved file for this)
            self.stdout.write(self.style.SUCCESS('[OK] Image optimization tests completed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Image optimization failed: {e}'))
    
    def test_menu_item_image_processing(self):
        """Test image processing with actual menu items"""
        self.stdout.write(self.style.HTTP_INFO('Testing menu item image processing...'))
        
        try:
            # Get or create a test category
            category, created = Category.objects.get_or_create(
                name='Test Category',
                defaults={'description': 'Test category for image processing', 'order': 999}
            )
            
            # Create a test menu item without image
            menu_item, created = MenuItem.objects.get_or_create(
                name='Test Coffee with Image Processing',
                defaults={
                    'description': 'A test coffee item for image processing',
                    'price': 4.95,
                    'category': category,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'[OK] Created test menu item: {menu_item.name}'))
            
            # Test placeholder generation for menu item
            if not menu_item.image:
                success = ensure_placeholder_exists(menu_item)
                if success:
                    menu_item.save()
                    self.stdout.write(self.style.SUCCESS('[OK] Placeholder created for menu item'))
                else:
                    self.stdout.write(self.style.WARNING('[WARNING] Could not create placeholder for menu item'))
            
            # Test image URLs
            image_urls = menu_item.get_image_urls()
            self.stdout.write(self.style.SUCCESS(f'[OK] Image URLs: {list(image_urls.keys())}'))
            
            # Test display URL
            display_url = menu_item.get_display_image_url('card')
            if display_url:
                self.stdout.write(self.style.SUCCESS('[OK] Display URL generation works'))
            
            # Test has_image method
            has_image = menu_item.has_image()
            self.stdout.write(self.style.SUCCESS(f'[OK] Has real image: {has_image}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Menu item image processing failed: {e}'))
    
    def create_test_images(self):
        """Create test images for manual testing"""
        self.stdout.write(self.style.HTTP_INFO('Creating test images...'))
        
        try:
            # Create test images directory
            test_dir = 'media/test_images'
            os.makedirs(test_dir, exist_ok=True)
            
            # Create different sized test images
            sizes = [(400, 300), (800, 600), (1200, 900)]
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            
            for i, size in enumerate(sizes):
                img = Image.new('RGB', size, colors[i % len(colors)])
                
                # Add some text to make it identifiable
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                text = f'Test Image {size[0]}x{size[1]}'
                
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                except:
                    font = None
                
                # Calculate text position
                if font:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                else:
                    text_width = len(text) * 10
                    text_height = 20
                
                x = (size[0] - text_width) // 2
                y = (size[1] - text_height) // 2
                
                draw.text((x, y), text, fill='white', font=font)
                
                # Save image
                filename = f'{test_dir}/test_image_{size[0]}x{size[1]}.jpg'
                img.save(filename, 'JPEG', quality=90)
                
                self.stdout.write(self.style.SUCCESS(f'[OK] Created {filename}'))
            
            self.stdout.write(self.style.SUCCESS(f'[OK] Test images created in {test_dir}/'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Test image creation failed: {e}'))
    
    def create_test_image(self, width, height):
        """Create a test image in memory"""
        # Create a simple colored image
        img = Image.new('RGB', (width, height), '#4ECDC4')
        
        # Add some content
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes
        draw.rectangle([50, 50, width-50, height-50], outline='white', width=5)
        draw.ellipse([100, 100, width-100, height-100], fill='#FF6B6B')
        
        # Convert to file-like object
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=90)
        buffer.seek(0)
        
        return buffer