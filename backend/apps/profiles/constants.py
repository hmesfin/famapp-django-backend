"""
Constants for the profiles app
Following RefactorA's recommendation to eliminate magic numbers
"""

# Avatar upload constraints
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
AVATAR_UPLOAD_PATH = 'avatars'

# Profile field constraints
MAX_BIO_LENGTH = 500
MAX_LOCATION_LENGTH = 100
MAX_COMPANY_LENGTH = 100
MAX_WEBSITE_LENGTH = 200

# User settings defaults
DEFAULT_THEME = 'light'
DEFAULT_LANGUAGE = 'en'
DEFAULT_TIMEZONE = 'UTC'
DEFAULT_EMAIL_NOTIFICATIONS = True
DEFAULT_PUSH_NOTIFICATIONS = False
DEFAULT_PROFILE_VISIBILITY = 'public'
DEFAULT_SHOW_EMAIL = False
DEFAULT_SHOW_ACTIVITY = True

# Cache timeouts (in seconds)
PROFILE_CACHE_TIMEOUT = 3600  # 1 hour
SETTINGS_CACHE_TIMEOUT = 7200  # 2 hours

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100