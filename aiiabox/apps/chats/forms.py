from django import forms

from apps.chats.models import Chat


class ChatForm(forms.ModelForm):
    """
    Form for creating or editing a chat.

    Allows users to set a chat title. Handles whitespace trimming and validation
    to ensure valid chat titles.

    Fields:
        title: CharField for chat name (required, max_length=255)

    Validation:
        title: Required, max 255 characters, whitespace trimmed
    """

    class Meta:
        model = Chat
        fields = ("title",)
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded "
                    "dark:bg-gray-800 dark:border-gray-600 dark:text-gray-50 "
                    "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                    "transition-colors",
                    "placeholder": "Chat title...",
                    "maxlength": "255",
                }
            ),
        }

    def clean_title(self) -> str:
        """
        Validate and clean chat title.

        Strips leading/trailing whitespace and ensures title is not empty
        after trimming.

        Returns:
            str: Trimmed title string

        Raises:
            ValidationError: If title is empty or only whitespace
        """
        title = self.cleaned_data.get("title")

        # Return early if title wasn't provided (required validation handled by Django)
        if not title:  # pragma: no cover
            return title

        # Strip whitespace and check if title is empty after stripping
        title = title.strip()
        if not title:  # pragma: no cover
            raise forms.ValidationError(
                "Chat title cannot be empty or whitespace only."
            )

        return title
