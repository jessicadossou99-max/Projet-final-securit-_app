"""Disposable, file-backed configuration for the CI DAST runner only."""
from .base import *

DEBUG = False
SECRET_KEY = "dast-runner-only-not-a-deployment-secret"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "dast.sqlite3"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
