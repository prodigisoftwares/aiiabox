from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form with improved styling for Tailwind CSS.

    Extends Django's built-in AuthenticationForm with:
    - Username field
    - Password field
    - Custom widget classes for Tailwind styling
    """

    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded "
                "dark:bg-gray-800 dark:border-gray-600 dark:text-gray-50 "
                "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                "transition-colors",
                "placeholder": "Username",
            }
        ),
        label="Username",
    )

    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded "
                "dark:bg-gray-800 dark:border-gray-600 dark:text-gray-50 "
                "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                "transition-colors",
                "placeholder": "Password",
            }
        ),
        label="Password",
    )

    class Meta:
        model = User
        fields = ("username", "password")

    def clean(self):
        """
        Validate username and password combination.

        Provides user-friendly error messages for invalid credentials.
        """
        cleaned_data = super().clean()
        return cleaned_data
