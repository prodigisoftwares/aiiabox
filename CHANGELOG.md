# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 1: Foundation & Authentication

#### Issue #2: User Profile & Settings Models

**Added**

- `apps.profiles` app with organized module structure (models/, admin/, tests/)
- `UserProfile` model for storing user personal information
  - OneToOne relationship with Django User model
  - Fields: avatar (with uploads/%Y/%m/%d/ path), bio, preferences (JSONField)
  - Timestamps: created_at, updated_at
  - Auto-created via post_save signal when User is created
- `UserSettings` model for storing system preferences
  - OneToOne relationship with Django User model
  - Fields: theme (light/dark/auto), default_project (FK to projects.Project for Phase 4), llm_preferences (JSONField)
  - Timestamps: created_at, updated_at
  - Auto-created via post_save signal when User is created
  - Helper method: `get_llm_setting(key, default=None)` for safe LLM preference retrieval
- `UserProfileAdmin` and `UserSettingsAdmin` classes with custom display methods
  - `user_display()` - Shows user full name with fallback to username
  - `has_avatar()` - Boolean indicator for avatar presence
- Post-save signals in `apps.profiles.signals` for automatic UserProfile and UserSettings creation
- Comprehensive test suite (25 tests) covering:
  - Model auto-creation on User creation
  - Default values and field behavior
  - Custom methods and helpers
  - Admin display methods
  - Cascade deletion on User deletion
  - Multi-user independence

**Technical Details**

- Models properly reference Django's built-in User model (OneToOne pattern)
- Forward reference to projects.Project via string for Phase 4 compatibility
- Minimal Project stub model in apps.projects to support FK resolution
- All tests pass: `python manage.py test apps.profiles.tests` (25/25 passing)
- Follows CLAUDE.md architecture standards:
  - App as sub-package with organized modules
  - Proper app registration in apps.py with signal handling
  - Custom business logic only in tests (no framework testing)
  - 4-space Python indentation
  - Comprehensive docstrings on models and methods

**Migration Files Created**

- `apps/profiles/migrations/0001_initial.py` - UserProfile and UserSettings tables
- `apps/projects/migrations/0001_initial.py` - Project stub table
