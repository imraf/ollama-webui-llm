# Error Handling

## Overview

The application implements comprehensive error handling at both the frontend and backend levels. Errors are caught, processed, and presented to users in a user-friendly manner. The system handles network errors, API errors, validation errors, and unexpected exceptions.

## Backend Error Handling

### Exception Hierarchy

The backend handles errors in order of specificity:

```94:99:server.py
    except BadRequest:
        return jsonify({"error": "Invalid JSON data provided"}), 400
    except ollama.ResponseError as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
```

**Error Types:**
1. **BadRequest**: Invalid JSON format (from Flask)
2. **ollama.ResponseError**: Ollama-specific errors (model not found, connection issues)
3. **Exception**: Catch-all for unexpected errors

### Request Validation Errors

#### Missing JSON Data

```53:54:server.py
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
```

**Error Response:**
- Status: `400 Bad Request`
- Message: `"No JSON data provided"`

#### Missing Required Fields

```60:64:server.py
        if not prompt:
            return jsonify({"error": "Missing 'prompt' field"}), 400
        
        if not model:
            return jsonify({"error": "Missing 'model' field"}), 400
```

**Error Responses:**
- Status: `400 Bad Request`
- Messages: `"Missing 'prompt' field"` or `"Missing 'model' field"`

#### Invalid JSON Format

```94:95:server.py
    except BadRequest:
        return jsonify({"error": "Invalid JSON data provided"}), 400
```

**Error Response:**
- Status: `400 Bad Request`
- Message: `"Invalid JSON data provided"`

### Ollama Errors

#### Response Errors

```96:97:server.py
    except ollama.ResponseError as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500
```

**Common Ollama Errors:**
- Model not found
- Ollama server not running
- Connection refused
- Timeout errors

**Error Response:**
- Status: `500 Internal Server Error`
- Message: `"Ollama error: {error details}"`

#### Models Endpoint Errors

```120:123:server.py
    except ollama.ResponseError as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
```

**Error Responses:**
- Status: `500 Internal Server Error`
- Messages: `"Ollama error: ..."` or `"Server error: ..."`

### Authentication Errors

#### Missing API Key

```24:26:server.py
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
```

**Error Response:**
- Status: `401 Unauthorized`
- Message: `"Invalid or missing API key"`

### Auth Requirement Detection Endpoint

The `/api/v1/auth-required` endpoint is intentionally simple and public. It returns `200` with a JSON body indicating whether authentication is enforced. It does not raise authentication errors itself; failures are limited to unexpected server errors (very rare) or network issues on the client side.

**Client-Side Failure Handling:**
- If the fetch to `/api/v1/auth-required` fails (network error, offline state, CORS misconfiguration), the frontend conservatively assumes `auth_required = true` and shows the login form.
- This prevents accidentally exposing protected endpoints if the detection request cannot complete.

**Design Rationale:**
- Keeps detection lightweight (no decorator / authentication logic).
- Ensures a single source of truth for auth state communicated early in the lifecycle.
- Avoids ambiguous UI states (e.g., flashing the interface then swapping to login).

## Frontend Error Handling

### Network Errors

#### Fetch Failures

```288:292:static/app.js
    } catch (error) {
        removeLoading(loadingId);
        addMessage('assistant', `Error: ${error.message}`);
        console.error('Error sending message:', error);
    }
```

**Error Display:**
- Shows error message in chat
- Logs error to console
- Removes loading indicator

#### API Error Responses

```284:287:static/app.js
        } else {
            removeLoading(loadingId);
            addMessage('assistant', `Error: ${data.error || 'Unknown error occurred'}`);
        }
```

**Error Display:**
- Shows backend error message
- Falls back to generic message if error field missing
- Removes loading indicator

### Authentication Errors

#### Unauthorized (401) Handling

```264:270:static/app.js
        if (response.status === 401) {
            handleUnauthorized();
            removeLoading(loadingId);
            isLoading = false;
            updateSendButton();
            return;
        }
```

**Behavior:**
- Clears API key
- Shows login form
- Displays error message
- Resets UI state

#### Unauthorized Handler

```206:211:static/app.js
// Handle 401 unauthorized responses
function handleUnauthorized() {
    clearApiKey();
    showLoginForm();
    showLoginError('Session expired. Please enter your API key again.');
}
```

**Actions:**
- Clears stored API key
- Shows login form
- Displays session expired message

### Model Loading Errors

#### Ollama Not Available

```166:172:static/app.js
        if (data.error) {
            showOllamaError(data.error);
            modelSelect.innerHTML = '<option value="">Ollama not available</option>';
            disableChatInterface();
            return false;
        }
```

**Error Display:**
- Shows error page with instructions
- Disables chat interface
- Provides retry button

#### No Models Available

```191:196:static/app.js
        } else {
            modelSelect.innerHTML = '<option value="">No models available</option>';
            showNoModelsError();
            disableChatInterface();
            return false;
        }
```

**Error Display:**
- Shows instructions for installing models
- Disables chat interface
- Provides retry button

#### Connection Errors

```197:203:static/app.js
    } catch (error) {
        console.error('Error loading models:', error);
        modelSelect.innerHTML = '<option value="">Error loading models</option>';
        showOllamaError('Failed to connect to server');
        disableChatInterface();
        return false;
    }
```

**Error Display:**
- Shows generic connection error
- Disables chat interface
- Logs error to console

### API Key Validation Errors

#### Invalid API Key

```99:103:static/app.js
    } else {
        showLoginError('Invalid API key. Please try again.');
        loginSubmitBtn.disabled = false;
        loginSubmitBtn.textContent = 'Connect';
    }
```

**Error Display:**
- Shows error message in login form
- Re-enables submit button
- Allows retry

#### Validation Failure

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

**Behavior:**
- Returns `false` on 401 or network errors
- Logs errors to console
- Handles errors gracefully

## Error Display Components

### Error Pages

#### Ollama Error Page

```579:618:static/app.js
// Show Ollama error page
function showOllamaError(errorMessage) {
    chatContainer.innerHTML = `
        <div class="error-page">
            <div class="error-icon">⚠️</div>
            <h1>Ollama Not Available</h1>
            <p class="error-message">${errorMessage || 'Failed to connect to Ollama'}</p>
            <div class="error-instructions">
                <h3>To fix this:</h3>
                <ol>
                    <li>Make sure Ollama is installed. If not, download it from <a href="https://ollama.com/download" target="_blank">ollama.com/download</a></li>
                    <li>Start Ollama by running: <code>ollama serve</code></li>
                    <li>Or if using the desktop app, make sure it's running</li>
                    <li>Click the retry button below once Ollama is running</li>
                </ol>
            </div>
            <button id="retry-connection-btn" class="retry-btn">🔄 Retry Connection</button>
        </div>
    `;
    
    const retryBtn = document.getElementById('retry-connection-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', async () => {
            retryBtn.textContent = 'Connecting...';
            retryBtn.disabled = true;
            const success = await loadModels();
            if (success) {
                chatContainer.innerHTML = `
                    <div class="welcome-message">
                        <h1>Welcome to LLM Chat</h1>
                        <p>Select a model and start chatting!</p>
                    </div>
                `;
            } else {
                retryBtn.textContent = '🔄 Retry Connection';
                retryBtn.disabled = false;
            }
        });
    }
}
```

**Features:**
- Clear error icon and title
- Error message display
- Step-by-step instructions
- Retry button with loading state
- Updates UI on success

#### No Models Error Page

```620:659:static/app.js
// Show no models error
function showNoModelsError() {
    chatContainer.innerHTML = `
        <div class="error-page">
            <div class="error-icon">📦</div>
            <h1>No Models Available</h1>
            <p class="error-message">Ollama is running, but no models are installed.</p>
            <div class="error-instructions">
                <h3>To install a model:</h3>
                <ol>
                    <li>Open a terminal</li>
                    <li>Run: <code>ollama pull llama2</code></li>
                    <li>Or choose another model from <a href="https://ollama.com/library" target="_blank">ollama.com/library</a></li>
                    <li>Click the retry button below once a model is installed</li>
                </ol>
            </div>
            <button id="retry-connection-btn" class="retry-btn">🔄 Retry Connection</button>
        </div>
    `;
    
    const retryBtn = document.getElementById('retry-connection-btn');
    if (retryBtn) {
        retryBtn.addEventListener('click', async () => {
            retryBtn.textContent = 'Checking...';
            retryBtn.disabled = true;
            const success = await loadModels();
            if (success) {
                chatContainer.innerHTML = `
                    <div class="welcome-message">
                        <h1>Welcome to LLM Chat</h1>
                        <p>Select a model and start chatting!</p>
                    </div>
                `;
            } else {
                retryBtn.textContent = '🔄 Retry Connection';
                retryBtn.disabled = false;
            }
        });
    }
}
```

**Features:**
- Instructions for installing models
- Link to Ollama model library
- Retry functionality

### Inline Error Messages

#### Chat Error Messages

Errors in chat are displayed as assistant messages:

```284:287:static/app.js
        } else {
            removeLoading(loadingId);
            addMessage('assistant', `Error: ${data.error || 'Unknown error occurred'}`);
        }
```

**Format:**
- Prefixed with "Error: "
- Shows backend error message
- Falls back to generic message

#### Login Error Messages

```129:133:static/app.js
// Show login error
function showLoginError(message) {
    loginError.textContent = message;
    loginError.style.display = 'block';
}
```

**Display:**
- Red error box in login form
- Clear error message
- Visible until cleared

## Retry Mechanisms

### Model Loading Retry

Users can retry model loading via error page buttons:

```600:616:static/app.js
        retryBtn.addEventListener('click', async () => {
            retryBtn.textContent = 'Connecting...';
            retryBtn.disabled = true;
            const success = await loadModels();
            if (success) {
                chatContainer.innerHTML = `
                    <div class="welcome-message">
                        <h1>Welcome to LLM Chat</h1>
                        <p>Select a model and start chatting!</p>
                    </div>
                `;
            } else {
                retryBtn.textContent = '🔄 Retry Connection';
                retryBtn.disabled = false;
            }
        });
```

**Behavior:**
- Shows loading state
- Attempts to reload models
- Updates UI on success
- Re-enables button on failure

### API Key Retry

Users can retry API key entry:

```99:103:static/app.js
    } else {
        showLoginError('Invalid API key. Please try again.');
        loginSubmitBtn.disabled = false;
        loginSubmitBtn.textContent = 'Connect';
    }
```

**Behavior:**
- Shows error message
- Re-enables form
- Allows immediate retry

## Error Recovery

### Graceful Degradation

The application handles errors gracefully:

1. **Model Loading Failure**: Disables chat, shows error page
2. **API Request Failure**: Shows error in chat, allows retry
3. **Authentication Failure**: Shows login form, clears invalid key
4. **Network Failure**: Shows error message, allows retry

### State Recovery

Errors don't corrupt application state:

- Current chat preserved on transient errors
- Chat history maintained in localStorage
- UI state reset appropriately
- No data loss on errors

## Error Logging

### Console Logging

Errors are logged to browser console:

```197:203:static/app.js
    } catch (error) {
        console.error('Error loading models:', error);
        modelSelect.innerHTML = '<option value="">Error loading models</option>';
        showOllamaError('Failed to connect to server');
        disableChatInterface();
        return false;
    }
```

**Logged Information:**
- Error messages
- Stack traces (in development)
- Context about where error occurred

### Backend Logging

Flask logs errors automatically in debug mode:

```129:134:server.py
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Flask server on http://localhost:{port}")
    print(f"Ollama host: {OLLAMA_HOST}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
```

**Debug Mode:**
- Detailed error pages
- Stack traces
- Request/response logging

## User-Friendly Error Messages

### Error Message Guidelines

- **Clear**: Explain what went wrong
- **Actionable**: Tell user how to fix it
- **Contextual**: Show where error occurred
- **Helpful**: Provide next steps

### Example Error Messages

**Good:**
- "Ollama is running, but no models are installed. Install a model with: `ollama pull llama2`"
- "Invalid API key. Please check your key and try again."
- "Failed to connect to server. Check your internet connection."

**Less Helpful:**
- "Error 500"
- "Something went wrong"
- "Request failed"

## Related Documentation

- [Backend Setup](03-Backend-Setup.md) - Server error handling
- [API Key System](04-API-Key-System.md) - Authentication errors
- [Model Selection](08-Model-Selection.md) - Model loading errors
- [Tests](05-Tests.md) - Error handling test cases

