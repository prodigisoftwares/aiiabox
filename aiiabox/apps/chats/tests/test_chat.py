from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.chats.models import Chat, Message


class ChatModelTests(TestCase):
    """Test suite for Chat model."""

    @classmethod
    def setUpTestData(cls):
        """Create reusable test data for all test methods."""
        cls.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        cls.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )

    def test_chat_creation_with_required_fields(self):
        """Test creating a chat with only required fields."""
        chat = Chat.objects.create(user=self.user, title="Test Chat")

        self.assertEqual(chat.user, self.user)
        self.assertEqual(chat.title, "Test Chat")
        self.assertEqual(chat.metadata, {})
        self.assertIsNotNone(chat.created_at)
        self.assertIsNotNone(chat.updated_at)

    def test_chat_creation_with_metadata(self):
        """Test creating a chat with metadata."""
        metadata = {"model": "llama-2", "temperature": 0.7, "max_tokens": 2048}
        chat = Chat.objects.create(
            user=self.user, title="Chat with Metadata", metadata=metadata
        )

        chat.refresh_from_db()
        self.assertEqual(chat.metadata, metadata)
        self.assertEqual(chat.metadata["model"], "llama-2")
        self.assertEqual(chat.metadata["temperature"], 0.7)

    def test_chat_title_max_length(self):
        """Test chat title respects max length constraint."""
        long_title = "a" * 255
        chat = Chat.objects.create(user=self.user, title=long_title)

        self.assertEqual(len(chat.title), 255)

    def test_chat_timestamps_auto_set(self):
        """Test that created_at and updated_at are automatically set."""
        before = timezone.now()
        chat = Chat.objects.create(user=self.user, title="Timestamp Test")
        after = timezone.now()

        self.assertGreaterEqual(chat.created_at, before)
        self.assertLessEqual(chat.created_at, after)
        # For newly created objects, created_at and updated_at should be very close
        # Allow for small timing differences (within 1 millisecond)
        time_diff = abs((chat.updated_at - chat.created_at).total_seconds())
        self.assertLess(time_diff, 0.001)

    def test_chat_updated_at_changes_on_update(self):
        """Test that updated_at changes when chat is modified."""
        chat = Chat.objects.create(user=self.user, title="Original Title")
        original_updated = chat.updated_at

        # Wait a moment to ensure timestamp difference
        import time

        time.sleep(0.01)

        chat.title = "Updated Title"
        chat.save()

        self.assertGreater(chat.updated_at, original_updated)

    def test_chat_metadata_default_is_empty_dict(self):
        """Test that metadata defaults to empty dict."""
        chat = Chat.objects.create(user=self.user, title="No Metadata")

        self.assertEqual(chat.metadata, {})
        self.assertIsInstance(chat.metadata, dict)

    def test_chat_user_relationship(self):
        """Test that chat is properly associated with user."""
        chat = Chat.objects.create(user=self.user, title="User Chat")

        self.assertEqual(chat.user.username, "testuser")
        self.assertIn(chat, self.user.chats.all())

    def test_multiple_chats_per_user(self):
        """Test that a user can have multiple chats."""
        chat1 = Chat.objects.create(user=self.user, title="Chat 1")
        chat2 = Chat.objects.create(user=self.user, title="Chat 2")
        chat3 = Chat.objects.create(user=self.user, title="Chat 3")

        user_chats = self.user.chats.all()
        self.assertEqual(user_chats.count(), 3)
        self.assertIn(chat1, user_chats)
        self.assertIn(chat2, user_chats)
        self.assertIn(chat3, user_chats)

    def test_chats_isolated_by_user(self):
        """Test that different users have separate chats."""
        chat1 = Chat.objects.create(user=self.user, title="User 1 Chat")
        chat2 = Chat.objects.create(user=self.other_user, title="User 2 Chat")

        self.assertNotIn(chat2, self.user.chats.all())
        self.assertNotIn(chat1, self.other_user.chats.all())

    def test_chat_default_ordering_by_updated_at(self):
        """Test that chats are ordered by updated_at descending."""
        import time

        chat1 = Chat.objects.create(user=self.user, title="Old Chat")
        time.sleep(0.01)
        chat2 = Chat.objects.create(user=self.user, title="New Chat")

        chats = Chat.objects.filter(user=self.user)
        self.assertEqual(chats[0].id, chat2.id)
        self.assertEqual(chats[1].id, chat1.id)

    def test_chat_cascade_delete_messages(self):
        """Test that deleting chat also deletes its messages."""
        chat = Chat.objects.create(user=self.user, title="Chat to Delete")
        Message.objects.create(
            chat=chat, user=self.user, content="Message 1", role="user"
        )
        Message.objects.create(
            chat=chat, user=self.user, content="Message 2", role="assistant"
        )

        chat_id = chat.id
        self.assertEqual(Message.objects.filter(chat_id=chat_id).count(), 2)

        chat.delete()

        self.assertFalse(Chat.objects.filter(id=chat_id).exists())
        self.assertEqual(Message.objects.filter(chat_id=chat_id).count(), 0)

    def test_chat_str_representation(self):
        """Test chat string representation returns title."""
        chat = Chat.objects.create(user=self.user, title="Test Chat Title")

        self.assertEqual(str(chat), "Test Chat Title")

    def test_chat_metadata_complex_structure(self):
        """Test metadata can store complex nested structures."""
        metadata = {
            "model": "gpt-4",
            "settings": {"temperature": 0.8, "top_p": 0.9, "max_tokens": 4096},
            "tags": ["important", "code-review"],
            "context": {"file": "app.py", "line": 42},
        }
        chat = Chat.objects.create(
            user=self.user, title="Complex Metadata Chat", metadata=metadata
        )

        chat.refresh_from_db()
        self.assertEqual(chat.metadata["settings"]["temperature"], 0.8)
        self.assertEqual(chat.metadata["tags"], ["important", "code-review"])
        self.assertEqual(chat.metadata["context"]["line"], 42)

    def test_chat_with_empty_title_allowed(self):
        """Test that empty title is technically allowed at model level."""
        chat = Chat.objects.create(user=self.user, title="")

        self.assertEqual(chat.title, "")
        self.assertTrue(Chat.objects.filter(id=chat.id).exists())

    def test_chat_metadata_can_be_modified_and_saved(self):
        """Test that metadata can be modified and persisted."""
        chat = Chat.objects.create(
            user=self.user, title="Mutable Metadata Chat", metadata={"version": 1}
        )

        chat.metadata["version"] = 2
        chat.metadata["updated"] = True
        chat.save()

        chat.refresh_from_db()
        self.assertEqual(chat.metadata["version"], 2)
        self.assertTrue(chat.metadata["updated"])

    def test_chat_id_is_auto_incremented(self):
        """Test that chat IDs are automatically assigned and unique."""
        chat1 = Chat.objects.create(user=self.user, title="Chat 1")
        chat2 = Chat.objects.create(user=self.user, title="Chat 2")

        self.assertIsNotNone(chat1.id)
        self.assertIsNotNone(chat2.id)
        self.assertNotEqual(chat1.id, chat2.id)

    def test_chat_queryset_filtering_by_user(self):
        """Test filtering chats by specific user."""
        Chat.objects.create(user=self.user, title="User 1 - Chat 1")
        Chat.objects.create(user=self.user, title="User 1 - Chat 2")
        Chat.objects.create(user=self.other_user, title="User 2 - Chat 1")

        user_chats = Chat.objects.filter(user=self.user)
        self.assertEqual(user_chats.count(), 2)

        other_user_chats = Chat.objects.filter(user=self.other_user)
        self.assertEqual(other_user_chats.count(), 1)

    def test_chat_queryset_count_total(self):
        """Test counting all chats."""
        for i in range(5):
            Chat.objects.create(user=self.user, title=f"Chat {i}")

        self.assertEqual(Chat.objects.count(), 5)

    def test_chat_bulk_create(self):
        """Test creating multiple chats in bulk."""
        chats = [Chat(user=self.user, title=f"Bulk Chat {i}") for i in range(3)]
        Chat.objects.bulk_create(chats)

        self.assertEqual(Chat.objects.filter(user=self.user).count(), 3)

    def test_chat_get_by_id(self):
        """Test retrieving chat by ID."""
        chat = Chat.objects.create(user=self.user, title="Get by ID Chat")

        retrieved = Chat.objects.get(id=chat.id)
        self.assertEqual(retrieved.title, "Get by ID Chat")

    def test_chat_update_via_save(self):
        """Test updating chat via save method."""
        chat = Chat.objects.create(user=self.user, title="Original")

        chat.title = "Modified"
        chat.save()

        retrieved = Chat.objects.get(id=chat.id)
        self.assertEqual(retrieved.title, "Modified")

    def test_chat_delete(self):
        """Test deleting a specific chat."""
        chat = Chat.objects.create(user=self.user, title="Chat to Delete")
        chat_id = chat.id

        chat.delete()

        self.assertFalse(Chat.objects.filter(id=chat_id).exists())

    def test_chat_queryset_exists(self):
        """Test checking if chats exist."""
        Chat.objects.create(user=self.user, title="Exists Test")

        user_has_chats = Chat.objects.filter(user=self.user).exists()
        self.assertTrue(user_has_chats)

        other_has_chats = Chat.objects.filter(user=self.other_user).exists()
        self.assertFalse(other_has_chats)
