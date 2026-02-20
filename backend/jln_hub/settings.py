"""
Django settings for jln_hub project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production-jln-hub-2026')

# SECURITY WARNING: don't run with debug turned on in production!
# Default to True for local development, False in production
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]  # Temporarily allow all for Railway deployment testing



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jln_hub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'frontend'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jln_hub.wsgi.application'


# Database
# Using SQLite for development - suitable for offline-first app
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
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
TIME_ZONE = 'Africa/Juba'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Static files directories (for development - Django automatically finds files here)
# In production, collectstatic copies these to STATIC_ROOT
STATICFILES_DIRS = [
    BASE_DIR.parent / 'frontend' / 'src',
    BASE_DIR.parent / 'frontend',
]

# WhiteNoise configuration (version 6.x)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # For development - restrict in production
CORS_ALLOW_CREDENTIALS = True

# CSRF settings - add your production domain to CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000', 
    'http://127.0.0.1:8000',
]

# Railway-specific configuration
RAILWAY_ENVIRONMENT = os.environ.get('RAILWAY_ENVIRONMENT')
if RAILWAY_ENVIRONMENT:
    # Railway provides PUBLIC_DOMAIN or RAILWAY_PUBLIC_DOMAIN
    railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN') or os.environ.get('PUBLIC_DOMAIN')
    if railway_domain:
        CSRF_TRUSTED_ORIGINS.append(f'https://{railway_domain}')
        ALLOWED_HOSTS.append(railway_domain)
        # Also allow the .railway.app domain
        CSRF_TRUSTED_ORIGINS.append(f'https://*.railway.app')

# Render-specific configuration (fallback support)
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
if RENDER_EXTERNAL_URL:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_URL}')
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_URL)

CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# AI API Keys (for AI lesson generation in production)
# OpenRouter provides access to multiple AI models with free options
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', None)
# Legacy OpenAI support (optional)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', None)

