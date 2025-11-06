from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.chats.models import Chat, Message


class MessageModelTests(TestCase):
    """Test suite for Message model."""

    @classmethod
    def setUpTestData(cls):
        """Create reusable test data for all test methods."""
        cls.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        cls.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )
        cls.chat = Chat.objects.create(user=cls.user, title="Test Chat")

    def test_message_creation_with_required_fields(self):
        """Test creating a message with required fields."""
        message = Message.objects.create(
            chat=self.chat, user=self.user, content="Hello, world!", role="user"
        )

        self.assertEqual(message.chat, self.chat)
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.content, "Hello, world!")
        self.assertEqual(message.role, "user")
        self.assertEqual(message.tokens, 0)
        self.assertIsNotNone(message.created_at)

    def test_message_role_user(self):
        """Test creating a message with user role."""
        message = Message.objects.create(
            chat=self.chat, user=self.user, content="User message", role="user"
        )

        self.assertEqual(message.role, "user")

    def test_message_role_assistant(self):
        """Test creating a message with assistant role."""
        message = Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="Assistant message",
            role="assistant",
        )

        self.assertEqual(message.role, "assistant")

    def test_message_role_system(self):
        """Test creating a message with system role."""
        message = Message.objects.create(
            chat=self.chat, user=self.user, content="System message", role="system"
        )

        self.assertEqual(message.role, "system")

    def test_message_with_tokens(self):
        """Test creating a message with token count."""
        message = Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="Message with tokens",
            role="user",
            tokens=42,
        )

        self.assertEqual(message.tokens, 42)

    def test_message_tokens_default_zero(self):
        """Test that tokens default to 0."""
        message = Message.objects.create(
            chat=self.chat, user=self.user, content="No tokens specified", role="user"
        )

        self.assertEqual(message.tokens, 0)

    def test_message_timestamps_auto_set(self):
        """Test that created_at is automatically set."""
        before = timezone.now()
        message = Message.objects.create(
            chat=self.chat, user=self.user, content="Timestamp test", role="user"
        )
        after = timezone.now()

        self.assertGreaterEqual(message.created_at, before)
        self.assertLessEqual(message.created_at, after)

    def test_message_content_can_be_long(self):
        """Test that message can store long text content."""
        long_content = "a" * 10000
        message = Message.objects.create(
            chat=self.chat, user=self.user, content=long_content, role="user"
        )

        self.assertEqual(len(message.content), 10000)
        retrieved = Message.objects.get(id=message.id)
        self.assertEqual(retrieved.content, long_content)

    def test_message_chat_relationship(self):
        """Test that message is properly associated with chat."""
        message = Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="Chat relationship test",
            role="user",
        )

        self.assertEqual(message.chat.title, "Test Chat")
        self.assertIn(message, self.chat.messages.all())

    def test_message_user_relationship(self):
        """Test that message is properly associated with user."""
        message = Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="User relationship test",
            role="user",
        )

        self.assertEqual(message.user.username, "testuser")
        self.assertIn(message, self.user.messages.all())

    def test_multiple_messages_in_single_chat(self):
        """Test that a chat can contain multiple messages."""
        msg1 = Message.objects.create(
            chat=self.chat, user=self.user, content="Message 1", role="user"
        )
        msg2 = Message.objects.create(
            chat=self.chat, user=self.user, content="Message 2", role="assistant"
        )
        msg3 = Message.objects.create(
            chat=self.chat, user=self.user, content="Message 3", role="user"
        )

        chat_messages = self.chat.messages.all()
        self.assertEqual(chat_messages.count(), 3)
        self.assertIn(msg1, chat_messages)
        self.assertIn(msg2, chat_messages)
        self.assertIn(msg3, chat_messages)

    def test_message_default_ordering_by_created_at(self):
        """Test that messages are ordered by created_at ascending."""
        import time

        msg1 = Message.objects.create(
            chat=self.chat, user=self.user, content="First", role="user"
        )
        time.sleep(0.01)
        msg2 = Message.objects.create(
            chat=self.chat, user=self.user, content="Second", role="assistant"
        )

        messages = Message.objects.filter(chat=self.chat)
        self.assertEqual(messages[0].id, msg1.id)
        self.assertEqual(messages[1].id, msg2.id)

    def test_message_cascade_delete_with_chat(self):
        """Test that deleting chat also deletes messages."""
        message = Message.objects.create(
            chat=self.chat, user=self.user, content="Message to be deleted", role="user"
        )
        message_id = message.id
        chat_id = self.chat.id

        self.assertTrue(Message.objects.filter(id=message_id).exists())

        self.chat.delete()

        self.assertFalse(Message.objects.filter(id=message_id).exists())
        self.assertFalse(Chat.objects.filter(id=chat_id).exists())

    def test_message_user_can_be_different_from_chat_owner(self):
        """Test that message author can be different from chat owner."""
        message = Message.objects.create(
            chat=self.chat,
            user=self.other_user,
            content="Message from another user",
            role="user",
        )

        self.assertEqual(message.chat.user, self.user)
        self.assertEqual(message.user, self.other_user)

    def test_message_str_representation(self):
        """Test message string representation includes role and timestamp."""
        message = Message.objects.create(
            chat=self.chat, user=self.user, content="Test message", role="user"
        )

        str_repr = str(message)
        self.assertIn("User", str_repr)
        self.assertIn("2025", str_repr)

    def test_message_id_is_auto_incremented(self):
        """Test that message IDs are automatically assigned and unique."""
        msg1 = Message.objects.create(
            chat=self.chat, user=self.user, content="Message 1", role="user"
        )
        msg2 = Message.objects.create(
            chat=self.chat, user=self.user, content="Message 2", role="user"
        )

        self.assertIsNotNone(msg1.id)
        self.assertIsNotNone(msg2.id)
        self.assertNotEqual(msg1.id, msg2.id)

    def test_message_empty_content_allowed(self):
        """Test that empty content is technically allowed at model level."""
        message = Message.objects.create(
            chat=self.chat, user=self.user, content="", role="user"
        )

        self.assertEqual(message.content, "")

    def test_message_with_special_characters(self):
        """Test that message can store special characters and unicode."""
        special_content = "Hello! 👋 Привет! 你好! \n\t Special chars: @#$%^&*()"
        message = Message.objects.create(
            chat=self.chat, user=self.user, content=special_content, role="user"
        )

        retrieved = Message.objects.get(id=message.id)
        self.assertEqual(retrieved.content, special_content)

    def test_message_queryset_filter_by_role(self):
        """Test filtering messages by role."""
        Message.objects.create(
            chat=self.chat, user=self.user, content="User message 1", role="user"
        )
        Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="Assistant response",
            role="assistant",
        )
        Message.objects.create(
            chat=self.chat, user=self.user, content="User message 2", role="user"
        )

        user_messages = Message.objects.filter(role="user")
        self.assertEqual(user_messages.count(), 2)

        assistant_messages = Message.objects.filter(role="assistant")
        self.assertEqual(assistant_messages.count(), 1)

    def test_message_queryset_filter_by_chat(self):
        """Test filtering messages by specific chat."""
        other_chat = Chat.objects.create(user=self.user, title="Other Chat")

        Message.objects.create(
            chat=self.chat, user=self.user, content="Chat 1 message", role="user"
        )
        Message.objects.create(
            chat=other_chat, user=self.user, content="Chat 2 message", role="user"
        )

        chat1_messages = Message.objects.filter(chat=self.chat)
        self.assertEqual(chat1_messages.count(), 1)

        chat2_messages = Message.objects.filter(chat=other_chat)
        self.assertEqual(chat2_messages.count(), 1)

    def test_message_queryset_filter_by_user(self):
        """Test filtering messages by specific user."""
        Message.objects.create(
            chat=self.chat, user=self.user, content="User 1 message", role="user"
        )
        Message.objects.create(
            chat=self.chat, user=self.other_user, content="User 2 message", role="user"
        )

        user1_messages = Message.objects.filter(user=self.user)
        self.assertEqual(user1_messages.count(), 1)

        user2_messages = Message.objects.filter(user=self.other_user)
        self.assertEqual(user2_messages.count(), 1)

    def test_message_bulk_create(self):
        """Test creating multiple messages in bulk."""
        messages = [
            Message(
                chat=self.chat,
                user=self.user,
                content=f"Bulk message {i}",
                role="user" if i % 2 == 0 else "assistant",
            )
            for i in range(5)
        ]
        Message.objects.bulk_create(messages)

        self.assertEqual(Message.objects.filter(chat=self.chat).count(), 5)

    def test_message_get_by_id(self):
        """Test retrieving message by ID."""
        message = Message.objects.create(
            chat=self.chat, user=self.user, content="Get by ID test", role="user"
        )

        retrieved = Message.objects.get(id=message.id)
        self.assertEqual(retrieved.content, "Get by ID test")

    def test_message_update_via_save(self):
        """Test updating message via save method."""
        message = Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="Original content",
            role="user",
            tokens=10,
        )

        message.content = "Updated content"
        message.tokens = 20
        message.save()

        retrieved = Message.objects.get(id=message.id)
        self.assertEqual(retrieved.content, "Updated content")
        self.assertEqual(retrieved.tokens, 20)

    def test_message_delete(self):
        """Test deleting a specific message."""
        message = Message.objects.create(
            chat=self.chat, user=self.user, content="Message to delete", role="user"
        )
        message_id = message.id

        message.delete()

        self.assertFalse(Message.objects.filter(id=message_id).exists())

    def test_message_queryset_exists(self):
        """Test checking if messages exist."""
        Message.objects.create(
            chat=self.chat, user=self.user, content="Exists test", role="user"
        )

        has_messages = Message.objects.filter(chat=self.chat).exists()
        self.assertTrue(has_messages)

    def test_message_tokens_with_large_values(self):
        """Test that tokens can store large values."""
        message = Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="Large token count",
            role="user",
            tokens=999999,
        )

        self.assertEqual(message.tokens, 999999)

    def test_message_conversation_flow(self):
        """Test a realistic conversation flow with multiple messages."""
        Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="What is Django?",
            role="user",
            tokens=5,
        )
        Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="Django is a web framework...",
            role="assistant",
            tokens=45,
        )
        Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="Can you explain ORM?",
            role="user",
            tokens=7,
        )
        Message.objects.create(
            chat=self.chat,
            user=self.user,
            content="The ORM allows you to...",
            role="assistant",
            tokens=38,
        )

        messages = self.chat.messages.all()
        self.assertEqual(messages.count(), 4)

        # Verify conversation order
        self.assertEqual(messages[0].content, "What is Django?")
        self.assertEqual(messages[1].role, "assistant")
        self.assertEqual(messages[2].content, "Can you explain ORM?")
        self.assertEqual(messages[3].role, "assistant")

        # Verify token counts
        total_tokens = sum(msg.tokens for msg in messages)
        self.assertEqual(total_tokens, 95)
