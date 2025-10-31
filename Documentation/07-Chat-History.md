# Chat History

## Overview

The application maintains a persistent chat history using browser localStorage. Each conversation is stored with its messages, title, model, and metadata. Users can create new chats, load previous chats, and delete chats. The history persists across page reloads and browser sessions.

## Storage Implementation

### localStorage Usage

Chats are stored in browser localStorage under the key `'llm-chats'`:

```558:577:static/app.js
// Local storage functions
function saveChatsToStorage() {
    try {
        localStorage.setItem('llm-chats', JSON.stringify(chats));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function loadChatsFromStorage() {
    try {
        const stored = localStorage.getItem('llm-chats');
        if (stored) {
            chats = JSON.parse(stored);
        }
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        chats = [];
    }
}
```

**Storage Format:**
- JSON stringified array of chat objects
- Parsed on load, stringified on save
- Error handling for storage failures

### Chat Object Structure

Each chat object contains:

```428:443:static/app.js
    if (!currentChat.id) {
        currentChat.id = Date.now();
        currentChat.timestamp = new Date().toISOString();
        currentChat.model = modelSelect.value;
    }
    
    if (currentChat.messages.length === 0) return;
    
    // Generate title from first user message
    if (!currentChat.title) {
        const firstUserMessage = currentChat.messages.find(m => m.role === 'user');
        currentChat.title = firstUserMessage 
            ? firstUserMessage.content.substring(0, 50) + (firstUserMessage.content.length > 50 ? '...' : '')
            : 'Untitled Chat';
    }
```

**Chat Object:**
```javascript
{
    id: 1234567890123,              // Timestamp (Date.now())
    messages: [                      // Array of message objects
        {
            role: 'user',
            content: 'Message text'
        },
        {
            role: 'assistant',
            content: 'Response text'
        }
    ],
    title: 'Chat Title',             // Auto-generated or fallback
    model: 'llama2',                 // Model used for this chat
    timestamp: '2024-01-01T12:00:00.000Z'  // ISO timestamp
}
```

## Saving Chats

### Auto-Save Behavior

Chats are automatically saved after:
1. Receiving a response from the model
2. Creating a new chat (saves previous chat first)
3. Loading a different chat (saves current chat first)

### Save Function

```427:460:static/app.js
// Save current chat
function saveCurrentChat() {
    if (!currentChat.id) {
        currentChat.id = Date.now();
        currentChat.timestamp = new Date().toISOString();
        currentChat.model = modelSelect.value;
    }
    
    if (currentChat.messages.length === 0) return;
    
    // Generate title from first user message
    if (!currentChat.title) {
        const firstUserMessage = currentChat.messages.find(m => m.role === 'user');
        currentChat.title = firstUserMessage 
            ? firstUserMessage.content.substring(0, 50) + (firstUserMessage.content.length > 50 ? '...' : '')
            : 'Untitled Chat';
    }
    
    // Update or add chat to the list
    const existingIndex = chats.findIndex(c => c.id === currentChat.id);
    if (existingIndex !== -1) {
        chats[existingIndex] = { ...currentChat };
    } else {
        chats.unshift({ ...currentChat });
    }
    
    // Keep only last 50 chats
    if (chats.length > 50) {
        chats = chats.slice(0, 50);
    }
    
    saveChatsToStorage();
    renderPreviousChats();
}
```

**Process:**
1. Generates ID and timestamp if new chat
2. Skips save if no messages
3. Generates title from first user message if missing
4. Updates existing chat or adds new one to beginning
5. Limits to last 50 chats
6. Saves to localStorage
7. Updates UI

### Title Generation

Titles are generated from the first user message:

```438:443:static/app.js
    if (!currentChat.title) {
        const firstUserMessage = currentChat.messages.find(m => m.role === 'user');
        currentChat.title = firstUserMessage 
            ? firstUserMessage.content.substring(0, 50) + (firstUserMessage.content.length > 50 ? '...' : '')
            : 'Untitled Chat';
    }
```

**Title Logic:**
- Uses first user message content
- Truncates to 50 characters
- Adds "..." if truncated
- Falls back to "Untitled Chat" if no user messages

### Auto Title Generation

For a better title, the app generates one using the model:

```298:334:static/app.js
// Generate chat title from first message
async function generateChatTitle(firstPrompt, model) {
    try {
        const response = await fetch('/api/v1/response', {
            method: 'POST',
            headers: getApiHeaders(),
            body: JSON.stringify({
                prompt: `Generate a short, concise title (maximum 6 words) for a conversation that starts with this user question: "${firstPrompt}". Only respond with the title, nothing else.`,
                model: model,
                context: []
            })
        });
        
        if (response.status === 401) {
            handleUnauthorized();
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            // Clean up the title (remove quotes, trim, limit length)
            let title = data.response.trim().replace(/^["']|["']$/g, '');
            if (title.length > 50) {
                title = title.substring(0, 50) + '...';
            }
            currentChat.title = title;
            saveCurrentChat();
            renderPreviousChats();
            console.log('Chat title generated:', title);
        }
    } catch (error) {
        console.error('Error generating chat title:', error);
        // Fallback to using first prompt as title
        currentChat.title = firstPrompt.substring(0, 50) + (firstPrompt.length > 50 ? '...' : '');
    }
}
```

**Title Generation:**
- Triggered after first message response
- Uses LLM to generate concise title (max 6 words)
- Cleans up response (removes quotes, trims)
- Falls back to first prompt if generation fails

## Loading Chats

### Loading from Storage

On app initialization:

```567:577:static/app.js
function loadChatsFromStorage() {
    try {
        const stored = localStorage.getItem('llm-chats');
        if (stored) {
            chats = JSON.parse(stored);
        }
    } catch (error) {
        console.error('Error loading from localStorage:', error);
        chats = [];
    }
}
```

**Process:**
1. Retrieves JSON string from localStorage
2. Parses into JavaScript array
3. Handles errors gracefully (empty array on failure)

### Loading a Specific Chat

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

**Process:**
1. Saves current chat if it has messages
2. Finds chat by ID
3. Copies chat to currentChat
4. Clears chat container
5. Renders all messages (with markdown for assistant)
6. Restores model selection
7. Scrolls to bottom
8. Updates sidebar highlighting

## Rendering Chat History

### Sidebar Display

Previous chats are displayed in the sidebar:

```524:556:static/app.js
// Render previous chats list
function renderPreviousChats() {
    previousChatsContainer.innerHTML = '';
    
    if (chats.length === 0) {
        previousChatsContainer.innerHTML = '<p style="color: #666; font-size: 13px; padding: 10px;">No previous chats</p>';
        return;
    }
    
    chats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        if (chat.id === currentChat.id) {
            chatItem.classList.add('active');
        }
        
        const title = document.createElement('div');
        title.className = 'chat-item-title';
        title.textContent = chat.title || 'Untitled Chat';
        
        const preview = document.createElement('div');
        preview.className = 'chat-item-preview';
        const lastMessage = chat.messages[chat.messages.length - 1];
        preview.textContent = lastMessage ? lastMessage.content.substring(0, 60) + '...' : 'Empty chat';
        
        chatItem.appendChild(title);
        chatItem.appendChild(preview);
        
        chatItem.addEventListener('click', () => loadChat(chat.id));
        
        previousChatsContainer.appendChild(chatItem);
    });
}
```

**Display:**
- Shows title and preview of last message
- Highlights active chat
- Click to load chat
- Shows "No previous chats" if empty

## Creating New Chats

### New Chat Function

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

**Process:**
1. Saves current chat if it has messages
2. Creates new chat object with timestamp ID
3. Resets messages and title
4. Shows welcome message
5. Updates sidebar

## Deleting Chats

### Delete Function

```508:522:static/app.js
// Delete chat
function deleteChat(chatId, event) {
    event.stopPropagation();
    
    if (confirm('Are you sure you want to delete this chat?')) {
        chats = chats.filter(c => c.id !== chatId);
        saveChatsToStorage();
        
        if (currentChat.id === chatId) {
            createNewChat();
        } else {
            renderPreviousChats();
        }
    }
}
```

**Process:**
1. Confirms deletion with user
2. Filters chat from array
3. Saves to localStorage
4. Creates new chat if deleted chat was active
5. Updates sidebar

**Note:** Delete functionality is defined but not currently wired to UI elements in the current implementation.

## Storage Limits

### Chat Limit

The application limits stored chats to 50:

```453:456:static/app.js
    // Keep only last 50 chats
    if (chats.length > 50) {
        chats = chats.slice(0, 50);
    }
```

**Behavior:**
- When saving, if more than 50 chats exist, keeps only first 50
- Oldest chats are removed automatically
- Prevents localStorage from growing too large

### localStorage Limits

Browser localStorage typically has limits:
- **Size**: 5-10MB per origin (varies by browser)
- **Quota**: Can throw `QuotaExceededError` if limit exceeded

**Mitigation:**
- 50 chat limit helps prevent quota issues
- Error handling in save function catches storage errors
- No explicit quota checking (relies on browser error)

## Data Persistence

### What Persists

- **Chat messages**: Full conversation history
- **Chat titles**: Auto-generated or fallback
- **Model selection**: Model used for each chat
- **Timestamps**: When chat was created

### What Doesn't Persist

- **Current input**: Textarea content is not saved
- **Loading state**: UI state is reset on reload
- **Selected model**: Model selector resets (though can be restored from chat data)

### Cross-Session Persistence

- Chats persist across:
  - Page reloads
  - Browser restarts
  - Tab closures (same browser)
- Chats don't persist across:
  - Different browsers
  - Incognito/private mode (may clear localStorage)
  - localStorage clearing (manual or browser setting)

## Related Documentation

- [Chat Interface](02-Chat-Interface.md) - UI components and interactions
- [Conversation Context](06-Conversation-Context.md) - How context is managed
- [Markdown Rendering](10-Markdown-Rendering.md) - How messages are displayed

