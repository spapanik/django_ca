import contextlib
from datetime import timedelta
from functools import partial
from pathlib import Path

import django_stubs_ext
from dj_settings import get_setting

BASE_DIR = Path(__file__).parents[2]
PROJECT_DIR = BASE_DIR.joinpath("src")
project_setting = partial(get_setting, project_dir=BASE_DIR, filename="django_ca.yaml")
django_stubs_ext.monkeypatch()

# region Security
validation = "django.contrib.auth.password_validation"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"{validation}.UserAttributeSimilarityValidator"},
    {"NAME": f"{validation}.MinimumLengthValidator"},
    {"NAME": f"{validation}.CommonPasswordValidator"},
    {"NAME": f"{validation}.NumericPasswordValidator"},
]

SECRET_KEY = project_setting("DJ_CA_SECRET_KEY", sections=["project", "security"])

signup_token_expiry = project_setting(
    "DJ_CA_SIGNUP_TOKEN_EXPIRY", sections=["project", "tokens"], rtype=dict
)
SIGNUP_TOKEN_EXPIRY = timedelta(**signup_token_expiry)
access_token_expiry = project_setting(
    "DJ_CA_ACCESS_TOKEN_EXPIRY", sections=["project", "tokens"], rtype=dict
)
ACCESS_TOKEN_EXPIRY = timedelta(**access_token_expiry)
refresh_token_expiry = project_setting(
    "DJ_CA_REFRESH_TOKEN_EXPIRY", sections=["project", "tokens"], rtype=dict
)
REFRESH_TOKEN_EXPIRY = timedelta(**refresh_token_expiry)
# endregion

# region Application definition
DEBUG = project_setting("DJ_CA_DEBUG", sections=["project", "app"], rtype=bool)
CI_MODE = project_setting("DJ_CA_CI_MODE", sections=["project", "app"], rtype=bool)
BASE_API_SCHEME = project_setting(
    "DJ_CA_BASE_API_SCHEME", sections=["project", "servers"]
)
BASE_API_DOMAIN = project_setting(
    "DJ_CA_BASE_API_DOMAIN", sections=["project", "servers"]
)
BASE_API_PORT = project_setting(
    "DJ_CA_BASE_API_PORT", sections=["project", "servers"], rtype=int
)
BASE_APP_SCHEME = project_setting(
    "DJ_CA_BASE_APP_SCHEME", sections=["project", "servers"]
)
BASE_APP_DOMAIN = project_setting(
    "DJ_CA_BASE_APP_DOMAIN", sections=["project", "servers"]
)
BASE_APP_PORT = project_setting(
    "DJ_CA_BASE_APP_PORT", sections=["project", "servers"], rtype=int
)
ALLOWED_HOSTS = [BASE_API_DOMAIN]

AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ROOT_URLCONF = "django_ca.urls"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.messages",
    "corsheaders",
    "django_ca.lib",
    "django_ca.accounts",
    "django_ca.certificates",
    "django_ca.home",
]

if DEBUG and not CI_MODE:
    INSTALLED_APPS += ["django_extensions"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOWED_ORIGINS = [f"{BASE_APP_SCHEME}://{BASE_APP_DOMAIN}:{BASE_APP_PORT}"]

NO_REPLY_USER_PART = project_setting(
    "DJ_CA_NO_REPLY_USER_PART", sections=["project", "app", "email"]
)
NO_REPLY_EMAIL_PART = project_setting(
    "DJ_CA_NO_REPLY_EMAIL_PART", sections=["project", "app", "email"]
)
NO_REPLY_EMAIL = f'"{NO_REPLY_USER_PART}" <{NO_REPLY_EMAIL_PART}>'
EMAIL_BACKEND = project_setting(
    "DJ_CA_EMAIL_BACKEND", sections=["project", "app", "email"]
)
email_file_path = project_setting(
    "DJ_CA_EMAIL_FILE_PATH", sections=["project", "app", "email"]
)
EMAIL_FILE_PATH = BASE_DIR.joinpath(email_file_path)
email_template_dir = project_setting(
    "DJ_CA_EMAIL_TEMPLATE_DIR", sections=["project", "app", "email"]
)
EMAIL_TEMPLATE_DIR = PROJECT_DIR.joinpath(email_template_dir)

MIGRATION_HASHES_PATH = BASE_DIR.joinpath("migrations.lock")

OPTIMUS_PRIME = project_setting(
    "DJ_CA_OPTIMUS_PRIME", sections=["project", "app", "optimus"], rtype=int
)
OPTIMUS_INVERSE = project_setting(
    "DJ_CA_OPTIMUS_INVERSE", sections=["project", "app", "optimus"], rtype=int
)
OPTIMUS_RANDOM = project_setting(
    "DJ_CA_OPTIMUS_RANDOM", sections=["project", "app", "optimus"], rtype=int
)

# endregion

# region Application settings
DEFAULT_COUNTRY = "GB"
DEFAULT_PROVINCE = "England"
DEFAULT_LOCALITY = "London"
CA_EMAIL = "john.snow@westeros.gov"
SERVER_EMAIL = "serena.kogan@skynet.org"

CA_NAME = "Night's Watch"
SERVER_NAME = "Cyberdyne Systems"

RSA_KEY_SIZE = project_setting(
    "DJ_CA_RSA_KEY_SIZE", sections=["project", "certificates"], rtype=int, default=4096
)
RSA_PUBLIC_EXPONENT = project_setting(
    "DJ_CA_RSA_PUBLIC_EXPONENT",
    sections=["project", "certificates"],
    rtype=int,
    default=65537,
)


ca_validity_days = project_setting(
    "DJ_CA_CA_VALIDITY_DAYS",
    sections=["project", "certificates"],
    rtype=int,
    default=20 * 365,
)
CA_VALIDITY_PERIOD = timedelta(days=ca_validity_days)
server_validity_days = project_setting(
    "DJ_CA_SERVER_VALIDITY_DAYS",
    sections=["project", "certificates"],
    rtype=int,
    default=5 * 365,
)
SERVER_VALIDITY_PERIOD = timedelta(days=server_validity_days)
# endregion

# region Databases
db_name = project_setting("DJ_CA_DB_NAME", sections=["project", "database"])
DATABASES = {
    "default": {"ENGINE": "django.db.backends.postgresql", "NAME": db_name},
}
# endregion

# region i18n/l10n
TIME_ZONE = "UTC"
# endregion

with contextlib.suppress(ImportError):
    from django_ca.local.settings import *  # noqa: F403
