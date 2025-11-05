from django import forms

from apps.profiles.models import UserProfile


class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile information.

    Allows users to update their avatar and bio. Uses Tailwind CSS styling
    for form inputs and validation.

    Fields:
        avatar: ImageField for profile picture (optional, up to 10MB, any image type)
        bio: TextField for user biography (optional, no length limit)

    Excludes:
        user: User is set from request context
        created_at: Auto-generated timestamp
        updated_at: Auto-generated timestamp
        preferences: Not editable via form (use settings for extensible prefs)

    Validation:
        avatar: File size max 10MB
    """

    class Meta:
        model = UserProfile
        fields = ("avatar", "bio")
        widgets = {
            "avatar": forms.FileInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded "
                    "dark:bg-gray-800 dark:border-gray-600 dark:text-gray-50 "
                    "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                    "transition-colors",
                    "accept": "image/*",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded "
                    "dark:bg-gray-800 dark:border-gray-600 dark:text-gray-50 "
                    "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                    "transition-colors",
                    "rows": 4,
                    "placeholder": "Tell us about yourself...",
                }
            ),
        }

    def clean_avatar(self):
        """
        Validate avatar file size (max 10MB).

        Raises:
            ValidationError: If file size exceeds 10MB
        """
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            max_size_mb = 10
            max_size_bytes = max_size_mb * 1024 * 1024

            if avatar.size > max_size_bytes:
                raise forms.ValidationError(
                    f"Image size must not exceed {max_size_mb}MB. "
                    f"Your file is {avatar.size / (1024 * 1024):.1f}MB."
                )

        return avatar
