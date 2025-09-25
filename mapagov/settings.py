# mapagov/settings.py - CORRIGIDO PARA DEPLOY

import os  # Adicionado para ler variáveis de ambiente
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Para um projeto real, isso também deveria ser uma variável de ambiente
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ol5&1dnbx!nzm!4hl6!yk1aah8t*vnmowqo@qtgp8vnqf*%vd9')

# SECURITY WARNING: don't run with debug turned on in production!
# Em produção (Vercel), DEBUG será False. Localmente, continuará True se você não definir a variável.
DEBUG = os.getenv('DEBUG', 'False') == 'True'


# --- MUDANÇA OBRIGATÓRIA ---
# Adiciona os domínios da Vercel aos hosts permitidos
ALLOWED_HOSTS = ['mapagov.vercel.app', '.vercel.app']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'import_export',
    'processos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # --- MUDANÇA RECOMENDADA ---
    # WhiteNoise para servir arquivos estáticos de forma eficiente
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mapagov.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mapagov.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# AVISO: O banco de dados SQLite não é persistente na Vercel.
# Qualquer dado salvo será perdido em novos deploys.
# Para um projeto real, use o Vercel Postgres ou outro banco de dados externo.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br' # Alterado para português do Brasil
TIME_ZONE = 'America/Sao_Paulo' # Alterado para fuso horário de Brasília

USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- MUDANÇA RECOMENDADA ---
# Configuração do WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'