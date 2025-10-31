# Markdown Rendering

## Overview

The application renders assistant responses as markdown, providing rich formatting for code blocks, lists, tables, headers, and other markdown elements. User messages are displayed as plain text, while assistant messages are parsed and rendered using the Marked.js library. Rendering begins only after startup finishes the authentication requirement detection (`/api/v1/auth-required`) and, if needed, user API key validation—ensuring the interface does not partially render before access is granted.

## Marked.js Integration

### Library Inclusion

Marked.js is loaded from a CDN in the HTML:

```8:8:static/index.html
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
```

**Library:** Marked.js (latest version from CDN)
**Purpose:** Parse markdown and convert to HTML

### Usage

Marked.js is used to parse assistant message content:

```352:353:static/app.js
        if (role === 'assistant') {
            // Render markdown for assistant messages
            contentDiv.innerHTML = marked.parse(content);
```

**Function:** `marked.parse(content)`
**Returns:** HTML string from markdown input

## Message Rendering

### Adding Messages

When adding a new message, the app checks the role:

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

**Rendering Logic:**
- **User messages**: Plain text (`textContent`)
- **Assistant messages**: Markdown parsed to HTML (`innerHTML`)

### Loading Previous Messages

When loading a chat from history, messages are rendered the same way:

```488:492:static/app.js
        if (msg.role === 'assistant') {
            contentDiv.innerHTML = marked.parse(msg.content);
        } else {
            contentDiv.textContent = msg.content;
        }
```

**Consistency:**
- Same rendering logic for new and loaded messages
- Ensures consistent display across sessions

## Supported Markdown Features

### Code Blocks

Code blocks are rendered with syntax highlighting support:

**Markdown:**
````markdown
```python
def hello():
    print("Hello, World!")
```
````

**Rendered:** Styled code block with dark background

**Styling:**
```380:400:static/style.css
.message.assistant .message-content pre {
    background-color: #1e1e1e;
    color: #d4d4d4;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 12px 0;
}

.message.assistant .message-content code {
    background-color: #e8e8e8;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
}

.message.assistant .message-content pre code {
    background-color: transparent;
    padding: 0;
}
```

**Features:**
- Dark theme for code blocks (`#1e1e1e` background)
- Light theme for inline code (`#e8e8e8` background)
- Horizontal scrolling for long lines
- Monospace font

### Headers

Headers are styled appropriately:

**Markdown:**
```markdown
# H1 Header
## H2 Header
### H3 Header
```

**Styling:**
```426:430:static/style.css
.message.assistant .message-content h1,
.message.assistant .message-content h2,
.message.assistant .message-content h3 {
    margin: 16px 0 8px 0;
}
```

**Features:**
- Proper spacing
- Clear hierarchy

### Lists

Both ordered and unordered lists are supported:

**Markdown:**
```markdown
- Item 1
- Item 2
  - Nested item

1. First item
2. Second item
```

**Styling:**
```420:424:static/style.css
.message.assistant .message-content ul,
.message.assistant .message-content ol {
    margin: 12px 0;
    padding-left: 24px;
}
```

**Features:**
- Proper indentation
- Consistent spacing

### Tables

Tables are rendered with borders and styling:

**Markdown:**
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

**Styling:**
```402:418:static/style.css
.message.assistant .message-content table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
}

.message.assistant .message-content table th,
.message.assistant .message-content table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

.message.assistant .message-content table th {
    background-color: #f0f0f0;
    font-weight: 600;
}
```

**Features:**
- Bordered cells
- Header row highlighting
- Full width tables
- Proper padding

### Other Markdown Elements

Marked.js supports many other markdown features:

- **Bold text**: `**bold**` or `__bold__`
- **Italic text**: `*italic*` or `_italic_`
- **Links**: `[text](url)`
- **Images**: `![alt](url)`
- **Blockquotes**: `> quote`
- **Horizontal rules**: `---`
- **Strikethrough**: `~~text~~`

All standard markdown features supported by Marked.js are available.

## Styling

### Message Container

Assistant messages have distinct styling:

```375:378:static/style.css
.message.assistant .message-content {
    background-color: #f7f7f8;
    color: #333;
}
```

**Styling:**
- Light gray background (`#f7f7f8`)
- Dark text (`#333`)
- Contrasts with user messages

### User Messages

User messages use plain text styling:

```370:373:static/style.css
.message.user .message-content {
    background-color: #f0f0f0;
    color: #333;
}
```

**Styling:**
- Light gray background (`#f0f0f0`)
- Plain text only (no markdown)

## Security Considerations

### XSS Prevention

Marked.js by default sanitizes HTML to prevent XSS attacks. However, note:

- **Content Trust**: Assistant responses come from the LLM model
- **Model Trust**: If you trust the model, you trust its output
- **Sanitization**: Marked.js has built-in XSS protection

**Best Practice:** If concerned about XSS, consider:
- Using a sanitization library (DOMPurify)
- Configuring Marked.js sanitization options
- Validating model responses

### Content Sanitization

The current implementation relies on Marked.js default sanitization. For enhanced security:

```javascript
// Example with DOMPurify (not currently implemented)
import DOMPurify from 'dompurify';
contentDiv.innerHTML = DOMPurify.sanitize(marked.parse(content));
```

## Performance

### Rendering Performance

- **Parsing**: Marked.js is fast and efficient
- **DOM Updates**: Single `innerHTML` assignment
- **No Re-rendering**: Messages rendered once and stored

### Large Messages

For very long markdown content:
- Rendering happens synchronously
- May cause brief UI freeze for very large messages
- Consider lazy rendering or pagination for extremely long responses

## Storage and Persistence

### Markdown Storage

- **Storage Format**: Raw markdown stored in localStorage
- **Rendering**: Markdown parsed on display
- **No HTML Storage**: HTML is generated on-the-fly

**Benefits:**
- Smaller storage size
- Re-render with updated styles
- Original content preserved

### Loading from Storage

When loading chats, markdown is re-parsed:

```488:492:static/app.js
        if (msg.role === 'assistant') {
            contentDiv.innerHTML = marked.parse(msg.content);
        } else {
            contentDiv.textContent = msg.content;
        }
```

**Behavior:**
- Markdown content from storage
- Re-parsed with current Marked.js version
- Styles applied from current CSS

## Example Output

### Markdown Input

```markdown
# Python Example

Here's a simple Python function:

```python
def greet(name):
    return f"Hello, {name}!"
```

**Features:**
- Simple syntax
- Readable code
```

### Rendered Output

The markdown is converted to HTML and styled:

- **H1 Header**: Large, bold
- **Paragraph**: Normal text
- **Code Block**: Dark background, monospace
- **Bold Text**: Strong emphasis
- **List**: Bulleted items

## Customization

### Styling Customization

All markdown elements can be styled via CSS:

```css
/* Custom code block styling */
.message.assistant .message-content pre {
    background-color: #2d2d2d;
    border-left: 4px solid #0084ff;
}

/* Custom table styling */
.message.assistant .message-content table {
    border: 2px solid #0084ff;
}
```

### Marked.js Configuration

Marked.js can be configured for different behavior:

```javascript
// Example configuration (not currently used)
marked.setOptions({
    breaks: true,        // Convert line breaks to <br>
    gfm: true,          // GitHub Flavored Markdown
    headerIds: false,    // Don't add IDs to headers
});
```

## Limitations

### Current Limitations

1. **No Syntax Highlighting**: Code blocks don't have syntax highlighting (only styling)
2. **No Math Rendering**: Mathematical expressions not supported
3. **No Custom Extensions**: Standard markdown only
4. **No Mermaid Diagrams**: Diagram rendering not supported

### Potential Enhancements

- Add syntax highlighting (highlight.js, Prism.js)
- Add math rendering (KaTeX, MathJax)
- Add diagram support (Mermaid.js)
- Add custom markdown extensions

## Related Documentation

- [Chat Interface](02-Chat-Interface.md) - Message rendering implementation
- [Chat History](07-Chat-History.md) - Markdown storage and loading

