from django import template
from library.models import LibrarySettings
from cloudinary import CloudinaryImage

register = template.Library()


@register.simple_tag
def get_library_setting(setting_name, default=None):
    """
    Get a specific library setting value
    Usage: {% get_library_setting 'library_name' 'Default Name' %}
    """
    try:
        settings = LibrarySettings.get_settings()
        return getattr(settings, setting_name, default)
    except:
        return default


@register.simple_tag
def library_name():
    """
    Get the library name
    Usage: {% library_name %}
    """
    try:
        settings = LibrarySettings.get_settings()
        return settings.library_name or "Library Management System"
    except:
        return "Library Management System"


@register.simple_tag
def library_logo():
    """
    Get the library logo
    Usage: {% library_logo %}
    """
    try:
        settings = LibrarySettings.get_settings()
        return settings.library_logo
    except:
        return None


@register.inclusion_tag('library/tags/library_contact.html')
def library_contact():
    """
    Render library contact information
    Usage: {% library_contact %}
    """
    try:
        settings = LibrarySettings.get_settings()
        return {
            'settings': settings,
            'has_contact_info': bool(settings.library_email or settings.library_phone or settings.library_address)
        }
    except:
        return {
            'settings': None,
            'has_contact_info': False
        }


@register.simple_tag
def safe_cloudinary_url(image_field, **kwargs):
    """
    Safely generate cloudinary URL from ImageField
    Usage: {% safe_cloudinary_url library_settings.library_logo width=32 height=32 crop='fill' %}
    """
    if not image_field:
        return ''

    try:
        # If it's an ImageFieldFile, get the public_id
        if hasattr(image_field, 'public_id'):
            public_id = image_field.public_id
        elif hasattr(image_field, 'name'):
            # Extract public_id from the name
            public_id = image_field.name
        else:
            # Assume it's already a string
            public_id = str(image_field)

        # Create CloudinaryImage and build URL
        cloudinary_image = CloudinaryImage(public_id)
        return cloudinary_image.build_url(**kwargs)
    except Exception:
        return ''
