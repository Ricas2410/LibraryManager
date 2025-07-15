"""
Production settings for library_management project.
"""

from .settings import *
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allow the fly.io domain, custom subdomain, and internal IPs for health checks
ALLOWED_HOSTS = [
    'dgms-library.fly.dev',  # Updated to match the actual app name
    'library.deigratiams.edu.gh',
    '.fly.io',
    '172.19.16.98',  # Internal IP used by fly.io for health checks
    '172.19.11.178',  # Current internal IP for health checks
    'localhost',
    '127.0.0.1',
    '*',  # Temporarily allow all hosts to fix health check issues
]

# WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
# Note: SECURE_SSL_REDIRECT is disabled because Fly.io handles HTTPS redirects
SECURE_SSL_REDIRECT = False  # Fly.io handles this with force_https = true
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Tell Django to trust the proxy headers from Fly.io
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Cache middleware - Disabled for now to ensure immediate updates
# MIDDLEWARE.insert(2, 'django.middleware.cache.UpdateCacheMiddleware')
# MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')

# Cache settings - Reduced cache time for immediate updates
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 30  # 30 seconds instead of 10 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'library'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# Email settings - use environment variables
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', '')

# Cloudinary settings for media files
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'ds5udo8jc'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', '848358464858687'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', 'j2nc79sJrSse9ST8AGwf72eGBWg'),
}

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

# Print debug info (remove in production)
print(f"Cloudinary configured with cloud_name: {CLOUDINARY_STORAGE['CLOUD_NAME']}")

# Use Cloudinary for media files in production
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Media files settings - Keep MEDIA_ROOT for migration compatibility
MEDIA_URL = '/media/'
MEDIA_ROOT = '/tmp/media'  # Temporary location for migration