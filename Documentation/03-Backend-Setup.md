# Backend Setup

## Overview

The backend is built with Flask, a lightweight Python web framework. It provides REST API endpoints for interacting with Ollama models and serves the static frontend files. The server handles request validation, error handling, and integrates with the Ollama library for LLM interactions.

## Flask Application Structure

### Application Initialization

The Flask app is created at module level:

```7:7:server.py
app = Flask(__name__)
```

This creates a Flask application instance that handles routing and request processing.

### Static File Serving

Flask automatically serves files from the `static/` directory. The index route explicitly serves `index.html`:

```32:35:server.py
@app.route('/')
def index():
    """Serve the main HTML page (to be created later)"""
    return send_from_directory('static', 'index.html')
```

**Static Files:**
- `static/index.html` - Main HTML structure
- `static/app.js` - Frontend JavaScript logic
- `static/style.css` - Styling

## API Endpoints

### POST /api/v1/response

Handles chat requests and returns model responses.

**Endpoint Definition:**

```38:99:server.py
@app.route('/api/v1/response', methods=['POST'])
@require_api_key
def get_response():
    """
    Query Ollama with a user prompt and return the response.
    Expected JSON body:
    {
        "prompt": "user prompt text",
        "model": "model name",
        "context": [] (optional list of previous messages)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        prompt = data.get('prompt')
        model = data.get('model')
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
        
        # Add current user prompt
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        # Query Ollama with full conversation context
        response = ollama.chat(
            model=model,
            messages=messages
        )
        
        return jsonify({
            "response": response['message']['content'],
            "model": model
        }), 200
        
    except BadRequest:
        return jsonify({"error": "Invalid JSON data provided"}), 400
    except ollama.ResponseError as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
```

**Request Validation:**
- Checks for JSON data presence
- Validates required fields (`prompt`, `model`)
- Handles optional `context` array
- Validates context structure

**Response Format:**
```json
{
    "response": "Model response text",
    "model": "model-name"
}
```

**Error Responses:**
- `400`: Missing or invalid JSON, missing required fields
- `401`: Invalid or missing API key (if authentication enabled)
- `500`: Ollama errors or server exceptions

### GET /api/v1/models

Retrieves list of available models from Ollama.

**Endpoint Definition:**

```102:123:server.py
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
        
    except ollama.ResponseError as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
```

**Response Format:**
```json
{
    "models": ["llama2", "granite3.3:2b"],
    "count": 2
}
```

**Error Responses:**
- `401`: Invalid or missing API key (if authentication enabled)
- `500`: Ollama connection errors or server exceptions

### GET /api/v1/auth-required

Public detection endpoint indicating whether the server is currently enforcing API key authentication. Always returns `200` and never requires an API key itself.

**Endpoint Definition:**

```python
@app.route('/api/v1/auth-required', methods=['GET'])
def auth_required():
    """Return whether API key authentication is enforced by the server.

    Response JSON:
    { "auth_required": true/false }
    """
    return jsonify({"auth_required": bool(API_KEY)})
```

**Response Format:**
```json
{ "auth_required": true }
```

**Behavior:**
- If `API_KEY` environment variable is unset: returns `{ "auth_required": false }` and the frontend skips login.
- If `API_KEY` is set: returns `{ "auth_required": true }` and the frontend validates or requests a key.
- If the request fails client-side (network error), the frontend assumes auth is required (conservative fallback) and shows the login form.

**Usage in Frontend Startup:**
1. Call `/api/v1/auth-required`.
2. Branch UI: login flow vs direct interface.
3. Protected endpoints (`/api/v1/models`, `/api/v1/response`) include `X-API-Key` when required.

See: [Chat Interface](02-Chat-Interface.md) and [API Key System](04-API-Key-System.md).

## Request/Response Handling

### JSON Processing

Flask automatically parses JSON request bodies:

```51:51:server.py
        data = request.get_json()
```

If JSON parsing fails, Flask raises `BadRequest` exception, which is caught:

```94:95:server.py
    except BadRequest:
        return jsonify({"error": "Invalid JSON data provided"}), 400
```

### Response Formatting

All API responses use Flask's `jsonify()` helper:

```89:92:server.py
        return jsonify({
            "response": response['message']['content'],
            "model": model
        }), 200
```

This ensures proper JSON encoding and sets appropriate headers.

## Error Handling Patterns

### Exception Hierarchy

The application handles errors in order of specificity:

1. **BadRequest** - Invalid JSON format
2. **ollama.ResponseError** - Ollama-specific errors (model not found, connection issues)
3. **Exception** - Catch-all for unexpected errors

```94:99:server.py
    except BadRequest:
        return jsonify({"error": "Invalid JSON data provided"}), 400
    except ollama.ResponseError as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
```

### Error Response Format

All errors return consistent JSON structure:

```json
{
    "error": "Error message description"
}
```

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication failures)
- `500`: Internal Server Error (Ollama or server errors)

## Environment Configuration

### Server Configuration

The server uses environment variables for configuration:

```126:134:server.py
def run_server():
    """Run the Flask development server"""
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Flask server on http://localhost:{port}")
    print(f"Ollama host: {OLLAMA_HOST}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
```

**Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Server port number |
| `DEBUG` | `True` | Enable Flask debug mode (auto-reload, detailed errors) |
| `API_KEY` | `None` | Optional API key for authentication |

### Running the Server

**Default:**
```bash
python server.py
```

**Custom Port:**
```bash
PORT=8080 python server.py
```

**Production Mode (No Debug):**
```bash
DEBUG=False PORT=8080 python server.py
```

**With API Key:**
```bash
API_KEY=your-secret-key python server.py
```

### Host Configuration

The server binds to `0.0.0.0`, making it accessible from all network interfaces:

```134:134:server.py
    app.run(host='0.0.0.0', port=port, debug=debug)
```

**Security Note:** In production, consider:
- Using a reverse proxy (nginx, Apache)
- Implementing HTTPS
- Restricting network access
- Using proper authentication

## API Key Authentication

All API endpoints (except `/`) are protected by the `@require_api_key` decorator:

```16:29:server.py
def require_api_key(f):
    """Decorator to require API key authentication for endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not API_KEY:
            # If no API key is configured, allow access (backward compatibility)
            return f(*args, **kwargs)
        
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        
        return f(*args, **kwargs)
    return decorated_function
```

See [API Key System](04-API-Key-System.md) for detailed authentication documentation.

## Server Startup

The server can be run directly or imported:

```137:138:server.py
if __name__ == "__main__":
    run_server()
```

**Direct Execution:**
```bash
python server.py
```

**Import in Another Script:**
```python
from server import app
# Use app with WSGI server (gunicorn, uwsgi, etc.)
```

## Dependencies

Required packages (from `requirements.txt` or `pyproject.toml`):

- `flask>=3.1.2` - Web framework
- `ollama>=0.6.0` - Ollama Python client

## Production Considerations

### WSGI Server

For production, use a production WSGI server:

```bash
# Using gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app

# Using uwsgi
pip install uwsgi
uwsgi --http 0.0.0.0:5000 --module server:app --processes 4
```

### Reverse Proxy

Use nginx or Apache as reverse proxy for:
- SSL/TLS termination
- Static file serving
- Load balancing
- Rate limiting

### Security Checklist

- [ ] Set strong `API_KEY` environment variable
- [ ] Use HTTPS (via reverse proxy or Flask-TLS)
- [ ] Restrict network access (firewall rules)
- [ ] Keep dependencies updated
- [ ] Disable Flask debug mode in production
- [ ] Use environment variables for secrets (never hardcode)

## Related Documentation

- [LLM Serving](01-LLM-Serving.md) - Ollama integration details
- [API Key System](04-API-Key-System.md) - Authentication implementation
- [Error Handling](09-Error-Handling.md) - Error management patterns

