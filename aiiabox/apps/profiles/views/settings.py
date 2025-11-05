from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from apps.profiles.forms import UserSettingsForm
from apps.profiles.models import UserSettings


class SettingsEditView(LoginRequiredMixin, UpdateView):
    """
    View for editing user settings (theme preference).

    Displays a form pre-filled with the logged-in user's current settings.
    On form submission, updates the settings in the database and redirects to
    the profile detail page.

    Assumes:
        - User is authenticated (enforced by LoginRequiredMixin)
        - User has UserSettings (auto-created via signal in apps.profiles.signals)

    Returns:
        - GET: Rendered form with pre-filled user settings data
        - POST (valid): Redirect to profile detail page
        - POST (invalid): Re-render form with validation errors

    Side effects:
        - Updates UserSettings in database on valid form submission
    """

    model = UserSettings
    form_class = UserSettingsForm
    template_name = "profiles/settings_edit.html"

    def get_object(self, queryset=None):
        """
        Get the current user's settings.

        Returns the UserSettings associated with the authenticated user.
        Does not require a URL parameter since we're always editing the
        current user's settings.

        Returns:
            UserSettings: The settings for the currently authenticated user
        """
        return self.request.user.settings

    def get_success_url(self):
        """
        Get the URL to redirect to after successful form submission.

        Redirects to the profile detail page after settings are updated.

        Returns:
            str: URL path for profile detail view
        """
        return reverse_lazy("profiles:profile_detail")
