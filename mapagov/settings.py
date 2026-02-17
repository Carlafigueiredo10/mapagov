# mapagov/settings.py - CORRIGIDO PARA RENDER + COMPLETO

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Carregar variáveis do .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-ol5&1dnbx!nzm!4hl6!yk1aah8t*vnmowqo@qtgp8vnqf*%vd9')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# --- FAIL-FAST: SECRET_KEY insegura em produção ---
if not DEBUG and 'django-insecure' in SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY insegura detectada em produção. "
        "Defina a variável de ambiente SECRET_KEY com um valor seguro."
    )

# MVP sem autenticação - API pública apenas para desenvolvimento/demo
# Default: desativado (autenticação obrigatória)
PUBLIC_MVP_MODE = os.getenv("PUBLIC_MVP_MODE", "0") == "1"

# --- FAIL-FAST: PUBLIC_MVP_MODE em produção ---
if not DEBUG and PUBLIC_MVP_MODE:
    raise RuntimeError(
        "PUBLIC_MVP_MODE=1 não é permitido em produção (DEBUG=False). "
        "Remova PUBLIC_MVP_MODE ou defina PUBLIC_MVP_MODE=0."
    )

# --- ALLOWED HOSTS: Render + Google Cloud ---
ALLOWED_HOSTS = [
    'mapagov.onrender.com',
    '.onrender.com',
    'localhost',
    '127.0.0.1',
    '.run.app',  # Google Cloud Run
]

# CSRF Trusted Origins (para formulários de login/admin + cookies)
CSRF_TRUSTED_ORIGINS = [
    # NOTA: Wildcards NÃO funcionam no Django! Use URL exata do Cloud Run
    # Adicione via variável de ambiente CSRF_TRUSTED_ORIGINS após deploy
    'https://mapagov.onrender.com',
    # Desenvolvimento local (necessário para cookies CORS)
    'http://localhost:5173',
    'http://localhost:5174',
    'http://localhost:5175',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:5174',
    'http://127.0.0.1:5175',
]

# Adicionar origens de produção via variável de ambiente
csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in csrf_origins_env.split(',')])

# ============================================================================
# CONFIGURAÇÕES DE SEGURANÇA PARA PRODUÇÃO
# ============================================================================
if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = False  # Cloud Run proxy já gerencia HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'   # Same-origin (WhiteNoise SPA) — Lax e suficiente
    CSRF_COOKIE_SAMESITE = 'Lax'

    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Outros headers de segurança
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
else:
    # Desenvolvimento local - permitir cookies sem HTTPS
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'  # Lax funciona melhor em desenvolvimento local

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
    'import_export',
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
    'processos.infra.access_control_middleware.AccessControlMiddleware',  # Auth: bloqueia usuarios nao aprovados
    'processos.infra.rls_middleware.RLSMiddleware',  # FASE 2: Row-Level Security
    'processos.infra.structured_logging.RequestLoggingMiddleware',  # FASE 3: Structured Logging
    'processos.infra.metrics.PrometheusMetricsMiddleware',  # FASE 3: Prometheus Metrics
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

# ============================================================================
# DATABASE: Render (Neon PostgreSQL) + SQLite local
# ============================================================================
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Deteccao de testes: manage.py test, pytest, CI
RUNNING_TESTS = (
    "test" in sys.argv
    or (sys.argv[0].endswith("pytest") if sys.argv else False)
    or os.getenv("PYTEST_CURRENT_TEST") is not None
)
FORCE_TEST_SQLITE = os.getenv("DJANGO_TEST_SQLITE", "0") == "1"

if RUNNING_TESTS and FORCE_TEST_SQLITE:
    # Testes isolados em SQLite em memoria — nunca toca Neon
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
elif DATABASE_URL:
    # Postgres via URL (Neon/Render)
    ssl_require = os.getenv("DB_SSL_REQUIRE", "1") == "1"
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "60")),
            ssl_require=ssl_require,
        )
    }
else:
    # Dev local com SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Fail-safe: nao permitir SQLite em producao
SKIP_DB_CHECK = os.getenv("SKIP_DB_CHECK", "0") == "1"
if not DEBUG and not SKIP_DB_CHECK and DATABASES["default"]["ENGINE"].endswith("sqlite3"):
    raise RuntimeError(
        "SQLite nao e permitido com DEBUG=False. Configure DATABASE_URL."
    )

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 6}},
    {'NAME': 'processos.validators.GovBrPasswordValidator'},
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
# Usar CompressedStaticFilesStorage SEM manifest (evita problemas com index.html)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ============================================================================
# SERVIR FRONTEND REACT (BUILD) - Para deploy no Render com tudo junto
# ============================================================================
# O frontend React buildado (npm run build) gera arquivos em frontend/dist/
# Vamos servir esses arquivos como parte do Django

# Configurar STATICFILES_DIRS apenas com diretórios que existem
STATICFILES_DIRS = [
    BASE_DIR / 'processos' / 'static',  # Arquivos estáticos do Django
]

# Adicionar frontend/dist apenas se existir (evita WARNING W004)
frontend_dist = BASE_DIR / 'frontend' / 'dist'
if frontend_dist.exists():
    STATICFILES_DIRS.append(frontend_dist)

# Arquivos de mídia (uploads, PDFs, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'MapaGov <noreply@gestao.gov.br>')

# Token de verificacao expira em 24h
PASSWORD_RESET_TIMEOUT = 86400

# ============================================================================
# SESSION CONFIGURATION
# ============================================================================
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = True  # Sliding expiry — reseta timeout em cada atividade
SESSION_COOKIE_HTTPONLY = True  # Previne acesso JS ao cookie de sessao

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
    # MVP: API pública (PUBLIC_MVP_MODE=1) ou com auth (PUBLIC_MVP_MODE=0)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny' if PUBLIC_MVP_MODE
        else 'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [] if PUBLIC_MVP_MODE else [
        'rest_framework.authentication.SessionAuthentication',
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

# Windows + DEBUG: RotatingFileHandler falha por file-locking no runserver
# (dois processos — reloader + real — disputam os.rename no mesmo arquivo).
# Em dev no Windows, console é suficiente. Em produção (Linux), rotação normal.
ENABLE_FILE_LOGS = not (DEBUG and os.name == 'nt')

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
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'processos': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'processos.views': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'processos.helena_produtos': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Adicionar file handlers apenas quando seguro (Linux ou produção)
if ENABLE_FILE_LOGS:
    LOGGING['handlers']['file_info'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': BASE_DIR / 'logs' / 'info.log',
        'maxBytes': 10 * 1024 * 1024,  # 10MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
    LOGGING['handlers']['file_error'] = {
        'level': 'ERROR',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': BASE_DIR / 'logs' / 'error.log',
        'maxBytes': 10 * 1024 * 1024,  # 10MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
    LOGGING['handlers']['file_helena'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': BASE_DIR / 'logs' / 'helena.log',
        'maxBytes': 10 * 1024 * 1024,  # 10MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
    LOGGING['loggers']['django']['handlers'].append('file_error')
    LOGGING['loggers']['django.request']['handlers'].append('file_error')
    LOGGING['loggers']['processos']['handlers'].extend(['file_info', 'file_error'])
    LOGGING['loggers']['processos.views']['handlers'].extend(['file_helena', 'file_error'])
    LOGGING['loggers']['processos.helena_produtos']['handlers'].extend(['file_helena', 'file_error'])

# Criar diretório de logs apenas se file logging ativo
if ENABLE_FILE_LOGS:
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

    else:
        pass
else:
    pass


# ============================================================================
# ⚡ OTIMIZAÇÃO MEMÓRIA: HELENA LITE MODE
# ============================================================================
# Controla quais produtos Helena carregar para economizar RAM em ambientes limitados
# Use HELENA_LITE_MODE=True em produção com <1GB RAM (Render Free, etc.)

HELENA_LITE_MODE = os.getenv('HELENA_LITE_MODE', 'False').lower() in ('true', '1', 'yes')



# ============================================================================
# 🚀 REDIS CACHE - FASE 1 (Sessões de Chat)
# ============================================================================
# Redis para cache de sessões + sincronização híbrida com PostgreSQL
# Modo degradado: se Redis indisponível, usa apenas PostgreSQL

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",  # Fallback
    }
}

# Tenta usar Redis se disponível
try:
    import redis
    # Testa conexão
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, socket_connect_timeout=2)
    r.ping()

    # Se chegou aqui, Redis está disponível
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 50,
                    "retry_on_timeout": True,
                },
                "REDIS_CLIENT_KWARGS": {
                    "health_check_interval": 30,
                },
            },
            "KEY_PREFIX": "mapagov",
            "TIMEOUT": 900,  # 15 minutos (padrão)
        }
    }
except Exception:
    if not DEBUG:
        import logging
        logging.getLogger('mapagov.startup').warning(
            "Redis indisponivel. Cache LocMemCache ativo em producao. "
            "Configure REDIS_HOST para rate limiting distribuido."
        )
