from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
import json
import os

register = template.Library()


@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """Calculate percentage."""
    try:
        if total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def chart_color(index):
    """Generate chart colors based on index."""
    colors = [
        '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
        '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6366F1'
    ]
    return colors[index % len(colors)]


@register.filter
def json_script(value):
    """Convert Python object to JSON for use in JavaScript."""
    return mark_safe(json.dumps(value))


@register.simple_tag
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    return dictionary.get(key)


@register.filter
def range_filter(value):
    """Create a range for iteration in templates."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)


@register.filter
def subtract(value, arg):
    """Subtract arg from value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def add_class(field, css_class):
    """Add CSS class to form field."""
    return field.as_widget(attrs={'class': css_class})


@register.filter
def truncate_chars(value, length):
    """Truncate string to specified length."""
    if len(str(value)) > length:
        return str(value)[:length] + '...'
    return str(value)


@register.filter
def days_until(date):
    """Calculate days until a date."""
    from django.utils import timezone
    from datetime import timedelta
    
    if not date:
        return None
    
    now = timezone.now().date()
    if hasattr(date, 'date'):
        date = date.date()
    
    delta = date - now
    return delta.days


@register.filter
def is_overdue(date):
    """Check if a date is overdue."""
    from django.utils import timezone
    
    if not date:
        return False
    
    now = timezone.now()
    if hasattr(date, 'date'):
        return date < now
    return date < now.date()


@register.inclusion_tag('library/components/status_badge.html')
def status_badge(status, item_type='loan'):
    """Render a status badge component."""
    status_configs = {
        'loan': {
            'active': {'class': 'bg-blue-100 text-blue-800', 'icon': 'fas fa-clock'},
            'returned': {'class': 'bg-green-100 text-green-800', 'icon': 'fas fa-check'},
            'overdue': {'class': 'bg-red-100 text-red-800', 'icon': 'fas fa-exclamation-triangle'},
        },
        'book': {
            'available': {'class': 'bg-green-100 text-green-800', 'icon': 'fas fa-check-circle'},
            'borrowed': {'class': 'bg-yellow-100 text-yellow-800', 'icon': 'fas fa-clock'},
            'reserved': {'class': 'bg-blue-100 text-blue-800', 'icon': 'fas fa-bookmark'},
            'maintenance': {'class': 'bg-red-100 text-red-800', 'icon': 'fas fa-tools'},
        },
        'user': {
            'active': {'class': 'bg-green-100 text-green-800', 'icon': 'fas fa-check-circle'},
            'inactive': {'class': 'bg-red-100 text-red-800', 'icon': 'fas fa-times-circle'},
        }
    }
    
    config = status_configs.get(item_type, {}).get(status, {
        'class': 'bg-gray-100 text-gray-800',
        'icon': 'fas fa-question'
    })
    
    return {
        'status': status,
        'css_class': config['class'],
        'icon': config['icon']
    }


@register.filter
def cloudinary_url(image_field):
    """Convert image field to proper Cloudinary URL"""
    if not image_field:
        return ''

    # Get the image path
    image_path = str(image_field)

    # If it's already a full URL, return as is
    if image_path.startswith('http'):
        return image_path

    # If it's a local path, convert to Cloudinary URL
    if image_path.startswith('book_covers/') or image_path.startswith('library_logos/'):
        # Extract filename without extension
        filename = os.path.basename(image_path)
        name_without_ext = os.path.splitext(filename)[0]

        # Determine folder
        if image_path.startswith('book_covers/'):
            folder = 'book_covers'
        else:
            folder = 'library_logos'

        # Return Cloudinary URL
        cloud_name = getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME', 'ds5udo8jc')
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{folder}/{name_without_ext}.jpg"

    # Fallback to original URL
    try:
        return image_field.url
    except:
        return ''
