# Model Selection

## Overview

The application dynamically loads available models from Ollama and presents them in a dropdown selector. Users can switch between models at any time, and the selected model is used for subsequent requests. The model selection is integrated with chat history, allowing each chat to remember which model was used.

## Model Loading

### Initial Load

Models are loaded when the application initializes:

```153:204:static/app.js
// Load available models from the API
async function loadModels() {
    try {
        const response = await fetch('/api/v1/models', {
            headers: getApiHeaders()
        });
        
        if (response.status === 401) {
            handleUnauthorized();
            return false;
        }
        
        const data = await response.json();
        
        if (data.error) {
            showOllamaError(data.error);
            modelSelect.innerHTML = '<option value="">Ollama not available</option>';
            disableChatInterface();
            return false;
        }
        
        if (data.models && data.models.length > 0) {
            availableModels = data.models;
            modelSelect.innerHTML = '';
            
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
            
            // Select first model by default
            if (!currentChat.id) {
                modelSelect.value = data.models[0];
            }
            enableChatInterface();
            return true;
        } else {
            modelSelect.innerHTML = '<option value="">No models available</option>';
            showNoModelsError();
            disableChatInterface();
            return false;
        }
    } catch (error) {
        console.error('Error loading models:', error);
        modelSelect.innerHTML = '<option value="">Error loading models</option>';
        showOllamaError('Failed to connect to server');
        disableChatInterface();
        return false;
    }
}
```

**Process:**
1. Fetches models from `/api/v1/models` endpoint
2. Handles authentication errors (401)
3. Checks for API errors
4. Populates dropdown with model names
5. Selects first model by default (if no current chat)
6. Enables chat interface on success
7. Shows error state on failure

### Backend Model Retrieval

The backend queries Ollama for available models:

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

## Model Dropdown

### HTML Structure

The model selector is a `<select>` element:

```37:42:static/index.html
            <div class="model-selector">
                <label for="model-select">Model:</label>
                <select id="model-select">
                    <option value="">Loading...</option>
                </select>
            </div>
```

### Dynamic Population

Models are added as `<option>` elements:

```174:189:static/app.js
        if (data.models && data.models.length > 0) {
            availableModels = data.models;
            modelSelect.innerHTML = '';
            
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
            
            // Select first model by default
            if (!currentChat.id) {
                modelSelect.value = data.models[0];
            }
            enableChatInterface();
            return true;
```

**Population:**
- Clears existing options
- Creates option for each model
- Sets value and text to model name
- Selects first model if no current chat
- Stores models in `availableModels` array

## Model Selection State

### Current Model Storage

The selected model is stored in multiple places:

1. **HTML Select Element**: `modelSelect.value`
2. **Current Chat Object**: `currentChat.model`
3. **Available Models Array**: `availableModels`

### Model Association with Chats

Each chat stores the model it was created with:

```428:433:static/app.js
    if (!currentChat.id) {
        currentChat.id = Date.now();
        currentChat.timestamp = new Date().toISOString();
        currentChat.model = modelSelect.value;
    }
```

When loading a chat, the model is restored:

```499:502:static/app.js
    // Set model if available
    if (chat.model && availableModels.includes(chat.model)) {
        modelSelect.value = chat.model;
    }
```

**Behavior:**
- New chats store current model selection
- Loading chat restores model if still available
- If model no longer available, keeps current selection

## Model Switching

### Changing Models

Users can change models via the dropdown:

```132:141:static/style.css
.model-selector select {
    width: 100%;
    padding: 10px;
    border: 1px solid #444;
    border-radius: 6px;
    background-color: #3c3c3c;
    color: #fff;
    font-size: 14px;
    cursor: pointer;
}
```

**Behavior:**
- Changes take effect immediately
- No confirmation required
- Affects subsequent messages only
- Previous messages keep their original model

### Model in Requests

The selected model is sent with each request:

```254:262:static/app.js
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

**Usage:**
- `selectedModel` comes from `modelSelect.value`
- Sent as `model` field in request body
- Backend uses this to query appropriate Ollama model

## Error Handling

### Ollama Not Available

If Ollama is not running or unreachable:

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

### No Models Available

If Ollama is running but no models are installed:

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

### Network Errors

If the request fails:

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

## Interface State Management

### Enabling Chat Interface

When models load successfully:

```668:673:static/app.js
// Enable chat interface
function enableChatInterface() {
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.placeholder = 'Type your message here...';
}
```

**Actions:**
- Enables input textarea
- Enables send button
- Sets normal placeholder text

### Disabling Chat Interface

When models fail to load:

```661:666:static/app.js
// Disable chat interface
function disableChatInterface() {
    userInput.disabled = true;
    sendBtn.disabled = true;
    userInput.placeholder = 'Chat unavailable - Ollama not connected';
}
```

**Actions:**
- Disables input textarea
- Disables send button
- Sets error placeholder text

## Error Pages

### Ollama Error Page

Shown when Ollama is not available:

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
- Clear error message
- Step-by-step instructions
- Retry button to reload models
- Updates UI on successful retry

### No Models Error Page

Shown when no models are installed:

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
- Retry button to check for new models

## Model Validation

### Validation Before Sending

Before sending a message, the app validates model selection:

```226:230:static/app.js
async function sendMessage() {
    const prompt = userInput.value.trim();
    const selectedModel = modelSelect.value;
    
    if (!prompt || !selectedModel || isLoading) return;
```

**Validation:**
- Checks prompt is not empty
- Checks model is selected
- Checks not already loading
- Returns early if validation fails

### Model Availability Check

When loading a chat, checks if stored model is still available:

```499:502:static/app.js
    // Set model if available
    if (chat.model && availableModels.includes(chat.model)) {
        modelSelect.value = chat.model;
    }
```

**Behavior:**
- Only restores model if it exists in available models
- If model removed from Ollama, keeps current selection
- Prevents errors from selecting unavailable models

## Refresh Behavior

### No Auto-Refresh

The application does not automatically refresh the model list:
- Models loaded once on initialization
- Manual refresh via retry button
- Page reload required to see newly installed models

### Manual Refresh

Users can refresh models by:
1. Clicking retry button on error pages
2. Reloading the page
3. Restarting the application

## Related Documentation

- [LLM Serving](01-LLM-Serving.md) - How models are queried
- [Backend Setup](03-Backend-Setup.md) - API endpoint implementation
- [Error Handling](09-Error-Handling.md) - Error management
- [Chat History](07-Chat-History.md) - Model storage in chats

