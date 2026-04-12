import os
import base64
import json
import tempfile
from pathlib import Path
from datetime import timedelta

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DEBUG      = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")


def _load_firebase_credentials() -> str:
    b64 = os.environ.get("FIREBASE_CREDENTIALS_BASE64")
    if b64:
        try:
            decoded = base64.b64decode(b64).decode("utf-8")
            json.loads(decoded)
            tmp = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                delete=False,
                prefix="firebase_",
            )
            tmp.write(decoded)
            tmp.close()
            return tmp.name
        except Exception as e:
            raise RuntimeError(f"Failed to decode Firebase credentials: {e}")

    configured_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "")
    candidate_paths = [
        configured_path,
        str(BASE_DIR / "firebase-credentials.json"),
        "/app/firebase-credentials.json",
    ]

    for candidate in candidate_paths:
        if candidate and os.path.exists(candidate):
            return candidate

    raise FileNotFoundError(
        "Firebase credentials not found. Checked:\n"
        + "\n".join([p for p in candidate_paths if p])
        + "\nSet FIREBASE_CREDENTIALS_BASE64 on Render or "
        "FIREBASE_CREDENTIALS_PATH locally."
    )


FIREBASE_CREDENTIALS_PATH = _load_firebase_credentials()
FIREBASE_API_KEY          = os.environ.get("FIREBASE_API_KEY",     "")
FIREBASE_AUTH_DOMAIN      = os.environ.get("FIREBASE_AUTH_DOMAIN", "")
FIREBASE_PROJECT_ID       = os.environ.get("FIREBASE_PROJECT_ID",  "")


DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "cloudinary",
    "cloudinary_storage",
    "django_celery_beat",
]

LOCAL_APPS = [
    "accounts",
    "appointments",
    "consultation",
    "medicals",
    "pharmacy",
    "homecare",
    "helper",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF     = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS":    [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


DATABASE_URL = os.environ.get("DATABASE_URL")


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


if DATABASE_URL:
    inferred_local_db = (
        "@db:" in DATABASE_URL
        or "@localhost:" in DATABASE_URL
        or "@127.0.0.1:" in DATABASE_URL
    )
    ssl_require = _env_bool("DB_SSL_REQUIRE", default=not inferred_local_db)

    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=ssl_require,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE":   "django.db.backends.postgresql",
            "NAME":     os.environ.get("DB_NAME",     "health_mate"),
            "USER":     os.environ.get("DB_USER",     "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
            "HOST":     os.environ.get("DB_HOST",     "db"),
            "PORT":     os.environ.get("DB_PORT",     "5432"),
            "OPTIONS": {
                "connect_timeout": 10,
            },
        }
    }

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/1")

redis_cache_options = {
    "CLIENT_CLASS": "django_redis.client.DefaultClient",
    "IGNORE_EXCEPTIONS": True,
}

if REDIS_URL.startswith("rediss://"):
    redis_cache_options["CONNECTION_POOL_KWARGS"] = {
        "ssl_cert_reqs": "CERT_NONE",
    }

CACHES = {
    "default": {
        "BACKEND":  "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": redis_cache_options,
    }
}



CELERY_BROKER_URL        = os.environ.get("CELERY_BROKER_URL",    "redis://redis:6379/0")
CELERY_RESULT_BACKEND    = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT    = ["json"]
CELERY_TASK_SERIALIZER   = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE          = "Africa/Lagos"
CELERY_BEAT_SCHEDULER    = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_TASK_ALWAYS_EAGER     = True
CELERY_TASK_EAGER_PROPAGATES = True

if CELERY_BROKER_URL.startswith("rediss://"):
    CELERY_BROKER_USE_SSL = {
        "ssl_cert_reqs": "CERT_NONE"
    }

if CELERY_RESULT_BACKEND.startswith("rediss://"):
    CELERY_REDIS_BACKEND_USE_SSL = {
        "ssl_cert_reqs": "CERT_NONE"
    }



AUTH_USER_MODEL = "accounts.CompanyUser"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]



SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_LIFETIME", 900))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        seconds=int(os.environ.get("JWT_REFRESH_TOKEN_LIFETIME", 604800))
    ),
    "ROTATE_REFRESH_TOKENS":    True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN":        True,
    "ALGORITHM":                "HS256",
    "SIGNING_KEY":              SECRET_KEY,
    "AUTH_HEADER_TYPES":        ("Bearer",),
    "AUTH_TOKEN_CLASSES":       ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM":         "token_type",
    "JTI_CLAIM":                "jti",

    # Store tokens in HttpOnly cookies
    "AUTH_COOKIE":              "access_token",
    "AUTH_COOKIE_REFRESH":      "refresh_token",
    "AUTH_COOKIE_SECURE":       not DEBUG,
    "AUTH_COOKIE_HTTP_ONLY":    True,
    "AUTH_COOKIE_PATH":         "/",
    "AUTH_COOKIE_SAMESITE":     "Lax",
}



REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CookieJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS":     "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
    },
}


CONSULTATION_TYPE_ENUM_CHOICES = [
    ("video", "Video"),
    ("audio", "Audio"),
    ("chat", "Chat"),
]

GENDER_ENUM_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
]

SPECTACULAR_SETTINGS = {
    "TITLE":       "Health Mate API",
    "DESCRIPTION": "A secure, production-ready healthcare platform API.",
    "VERSION":     "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,

    "TAGS": [
        {
            "name":        "Authentication",
            "description": "Register, Login, OTP, Password Reset, Profile — "
                           "Personal, Medical, Emergency Contact",
        },
        {
            "name":        "Appointments",
            "description": "Book appointments, manage schedules, "
                           "doctor availability and slots",
        },
        {
            "name":        "Consultation",
            "description": "Video Consultations with Daily.co",
        },
        {
            "name":        "Medical Records",
            "description": "Consultation reports, prescriptions, "
                           "lab results and downloads",
        },
        {
            "name":        "Lab Tests",
            "description": "Book and track lab tests and results",
        },
        {
            "name":        "Pharmacy",
            "description": "Browse products, manage cart, "
                           "checkout and track orders via Paystack",
        },
        {
            "name":        "Home Care",
            "description": "Request home care services with location and scheduling",
        },
    ],

    "ENUM_NAME_OVERRIDES": {
        "ConsultationTypeEnum":       CONSULTATION_TYPE_ENUM_CHOICES,
        "AppointmentStatusEnum":      "appointments.models.AppointmentStatus",
        "ConsultationStatusEnum":     "consultation.models.ConsultationStatus",
        "GenderEnum":                 GENDER_ENUM_CHOICES,
        "LabTestStatusEnum":          "medicals.models.LabTestStatus",
        "HomeCareRequestStatusEnum":  "homecare.models.HomeCareRequest.Status",
        "PharmacyOrderStatusEnum":    "pharmacy.models.PharmacyOrder.Status",
        "PharmacyPaymentStatusEnum":  "pharmacy.models.PharmacyOrder.PaymentStatus",
    },

    "SECURITY": [{"BearerAuth": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type":         "http",
                "scheme":       "bearer",
                "bearerFormat": "JWT",
            }
        }
    },

    "SWAGGER_UI_SETTINGS": {
        "deepLinking":              True,
        "persistAuthorization":     True,
        "displayOperationId":       False,
        "defaultModelsExpandDepth": 1,
        "docExpansion":             "list",
        "filter":                   False,
    },

    "SORT_OPERATIONS": False,
}



CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    "API_KEY":    os.environ.get("CLOUDINARY_API_KEY",    ""),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET", ""),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",")

CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:3000"
).split(",")

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]


DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@ordfellow.com")
SERVER_EMAIL       = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@ordfellow.com")
RESEND_API_KEY     = os.environ.get("RESEND_API_KEY",     "")
RESEND_FROM_EMAIL  = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@ordfellow.com")


DAILY_API_KEY   = os.environ.get("DAILY_API_KEY",   "")
DAILY_API_URL   = os.environ.get("DAILY_API_URL",   "https://api.daily.co/v1")
DAILY_SUBDOMAIN = os.environ.get("DAILY_SUBDOMAIN", "")



PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY", "")
PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY", "")


OTP_EXPIRY_SECONDS = int(os.environ.get("OTP_EXPIRY_SECONDS", 300))


if not DEBUG:
    SECURE_SSL_REDIRECT            = True
    SECURE_HSTS_SECONDS            = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD            = True
    SECURE_PROXY_SSL_HEADER        = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE          = True
    CSRF_COOKIE_SECURE             = True
    SECURE_BROWSER_XSS_FILTER      = True
    SECURE_CONTENT_TYPE_NOSNIFF    = True
    X_FRAME_OPTIONS                = "DENY"



LANGUAGE_CODE      = "en-us"
TIME_ZONE          = "Africa/Lagos"
USE_I18N           = True
USE_TZ             = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGGING = {
    "version":                  1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {message}",
            "style":  "{",
        },
    },
    "handlers": {
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level":    "INFO",
    },
    "loggers": {
        "django": {
            "handlers":  ["console"],
            "level":     "WARNING",
            "propagate": False,
        },
        "celery": {
            "handlers":  ["console"],
            "level":     "INFO",
            "propagate": False,
        },
    },
}
