# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 1: Foundation & Authentication

#### Issue #5: Base Template & Navigation System

**Added**

- `apps.core` app for shared UI components and foundational templates
  - Organized as sub-package following CLAUDE.md architecture standards
  - Registered in INSTALLED_APPS
- `base.html` template - Foundation for all pages
  - Meta tags for viewport, OG tags, Twitter card tags
  - Tailwind CSS via CDN integration
  - Alpine.js via CDN integration
  - Named template blocks: title, og_title, og_description, twitter_title, twitter_description, content, extra_css, extra_js
  - Navigation component include with mobile-first approach
  - Footer with copyright year
  - Smooth transition CSS utilities for animations
  - Hamburger menu animation styles
- `_navigation.html` component - Mobile-first responsive navigation
  - Sticky header with shadow on scroll
  - Desktop: Horizontal navigation with user dropdown menu
  - Mobile: Hamburger menu with slide animations
  - Alpine.js state management for menu toggling
  - Click-away and Escape key handling
  - ARIA attributes for accessibility
  - Responsive breakpoints: sm: (640px), md:, lg:, xl:
  - Conditional rendering for authenticated vs. anonymous users
- Error templates
  - `404.html` - Page not found error
  - `500.html` - Server error
  - Both extend base.html for consistent styling
- `home.html` - Example page demonstrating base template extension
  - Mobile-first responsive card layouts
  - Conditional content for authenticated/anonymous users
  - Shows dashboard/profile/settings for authenticated users
  - Shows sign in/register for anonymous users
- `HomeView` class-based view for home page
- Core app URL routing in `apps/core/urls.py`
- Comprehensive test suite (7 tests) covering:
  - Home view renders with correct status code
  - Base template content present
  - Navigation component included
  - Anonymous users see login/register links
  - Authenticated users see dashboard and settings
  - Footer renders with copyright
  - 404 status codes returned for missing pages

**Technical Details**

- Mobile-first design approach (responsive design for mobile first, enhance for desktop)
- Progressive enhancement: core functionality works without JavaScript
- Tailwind CSS for styling (via CDN)
- Alpine.js for interactive components (hamburger menu, dropdowns)
- All templates use 2-space indentation per CLAUDE.md standards
- Follows djlint template formatting standards (double quotes in tags, named endblocks)
- Accessibility built-in: ARIA attributes, focus states, keyboard navigation
- Smooth 200-300ms transitions for animations
- All tests pass: `poetry run python manage.py test apps.core.tests.test_views` (7/7 passing)

**Files Created**

- `apps/core/templates/core/base.html` - Main base template
- `apps/core/templates/core/home.html` - Home page example
- `apps/core/templates/core/includes/_navigation.html` - Navigation component
- `apps/core/templates/core/errors/404.html` - 404 error page
- `apps/core/templates/core/errors/500.html` - 500 error page
- `apps/core/urls.py` - Core app URL routing
- `apps/core/views.py` - HomeView class
- `apps/core/tests/__init__.py` - Tests package initialization
- `apps/core/tests/test_views.py` - View and template rendering tests

**Files Modified**

- `config/settings.py` - Added apps.core to INSTALLED_APPS
- `config/urls.py` - Included core app URLs at root path
- `DEVELOPMENT.md` - Added comprehensive Base Template & Navigation documentation

**Navigation Features Ready for Next Phase**

- All authenticated pages now have consistent navigation
- Mobile hamburger menu prevents users from feeling "stuck" on pages
- Foundation ready for:
  - Login/logout pages (Issue #6)
  - Profile edit pages
  - Settings edit pages
  - Dashboard pages
  - All Phase 2+ pages automatically inherit navigation

**Dependencies Unblocked**

- Issue #5 completion unblocks all other Phase 1 frontend issues
- Login page (Issue #6) can now extend base.html
- All authenticated pages can use navigation component
- Error pages are ready for proper Django error handling

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
