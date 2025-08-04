from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from .fields import MenuImageField
from .utils.image_processing import (
    cleanup_old_images, 
    create_multiple_sizes, 
    get_responsive_image_urls,
    ensure_placeholder_exists
)
import logging

logger = logging.getLogger(__name__)

class Category(models.Model):
    """
    Menu categories for organizing menu items (e.g., Coffee, Food, Desserts)
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Category name (e.g., 'Coffee', 'Food', 'Desserts')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Optional description of this category"
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order on menu (lower numbers appear first)"
    )
    
    active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this category from the public menu"
    )
    
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the name (auto-generated)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def active_items_count(self):
        """Return count of active menu items in this category"""
        return self.menuitem_set.filter(available=True).count()


class MenuItem(models.Model):
    """
    Individual menu items with pricing and details
    """
    TEMPERATURE_CHOICES = [
        ('hot', 'Hot'),
        ('cold', 'Cold'),
        ('both', 'Hot & Cold'),
        ('room', 'Room Temperature'),
    ]
    
    SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('xl', 'Extra Large'),
        ('one_size', 'One Size'),
    ]
    
    name = models.CharField(
        max_length=100,
        help_text="Menu item name"
    )
    
    description = models.TextField(
        help_text="Description of the item, ingredients, etc."
    )
    
    price = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price in dollars (e.g., 4.95)"
    )
    
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        help_text="Which category this item belongs to"
    )
    
    available = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this item from the public menu"
    )
    
    featured = models.BooleanField(
        default=False,
        help_text="Check to feature this item on the homepage"
    )
    
    image = MenuImageField(
        blank=True,
        help_text="Upload an image for this menu item. Images will be automatically optimized for web display."
    )
    
    temperature = models.CharField(
        max_length=10,
        choices=TEMPERATURE_CHOICES,
        default='both',
        help_text="Temperature options for this item"
    )
    
    size = models.CharField(
        max_length=10,
        choices=SIZE_CHOICES,
        default='one_size',
        help_text="Size options for this item"
    )
    
    calories = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Calories per serving (optional)"
    )
    
    contains_caffeine = models.BooleanField(
        default=False,
        help_text="Check if this item contains caffeine"
    )
    
    dietary_notes = models.CharField(
        max_length=200,
        blank=True,
        help_text="Dietary information (e.g., 'Vegan', 'Gluten-Free', 'Contains Nuts')"
    )
    
    preparation_time = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        help_text="Estimated preparation time in minutes"
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the name (auto-generated)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ['category__order', 'name']
    
    def __str__(self):
        return f"{self.name} (${self.price})"
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided and handle image processing"""
        # Store old image path for cleanup
        old_image_path = None
        if self.pk:
            try:
                old_instance = MenuItem.objects.get(pk=self.pk)
                old_image_path = old_instance.image.name if old_instance.image else None
            except MenuItem.DoesNotExist:
                pass
        
        # Auto-generate slug from name if not provided
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while MenuItem.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Save the instance first
        super().save(*args, **kwargs)
        
        # Handle image processing after save (when we have an ID)
        if self.image and hasattr(self.image, '_file'):
            try:
                # Create multiple image sizes for responsive display
                base_name = f"{self.slug}_{self.pk}"
                create_multiple_sizes(self.image._file, base_name)
                
                # Clean up old images if they exist and are different
                if old_image_path and old_image_path != self.image.name:
                    cleanup_old_images(old_image_path)
                    
            except Exception as e:
                logger.error(f"Error processing images for menu item {self.pk}: {e}")
        
        # Ensure placeholder exists if no image (optional)
        # Uncomment the line below if you want automatic placeholder generation
        # elif not self.image:
        #     ensure_placeholder_exists(self)
    
    @property
    def display_price(self):
        """Format price for display"""
        return f"${self.price:.2f}"
    
    @property
    def is_drink(self):
        """Check if item is in a drink category"""
        drink_categories = ['coffee', 'tea', 'drinks', 'beverages']
        return self.category.slug.lower() in drink_categories
    
    def get_image_urls(self, create_placeholder=False):
        """
        Get responsive image URLs for this menu item.
        
        Args:
            create_placeholder: bool, whether to create placeholder if no image exists
            
        Returns:
            dict: Dictionary with image URLs for different sizes
        """
        if self.image:
            return get_responsive_image_urls(self.image)
        elif create_placeholder:
            # Try to ensure placeholder exists
            if ensure_placeholder_exists(self):
                return get_responsive_image_urls(self.image)
        
        return {}
    
    def get_display_image_url(self, size='card'):
        """
        Get the best image URL for display purposes.
        
        Args:
            size: str, preferred size ('thumbnail', 'card', 'detail', 'original')
            
        Returns:
            str: Image URL or None if no image available
        """
        image_urls = self.get_image_urls()
        
        if not image_urls:
            return None
        
        # Return preferred size if available, fall back to others
        preferred_order = [size, 'card', 'detail', 'original', 'thumbnail']
        
        for preferred_size in preferred_order:
            if preferred_size in image_urls:
                return image_urls[preferred_size]
        
        # Return any available URL
        return next(iter(image_urls.values()), None)
    
    def has_image(self):
        """Check if this menu item has an image (not placeholder)"""
        if not self.image:
            return False
        
        # Check if it's a placeholder by looking at the path
        return 'placeholder' not in self.image.name.lower()
    
    def delete(self, *args, **kwargs):
        """Custom delete to clean up image files"""
        if self.image:
            try:
                cleanup_old_images(self.image.name)
            except Exception as e:
                logger.warning(f"Could not clean up images for menu item {self.pk}: {e}")
        
        super().delete(*args, **kwargs)


class Recipe(models.Model):
    """
    Recipes and preparation instructions for menu items
    """
    menu_item = models.OneToOneField(
        MenuItem, 
        on_delete=models.CASCADE,
        help_text="The menu item this recipe is for"
    )
    
    ingredients = models.TextField(
        help_text="List of ingredients with quantities (one per line)"
    )
    
    instructions = models.TextField(
        help_text="Step-by-step preparation instructions"
    )
    
    prep_time = models.PositiveIntegerField(
        help_text="Preparation time in minutes"
    )
    
    difficulty = models.CharField(
        max_length=10,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        default='easy',
        help_text="Difficulty level for staff"
    )
    
    equipment_needed = models.TextField(
        blank=True,
        help_text="Special equipment or tools needed (optional)"
    )
    
    yield_quantity = models.CharField(
        max_length=50,
        default='1 serving',
        help_text="How much this recipe makes (e.g., '1 serving', '2 cups')"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes, tips, or variations"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
    
    def __str__(self):
        return f"Recipe for {self.menu_item.name}"
    
    @property
    def ingredients_list(self):
        """Return ingredients as a list"""
        return [ingredient.strip() for ingredient in self.ingredients.split('\n') if ingredient.strip()]
    
    @property
    def instructions_list(self):
        """Return instructions as a numbered list"""
        instructions = [instruction.strip() for instruction in self.instructions.split('\n') if instruction.strip()]
        return [(i+1, instruction) for i, instruction in enumerate(instructions)]