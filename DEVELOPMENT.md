# Development Guide

Technical implementation details and guidelines for developing on this project.

## Database Schema

### Phase 1: User Profiles & Settings (Issue #2)

#### UserProfile Model

- **Table:** `profiles_userprofile`
- **Location:** `apps.profiles.models.profile.UserProfile`
- **Purpose:** Store user personal information and preferences
- **Fields:**
  - `user` (OneToOneField) - Reference to Django User, CASCADE delete
  - `avatar` (ImageField) - Profile picture, optional, stored in `uploads/%Y/%m/%d/`
  - `bio` (TextField) - User biography, optional, default empty string
  - `preferences` (JSONField) - Extensible user preferences, default empty dict
  - `created_at` (DateTimeField) - Auto-set on creation
  - `updated_at` (DateTimeField) - Auto-updated on save
- **Relationships:**
  - OneToOne with User (user.profile)
- **Signals:**
  - Auto-created via post_save signal when User is created (apps.profiles.signals.create_user_profile)

#### UserSettings Model

- **Table:** `profiles_usersettings`
- **Location:** `apps.profiles.models.settings.UserSettings`
- **Purpose:** Store system preferences and LLM configuration
- **Fields:**
  - `user` (OneToOneField) - Reference to Django User, CASCADE delete
  - `theme` (CharField) - UI theme preference: "light", "dark", "auto" (default: "auto")
  - `default_project` (ForeignKey) - Default project for new chats, optional, SET_NULL (added Phase 4)
  - `llm_preferences` (JSONField) - LLM settings, default empty dict
    - Expected structure:
      ```json
      {
        "model": "llama2",
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.95,
        "top_k": 40
      }
      ```
  - `created_at` (DateTimeField) - Auto-set on creation
  - `updated_at` (DateTimeField) - Auto-updated on save
- **Relationships:**
  - OneToOne with User (user.settings)
  - ForeignKey to projects.Project (default_project) - nullable, forward reference for Phase 4
- **Methods:**
  - `get_llm_setting(key, default=None)` - Safely retrieve LLM preference
- **Signals:**
  - Auto-created via post_save signal when User is created (apps.profiles.signals.create_user_settings)

### Project Model (Phase 1 Stub)

- **Table:** `projects_project`
- **Location:** `apps.projects.models.Project`
- **Purpose:** Stub model for Phase 1, full implementation in Phase 4
- **Fields:**
  - `name` (CharField) - Project name
- **Note:** This stub exists to support the FK reference in UserSettings.default_project

## Base Template & Navigation (Issue #5)

### Core App Structure

The `apps.core` app provides shared UI components and foundational templates for the entire application.

```
apps/core/
├── templates/core/
│   ├── base.html                    # Main base template with sidebar layout
│   ├── home.html                    # Home/landing page
│   ├── includes/
│   │   └── _sidebar.html            # Minimal sidebar navigation component
│   └── errors/
│       ├── 404.html                 # Page not found error template
│       └── 500.html                 # Server error template
├── tests/
│   ├── __init__.py
│   └── test_views.py                # View and template rendering tests
├── urls.py                          # Core app URL routing
├── views.py                         # HomeView
├── models.py                        # Empty (core app has no models)
├── admin.py                         # Empty
└── apps.py                          # App configuration
```

### Base Template (`base.html`)

Minimal sidebar-based layout inspired by Open WebUI.

**Features:**

- Clean, minimal design focused on functionality
- Tailwind CSS via CDN
- Alpine.js for interactive components
- Two-column layout: sidebar + main content area
- Dark mode ready with `dark:` Tailwind classes
- Full-height layout (h-screen)

**Blocks for Extension:**

```django
{% block title %}     {# Page title in browser tab #}
{% block content %}   {# Main page content #}
{% block extra_css %} {# Page-specific CSS #}
{% block extra_js %}  {# Page-specific JavaScript #}
```

**Usage - Extending Base Template:**

```django
{% extends "core/base.html" %}

{% block title %}Page Title{% endblock title %}

{% block content %}
  <div class="p-8">
    {# Your content here #}
  </div>
{% endblock content %}
```

### Sidebar Navigation Component (`_sidebar.html`)

Minimal, functional sidebar navigation (Open WebUI style).

**Features:**

- Fixed-width sidebar (w-64)
- Clean borders and minimal styling
- Shows authenticated user menu: Dashboard, Chats, Images, Profile, Settings, Logout
- Shows unauthenticated user menu: Sign In only
- Hover states for interactive feedback
- Dark mode support via `dark:` classes
- Simple, functional design - no fancy animations

**Layout:**

```
Sidebar (w-64)
├── Header with logo/brand
├── Navigation Links (flex-1 to fill space)
│   ├── Dashboard
│   ├── Chats
│   ├── Images
│   └── [More links as needed]
└── User Menu (at bottom)
    ├── Profile
    ├── Settings
    └── Logout
```

**Customization:**

To add new navigation links, edit:

```
apps/core/templates/core/includes/_sidebar.html
```

Simply add more `<a>` tags in the navigation section with the same styling:

```django
<a href="/path" class="block px-4 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-smooth">
  Link Text
</a>
```

### Error Pages

#### 404 Page (`errors/404.html`)

- Extends base template for consistent styling and sidebar
- Shows "Page Not Found" with helpful message
- Links to home and dashboard (for authenticated users)
- Maintains sidebar navigation context

#### 500 Page (`errors/500.html`)

- Extends base template for consistent styling and sidebar
- Shows "Server Error" with helpful message
- Links to home and dashboard (for authenticated users)
- Maintains sidebar navigation context

### Home Page (`home.html`)

Minimal landing/home page that extends `base.html`.

**Features:**

- Simple welcome message for unauthenticated users (Sign In link available in sidebar)
- For authenticated users: welcome message with link to dashboard
- No fancy cards or complex layouts - just clean, functional
- No duplicate buttons - authentication links centralized in sidebar

### Testing

View rendering tests verify:

- Base template renders without errors
- Sidebar navigation is included
- Anonymous users see login/register links
- Authenticated users see dashboard and settings
- 404 pages return correct status code

Run tests:

```bash
poetry run python manage.py test apps.core.tests.test_views
```

### CSS Classes & Utilities

**Transition Classes:**

- `.transition-smooth` - 200ms smooth transition for all properties

**Tailwind Responsive Prefixes:**

- `dark:` - Dark mode styles

**Dark Mode:**

Body uses `dark:` prefixes for dark mode support:

- `dark:bg-gray-950` - Sidebar background
- `dark:border-gray-800` - Borders
- `dark:hover:bg-gray-800` - Hover states
- `dark:text-gray-50` - Text

### Frontend Asset Configuration

**Current Setup:**

- Tailwind CSS: Loaded via Tailwind CDN (includes JIT compiler)
- Alpine.js: Loaded via jsDelivr CDN v3
- No external CSS frameworks or bloat

**Production Optimization:**

- Move Tailwind build to npm pipeline for better tree-shaking
- Pre-compile CSS to reduce initial load
- Store Alpine.js locally in static/js/

## App Structure

### profiles App

```
apps/profiles/
├── models/
│   ├── __init__.py          # Exports UserProfile, UserSettings
│   ├── profile.py           # UserProfile model
│   └── settings.py          # UserSettings model
├── admin/
│   ├── __init__.py          # Exports admin classes
│   ├── profile.py           # UserProfileAdmin
│   └── settings.py          # UserSettingsAdmin
├── forms/
│   ├── __init__.py          # Exports UserProfileForm, UserSettingsForm
│   ├── profile.py           # UserProfileForm (avatar, bio)
│   └── settings.py          # UserSettingsForm (theme)
├── views/
│   ├── __init__.py          # Exports ProfileDetailView, ProfileEditView, SettingsEditView
│   ├── profile.py           # ProfileDetailView, ProfileEditView
│   └── settings.py          # SettingsEditView
├── templates/profiles/
│   ├── profile_detail.html
│   ├── profile_edit.html
│   ├── settings_edit.html   # Settings page template
│   ├── includes/forms/
│   │   ├── _form_errors.html
│   │   ├── _form_actions.html
│   │   ├── _avatar_field.html
│   │   ├── _avatar_script.html
│   │   ├── _bio_field.html
│   │   └── _theme_field.html
│   ├── includes/sections/
│   │   ├── _page_title.html
│   │   ├── _account_info.html
│   │   ├── _account_info_section.html
│   │   ├── _avatar_section.html
│   │   └── _bio_section.html
│   ├── includes/header/
│   │   └── _page_header.html
│   └── includes/footer/
│       └── _profile_footer.html
├── tests/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── test_user_profile.py
│   │   └── test_user_settings.py
│   ├── forms/
│   │   ├── __init__.py
│   │   ├── test_profile_form.py
│   │   └── test_settings_form.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── test_profile_edit.py
│   │   └── test_settings_edit.py
│   ├── test_admin.py
│   └── test_models.py       # Legacy (use tests/ subdirs)
├── migrations/              # Django auto-generated migrations
├── apps.py                  # App configuration with signal registration
├── admin.py                 # Imports admin classes (top-level)
├── models.py                # Imports models (top-level)
├── signals.py               # Post-save signal handlers
├── urls.py                  # URL routing for profiles app
└── tests.py                 # Empty (tests in tests/ package)
```

## Testing

### Running Tests

```bash
# Run all profiles tests
python aiiabox/manage.py test apps.profiles.tests -v 2

# Run specific test module
python aiiabox/manage.py test apps.profiles.tests.models
python aiiabox/manage.py test apps.profiles.tests.forms.test_settings_form
python aiiabox/manage.py test apps.profiles.tests.views.test_settings_edit

# Run specific test class
python aiiabox/manage.py test apps.profiles.tests.test_models.UserProfileCreationTestCase
python aiiabox/manage.py test apps.profiles.tests.forms.test_settings_form.UserSettingsFormTestCase
python aiiabox/manage.py test apps.profiles.tests.views.test_settings_edit.SettingsEditViewTestCase

# Run specific test
python aiiabox/manage.py test apps.profiles.tests.test_models.UserProfileCreationTestCase.test_user_profile_auto_created_on_user_creation
python aiiabox/manage.py test apps.profiles.tests.forms.test_settings_form.UserSettingsFormTestCase.test_form_saves_theme_selection
```

### Test Coverage

- **Models:** 17 tests
  - UserProfile auto-creation and defaults
  - UserProfile field behavior (bio, preferences, avatar)
  - UserSettings auto-creation and defaults
  - UserSettings theme choices and LLM preferences
  - Custom method testing (get_llm_setting, **str**)
  - Cascade deletion behavior
  - Multi-user independence
- **Forms:** 17 tests
  - UserProfileForm: 10 tests (avatar validation, field exclusions, save behavior)
  - UserSettingsForm: 14 tests (theme selection, field exclusions, radio widget, theme choices)
- **Views:** 13 tests
  - ProfileEditView: 13 tests (auth, form rendering, updates, redirects, multi-user isolation)
  - SettingsEditView: 13 tests (auth, form rendering, theme updates, redirects, multi-user isolation)
- **Admin:** 8 tests
  - Admin display methods (user_display, has_avatar)
  - Custom display logic with full names and usernames

**Total: 55 tests**

### Test Philosophy

- Only custom business logic is tested (not Django framework)
- Signal handlers tested via model creation tests
- Admin display methods tested directly without HTTP requests
- Form validation and view behavior tested via integration tests
- Follows CLAUDE.md "DO NOT TEST EXTERNAL CODE" principle

## Signals

### User Profile Auto-Creation

- **Signal:** `django.db.models.signals.post_save` on User model
- **Handler:** `apps.profiles.signals.create_user_profile`
- **Behavior:** Creates UserProfile automatically when new User is created
- **Triggered On:** User creation only (checked via `created` parameter)

### User Settings Auto-Creation

- **Signal:** `django.db.models.signals.post_save` on User model
- **Handler:** `apps.profiles.signals.create_user_settings`
- **Behavior:** Creates UserSettings automatically when new User is created
- **Triggered On:** User creation only (checked via `created` parameter)

### Registration

- Signals are registered in `apps.profiles.apps.ProfilesConfig.ready()` method
- Imported in `apps.profiles.apps.py` to ensure signal handlers are active

## Views & Forms

### User Profile Edit View

- **URL:** `/profile/edit/`
- **Name:** `profiles:profile_edit`
- **Class:** `apps.profiles.views.ProfileEditView`
- **Form:** `UserProfileForm`
- **Model:** `UserProfile`
- **Authentication:** LoginRequiredMixin (redirects to login if not authenticated)
- **Behavior:**
  - GET: Shows profile edit form with avatar and bio fields
  - POST (valid): Saves changes and redirects to profile detail page
  - POST (invalid): Re-renders form with validation errors
- **Template:** `profiles/profile_edit.html`

### User Settings Edit View

- **URL:** `/settings/edit/`
- **Name:** `profiles:settings_edit`
- **Class:** `apps.profiles.views.SettingsEditView`
- **Form:** `UserSettingsForm`
- **Model:** `UserSettings`
- **Authentication:** LoginRequiredMixin (redirects to login if not authenticated)
- **Behavior:**
  - GET: Shows settings form with theme preference options
  - POST (valid): Saves changes and redirects to profile detail page
  - POST (invalid): Re-renders form with validation errors
- **Template:** `profiles/settings_edit.html`
- **Theme Options:** light, dark, auto (system preference)

### UserProfileForm

- **Location:** `apps.profiles.forms.UserProfileForm`
- **Model:** `UserProfile`
- **Fields:**
  - `avatar` (ImageField) - Optional, max 10MB
  - `bio` (TextField) - Optional
- **Excludes:** user, created_at, updated_at, preferences
- **Validation:**
  - Avatar size cannot exceed 10MB
  - Both fields are optional
- **Widget Customization:**
  - Avatar: FileInput with image/\* accept filter
  - Bio: Textarea with 4 rows, placeholder text

### UserSettingsForm

- **Location:** `apps.profiles.forms.UserSettingsForm`
- **Model:** `UserSettings`
- **Fields:**
  - `theme` (ChoiceField) - Required, RadioSelect widget
- **Excludes:** user, default_project, llm_preferences, created_at, updated_at
- **Theme Choices:**
  - "light" - Light theme
  - "dark" - Dark theme
  - "auto" - Auto (System Preference)
- **Validation:**
  - Theme must be a valid choice from THEME_CHOICES
  - Theme is a required field

## Admin Interface

### UserProfile Admin

- **URL:** `/admin/profiles/userprofile/`
- **Display Columns:** user (with full name), has_avatar, created_at, updated_at
- **Read-Only Fields:** user, created_at, updated_at
- **Filterable:** created_at, updated_at
- **Searchable:** username, email, first_name, last_name
- **Custom Display Methods:**
  - `user_display()` - Shows "John Doe (johndoe)" or "johndoe"
  - `has_avatar()` - Boolean indicator for avatar presence

### UserSettings Admin

- **URL:** `/admin/profiles/usersettings/`
- **Display Columns:** user (with full name), theme, created_at, updated_at
- **Read-Only Fields:** user, created_at, updated_at
- **Filterable:** theme, created_at, updated_at
- **Searchable:** username, email, first_name, last_name
- **Custom Display Methods:**
  - `user_display()` - Shows "Jane Smith (janesmith)" or "janesmith"

## Migration Notes

### Phase 1 Migrations

- `0001_initial` migrations created for both profiles and projects apps
- Migrations create UserProfile, UserSettings, and Project tables
- Run migrations with: `python aiiabox/manage.py migrate`

### Future Migrations (Phase 4)

- Will need to populate UserSettings.default_project with actual Project references
- No schema changes needed for Phase 1-3 (extensions via JSONField)

## Code Standards Applied

### Architecture

- Follows CLAUDE.md "Orthogonal Systems & Decoupling" principle
- Each app has single, well-defined responsibility
- No circular imports or cross-app coupling

### Naming

- Models: PascalCase (UserProfile, UserSettings)
- Fields: snake_case (avatar, llm_preferences)
- Methods: snake_case (get_llm_setting, user_display)
- Constants: UPPERCASE_WITH_UNDERSCORES (THEME_CHOICES)

### Documentation

- Model docstrings explain purpose, fields, and relationships
- Method docstrings document parameters, behavior, and return values
- Comments explain signal handlers and why they exist

### Code Quality

- 4-space Python indentation (per CLAUDE.md)
- Type hints in docstrings for clarity
- PEP 8 compliance
- DRY principle applied (no code duplication)

## Next Steps (Phase 2+)

### Phase 2: Chat System

- Create Chat and Message models
- Build chat UI and API endpoints
- Integrate with UserProfile for user ownership

### Phase 3: LLM Integration

- Use UserSettings.llm_preferences for LLM configuration
- Implement context window management
- Add token tracking to Message model

### Phase 4: Projects

- Implement full Project model
- Add project field to Chat model
- Populate UserSettings.default_project
- Implement project-level settings via JSONField

## API Authentication (Phase 2.2 - Issue #25)

### Refactored Architecture (Issue #25 - Focused Modules)

The monolithic `apps.api` app has been refactored into focused, single-responsibility modules following CLAUDE.md principles:

- **`apps.auth`** - Authentication functionality (tokens, signals, views, serializers)
- **`apps.permissions`** - Permission classes and logic

This refactoring improves maintainability, testability, and follows orthogonal system design principles.

### Token-Based Authentication

The API uses Django REST Framework's TokenAuthentication for programmatic access.

#### Setup

- DRF configured in `config/settings.py`
- Token model: `rest_framework.authtoken.models.Token`
- Tokens auto-created when users are created via signal in `apps.auth.signals.auth.create_auth_token`

#### Getting Your Token

**Option 1: Retrieve in Admin**

1. Login to `/admin/`
2. Navigate to "Tokens" under "Auth Token" section
3. View your token (masked as `XXXXXXXXX...XXXXXXXXX`)

**Option 2: API Endpoint (requires authentication)**

Logged-in users can retrieve their token:

```bash
# With session authentication (browser)
curl -X GET http://localhost:8000/api/auth/token/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"

# Response:
{
  "token": "1234567890abcdef1234567890abcdef12345678",
  "created": "2025-01-15T10:30:00Z"
}
```

#### Using Your Token

**HTTP Header Format:**

```
Authorization: Token YOUR_TOKEN_HERE
```

**Example Requests:**

```bash
# Get your token (verify authentication works)
curl -X GET http://localhost:8000/api/auth/token/ \
  -H "Authorization: Token 1234567890abcdef1234567890abcdef12345678"

# With Python requests
import requests
headers = {
    "Authorization": "Token 1234567890abcdef1234567890abcdef12345678"
}
response = requests.get("http://localhost:8000/api/auth/token/", headers=headers)
```

**With VSCode Plugin/CLI (Phase 7-8):**

```yaml
# ~/.aiia/config.yaml
api:
  url: http://localhost:8000
  token: 1234567890abcdef1234567890abcdef12345678
```

#### Token Security

- **Storage:** Keep tokens in environment variables or config files, never in code
- **Transmission:** Always use HTTPS in production (Bearer Token over HTTP is insecure)
- **Rotation:** Delete token in admin to revoke access
- **Expiration:** No built-in expiration (tokens valid until deleted)

#### API Endpoints (Phase 2+)

| Endpoint                    | Method | Auth     | Description                 |
| --------------------------- | ------ | -------- | --------------------------- |
| `/api/auth/token/`          | GET    | Required | Get current user's token    |
| `/api/chats/`               | GET    | Required | List user's chats (Phase 2) |
| `/api/chats/`               | POST   | Required | Create new chat (Phase 2)   |
| `/api/chats/{id}/`          | GET    | Required | Get chat detail (Phase 2)   |
| `/api/chats/{id}/messages/` | POST   | Required | Add message (Phase 2)       |

#### Permission Classes

All API endpoints use these permission classes by default:

- `IsAuthenticated` - User must provide valid token
- Can override per-endpoint with custom classes like `apps.permissions.permissions.IsOwnerOrReadOnly`

#### Benefits of Focused Module Architecture

- **Single Responsibility:** Each module has one clear purpose
- **Orthogonal Design:** Modules are independent and loosely coupled
- **Better Testability:** Focused modules are easier to test in isolation (13 total tests)
- **Maintainability:** Changes to one module don't affect others
- **Scalability:** Easy to extend each module independently
- **Django Compatibility:** Resolved app label conflicts with built-in `auth` app

#### Admin Token Management

**Location:** `/admin/authtoken/token/`

**Features:**

- **List View:** Shows all tokens with user, masked token, and creation date
- **Detail View:** Shows full token (read-only), user, and creation timestamp
- **Search:** Find tokens by username, email, first name, or last name
- **Filters:** Filter by creation date
- **Delete:** Revoke access by deleting token
- **Regenerate:** Delete and make next API request to auto-create new token

**Permissions:**

- Only admin/staff can view tokens
- Manual token creation is disabled (auto-created via signal)
- Staff can delete tokens to revoke access

#### Testing Token Auth

```bash
# Test with valid token
curl -X GET http://localhost:8000/api/auth/token/ \
  -H "Authorization: Token YOUR_TOKEN"
# Response: 200 OK with token data

# Test without token
curl -X GET http://localhost:8000/api/auth/token/
# Response: 401 Unauthorized

# Test with invalid token
curl -X GET http://localhost:8000/api/auth/token/ \
  -H "Authorization: Token invalid123"
# Response: 401 Unauthorized
```

#### Troubleshooting

**401 Unauthorized - "Authentication credentials were not provided"**

- Missing `Authorization` header
- Token not in header (check spacing and format)

**401 Unauthorized - "Invalid token"**

- Token is invalid/malformed
- Token was deleted (revoked)
- Token belongs to deleted user

**Token endpoint returns 200 but claims it's unauthenticated**

- Check that `rest_framework.authentication.TokenAuthentication` is configured
- Verify token is valid in admin
- Check `DEFAULT_AUTHENTICATION_CLASSES` in settings.py

#### App Structure

**Authentication Module (`apps.auth/`):**

```
apps/auth/
├── admin.py               # TokenAdmin for admin interface
├── apps.py                # App config with signal registration (label: 'apps_auth')
├── models.py              # Uses DRF's built-in Token model
├── serializers/
│   ├── __init__.py        # Exports TokenSerializer
│   └── auth.py            # TokenSerializer for responses
├── signals/
│   ├── __init__.py        # Exports create_auth_token
│   └── auth.py            # Auto-create token on user creation
├── urls.py                # Auth endpoint routing (/api/auth/token/)
├── views/
│   ├── __init__.py        # Exports TokenView
│   └── auth.py            # TokenView for token retrieval
└── tests/
    ├── __init__.py        # Exports test classes
    └── auth.py            # Token signal, view, serializer tests (7 tests)
```

**Permissions Module (`apps.permissions/`):**

```
apps/permissions/
├── admin.py               # Empty (permissions are code-only)
├── apps.py                # App configuration
├── models.py              # Empty (permissions are code-only)
├── permissions/
│   ├── __init__.py        # Exports IsOwnerOrReadOnly
│   └── base.py            # IsOwnerOrReadOnly permission class
├── urls.py                # Empty (permissions used by other views)
└── tests/
    ├── __init__.py        # Exports test classes
    └── permissions.py     # Permission class tests (6 tests)
```
