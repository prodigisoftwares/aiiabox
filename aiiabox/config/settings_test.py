"""
Django settings for testing with optimizations for speed.

This file extends the production settings with test-specific optimizations:
- SQLite in-memory database (10x faster than PostgreSQL)
- MD5 password hashing (10x faster than PBKDF2 - security not needed in tests)
- Console email backend (no I/O overhead)
- Disabled migrations (fresh database created for each test session)
"""

from config.settings import *  # noqa: F401, F403

# Use in-memory SQLite database for tests (10x faster than PostgreSQL)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": True,
    }
}

# Use MD5 password hashing for tests (10x faster than PBKDF2)
# Security is not a concern in tests, only speed
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use console email backend (no I/O overhead)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Disable migrations for tests (fresh database created for each test session)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()
