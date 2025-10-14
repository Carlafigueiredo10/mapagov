# mapagov/settings.py - CORRIGIDO PARA RENDER + COMPLETO

import os
from pathlib import Path
from dotenv import load_dotenv  # ← importa aqui
from urllib.parse import urlparse

# Carregar variáveis do .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ol5&1dnbx!nzm!4hl6!yk1aah8t*vnmowqo@qtgp8vnqf*%vd9')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# --- CORRIGIDO PARA RENDER ---
ALLOWED_HOSTS = ['mapagov.onrender.com', '.onrender.com', 'localhost', '127.0.0.1']

# ============================================================================
# CONFIGURAÇÕES DE SEGURANÇA PARA PRODUÇÃO
# ============================================================================
if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Outros headers de segurança
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Pacotes externos
    'rest_framework',
    # 'import_export',  # Temporariamente desabilitado
    'corsheaders',  # CORS para React

    # Apps locais
    'processos',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS deve ser o primeiro
    'django.middleware.security.SecurityMiddleware',
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
        # Adiciona pasta de templates no projeto + frontend React buildado
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'frontend' / 'dist',  # Para servir index.html do React
        ],
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

WSGI_APPLICATION = 'mapagov.wsgi.application'

# Database (Postgres via DATABASE_URL ou fallback para SQLite)
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    # Suporta formatos: postgres://user:pass@host:port/dbname
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path.lstrip('/'),
            'USER': parsed.username,
            'PASSWORD': parsed.password,
            'HOST': parsed.hostname,
            'PORT': parsed.port or '5432',
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '60')),
            'OPTIONS': {
                'sslmode': os.getenv('DB_SSLMODE', 'prefer')
            } if os.getenv('DB_REQUIRE_SSL', 'false').lower() == 'true' else {}
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 🔥 FASE 1: Forçar PostgreSQL em produção (segurança + escalabilidade)
if not DEBUG and DATABASES['default']['ENGINE'].endswith('sqlite3'):
    raise RuntimeError(
        "❌ PRODUÇÃO COM SQLITE DETECTADA! SQLite não suporta concorrência e não escala.\n"
        "Defina DATABASE_URL para PostgreSQL: export DATABASE_URL='postgresql://user:pass@host:5432/dbname'\n"
        "Veja MIGRATION_POSTGRES.md para instruções completas."
    )

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration (para Render)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================================
# SERVIR FRONTEND REACT (BUILD) - Para deploy no Render com tudo junto
# ============================================================================
# O frontend React buildado (npm run build) gera arquivos em frontend/dist/
# Vamos servir esses arquivos como parte do Django

STATICFILES_DIRS = [
    BASE_DIR / 'frontend' / 'dist',  # Frontend React buildado
    BASE_DIR / 'processos' / 'static',  # Arquivos estáticos do Django
]

# Arquivos de mídia (uploads, PDFs, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework - configuração básica
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# ============================================================================
# CONFIGURAÇÕES CORS PARA FRONTEND REACT
# ============================================================================

# URL do frontend React (configurável por ambiente)
REACT_FRONTEND_URL = os.getenv('REACT_FRONTEND_URL', 'http://localhost:5174')

# Permitir requisições do frontend React
CORS_ALLOWED_ORIGINS = [
    # Desenvolvimento local
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

# Adicionar origens de produção via variável de ambiente
# Exemplo: CORS_ALLOWED_ORIGINS=https://mapagov.vercel.app,https://mapagov-git-*.vercel.app
cors_origins_env = os.getenv('CORS_ALLOWED_ORIGINS', '')
if cors_origins_env:
    CORS_ALLOWED_ORIGINS.extend([origin.strip() for origin in cors_origins_env.split(',')])

# Headers permitidos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Métodos HTTP permitidos
CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Permitir cookies/credenciais
CORS_ALLOW_CREDENTIALS = True

# Para desenvolvimento, permitir todas as origens
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True


# ============================================================================
# 🔥 FASE 1: LOGGING ESTRUTURADO COM NÍVEIS
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} [{name}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        } if not DEBUG else {
            'format': '{levelname} {asctime} [{name}] {message}',
            'style': '{',
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file_info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'info.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'error.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_helena': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'helena.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file_error'],
            'level': 'ERROR',
            'propagate': False,
        },
        'processos': {
            'handlers': ['console', 'file_info', 'file_error'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'processos.views': {
            'handlers': ['console', 'file_helena', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        'processos.helena_produtos': {
            'handlers': ['console', 'file_helena', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Criar diretório de logs se não existir
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)


# ============================================================================
# 🔥 FASE 1: SENTRY - MONITORAMENTO DE ERROS EM PRODUÇÃO
# ============================================================================

if not DEBUG:
    try:
        import sentry_sdk
        import logging
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
    except ImportError:
        print("[WARNING] sentry-sdk não instalado. Sentry desabilitado.")
        sentry_sdk = None

    SENTRY_DSN = os.getenv('SENTRY_DSN') if 'sentry_sdk' in locals() and sentry_sdk else None

    if SENTRY_DSN and sentry_sdk:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(),
                LoggingIntegration(
                    level=logging.INFO,  # Captura logs INFO e acima
                    event_level=logging.ERROR  # Envia para Sentry apenas ERRORs
                ),
            ],
            # Performance Monitoring
            traces_sample_rate=0.1,  # 10% das transações para performance

            # Profiling
            profiles_sample_rate=0.1,  # 10% para profiling

            # Environment
            environment=os.getenv('ENVIRONMENT', 'production'),

            # Release tracking
            release=os.getenv('GIT_COMMIT_SHA', 'unknown'),

            # Dados sensíveis - não enviar
            send_default_pii=False,

            # Breadcrumbs
            max_breadcrumbs=50,

            # Antes de enviar para Sentry, filtrar dados sensíveis
            before_send=lambda event, hint: event if not any(
                key in str(event) for key in ['password', 'token', 'secret', 'api_key']
            ) else None,
        )

        print("[OK] Sentry configurado para monitoramento de erros")
    else:
        print("[WARNING] SENTRY_DSN nao configurado. Configure para monitoramento em producao.")
        print("    Obtenha seu DSN em: https://sentry.io/settings/projects/")
        print("    Depois: export SENTRY_DSN='https://...@sentry.io/...'")
else:
    print("[DEBUG] Modo DEBUG ativo - Sentry desabilitado")
