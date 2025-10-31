# Chat Interface

## Overview

The chat interface is a single-page web application built with vanilla JavaScript, HTML, and CSS. It provides a clean, mobile-inspired UI for interacting with LLM models through the backend API. The interface handles message rendering, state management, user interactions, and integrates with browser localStorage for persistence.

## UI Components

### Layout Structure

The interface uses a two-column layout:

```30:66:static/index.html
    <div class="container" id="main-container" style="display: none;">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2>LLM Chat</h2>
            </div>
            
            <div class="model-selector">
                <label for="model-select">Model:</label>
                <select id="model-select">
                    <option value="">Loading...</option>
                </select>
            </div>
            
            <button id="new-chat-btn" class="new-chat-btn">+ New Chat</button>
            
            <div class="chat-history">
                <h3>Previous Chats</h3>
                <div id="previous-chats"></div>
            </div>
        </aside>
        
        <!-- Main Chat Area -->
        <main class="main-content">
            <div id="chat-container" class="chat-container">
                <div class="welcome-message">
                    <h1>Welcome to LLM Chat</h1>
                    <p>Select a model and start chatting!</p>
                </div>
            </div>
            
            <div class="input-area">
                <textarea id="user-input" placeholder="Type your message here..." rows="3"></textarea>
                <button id="send-btn" class="send-btn">Send</button>
            </div>
        </main>
    </div>
```

**Components:**
- **Sidebar**: Contains model selector, new chat button, and chat history
- **Main Content**: Chat container for messages and input area
- **Chat Container**: Scrollable area displaying conversation messages
- **Input Area**: Textarea and send button for user input

### Login Form

When API key authentication is enabled, a login form is displayed:

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

## State Management

The application maintains state using JavaScript variables:

```2:11:static/app.js
// State management
let currentChat = {
    id: null,
    messages: [],
    title: null
};

let chats = [];
let availableModels = [];
let isLoading = false;
let apiKey = null;
```

**State Variables:**
- `currentChat`: Current active chat session with id, messages array, and title
- `chats`: Array of all saved chat sessions
- `availableModels`: List of available models from the API
- `isLoading`: Boolean flag to prevent concurrent requests
- `apiKey`: Stored API key for authenticated requests

## Message Rendering

### Adding Messages

Messages are added to the chat container dynamically:

```337:363:static/app.js
// Add message to the chat
function addMessage(role, content) {
    const message = { role, content };
    currentChat.messages.push(message);
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const header = document.createElement('div');
    header.className = 'message-header';
    header.textContent = role === 'user' ? 'You' : 'Assistant';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (role === 'assistant') {
        // Render markdown for assistant messages
        contentDiv.innerHTML = marked.parse(content);
    } else {
        contentDiv.textContent = content;
    }
    
    messageDiv.appendChild(header);
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    scrollToBottom();
}
```

**Message Structure:**
- Each message has a `role` ('user' or 'assistant') and `content`
- User messages display plain text
- Assistant messages are rendered as markdown (see [Markdown Rendering](10-Markdown-Rendering.md))
- Messages include a header showing "You" or "Assistant"
- Chat automatically scrolls to bottom after adding a message

### Loading Indicator

While waiting for a response, a loading indicator is shown:

```366:382:static/app.js
// Show loading indicator
function showLoading() {
    const loadingId = 'loading-' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.id = loadingId;
    loadingDiv.className = 'loading-indicator';
    loadingDiv.innerHTML = `
        <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
        <span>Thinking...</span>
    `;
    chatContainer.appendChild(loadingDiv);
    scrollToBottom();
    return loadingId;
}
```

The loading indicator is removed when the response arrives:

```384:390:static/app.js
// Remove loading indicator
function removeLoading(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}
```

## User Interactions

### Sending Messages

The send functionality handles user input:

```226:296:static/app.js
// Send message to the API
async function sendMessage() {
    const prompt = userInput.value.trim();
    const selectedModel = modelSelect.value;
    
    if (!prompt || !selectedModel || isLoading) return;
    
    // Clear welcome message if it exists
    const welcomeMessage = chatContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // Check if this is the first message in a new chat
    const isFirstMessage = currentChat.messages.length === 0;
    
    // Add user message to chat
    addMessage('user', prompt);
    userInput.value = '';
    isLoading = true;
    updateSendButton();
    
    // Show loading indicator
    const loadingId = showLoading();
    
    try {
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
        
        if (response.status === 401) {
            handleUnauthorized();
            removeLoading(loadingId);
            isLoading = false;
            updateSendButton();
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            removeLoading(loadingId);
            addMessage('assistant', data.response);
            
            // If this was the first message, generate a title
            if (isFirstMessage) {
                await generateChatTitle(prompt, selectedModel);
            }
            
            saveCurrentChat();
        } else {
            removeLoading(loadingId);
            addMessage('assistant', `Error: ${data.error || 'Unknown error occurred'}`);
        }
    } catch (error) {
        removeLoading(loadingId);
        addMessage('assistant', `Error: ${error.message}`);
        console.error('Error sending message:', error);
    }
    
    isLoading = false;
    updateSendButton();
}
```

**Flow:**
1. Validates input (non-empty prompt and selected model)
2. Clears welcome message if present
3. Adds user message to chat
4. Sends request to backend with context
5. Displays response or error
6. Generates title for first message
7. Saves chat to localStorage

### Event Listeners

Event listeners are set up during initialization:

```214:223:static/app.js
// Setup event listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    newChatBtn.addEventListener('click', createNewChat);
}
```

**Interactions:**
- Click send button to send message
- Press Enter (without Shift) to send message
- Shift+Enter creates a new line
- New Chat button creates a fresh conversation

### Creating New Chat

```403:425:static/app.js
// Create new chat
function createNewChat() {
    if (currentChat.messages.length > 0) {
        saveCurrentChat();
    }
    
    currentChat = {
        id: Date.now(),
        messages: [],
        title: null,
        model: modelSelect.value,
        timestamp: new Date().toISOString()
    };
    
    chatContainer.innerHTML = `
        <div class="welcome-message">
            <h1>New Chat</h1>
            <p>Start a conversation!</p>
        </div>
    `;
    
    renderPreviousChats();
}
```

**Behavior:**
- Saves current chat if it has messages
- Creates new chat object with timestamp
- Resets chat container with welcome message
- Updates chat history sidebar

### Loading Previous Chats

```462:506:static/app.js
// Load chat from history
function loadChat(chatId) {
    if (currentChat.messages.length > 0 && currentChat.id !== chatId) {
        saveCurrentChat();
    }
    
    const chat = chats.find(c => c.id === chatId);
    if (!chat) return;
    
    currentChat = { ...chat };
    
    // Clear chat container
    chatContainer.innerHTML = '';
    
    // Render all messages
    currentChat.messages.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${msg.role}`;
        
        const header = document.createElement('div');
        header.className = 'message-header';
        header.textContent = msg.role === 'user' ? 'You' : 'Assistant';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (msg.role === 'assistant') {
            contentDiv.innerHTML = marked.parse(msg.content);
        } else {
            contentDiv.textContent = msg.content;
        }
        
        messageDiv.appendChild(header);
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
    });
    
    // Set model if available
    if (chat.model && availableModels.includes(chat.model)) {
        modelSelect.value = chat.model;
    }
    
    scrollToBottom();
    renderPreviousChats();
}
```

**Behavior:**
- Saves current chat before switching
- Finds chat by ID from stored chats
- Renders all messages from the loaded chat
- Restores model selection if available
- Updates active chat highlight in sidebar

## Styling

The interface uses a clean, modern design with:

- **Dark sidebar** (#2c2c2c) for navigation and controls
- **Light main area** (#fff) for chat content
- **Responsive layout** that narrows chat area on wider screens
- **Message styling** with distinct colors for user (blue) and assistant (green) messages
- **Smooth scrolling** and transitions

See `static/style.css` for complete styling details.

## Initialization

The application initializes when the DOM is ready. The first action performed is an authentication requirement check via the public endpoint `/api/v1/auth-required`.

```675:680:static/app.js
// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
```

### Startup Flow (`init()`)

```javascript
async function init() {
    const authRequired = await checkAuthRequirement();
    
    if (!authRequired) {
        // Auth not required: show interface immediately
        showMainInterface();
        loadChatsFromStorage();
        // Immediately render any previously saved chats in the sidebar
        renderPreviousChats();
        await loadModels();
        setupEventListeners();
        return; // Skip login listeners entirely
    }
    
    // Auth required path
    apiKey = localStorage.getItem(API_KEY_STORAGE_KEY);
    if (apiKey) {
        const isValid = await validateApiKey(apiKey);
        if (isValid) {
            showMainInterface();
            loadChatsFromStorage();
            // Populate sidebar before model load
            renderPreviousChats();
            await loadModels();
            setupEventListeners();
        } else {
            clearApiKey();
            showLoginForm();
        }
    } else {
        showLoginForm();
    }
    setupLoginListeners();
}
```

### Sequence Explanation
1. Call `/api/v1/auth-required` (always public) to detect whether API key enforcement is active.
2. If `auth_required` is false:
   - Skip all login logic.
   - Immediately show main interface and proceed to load chats/models.
3. If `auth_required` is true:
   - Attempt to reuse a stored key from `localStorage`.
   - Validate the key by calling `/api/v1/models` and checking for a non-401 status.
   - If validation succeeds: show interface and continue loading.
   - If validation fails or no key exists: present the login form.
4. Attach either chat event listeners (unprotected path) or both login + chat listeners (protected path).

### Why Detection First?
- Avoids unnecessary login prompts when the server runs without an `API_KEY`.
- Provides a frictionless startup in open mode (no modal flash).
- Enables graceful fallback: if detection fails (network error), the frontend assumes auth is required for safety.

### Post-Auth Actions
After successful detection (and optional validation):
- Chat history is loaded (`loadChatsFromStorage()`).
- Model list is fetched (`loadModels()`), including `X-API-Key` if applicable.
- Event listeners for sending messages, creating chats, and Enter key handling are installed.
- Previous chats are rendered in the sidebar.

See also: [API Key System](04-API-Key-System.md) and [Backend Setup](03-Backend-Setup.md) for related endpoint details.

## Related Documentation

- [Chat History](07-Chat-History.md) - Persistence and history management
- [Markdown Rendering](10-Markdown-Rendering.md) - How assistant messages are formatted
- [API Key System](04-API-Key-System.md) - Authentication flow
- [Model Selection](08-Model-Selection.md) - Model loading and selection

