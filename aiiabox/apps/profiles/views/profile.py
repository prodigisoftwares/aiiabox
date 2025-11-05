from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView

from apps.profiles.forms import UserProfileForm
from apps.profiles.models import UserProfile


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying user profile information.

    Shows the logged-in user's profile data (avatar, bio, account info).
    Provides a link to edit the profile.

    Assumes:
        - User is authenticated (enforced by LoginRequiredMixin)
        - User has a UserProfile (auto-created via signal in apps.profiles.signals)

    Returns:
        - GET: Rendered profile detail page with user information
    """

    model = UserProfile
    template_name = "profiles/profile_detail.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        """
        Get the current user's profile.

        Returns the UserProfile associated with the authenticated user.

        Returns:
            UserProfile: The profile for the currently authenticated user
        """
        return self.request.user.profile


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    View for editing user profile (avatar, bio).

    Displays a form pre-filled with the logged-in user's current profile data.
    On form submission, updates the profile in the database and redirects to
    the profile detail page.

    Assumes:
        - User is authenticated (enforced by LoginRequiredMixin)
        - User has a UserProfile (auto-created via signal in apps.profiles.signals)

    Returns:
        - GET: Rendered form with pre-filled user profile data
        - POST (valid): Redirect to profile detail page
        - POST (invalid): Re-render form with validation errors

    Side effects:
        - Updates UserProfile in database on valid form submission
        - Writes avatar file to filesystem if provided
    """

    model = UserProfile
    form_class = UserProfileForm
    template_name = "profiles/profile_edit.html"

    def get_object(self, queryset=None):
        """
        Get the current user's profile.

        Returns the UserProfile associated with the authenticated user.
        Does not require a URL parameter since we're always editing the
        current user's profile.

        Returns:
            UserProfile: The profile for the currently authenticated user
        """
        return self.request.user.profile

    def get_success_url(self):
        """
        Get the URL to redirect to after successful form submission.

        Redirects to the profile detail page after profile is updated.

        Returns:
            str: URL path for profile detail view
        """
        return reverse_lazy("profiles:profile_detail")
