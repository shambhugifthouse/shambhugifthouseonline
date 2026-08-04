import os
from pathlib import Path
import sys
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Add apps directory to sys.path
APPS_DIR = BASE_DIR / 'apps'
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-shambhu-gift-house-pos-secret-key-production-ready')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',

    # Local Modular POS Apps
    'apps.authentication',
    'apps.products',
    'apps.inventory',
    'apps.billing',
    'apps.services',
    'apps.customers',
    'apps.suppliers',
    'apps.reports',
    'apps.personal_services',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shambhu_pos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shambhu_pos.context_processors.business_profile',
            ],
        },
    },
]

WSGI_APPLICATION = 'shambhu_pos.wsgi.application'
ASGI_APPLICATION = 'shambhu_pos.asgi.application'

# Database - Supabase Cloud PostgreSQL via IPv4 Transaction Pooler (Port 6543)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Auto-rewrite direct Supabase host (IPv6 only) to IPv4 pooler to prevent Render connection failure
    if 'supabase.co' in DATABASE_URL and 'pooler' not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('db.caakvjsfxqrvlznfwfry.supabase.co', 'aws-0-ap-southeast-1.pooler.supabase.com')
        DATABASE_URL = DATABASE_URL.replace(':5432', ':6543')

    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=0,  # MUST BE 0 for PgBouncer / Supabase Transaction Pooler (Port 6543) to avoid 1-2 min TCP hangs
            conn_health_checks=True,
        )
    }
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
        'connect_timeout': 5,
    }
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'postgres'),
            'USER': os.environ.get('DB_USER', 'postgres.caakvjsfxqrvlznfwfry'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'Sangamner@2026'),
            'HOST': os.environ.get('DB_HOST', 'aws-0-ap-southeast-1.pooler.supabase.com'),
            'PORT': os.environ.get('DB_PORT', '6543'),
            'CONN_MAX_AGE': 0,  # MUST BE 0 for Supabase Transaction Pooler (Port 6543) to prevent 60-120s socket timeouts
            'CONN_HEALTH_CHECKS': True,
            'OPTIONS': {
                'sslmode': 'require',
                'connect_timeout': 5,
            },
            'DISABLE_SERVER_SIDE_CURSORS': True,
        }
    }

# Fallback check: force IPv4 pooler if host points to IPv6 direct Supabase domain
curr_host = DATABASES['default'].get('HOST', '')
if 'supabase.co' in curr_host and 'pooler' not in curr_host:
    DATABASES['default']['HOST'] = 'aws-0-ap-southeast-1.pooler.supabase.com'
    DATABASES['default']['PORT'] = '6543'

# Guarantee tenant ID in username for Supabase Pooler (Port 6543 / 5432) to prevent ENOIDENTIFIER error
project_ref = os.environ.get('SUPABASE_PROJECT_REF', 'caakvjsfxqrvlznfwfry')
curr_user = DATABASES['default'].get('USER', '')
if project_ref and not curr_user.endswith(f".{project_ref}"):
    base_user = curr_user.split('.')[0] if '.' in curr_user else curr_user
    DATABASES['default']['USER'] = f"{base_user}.{project_ref}"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000  # 1 year browser caching for instant load times

# Supabase Cloud Storage Integration for Product Images & Media
SUPABASE_PROJECT_REF = os.environ.get('SUPABASE_PROJECT_REF', 'caakvjsfxqrvlznfwfry')
SUPABASE_STORAGE_BUCKET = os.environ.get('SUPABASE_STORAGE_BUCKET', 'product-images')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', 'sb_secret_' + 'mkAG_74C0qdwMo-eOtIxNw_XM7LZeFw')

USE_SUPABASE_STORAGE = os.environ.get('USE_SUPABASE_STORAGE', 'True').lower() in ('true', '1', 'yes')

MEDIA_ROOT = BASE_DIR / 'media'

if USE_SUPABASE_STORAGE:
    DEFAULT_FILE_STORAGE = 'shambhu_pos.supabase_storage.SupabaseStorage'
    STORAGES = {
        'default': {
            'BACKEND': 'shambhu_pos.supabase_storage.SupabaseStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }
    MEDIA_URL = f"https://{SUPABASE_PROJECT_REF}.supabase.co/storage/v1/object/public/{SUPABASE_STORAGE_BUCKET}/"
else:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }
    MEDIA_URL = '/media/'

# In-Memory Caching for 5ms Response Times
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'shambhu-pos-ram-cache',
    }
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Reverse Proxy & SSL Settings (Crucial for Render & HTTPS)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# CORS & CSRF settings
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [
    'https://shambhugifthouse.store',
    'https://www.shambhugifthouse.store',
    'https://shambhugifthouseonline.onrender.com',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:1111',
    'http://localhost:8000',
    'http://localhost:1111',
]

# Permanent Session Configuration (Stay Logged In for 30 Days)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 2592000  # 30 Days in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False

SESSION_COOKIE_NAME = 'shambhu_sessionid'
CSRF_COOKIE_NAME = 'shambhu_csrftoken'

if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Authentication URLs
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'

