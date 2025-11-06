# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 2: Chat System Core

#### Chat Models & Message Storage

**Added**

- New `apps/chats/` Django app for chat management and message storage
  - Organized module structure following CLAUDE.md best practices
  - `apps/chats/models/` - Focused model definitions
  - `apps/chats/tests/` - Comprehensive test suite
  - `apps/chats/admin/` - Django admin interface
- Chat model (`apps/chats/models/chat.py`)
  - `user` (ForeignKey) - Chat owner with cascading delete
  - `title` (CharField, max_length=255) - Chat title
  - `created_at` (DateTimeField, auto_now_add=True) - Creation timestamp
  - `updated_at` (DateTimeField, auto_now=True) - Last update timestamp
  - `metadata` (JSONField, default=dict) - Flexible metadata storage for future features
  - Database index on `(user, -updated_at)` for efficient user chat queries
  - Default ordering by `updated_at` descending (newest first)
  - Docstring with assumptions and contract documentation
- Message model (`apps/chats/models/message.py`)
  - `chat` (ForeignKey) - Parent chat with cascading delete
  - `user` (ForeignKey) - Message author
  - `content` (TextField) - Message content (supports long text)
  - `role` (CharField, choices=['user', 'assistant', 'system'], db_index=True) - Message role for LLM conversation
  - `tokens` (IntegerField, default=0, validators=[MinValueValidator(0)]) - Token count for cost tracking
  - `created_at` (DateTimeField, auto_now_add=True) - Message timestamp
  - Database indexes on `(chat, created_at)`, `(user, created_at)`, and `(role)` for efficient queries
  - Default ordering by `created_at` ascending (chronological)
  - Docstring with assumptions and contract documentation
- Admin interface (`apps/chats/admin/chat.py`)
  - ChatAdmin with inline message display
  - MessageAdmin for individual message management
  - List displays with filtering and search capabilities
  - Read-only timestamps and computed fields
- Database migrations (`apps/chats/migrations/0001_initial.py`)
  - Creates `chats_chat` and `chats_message` tables
  - Sets up all indexes for query optimization
- Comprehensive test suite (52 tests, 100% coverage)
  - ChatModelTests (25 tests)
    - Model creation with required and optional fields
    - Metadata storage and modification
    - Timestamps (auto_now_add and auto_now behavior)
    - User relationships and isolation
    - Chat ordering and filtering
    - Cascading delete behavior
    - Queryset operations (filter, count, exists, bulk_create, get, update, delete)
  - MessageModelTests (27 tests)
    - Model creation with required and optional fields
    - Role validation (user/assistant/system)
    - Token counting and storage
    - Timestamps (auto_now_add behavior)
    - Long text content support
    - Unicode and special character support
    - Chat and user relationships
    - Message ordering (chronological)
    - Cascading delete behavior
    - Conversation flow testing with realistic multi-turn dialogs
    - Queryset operations (filter by role/chat/user, bulk_create, get, update, delete)
  - Test organization following CLAUDE.md guidelines
    - Uses `django.test.TestCase` for proper database isolation
    - Uses `setUpTestData` for efficient test fixture creation
    - Each test is focused on single behavior
    - Clear assertion methods (assertEqual, assertGreater, assertIn, etc.)
    - Docstrings explaining test purpose

**Updated**

- `config/settings.py` - Added `"apps.chats"` to INSTALLED_APPS (between `apps.projects` and `apps.auth`)

**Database**

- New migration: `apps/chats/migrations/0001_initial.py`
  - Creates Chat model with user FK, title, timestamps, metadata
  - Creates Message model with chat FK, user FK, content, role, tokens, created_at
  - Creates indexes for efficient querying:
    - Chat: `(user, -updated_at)` for user's chats ordered by recency
    - Message: `(chat, created_at)` for chat's messages in chronological order
    - Message: `(user, created_at)` for user's messages across chats
    - Message: `(role)` for role-based filtering

**Technical Details**

- Models use string references for clarity and decoupling
- JSONField for metadata enables future Phase 3 features (system_prompt, model_name, settings)
- Message role choices enable LLM integration (user/assistant/system roles)
- Token field prepares for cost tracking and context window management (with MinValueValidator(0) for data integrity)
- Cascading deletes ensure data integrity (delete chat → delete messages)
- Database indexes optimize common query patterns
- Models follow orthogonal systems principle - self-contained, no cross-app dependencies

**Notes**

- Models are foundational for Phase 2 API endpoints (CRUD operations)
- Metadata field design allows storing model settings without schema migrations
- Test coverage at 100% (52/52 tests passing, all code paths covered)
- Models are fully documented with docstrings explaining assumptions and contracts

#### Issue #25: API Authentication & Token Management

**Added**

- Django REST Framework (DRF) integration with TokenAuthentication
  - Added `djangorestframework` dependency to `pyproject.toml`
  - Configured DRF in `config/settings.py` with token auth settings
  - Added `rest_framework` and `rest_framework.authtoken` to INSTALLED_APPS
- New `apps/auth/` Django app for API token authentication
  - `apps/auth/apps.py` - App configuration with signal registration
  - `apps/auth/models.py` - Uses DRF's built-in Token model
  - `apps/auth/serializers.py` - TokenSerializer for API responses
  - `apps/auth/views.py` - TokenView for token retrieval/creation
  - `apps/auth/urls.py` - API endpoint routing with `auth:` namespace
  - `apps/auth/admin.py` - TokenAdmin for token management in admin interface
  - `apps/auth/tests/` - Comprehensive token authentication tests
- New `apps/permissions/` Django app for API permission classes
  - `apps/permissions/permissions.py` - IsOwnerOrReadOnly permission class
  - `apps/permissions/tests/` - Permission class tests
- Token auto-creation signal
  - `apps/auth/signals.py` - Auto-creates Token when User is created
  - Registered in `AuthConfig.ready()` method
  - Ensures every user has an API token
- API token endpoint
  - `GET /api/auth/token/` - Requires authentication, returns user's token
  - Returns `{ "token": "...", "created": "2025-..." }` JSON
  - Auto-creates token if deleted (via get_or_create logic)
- TokenAdmin in Django admin
  - `/admin/authtoken/token/` - List all user tokens
  - `user_display()` - Shows user with full name if available
  - `token_preview()` - Shows masked token (first 10 + ... + last 10)
  - `token_display()` - Shows full token in detail view (read-only)
  - Disabled manual token creation (auto-created via signal)
  - Allows deletion to revoke API access
  - Searchable by username, email, first_name, last_name
- Comprehensive test suite (16 tests, 100% pass rate)
  - Token signal, view, and serializer tests
  - Permission class tests
  - Tests for:
    - Token auto-creation on user creation
    - Unique tokens per user
    - Token get_or_create logic in view
    - Serializer field validation
    - Permission enforcement (read/write access control)
  - All tests follow CLAUDE.md principle: only tests custom business logic

**Updated**

- `config/urls.py` - Added API URL routing with `path("api/", include("apps.auth.urls"))`
- `config/settings.py` - Added both `apps.auth` and `apps.permissions` to INSTALLED_APPS
- `config/settings.py` - Added DRF configuration:
  ```python
  REST_FRAMEWORK = {
      "DEFAULT_AUTHENTICATION_CLASSES": [
          "rest_framework.authentication.TokenAuthentication",
      ],
      "DEFAULT_PERMISSION_CLASSES": [
          "rest_framework.permissions.IsAuthenticated",
      ],
  }
  ```

**Database**

- DRF TokenAuthentication migrations applied
  - `authtoken.0001_initial` - Creates `authtoken_token` table
  - `authtoken.0002_auto_20160226_1747` - Auto-migration
  - `authtoken.0003_tokenproxy` - Token proxy model
  - `authtoken.0004_alter_tokenproxy_options` - Options update

**Technical Details**

- Token format: 40-character hex string (DRF standard)
- Token tied to User model via OneToOne relationship
- Auto-created immediately when user is created via signal
- Idempotent token endpoint (returns same token on multiple calls)
- Token deletion revokes API access
- Next API request after deletion will create new token

**App Structure (Refactored)**

Following CLAUDE.md orthogonal systems principle:

- `apps/auth/` - Focused on token authentication
- `apps/permissions/` - Focused on authorization/permission logic
- Loose coupling allows independent evolution and testing
- Clear separation of concerns: authentication vs authorization

**Notes**

- Ready for Phase 7 (VSCode Plugin) and Phase 8 (CLI) which need token auth
- Tokens stored securely in database (not in code/config)
- Admin can view token previews and revoke access
- TokenAdmin prevents manual token creation (must be auto-created)
- Backward compatible - session auth still works for web interface
- Refactored into separate apps for better orthogonality and maintainability

### Phase 1: Foundation & Authentication

#### Issue #8: Error Pages (404 & 500)

**Added**

- Custom 404 error page handler in `apps/core/views.py`
  - `handler_404(request, exception=None)` function
  - Renders `core/errors/404.html` template
  - Returns proper 404 HTTP status code
  - Displays user-friendly message with navigation options
  - Shows "Dashboard" link for authenticated users
- Custom 500 error page handler in `apps/core/views.py`
  - `handler_500(request)` function
  - Renders `core/errors/500.html` template
  - Returns proper 500 HTTP status code
  - Displays user-friendly error message with navigation options
  - Shows "Dashboard" link for authenticated users
- Error handler registration in `aiiabox/config/urls.py`
  - Imported `handler_404` and `handler_500` from `apps.core.views`
  - Set as Django error handlers: `handler404` and `handler500`
  - Ensures custom error pages render instead of default Django pages

**Updated**

- `aiiabox/config/settings.py`
  - Added `"127.0.0.1"` to `ALLOWED_HOSTS` for localhost testing
  - Added `"testserver"` to `ALLOWED_HOSTS` for test environment support
- `apps/core/tests/test_views.py`
  - Added `test_404_handler_renders_custom_template()` test
    - Verifies custom 404 handler renders correct template
    - Confirms 404 status code
    - Validates error message and navigation links display
  - Added `test_500_handler_renders_custom_template()` test
    - Verifies custom 500 handler renders correct template
    - Confirms 500 status code
    - Validates error message and navigation links display

**Note**

- Error templates (`404.html`, `500.html`) were already created in previous work
- Templates extend `base.html` for consistent navigation and styling
- Both templates use Tailwind CSS for professional appearance
- Both templates are responsive and mobile-friendly
- Tests confirm all error pages render correctly with proper content

#### Issue #13: Settings/Preferences Edit Page

**Added**

- `UserSettingsForm` class in `apps/profiles/forms/settings.py`
  - Allows users to edit theme preference (light/dark/auto)
  - Uses RadioSelect widget for better UX
  - Excludes non-editable fields: user, default_project, llm_preferences, timestamps
  - Theme field is required, must be valid choice
  - Extensible for future LLM preference fields
- `SettingsEditView` class-based view in `apps/profiles/views/settings.py`
  - UpdateView for editing UserSettings
  - Requires LoginRequiredMixin authentication
  - Gets current user's settings automatically
  - Redirects to profile detail on successful save
  - Shows form errors on invalid input
- `settings_edit.html` template
  - Mirrors profile_edit.html structure and styling
  - Displays settings page title and description
  - Includes theme field radio buttons
  - Reuses \_form_errors.html and \_form_actions.html includes
  - Mobile-first responsive design with dark mode support
- `_theme_field.html` template partial
  - Reusable theme selection field component
  - Radio button options for light/dark/auto themes
  - Field label, help text, and error display
  - Proper spacing and accessibility
- URL route in `apps/profiles/urls.py`
  - `path("settings/edit/", views.SettingsEditView.as_view(), name="settings_edit")`
- Comprehensive test suite (25 tests)
  - UserSettingsForm: 14 tests
    - Theme validation (light, dark, auto, invalid, empty)
    - Field exclusions (user, default_project, llm_preferences, timestamps)
    - RadioSelect widget verification
    - Save behavior and database persistence
  - SettingsEditView: 13 tests
    - Authentication requirement (LoginRequiredMixin)
    - Form rendering and initialization
    - Theme updates and persistence
    - Multi-user isolation
    - Preservation of other settings fields
    - Default theme value (auto)
    - Redirect behavior

**Technical Details**

- Follows ProfileEditView/ProfileEditForm pattern for consistency
- Uses RadioSelect widget (better UX than dropdown for small choice sets)
- Theme options: "light", "dark", "auto" (from UserSettings.THEME_CHOICES)
- Form validates theme against valid choices
- Proper docstrings on form and view classes
- 25/25 tests passing
- Follows CLAUDE.md standards:
  - Organized form/view modules matching profile patterns
  - Clear single responsibility (form handles validation, view handles routing)
  - Comprehensive docstrings explaining assumptions and behavior
  - LoginRequiredMixin for authentication enforcement
  - Mobile-first responsive template design

**Files Created**

- `apps/profiles/forms/settings.py` - UserSettingsForm
- `apps/profiles/views/settings.py` - SettingsEditView
- `apps/profiles/templates/profiles/settings_edit.html` - Settings page template
- `apps/profiles/templates/profiles/includes/forms/_theme_field.html` - Theme field partial
- `apps/profiles/tests/forms/test_settings_form.py` - UserSettingsForm tests (14 tests)
- `apps/profiles/tests/views/test_settings_edit.py` - SettingsEditView tests (13 tests)

**Files Modified**

- `apps/profiles/forms/__init__.py` - Export UserSettingsForm
- `apps/profiles/views/__init__.py` - Export SettingsEditView
- `apps/profiles/urls.py` - Add settings edit URL route
- `DEVELOPMENT.md` - Updated app structure and testing documentation

**Foundation for Phase 3**

- Settings form framework ready for LLM preference fields in Phase 3
- Theme selection enables dark mode implementation across frontend
- Settings infrastructure extensible for future preference types

#### Issue #6: Authentication Pages (Login & Logout)

**Added**

- `CustomAuthenticationForm` in `apps/core/forms.py`
  - Extends Django's `AuthenticationForm` with Tailwind CSS styling
  - Username field with dark mode support
  - Password field with dark mode support
  - Custom widget classes for consistent form styling across app
  - Focus states and transitions for better UX
- `CustomLoginView` class-based view
  - Uses Django's built-in `LoginView` with custom form
  - Renders `core/auth/login.html` template
  - Redirects authenticated users away from login page
  - Redirects to home page after successful login
- `CustomLogoutView` class-based view
  - Uses Django's built-in `LogoutView`
  - Clears user session on logout
  - Redirects to home page
- `login.html` template - User sign-in form
  - Centered form layout with max-width container
  - Header with sign-in title and welcome message
  - Form fields with Tailwind styling
  - Error message display with color-coded feedback
  - Remember me checkbox (for future functionality)
  - Submit button with hover/active states
  - Footer with admin contact link
  - Mobile-first responsive design
  - Dark mode support with CSS variables
- Authentication configuration in `config/settings.py`
  - `LOGIN_URL = "core:login"` - Redirect for @login_required views
  - `LOGIN_REDIRECT_URL = "core:home"` - Redirect after successful login
- URL routes in `apps/core/urls.py`
  - `path("login/", views.CustomLoginView.as_view(), name="login")`
  - `path("logout/", views.CustomLogoutView.as_view(), name="logout")`
- Comprehensive test suite (11 tests) in `apps/core/tests/test_auth.py`
  - Login page loads and displays form
  - Valid credentials authenticate user and redirect
  - Invalid credentials show error messages
  - Authenticated users redirected from login page
  - Username case-sensitivity documented
  - Logout clears authentication
  - Logout redirects to home page
  - Session handling and cleanup

**Technical Details**

- Uses Django's built-in authentication system (no custom auth)
- Tailwind CSS for responsive, accessible form styling
- Dark mode support with CSS variables and dark: modifiers
- All form inputs use consistent styling patterns
- Error messages display inline with form fields
- Focus states with blue-500 ring for accessibility
- 11/11 tests passing: `python manage.py test apps.core.tests.test_auth`
- Follows CLAUDE.md architecture standards:
  - Form classes separated in dedicated forms.py
  - Class-based views with clear single responsibility
  - Comprehensive docstrings on all classes
  - User-friendly error messages
  - Progressive enhancement (works without JavaScript)

**Files Created**

- `apps/core/forms.py` - CustomAuthenticationForm
- `apps/core/templates/core/auth/login.html` - Login page template
- `apps/core/tests/test_auth.py` - Authentication tests (11 tests)

**Files Modified**

- `apps/core/views.py` - Added CustomLoginView and CustomLogoutView
- `apps/core/urls.py` - Added login and logout URL routes
- `config/settings.py` - Added LOGIN_URL and LOGIN_REDIRECT_URL settings
- `apps/core/templates/core/includes/_sidebar.html` - Changed logout from GET link to POST form (Django requirement)
- `PROJECT_OVERVIEW.md` - Updated Phase 1 deliverables (password reset deferred for single-user scenario)

**Password Reset Deferred**

- Single-user scenario (admin access only) makes traditional password reset unnecessary
- Users can reset passwords via Django admin console if needed
- Reduces scope and complexity per CLAUDE.md simplicity principle
- Can be implemented in future if multi-user support is added

**Integration Points Ready**

- Sidebar navigation links to `/login` for anonymous users
- Sidebar navigation links to `/logout` for authenticated users (red colored)
- Home page template conditional rendering based on user.is_authenticated
- Foundation for @login_required protected views in Phase 2

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
