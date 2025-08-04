#!/usr/bin/env python
"""
Helper function to group menu items by base name for cleaner display
This avoids database changes by processing the data in the view
"""

import re
from decimal import Decimal

def group_menu_items_by_base_name(menu_items):
    """
    Group menu items by their base name (without size info)
    Returns dict with base names as keys and item info + size variations
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
    
    # Sort sizes by price for each item
    for item_data in grouped_items.values():
        item_data['sizes'].sort(key=lambda x: x['price'])
        
        # Set the lowest price as the "starting from" price
        if item_data['sizes']:
            item_data['starting_price'] = item_data['sizes'][0]['display_price']
            item_data['price_range'] = f"${item_data['sizes'][0]['price']}" + (
                f" - ${item_data['sizes'][-1]['price']}" if len(item_data['sizes']) > 1 else ""
            )
    
    return list(grouped_items.values())

def get_grouped_menu_by_category(menu_items_queryset):
    """
    Get menu items grouped by category, with items grouped by base name
    """
    menu_by_category = {}
    
    for item in menu_items_queryset:
        category_name = item.category.name
        if category_name not in menu_by_category:
            menu_by_category[category_name] = []
        menu_by_category[category_name].append(item)
    
    # Group items within each category
    grouped_menu = {}
    for category_name, items in menu_by_category.items():
        grouped_menu[category_name] = group_menu_items_by_base_name(items)
    
    return grouped_menu

# Example usage in views.py:
"""
# In menu_list view, replace the menu_by_category logic with:
from .group_menu_items import get_grouped_menu_by_category

grouped_menu = get_grouped_menu_by_category(menu_items)
context['menu_by_category'] = grouped_menu
"""