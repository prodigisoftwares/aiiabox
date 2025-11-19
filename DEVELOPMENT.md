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
- Vanilla JavaScript: Stored locally in static/js/
- No external JavaScript frameworks or dependencies

**Production Optimization:**

- Move Tailwind build to npm pipeline for better tree-shaking
- Pre-compile CSS to reduce initial load
- Keep JavaScript minimal and modular (only when necessary)

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

### Chat Views (Phase 2.4a - Issue #37)

#### ChatListView

- **URL:** `/chats/`
- **Name:** `chats:chat_list`
- **Class:** `apps.chats.views.ChatListView`
- **Authentication:** LoginRequiredMixin (redirects to login if not authenticated)
- **Behavior:**
  - GET: Shows paginated list of current user's chats (20 per page)
  - Chats ordered by most recently updated first
  - Returns empty list if user has no chats
- **Authorization:** Queryset filtered by `request.user` (user can only see own chats)
- **Pagination:** 20 chats per page via `paginate_by = 20`
- **Template:** `chats/chat_list.html`

#### ChatDetailView

- **URL:** `/chats/<pk>/`
- **Name:** `chats:chat_detail`
- **Class:** `apps.chats.views.ChatDetailView`
- **Authentication:** LoginRequiredMixin (redirects to login if not authenticated)
- **Behavior:**
  - GET: Shows chat detail with all messages
  - Returns 404 if chat doesn't exist or belongs to another user
- **Authorization:** Queryset filtered by `request.user` (prevents accessing other users' chats)
- **Template:** `chats/chat_detail.html`

#### ChatCreateView

- **URL:** `/chats/create/`
- **Name:** `chats:chat_create`
- **Class:** `apps.chats.views.ChatCreateView`
- **Form:** `ChatForm`
- **Model:** `Chat`
- **Authentication:** LoginRequiredMixin (redirects to login if not authenticated)
- **Behavior:**
  - GET: Shows chat creation form with title field
  - POST (valid): Creates chat and redirects to chat detail page
  - POST (invalid): Re-renders form with validation errors
- **Authorization:** `form_valid()` auto-assigns `chat.user = request.user` (prevents user spoofing)
- **Template:** `chats/chat_form.html`

#### ChatDeleteView

- **URL:** `/chats/<pk>/delete/`
- **Name:** `chats:chat_delete`
- **Class:** `apps.chats.views.ChatDeleteView`
- **Model:** `Chat`
- **Authentication:** LoginRequiredMixin (redirects to login if not authenticated)
- **Behavior:**
  - GET: Shows deletion confirmation page
  - POST: Deletes chat and redirects to chat list
  - Returns 404 if chat doesn't exist or belongs to another user
- **Authorization:** Queryset filtered by `request.user` (prevents deleting other users' chats)
- **Template:** `chats/chat_confirm_delete.html`

### ChatForm

- **Location:** `apps.chats.forms.ChatForm`
- **Model:** `Chat`
- **Fields:**
  - `title` (CharField) - Required, max_length=255
- **Validation:**
  - Title is required
  - Title cannot exceed 255 characters
  - Title is trimmed of leading/trailing whitespace
  - Title cannot be empty or whitespace-only after trimming
- **Widget Customization:**
  - Title: TextInput with Tailwind CSS classes, placeholder "Chat title...", maxlength="255"

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

## Admin Interface (Phase 2.3 - Issue #26)

### Chat Admin Interface

**URL:** `/admin/chats/chat/`

**Features:**

- **List Display:** Shows title, user (with full name and username), message count, created_at, updated_at
- **Filtering:** Filter by creation date (created_at), update date (updated_at), or user
- **Search:** Search by chat title or username
- **Organization:** Fieldsets for Chat Information, Metadata (collapsible), and Timestamps
- **Read-Only Fields:** created_at, updated_at (system-generated)
- **Inline Messages:** View and manage messages directly within chat detail view (MessageInline)

**Custom Display Methods:**

- `user_display()` - Shows user's full name with username fallback (e.g., "John Doe (johndoe)" or "johndoe")
- `message_count()` - Displays total number of messages in the chat

**Example:**

```
Chat List Admin:
┌─────────────────────────────────────────────────────────────────┐
│ Title               │ User              │ Messages │ Created     │
├─────────────────────────────────────────────────────────────────┤
│ Python Tips         │ John Doe (john)   │ 42       │ 2025-01-15  │
│ Django Questions    │ Jane Smith (jane) │ 18       │ 2025-01-14  │
└─────────────────────────────────────────────────────────────────┘
```

### Message Admin Interface

**URL:** `/admin/chats/message/`

**Features:**

- **List Display:** Shows parent chat title, message author (with full name), role, content preview (first 100 chars), created_at
- **Filtering:** Filter by message role (user/assistant/system), creation date, or author
- **Search:** Search by message content, chat title, or username
- **Organization:** Fieldsets for Message Information, Content, and Timestamps
- **Read-Only Fields:** created_at (system-generated)

**Custom Display Methods:**

- `chat_display()` - Shows parent chat title for quick navigation
- `user_display()` - Shows message author's full name with username fallback (e.g., "John Doe (johndoe)" or "johndoe")
- `content_preview()` - Shows first 100 characters of message content with ellipsis if truncated

**Example:**

```
Message List Admin:
┌──────────────────────────────────────────────────────────────────────────┐
│ Chat            │ Author          │ Role      │ Preview              │
├──────────────────────────────────────────────────────────────────────────┤
│ Python Tips     │ John Doe (john) │ user      │ How do I optimize... │
│ Python Tips     │ Assistant       │ assistant │ You can use profile… │
│ Django Q's      │ Jane Smith      │ user      │ What's the best way… │
└──────────────────────────────────────────────────────────────────────────┘
```

### Admin Access

**Login Required:**

1. Create a superuser:

   ```bash
   poetry run python manage.py createsuperuser
   ```

2. Login at `/admin/` with superuser credentials

3. Navigate to "Chats" section to see Chat and Message admin interfaces

**Permissions:**

- Admin users can view, add, change, and delete chats and messages
- Staff users with permissions can perform assigned actions
- Regular users cannot access the admin interface

**Common Admin Tasks:**

- **View all chats:** `/admin/chats/chat/` - See all user conversations
- **View specific chat:** Click chat title to see detail view with inline messages
- **Search chats:** Use search bar to find by title or username
- **Filter chats:** Use sidebar filters to find chats by date or user
- **View all messages:** `/admin/chats/message/` - See all messages across all chats
- **Filter messages:** Filter by role (user/assistant/system), date, or author
- **Search messages:** Search message content by keywords

### App Structure

**Chats Module (`apps.chats/`):**

```
apps/chats/
├── admin/
│   ├── __init__.py        # Exports ChatAdmin, MessageAdmin
│   └── chat.py            # ChatAdmin, MessageAdmin, MessageInline classes
├── models/
│   ├── __init__.py        # Exports Chat, Message
│   ├── chat.py            # Chat model (user-owned conversations)
│   └── message.py         # Message model (individual messages in chats)
├── templates/chats/       # Chat UI templates (Phase 2.1)
├── tests/
│   ├── __init__.py
│   ├── test_chat.py       # Chat model tests
│   └── test_message.py    # Message model tests
├── migrations/            # Django auto-generated migrations
├── apps.py                # App configuration
├── models.py              # Imports models (top-level)
└── urls.py                # URL routing for chats (Phase 2.1)
```

## API Architecture (Phase 2.5: Issue #28)

### Chat API Module Structure

The Chat API provides REST endpoints for programmatic access via CLI, VSCode plugin, and mobile clients.

**Module Location:** `apps/chats/api/`

```
apps/chats/api/
├── __init__.py           # Module exports
├── permissions.py        # IsOwnerOrReadOnly permission class
├── serializers.py        # ChatSerializer, MessageSerializer
├── viewsets.py           # ChatViewSet, MessageViewSet
├── urls.py               # DRF router configuration (nested routes)
├── README.md             # API documentation
└── tests/
    ├── __init__.py
    └── test_api.py       # 28 comprehensive API endpoint tests
```

### Authentication Strategy

**Token-Based Authentication:**

- Uses DRF's `TokenAuthentication`
- Tokens stored in `authtoken_token` table
- Format: `Authorization: Token <token_key>`
- Session auth still used for web interface

**Getting API Token:**

```python
from rest_framework.authtoken.models import Token
user = User.objects.get(username='your_user')
token, created = Token.objects.get_or_create(user=user)
print(token.key)  # Share this securely with client
```

### API Endpoints

**Base URL:** `http://localhost:8000/api/`

#### Chat Endpoints

| Method | Endpoint       | Auth  | Purpose                       |
| ------ | -------------- | ----- | ----------------------------- |
| GET    | `/chats/`      | Token | List user's chats (paginated) |
| POST   | `/chats/`      | Token | Create new chat               |
| GET    | `/chats/{id}/` | Token | Get chat detail               |
| DELETE | `/chats/{id}/` | Token | Delete chat                   |

#### Nested Message Endpoints

| Method | Endpoint                          | Auth  | Purpose             |
| ------ | --------------------------------- | ----- | ------------------- |
| GET    | `/chats/{chat_id}/messages/`      | Token | List chat messages  |
| POST   | `/chats/{chat_id}/messages/`      | Token | Add message to chat |
| GET    | `/chats/{chat_id}/messages/{id}/` | Token | Get single message  |
| DELETE | `/chats/{chat_id}/messages/{id}/` | Token | Delete message      |

### Serializers

**ChatSerializer:**

- **Fields:** id (read-only), user (read-only, auto-set), title, created_at, updated_at, message_count
- **Validation:**
  - `title` required, max 200 chars
  - Empty/whitespace-only titles rejected
- **Method Field:** `message_count` = Message count for chat

**MessageSerializer:**

- **Fields:** id (read-only), chat, user (read-only, auto-set), content, role, tokens, created_at
- **Validation:**
  - `content` required, non-empty
  - `role` must be 'user', 'assistant', or 'system'
  - Auto-sets user from request context
- **create() Method:** Sets user and validates chat ownership

### Permission Classes

**IsOwnerOrReadOnly:**

- **View-Level:** Verifies authenticated user (token valid)
- **View-Level (Nested):** For `/chats/{chat_id}/messages/`, verifies chat exists and user owns it
- **Object-Level:** For individual operations, verifies user owns the object
- **404 vs 403:** Returns 404 for non-existent objects (doesn't leak existence to other users)

### Viewsets

**ChatViewSet:**

- Inherits from `ModelViewSet` (auto-generates CRUD)
- **Auth:** TokenAuthentication
- **Permissions:** IsAuthenticated, IsOwnerOrReadOnly
- **get_queryset():** Filters chats to current user only
- **perform_create():** Auto-sets user from request

**MessageViewSet (Nested):**

- Inherits from `ModelViewSet`
- **Auth:** TokenAuthentication
- **Permissions:** IsAuthenticated, IsOwnerOrReadOnly
- **get_queryset():** Filters messages by chat_pk (nested) AND user ownership
- **perform_create():** Auto-sets user AND validates chat ownership

### Routing Configuration

Uses `drf-nested-routers` library for nested resource routing:

```python
# Main router for chats
router.register(r'chats', ChatViewSet, basename='chat')

# Nested router for messages under each chat
messages_router = NestedSimpleRouter(router, 'chats', lookup='chat')
messages_router.register(r'messages', MessageViewSet, basename='message')
```

**Generated URLs:**

- `/api/chats/` - Chat list/create
- `/api/chats/{id}/` - Chat detail/update/delete
- `/api/chats/{chat_id}/messages/` - Message list/create
- `/api/chats/{chat_id}/messages/{id}/` - Message detail/update/delete

### Pagination

- **Default:** 20 items per page
- **Configurable:** `?page_size=50` (max 100)
- **Response:** Includes `count`, `next`, `previous`, `results`

### Error Handling

**Status Codes:**

- 200: GET success
- 201: POST/create success
- 204: DELETE success
- 400: Validation error (bad input)
- 401: Unauthenticated (missing/invalid token)
- 403: Forbidden (permission denied) - rarely returned, 404 preferred
- 404: Not found (object doesn't exist or user has no access)

**Response Format:**

```json
{
  "detail": "Error message or field errors"
}
```

### Testing

**Test File:** `apps/chats/api/tests/test_api.py`
**Test Count:** 28 comprehensive tests
**Coverage:** >85% of API code

**Test Categories:**

- **Authentication:** Token required, invalid tokens rejected
- **Authorization:** Users see only their own chats/messages
- **CRUD Operations:** Create, read, update, delete for chats and messages
- **Validation:** Title, content, role validation
- **Pagination:** Page navigation, limits
- **HTTP Status Codes:** 200, 201, 204, 400, 403, 404
- **Permission Enforcement:** User isolation verified

**Running Tests:**

```bash
python manage.py test apps.chats.api.tests.test_api
```

### Usage Examples

**Get User's Chats:**

```bash
curl -H "Authorization: Token abc123" http://localhost:8000/api/chats/
```

**Create Chat:**

```bash
curl -X POST \
  -H "Authorization: Token abc123" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Chat"}' \
  http://localhost:8000/api/chats/
```

**Add Message:**

```bash
curl -X POST \
  -H "Authorization: Token abc123" \
  -H "Content-Type: application/json" \
  -d '{"chat":1,"content":"Hello!","role":"user"}' \
  http://localhost:8000/api/chats/1/messages/
```

For full documentation see: `apps/chats/api/README.md`

## Vanilla JavaScript Guidelines

### Philosophy

- **Only use JavaScript when absolutely necessary**
- **Pages must work without JavaScript** - use progressive enhancement
- **Prefer native HTML5 features** over custom solutions
- **Keep code simple and focused** - each script has one responsibility
- **Store scripts locally** in `static/js/` - no CDN dependencies

### When to Use JavaScript

✅ **Use JavaScript for:**

- Modal/dialog management (but use native `<dialog>` element)
- Dropdown menus and toggles
- Form validation feedback (real-time)
- Scroll detection and auto-scroll
- Auto-dismiss notifications
- File upload validation before submission
- Character counters
- Keyboard navigation (Escape, arrows, etc.)

❌ **Don't use JavaScript for:**

- Form submission (use Django forms)
- Page navigation (use HTML links)
- Basic show/hide (use CSS or native `<dialog>`)
- Layout and styling (use HTML and CSS)
- Data that should be server-rendered

### Native HTML5 Features to Use

**Dialogs/Modals:**

```html
<!-- Use native <dialog> instead of custom modal divs -->
<dialog id="rename-form">
  <form method="dialog" @submit.prevent="renameChat(event)">
    <h2>Rename Chat</h2>
    <input type="text" name="title" required />
    <button type="button" onclick="this.closest('dialog').close()">
      Cancel
    </button>
    <button type="submit">Save</button>
  </form>
</dialog>

<script>
  // Open dialog
  document.querySelector("button").onclick = () => {
    document.getElementById("rename-form").showModal();
  };
</script>
```

**Details/Summary (Accordion):**

```html
<!-- Use native <details> for expandable sections -->
<details>
  <summary>Click to expand</summary>
  <p>Content that shows/hides</p>
</details>
```

**Input Validation:**

```html
<!-- Use built-in HTML5 validation -->
<input type="email" required />
<input type="number" min="0" max="100" />
<input
  type="text"
  maxlength="255"
  pattern="[A-Za-z0-9]+"
  title="Letters and numbers only"
/>

<script>
  form.addEventListener("submit", (e) => {
    if (!form.checkValidity()) {
      e.preventDefault();
    }
  });
</script>
```

### Vanilla JavaScript Patterns

**Event Listeners (Instead of Inline Handlers):**

```javascript
// Good - Use addEventListener
document.querySelector(".button").addEventListener("click", () => {
  // Handle click
});

// Bad - Avoid inline onclick
// <button onclick="doSomething()">Click</button>
```

**Simple Component Pattern:**

```javascript
// Encapsulate component logic in a function
function chatDetail() {
  const state = {
    chatId: null,
  };

  const methods = {
    init() {
      state.chatId = window.location.pathname.split("/")[2];
      this.setupListeners();
    },

    setupListeners() {
      document.querySelector(".rename-btn").addEventListener("click", () => {
        document.getElementById("rename-form").showModal();
      });
    },

    async renameChat(event) {
      const form = event.target;
      const newTitle = form.querySelector('input[name="title"]').value.trim();

      if (!newTitle) {
        alert("Title cannot be empty");
        return;
      }

      try {
        const response = await fetch(`/api/chats/${state.chatId}/`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken":
              document.querySelector("[name=csrfmiddlewaretoken]")?.value || "",
          },
          body: JSON.stringify({ title: newTitle }),
        });

        if (!response.ok) {
          alert("Error updating chat");
          return;
        }

        document.querySelector("h1").textContent = newTitle;
        document.getElementById("rename-form").close();
      } catch (error) {
        console.error("Error:", error);
        alert("Error updating chat");
      }
    },
  };

  return methods;
}

// Initialize
const detail = chatDetail();
document.addEventListener("DOMContentLoaded", () => detail.init());
```

**Auto-Scroll Pattern:**

```javascript
function chatScroller() {
  const container = document.getElementById("messages-container");

  return {
    scrollToBottom() {
      if (container) {
        setTimeout(() => {
          container.scrollTop = container.scrollHeight;
        }, 0);
      }
    },

    observeMessages() {
      const observer = new MutationObserver(() => this.scrollToBottom());
      observer.observe(container, { childList: true, subtree: true });
    },

    init() {
      this.scrollToBottom();
      this.observeMessages();
    },
  };
}

chatScroller().init();
```

**Click-Away Pattern (Close on Outside Click):**

```javascript
const modal = document.getElementById("modal");
const openBtn = document.querySelector(".open-modal");

openBtn.addEventListener("click", () => {
  modal.showModal();
});

// Close when clicking outside the dialog
modal.addEventListener("click", (e) => {
  // Click on dialog itself, not inside it
  if (e.target === modal) {
    modal.close();
  }
});

// Close on Escape key (native to <dialog>)
// No JavaScript needed - browsers handle this automatically
```

**Keyboard Navigation Pattern:**

```javascript
function dropdownMenu() {
  const menu = document.querySelector(".dropdown-menu");
  const items = menu.querySelectorAll('[role="menuitem"]');
  let currentIndex = -1;

  const methods = {
    handleKeydown(e) {
      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          currentIndex = Math.min(currentIndex + 1, items.length - 1);
          items[currentIndex].focus();
          break;
        case "ArrowUp":
          e.preventDefault();
          currentIndex = Math.max(currentIndex - 1, 0);
          items[currentIndex].focus();
          break;
        case "Escape":
          menu.close();
          break;
      }
    },

    init() {
      menu.addEventListener("keydown", (e) => this.handleKeydown(e));
    },
  };

  return methods;
}

dropdownMenu().init();
```

**Form Validation (Client-Side Optional):**

```javascript
// Optional client-side validation for UX
// Server-side validation is ALWAYS authoritative

const form = document.querySelector("form");
const titleInput = form.querySelector('input[name="title"]');
const errorDiv = document.querySelector(".error-message");

titleInput.addEventListener("blur", () => {
  const value = titleInput.value.trim();

  if (!value) {
    errorDiv.textContent = "Title cannot be empty";
    titleInput.classList.add("has-error");
  } else if (value.length > 255) {
    errorDiv.textContent = "Title must be 255 characters or less";
    titleInput.classList.add("has-error");
  } else {
    errorDiv.textContent = "";
    titleInput.classList.remove("has-error");
  }
});

// Clear error when user starts typing again
titleInput.addEventListener("input", () => {
  if (titleInput.classList.contains("has-error")) {
    errorDiv.textContent = "";
    titleInput.classList.remove("has-error");
  }
});
```

### Structure for Complex Interactions

For larger interactive features, organize scripts like this:

```
static/js/
├── chat-detail.js      # Chat detail page interactions
├── chat-list.js        # Chat list page interactions
├── forms.js            # Form-related helpers
└── utils.js            # Shared utilities (scrolling, etc.)
```

Each file should export a single component or utility:

```javascript
// static/js/chat-detail.js
export function chatDetail() {
  // ... component logic
}

// main.js or in template
import { chatDetail } from "./chat-detail.js";
document.addEventListener("DOMContentLoaded", () => chatDetail().init());
```

### Testing JavaScript

Since JavaScript is optional and minimal, focus on testing:

- **Django view tests** - Test server-side logic (required)
- **Browser manual testing** - Test interactive features work
- **Accessibility testing** - Ensure keyboard navigation works
- **Network tests** - Fetch requests succeed with valid tokens

### Common Mistakes to Avoid

❌ **Don't:**

- Use JavaScript frameworks when HTML/CSS is sufficient
- Hide critical functionality behind JavaScript
- Forget server-side validation (even with client-side validation)
- Use inline `onclick` handlers or `eval()`
- Make JavaScript dependent on external global state
- Write "magic" JavaScript that does unexpected things

✅ **Do:**

- Use progressive enhancement - start with HTML
- Keep JavaScript focused and modular
- Always validate on server
- Use event listeners and clean separation of concerns
- Document why JavaScript is needed
- Test without JavaScript to ensure graceful degradation
