# LLM Serving

## Overview

The application integrates with [Ollama](https://ollama.ai/) to serve Large Language Models (LLMs) locally. Ollama handles the model inference, while this application provides a web interface to interact with these models. The integration is handled entirely on the backend through the `ollama` Python library.

## Implementation

### Ollama Library Integration

The application uses the official `ollama` Python library to communicate with a local Ollama instance:

```4:4:server.py
import ollama
```

The Ollama host is configured as a constant, defaulting to `http://localhost:11434`:

```10:10:server.py
OLLAMA_HOST = "http://localhost:11434"
```

**Note:** While `OLLAMA_HOST` is defined, the `ollama` library uses this host automatically by default. If you need to connect to a remote Ollama instance, you would configure the library's host settings accordingly.

### Model Querying

#### Listing Available Models

The application queries Ollama to retrieve a list of locally available models using the `ollama.list()` function:

```102:118:server.py
@app.route('/api/v1/models', methods=['GET'])
@require_api_key
def get_models():
    """
    Get list of available models from Ollama.
    """
    try:
        # Get list of models from Ollama
        models_response = ollama.list()
        
        # Extract model names
        models = [model.model for model in models_response.get('models', [])]
        
        return jsonify({
            "models": models,
            "count": len(models)
        }), 200
```

The response from `ollama.list()` contains a dictionary with a `models` key, where each model object has a `model` attribute containing the model name. The endpoint extracts these names and returns them as a JSON array.

#### Querying Models for Responses

To get responses from a model, the application uses `ollama.chat()`:

```84:87:server.py
        response = ollama.chat(
            model=model,
            messages=messages
        )
```

The `ollama.chat()` function accepts:
- `model`: The name of the model to use (e.g., "llama2", "granite3.3:2b")
- `messages`: An array of message objects, each with `role` and `content` fields

### Message Format

Messages are formatted as an array of dictionaries with `role` and `content` fields:

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

The `role` field can be:
- `'user'`: User prompts and questions
- `'assistant'`: Model responses (used in conversation context)

### Response Processing

After calling `ollama.chat()`, the response is a dictionary containing:

```89:92:server.py
        return jsonify({
            "response": response['message']['content'],
            "model": model
        }), 200
```

- `response['message']['content']`: The actual text response from the model
- The response is wrapped in a JSON object with the model name for client reference

### Error Handling

The application handles several error scenarios:

#### Ollama Response Errors

When Ollama returns an error (e.g., model not found, server unavailable):

```96:97:server.py
    except ollama.ResponseError as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500
```

This catches specific Ollama errors and returns a 500 status with an error message.

#### General Exceptions

For unexpected errors:

```98:99:server.py
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
```

This provides a fallback for any other exceptions that might occur.

## Configuration

### Environment Setup

Before using the application, ensure:

1. **Ollama is installed**: Download from [ollama.ai/download](https://ollama.ai/download)
2. **Ollama is running**: Start with `ollama serve` or use the desktop app
3. **Models are pulled**: Install models with `ollama pull <model-name>`

Example:
```bash
ollama pull llama2
ollama pull granite3.3:2b
```

### Default Configuration

- **Host**: `http://localhost:11434` (hardcoded constant)
- **Port**: Ollama default port is 11434
- **Connection**: Direct HTTP connection to local Ollama instance

## How It Works

1. **Client Request**: User sends a prompt through the web interface
2. **Backend Processing**: Flask endpoint receives the request with prompt, model name, and optional context
3. **Message Formatting**: Backend formats messages according to Ollama's API structure
4. **Ollama Query**: Backend calls `ollama.chat()` with formatted messages
5. **Response Extraction**: Backend extracts the content from Ollama's response
6. **Client Response**: Backend returns the model's response to the client

## Example Request Flow

```python
# Client sends:
{
    "prompt": "Explain quantum computing",
    "model": "llama2",
    "context": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help?"}
    ]
}

# Backend formats for Ollama:
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "Explain quantum computing"}
]

# Ollama processes and returns:
{
    "message": {
        "content": "Quantum computing is a type of computation..."
    }
}

# Backend returns to client:
{
    "response": "Quantum computing is a type of computation...",
    "model": "llama2"
}
```

## Related Documentation

- [Backend Setup](03-Backend-Setup.md) - Flask server architecture
- [Conversation Context](06-Conversation-Context.md) - How context is managed
- [Model Selection](08-Model-Selection.md) - How models are loaded and selected

