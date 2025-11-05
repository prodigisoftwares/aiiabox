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
│   ├── base.html                    # Main base template extended by all pages
│   ├── home.html                    # Home page example
│   ├── includes/
│   │   └── _navigation.html         # Responsive navigation component
│   └── errors/
│       ├── 404.html                 # Page not found error template
│       └── 500.html                 # Server error template
├── tests/
│   ├── __init__.py
│   └── test_views.py                # View and template rendering tests
├── urls.py                          # Core app URL routing
├── views.py                         # HomeView for testing base template
├── models.py                        # Empty (core app has no models)
├── admin.py                         # Empty
└── apps.py                          # App configuration
```

### Base Template (`base.html`)

The base template is the foundation for all authenticated and public pages. It includes:

**Features:**

- Meta tags (viewport, OG tags, Twitter card tags)
- Tailwind CSS via CDN (production should use local build)
- Alpine.js via CDN for interactive components
- Navigation component via include
- Named blocks for content extension
- Footer with copyright year
- Smooth transition CSS utilities
- Hamburger menu animation styles

**Blocks for Extension:**

```django
{% block title %}          {# Page title and browser tab #}
{% block og_title %}       {# Open Graph title #}
{% block og_description %} {# Open Graph description #}
{% block twitter_title %}  {# Twitter card title #}
{% block twitter_description %} {# Twitter card description #}
{% block content %}        {# Main page content #}
{% block extra_css %}      {# Page-specific CSS #}
{% block extra_js %}       {# Page-specific JavaScript #}
```

**Usage - Extending Base Template:**

```django
{% extends "core/base.html" %}

{% block title %}My Page Title{% endblock title %}
{% block content %}
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    {# Your page content here #}
  </div>
{% endblock content %}
```

### Navigation Component (`_navigation.html`)

Mobile-first responsive navigation with hamburger menu for mobile devices.

**Features:**

- Sticky header that stays at top on scroll
- Desktop: Horizontal navigation with user dropdown
- Mobile: Hamburger menu toggle with slide animations
- Active state indicators for current page
- User dropdown with profile/settings/logout links
- Keyboard navigation (Escape to close menu)
- Click-away closing on mobile menu
- Accessibility ARIA attributes

**Architecture:**

- Uses Alpine.js component scope: `mobileMenuOpen` boolean from parent
- Desktop navigation hidden with `hidden sm:flex` (mobile-first)
- Mobile menu hidden with `sm:hidden`
- Smooth transitions with `transition-smooth` and `transition-smooth-300` classes

**Alpine.js State Management:**

- `mobileMenuOpen` - Controls mobile menu visibility (managed in base.html)
- `userDropdownOpen` - Controls user dropdown visibility (desktop only)

**Responsive Breakpoints:**

- Mobile (< 640px): Hamburger menu, navigation links in dropdown
- Small+ (≥ 640px): Horizontal navigation visible, hamburger hidden

**Customization:**
To add new navigation links, edit the navigation component at:

```
apps/core/templates/core/includes/_navigation.html
```

### Error Pages

#### 404 Page (`errors/404.html`)

- Extends base template for consistent styling
- Shows "Page Not Found" with helpful links
- Links to home and dashboard (for authenticated users)

#### 500 Page (`errors/500.html`)

- Extends base template for consistent styling
- Shows "Server Error" with helpful messaging
- Links to home and dashboard (for authenticated users)

**Configuration:**
To enable custom error pages, add to settings.py:

```python
TEMPLATES = [
    {
        ...
        "OPTIONS": {
            ...
            "context_processors": [...],
        },
    },
]
```

Then in urls.py add custom error handlers:

```python
handler404 = 'apps.core.views.custom_404'
handler500 = 'apps.core.views.custom_500'
```

### Home Page (`home.html`)

Example page that extends `base.html` to demonstrate:

- How to extend the base template
- Mobile-first responsive card layouts
- Conditional content for authenticated vs. anonymous users
- Proper use of Tailwind CSS and Alpine.js integration

### Testing

View rendering tests verify:

- Base template renders without errors
- Navigation component is included
- Anonymous users see login/register links
- Authenticated users see dashboard and settings
- Footer renders with copyright
- 404 pages return correct status code

Run tests:

```bash
poetry run python manage.py test apps.core.tests.test_views
```

### CSS Classes & Utilities

**Transition Classes:**

- `.transition-smooth` - 200ms smooth transition
- `.transition-smooth-300` - 300ms smooth transition

**Tailwind Responsive Prefixes:**

- `sm:` - Small screens (640px+)
- `md:` - Medium screens (768px+)
- `lg:` - Large screens (1024px+)
- `xl:` - Extra large screens (1280px+)

**Button Styling:**

- Primary: `bg-blue-600 text-white hover:bg-blue-700`
- Secondary: `bg-gray-200 text-gray-900 hover:bg-gray-300`
- Consistent rounded corners: `rounded-lg`

### Frontend Asset Configuration

**Current Setup:**

- Tailwind CSS: Loaded via Tailwind CDN
- Alpine.js: Loaded via jsDelivr CDN
- Production: Should use local built files

**Future Optimization:**

- Move Tailwind build to npm pipeline
- Store Alpine.js locally in static/js/
- Implement CSS/JS minification
- Add cache busting via manifest file

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
├── tests/
│   ├── __init__.py
│   ├── test_models.py       # Model tests (25 tests)
│   └── test_admin.py        # Admin display method tests
├── migrations/              # Django auto-generated migrations
├── apps.py                  # App configuration with signal registration
├── admin.py                 # Imports admin classes (top-level)
├── models.py                # Imports models (top-level)
├── signals.py               # Post-save signal handlers
├── views.py                 # Empty for now
└── tests.py                 # Empty (tests in tests/ package)
```

## Testing

### Running Tests

```bash
# Run all profiles tests
python aiiabox/manage.py test apps.profiles.tests -v 2

# Run specific test class
python aiiabox/manage.py test apps.profiles.tests.test_models.UserProfileCreationTestCase

# Run specific test
python aiiabox/manage.py test apps.profiles.tests.test_models.UserProfileCreationTestCase.test_user_profile_auto_created_on_user_creation
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
- **Admin:** 8 tests
  - Admin display methods (user_display, has_avatar)
  - Custom display logic with full names and usernames

### Test Philosophy

- Only custom business logic is tested (not Django framework)
- Signal handlers tested via model creation tests
- Admin display methods tested directly without HTTP requests
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
