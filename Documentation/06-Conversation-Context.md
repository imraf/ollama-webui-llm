# Conversation Context

## Overview

The application maintains conversation context by sending the last 3 messages from the conversation history to Ollama with each new request. This allows the model to understand the conversation flow and provide coherent, contextually relevant responses across multiple turns.

## How Context Works

### Context Window

The application maintains a **sliding window** of the last 3 messages:

```251:261:static/app.js
        // Get last 3 messages for context (excluding the current prompt we just added)
        const contextMessages = currentChat.messages.slice(-4, -1); // Last 3 before current
        
        const response = await fetch('/api/v1/response', {
            method: 'POST',
            headers: getApiHeaders(),
            body: JSON.stringify({
                prompt: prompt,
                model: selectedModel,
                context: contextMessages
            })
        });
```

**Implementation Details:**
- `currentChat.messages.slice(-4, -1)` gets the last 3 messages before the current one
- The current user prompt is already added to `currentChat.messages` before context extraction
- This ensures the model sees the conversation flow leading up to the current question

### Backend Context Processing

The backend receives the context array and formats it for Ollama:

```66:81:server.py
        # Build messages array with context
        messages = []
        
        # Add context messages (last 3 messages from conversation history)
        if context_messages and isinstance(context_messages, list):
            for msg in context_messages:
                messages.append({
                    'role': msg.get('role', 'user'),
                    'content': msg.get('content', '')
                })
        
        # Add current user prompt
        messages.append({
            'role': 'user',
            'content': prompt
        })
```

**Process:**
1. Creates empty messages array
2. Iterates through context messages (if provided and is a list)
3. Adds each context message with role and content
4. Adds current user prompt as final message
5. Sends complete message array to Ollama

### Message Format

Each message in the context array follows this structure:

```json
{
    "role": "user" | "assistant",
    "content": "Message text content"
}
```

**Roles:**
- `"user"`: User prompts and questions
- `"assistant"`: Model responses

**Default Values:**
- If `role` is missing, defaults to `'user'`
- If `content` is missing, defaults to `''` (empty string)

## Example Conversation Flow

### First Message

**User sends:** "What is Python?"

**Context sent:** `[]` (empty, no previous messages)

**Messages to Ollama:**
```json
[
    {
        "role": "user",
        "content": "What is Python?"
    }
]
```

### Second Message

**User sends:** "How do I install it?"

**Context sent:** Previous message and response

**Messages to Ollama:**
```json
[
    {
        "role": "user",
        "content": "What is Python?"
    },
    {
        "role": "assistant",
        "content": "Python is a high-level programming language..."
    },
    {
        "role": "user",
        "content": "How do I install it?"
    }
]
```

### Third Message (Context Window Full)

**User sends:** "Which version should I use?"

**Context sent:** Last 2 messages (keeping window at 3 total)

**Messages to Ollama:**
```json
[
    {
        "role": "assistant",
        "content": "Python is a high-level programming language..."
    },
    {
        "role": "user",
        "content": "How do I install it?"
    },
    {
        "role": "assistant",
        "content": "You can install Python by downloading it from python.org..."
    },
    {
        "role": "user",
        "content": "Which version should I use?"
    }
]
```

**Note:** The first user message ("What is Python?") is now outside the context window and not sent.

## Context Limitations

### Fixed Window Size

The application uses a **fixed window of 3 messages**. This means:
- Conversations longer than 3 messages lose earlier context
- The model only sees recent conversation history
- Very long conversations may lose important context from earlier turns

### Why 3 Messages?

- **Balance**: Provides enough context for coherent conversations without overwhelming the model
- **Token Efficiency**: Keeps request sizes manageable
- **Performance**: Smaller context means faster responses

### Limitations in Practice

1. **Context Loss**: After 3+ messages, earlier context is forgotten
2. **No Conversation Memory**: Context is session-based, not persistent across page reloads
3. **No System Prompts**: No way to set persistent conversation instructions

## Context Validation

### Frontend Validation

The frontend always sends context as an array:

```251:261:static/app.js
        // Get last 3 messages for context (excluding the current prompt we just added)
        const contextMessages = currentChat.messages.slice(-4, -1); // Last 3 before current
        
        const response = await fetch('/api/v1/response', {
            method: 'POST',
            headers: getApiHeaders(),
            body: JSON.stringify({
                prompt: prompt,
                model: selectedModel,
                context: contextMessages
            })
        });
```

### Backend Validation

The backend validates context structure:

```58:75:server.py
        context_messages = data.get('context', [])
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' field"}), 400
        
        if not model:
            return jsonify({"error": "Missing 'model' field"}), 400
        
        # Build messages array with context
        messages = []
        
        # Add context messages (last 3 messages from conversation history)
        if context_messages and isinstance(context_messages, list):
            for msg in context_messages:
                messages.append({
                    'role': msg.get('role', 'user'),
                    'content': msg.get('content', '')
                })
```

**Validation:**
- Checks if context exists and is a list
- Handles missing or invalid context gracefully
- Defaults missing fields appropriately

## Edge Cases

### Empty Context

If no context is provided or context is empty:

```233:257:tests/test_server.py
    def test_context_with_empty_list(self, client, mock_ollama_chat, api_headers):
        """Test context with empty list."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Response'
            }
        }
        
        data = {
            'prompt': 'Test',
            'model': 'llama2',
            'context': []
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json',
            headers=api_headers
        )
        
        assert response.status_code == 200
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert len(messages) == 1
```

**Result:** Only the current prompt is sent (single message array).

### Invalid Context Type

If context is not a list:

```206:231:tests/test_server.py
    def test_invalid_context_not_list(self, client, mock_ollama_chat, api_headers):
        """Test context that is not a list."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Response'
            }
        }
        
        data = {
            'prompt': 'Test',
            'model': 'llama2',
            'context': 'not a list'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json',
            headers=api_headers
        )
        
        # Should still succeed, but context is ignored
        assert response.status_code == 200
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert len(messages) == 1
```

**Result:** Context is ignored, only current prompt sent.

### Missing Context Fields

If context messages have missing fields:

```94:126:tests/test_server.py
    def test_context_with_missing_fields(self, client, mock_ollama_chat, api_headers):
        """Test context messages with missing role or content fields."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Response'
            }
        }
        
        data = {
            'prompt': 'Test',
            'model': 'llama2',
            'context': [
                {'role': 'user'},  # Missing content
                {'content': 'Hello'}  # Missing role
            ]
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json',
            headers=api_headers
        )
        
        assert response.status_code == 200
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert len(messages) == 3
        assert messages[0]['role'] == 'user'
        assert messages[0]['content'] == ''
        assert messages[1]['role'] == 'user'  # Default role
        assert messages[1]['content'] == 'Hello'
```

**Result:** Missing fields use defaults (`role='user'`, `content=''`).

## Context vs. Full History

### Current Implementation

The application uses a **sliding window** approach:
- Only last 3 messages sent with each request
- Earlier messages are not included
- Context is recalculated for each request

### Alternative Approaches

**Full History:**
- Send all messages from conversation start
- Pros: Complete context, no information loss
- Cons: Larger requests, slower responses, token limits

**Summarization:**
- Summarize earlier messages into a system prompt
- Pros: Maintains context without large requests
- Cons: Information loss, requires summarization logic

**Fixed Window (Current):**
- Send last N messages
- Pros: Simple, predictable, efficient
- Cons: Context loss beyond window

## Storage vs. Context

### Chat Storage

Full conversation history is stored in localStorage (see [Chat History](07-Chat-History.md)):
- All messages preserved in browser storage
- Accessible when loading previous chats
- Not sent to Ollama (only context window is)

### Context Window

Only the context window is sent to Ollama:
- Last 3 messages from current session
- Calculated dynamically per request
- Not persisted separately

## Performance Considerations

### Request Size

- **Small Context**: Fewer tokens = faster requests
- **Large Context**: More tokens = slower requests, higher costs (if using paid APIs)

### Model Limits

Different models have different context window limits:
- Smaller models: 2K-4K tokens
- Larger models: 8K-32K+ tokens

The 3-message window keeps requests well within most model limits.

## Related Documentation

- [LLM Serving](01-LLM-Serving.md) - How messages are sent to Ollama
- [Chat History](07-Chat-History.md) - Full conversation storage
- [Backend Setup](03-Backend-Setup.md) - API endpoint implementation

