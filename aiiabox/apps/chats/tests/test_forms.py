from django.test import TestCase

from apps.chats.forms import ChatForm


class ChatFormTests(TestCase):
    """Tests for ChatForm."""

    def test_valid_form(self):
        """ChatForm is valid with a proper title."""
        form = ChatForm(data={"title": "Valid Chat Title"})
        self.assertTrue(form.is_valid())

    def test_required_title(self):
        """ChatForm title field is required."""
        form = ChatForm(data={"title": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_max_length_255(self):
        """ChatForm title can be up to 255 characters."""
        title = "a" * 255
        form = ChatForm(data={"title": title})
        self.assertTrue(form.is_valid())

    def test_exceeds_max_length(self):
        """ChatForm rejects title over 255 characters."""
        title = "a" * 256
        form = ChatForm(data={"title": title})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_title_whitespace_trimming(self):
        """ChatForm trims leading and trailing whitespace from title."""
        form = ChatForm(data={"title": "  Chat Title  "})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "Chat Title")

    def test_title_internal_spaces_preserved(self):
        """ChatForm preserves internal spaces in title."""
        form = ChatForm(data={"title": "Chat  With  Multiple  Spaces"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "Chat  With  Multiple  Spaces")

    def test_special_characters_allowed(self):
        """ChatForm allows special characters in title."""
        title = "Chat: Python & AI! (v2.0)"
        form = ChatForm(data={"title": title})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], title)

    def test_unicode_characters(self):
        """ChatForm allows unicode characters in title."""
        title = "Python 🐍 Chat 中文"
        form = ChatForm(data={"title": title})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], title)
