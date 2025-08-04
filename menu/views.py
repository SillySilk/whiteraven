from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min, Max
from django.http import JsonResponse
from .models import Category, MenuItem
from core.models import BusinessInfo
import re

def group_menu_items_by_base_name(menu_items):
    """
    Group menu items by their base name (without size info)
    Returns list of grouped items with size variations
    """
    grouped_items = {}
    
    for item in menu_items:
        # Extract base name by removing size info in parentheses
        base_name = re.sub(r'\s*\([^)]*\)\s*$', '', item.name).strip()
        
        if base_name not in grouped_items:
            # Create new group with the first item's info
            grouped_items[base_name] = {
                'base_name': base_name,
                'description': item.description,
                'category': item.category,
                'image': item.image,
                'contains_caffeine': item.contains_caffeine,
                'temperature': item.temperature,
                'dietary_notes': item.dietary_notes,
                'preparation_time': item.preparation_time,
                'featured': item.featured,
                'slug': item.slug,  # Use first item's slug
                'calories': item.calories,
                'sizes': []
            }
        
        # Extract size from item name or use "Standard" if no size found
        size_match = re.search(r'\(([^)]+)\)', item.name)
        size = size_match.group(1) if size_match else "Standard"
        
        # Add size and price info
        grouped_items[base_name]['sizes'].append({
            'size': size,
            'price': item.price,
            'display_price': item.display_price
        })
    
    # Sort sizes by price for each item and set display price
    for item_data in grouped_items.values():
        item_data['sizes'].sort(key=lambda x: x['price'])
        
        # Set the lowest price as the "starting from" price
        if item_data['sizes']:
            if len(item_data['sizes']) > 1:
                item_data['price_display'] = f"From {item_data['sizes'][0]['display_price']}"
            else:
                item_data['price_display'] = item_data['sizes'][0]['display_price']
    
    return list(grouped_items.values())


def menu_list(request):
    """
    Menu page view displaying all available menu items organized by category
    with advanced search and filtering capabilities
    """
    # Get business info for context
    try:
        business_info = BusinessInfo.objects.first()
    except BusinessInfo.DoesNotExist:
        business_info = None
    
    # Get filter parameters
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')
    temperature_filter = request.GET.get('temperature')
    caffeine_filter = request.GET.get('caffeine')
    dietary_filter = request.GET.get('dietary')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    sort_by = request.GET.get('sort', 'category')
    
    # Get all active categories with available items
    categories = Category.objects.filter(
        active=True,
        menuitem__available=True
    ).distinct().order_by('order', 'name')
    
    # Build the queryset for menu items
    menu_items = MenuItem.objects.filter(
        available=True,
        category__active=True
    ).select_related('category')
    
    # Apply category filter if specified
    selected_category = None
    if category_filter:
        try:
            selected_category = Category.objects.get(slug=category_filter, active=True)
            menu_items = menu_items.filter(category=selected_category)
        except Category.DoesNotExist:
            pass
    
    # Apply search filter if specified
    if search_query:
        menu_items = menu_items.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(dietary_notes__icontains=search_query)
        )
    
    # Apply temperature filter
    if temperature_filter and temperature_filter != 'all':
        if temperature_filter == 'hot':
            menu_items = menu_items.filter(Q(temperature='hot') | Q(temperature='both'))
        elif temperature_filter == 'cold':
            menu_items = menu_items.filter(Q(temperature='cold') | Q(temperature='both'))
        else:
            menu_items = menu_items.filter(temperature=temperature_filter)
    
    # Apply caffeine filter
    if caffeine_filter and caffeine_filter != 'all':
        if caffeine_filter == 'with':
            menu_items = menu_items.filter(contains_caffeine=True)
        elif caffeine_filter == 'without':
            menu_items = menu_items.filter(contains_caffeine=False)
    
    # Apply dietary filter
    if dietary_filter and dietary_filter != 'all':
        dietary_keywords = {
            'vegan': ['vegan'],
            'vegetarian': ['vegetarian', 'veggie'],
            'gluten_free': ['gluten-free', 'gluten free'],
            'dairy_free': ['dairy-free', 'dairy free', 'lactose free'],
            'sugar_free': ['sugar-free', 'sugar free', 'no sugar'],
            'keto': ['keto', 'ketogenic', 'low carb']
        }
        
        if dietary_filter in dietary_keywords:
            dietary_q = Q()
            for keyword in dietary_keywords[dietary_filter]:
                dietary_q |= Q(dietary_notes__icontains=keyword)
            menu_items = menu_items.filter(dietary_q)
    
    # Apply price range filters
    if price_min:
        try:
            menu_items = menu_items.filter(price__gte=float(price_min))
        except ValueError:
            pass
    
    if price_max:
        try:
            menu_items = menu_items.filter(price__lte=float(price_max))
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'name':
        menu_items = menu_items.order_by('name')
    elif sort_by == 'price_low':
        menu_items = menu_items.order_by('price', 'name')
    elif sort_by == 'price_high':
        menu_items = menu_items.order_by('-price', 'name')
    elif sort_by == 'newest':
        menu_items = menu_items.order_by('-created_at', 'name')
    else:  # Default to category ordering
        menu_items = menu_items.order_by('category__order', 'name')
    
    # Group menu items by category for display (preserve sort order within categories)
    menu_by_category = {}
    if sort_by == 'category':
        # Group by category when using category sort
        for item in menu_items:
            category_name = item.category.name
            if category_name not in menu_by_category:
                menu_by_category[category_name] = []
            menu_by_category[category_name].append(item)
        
        # Apply grouping to each category
        for category_name, items in menu_by_category.items():
            menu_by_category[category_name] = group_menu_items_by_base_name(items)
    else:
        # Show all items in one group when using other sorts
        if menu_items:
            menu_by_category['Search Results'] = group_menu_items_by_base_name(list(menu_items))
    
    # Get filter options for the template
    temperature_options = MenuItem.TEMPERATURE_CHOICES
    dietary_options = [
        ('vegan', 'Vegan'),
        ('vegetarian', 'Vegetarian'),
        ('gluten_free', 'Gluten-Free'),
        ('dairy_free', 'Dairy-Free'),
        ('sugar_free', 'Sugar-Free'),
        ('keto', 'Keto/Low Carb'),
    ]
    
    # Get price range for the slider
    all_items = MenuItem.objects.filter(available=True, category__active=True)
    min_price = all_items.aggregate(min_price=Min('price'))['min_price'] or 0
    max_price = all_items.aggregate(max_price=Max('price'))['max_price'] or 20
    
    context = {
        'business_info': business_info,
        'categories': categories,
        'menu_by_category': menu_by_category,
        'selected_category': selected_category,
        'search_query': search_query,
        'temperature_filter': temperature_filter,
        'caffeine_filter': caffeine_filter,
        'dietary_filter': dietary_filter,
        'price_min': price_min,
        'price_max': price_max,
        'sort_by': sort_by,
        'temperature_options': temperature_options,
        'dietary_options': dietary_options,
        'min_price': min_price,
        'max_price': max_price,
        'page_title': 'Our Menu',
        'total_items': menu_items.count(),
    }
    
    return render(request, 'menu/menu_list.html', context)


def menu_item_detail(request, slug):
    """
    Detailed view for a specific menu item
    """
    menu_item = get_object_or_404(
        MenuItem, 
        slug=slug, 
        available=True,
        category__active=True
    )
    
    # Get business info for context
    try:
        business_info = BusinessInfo.objects.first()
    except BusinessInfo.DoesNotExist:
        business_info = None
    
    # Get related items from the same category
    related_items = MenuItem.objects.filter(
        category=menu_item.category,
        available=True
    ).exclude(pk=menu_item.pk)[:4]  # Limit to 4 related items
    
    context = {
        'business_info': business_info,
        'menu_item': menu_item,
        'related_items': related_items,
        'page_title': f'{menu_item.name} - Menu',
    }
    
    return render(request, 'menu/menu_item_detail.html', context)


def menu_filter_ajax(request):
    """
    AJAX endpoint for live filtering of menu items
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    # Get filter parameters
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')
    temperature_filter = request.GET.get('temperature')
    caffeine_filter = request.GET.get('caffeine')
    dietary_filter = request.GET.get('dietary')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    
    # Build the queryset for menu items
    menu_items = MenuItem.objects.filter(
        available=True,
        category__active=True
    ).select_related('category')
    
    # Apply filters (same logic as menu_list view)
    if category_filter and category_filter != 'all':
        try:
            category = Category.objects.get(slug=category_filter, active=True)
            menu_items = menu_items.filter(category=category)
        except Category.DoesNotExist:
            pass
    
    if search_query:
        menu_items = menu_items.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(dietary_notes__icontains=search_query)
        )
    
    if temperature_filter and temperature_filter != 'all':
        if temperature_filter == 'hot':
            menu_items = menu_items.filter(Q(temperature='hot') | Q(temperature='both'))
        elif temperature_filter == 'cold':
            menu_items = menu_items.filter(Q(temperature='cold') | Q(temperature='both'))
        else:
            menu_items = menu_items.filter(temperature=temperature_filter)
    
    if caffeine_filter and caffeine_filter != 'all':
        if caffeine_filter == 'with':
            menu_items = menu_items.filter(contains_caffeine=True)
        elif caffeine_filter == 'without':
            menu_items = menu_items.filter(contains_caffeine=False)
    
    if dietary_filter and dietary_filter != 'all':
        dietary_keywords = {
            'vegan': ['vegan'],
            'vegetarian': ['vegetarian', 'veggie'],
            'gluten_free': ['gluten-free', 'gluten free'],
            'dairy_free': ['dairy-free', 'dairy free', 'lactose free'],
            'sugar_free': ['sugar-free', 'sugar free', 'no sugar'],
            'keto': ['keto', 'ketogenic', 'low carb']
        }
        
        if dietary_filter in dietary_keywords:
            dietary_q = Q()
            for keyword in dietary_keywords[dietary_filter]:
                dietary_q |= Q(dietary_notes__icontains=keyword)
            menu_items = menu_items.filter(dietary_q)
    
    if price_min:
        try:
            menu_items = menu_items.filter(price__gte=float(price_min))
        except ValueError:
            pass
    
    if price_max:
        try:
            menu_items = menu_items.filter(price__lte=float(price_max))
        except ValueError:
            pass
    
    # Prepare JSON response
    items_data = []
    for item in menu_items.order_by('category__order', 'name'):
        items_data.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': str(item.price),
            'display_price': item.display_price,
            'category': item.category.name,
            'image_url': item.image.url if item.image else None,
            'contains_caffeine': item.contains_caffeine,
            'temperature': item.get_temperature_display(),
            'size': item.get_size_display(),
            'dietary_notes': item.dietary_notes,
            'preparation_time': item.preparation_time,
            'calories': item.calories,
            'slug': item.slug,
        })
    
    return JsonResponse({
        'items': items_data,
        'total_count': len(items_data)
    })
