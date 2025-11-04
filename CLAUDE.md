# CLAUDE.md - General Development Best Practices

A comprehensive guide to development best practices for building modern web applications with Django, Tailwind CSS, and Alpine.js. These practices are universally applicable across projects and should be adapted to your specific needs.

## Core Development Philosophy

### Principles

- **Simplicity First:** Write just enough code to get the job done, then refactor according to best practices
- **Avoid Over-Architecture:** Do everything possible to avoid overthinking or over-architecting solutions
- **Quality Over Speed:** No shortcuts, no "good enough" - everything done right the first time
- **Documentation First:** Always read project documentation before coding
- **Consistency:** Follow established patterns and conventions throughout the codebase
- **Evidence-Based:** Check existing code before claiming work is needed
- **Mobile-First:** Design and build for mobile devices first, then enhance for larger screens
- **Progressive Enhancement:** Core functionality should work without JavaScript; JS adds enhancement
- **Accessibility:** Build inclusive experiences for all users
- **Write Less Code:** Every line of code is a liability. Prefer existing frameworks and Django built-ins over custom solutions
- **Explicit Over Implicit:** Make code behavior obvious and clear - avoid "magic" and implicit conventions
- **Refactor Regularly:** Fix design issues, duplication, and technical debt as they're discovered, not later

### Code Style Standards

- **Python:** Follow Django best practices, PEP 8, **4-space indentation (spaces, not tabs)**
- **HTML/CSS:** Mobile-first responsive design, **2-space indentation (not 4-space)**
- **JavaScript:** Minimal, progressive enhancement, **2-space indentation**
- **Database:** PostgreSQL with proper migrations
- **Indentation Standards:** Python=4 spaces, HTML/CSS/JS=2 spaces (strictly enforced)

---

## Clean Code Best Practices

This section consolidates all clean code principles used throughout the codebase. These principles apply to Python, JavaScript, templates, and all other code.

### Naming Conventions

**Use Meaningful, Pronounceable, and Searchable Names:**

- **Meaningful names reveal intent:** Variable names should answer why something exists, what it is, and how it's used
  - Bad: `d`, `x`, `obj`, `temp` - No context or meaning
  - Good: `elapsedTimeInDays`, `activeUser`, `userList` - Clear purpose and type
- **Pronounceable names:** Avoid abbreviations and cryptic abbreviations that can't be spoken
  - Bad: `genymdhms`, `pszqint`, `DtaRcrd` - Hard to pronounce, impossible to discuss in conversation
  - Good: `generationTimestamp`, `dataRecord` - Easy to say and discuss
- **Searchable names:** Names should be easily found in code searches
  - Bad: Single-letter variables like `e` (error), `x`, `i` except in loops
  - Good: `maxIterations`, `emailAddress` - Can be searched and found
- **Avoid encodings and type information:** Names shouldn't include type prefixes or encoding
  - Bad: `strUserName`, `iCount`, `mUserList` (Hungarian notation)
  - Good: `userName`, `count`, `userList` - Let type hints clarify types
- **Make meaningful distinctions:** When multiple similar variables exist, names must differ meaningfully
  - Bad: `user1`, `user2`, `userData1`, `userData2` - No semantic difference
  - Good: `currentUser`, `selectedUser`, `adminUser` - Each name has distinct meaning
- **Use vocabulary from the domain:** Names should relate to the problem domain
  - Bad: Generic names like `Item`, `Data`, `Info`
  - Good: `Customer`, `Invoice`, `PaymentMethod` - Domain-specific terminology

### Constants & Magic Numbers

**Replace all magic numbers and strings with named constants:**

- **What is a magic number?** A literal value in code whose purpose isn't immediately obvious
  - Bad: `if count > 5:` - Why 5? What does it mean?
  - Bad: `timeout = 3600` - Is this seconds? Minutes? What's the significance?
  - Bad: `maxFileSize = 5242880` - What's this number? Bytes? How large?
- **Solution: Use named constants** - Constants make code self-documenting
  - Good: `MAX_RETRIES = 5` with comment explaining retry strategy
  - Good: `TIMEOUT_SECONDS = 3600` or `TIMEOUT_MINUTES = 60` - Units are clear
  - Good: `MAX_FILE_SIZE_MB = 5` then convert to bytes if needed
- **Constant organization:**
  - Define constants at module or class level (top of file)
  - Use UPPERCASE_WITH_UNDERSCORES for constant names
  - Group related constants together with comments
  - Example: All validation rules in a `VALIDATION_RULES` dict
- **String constants:** Extract repeated string literals
  - Bad: Multiple places checking `status == "pending"`
  - Good: `STATUS_PENDING = "pending"` defined once, used everywhere
- **Benefits:**
  - Code becomes self-documenting
  - Changes to values happen in one place
  - Prevents subtle bugs from copy-paste errors
  - Makes code more maintainable and testable

### Clarity in Complex Logic

**Use Explanatory Variables for Complex Expressions:**

- **Break complex expressions into smaller pieces** with descriptive variable names
  - Bad: `if user.is_active and user.membership.is_premium and user.payment.status == "paid":`
  - Good:
    ```python
    is_active_user = user.is_active
    has_premium_membership = user.membership.is_premium
    payment_is_current = user.payment.status == "paid"
    if is_active_user and has_premium_membership and payment_is_current:
    ```
  - Benefits: Self-documenting, easier to debug, easier to test individual conditions
- **Encapsulate boundary conditions** - Extract edge cases and limits into named checks
  - Bad: `if user.age >= 18 and user.age < 65:` (magic numbers, unclear meaning)
  - Good: `is_working_age = user.age >= MINIMUM_WORKING_AGE and user.age < RETIREMENT_AGE`
- **Avoid negative conditionals** - Positive conditions are easier to read
  - Bad: `if not user.is_inactive:` (double negative)
  - Good: `if user.is_active:` (positive and clear)
  - Exception: Simple cases like `if not file_exists:` are acceptable
- **Use intermediate values** for complex calculations
  - Bad: `total = (price * quantity) - (price * quantity * discount) + (price * quantity * tax)`
  - Good:
    ```python
    subtotal = price * quantity
    discounted = subtotal - (subtotal * discount)
    final_total = discounted + (discounted * tax)
    ```

### Function Arguments & Side Effects

- **Minimize arguments:** Prefer 0-1 arguments when possible, avoid 3+ arguments
  - 0 args: Best - clean, easy to test
  - 1-2 args: Good - still manageable
  - 3+ args: Bad - hard to understand, test, and remember order
  - Workaround: Use objects/dicts to group related arguments
- **Avoid flag arguments:** Boolean parameters that change function behavior are confusing
  - Bad: `render(user, renderInactive=True)` - Flag changes behavior unexpectedly
  - Good: `render(activeUser)` and `render(inactiveUser)` - Separate functions for clarity
- **No side effects:** Functions should not modify global state or external objects unexpectedly
  - Bad: Function that logs AND modifies database AND returns value - three things at once
  - Good: Separate functions for logging, database operations, and calculations
  - Document side effects clearly if unavoidable

### Comments Best Practices

**Write comments that explain intent, not implementation:**

- **The Goal:** Code should explain *what* it does; comments should explain *why* it does it
- **Bad comments** - Redundant or obvious:
  - `count = count + 1  # Increment count` - The code already says this
  - `user = get_user(id)  # Get the user` - Method name already says this
  - `x = x * 2  # Double x` - Code is self-explanatory
- **Good comments** - Clarify intent and reasoning:
  - `# Skip inactive users to avoid sending emails to deleted accounts` - Explains *why*
  - `# Must process in this order: deletion cascades require parent removal first` - Explains *why* this order
  - `# Cache for 5 minutes to balance freshness with API rate limits` - Trade-off explanation
- **Comments for clarification, not explanation:**
  - Explain non-obvious algorithms or complex business logic
  - Document assumptions: "Assumes user is already authenticated", "Requires valid email format"
  - Explain trade-offs and design decisions
  - Note performance implications or workarounds for bugs in dependencies
- **Avoid noise and redundancy:**
  - Don't repeat variable names or method behavior in comments
  - Don't comment out code (use git history instead)
  - Don't add comments with timestamps or "TODO" without urgency
- **Comments for warnings and clarifications:**
  ```python
  # WARNING: This method is O(n²) - use with small datasets only
  def process_all_pairs(items):
      ...

  # HACK: Workaround for Django bug #12345 - remove when upgrading
  if django.VERSION >= (4, 0):
      ...
  ```
- **Use docstrings for public APIs:**
  - Explain what method/function does, its parameters, and return value
  - Document exceptions that might be raised
  - Provide examples for complex functionality

### Code Contracts & Assumptions

Document what each function, view, or form assumes and guarantees. This prevents bugs from incorrect usage:

- **Write detailed docstrings** explaining:
  - Inputs: What parameters are required, their types, valid ranges
  - Outputs: What is returned and its type/structure
  - Assumptions: Required preconditions (user authenticated, data validated, etc.)
  - Side effects: Any state modifications, database changes, or external calls
  - Exceptions: What errors might be raised and when
  - Example:
    ```python
    def get_context_data(self, **kwargs) -> dict:
        """
        Builds context for list view.

        Assumes: User is authenticated (enforced by LoginRequiredMixin)
        Returns: Dict with 'items' (paginated QuerySet) and 'total_count' (int)
        Side effects: Filters queryset based on user permissions
        """
    ```
- **Document required parameters:**
  - URL parameters: `slug` must be URL-safe, `page` must be positive integer
  - Query parameters: Valid ranges, default values, required vs optional
  - Data types: Use type hints to clarify expected types
- **Document assumptions about state:**
  - "Requires logged-in user"
  - "User must own this resource"
  - "Assumes items are sorted chronologically"
  - "POST data must be URL-encoded, not multipart"
- **Document what context variables are always present vs optional** (for views/templates)
- **Benefits:**
  - Prevents bugs from incorrect usage
  - Makes code self-documenting
  - Easier to refactor safely
  - Reduces cognitive load when reading code

### Objects vs Data Structures

**Understand the difference and don't mix them:**

- **Objects:** Encapsulate data + methods that operate on that data
  - Hide internal structure (private attributes)
  - Expose behavior through methods (public interface)
  - Example: `User` object with `authenticate()`, `change_password()` methods
  - Good for: Domain models, business logic
- **Data Structures:** Hold data with minimal behavior
  - Expose raw data for external processing
  - Minimal methods, mostly used as containers
  - Example: Configuration dictionaries, request/response objects
  - Good for: Passing data around, configuration
- **Bad pattern - Hybrid (Worst of both worlds):**
  ```python
  # BAD: Mixes object behavior with exposed internal data
  class User:
      def __init__(self, name, email, age):
          self.name = name  # Public attributes
          self.email = email
          self.age = age

      def get_formatted_name(self):  # Some behavior
          return self.name.upper()
      # But all data is directly accessible and modifiable
      # Breaks encapsulation
  ```
- **Good pattern - Pure object:**
  ```python
  # GOOD: Encapsulates behavior, hides implementation
  class User:
      def __init__(self, name, email, age):
          self._name = name  # Private
          self._email = email
          self._age = age

      @property
      def name(self):
          return self._name

      def set_email(self, email):
          # Validation happens here
          if self.is_valid_email(email):
              self._email = email

      def get_formatted_name(self):
          return self._name.upper()
  ```
- **Good pattern - Pure data structure:**
  ```python
  # GOOD: Just data, no hidden behavior
  user_data = {
      'name': 'John Doe',
      'email': 'john@example.com',
      'age': 30,
  }
  # Or using dataclass
  from dataclasses import dataclass
  @dataclass
  class UserData:
      name: str
      email: str
      age: int
  ```
- **Django Models:** These are objects, not data structures
  - Hide database internals, expose domain behavior
  - Use properties and methods to encapsulate business logic
  - Don't expose raw database fields for direct modification without validation

### Code Formatting & Structure

**Use whitespace and formatting to reveal code structure:**

- **Vertical spacing:** Group related lines, separate unrelated concepts
  - Bad: No blank lines between unrelated operations (dense, hard to scan)
  - Good: Blank lines between logical sections (easy to scan and understand)
  - Example:
    ```python
    # Bad - all dense together
    user = get_user(id)
    items = user.items.all()
    count = items.count()
    total = sum(item.price for item in items)
    formatted_user = format_user(user)
    formatted_items = format_items(items)
    render_template('dashboard', {'user': formatted_user, 'items': formatted_items})

    # Good - related operations grouped together
    user = get_user(id)
    items = user.items.all()

    count = items.count()
    total = sum(item.price for item in items)

    formatted_user = format_user(user)
    formatted_items = format_items(items)

    render_template('dashboard', {'user': formatted_user, 'items': formatted_items})
    ```
- **Keep lines reasonably short:** Aim for 80-100 characters max (helps readability on narrow screens)
- **Indentation consistency:** Follow project standards strictly (Python=4 spaces, HTML/CSS/JS=2 spaces)
- **Organize class members logically:**
  - Constants first
  - Static methods
  - `__init__` and lifecycle methods
  - Public methods
  - Private methods
  - Properties/descriptors at the end
- **Related concepts close together:** Don't scatter related functionality across a large class

### Test Assertions & Structure

**Keep test assertions focused and readable:**

- **One logical assertion per test:** Each test should verify one behavior or concept
  - Bad: Tests that check multiple unrelated things in one method
  - Good: Separate test methods for each behavior
  - Exception: Testing related assertions about the same object is acceptable
- **Clear assertion messages:** When assertions fail, the message should explain what was tested
  - Bad: `self.assertTrue(result)` - What does `result` represent?
  - Good: `self.assertTrue(user.is_active)` or `self.assertEqual(status, "pending")`
  - Better: Use assertion methods that describe intent: `self.assertIsNotNone()`, `self.assertIn()`, `self.assertRaises()`
- **Use specific assertion methods:**
  - `self.assertEqual(a, b)` instead of `self.assertTrue(a == b)`
  - `self.assertIn(item, list)` instead of `self.assertTrue(item in list)`
  - `self.assertIsNone(value)` instead of `self.assertTrue(value is None)`
  - `self.assertRaises(ExceptionType)` instead of try/except in test
- **Arrange-Act-Assert pattern:**
  ```python
  def test_user_can_be_deactivated(self):
      # Arrange: Set up test data
      user = User.objects.create(username="testuser", is_active=True)

      # Act: Perform the action being tested
      user.is_active = False
      user.save()

      # Assert: Verify the result
      user.refresh_from_db()
      self.assertFalse(user.is_active)
  ```

---

## Django Application Architecture

### Orthogonal Systems & Decoupling (CRITICAL)

**Build independent, loosely-coupled apps that can be modified without affecting others:**

- Each app should have a single, well-defined responsibility
- Changes to one app should not require changes to other apps
- Use Django's app isolation: keep app logic internal, expose only clear interfaces
- **Benefits:**
  - Easier to test each app independently
  - Simpler to understand individual components
  - Reduced risk when making changes (changes don't ripple across codebase)
  - Easier to reuse apps in different projects
  - Teams can work on different apps without conflicts

**Implementation practices:**
- Don't import directly from other apps - use public APIs and signals when needed
- Each app owns its models, views, forms, and templates - don't share model definitions across apps
- Use Django signals for cross-app communication instead of direct coupling
- Abstract reusable utilities into separate `utils/` apps that other apps depend on
- Avoid circular imports - if two apps need to import each other, refactor to a third app both depend on

### App Structure Standards

**All Django apps must be organized as sub-packages, not single files:**

- Create `admin/`, `models/`, `tests/`, `views/`, `utils/` as folders with `__init__.py`
- Each package should import from its submodules and use explicit `__all__` exports
- Name submodules appropriately: `admin/resource.py`, `models/resource.py`, `tests/test_resource.py`
- For views, organize by functionality: `views/public.py`, `views/authenticated.py`, `views/api.py`
- Keep view modules focused and around 70 lines when possible (same as templates)
- Remove original single `.py` files after converting to packages

**App Location and Naming:**

- Apps live in `apps/[app_name]/` directory structure
- Reference apps as `"apps.[app_name]"` in `INSTALLED_APPS`
- Set `name = "apps.[app_name]"` in the app's `apps.py` file
- Create `urls.py` in each app with `app_name` namespace and include in main URLs

**Creating New Apps:**

```bash
python manage.py startapp [app_name] apps/[app_name]
```

**Python Module Refactoring Guidelines:**

- **If over 100 lines with multiple classes:** Refactor into focused, single-responsibility modules
  - Each class should live in its own file (e.g., `models/user.py`, `models/profile.py`)
  - Import and re-export from `__init__.py` for clean public API
  - Benefits: Easier to navigate, test, and maintain
- **If over 1000 lines (single class):** Refactor for readability and testability
  - Break large classes into focused subclasses with specific responsibilities
  - Extract complex methods into smaller helper methods
  - Consider splitting into multiple related classes that work together
  - Benefits: Improved readability, easier testing, better code organization

### Views Architecture

**Prefer class-based views over function-based views:**

- Use Django's generic class-based views (ListView, DetailView, CreateView, UpdateView, DeleteView, etc.)
- Leverage mixins like LoginRequiredMixin for authentication
- Override methods like `get_context_data()`, `get_queryset()` for custom behavior
- Organize views into logical modules by functionality
- Use explicit imports and `__all__` in `views/__init__.py` for clear API
- Class-based views provide better code organization and reusability

**Method Segmentation (CRITICAL):**

Break complex view methods into focused helper methods:

- No method should have more than 5 statements when possible
- Extract logical operations into private methods (prefixed with `_`)
- Use descriptive method names that clearly indicate their single responsibility
- Keep the main method (e.g., `get_context_data()`) as orchestration layer
- Benefits: Improved testability, easier debugging, better code organization
- Example: Break `get_context_data()` into `_get_base_queryset()`, `_apply_filters()`, `_calculate_statistics()`, etc.

**See "Function Arguments & Side Effects" and "Code Contracts & Assumptions"** in the Clean Code Best Practices section for detailed guidance on these principles.

**See "Constants & Magic Numbers"** in the Clean Code Best Practices section for detailed guidance on this principle.

### Forms Best Practices

**Use Django ModelForms with proper validation:**

- **Styling preference order:**
  1. Tailwind classes in templates first
  2. Form widget attrs if template styling not feasible
  3. Form Media definitions last resort
- Implement custom `clean_[field]()` methods for field-specific validation
- Use `form.cleaned_data.get()` to safely access validated data
- Handle file uploads with `request.FILES.getlist()` for multiple files
- Provide user-friendly error messages via `forms.ValidationError`

**Extending Built-in Forms:**

- When extending Django's built-in forms (e.g., `UserCreationForm`), add required fields in the extended class
- Override `save()` method if needed for custom behavior

**Uniqueness Validation:**

- Check for duplicate values in `clean_[field]()` using `Model.objects.filter(field=value).exists()`
- Raise `forms.ValidationError` with clear, user-friendly messages

**Form Organization:**

- Create forms in `[app_name]/forms.py` file, import in views as needed

**Code Contracts for Forms:**

Document form behavior and validation contracts:

- Document what fields are required vs optional: "username is unique and required"
- Document validation rules and their reasons: "email must be unique because it's used for password reset"
- Document what the `save()` method does beyond the obvious: "save() also sends confirmation email"
- Document assumptions: "assumes user is already authenticated", "assumes POST data is URL-encoded, not multipart"
- Use docstrings on custom `clean_*` methods explaining the validation rule
- Example:
  ```python
  def clean_email(self) -> str:
      """
      Validates email is unique across User model.

      Raises: ValidationError if email already registered
      """
      email = self.cleaned_data.get("email")
      if User.objects.filter(email=email).exists():
          raise forms.ValidationError("Email already registered")
      return email
  ```

**Validation Configuration:**

Use configuration constants for validation rules that appear in multiple places (client-side and server-side):

- Define constants at the top of JavaScript files for allowed values (e.g., `ALLOWED_IMAGE_FORMATS`, `ALLOWED_FORMATS_DISPLAY`)
- Keep Python validation in sync with JavaScript validation by using the same allowed values
- Benefits: Single source of truth, easier maintenance, consistent user experience across client/server validation

**Form Validation Strategy:**

Implement server-side validation by default. Client-side validation is optional and should only be added when it provides significant user experience benefits:

- **Server-side (Django):** Always required, authoritative validation
  - Validate in form `clean()` or `clean_[field]()` methods
  - Use `forms.ValidationError` for user-friendly error messages
  - Handle edge cases and security concerns
  - Wrap operations in try-catch for graceful error handling
  - Works without JavaScript - users always get feedback

- **Client-side (JavaScript):** Optional, only for high-value interactions
  - When to use: File uploads (validate before upload), complex forms with many fields, password strength indicators
  - When NOT to use: Simple forms like login, basic contact forms - server validation is sufficient
  - Validate file types, sizes, and formats before upload
  - Display validation errors inline with clear messaging
  - Prevent form submission if validation fails
  - **IMPORTANT:** Always validate on server even if client-side validation exists

- **User Feedback:** Provide clear messages at every stage
  - Show validation errors with specific details and reasons
  - Display progress indicators during long operations
  - Confirm successful operations with counts and details
  - Enable retry via back navigation after errors

**Simplicity First Philosophy:**

Following the core principle of "Simplicity First," avoid adding JavaScript validation to simple forms. Server-side validation provides security and reliability without complexity. Only add client-side validation when it meaningfully improves the user experience (e.g., file type validation before upload, real-time character counting).

**See "Clarity in Complex Logic"** in the Clean Code Best Practices section for detailed guidance on this principle.

### Admin Interface

**Admin Interface Pattern:**

- Use Django's built-in admin: `from django.contrib import admin`
- Extend `admin.ModelAdmin` for all model admin classes
- Register models using `@admin.register(Model)` decorator
- Keep admin interface consistent and professional across all models
- Example structure: `apps/resource/admin/resource.py`

**See "Objects vs Data Structures"** in the Clean Code Best Practices section for detailed guidance on this principle, especially as it applies to Django models.

### User Model vs Profile Model Pattern

**CRITICAL: DO NOT CREATE A CUSTOM USER MODEL - Use Django's Built-in User Model**

- Django's default User model is battle-tested, well-optimized, and integrates seamlessly with the entire framework
- Custom user models add unnecessary complexity and create migration challenges
- Always use Django's built-in User model with a OneToOne Profile model for additional data

**Separate account data from profile/business data:**

- **User Model (Django's built-in):** Username, email (for login/notifications), password - account-level data
- **Profile Model (OneToOne with User):** Business information, preferences, optional contact details
- Display read-only account information (username, email) separately from editable profile forms
- Use gray background box at top of profile page to show non-editable User fields
- Profile can have optional business email separate from account email for flexibility
- Pattern: Account email = system notifications, Business email = public contact

**Example Pattern:**

```python
# DO NOT do this L
class CustomUser(AbstractUser):
    # This adds unnecessary complexity
    pass

# DO this instead 
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    # Other business-specific fields
```

---

## Template Architecture

### Template Organization

**Template Length Guidelines:**

- Keep templates under 100 lines when possible
- If over 100 lines: Refactor into focused partials in organized subfolders
  - Break template into logical components (header, form, content sections, etc.)
  - Create separate partial templates for each component
  - Place related partials in focused subfolders (e.g., `includes/footer/`, `includes/forms/`)
  - Main template becomes orchestration layer with includes
  - Benefits: DRY code, consistent UI, easier maintenance, improved testability

**Template Subfolder Organization:**

Group related template partials into focused subfolders for better organization:

- Create subfolders like `includes/footer/`, `includes/navigation/`, `includes/forms/` for related components
- Move related partials into their respective subfolders (e.g., `_footer_brand.html`, `_footer_nav.html` � `footer/`)
- Update all include paths to reference the new subfolder locations
- Benefits: Cleaner directory structure, easier maintenance, logical grouping of related templates
- Example: Footer components in `includes/footer/`, navigation components in `includes/navigation/`

**Template Standards:**

- Django templates must use named endblocks (e.g., `{% endblock content %}` not `{% endblock %}`)
- Use 2-space indentation for all HTML/template code
- Use `{% comment %}` tags for multiline comments in templates:

  ```django
  {% comment %}
  Multi-line comment explaining template logic,
  parameters, or complex functionality
  {% endcomment %}
  ```

  - **CRITICAL**: Always use `{% comment %}` for multiline comments instead of HTML `<!-- -->` comments
  - HTML comments `<!-- -->` are sent to the browser and increase page size
  - Django `{% comment %}` tags are stripped during template rendering and don't affect page size
  - Use for documenting template parameters, logic, and reusable component interfaces

### Reusable Template Includes

Create reusable template includes for common UI patterns:

- Store includes in `templates/[app_name]/includes/` directory
- Prefix include filenames with underscore (e.g., `_messages.html`, `_back_link.html`)
- Make includes flexible with context variables (e.g., `submit_text|default:"Submit"`)
- Common patterns to extract: navigation elements, form actions, messages, complex interactive components, headers, empty states
- Name includes descriptively based on functionality (e.g., `_header.html`, `_actions.html`)

**Complex Template Refactoring:**

Break down large templates (>100 lines) into focused partials:

- Identify logical components (navigation, forms, content sections)
- Create separate partial templates for each component
- Main template becomes orchestration layer with includes
- Example: Navigation system split into `_nav_links.html`, `_user_dropdown_button.html`, `_user_dropdown_menu.html`
- Benefits: DRY code, consistent UI, easier maintenance across multiple views, improved testability

**Component Reusability (CRITICAL):**

**See "Principle 3: Apply DRY & Code Reusability"** in the Agent Best Practices section for comprehensive guidance on designing reusable components.

Template-specific reusability checklist:

- Use flexible context variables with sensible defaults (e.g., `title|default:"Default Title"`, `css_classes|default:""`)
- Avoid hard-coded app-specific paths, IDs, or styling - make them configurable
- Design components to work across different apps and contexts
- Include comprehensive documentation in component comments explaining all available parameters
- Test components in multiple contexts to ensure they work universally
- Benefits: Maximum code reuse, consistent UI patterns, easier maintenance, faster development

**Icon Template Partials:**

Store reusable SVG icons as template includes:

- Create `templates/[app_name]/includes/icons/` directory for icon partials
- Each icon is a separate template file (e.g., `_plus.html`, `_chevron.html`, `_user.html`)
- Include accessibility attributes directly in icon templates: `aria-hidden="true" focusable="false"` for decorative icons
- Pass icon templates via `icon_template` parameter instead of inline SVG strings with escaped quotes
- Example: `{% include "card.html" with icon_template="app/includes/icons/_plus.html" %}`
- Card/component templates use `{% if icon_template %}{% include icon_template %}{% endif %}`
- Benefits: No escaped quotes, reusable icons, accessibility built-in, cleaner code, easier maintenance

**See "Comments Best Practices"** in the Clean Code Best Practices section for detailed guidance on commenting principles.

### Template Linting with djlint

**Use djlint to enforce consistent Django template formatting:**

**Installation and Setup:**

```bash
pip install djlint
```

**Configuration (.djlintrc):**

Create `.djlintrc` in project root with project-specific rules:

```ini
[tool.djlint]
profile = "django"
extension = "html"
indent = 2
max_line_length = 120
format_attribute_template_tags = true
ignore = "H006,H030,H031"  # Add specific rules to ignore if needed
```

**Common djlint Rules and How to Avoid Errors:**

**T002 - Double quotes in tags (CRITICAL):**

- **ERROR:** `{% trans 'text' %}` L
- **CORRECT:** `{% trans "text" %}` 
- **Prevention:** Always use double quotes in Django template tags (`{% %}`, `{{ }}`)
- **Common violations:** `{% trans %}`, `{% blocktrans %}`, `{% url %}`, `{% static %}`, `{% include %}`
- **Auto-fix:** `djlint --reformat` can fix this automatically

**T001 - Extra whitespace in tags:**

- **ERROR:** `{%trans "text"%}` L (no spaces around content)
- **CORRECT:** `{% trans "text" %}` 
- **Prevention:** Always include single space after tag name and before closing `%}`

**T003 - Endblock tag naming:**

- **ERROR:** `{% endblock %}` L (unnamed endblock)
- **CORRECT:** `{% endblock content %}` 
- **Prevention:** Always name your `{% endblock %}` tags to match the opening `{% block %}`

**T004 - Indentation:**

- **ERROR:** Inconsistent indentation levels
- **CORRECT:** Use consistent 2-space indentation for HTML/template code
- **Prevention:** Follow project's indentation standards (2 spaces for HTML/JS/CSS, 4 spaces for Python)

**Running djlint:**

```bash
# Check specific template directory
djlint apps/[app_name]/templates/[app_name]/

# Check all templates
djlint apps/*/templates/

# Auto-fix formatting issues
djlint --reformat apps/[app_name]/templates/[app_name]/

# Check without fixing
djlint --check apps/[app_name]/templates/[app_name]/
```

**Integration with Development Workflow:**

- **Pre-commit hooks:** Add djlint to pre-commit configuration to catch formatting issues before commits
- **CI/CD:** Include djlint checks in CI pipeline to prevent poorly formatted templates from being merged
- **IDE integration:** Configure your editor to run djlint on save or use djlint extensions

**Common Mistakes to Avoid:**

1. **Single quotes in template tags:** Always use double quotes for consistency
2. **Unnamed endblocks:** Always name `{% endblock %}` tags
3. **Inconsistent indentation:** Stick to 2-space indentation for templates
4. **Missing spaces in tags:** Include proper spacing: `{% tag %}` not `{%tag%}`
5. **Mixed quote styles:** Choose double quotes for template tags, single quotes for HTML attributes when needed

**T002 - Template Tags Inside HTML Attributes (CRITICAL):**

When you need to use Django template tags inside HTML attributes, use the `as` syntax to avoid quote conflicts:

- **ERROR:** `title="{% trans 'Tooltip text' %}"` L (single quotes inside double quotes violates T002)
- **ERROR:** `title='{% trans "Tooltip text" %}'` L (double quotes inside single quotes are inconsistent)
- **CORRECT:** Extract the translation first, then reference it:
  ```django
  {% trans "Tooltip text" as tooltip_var %}
  <button title="{{ tooltip_var }}">Click</button>
  ```
- **Prevention:** When template tags are needed in attributes, always use the `as` pattern to assign to a variable, then reference that variable in the attribute
- **Why:** This keeps quotes consistent (always double quotes in template tags) and makes djlint happy
- **Example for multiple attributes:**
  ```django
  {% trans "Tooltip text" as tooltip_text %}
  {% trans "Button label" as button_text %}
  <button title="{{ tooltip_text }}" aria-label="{{ button_text }}">Click</button>
  ```

**Benefits of djlint:**

- Consistent code formatting across all templates
- Automated detection of common formatting mistakes
- Improved code readability and maintainability
- Prevention of formatting-related merge conflicts
- Professional code standards enforcement

### Navigation Patterns

**Navigation Consistency:**

ALL authenticated pages must include navigation for consistent UX:

- Every app's base template must include the navigation component (e.g., `{% include "includes/_navigation.html" %}`)
- Navigation should appear at the top of every authenticated page
- Users must always be able to navigate back to primary sections from any page
- Never create isolated pages without navigation - users should never feel "stuck" on a page
- Public/unauthenticated pages can have different navigation appropriate for their context

**Navigation Component System:**

- **Reusable Partial Templates:** Break down complex navigation into focused partials:
  - `_nav_links.html` - Main navigation links with active state logic
  - `_user_dropdown_button.html` - Dropdown trigger with accessibility attributes
  - `_user_dropdown_menu.html` - Dropdown content with user info and actions
  - Main template orchestrates components with Alpine.js context

- **Active State Indicators:** Visual feedback for current page using custom active class with bottom border or background highlight

- **Mobile Menu Patterns:** Smooth slide animations with transition classes
  - Enter: `opacity-0 transform -translate-y-2 scale-95` � `opacity-100 transform translate-y-0 scale-100`
  - Leave: Reverse animation with 200ms duration
  - Use custom transition classes for consistent animations

- **User Dropdown Patterns:** Scale/fade animations with click-away and escape key handling

- **Sticky Navigation:** Header sticks to top with dynamic shadow on scroll detection

- **Keyboard Accessibility:** Full tab navigation with visible focus rings and ARIA attributes

### Internationalization (i18n)

**Wrap user-facing strings with Django translation tags for localization:**

- Load i18n tags: `{% load i18n %}` at top of templates
- Simple strings: `{% trans "Text to translate" %}`
- Strings with variables: `{% blocktrans %}Text with {{ variable }}{% endblocktrans %}`

**CRITICAL - Template Partials Must Load i18n:**

Each partial template that uses i18n tags MUST include `{% load i18n %}` at the top:

- When splitting templates into partials, each partial is independent and must load its own template tags
- Missing `{% load i18n %}` in partials causes "Invalid block tag" or "Did you forget to register or load this tag?" errors
- Example: If `_search.html` uses `{% trans %}`, it needs `{% load i18n %}` even if parent template has it

**Include Tag Compatibility:**

Cannot nest `{% trans %}` inside `{% include %}` tag attributes:

- Wrong: `{% include "template.html" with title="{% trans "Title" %}" %}` L
- Correct: `{% trans "Title" as card_title %}{% include "template.html" with title=card_title %}` 
- Pass translated variables without quotes to include tags

**Extract Strings:**

```bash
python manage.py makemessages -l [locale]
```

### Django URL Template Tags

**Always use keyword arguments for URL patterns with named groups:**

- Correct: `{% url 'app:view' slug=object.slug %}`
- Incorrect: `{% url 'app:view' object.slug %}`
- Use conditional checks before rendering URLs if field might be empty: `{% if object.slug %}...{% endif %}`

### Social Media Meta Tags

**Add Open Graph and Twitter Card tags for professional social sharing:**

- **Open Graph tags:** `og:title`, `og:description`, `og:image`, `og:url`, `og:type`, `og:site_name`
- **Twitter Card tags:** `twitter:card` (use `summary_large_image`), `twitter:title`, `twitter:description`, `twitter:image`
- Use dynamic content from model fields when available
- Place in `<head>` section of public-facing templates
- Fallback to generic descriptions when model fields are empty
- Use `request.build_absolute_uri` for canonical URLs
- Benefits: Professional appearance when links shared on Facebook, Twitter, LinkedIn, etc.

---

## Frontend Architecture

### Third-Party Assets Policy

**ALL external libraries and assets must be stored locally in the project:**

- NO CDN dependencies in production (reliability, security, performance, offline development)
- Store JavaScript libraries in `static/js/`
- Store CSS libraries in `static/css/`
- Store fonts/icons in appropriate static directories
- Version control ensures consistency across all environments

### Tailwind CSS

**Utility-first styling with mobile-first breakpoints:**

- Build locally via npm
- Custom styles that cannot be handled by Tailwind classes should be placed in custom CSS file using proper `@layer` directives, not inline `<style>` tags in templates
- Use Tailwind's default spacing scale and conventions
- Leverage Tailwind's responsive modifiers (sm:, md:, lg:, xl:, 2xl:)

**Build Commands:**

```bash
npm run build              # Development build
npm run tw:build          # Optimized production build
```

**CSS File Refactoring Guidelines:**

- **If over 1000 lines:** Refactor into focused, organized CSS files
  - Split by component or feature: `buttons.css`, `forms.css`, `layout.css`, `animations.css`
  - Use `@import` statements to organize and reference files appropriately
  - Group related styles together with clear section comments
  - Benefits: Easier maintenance, faster lookups, better code organization

### Alpine.js

**Lightweight JavaScript framework for reactive components:**

- Served as local static asset
- Use for: drag-and-drop, auto-dismissing messages, show/hide toggles, dynamic UI updates
- Syntax: `x-data`, `x-show`, `x-transition`, `x-init`, `@click`, `@dragover`, etc.
- Keep JavaScript logic minimal and progressive - pages should work without JS

**Component Pattern:**

Create reusable Alpine.js components using function-based pattern:

- Define components as functions in `<script>` tags: `function componentName() { return { ... } }`
- Initialize with `x-data="componentName()"` on container element
- Keep component logic focused and single-responsibility
- Use descriptive method names: `handleSubmit()`, `validateFile()`, `handleDrop()`
- Store component state in data properties: `uploading`, `validFiles`, `errors`
- Provide immediate user feedback with reactive UI updates

**Example Patterns:**

- **File upload with drag-and-drop:** `x-data="{ dragging: false, files: [] }"`
- **Auto-dismissing notifications:** `x-init="setTimeout(() => show = false, 5000)"`
- **Dropdown menus:** `x-data="{ menuOpen: false }"` with `@click.away="menuOpen = false"` and `@keydown.escape.window`
- **Mobile menus:** `x-show="mobileMenuOpen"` with smooth transition classes and keyboard handling
- **Scroll detection:** `x-data="{ scrolled: false }"` with `@scroll.window="scrolled = (window.pageYOffset > 0)"`

**Lightbox/Modal Galleries:**

Function-based component pattern with keyboard and touch navigation:

- Use function factory: `x-data="galleryLightbox(photoCount)"` for scoped instances
- Collect data from DOM: `init()` method gathers photo data from `data-*` attributes
- Computed properties: Use getters (`get hasPrevious()`) for reactive UI states
- Keyboard navigation: `@keydown.escape.window`, `@keydown.arrow-left.window`, `@keydown.arrow-right.window`
- Touch/swipe support: Track `touchstart` and `touchend` events with threshold detection
- Body scroll control: Toggle `document.body.style.overflow` to prevent background scrolling
- DOM state binding: Use `data-*` attributes on elements to pass data to Alpine.js component

**Single Scope Pattern (CRITICAL):**

Use ONE Alpine scope per form/component tree:

- Place `x-data="componentName()"` on the outermost container (e.g., `<form>`)
- All child includes/partials inherit this scope automatically
- DO NOT add nested `x-data` scopes unless truly independent
- Child templates can reference parent scope variables (e.g., `validFiles`, `errors`)
- Avoids `ReferenceError` when includes try to access component state
- Example: Form component owns both submit state AND validation state for all child includes

**Form Validation Initialization:**

Don't show validation errors on page load:

- Start with `isValid: false` and empty error messages (`errors: { field: '' }`)
- In `init()` method, only initialize non-error state (e.g., character counts, field values)
- DO NOT call validation methods in `init()` - only validate on user interaction
- Trigger validation on blur/input events: `@blur="validateField"`, `@input="validateField"`
- Run full validation on submit: `@submit="handleSubmit"` calls `validateAll()`
- This prevents showing "Field is required" errors before user interacts with form

### HTMX (Optional)

**For progressive enhancement and partial page updates:**

- Minimal framework, stored locally
- Use for dynamic content updates without full page reloads
- Maintains server-side rendering benefits while enhancing interactivity

### Vanilla JavaScript

**When Alpine.js or HTMX are not needed:**

- Keep vanilla JavaScript minimal and focused
- Use modern ES6+ syntax
- Progressive enhancement principle applies
- Store in `static/js/` directory as local assets
- Use descriptive filenames and module pattern when appropriate

**JavaScript File Refactoring Guidelines:**

- **If over 1000 lines:** Refactor into a focused package with organized modules
  - Break into focused modules by feature or responsibility (e.g., `form-validation.js`, `gallery.js`, `api.js`)
  - Create an index file that exports the public API
  - Use module pattern or ES6 modules for proper encapsulation
  - Benefits: Improved readability, easier testing, better code reusability

---

## Design System

### Typography

**Font Strategy:**

- Choose a modern, professional font (variable fonts preferred for performance)
- Host fonts locally for reliability and GDPR compliance
- Use system font stack as fallback: `system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif`

**Typography Scale:**

```
h1: text-6xl (60px) / font-extrabold (800) / tracking-tight
h2: text-5xl (48px) / font-bold (700) / tracking-tight
h3: text-4xl (36px) / font-bold (700)
h4: text-3xl (30px) / font-semibold (600)
h5: text-2xl (24px) / font-semibold (600)
h6: text-xl (20px) / font-semibold (600)
Body: text-base (16px) / font-normal (400) / line-height 1.5
Small: text-sm (14px) / Secondary text
Caption: text-xs (12px) / Labels and metadata
```

**Utility Classes:**

- `.text-display` - Large display text (48px/extrabold)
- `.text-heading` - Section headings (30px/bold)
- `.text-subheading` - Subsection headings (20px/semibold)
- `.text-body` - Body text (16px/normal)
- `.text-body-emphasized` - Emphasized body (16px/medium)
- `.text-small` - Small text (14px)
- `.text-caption` - Captions and labels (12px)
- `.text-label` - Form labels (14px/medium)

### Color Palette

**WCAG 2.1 AA compliant color system with semantic tokens:**

**Primary Color:**

```
primary-50: Lightest backgrounds
primary-100: Light hover states
primary-500: Main primary - buttons, links
primary-600: Hover - interactive elements
primary-700: Active states
primary-900: Darkest - text on light bg
```

**Secondary/Neutral Color:**

```
secondary-50: Lightest backgrounds
secondary-100: Card backgrounds
secondary-200: Borders, dividers
secondary-300: Disabled states
secondary-400: Placeholder text
secondary-500: Secondary text
secondary-600: Body text
secondary-700: Headings
secondary-800: Dark headings
secondary-900: Darkest text
```

**Semantic Colors:**

```
success-500: Green - success states
success-600: Hover
warning-500: Amber - warnings
warning-600: Hover
error-500: Red - errors
error-600: Hover
```

**Usage Guidelines:**

- Use `primary-*` for interactive elements (buttons, links, focus states)
- Use `secondary-*` for text hierarchy and neutral UI
- Use semantic colors (success/warning/error) for states and feedback
- Ensure 4.5:1 contrast ratio for text (WCAG AA)
- Ensure 3:1 contrast ratio for UI components

### Spacing & Layout

**Spacing Scale:**

Tailwind's default 4px scale: 0, 1(4px), 2(8px), 3(12px), 4(16px), 5(20px), 6(24px), 8(32px), 10(40px), 12(48px), 16(64px), 20(80px), 24(96px), 32(128px)

**Standard Spacing Conventions:**

- **Page padding (mobile):** `px-4` (16px)
- **Page padding (desktop):** `px-6 lg:px-8` (24px/32px)
- **Section vertical spacing:** `py-12 lg:py-16` (48px/64px)
- **Section gaps:** `space-y-8` or `space-y-12` (32px/48px)
- **Card padding:** `p-6` (24px)
- **Form spacing:** `space-y-6` (24px between fields)
- **Grid gaps:** `gap-4` (16px) or `gap-6` (24px)
- **Element margins:** `mb-8` (32px) or `mb-12` (48px)

**Container Widths:**

- `max-w-7xl` (1280px) - Main app pages/dashboards
- `max-w-4xl` (896px) - Public pages, content pages
- `max-w-2xl` (672px) - Narrow forms, focused content
- `max-w-md` (448px) - Authentication forms, modals

**Layout Utility Classes:**

- `.container-page` - Full-width page container (`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`)
- `.container-narrow` - Narrow content container (`max-w-4xl mx-auto px-4 sm:px-6 lg:px-8`)
- `.container-form` - Form container (`max-w-md mx-auto px-4`)
- `.section-spacing` - Standard section spacing (`py-12 lg:py-16`)
- `.section-spacing-sm` - Small section spacing (`py-8 lg:py-12`)
- `.section-spacing-lg` - Large section spacing (`py-16 lg:py-24`)

**Border Radius:**

- `rounded` (default): 8px - Cards, buttons
- `rounded-lg`: 12px - Larger cards
- `rounded-xl`: 16px - Feature sections
- `rounded-full`: Pills, avatars

**Shadows:**

- `shadow-sm`: Subtle card elevation
- `shadow` (default): Standard cards
- `shadow-md`: Hover states, dropdowns
- `shadow-lg`: Modals, popovers

### Transitions & Animations

**Timing:**

- Default: 200ms (quick feedback)
- Smooth: 300ms (page transitions, modals)
- Timing function: cubic-bezier(0.4, 0, 0.2, 1) - ease-in-out

**Utility Classes:**

- `.transition-smooth` - 200ms transitions
- `.transition-smooth-300` - 300ms transitions
- `.text-crisp` - Optimized text rendering

**Best Practices:**

- Keep animations subtle and fast (200-300ms)
- Use transitions for hover, focus, active states
- Respect `prefers-reduced-motion` setting

### Mobile Menu Implementation

**Professional mobile navigation with smooth animations and accessibility:**

**Hamburger Animation:**

- CSS-powered X transformation using custom class (e.g., `hamburger-open`)
- Lines rotate 45� and -45� with `transform: rotate() translateY()`
- Middle line fades with `opacity: 0`
- Smooth 300ms transitions with `transition-all duration-300`

**Slide Animations:**

- Full-height overlay with smooth slide transitions
- Enter: `opacity-0 transform -translate-y-2 scale-95` � `opacity-100 transform translate-y-0 scale-100`
- Leave: Reverse animation with 200ms duration
- Use custom transition classes for consistent behavior

**Touch-Friendly Design:**

- Minimum 44px touch targets for mobile accessibility
- Generous padding: `px-4 py-3` for menu items
- Clear visual hierarchy with proper spacing

**Accessibility Features:**

- ARIA attributes: `aria-expanded`, `aria-label`
- Keyboard navigation: Tab order, Enter/Space activation, Escape to close
- Focus management: Visible focus rings, logical tab order
- Screen reader announcements for menu state changes

**Alpine.js Integration:**

- `x-data="{ mobileMenuOpen: false }"` for menu state
- `@click="mobileMenuOpen = !mobileMenuOpen"` for toggle
- `@click.away="mobileMenuOpen = false"` for outside clicks
- `@keydown.escape.window="mobileMenuOpen = false"` for keyboard handling

### Button Philosophy (CRITICAL)

**NO buttons should EVER be significantly wider than their text content:**

- Buttons size to content automatically via `inline-flex` in base class
- NEVER use `w-full` or `flex-1` on buttons unless specifically required for layout
- Button component classes: `.btn-primary`, `.btn-secondary`, `.btn-tertiary`, `.btn-danger`, `.btn-success`
- Size variants: `.btn-sm`, `.btn-lg` (adjust padding, not width)
- All buttons must include appropriate hover states with proper text contrast
- Clean, simple design: no excessive animations, just solid color transitions (200ms)
- Use `flex flex-wrap gap-3` for button groups so they wrap naturally
- This applies to ALL buttons: form submits, action buttons, CTAs, everything

### Mobile-First Patterns

**Mobile-First Button Visibility Pattern:**

For image overlays and interactive galleries, use responsive opacity controls:

- Pattern: `opacity-100 sm:opacity-0 sm:group-hover:opacity-100` on overlay containers
- **Mobile (< sm):** Buttons always visible for touch accessibility
- **Desktop (e sm):** Buttons hidden by default, appear on hover for clean UI
- Combine with transparent button backgrounds (`bg-black/60`) to show content beneath
- Position action buttons intuitively (e.g., bottom of images for mobile interaction)
- Benefits: Clean desktop experience, full mobile accessibility, no hover dependency

---

## Accessibility Standards

### Decorative SVGs

**Mark purely decorative icons appropriately:**

- Decorative icons: `aria-hidden="true" focusable="false"`
- Decorative icons include: arrows, visual indicators, icons that duplicate adjacent text
- Add comments explaining why decorative icons are hidden: `{# Decorative icon - visual indicator only #}`
- Screen readers should only announce meaningful content, not redundant visual decorations
- If an icon conveys unique information, provide alternative text via `aria-label` or visually-hidden text
- Test with screen readers (VoiceOver, NVDA) or browser accessibility inspectors to verify proper behavior

### Keyboard Navigation

- Full tab navigation support for all interactive elements
- Visible focus rings on all focusable elements
- Escape key to close modals/dropdowns
- Arrow keys for navigation within components (galleries, menus)
- Enter/Space for activation

### ARIA Attributes

- Use appropriate ARIA roles, states, and properties
- `aria-expanded` for disclosure widgets
- `aria-label` for elements without visible text
- `aria-hidden` for decorative or redundant elements
- Maintain proper heading hierarchy (h1-h6)

---

## Testing Strategy

### Test Organization

**Use Django's TestCase as the foundation for all tests:**

- **Always use `django.test.TestCase`** - Not unittest.TestCase, not pytest
- Django's TestCase provides essential features: database transactions, fixtures, assertions specific to web testing
- TestCase automatically rolls back database changes after each test (isolation)
- Use `django.test.TransactionTestCase` only when you specifically need transaction behavior (rare)
- Benefits: Proper database isolation, faster test cleanup, integration with Django's testing utilities

**Organize tests into logical modules mirroring code structure:**

- Create `tests/test_forms.py`, `tests/test_views.py`, `tests/test_models.py`, etc.
- **For larger test suites, organize tests into sub-packages mirroring the app structure:**
  - `tests/views/` - All view-related tests (e.g., `test_landing_page_view.py`, `test_detail_view.py`)
  - `tests/models/` - All model-related tests
  - `tests/forms/` - All form-related tests
  - `tests/admin/` - All admin-related tests
- Keep test files focused around 70 lines when possible (same guideline as views/templates)
- Extract shared test utilities to `tests/helpers.py` (e.g., `create_test_user()`, `create_test_image()`)
- Import all test modules in `tests/__init__.py` for test discovery
- Benefits: Easier to find tests, faster test execution, better organization, scalable structure for growing test suites

### Testing Philosophy - DO NOT TEST EXTERNAL CODE

**NEVER write tests for Django's built-in functionality or third-party packages:**

- **NEVER test Django's built-in functionality** - Django is already well-tested
- **NEVER test third-party packages** - They have their own test suites
- **DO NOT test basic model field behavior** (CharField, IntegerField, ForeignKey, etc.)
- **DO NOT test ORM operations** (create, save, filter, get)
- **DO NOT test framework validators** (EmailValidator, URLValidator, etc.)

**ONLY test custom business logic you wrote:**

- Custom model methods (e.g., `get_formatted_display()`, `calculate_total()`)
- Custom form validation logic (e.g., `clean_field()` with file size/format checks)
- Custom view behavior (e.g., auto-creating records, special permissions)
- Custom template filters and tags (e.g., `format_phone`)
- Integration points between your components

**When in doubt, ask:** "Am I testing my code or someone else's code?" If it's external code, delete the test.

**Example - BAD tests (testing external code):**

- Testing that a CharField can be created L
- Testing that OneToOneField enforces uniqueness L
- Testing that blank=True makes a field optional L
- Testing that image library can resize images L

**Example - GOOD tests (testing your code):**

- Testing custom validation logic in `clean_field()` 
- Testing custom formatting template filter 
- Testing view creates related record automatically on first access 

### Test Assertions & Structure (Clean Code)

**Keep test assertions focused and readable:**

- **One logical assertion per test:** Each test should verify one behavior or concept
  - Bad: Tests that check multiple unrelated things in one method
  - Good: Separate test methods for each behavior
  - Exception: Testing related assertions about the same object is acceptable
- **Clear assertion messages:** When assertions fail, the message should explain what was tested
  - Bad: `self.assertTrue(result)` - What does `result` represent?
  - Good: `self.assertTrue(user.is_active)` or `self.assertEqual(status, "pending")`
  - Better: Use assertion methods that describe intent: `self.assertIsNotNone()`, `self.assertIn()`, `self.assertRaises()`
- **Use specific assertion methods:**
  - `self.assertEqual(a, b)` instead of `self.assertTrue(a == b)`
  - `self.assertIn(item, list)` instead of `self.assertTrue(item in list)`
  - `self.assertIsNone(value)` instead of `self.assertTrue(value is None)`
  - `self.assertRaises(ExceptionType)` instead of try/except in test
- **Arrange-Act-Assert pattern:**
  ```python
  def test_user_can_be_deactivated(self):
      # Arrange: Set up test data
      user = User.objects.create(username="testuser", is_active=True)

      # Act: Perform the action being tested
      user.is_active = False
      user.save()

      # Assert: Verify the result
      user.refresh_from_db()
      self.assertFalse(user.is_active)
  ```

### Test Coverage Exclusions

**Use `# pragma: no cover` for code that doesn't need coverage:**

- Model `__str__()` methods: `def __str__(self): # pragma: no cover`
- Admin display methods that are simple property accessors or counts
- Simple one-line methods that just return formatted strings or counts

### Test Performance Optimization

**Test Settings Configuration:**

Create a dedicated test settings file (`config/settings_test.py`) with optimizations:

```python
# config/settings_test.py
from config.settings import *  # Import production settings

# SQLite in-memory database (10x faster than PostgreSQL)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": True,
    }
}

# MD5 password hashing (10x faster than PBKDF2 - security not needed in tests)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Console email backend (no I/O overhead)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable migrations (fresh database created for each test session)
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()
```

**Run tests with optimized settings:**

```bash
DJANGO_SETTINGS_MODULE=config.settings_test python manage.py test
```

**Pre-commit Configuration:**

Update `.pre-commit-config.yaml` to use test settings automatically:

```yaml
- id: runtests
  entry: bash -c "DJANGO_SETTINGS_MODULE=config.settings_test poetry run coverage run ... manage.py test"
```

**Performance Results:**

- Test execution: 40x faster
- With coverage: 24x faster
- All tests pass with same coverage

**Fixture Creation with setUpTestData():**

Use class-level fixtures for immutable data:

- Move object creation from `setUp()` to `@classmethod setUpTestData(cls)` when data doesn't change between tests
- Keep per-test setup (like `client.login()`) in `setUp()` since state changes per-test
- Pattern: Create fixtures once per test class, not once per test method
- 30-50% speed improvement for test classes with multiple test methods

**Test Data Optimization:**

- Use minimal data sizes (e.g., 10x10 pixel test images instead of 100x100)
- Only use larger data when specifically testing file size validation
- Reuse test fixtures across tests when possible

**Parallel Execution:**

- Tests can run in parallel with appropriate flags
- Automatically uses number of CPU cores available
- 2-4x speedup on multi-core systems

**Coverage Configuration:**

Exclude test files and generated code from coverage reports:

- Omit: `**/tests/*`, `**/test_*.py`, `**/migrations/*`
- Focus coverage on actual application code, not test code or auto-generated files

**Testing Guidance for Time-Based Logic:**

When testing time-bucketed or date-based logic:

- Patch framework's time function to a fixed value for deterministic tests
- For models with auto-timestamp fields, create objects then update timestamp via query and refresh
- Add focused unit tests that call helper methods directly when possible to avoid brittle integration tests
- Example: Test `_get_monthly_stats(start_date, end_date)` directly rather than only testing via view

**See "Principle 2: Fix Problems Immediately When Discovered"** in the Agent Best Practices section for guidance on preventing technical debt and the "Broken Window" effect.

### Debug with Evidence - Prove It Works

**Don't assume code works - verify with concrete evidence:**

- **When debugging bugs:** Don't guess at the problem - gather evidence
  - Add logging or print statements to prove code paths are executed
  - Use a debugger with breakpoints to inspect variable state
  - Add assertions to verify assumptions: `assert user is not None, "User should be authenticated"`
  - Test with real data, not just happy paths
- **When verifying fixes work:** Run the test that reproduces the bug, confirm it passes after fix
  - Don't just read the code and assume it's fixed
  - Write test that specifically covers the bug scenario
  - Include edge cases: None values, empty lists, boundary conditions
- **When validating changes:** Actually run the tests and features, don't skip verification
  - Use real browser testing for UI changes, not just code review
  - Test on mobile devices if relevant
  - Verify database changes with sample data
- **Benefits:**
  - Catches subtle bugs that code review would miss
  - Builds confidence that fix is correct
  - Prevents regressions with test coverage
  - Avoids "it must work because I read the code" fallacy

### Test Prioritization - Avoid Rabbit Holes

**CRITICAL: Don't spend excessive time on low-value tests:**

When a test is causing problems or taking disproportionate time to fix:

- **Evaluate its value:** Does this test provide unique value, or is it redundant with other tests?
- **Check for redundancy:** If similar functionality is already tested elsewhere, DELETE the problematic test rather than spend hours debugging it
- **Recognize the cost:** Spending 30+ minutes on a single test that validates basic framework behavior or duplicates other tests is a waste of time
- **Use judgment:** A test that takes 5x longer to fix than it took to write is a candidate for removal
- **Document:** Add the test result to CHANGELOG but don't spend excessive debugging effort on edge-case test scenarios

**Example red flags:**

- Test relies on complex mock setup that keeps breaking (probably testing framework behavior, not your code)
- Test needs constant tweaking for minor implementation details (sign of brittle test design)
- Test seems to validate basic functionality already covered by other tests (redundant)
- Test setup is nearly as complex as the feature being tested (over-engineered)

**When in doubt:** Delete the redundant test and focus on the ones that provide real value

---

## Security Best Practices

### Django Security Configuration

**Production CSRF Settings (CRITICAL):**

- **ALWAYS configure `CSRF_TRUSTED_ORIGINS`** in settings for production deployments
- Required for Django CSRF middleware to accept POST requests from HTTPS origins
- Without this setting, all form submissions will fail with "Origin checking failed" error
- Configuration example:
  ```python
  CSRF_TRUSTED_ORIGINS = [
      "https://yourdomain.com",
  ]
  ```

**Testing Checklist for New Domains:**

- Add domain to `ALLOWED_HOSTS`
- Add HTTPS URL to `CSRF_TRUSTED_ORIGINS`
- Test login form submission on production
- Test all POST forms (uploads, updates, etc.)

### Environment Variables and Secrets

**Key Principle:** Proper environment configuration is essential for security and deployability across development, staging, and production environments.

**Never Hardcode Secrets in Source Code:**

- Remove all hardcoded database credentials, SECRET_KEYs, and API keys from settings.py
- Use django-environ to read from .env files during development
- Prevents accidental exposure of secrets in git commits
- Makes it easier to rotate credentials in production

**.env File Management:**

- Create `.env.example` template file with all required variables and default values
- Add `.env` to `.gitignore` to prevent committing sensitive data
- The `.env.example` should be version-controlled to document requirements for new developers
- Developers copy `.env.example` to `.env` and customize for their environment
- For production: use platform-native environment variable management (Heroku Config Vars, AWS Systems Manager, etc.)
- Never commit actual `.env` files to version control

**Environment Variable Naming Conventions:**

- Use UPPERCASE_WITH_UNDERSCORES for all environment variable names
- Group related variables with prefixes: `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Use descriptive names that indicate purpose: `SECRET_KEY`, `ALLOWED_HOSTS`

**Development vs Production Configuration:**

Use sensible defaults for development while allowing override in production:

```python
# Settings pattern with environment variables
SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-key-here")
DEBUG = env("DEBUG", default=True)  # Explicit type casting
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")
DB_PASSWORD = env("DB_PASSWORD", default="dev-password")
```

- **Development defaults:** `DEBUG=True`, localhost database, insecure SECRET_KEY
- **Production values:** `DEBUG=False`, secure credentials, strong SECRET_KEY
- Environment variables always override defaults in production
- Type casting: Explicitly convert string environment variables to correct types (booleans, lists, etc.)

**Required Environment Variables in Production:**

Always define these variables when deploying to production:

- `SECRET_KEY` - Generate a new strong random key (not the development default)
- `DEBUG` - Set to False in production
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts (your domain)
- `DB_*` - Database connection credentials (engine, name, user, password, host, port)

**Example Environment Configuration:**

```
# Development (.env.dev)
DEBUG=True
SECRET_KEY=django-insecure-dev-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DB_PASSWORD=dev-password

# Production (.env.prod)
DEBUG=False
SECRET_KEY=<generate-strong-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=<secure-production-password>
```

**Best Practices:**

- Always set `DEBUG=False` in production
- Use strong, unique SECRET_KEY values in production (never reuse development keys)
- Use secure database passwords in production
- Test production-like configurations before deployment
- Validate deployment configurations match security requirements
- Document all required environment variables in DEVELOPMENT.md
- Include examples for both development and production values
- Clearly mark which variables must be changed in production
- Make it easy for new team members to get started by documenting the setup process

**Validation Checklist:**

- [ ] All sensitive data moved from settings.py to environment variables
- [ ] `.env.example` created with complete list of required variables
- [ ] `.env` added to `.gitignore` to prevent accidental commits
- [ ] Reasonable defaults provided for development convenience
- [ ] Documentation (DEVELOPMENT.md) updated with setup instructions and examples
- [ ] All tests pass with environment-based configuration
- [ ] Developers can run application without modifying settings.py
- [ ] Production deployment uses platform-native environment variable management

### General Security Requirements

- HTTPS everywhere in production
- Secure file upload validation
- Rate limiting on public endpoints
- CSRF protection on all forms
- Input sanitization and validation
- Proper authentication and authorization checks

---

## Database Management

### Migration Strategy

**Important - User Responsibility:**

- Users are responsible for running migrations (`python manage.py makemigrations` and `python manage.py migrate`)
- AI agents may create migration files using `makemigrations` (dry-run is acceptable)
- AI agents must document which migrations were created
- The user maintains control over when and how database schema changes are applied

**Migration Best Practices:**

- Always create reversible migrations
- Test migrations on sample data before production
- Document breaking changes in migration comments
- Use descriptive migration names

### Common Patterns

- Use `select_related()` and `prefetch_related()` for query optimization
- Index frequently queried fields
- Use database constraints where appropriate
- Avoid N+1 query problems

---

## Development Workflow

### Code Formatting & Structure (Clean Code)

**Use whitespace and formatting to reveal code structure:**

- **Vertical spacing:** Group related lines, separate unrelated concepts
  - Bad: No blank lines between unrelated operations (dense, hard to scan)
  - Good: Blank lines between logical sections (easy to scan and understand)
  - Example:
    ```python
    # Bad - all dense together
    user = get_user(id)
    items = user.items.all()
    count = items.count()
    total = sum(item.price for item in items)
    formatted_user = format_user(user)
    formatted_items = format_items(items)
    render_template('dashboard', {'user': formatted_user, 'items': formatted_items})

    # Good - related operations grouped together
    user = get_user(id)
    items = user.items.all()

    count = items.count()
    total = sum(item.price for item in items)

    formatted_user = format_user(user)
    formatted_items = format_items(items)

    render_template('dashboard', {'user': formatted_user, 'items': formatted_items})
    ```
- **Keep lines reasonably short:** Aim for 80-100 characters max (helps readability on narrow screens)
- **Indentation consistency:** Follow project standards strictly (Python=4 spaces, HTML/CSS/JS=2 spaces)
- **Organize class members logically:**
  - Constants first
  - Static methods
  - `__init__` and lifecycle methods
  - Public methods
  - Private methods
  - Properties/descriptors at the end
- **Related concepts close together:** Don't scatter related functionality across a large class

### File Formatting

- All files must end with a newline character (actual `\n`, not just empty space)
- Let pre-commit hooks handle formatting automatically
- Compiled/generated files (like `static/css/styles.css`) should be excluded from pre-commit formatting
- Markdown files may be excluded from formatters to preserve specific formatting requirements

### Documentation

**Maintain comprehensive documentation:**

These should be updated for issue worked (CHANGELOG.md for sure, the rest should be update appropriately where action was taken that relates to each document's purpose)

- `README.md` - Project overview and setup
- `CHANGELOG.md` - Document all changes made for each issue/feature
- `DEVELOPMENT.md` - Technical implementation details specifically for this project
- `CLAUDE.md` - Development guidelines and general best practices good for any project (this file)

**Documentation Updates:**

- **ALL changes must be documented in CHANGELOG.md** with detailed descriptions
- Update relevant documentation when adding new patterns or utilities
- Add usage examples where appropriate
- Document new commands, utilities, or patterns created

### Issue Management

**Issue Scope:**

- Keep issues small and focused - one specific task or change per issue
- Limit scope to 10 files or less whenever possible
- Break large features into multiple focused issues

**Issue Labeling:**

- Use priority labels (`must-have`, `should-have`, `nice-to-have`)
- Use effort labels (`trivial`, `simple`, `moderate`, `complex`, `difficult`)
- All issues should have both priority and effort labels

### Development Environment

**Virtual Environment:**

- Use modern dependency management (Poetry, pipenv, etc.)
- Keep dependencies isolated and version-controlled
- Run all Python/Django commands via your package manager: `poetry run python manage.py [command]`
- **IMPORTANT:** Always use `poetry add [package]` to add new dependencies - NEVER manually edit `pyproject.toml`
  - `poetry add` automatically updates both `pyproject.toml` and `poetry.lock` with correct versions
  - Manual edits risk version conflicts and broken lock files
  - Always source the venv before running poetry commands: `source .venv/bin/activate && poetry add [package]`

**Testing:**

- DO NOT start the development server (`runserver`) during development tasks
- Use `python manage.py check` to verify Django configuration
- Run tests with `python manage.py test`
- The application does not need to be running for development work

**Media Files:**

- Configure `MEDIA_ROOT` for uploaded files
- Serve at `MEDIA_URL` in development
- Use date-based paths for organized storage: `uploads/%Y/%m/%d/`

**Environment Variables:**

- Development: `.env.dev`
- Production: `.env.prod`
- Database: `.env.prod.db` (if separate)
- Never commit environment files to git

---

## Agent Best Practices (from The Pragmatic Programmer)

### Principle 1: Provide Options, Not Excuses

When constraints are discovered or blockers appear:

- **Never simply say "it can't be done"** - always provide the user with viable options
- When a requested approach has issues, analyze alternatives and present tradeoffs clearly
- **Format options with clarity:**
  - Option A: Approach with its specific benefits and limitations
  - Option B: Alternative approach with different tradeoffs
  - Recommendation: Which option is pragmatic and why
- If scope needs adjustment, propose specific scope changes rather than rejecting the task
- Explain technical constraints in user-friendly terms with concrete examples
- Offer creative solutions that work within project constraints
- Document decisions in code comments and commit messages for future reference

**Example (NOT this):** "We can't refactor that without breaking tests"
**Example (THIS):** "Refactoring has two viable paths:
- Option A: Refactor incrementally with full test coverage (slower, safer)
- Option B: Refactor with fallback tests (faster, slightly riskier)
- Recommendation: Option A because stability is critical here"

### Principle 2: Fix Problems Immediately When Discovered

Addresses technical debt and design issues proactively:

- **Upon discovering bad code/design/bugs:** Create a task to fix it immediately rather than deferring
- **Escalate appropriately:** If fixing now blocks current work, document the issue and ensure it's tracked
- **Don't ignore warnings:** Unused imports, type errors, linting failures - fix them right away
- **Prevent compounding debt:** Small issues compound exponentially, fixed early they're trivial
- **Update documentation:** When fixing design issues, update CLAUDE.md and DEVELOPMENT.md
- **Test the fix thoroughly:** When fixing bugs, ensure the fix is robust and well-tested
- **Commit immediately:** Don't batch fixes - commit each fix with clear messaging

**Benefits:**
- Code quality stays high consistently
- Prevents "broken window" effect where one bad pattern spreads
- Keeps codebase maintainable and refactorable
- Developers stay confident in the code they're working with

### Principle 3: Apply DRY (Don't Repeat Yourself) & Code Reusability

Every piece of knowledge must have a single, unambiguous source of truth. Make reusable code easy to use and understand.

**DRY - Never Repeat Yourself:**

Every concept should exist in only one place in the codebase:

- **Code duplication:** Extract duplicated logic into shared utilities, mixins, or template includes
- **Constants in multiple places:** Define once, import everywhere
  - Example: Validation rules (file size limits, allowed formats) defined as `ALLOWED_FORMATS = ["jpg", "png", "gif"]` in one place
  - Import in Python, JavaScript, and templates from that single source
- **Template patterns:** Create reusable template includes for common UI patterns instead of copy-pasting HTML
- **Configuration values:** Never hardcode the same value in multiple places - use settings, constants, or template variables
- **SQL queries:** Use ORM querysets consistently rather than writing raw SQL multiple times
- **Regular expressions:** Define complex patterns as named constants, not inline
- **Validation logic:** Single implementation in form/model, referenced from all validation points

**Refactoring Strategy:**

- When you see duplication, resist the urge to "get it working" first - refactor immediately
- Break 3+ instances of similar code into shared logic
- Test the extracted logic thoroughly before removing duplication
- Update comments to explain why code is shared, not just what it does

**Benefits of DRY:**

- Changes to logic need to happen in only one place
- Bugs fixed in one place fix everywhere at once
- Easier to maintain consistency across the codebase
- Reduces cognitive load - fewer things to understand

**Code Reusability - Make Components Reusable Everywhere:**

When creating code (functions, classes, templates, components), design them to be usable in multiple contexts, not just the current one:

- **Clear interfaces:** Public API should be obvious and minimal
  - Document what parameters are required vs optional
  - Provide sensible defaults
  - Include usage examples in docstrings
- **Discoverable components:** Name things clearly so reuse is obvious
  - Template includes with descriptive names: `_pagination.html`, `_error_alert.html`
  - Utility functions with clear purpose: `format_phone_number()`, `validate_file_upload()`
  - Mixins named for their behavior: `TimestampMixin`, `SlugifyMixin`
- **Remove unnecessary coupling:** Components shouldn't depend on specific app structure or database models
  - Use parameters instead of accessing globals
  - Accept generic data types, not specific model instances
  - Example: Accept a list of items, not a specific QuerySet
- **Document limitations and assumptions:** If a component has constraints, document them
  - "Assumes items are sorted chronologically"
  - "Requires Bootstrap 5 for styling"
  - "Works with HTML5 only"
- **Provide configuration:** Let callers customize behavior without modifying code
  - CSS class parameters for styling
  - Callback functions for custom behavior
  - Template override hooks
- **Keep components focused:** Single responsibility makes reuse easier
  - A pagination component does pagination, not sorting
  - A form includes field rendering, not business logic
  - A utility formats data, doesn't fetch it
- **Design for flexibility and change:** Code must adapt as requirements change
  - Avoid hard-coding paths/IDs/values - make them configurable through templates, settings, or parameters
  - When creating components (templates, views, utilities), design them to be used in multiple contexts
  - Use flexible context variables with sensible defaults; don't assume a single use case
  - Example: A card component should work with/without images, different text lengths, various button configurations
  - Settings over magic strings: Use settings for values that might change per environment or deployment
  - Backward compatibility: When changing APIs, provide deprecation paths rather than breaking changes
  - Extensibility hooks: Design classes/functions for subclassing or extension rather than modification

**Refactoring for Reusability:**

- When writing a component for one use case, ask: "How would someone else use this?"
- If extraction requires understanding the original context, it's not reusable
- Test components in at least 2 different contexts before marking as "done"
- Update template/module docs when making something reusable
- When adding new components to the codebase, design them to be usable in most any other context in the project

**Benefits of Reusability:**

- Same code serves multiple features, reducing development time
- Consistent UI/behavior across entire application
- Fixes/improvements to components benefit all users of that component
- Easier to maintain patterns and standards
- Code is self-documenting through consistent patterns

**Implementation Pattern Example:**
```python
# Good - flexible and configurable
class CardComponent:
    def __init__(self, title, image_url=None, button_text="Learn More", button_url=None):
        self.title = title
        self.image = image_url  # Optional
        self.button_text = button_text  # Customizable
        self.button_url = button_url  # Optional

# Avoid - hard-coded for single use case
class FeaturedProductCard:
    def render(self):
        return f"<div>{self.title}<img src='/images/{self.id}.jpg'>..."
```

### Principle 4: Clarify Requirements & Understand Before Building

Never assume you understand the requirement - ask clarifying questions:

- **Before starting work:** Ensure the requirement is unambiguous
  - "What does 'admin dashboard' mean?" - Real-time data? What metrics? How many users?
  - "Fix the slow search" - Which queries are slow? What volume of data? Acceptable latency?
  - "Add user profiles" - What fields? Photo upload? Validation rules?
- **Identify edge cases and constraints:**
  - "Can users have multiple profiles?" or "One profile per user?"
  - "What happens to data when user deletes account?"
  - "Do we need to support international characters?" or "ASCII only?"
- **Document assumptions in writing:**
  - Once clarified, write down the specifics in the issue/task
  - Prevents misunderstandings when building or reviewing
  - Makes estimation more accurate
- **Ask about priorities when trade-offs exist:**
  - "Build quickly (2 days) with basic features, or build fully (5 days) with all features?"
  - "Perfect for 1000 users or scalable to 1 million?"
  - "Ship now with minimal testing or spend time on quality?"
- **Understand WHY before building:**
  - "Why do we need this feature?" - Business goal? User problem? Competitive feature?
  - Understanding purpose helps make better design decisions
  - Prevents building wrong solution to the stated problem
- **Benefits:**
  - Avoids rework from misunderstood requirements
  - More accurate time estimates
  - Faster implementation (no back-and-forth clarifications during build)
  - Confidence that solution actually solves the real problem
  - Better design decisions informed by context

### Principle 5: Professional Communication & Transparency

Communicate clearly about status, blockers, and decisions:

- **Transparency about progress:**
  - Don't wait until end to surface blockers - report immediately when discovered
  - Explain what you've done, what you're currently working on, what's next
  - Include actual evidence: "tests pass", "feature works in browser X", "covers N edge cases"
- **Explain decisions and tradeoffs:**
  - Don't just implement one way - explain why that way vs alternatives
  - "Chose approach A because X, could also do B but has limitation Y"
  - Use data/evidence when possible: "QuerySet filtering is faster than Python filtering based on benchmark"
- **Admit what you don't know:**
  - "I'm uncertain about X, let me research" vs pretending to know
  - "This might have performance implications, should we test?"
  - "I'm not sure if Django's built-in behavior covers this case"
- **Ask for feedback early and often:**
  - Show code early before it's "perfect" - catch misunderstandings sooner
  - "Does this approach make sense to you?" vs waiting for final review
  - Request clarification when something is unclear rather than guessing
- **Document important decisions:**
  - Why a particular library was chosen
  - Why a component was designed a certain way
  - Known limitations or future refactoring needs
  - Add comments to CLAUDE.md or DEVELOPMENT.md if it's a pattern
- **Benefits:**
  - Builds trust through transparency and honesty
  - Reduces surprises and scope creep
  - Catches misunderstandings early when changes are cheap
  - Improves collaboration and knowledge sharing
  - Makes code reviews faster (context already clear)

---

## Command-Line Tools for Agents

AI agents and developers should use command-line tools strategically for **read operations** and source control management. This section covers best practices for using `git`, `gh` (GitHub CLI), and other command-line tools effectively.

### Git Operations

**Use git for source control tasks, not for code communication:**

- **Primary purpose:** Track project history, manage branches, understand code evolution
- **For agents:** Use git to understand current state, inspect changes, and view commit history
- **Read operations:**
  - `git status` - See working tree status and staged changes
  - `git diff` - Compare working changes vs staged changes
  - `git log` - View commit history with messages and authorship
  - `git show [commit]` - Inspect specific commits
  - `git branch -a` - List all branches (local and remote)
  - `git remote -v` - View configured remotes

**Never use git as a communication tool:**

- Don't commit "work in progress" messages to ask for feedback
- Don't use commit messages to document decisions or requirements
- Don't rely on git history to communicate project context
- Use documentation files (CLAUDE.md, DEVELOPMENT.md, CHANGELOG.md) for communication instead

**Safe read-only git patterns for agents:**

```bash
# Inspect current state (safe, read-only)
git status
git diff
git log --oneline -10

# Understand branch structure (safe)
git branch -a
git log [branch]...HEAD  # See commits on current branch

# Check authorship (safe, informational)
git log -1 --format='%an %ae'

# View specific file history (safe)
git log -- path/to/file.py
git show commit:path/to/file.py  # View file at specific commit
```

**Common git patterns agents should support:**

- **Before making changes:** Run `git status` and `git diff` to understand current state
- **After changes:** Document what changed, why, and how to test in commit messages
- **Before committing:** Always check what's being committed to avoid accidental includes
- **Review commits:** Use `git log` to understand recent changes and patterns

### GitHub CLI (gh)

**Use `gh` for GitHub-specific operations and metadata:**

- **Primary purpose:** Interact with GitHub API for PRs, issues, checks, and releases
- **For agents:** Use `gh` to gather information about issues, PRs, and repository state
- **Safe operations:**
  - `gh issue view [number]` - Get issue details
  - `gh pr view [number]` - Get PR details
  - `gh pr list` - List open PRs
  - `gh issue list` - List open issues
  - `gh api` - Make GraphQL queries to get repository metadata
  - `gh release list` - View existing releases

**GitHub CLI for PR/issue context:**

```bash
# Get full PR information
gh pr view 123

# Check PR status and checks
gh pr view 123 --json status,checks,commits

# List open PRs with labels
gh pr list --label "bug"

# Get issue details with assignee and labels
gh issue view 456

# Check commit status
gh api repos/owner/repo/commits/sha/status
```

**When to use `gh` vs git:**

- **Use `gh`** - Getting PR/issue metadata, checking CI status, inspecting GitHub-specific data
- **Use `git`** - Local repository operations, commit history, branch management
- **Use both** - Understanding context: `gh pr view` for the PR, `git log` for commits it contains

### Command-Line Tool Strategy for Agents

**Read operations are safe and encouraged:**

Agents should actively use read operations to understand code context before making changes:

- **Explore codebase:** Use file search tools to find relevant code
- **Understand state:** Use `git status` and `git diff` to see current changes
- **Review history:** Use `git log` to understand recent changes and patterns
- **Check tests:** Run tests to validate changes
- **Inspect CI:** Use `gh pr checks` to see test results

**Write operations require explicit user consent:**

- Never make commits, push changes, or create PRs without explicit user request
- Always show the user what will be committed before creating commits
- Get explicit approval for potentially destructive operations (force push, rebase, etc.)
- Respect git hooks and pre-commit configurations
- Never bypass safety mechanisms (--no-verify, --force, etc.)

**Best practices for agent tool usage:**

1. **Gather context first:** Use read operations to understand the current state
2. **Propose changes:** Show user what will be changed before making changes
3. **Execute with explicit approval:** Only write after user explicitly requests action
4. **Verify results:** Use read operations to confirm changes are correct
5. **Report findings:** Communicate results back to user via documentation

### Common Development Tasks with CLI Tools

**Understanding a failing test:**

```bash
# See what files have been changed
git status

# Review the diff of recent changes
git diff

# Look at recent commits to understand context
git log -5 --oneline

# Run the failing test to see error
python manage.py test app.tests.test_module.TestCase.test_method
```

**Investigating a code section:**

```bash
# Find related files by pattern
grep -r "FunctionName" apps/

# Check git history of specific file
git log --oneline -- path/to/file.py

# See who last modified a line
git blame path/to/file.py

# View full commit that changed important section
git show commit-hash
```

**Reviewing a PR before implementation:**

```bash
# Get PR details and commit information
gh pr view 123

# See all commits in the PR
gh pr view 123 --json commits

# Check if CI passed
gh pr view 123 --json status,checks

# View the diff (if repo is local)
git diff origin/main...feature-branch
```

**Tracking project state over time:**

```bash
# See recent commits by multiple authors
git log -20 --oneline

# Find commits by specific person
git log --author="Name" -10 --oneline

# Understand branch status
git branch -a
git for-each-ref --sort=-committerdate refs/heads/

# Check what's ahead/behind remote
git log --oneline origin/main..HEAD  # Local commits not yet pushed
git log --oneline HEAD..origin/main  # Remote commits not yet pulled
```

### Tool Usage Philosophy

**Leverage tools for understanding, not communication:**

- Use tools to gather accurate information about code state
- Use documentation files to communicate decisions and context
- Use commit messages to explain code changes (git responsibility)
- Use GitHub issues/PRs to track work and get feedback (gh responsibility)
- Use CLAUDE.md/DEVELOPMENT.md to document patterns and practices (documentation responsibility)

**Respect tool boundaries:**

- git is for code version control and history
- gh is for GitHub platform interaction
- Documentation is for context and best practices
- Each tool has a specific purpose; use them appropriately

**Tool output interpretation:**

- `git status` tells you what files are staged/unstaged
- `git diff` shows actual code changes (useful for review)
- `git log` provides commit history and authorship information
- `gh pr view` gives GitHub-specific metadata
- Exit codes indicate success (0) or failure (non-zero)

---


## Key Principles Summary

- **Documentation First:** Always read docs before coding
- **Consistency:** Follow established patterns and conventions
- **Quality:** No shortcuts - do it right the first time
- **Communication:** Keep stakeholders informed of progress and decisions
- **Evidence-Based:** Check existing code before claiming work is needed
- **Mobile-First:** Design for mobile devices first, enhance for desktop
- **Progressive Enhancement:** Core functionality works without JavaScript
- **Accessibility:** Build inclusive experiences for all users
- **Performance:** Optimize for speed and efficiency
- **Security:** Follow security best practices always
- **Testability:** Write testable code and comprehensive tests for custom logic only
- **Maintainability:** Write code that's easy to understand and modify

---

_This guide represents generalized best practices for building modern web applications with Django, Tailwind CSS, Alpine.js, HTMX, and progressive JavaScript enhancement. Adapt these principles to your specific project needs while maintaining the core philosophy of simplicity, quality, and user-focused design._