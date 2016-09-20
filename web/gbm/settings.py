"""
Django settings for gbm project.

Generated by 'django-admin startproject' using Django 1.9.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# Include BOOTSTRAP3_FOLDER in path
BOOTSTRAP3_FOLDER = os.path.abspath(os.path.join(BASE_DIR, '..', 'bootstrap3'))
if BOOTSTRAP3_FOLDER not in sys.path:
    sys.path.insert(0, BOOTSTRAP3_FOLDER)

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False)

ALLOWED_HOSTS = [
    'gbm.sg',
    'bulletin.gbm.sg',
    'preview.gbm.sg'
]

SITE_ID = 1

# Email Settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', '')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = os.getenv('EMAIL_PORT', '')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '')

# Django allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'

# Application definition

INSTALLED_APPS = [
    # The Django sites framework is required for allauth
    'django.contrib.sites',
    # django-suit
    #    'suit',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'bootstrap3',
    'newswire',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',

    'paintstore',
    'crispy_forms',

    'widget_tweaks',
    'import_export',  # inport/export CSV function

    'constance',
    'constance.backends.database',

    'django.contrib.humanize',

]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gbm.urls'

# Get PROJECT_PATH
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [PROJECT_PATH],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # `allauth` needs this from django
                'django.template.context_processors.request',
                # constance
                'constance.context_processors.config',
                # newswire count under-review items
                'newswire.context_processors.under_review_count_processor',
            ],
        },
    },
]

# Django Suit configuration
SUIT_CONFIG = {
    # header
    'ADMIN_NAME': os.environ['DJANGO_SUIT_ADMIN_NAME'],
    # 'HEADER_DATE_FORMAT': 'l, j. F Y',
    # 'HEADER_TIME_FORMAT': 'H:i',

    # forms
    'SHOW_REQUIRED_ASTERISK': True,  # Default True
    'CONFIRM_UNSAVED_CHANGES': True,  # Default True

    # menu
    # 'SEARCH_URL': '/admin/auth/user/',
    # 'MENU_ICONS': {
    #    'sites': 'icon-leaf',
    #    'auth': 'icon-lock',
    # },
    # 'MENU_OPEN_FIRST_CHILD': True, # Default True
    # 'MENU_EXCLUDE': ('auth.group',),
    # 'MENU': (
    #     'sites',
    #     {'app': 'auth', 'icon':'icon-lock', 'models': ('user', 'group')},
    #     {'label': 'Settings', 'icon':'icon-cog', 'models': ('auth.user', 'auth.group')},
    #     {'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},
    # ),

    # misc
    'LIST_PER_PAGE': 15
}

AUTHENTICATION_BACKENDS = {
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
}

# auth and allauth settings
LOGIN_REDIRECT_URL = '/accounts/profile/'
LOGIN_URL = '/accounts/login/'

ABSOLUTE_URL_OVERRIDES = {
    #    'auth.user': lambda u: "/members/profile/%s/" % u.profile.pk,
}

SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email'],
        'METHOD': 'js_sdk'  # instead of 'oauth2'
    }
}

WSGI_APPLICATION = 'gbm.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME', ''),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASS', ''),
        'HOST': os.getenv('DB_SERVICE', ''),
        'PORT': os.getenv('DB_PORT', '')
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Singapore'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Settings for django-bootstrap3
BOOTSTRAP3 = {
    'set_required': False,
    'error_css_class': 'bootstrap3-error',
    'required_css_class': 'bootstrap3-required',
    'javascript_in_head': True,
}

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'BULLETIN_WELCOME_MESSAGE': ('Welcome to Grace Baptist Ministries. We\'re glad you\'re with us today! If something you encounter during the worship service moves you to want to know more, there are always leaders up front near the stage at the end of the service to talk to you, pray with you and help you in any way they can. Please also visit our website if you would like more information.', 'Welcome message at the top of the bulletin'),
    'THIS_YEAR_THEME_YEAR': ('2016', 'The year of the theme you entered below'),
    'THIS_YEAR_THEME': ('Loving Across Our Differences', 'This year\'s theme'),
    'THIS_YEAR_THEME_VERSE': ('<p class="text-justified"><sup>34</sup> A new commandment I give to you, that you love one another; as I have loved you, that you also love one another. <sup>35</sup> By this all will know that you are My disciples, if you have love for one another.<br /><br />John 13:34-35</p>', 'This year\'s theme verse'),
    'CONTACT_PHONE': ('+65 6745 2887', 'Contact number appearing in footer/bottom of page'),
    'CONTACT_PHONE_URL': ('tel:+6567452887', 'Contact number URL appearing in footer/bottom of page'),
    'CONTACT_EMAIL': ('office@gbm.sg', 'Email address appearing in footer/bottom of page'),
    'CONTACT_EMAIL_URL': ('mailto:office@gbm.sg?Subject=gbm.sg%20Contact%20Form', 'Email address URL appearing in footer/bottom of page'),
    'CONTACT_ADDRESS': ('146B Paya Lebar Road,<br/>ACE Building, #05-01<br/>Singapore 409017', 'Mailing Address appearing in footer/bottom of page'),
    'CONTACT_ADDRESS_URL': ('https://goo.gl/maps/55FGkrEbUf72', 'Google maps link for above address'),
    'MAX_PRINT_ANNOUCEMENTS': ('7', 'Maximum number of annoucements to print', int),

}
