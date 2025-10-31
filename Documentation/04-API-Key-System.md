# API Key System

## Overview

The application supports optional API key authentication to protect access to the chat interface and API endpoints. When an API key is configured, users must provide it to access the application. The system is designed to be backward compatible - if no API key is set, the application works without authentication.

## Backend Implementation

### API Key Configuration

The API key is read from environment variables:

```13:13:server.py
API_KEY = os.environ.get('API_KEY')
```

If `API_KEY` is not set, it defaults to `None`, which disables authentication.

### Authentication Decorator

The `@require_api_key` decorator protects API endpoints:

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

**How It Works:**
1. Checks if `API_KEY` is configured
2. If not configured, allows access (backward compatibility)
3. If configured, extracts `X-API-Key` header from request
4. Compares provided key with configured key
5. Returns 401 if key is missing or invalid
6. Allows request to proceed if key matches

### Protected Endpoints

Both API endpoints are protected:

```38:39:server.py
@app.route('/api/v1/response', methods=['POST'])
@require_api_key
```

```102:103:server.py
@app.route('/api/v1/models', methods=['GET'])
@require_api_key
```

The index route (`/`) is **not** protected, allowing users to access the login form:

```32:35:server.py
@app.route('/')
def index():
    """Serve the main HTML page (to be created later)"""
    return send_from_directory('static', 'index.html')
```

## Frontend Implementation

### API Key Storage

The frontend stores the API key in browser localStorage:

```13:14:static/app.js
// API Key storage key
const API_KEY_STORAGE_KEY = 'llm-api-key';
```

**Storage Key:** `'llm-api-key'`

### Initialization Flow

On app initialization, the system checks for a stored API key:

```31:55:static/app.js
// Initialize the app
async function init() {
    // Check for stored API key
    apiKey = localStorage.getItem(API_KEY_STORAGE_KEY);
    
    if (apiKey) {
        // Validate stored API key
        const isValid = await validateApiKey(apiKey);
        if (isValid) {
            showMainInterface();
            loadChatsFromStorage();
            await loadModels();
            setupEventListeners();
            renderPreviousChats();
        } else {
            // Invalid key, clear it and show login
            clearApiKey();
            showLoginForm();
        }
    } else {
        // No API key, show login form
        showLoginForm();
    }
    
    setupLoginListeners();
}
```

**Flow:**
1. Check localStorage for stored API key
2. If found, validate it with backend
3. If valid, show main interface
4. If invalid or missing, show login form

### Login Form

The login form is displayed when no valid API key is available:

```63:67:static/app.js
// Show login form
function showLoginForm() {
    loginContainer.style.display = 'flex';
    mainContainer.style.display = 'none';
    apiKeyInput.focus();
}
```

**HTML Structure:**

```12:28:static/index.html
    <div id="login-container" class="login-container" style="display: none;">
        <div class="login-form">
            <h1>API Key Required</h1>
            <p class="login-description">Please enter your API key to access the chat interface.</p>
            <form id="login-form">
                <input 
                    type="password" 
                    id="api-key-input" 
                    placeholder="Enter API key" 
                    required
                    autocomplete="off"
                />
                <div id="login-error" class="login-error" style="display: none;"></div>
                <button type="submit" id="login-submit-btn" class="login-submit-btn">Connect</button>
            </form>
        </div>
    </div>
```

**Features:**
- Password input type (masks key while typing)
- Form validation (required field)
- Error message display
- Submit button with loading state

### Login Handler

When the login form is submitted:

```76:104:static/app.js
// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const key = apiKeyInput.value.trim();
    if (!key) {
        showLoginError('Please enter an API key');
        return;
    }
    
    loginSubmitBtn.disabled = true;
    loginSubmitBtn.textContent = 'Connecting...';
    hideLoginError();
    
    const isValid = await validateApiKey(key);
    
    if (isValid) {
        apiKey = key;
        localStorage.setItem(API_KEY_STORAGE_KEY, key);
        showMainInterface();
        loadChatsFromStorage();
        await loadModels();
        setupEventListeners();
        renderPreviousChats();
    } else {
        showLoginError('Invalid API key. Please try again.');
        loginSubmitBtn.disabled = false;
        loginSubmitBtn.textContent = 'Connect';
    }
}
```

**Process:**
1. Prevents default form submission
2. Validates input (non-empty)
3. Shows loading state
4. Validates key with backend
5. If valid: stores key, shows main interface
6. If invalid: shows error, resets form

### API Key Validation

The frontend validates the API key by making a test request:

```106:121:static/app.js
// Validate API key by making a test request
async function validateApiKey(key) {
    try {
        const response = await fetch('/api/v1/models', {
            method: 'GET',
            headers: {
                'X-API-Key': key
            }
        });
        
        return response.status !== 401;
    } catch (error) {
        console.error('Error validating API key:', error);
        return false;
    }
}
```

**Validation Method:**
- Makes GET request to `/api/v1/models` endpoint
- Includes `X-API-Key` header
- Returns `true` if status is not 401 (unauthorized)
- Returns `false` on 401 or network errors

### API Headers

All API requests include the API key in headers:

```140:151:static/app.js
// Get API headers for requests
function getApiHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (apiKey) {
        headers['X-API-Key'] = apiKey;
    }
    
    return headers;
}
```

**Usage:**
- Adds `Content-Type: application/json` for POST requests
- Includes `X-API-Key` header if API key is set
- Used by all API requests (models, responses)

### Unauthorized Handling

When a 401 response is received, the app handles it:

```206:211:static/app.js
// Handle 401 unauthorized responses
function handleUnauthorized() {
    clearApiKey();
    showLoginForm();
    showLoginError('Session expired. Please enter your API key again.');
}
```

**Behavior:**
- Clears stored API key
- Shows login form
- Displays error message

This handles cases where:
- API key was revoked/changed on server
- Session expired
- Backend authentication was enabled after frontend load

### Clearing API Key

The API key can be cleared:

```123:127:static/app.js
// Clear API key
function clearApiKey() {
    apiKey = null;
    localStorage.removeItem(API_KEY_STORAGE_KEY);
}
```

**When Called:**
- Invalid API key detected
- 401 unauthorized response received
- User logout (if implemented)

## Configuration

### Setting API Key

**Server Side:**
```bash
API_KEY=your-secret-key-here python server.py
```

**Example:**
```bash
API_KEY=my-secure-key-123 python server.py
```

**Security Best Practices:**
- Use long, random strings (32+ characters)
- Don't commit API keys to version control
- Use environment variables or secrets management
- Rotate keys periodically

### Disabling Authentication

If `API_KEY` is not set, authentication is disabled:

```bash
python server.py
```

The application works normally without requiring API keys.

## Request Flow

### Authenticated Request

```
1. User enters API key in login form
2. Frontend validates key with /api/v1/models
3. If valid, key stored in localStorage
4. All subsequent requests include X-API-Key header
5. Backend validates header against API_KEY
6. Request proceeds if valid
```

### Unauthenticated Request (No API Key Set)

```
1. User accesses application
2. No login form shown (main interface immediately)
3. Requests sent without X-API-Key header
4. Backend allows all requests (API_KEY is None)
```

## Security Considerations

### Current Implementation

- **API key comparison**: Simple string comparison (timing-safe enough for this use case)
- **Storage**: Browser localStorage (accessible to JavaScript)
- **Transmission**: Plain HTTP headers (consider HTTPS in production)

### Security Limitations

1. **localStorage Security**: Keys stored in localStorage are accessible to any JavaScript on the page (XSS vulnerability)
2. **No Encryption**: Keys transmitted over HTTP (use HTTPS in production)
3. **Single Key**: All users share the same API key (no per-user authentication)

### Production Recommendations

1. **Use HTTPS**: Encrypt API key transmission
2. **Implement CSRF Protection**: Prevent cross-site request forgery
3. **Rate Limiting**: Prevent brute force attacks
4. **Key Rotation**: Regular key changes
5. **Multi-User Support**: Consider user accounts with individual keys
6. **Secure Storage**: For sensitive deployments, consider more secure storage mechanisms

## Backward Compatibility

The system maintains backward compatibility:

```20:22:server.py
        if not API_KEY:
            # If no API key is configured, allow access (backward compatibility)
            return f(*args, **kwargs)
```

**Behavior:**
- If `API_KEY` environment variable is not set, authentication is bypassed
- Existing deployments without API keys continue to work
- New deployments can optionally enable authentication

## Related Documentation

- [Backend Setup](03-Backend-Setup.md) - Server configuration
- [Chat Interface](02-Chat-Interface.md) - Frontend implementation
- [Error Handling](09-Error-Handling.md) - Error responses

