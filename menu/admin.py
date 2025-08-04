from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from .models import Category, MenuItem, Recipe
from .fields import MenuImageFormField, MenuImageWidget

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for menu categories
    """
    list_display = ('name', 'order', 'active_items_count', 'active', 'created_at')
    list_editable = ('order', 'active')
    list_filter = ('active', 'created_at')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'slug')
        }),
        ('Display Settings', {
            'fields': ('order', 'active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    
    def active_items_count(self, obj):
        """Show count of active items in category"""
        count = obj.active_items_count
        if count == 0:
            return format_html('<span style="color: #999;">0 items</span>')
        return format_html('<strong>{} items</strong>', count)
    active_items_count.short_description = 'Active Items'


class MenuItemAdminForm(forms.ModelForm):
    """
    Custom form for MenuItem admin with enhanced image handling.
    """
    image = MenuImageFormField(
        required=False,
        widget=MenuImageWidget(),
    )
    
    class Meta:
        model = MenuItem
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful text to various fields
        self.fields['name'].widget.attrs.update({
            'placeholder': 'e.g., Vanilla Latte, Chocolate Croissant'
        })
        self.fields['description'].widget.attrs.update({
            'rows': 4,
            'placeholder': 'Describe the item, its ingredients, and what makes it special...'
        })
        self.fields['price'].widget.attrs.update({
            'placeholder': '4.95'
        })
        self.fields['dietary_notes'].widget.attrs.update({
            'placeholder': 'e.g., Vegan, Gluten-Free, Contains Nuts'
        })


class RecipeInline(admin.StackedInline):
    """
    Inline admin for recipes within menu items
    """
    model = Recipe
    extra = 0
    fieldsets = (
        ('Recipe Details', {
            'fields': ('ingredients', 'instructions')
        }),
        ('Preparation Info', {
            'fields': ('prep_time', 'difficulty', 'yield_quantity')
        }),
        ('Additional Information', {
            'fields': ('equipment_needed', 'notes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """
    Admin interface for menu items with enhanced image handling
    """
    form = MenuItemAdminForm
    
    list_display = (
        'name', 
        'category', 
        'display_price', 
        'available', 
        'featured',
        'contains_caffeine',
        'enhanced_image_preview',
        'image_status',
        'updated_at'
    )
    
    list_editable = ('available', 'featured')
    
    list_filter = (
        'category', 
        'available', 
        'featured',
        'contains_caffeine',
        'temperature',
        'size',
        'created_at'
    )
    
    search_fields = ('name', 'description', 'dietary_notes')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'slug')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'available', 'featured')
        }),
        ('Product Details', {
            'fields': ('temperature', 'size', 'calories', 'contains_caffeine', 'dietary_notes')
        }),
        ('Operations', {
            'fields': ('preparation_time',)
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    
    inlines = [RecipeInline]
    
    # Bulk actions
    actions = [
        'make_available', 
        'make_unavailable', 
        'make_featured', 
        'remove_featured',
        'generate_placeholders',
        'optimize_images'
    ]
    
    def display_price(self, obj):
        """Format price for display"""
        return obj.display_price
    display_price.short_description = 'Price'
    display_price.admin_order_field = 'price'
    
    def enhanced_image_preview(self, obj):
        """Enhanced image preview with multiple sizes and status"""
        if obj.image:
            # Get the best available image URL
            display_url = obj.get_display_image_url('thumbnail') or obj.image.url
            
            # Check if it's a real image or placeholder
            is_placeholder = not obj.has_image()
            border_color = '#ffc107' if is_placeholder else '#28a745'
            
            return format_html(
                '<div style="position: relative;">'
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px; border: 2px solid {};" />'
                '{}'
                '</div>',
                display_url,
                border_color,
                '<div style="position: absolute; bottom: -2px; right: -2px; background: #ffc107; color: #000; '
                'font-size: 10px; padding: 1px 3px; border-radius: 2px;">P</div>' if is_placeholder else ''
            )
        return format_html('<span style="color: #999;">No image</span>')
    enhanced_image_preview.short_description = 'Image'
    
    def image_status(self, obj):
        """Show image status and information"""
        if not obj.image:
            return format_html('<span style="color: #dc3545;">No image</span>')
        
        if obj.has_image():
            # Check if multiple sizes exist
            image_urls = obj.get_image_urls()
            size_count = len(image_urls)
            
            if size_count > 1:
                return format_html(
                    '<span style="color: #28a745;" title="Original + {} optimized sizes">✓ Optimized</span>',
                    size_count - 1
                )
            else:
                return format_html('<span style="color: #17a2b8;" title="Original only">✓ Original</span>')
        else:
            return format_html('<span style="color: #ffc107;" title="Placeholder image">⚠ Placeholder</span>')
    
    image_status.short_description = 'Status'
    
    def make_available(self, request, queryset):
        """Bulk action to make items available"""
        updated = queryset.update(available=True)
        self.message_user(request, f'{updated} items marked as available.')
    make_available.short_description = "Mark selected items as available"
    
    def make_unavailable(self, request, queryset):
        """Bulk action to make items unavailable"""
        updated = queryset.update(available=False)
        self.message_user(request, f'{updated} items marked as unavailable.')
    make_unavailable.short_description = "Mark selected items as unavailable"
    
    def make_featured(self, request, queryset):
        """Bulk action to feature items"""
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} items marked as featured.')
    make_featured.short_description = "Mark selected items as featured"
    
    def remove_featured(self, request, queryset):
        """Bulk action to remove featured status"""
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} items removed from featured.')
    remove_featured.short_description = "Remove featured status from selected items"
    
    def generate_placeholders(self, request, queryset):
        """Bulk action to generate placeholder images for items without images"""
        from .utils.image_processing import ensure_placeholder_exists
        
        created_count = 0
        error_count = 0
        
        for item in queryset.filter(image=''):
            try:
                if ensure_placeholder_exists(item):
                    item.save(update_fields=['image'])
                    created_count += 1
            except Exception as e:
                error_count += 1
        
        if created_count > 0:
            self.message_user(request, f'Generated {created_count} placeholder images.')
        if error_count > 0:
            self.message_user(request, f'Failed to generate {error_count} placeholders.', level='warning')
        if created_count == 0 and error_count == 0:
            self.message_user(request, 'No items need placeholder images.')
    
    generate_placeholders.short_description = "Generate placeholder images for items without images"
    
    def optimize_images(self, request, queryset):
        """Bulk action to optimize existing images and create multiple sizes"""
        from .utils.image_processing import create_multiple_sizes
        
        optimized_count = 0
        error_count = 0
        
        for item in queryset.exclude(image=''):
            try:
                if item.image and item.has_image():
                    # Create multiple sizes if they don't exist
                    base_name = f"{item.slug}_{item.pk}"
                    create_multiple_sizes(item.image, base_name)
                    optimized_count += 1
            except Exception as e:
                error_count += 1
        
        if optimized_count > 0:
            self.message_user(request, f'Optimized {optimized_count} images.')
        if error_count > 0:
            self.message_user(request, f'Failed to optimize {error_count} images.', level='warning')
        if optimized_count == 0 and error_count == 0:
            self.message_user(request, 'No images need optimization.')
    
    optimize_images.short_description = "Optimize images and create multiple sizes"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Admin interface for standalone recipe management
    """
    list_display = ('menu_item', 'prep_time', 'difficulty', 'yield_quantity', 'updated_at')
    list_filter = ('difficulty', 'prep_time', 'updated_at')
    search_fields = ('menu_item__name', 'ingredients', 'instructions')
    
    fieldsets = (
        ('Menu Item', {
            'fields': ('menu_item',)
        }),
        ('Recipe Details', {
            'fields': ('ingredients', 'instructions')
        }),
        ('Preparation Information', {
            'fields': ('prep_time', 'difficulty', 'yield_quantity')
        }),
        ('Additional Information', {
            'fields': ('equipment_needed', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form to show ingredients and instructions as textareas"""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['ingredients'].widget.attrs.update({
            'rows': 10,
            'placeholder': 'Enter ingredients, one per line:\n\n• 2 shots espresso\n• 8 oz steamed milk\n• 1 tsp vanilla syrup\n• Cinnamon for dusting'
        })
        form.base_fields['instructions'].widget.attrs.update({
            'rows': 10,
            'placeholder': 'Enter step-by-step instructions:\n\n1. Pull 2 shots of espresso into cup\n2. Steam milk to 150-160°F\n3. Add vanilla syrup to espresso\n4. Pour steamed milk creating latte art\n5. Dust with cinnamon'
        })
        return form

# Custom admin site configuration for better organization
class MenuAdminSite(admin.AdminSite):
    """Custom admin site for menu-specific administration"""
    site_header = "White Raven Menu Administration"
    site_title = "Menu Admin"
    index_title = "Menu Management"

# Create menu-specific admin site instance (optional - can be used for separate menu admin)
menu_admin_site = MenuAdminSite(name='menu_admin')