# Chat API Documentation

REST API endpoints for programmatic access to chat functionality. Designed for CLI, VSCode plugin, and mobile client integration.

## Authentication

All API endpoints require token-based authentication using Django REST Framework's TokenAuthentication.

**Header Format:**

```
Authorization: Token <your_auth_token>
```

**Getting Your Token:**

Contact the admin or use Django's shell to retrieve/create your token:

```python
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

user = User.objects.get(username='your_username')
token = Token.objects.get_or_create(user=user)[0]
print(token.key)
```

**Error Response (Unauthenticated):**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Error Response (Invalid Token):**

```json
{
  "detail": "Invalid token."
}
```

## Base URL

```
http://localhost:8000/api/
```

## Endpoints

### Chat Endpoints

#### List User's Chats

```
GET /api/chats/
```

Returns paginated list of authenticated user's chats, ordered by most recently updated first.

**Authentication:** Required (Token)
**Permissions:** IsAuthenticated, IsOwner
**Pagination:** 20 items per page

**Response (200 OK):**

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/chats/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 5,
      "title": "Python Questions",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-20T14:22:15Z",
      "message_count": 12
    },
    {
      "id": 2,
      "user": 5,
      "title": "Django Best Practices",
      "created_at": "2024-01-14T09:15:00Z",
      "updated_at": "2024-01-19T16:45:30Z",
      "message_count": 8
    }
  ]
}
```

**Query Parameters:**

- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

---

#### Create New Chat

```
POST /api/chats/
```

Creates a new chat owned by the authenticated user.

**Authentication:** Required (Token)
**Permissions:** IsAuthenticated

**Request Body:**

```json
{
  "title": "New Chat Title"
}
```

**Validation:**

- `title` (required): Non-empty string, max 200 characters

**Response (201 Created):**

```json
{
  "id": 42,
  "user": 5,
  "title": "New Chat Title",
  "created_at": "2024-01-20T15:30:00Z",
  "updated_at": "2024-01-20T15:30:00Z",
  "message_count": 0
}
```

**Error Response (400 Bad Request):**

```json
{
  "title": ["This field is required."]
}
```

---

#### Retrieve Chat Detail

```
GET /api/chats/{id}/
```

Returns details of a single chat. Only chat owner can access.

**Authentication:** Required (Token)
**Permissions:** IsAuthenticated, IsOwner

**Response (200 OK):**

```json
{
  "id": 1,
  "user": 5,
  "title": "Python Questions",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:22:15Z",
  "message_count": 12
}
```

**Error Response (404 Not Found):**

```json
{
  "detail": "Not found."
}
```

---

#### Delete Chat

```
DELETE /api/chats/{id}/
```

Deletes a chat and all its messages. Only chat owner can delete.

**Authentication:** Required (Token)
**Permissions:** IsAuthenticated, IsOwner

**Response (204 No Content):**

```
(empty body)
```

**Error Response (404 Not Found):**

```json
{
  "detail": "Not found."
}
```

---

### Message Endpoints

#### List Chat Messages

```
GET /api/chats/{chat_id}/messages/
```

Returns paginated list of messages in a chat, ordered by creation time (oldest first).

**Authentication:** Required (Token)
**Permissions:** IsAuthenticated, IsOwner (of parent chat)
**Pagination:** 20 items per page

**Response (200 OK):**

```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "chat": 1,
      "user": 5,
      "content": "What's the best way to handle errors in Python?",
      "role": "user",
      "tokens": 15,
      "created_at": "2024-01-15T10:31:00Z"
    },
    {
      "id": 2,
      "chat": 1,
      "user": 5,
      "content": "Python has several error handling mechanisms...",
      "role": "assistant",
      "tokens": 125,
      "created_at": "2024-01-15T10:31:30Z"
    }
  ]
}
```

**Query Parameters:**

- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

**Error Response (403 Forbidden):**

```json
{
  "detail": "Access denied."
}
```

---

#### Create Message in Chat

```
POST /api/chats/{chat_id}/messages/
```

Adds a new message to a chat. User is auto-set from authenticated request.

**Authentication:** Required (Token)
**Permissions:** IsAuthenticated, IsOwner (of parent chat)

**Request Body:**

```json
{
  "chat": 1,
  "content": "This is my question or statement.",
  "role": "user"
}
```

**Validation:**

- `content` (required): Non-empty string
- `role` (required): One of `user`, `assistant`, `system`
- `chat`: Must be valid chat ID owned by authenticated user

**Role Values:**

- `user`: Message from the user
- `assistant`: Message from the AI assistant
- `system`: System message (context, instructions, etc.)

**Response (201 Created):**

```json
{
  "id": 42,
  "chat": 1,
  "user": 5,
  "content": "This is my question or statement.",
  "role": "user",
  "tokens": 8,
  "created_at": "2024-01-20T15:45:00Z"
}
```

**Error Response (400 Bad Request):**

```json
{
  "content": ["Message content cannot be empty."],
  "role": ["Invalid role. Must be one of: user, assistant, system"]
}
```

**Error Response (403 Forbidden):**

```json
{
  "detail": "Access denied."
}
```

---

#### Retrieve Single Message

```
GET /api/chats/{chat_id}/messages/{message_id}/
```

Returns details of a single message.

**Authentication:** Required (Token)
**Permissions:** IsAuthenticated, IsOwner (of parent chat)

**Response (200 OK):**

```json
{
  "id": 1,
  "chat": 1,
  "user": 5,
  "content": "What's the best way to handle errors in Python?",
  "role": "user",
  "tokens": 15,
  "created_at": "2024-01-15T10:31:00Z"
}
```

---

#### Delete Message

```
DELETE /api/chats/{chat_id}/messages/{message_id}/
```

Deletes a message from a chat.

**Authentication:** Required (Token)
**Permissions:** IsAuthenticated, IsOwner (of parent chat)

**Response (204 No Content):**

```
(empty body)
```

---

## HTTP Status Codes

| Code | Meaning                                                  |
| ---- | -------------------------------------------------------- |
| 200  | OK - Successful retrieval                                |
| 201  | Created - Successful creation                            |
| 204  | No Content - Successful deletion/update                  |
| 400  | Bad Request - Validation error                           |
| 401  | Unauthorized - Missing or invalid token                  |
| 403  | Forbidden - Insufficient permissions (not chat owner)    |
| 404  | Not Found - Resource doesn't exist or user has no access |

## Error Handling

All error responses include a JSON body with error details:

**Validation Error (400):**

```json
{
  "field_name": ["Error message explaining what's wrong"]
}
```

**Authorization Error (401):**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Permission Error (403):**

```json
{
  "detail": "Access denied."
}
```

**Not Found (404):**

```json
{
  "detail": "Not found."
}
```

## Example Requests

### Using curl

**List chats:**

```bash
curl -H "Authorization: Token abc123def456" \
  http://localhost:8000/api/chats/
```

**Create chat:**

```bash
curl -X POST \
  -H "Authorization: Token abc123def456" \
  -H "Content-Type: application/json" \
  -d '{"title":"My New Chat"}' \
  http://localhost:8000/api/chats/
```

**Create message:**

```bash
curl -X POST \
  -H "Authorization: Token abc123def456" \
  -H "Content-Type: application/json" \
  -d '{"chat":1,"content":"Hello!","role":"user"}' \
  http://localhost:8000/api/chats/1/messages/
```

### Using Python

```python
import requests

TOKEN = "abc123def456"
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# List chats
response = requests.get(f"{BASE_URL}/chats/", headers=HEADERS)
chats = response.json()['results']

# Create chat
chat_data = {"title": "My New Chat"}
response = requests.post(f"{BASE_URL}/chats/", json=chat_data, headers=HEADERS)
chat = response.json()

# Create message
message_data = {
    "chat": chat['id'],
    "content": "Hello!",
    "role": "user"
}
response = requests.post(
    f"{BASE_URL}/chats/{chat['id']}/messages/",
    json=message_data,
    headers=HEADERS
)
message = response.json()
```

## Pagination

List endpoints return paginated results with the following structure:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/chats/?page=2",
  "previous": null,
  "results": [...]
}
```

**Parameters:**

- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Example:**

```
GET /api/chats/?page=2&page_size=50
```

## Rate Limiting

Currently not implemented. Will be added in Phase 9 (Polish & Optimization).

## Versioning

Currently at v1 (implicit). Version may be added to URL path in future:

```
GET /api/v1/chats/
```

## Future Enhancements

- [ ] API versioning
- [ ] Rate limiting
- [ ] Response compression
- [ ] Query filtering (by date, title, etc.)
- [ ] Search endpoints
- [ ] Batch operations
- [ ] WebSocket support for real-time updates
- [ ] GraphQL alternative interface
