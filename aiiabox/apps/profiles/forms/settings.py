from django import forms

from apps.profiles.models import UserSettings


class UserSettingsForm(forms.ModelForm):
    """
    Form for editing user settings and preferences.

    Allows users to update their theme preference. Extensible for future
    LLM preferences (model, temperature, max_tokens, etc.).

    Fields:
        theme: Choice field for UI theme preference (light/dark/auto)

    Excludes:
        user: User is set from request context
        default_project: Not editable via form (will be added in Phase 4)
        llm_preferences: Not editable via form (requires specialized interface)
        created_at: Auto-generated timestamp
        updated_at: Auto-generated timestamp

    Validation:
        theme: Validates against THEME_CHOICES defined in UserSettings model
    """

    class Meta:
        model = UserSettings
        fields = ("theme",)
        widgets = {
            "theme": forms.RadioSelect(
                attrs={
                    "class": "form-radio",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text to the theme field
        self.fields["theme"].help_text = "Choose your preferred UI theme"
        self.fields["theme"].label = "Theme Preference"
