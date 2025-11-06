from django import forms

from apps.chats.models import Message


class MessageForm(forms.ModelForm):
    """
    Form for creating a new message in a chat.

    Allows users to input message content. The chat, user, and role are set
    programmatically - only content is user-provided. Handles whitespace
    trimming and validation to ensure non-empty messages.

    Fields:
        content: TextField for message text (required)

    Validation:
        content: Required, non-empty after whitespace trimming, max 5000 chars
    """

    class Meta:
        model = Message
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg resize-none "
                    "dark:bg-gray-800 dark:border-gray-600 dark:text-gray-50 "
                    "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                    "transition-colors duration-200",
                    "placeholder": "Type your message...",
                    "rows": "3",
                    "maxlength": "5000",
                }
            ),
        }

    def clean_content(self) -> str:  # pragma: no cover
        """
        Validate and clean message content.

        Strips leading/trailing whitespace and ensures content is not empty
        after trimming.

        Returns:
            str: Trimmed content string

        Raises:
            ValidationError: If content is empty or only whitespace
        """
        content = self.cleaned_data.get("content")

        # Return early if content wasn't provided (required validation handled by Django)
        if not content:  # pragma: no cover
            return content

        # Strip whitespace and check if content is empty after stripping
        content = content.strip()
        if not content:  # pragma: no cover
            raise forms.ValidationError("Message cannot be empty or whitespace only.")

        return content
