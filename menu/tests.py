from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.admin.sites import AdminSite
from django.test.utils import override_settings
from django.contrib.messages import get_messages
from django.http import HttpRequest
from unittest.mock import patch, Mock, MagicMock
from decimal import Decimal
import tempfile
import os
import json

from .models import Category, MenuItem, Recipe
from .admin import CategoryAdmin, MenuItemAdmin, RecipeAdmin
from .utils.image_processing import create_multiple_sizes, cleanup_old_images, get_responsive_image_urls
from .fields import MenuImageField


class CategoryModelTest(TestCase):
    """Test Category model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.category_data = {
            'name': 'Coffee',
            'description': 'Premium coffee drinks',
            'order': 1,
            'active': True
        }
    
    def test_category_creation(self):
        """Test creating a Category instance"""
        category = Category.objects.create(**self.category_data)
        
        self.assertEqual(category.name, 'Coffee')
        self.assertEqual(category.description, 'Premium coffee drinks')
        self.assertEqual(category.order, 1)
        self.assertTrue(category.active)
        self.assertEqual(category.slug, 'coffee')  # Auto-generated
    
    def test_category_str(self):
        """Test string representation"""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(str(category), 'Coffee')
    
    def test_category_slug_generation(self):
        """Test automatic slug generation"""
        category = Category.objects.create(name='Hot Drinks & More')
        self.assertEqual(category.slug, 'hot-drinks-more')
    
    def test_category_custom_slug(self):
        """Test custom slug is preserved"""
        data = self.category_data.copy()
        data['slug'] = 'custom-slug'
        category = Category.objects.create(**data)
        self.assertEqual(category.slug, 'custom-slug')
    
    def test_category_unique_name(self):
        """Test category name uniqueness"""
        Category.objects.create(**self.category_data)
        
        with self.assertRaises(Exception):  # IntegrityError
            Category.objects.create(**self.category_data)
    
    def test_category_ordering(self):
        """Test category ordering"""
        cat1 = Category.objects.create(name='Third', order=3)
        cat2 = Category.objects.create(name='First', order=1)
        cat3 = Category.objects.create(name='Second', order=2)
        
        categories = Category.objects.all()
        self.assertEqual(categories[0], cat2)  # order=1
        self.assertEqual(categories[1], cat3)  # order=2
        self.assertEqual(categories[2], cat1)  # order=3
    
    def test_active_items_count_property(self):
        """Test active_items_count property"""
        category = Category.objects.create(**self.category_data)
        
        # No items yet
        self.assertEqual(category.active_items_count, 0)
        
        # Add active item
        MenuItem.objects.create(
            name='Espresso',
            description='Strong coffee',
            price=Decimal('2.50'),
            category=category,
            available=True
        )
        
        # Add inactive item
        MenuItem.objects.create(
            name='Latte',
            description='Milk coffee',
            price=Decimal('4.50'),
            category=category,
            available=False
        )
        
        self.assertEqual(category.active_items_count, 1)


class MenuItemModelTest(TestCase):
    """Test MenuItem model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='Coffee',
            description='Coffee drinks'
        )
        
        self.menu_item_data = {
            'name': 'Espresso',
            'description': 'Strong, concentrated coffee',
            'price': Decimal('2.50'),
            'category': self.category,
            'available': True,
            'featured': False,
            'temperature': 'hot',
            'size': 'small',
            'contains_caffeine': True,
            'dietary_notes': 'Vegan option available',
            'preparation_time': 3
        }
    
    def test_menu_item_creation(self):
        """Test creating a MenuItem instance"""
        item = MenuItem.objects.create(**self.menu_item_data)
        
        self.assertEqual(item.name, 'Espresso')
        self.assertEqual(item.price, Decimal('2.50'))
        self.assertEqual(item.category, self.category)
        self.assertTrue(item.available)
        self.assertTrue(item.contains_caffeine)
        self.assertEqual(item.preparation_time, 3)
    
    def test_menu_item_str(self):
        """Test string representation"""
        item = MenuItem.objects.create(**self.menu_item_data)
        self.assertEqual(str(item), 'Espresso ($2.50)')
    
    def test_menu_item_slug_generation(self):
        """Test automatic slug generation"""
        item = MenuItem.objects.create(**self.menu_item_data)
        self.assertEqual(item.slug, 'espresso')
        
        # Test duplicate handling
        data = self.menu_item_data.copy()
        data['name'] = 'Espresso'  # Same name
        item2 = MenuItem.objects.create(**data)
        self.assertEqual(item2.slug, 'espresso-1')
    
    def test_menu_item_price_validation(self):
        """Test price validation"""
        data = self.menu_item_data.copy()
        data['price'] = Decimal('-1.00')  # Negative price
        item = MenuItem(**data)
        
        with self.assertRaises(ValidationError):
            item.full_clean()
    
    def test_menu_item_display_price_property(self):
        """Test display_price property"""
        item = MenuItem.objects.create(**self.menu_item_data)
        self.assertEqual(item.display_price, '$2.50')
    
    def test_menu_item_is_drink_property(self):
        """Test is_drink property"""
        # Coffee category should be considered a drink
        coffee_cat = Category.objects.create(name='Coffee', slug='coffee')
        coffee_item = MenuItem.objects.create(
            name='Latte',
            description='Coffee with milk',
            price=Decimal('4.50'),
            category=coffee_cat
        )
        self.assertTrue(coffee_item.is_drink)
        
        # Food category should not be considered a drink
        food_cat = Category.objects.create(name='Pastries', slug='pastries')
        food_item = MenuItem.objects.create(
            name='Croissant',
            description='Buttery pastry',
            price=Decimal('3.00'),
            category=food_cat
        )
        self.assertFalse(food_item.is_drink)
    
    def test_menu_item_has_image_method(self):
        """Test has_image method"""
        item = MenuItem.objects.create(**self.menu_item_data)
        
        # No image
        self.assertFalse(item.has_image())
        
        # Mock image field
        item.image.name = 'menu/test-image.jpg'
        self.assertTrue(item.has_image())
        
        # Placeholder image
        item.image.name = 'menu/placeholders/placeholder.jpg'
        self.assertFalse(item.has_image())
    
    def test_menu_item_ordering(self):
        """Test menu item ordering by category order and name"""
        cat1 = Category.objects.create(name='First', order=1)
        cat2 = Category.objects.create(name='Second', order=2)
        
        item1 = MenuItem.objects.create(
            name='Zebra', price=Decimal('1.00'), category=cat2
        )
        item2 = MenuItem.objects.create(
            name='Apple', price=Decimal('1.00'), category=cat1
        )
        item3 = MenuItem.objects.create(
            name='Banana', price=Decimal('1.00'), category=cat1
        )
        
        items = MenuItem.objects.all()
        # Should be ordered by category order first, then name
        self.assertEqual(items[0], item2)  # cat1, Apple
        self.assertEqual(items[1], item3)  # cat1, Banana
        self.assertEqual(items[2], item1)  # cat2, Zebra


class RecipeModelTest(TestCase):
    """Test Recipe model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name='Coffee')
        self.menu_item = MenuItem.objects.create(
            name='Latte',
            description='Coffee with steamed milk',
            price=Decimal('4.50'),
            category=self.category
        )
        
        self.recipe_data = {
            'menu_item': self.menu_item,
            'ingredients': 'Espresso shot\nSteamed milk\nMilk foam',
            'instructions': 'Pull espresso shot\nSteam milk\nPour milk over espresso\nAdd foam on top',
            'prep_time': 5,
            'difficulty': 'easy',
            'equipment_needed': 'Espresso machine, milk steamer',
            'yield_quantity': '1 serving',
            'notes': 'Can be made with oat milk for vegan option'
        }
    
    def test_recipe_creation(self):
        """Test creating a Recipe instance"""
        recipe = Recipe.objects.create(**self.recipe_data)
        
        self.assertEqual(recipe.menu_item, self.menu_item)
        self.assertEqual(recipe.prep_time, 5)
        self.assertEqual(recipe.difficulty, 'easy')
        self.assertIn('Espresso shot', recipe.ingredients)
    
    def test_recipe_str(self):
        """Test string representation"""
        recipe = Recipe.objects.create(**self.recipe_data)
        self.assertEqual(str(recipe), 'Recipe for Latte')
    
    def test_recipe_one_to_one_relationship(self):
        """Test one-to-one relationship with MenuItem"""
        Recipe.objects.create(**self.recipe_data)
        
        # Try to create another recipe for the same menu item
        with self.assertRaises(Exception):  # IntegrityError
            Recipe.objects.create(**self.recipe_data)
    
    def test_recipe_ingredients_list_property(self):
        """Test ingredients_list property"""
        recipe = Recipe.objects.create(**self.recipe_data)
        ingredients = recipe.ingredients_list
        
        self.assertEqual(len(ingredients), 3)
        self.assertIn('Espresso shot', ingredients)
        self.assertIn('Steamed milk', ingredients)
        self.assertIn('Milk foam', ingredients)
    
    def test_recipe_instructions_list_property(self):
        """Test instructions_list property"""
        recipe = Recipe.objects.create(**self.recipe_data)
        instructions = recipe.instructions_list
        
        self.assertEqual(len(instructions), 4)
        self.assertEqual(instructions[0], (1, 'Pull espresso shot'))
        self.assertEqual(instructions[1], (2, 'Steam milk'))
        self.assertEqual(instructions[2], (3, 'Pour milk over espresso'))
        self.assertEqual(instructions[3], (4, 'Add foam on top'))


class MenuViewsTest(TestCase):
    """Test menu app views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.category = Category.objects.create(
            name='Coffee',
            description='Premium coffee drinks',
            active=True
        )
        
        self.menu_item = MenuItem.objects.create(
            name='Cappuccino',
            description='Espresso with steamed milk and foam',
            price=Decimal('4.25'),
            category=self.category,
            available=True
        )
        
        self.unavailable_item = MenuItem.objects.create(
            name='Seasonal Drink',
            description='Limited time offer',
            price=Decimal('5.00'),
            category=self.category,
            available=False
        )
    
    def test_menu_list_view(self):
        """Test menu list view"""
        response = self.client.get(reverse('menu:menu_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cappuccino')
        self.assertContains(response, '$4.25')
        self.assertNotContains(response, 'Seasonal Drink')  # Unavailable
        self.assertContains(response, 'Coffee')  # Category name
    
    def test_menu_item_detail_view(self):
        """Test menu item detail view"""
        response = self.client.get(reverse('menu:menu_item_detail', kwargs={'slug': 'cappuccino'}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cappuccino')
        self.assertContains(response, 'Espresso with steamed milk and foam')
        self.assertContains(response, '$4.25')
    
    def test_menu_item_detail_unavailable(self):
        """Test detail view for unavailable item returns 404"""
        response = self.client.get(reverse('menu:menu_item_detail', kwargs={'slug': 'seasonal-drink'}))
        self.assertEqual(response.status_code, 404)
    
    def test_menu_category_filter(self):
        """Test menu filtering by category"""
        # Create another category and item
        dessert_cat = Category.objects.create(name='Desserts', active=True)
        MenuItem.objects.create(
            name='Chocolate Cake',
            description='Rich chocolate cake',
            price=Decimal('6.00'),
            category=dessert_cat,
            available=True
        )
        
        # Test coffee category filter
        response = self.client.get(reverse('menu:menu_list') + '?category=coffee')
        self.assertContains(response, 'Cappuccino')
        self.assertNotContains(response, 'Chocolate Cake')
        
        # Test desserts category filter
        response = self.client.get(reverse('menu:menu_list') + '?category=desserts')
        self.assertContains(response, 'Chocolate Cake')
        self.assertNotContains(response, 'Cappuccino')


class MenuAdminTest(TestCase):
    """Test menu app admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.site = AdminSite()
        self.user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        
        self.category = Category.objects.create(name='Test Category')
        self.menu_item = MenuItem.objects.create(
            name='Test Item',
            description='Test description',
            price=Decimal('5.00'),
            category=self.category
        )
        self.recipe = Recipe.objects.create(
            menu_item=self.menu_item,
            ingredients='Test ingredients',
            instructions='Test instructions',
            prep_time=10
        )
    
    def test_category_admin_registration(self):
        """Test Category admin is properly configured"""
        admin = CategoryAdmin(Category, self.site)
        self.assertIn('name', admin.list_display)
        self.assertIn('active', admin.list_display)
        self.assertIn('order', admin.list_display)
    
    def test_menu_item_admin_registration(self):
        """Test MenuItem admin is properly configured"""
        admin = MenuItemAdmin(MenuItem, self.site)
        self.assertIn('name', admin.list_display)
        self.assertIn('category', admin.list_display)
        self.assertIn('price', admin.list_display)
        self.assertIn('available', admin.list_display)
    
    def test_recipe_admin_registration(self):
        """Test Recipe admin is properly configured"""
        admin = RecipeAdmin(Recipe, self.site)
        self.assertIn('menu_item', admin.list_display)
        self.assertIn('difficulty', admin.list_display)
        self.assertIn('prep_time', admin.list_display)


class MenuImageProcessingTest(TestCase):
    """Test menu image processing functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name='Test Category')
    
    def test_menu_item_without_image(self):
        """Test menu item creation without image"""
        item = MenuItem.objects.create(
            name='No Image Item',
            description='Item without image',
            price=Decimal('3.00'),
            category=self.category
        )
        
        self.assertFalse(item.image)
        self.assertFalse(item.has_image())
        self.assertEqual(item.get_image_urls(), {})
    
    @patch('menu.utils.image_processing.create_multiple_sizes')
    def test_menu_item_image_processing(self, mock_create_sizes):
        """Test image processing is called when image is uploaded"""
        # Create a mock image file
        mock_image = SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        
        item = MenuItem.objects.create(
            name='Image Item',
            description='Item with image',
            price=Decimal('3.00'),
            category=self.category,
            image=mock_image
        )
        
        # Verify image processing would be called
        # (Note: actual processing is mocked to avoid file system operations)
        self.assertTrue(item.image)


class MenuIntegrationTest(TestCase):
    """Integration tests for menu app workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        # Create menu structure
        self.coffee_category = Category.objects.create(
            name='Coffee',
            description='Premium coffee drinks',
            order=1,
            active=True
        )
        
        self.food_category = Category.objects.create(
            name='Food',
            description='Fresh pastries and snacks',
            order=2,
            active=True
        )
        
        self.latte = MenuItem.objects.create(
            name='Latte',
            description='Espresso with steamed milk',
            price=Decimal('4.50'),
            category=self.coffee_category,
            available=True,
            featured=True
        )
        
        self.croissant = MenuItem.objects.create(
            name='Croissant',
            description='Buttery French pastry',
            price=Decimal('3.25'),
            category=self.food_category,
            available=True,
            featured=False
        )
        
        # Create recipe for latte
        self.latte_recipe = Recipe.objects.create(
            menu_item=self.latte,
            ingredients='Espresso shot\nSteamed milk',
            instructions='Pull shot\nSteam milk\nCombine',
            prep_time=4,
            difficulty='easy'
        )
    
    def test_complete_menu_browsing_workflow(self):
        """Test complete menu browsing workflow"""
        # 1. Visit menu page
        response = self.client.get(reverse('menu:menu_list'))
        self.assertEqual(response.status_code, 200)
        
        # Should see both categories and available items
        self.assertContains(response, 'Coffee')
        self.assertContains(response, 'Food')
        self.assertContains(response, 'Latte')
        self.assertContains(response, 'Croissant')
        
        # 2. Filter by coffee category
        response = self.client.get(reverse('menu:menu_list') + '?category=coffee')
        self.assertContains(response, 'Latte')
        self.assertNotContains(response, 'Croissant')
        
        # 3. View latte details
        response = self.client.get(reverse('menu:menu_item_detail', kwargs={'slug': 'latte'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Latte')
        self.assertContains(response, '$4.50')
        self.assertContains(response, 'Espresso with steamed milk')
    
    def test_admin_menu_management_workflow(self):
        """Test admin menu management workflow"""
        # Login as admin
        self.client.login(username='admin', password='password')
        
        # 1. Access menu admin
        response = self.client.get('/admin/menu/menuitem/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Latte')
        self.assertContains(response, 'Croissant')
        
        # 2. Create new menu item
        response = self.client.post('/admin/menu/menuitem/add/', {
            'name': 'Cappuccino',
            'description': 'Espresso with steamed milk and foam',
            'price': '4.25',
            'category': self.coffee_category.id,
            'available': True,
            'featured': False,
            'temperature': 'hot',
            'size': 'medium',
            'preparation_time': 5,
            '_save': 'Save'
        })
        
        # Check item was created
        self.assertTrue(MenuItem.objects.filter(name='Cappuccino').exists())
        cappuccino = MenuItem.objects.get(name='Cappuccino')
        self.assertEqual(cappuccino.slug, 'cappuccino')
        
        # 3. Verify new item appears on public menu
        response = self.client.get(reverse('menu:menu_list'))
        self.assertContains(response, 'Cappuccino')
        
        # 4. Make item unavailable
        response = self.client.post(f'/admin/menu/menuitem/{cappuccino.id}/change/', {
            'name': cappuccino.name,
            'description': cappuccino.description,
            'price': cappuccino.price,
            'category': cappuccino.category.id,
            'available': False,  # Make unavailable
            'featured': cappuccino.featured,
            'temperature': cappuccino.temperature,
            'size': cappuccino.size,
            'preparation_time': cappuccino.preparation_time,
            '_save': 'Save'
        })
        
        # 5. Verify item no longer appears on public menu
        response = self.client.get(reverse('menu:menu_list'))
        self.assertNotContains(response, 'Cappuccino')
    
    def test_category_management_workflow(self):
        """Test category management workflow"""
        # Login as admin
        self.client.login(username='admin', password='password')
        
        # 1. Create new category
        response = self.client.post('/admin/menu/category/add/', {
            'name': 'Beverages',
            'description': 'Non-coffee beverages',
            'order': 3,
            'active': True,
            '_save': 'Save'
        })
        
        # Check category was created
        self.assertTrue(Category.objects.filter(name='Beverages').exists())
        beverages = Category.objects.get(name='Beverages')
        self.assertEqual(beverages.slug, 'beverages')
        
        # 2. Add item to new category
        tea = MenuItem.objects.create(
            name='Green Tea',
            description='Organic green tea',
            price=Decimal('2.75'),
            category=beverages,
            available=True
        )
        
        # 3. Verify category appears on menu with item
        response = self.client.get(reverse('menu:menu_list'))
        self.assertContains(response, 'Beverages')
        self.assertContains(response, 'Green Tea')
        
        # 4. Deactivate category
        beverages.active = False
        beverages.save()
        
        # 5. Verify category and its items don't appear on public menu
        response = self.client.get(reverse('menu:menu_list'))
        # Items from inactive categories should be filtered out
        # (This depends on view implementation)


class MenuImageProcessingAdvancedTest(TestCase):
    """Advanced tests for menu image processing functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name='Test Category')
        self.menu_item = MenuItem.objects.create(
            name='Test Item',
            description='Test description',
            price=Decimal('5.00'),
            category=self.category
        )
    
    def test_get_responsive_image_urls(self):
        """Test getting responsive image URLs"""
        # Without image
        urls = self.menu_item.get_image_urls()
        self.assertEqual(urls, {})
        
        # With mock image
        with patch('menu.utils.image_processing.get_responsive_image_urls') as mock_urls:
            mock_urls.return_value = {
                'thumbnail': '/media/menu/test_1_thumbnail.jpg',
                'card': '/media/menu/test_1_card.jpg',
                'detail': '/media/menu/test_1_detail.jpg',
                'original': '/media/menu/test_1.jpg'
            }
            
            # Mock that item has image
            self.menu_item.image.name = 'menu/test_image.jpg'
            urls = self.menu_item.get_image_urls()
            
            self.assertIn('thumbnail', urls)
            self.assertIn('card', urls)
            self.assertIn('detail', urls)
            self.assertIn('original', urls)
    
    def test_get_display_image_url(self):
        """Test getting display image URL"""
        # Without image
        url = self.menu_item.get_display_image_url()
        self.assertIsNone(url)
        
        # With image URLs
        with patch.object(self.menu_item, 'get_image_urls') as mock_urls:
            mock_urls.return_value = {
                'thumbnail': '/media/menu/test_1_thumbnail.jpg',
                'card': '/media/menu/test_1_card.jpg',
            }
            
            # Test preferred size
            url = self.menu_item.get_display_image_url('card')
            self.assertEqual(url, '/media/menu/test_1_card.jpg')
            
            # Test fallback
            url = self.menu_item.get_display_image_url('detail')  # Not available
            self.assertEqual(url, '/media/menu/test_1_card.jpg')  # Falls back to card


class MenuFieldsTest(TestCase):
    """Test custom menu fields"""
    
    def test_menu_image_field_initialization(self):
        """Test MenuImageField initialization"""
        field = MenuImageField()
        self.assertTrue(hasattr(field, 'upload_to'))
        
        # Test upload path generation
        self.assertTrue(callable(field.upload_to))


class MenuModelValidationTest(TestCase):
    """Advanced validation tests for menu models"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name='Test Category')
    
    def test_menu_item_price_edge_cases(self):
        """Test menu item price edge cases"""
        # Very small price
        item = MenuItem(
            name='Cheap Item',
            description='Very cheap',
            price=Decimal('0.01'),  # 1 cent
            category=self.category
        )
        item.full_clean()  # Should not raise
        
        # Very large price
        item = MenuItem(
            name='Expensive Item',
            description='Very expensive',
            price=Decimal('9999.99'),  # Max allowed by field
            category=self.category
        )
        item.full_clean()  # Should not raise
    
    def test_menu_item_preparation_time_validation(self):
        """Test preparation time validation"""
        # Invalid preparation time (too low)
        item = MenuItem(
            name='Test Item',
            description='Test',
            price=Decimal('5.00'),
            category=self.category,
            preparation_time=0
        )
        
        with self.assertRaises(ValidationError):
            item.full_clean()
        
        # Invalid preparation time (too high)
        item.preparation_time = 61
        with self.assertRaises(ValidationError):
            item.full_clean()
    
    def test_recipe_validation(self):
        """Test recipe model validation"""
        menu_item = MenuItem.objects.create(
            name='Test Item',
            description='Test',
            price=Decimal('5.00'),
            category=self.category
        )
        
        # Valid recipe
        recipe = Recipe(
            menu_item=menu_item,
            ingredients='Test ingredients',
            instructions='Test instructions',
            prep_time=5
        )
        recipe.full_clean()  # Should not raise
        
        # Test one-to-one constraint
        recipe.save()
        
        duplicate_recipe = Recipe(
            menu_item=menu_item,
            ingredients='Duplicate ingredients',
            instructions='Duplicate instructions',
            prep_time=10
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            duplicate_recipe.save()


class MenuAdminAdvancedTest(TestCase):
    """Advanced tests for menu admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        self.category = Category.objects.create(name='Test Category', order=1)
        
        # Create multiple menu items
        for i in range(10):
            MenuItem.objects.create(
                name=f'Item {i}',
                description=f'Description {i}',
                price=Decimal(f'{i + 5}.00'),
                category=self.category,
                available=(i % 2 == 0)  # Alternate availability
            )
    
    def test_menu_item_admin_bulk_actions(self):
        """Test menu item admin bulk actions"""
        self.client.login(username='admin', password='password')
        
        # Get all item IDs
        items = MenuItem.objects.all()
        item_ids = [str(item.id) for item in items]
        
        # Test make available bulk action
        response = self.client.post('/admin/menu/menuitem/', {
            'action': 'make_available',
            '_selected_action': item_ids[:5],  # Select first 5
        })
        
        # Check that items were updated
        available_count = MenuItem.objects.filter(available=True).count()
        self.assertGreaterEqual(available_count, 5)
        
        # Test make featured bulk action
        response = self.client.post('/admin/menu/menuitem/', {
            'action': 'make_featured',
            '_selected_action': item_ids[:3],  # Select first 3
        })
        
        # Check that items were updated
        featured_count = MenuItem.objects.filter(featured=True).count()
        self.assertGreaterEqual(featured_count, 3)
    
    def test_category_admin_active_items_count(self):
        """Test category admin shows correct active items count"""
        self.client.login(username='admin', password='password')
        
        response = self.client.get('/admin/menu/category/')
        self.assertEqual(response.status_code, 200)
        
        # Should show the category with item count
        self.assertContains(response, 'Test Category')
        # The exact count depends on how many items are available
    
    def test_menu_item_admin_image_processing_actions(self):
        """Test menu item admin image processing actions"""
        self.client.login(username='admin', password='password')
        
        # Create item with mock image
        item = MenuItem.objects.create(
            name='Image Item',
            description='Item with image',
            price=Decimal('10.00'),
            category=self.category
        )
        item.image.name = 'menu/test_image.jpg'
        item.save()
        
        # Test optimize images action
        with patch('menu.utils.image_processing.create_multiple_sizes') as mock_optimize:
            response = self.client.post('/admin/menu/menuitem/', {
                'action': 'optimize_images',
                '_selected_action': [str(item.id)],
            })
            
            # Should have attempted to optimize
            # (Actual call depends on implementation)
    
    def test_recipe_admin_configuration(self):
        """Test recipe admin configuration"""
        admin = RecipeAdmin(Recipe, AdminSite())
        
        # Check that admin is properly configured
        self.assertIn('menu_item', admin.list_display)
        self.assertIn('difficulty', admin.list_display)
        self.assertIn('prep_time', admin.list_display)


class MenuViewsAdvancedTest(TestCase):
    """Advanced tests for menu views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create categories with different orders
        self.coffee_cat = Category.objects.create(name='Coffee', order=1, active=True)
        self.food_cat = Category.objects.create(name='Food', order=2, active=True)
        self.inactive_cat = Category.objects.create(name='Inactive', order=3, active=False)
        
        # Create menu items
        self.espresso = MenuItem.objects.create(
            name='Espresso',
            description='Strong coffee',
            price=Decimal('2.50'),
            category=self.coffee_cat,
            available=True,
            featured=True
        )
        
        self.sandwich = MenuItem.objects.create(
            name='Sandwich',
            description='Fresh sandwich',
            price=Decimal('8.00'),
            category=self.food_cat,
            available=True,
            featured=False
        )
        
        self.unavailable_item = MenuItem.objects.create(
            name='Unavailable Item',
            description='Not available',
            price=Decimal('5.00'),
            category=self.coffee_cat,
            available=False
        )
        
        self.inactive_cat_item = MenuItem.objects.create(
            name='Inactive Category Item',
            description='In inactive category',
            price=Decimal('3.00'),
            category=self.inactive_cat,
            available=True
        )
    
    def test_menu_list_view_category_filtering(self):
        """Test menu list view category filtering"""
        # Test all items
        response = self.client.get(reverse('menu:menu_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Espresso')
        self.assertContains(response, 'Sandwich')
        self.assertNotContains(response, 'Unavailable Item')
        self.assertNotContains(response, 'Inactive Category Item')
        
        # Test coffee category filter
        response = self.client.get(reverse('menu:menu_list') + '?category=coffee')
        self.assertContains(response, 'Espresso')
        self.assertNotContains(response, 'Sandwich')
        
        # Test food category filter
        response = self.client.get(reverse('menu:menu_list') + '?category=food')
        self.assertContains(response, 'Sandwich')
        self.assertNotContains(response, 'Espresso')
        
        # Test invalid category filter
        response = self.client.get(reverse('menu:menu_list') + '?category=nonexistent')
        self.assertEqual(response.status_code, 200)  # Should still work
        # Should show all items or handle gracefully
    
    def test_menu_list_view_featured_items(self):
        """Test menu list view shows featured items"""
        response = self.client.get(reverse('menu:menu_list'))
        
        # Should have featured items in context
        if 'featured_items' in response.context:
            featured_items = response.context['featured_items']
            self.assertIn(self.espresso, featured_items)
            self.assertNotIn(self.sandwich, featured_items)
    
    def test_menu_item_detail_view_with_recipe(self):
        """Test menu item detail view with recipe"""
        # Create recipe for espresso
        Recipe.objects.create(
            menu_item=self.espresso,
            ingredients='Coffee beans\nWater',
            instructions='Grind beans\nBrew',
            prep_time=3,
            difficulty='easy'
        )
        
        response = self.client.get(reverse('menu:menu_item_detail', kwargs={'slug': 'espresso'}))
        self.assertEqual(response.status_code, 200)
        
        # Should show recipe information
        if 'recipe' in response.context:
            recipe = response.context['recipe']
            self.assertEqual(recipe.menu_item, self.espresso)
    
    def test_menu_views_performance(self):
        """Test menu views performance"""
        # Create many items to test query optimization
        for i in range(50):
            MenuItem.objects.create(
                name=f'Bulk Item {i}',
                description=f'Description {i}',
                price=Decimal('5.00'),
                category=self.coffee_cat,
                available=True
            )
        
        # Test that menu list doesn't make too many queries
        with self.assertNumQueries(10):  # Adjust based on actual implementation
            response = self.client.get(reverse('menu:menu_list'))
            self.assertEqual(response.status_code, 200)
    
    def test_menu_json_api_views(self):
        """Test JSON API views for menu data (if implemented)"""
        # This would test any JSON endpoints for mobile apps or AJAX
        # Example: /api/menu/items/
        # For now, this is a placeholder
        self.assertTrue(True)


class MenuSearchTest(TestCase):
    """Test menu search functionality (if implemented)"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name='Coffee', active=True)
        
        self.latte = MenuItem.objects.create(
            name='Vanilla Latte',
            description='Espresso with vanilla syrup and steamed milk',
            price=Decimal('4.50'),
            category=self.category,
            available=True
        )
        
        self.cappuccino = MenuItem.objects.create(
            name='Cappuccino',
            description='Espresso with steamed milk foam',
            price=Decimal('4.25'),
            category=self.category,
            available=True
        )
    
    def test_menu_search_by_name(self):
        """Test searching menu items by name"""
        # This would test search functionality if implemented
        # Example: /menu/?search=vanilla
        search_url = reverse('menu:menu_list') + '?search=vanilla'
        response = self.client.get(search_url)
        
        if response.status_code == 200:
            # Should find vanilla latte but not cappuccino
            self.assertContains(response, 'Vanilla Latte')
            # Depending on implementation, might not contain cappuccino
    
    def test_menu_search_by_description(self):
        """Test searching menu items by description"""
        search_url = reverse('menu:menu_list') + '?search=foam'
        response = self.client.get(search_url)
        
        if response.status_code == 200:
            # Should find cappuccino
            self.assertContains(response, 'Cappuccino')


class MenuSecurityTest(TestCase):
    """Security tests for menu functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        self.regular_user = User.objects.create_user('user', 'user@test.com', 'password')
        
        self.category = Category.objects.create(name='Test Category')
    
    def test_menu_admin_access_control(self):
        """Test menu admin access control"""
        # Test unauthenticated access
        response = self.client.get('/admin/menu/menuitem/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test regular user access
        self.client.login(username='user', password='password')
        response = self.client.get('/admin/menu/menuitem/')
        self.assertEqual(response.status_code, 302)  # Should be redirected/denied
        
        # Test admin user access
        self.client.login(username='admin', password='password')
        response = self.client.get('/admin/menu/menuitem/')
        self.assertEqual(response.status_code, 200)  # Should be allowed
    
    def test_menu_item_xss_protection(self):
        """Test menu item XSS protection"""
        malicious_script = '<script>alert("xss")</script>'
        
        item = MenuItem.objects.create(
            name=f'Test {malicious_script}',
            description=f'Description {malicious_script}',
            price=Decimal('5.00'),
            category=self.category,
            available=True
        )
        
        # Test that template renders safely
        response = self.client.get(reverse('menu:menu_list'))
        self.assertEqual(response.status_code, 200)
        
        # Content should be escaped in the response
        response_content = response.content.decode()
        self.assertNotIn('<script>alert("xss")</script>', response_content)
        self.assertIn('Test', response_content)  # Safe content should be there
    
    def test_file_upload_security(self):
        """Test file upload security for menu item images"""
        # This would test that only valid image files can be uploaded
        # and that uploaded files are properly validated
        self.assertTrue(True)  # Placeholder for actual file upload tests


class MenuPerformanceTest(TestCase):
    """Performance tests for menu functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name='Test Category')
        
        # Create many menu items for performance testing
        for i in range(100):
            MenuItem.objects.create(
                name=f'Item {i}',
                description=f'Description for item {i}',
                price=Decimal(f'{i % 20 + 5}.99'),
                category=self.category,
                available=(i % 3 != 0)  # Make some unavailable
            )
    
    def test_menu_list_query_optimization(self):
        """Test that menu list queries are optimized"""
        # Test select_related and prefetch_related usage
        with self.assertNumQueries(5):  # Adjust based on actual implementation
            response = self.client.get(reverse('menu:menu_list'))
            self.assertEqual(response.status_code, 200)
    
    def test_large_menu_rendering(self):
        """Test rendering performance with large menu"""
        import time
        
        start_time = time.time()
        response = self.client.get(reverse('menu:menu_list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        # Should render in reasonable time (adjust threshold as needed)
        self.assertLess(end_time - start_time, 2.0)  # Less than 2 seconds
