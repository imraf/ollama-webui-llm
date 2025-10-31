# Prompts Document

This document contains the original prompts used in several stages of the app creation.

---

## PRD Structure Research Prompt

Research best practices and standard structures for Product Requirements Documents (PRDs), including typical sections, requirement numbering schemes, formatting conventions, and comprehensive coverage patterns used in software development, to inform the creation of a detailed PRD creation prompt.

## PRD Creation Prompt Construction

Based on the PRD structure research you found, create a comprehensive and detailed prompt that will generate a complete Product Requirements Document for a minimal, lightweight web-based chat interface for interacting with locally running Large Language Models (LLMs) served through Ollama.

## PRD Creation Prompt

Create a comprehensive Product Requirements Document (PRD) for a minimal, lightweight web-based chat interface for interacting with locally running Large Language Models (LLMs) served through Ollama.

### Project Overview

The application should be:
- **Minimal and Zero-Config**: No Node.js, no build tools, no bundlers, no transpilers
- **Python-Only Stack**: Backend and all dependencies managed through Python (use pip/venv)
- **Vanilla JavaScript Frontend**: No frameworks, just HTML, CSS, and vanilla JS
- **Instant Setup**: Clone repository, install Python dependencies, run Flask server, start chatting
- **Local-First**: Complete privacy with models running entirely on user's machine
- **Mobile-Inspired UI**: Clean, modern interface optimized for readability and conversation flow

### Core Requirements

1. **Chat Interface**
   - Send text prompts to selected Ollama models
   - Display model responses in real-time
   - Support multi-turn conversations with context awareness
   - Render assistant responses as markdown (code blocks, tables, lists, etc.)
   - User messages displayed as plain text

2. **Model Management**
   - Dynamically load available models from Ollama
   - Display models in dropdown selector
   - Allow switching models at any time
   - Handle cases where Ollama is not running or no models available

3. **Conversation Context**
   - Maintain last 3 messages (user + assistant pairs) as context
   - Send context with each request for coherent multi-turn dialogues
   - Calculate context dynamically for each request

4. **Chat History**
   - Persist all chats in browser localStorage
   - Display chat history in sidebar with titles and previews
   - Allow creating new chats and loading previous ones
   - Auto-generate chat titles from first user message (using LLM)
   - Limit to 50 stored chats to prevent storage overflow

5. **Markdown Rendering**
   - Use Marked.js library (loaded from CDN, no build required)
   - Support code blocks, tables, lists, headers, bold, italic, links
   - Style code blocks with dark background, inline code with light background
   - Parse markdown on display, store raw markdown in localStorage

6. **Optional Authentication**
   - Support optional API key authentication via environment variable
   - Display login form when API key is required
   - Store API key in browser localStorage
   - Backward compatible (works without API key if not configured)
   - All API requests include API key in headers when configured

### Technical Stack

**Backend:**
- Flask web framework (Python 3.12+)
- Ollama Python library for model interaction
- RESTful API endpoints: `/api/v1/response` (POST), `/api/v1/models` (GET)
- Environment variable configuration (PORT, DEBUG, API_KEY)
- No database (localStorage for frontend persistence)

**Frontend:**
- Vanilla JavaScript (ES6+)
- HTML5 and CSS3
- Marked.js from CDN
- Browser localStorage for chat persistence
- Single-page application (SPA) architecture

**Dependencies:**
- Python: Flask >= 3.1.2, ollama >= 0.6.0
- Dev: pytest, pytest-mock, pytest-cov
- No Node.js or npm dependencies

### User Interface

**Layout:**
- Two-column layout: sidebar (280px fixed) + main content (flexible)
- Sidebar: model selector, new chat button, chat history list
- Main content: scrollable chat container, fixed input area at bottom
- Responsive: narrow chat area on wider screens (max 800px)

**Styling:**
- Dark sidebar (#2c2c2c), light main area (#fff)
- User messages: blue header, light gray background
- Assistant messages: green header, slightly darker gray background
- Clean, modern design with proper spacing

**Interactive Elements:**
- Multi-line textarea for input (Enter to send, Shift+Enter for new line)
- Send button with loading state
- Loading indicator with animated dots
- Error pages with retry buttons
- Login form (when API key required)

### Error Handling

**Backend:**
- Catch Ollama ResponseError exceptions
- Return appropriate HTTP status codes (400, 401, 500)
- User-friendly error messages
- Validate JSON and required fields

**Frontend:**
- Display errors in chat as assistant messages
- Show error pages for Ollama connection issues
- Provide retry mechanisms
- Handle network errors gracefully
- Validate API key before requests

### Testing Requirements

- Comprehensive unit tests for all API endpoints
- Mock Ollama library (no running Ollama instance required)
- Test error handling scenarios
- Test edge cases (empty inputs, long prompts, special characters)
- Test authentication flows
- Use pytest, pytest-mock, pytest-cov
- Target > 80% test coverage

### Constraints

- Must work with Python 3.12+
- Requires Ollama installed and running
- Requires at least one model pulled in Ollama
- Browser must support localStorage and ES6+ JavaScript
- No Node.js or npm available

### Out of Scope (v1.0)

- Streaming responses (wait for complete response)
- Export chat functionality
- System prompt injection
- Theme customization
- Multi-user support
- Chat search
- Model configuration (temperature, etc.)
- Server-side storage
- User accounts

### Success Criteria

- Setup time < 5 minutes from clone to first chat
- All functional requirements implemented
- Test coverage > 80%
- Zero build tooling required
- Works with multiple Ollama models
- Chat history persists correctly
- Comprehensive error handling
- Intuitive UI

### PRD Structure Requested

Please create a comprehensive PRD document that includes:

1. **Executive Summary**: Product overview, value proposition, target users
2. **Product Goals**: Primary goals and success metrics
3. **Functional Requirements**: Detailed requirements organized by feature area (chat, models, context, history, markdown, authentication)
4. **Technical Requirements**: Technology stack, architecture, API specifications, error handling, testing
5. **User Interface Requirements**: Layout, styling, interactive elements, error states
6. **Non-Functional Requirements**: Performance, reliability, usability, security, maintainability
7. **Constraints and Assumptions**: Technical constraints and user assumptions
8. **Out of Scope**: Features not included in v1.0
9. **Success Criteria**: Definition of done and acceptance criteria
10. **Dependencies**: External and internal dependencies
11. **Risks and Mitigations**: Technical and UX risks with mitigation strategies
12. **Timeline and Milestones**: Development phases and key milestones
13. **Appendices**: Glossary and references

Format requirements:
- Use clear section numbering and hierarchical structure
- Include requirement IDs (FR-X.X, TR-X.X, UI-X.X, NFR-X.X)
- Be specific and actionable
- Include both functional and non-functional requirements
- Consider edge cases and error scenarios
- Provide clear acceptance criteria

The PRD should be detailed enough for a developer to implement the entire application without ambiguity, while remaining focused on the core goal of simplicity and zero-configuration setup.

