# Product Requirements Document (PRD)
## LLM Chatbot Web UI

**Version:** 1.0  
**Date:** Initial Planning Phase  
**Status:** Planning

---

## 1. Executive Summary

### 1.1 Product Overview
A minimal, lightweight web-based chat interface for interacting with locally running Large Language Models (LLMs) served through Ollama. The application prioritizes simplicity, zero-configuration setup, and a frictionless user experience.

### 1.2 Value Proposition
- **Zero Build Tooling**: No Node.js, bundlers, or transpilers required
- **Python-Only Stack**: Backend and dependencies managed entirely through Python
- **Instant Setup**: Clone, install dependencies, run, chat
- **Local-First**: Complete privacy with models running on user's machine
- **Mobile-Inspired UI**: Clean, modern interface optimized for readability

### 1.3 Target Users
- Developers experimenting with local LLMs
- Users wanting privacy-focused AI interactions
- Python developers preferring Python-only tooling
- Users seeking simple, distraction-free chat interfaces

---

## 2. Product Goals

### 2.1 Primary Goals
1. Provide a clean, intuitive web interface for Ollama models
2. Minimize setup complexity and external dependencies
3. Enable seamless multi-turn conversations with context awareness
4. Support multiple model selection and switching
5. Persist chat history across sessions

### 2.2 Success Metrics
- Setup time: < 5 minutes from clone to first chat
- First response time: < 3 seconds (model-dependent)
- Zero build errors or configuration complexity
- 100% local operation (no external API calls)
- Chat history persistence rate: 100%

---

## 3. Functional Requirements

### 3.1 Core Chat Functionality

#### 3.1.1 Message Exchange
- **FR-1.1**: Users must be able to send text prompts to selected models
- **FR-1.2**: The system must display model responses in real-time
- **FR-1.3**: User messages must be displayed as plain text
- **FR-1.4**: Assistant messages must be rendered as markdown with proper formatting
- **FR-1.5**: The interface must support multi-line input (Shift+Enter for new line, Enter to send)

#### 3.1.2 Response Handling
- **FR-1.6**: System must show loading indicator while waiting for model response
- **FR-1.7**: System must handle response errors gracefully with user-friendly messages
- **FR-1.8**: System must prevent concurrent requests (disable send button during processing)

### 3.2 Model Management

#### 3.2.1 Model Discovery
- **FR-2.1**: System must dynamically load available models from Ollama on startup
- **FR-2.2**: System must display models in a dropdown selector
- **FR-2.3**: System must handle cases where no models are available
- **FR-2.4**: System must handle cases where Ollama is not running

#### 3.2.2 Model Selection
- **FR-2.5**: Users must be able to switch models at any time
- **FR-2.6**: Selected model must be used for subsequent requests
- **FR-2.7**: Model selection must persist per chat session
- **FR-2.8**: System must validate model availability before sending requests

### 3.3 Conversation Context

#### 3.3.1 Context Management
- **FR-3.1**: System must maintain conversation context for coherent multi-turn dialogues
- **FR-3.2**: System must send last 3 messages (user + assistant pairs) as context
- **FR-3.3**: Context must be calculated dynamically for each request
- **FR-3.4**: First message in a conversation must have no context

#### 3.3.2 Context Format
- **FR-3.5**: Context messages must include role (user/assistant) and content
- **FR-3.6**: System must handle missing or invalid context gracefully
- **FR-3.7**: Context must not exceed 3 messages to maintain performance

### 3.4 Chat History

#### 3.4.1 History Persistence
- **FR-4.1**: System must persist all chats in browser localStorage
- **FR-4.2**: Chats must survive page reloads and browser restarts
- **FR-4.3**: System must limit stored chats to 50 to prevent storage overflow
- **FR-4.4**: System must automatically save chats after each message exchange

#### 3.4.2 Chat Management
- **FR-4.5**: Users must be able to create new chats
- **FR-4.6**: Users must be able to load previous chats from history
- **FR-4.7**: System must display chat titles and previews in sidebar
- **FR-4.8**: System must highlight currently active chat
- **FR-4.9**: Users must be able to delete chats (optional - future enhancement)

#### 3.4.3 Chat Titles
- **FR-4.10**: System must auto-generate chat titles from first user message
- **FR-4.11**: Title generation must use LLM to create concise titles (max 6 words)
- **FR-4.12**: System must fallback to truncated first message if title generation fails
- **FR-4.13**: Titles must be limited to 50 characters with ellipsis

### 3.5 Markdown Rendering

#### 3.5.1 Rendering Requirements
- **FR-5.1**: System must render assistant messages as markdown
- **FR-5.2**: System must support code blocks with syntax highlighting indicators
- **FR-5.3**: System must support tables, lists, headers, and other markdown elements
- **FR-5.4**: Code blocks must have distinct styling (dark background)
- **FR-5.5**: Inline code must have distinct styling (light background)

#### 3.5.2 Markdown Library
- **FR-5.6**: System must use Marked.js library for markdown parsing
- **FR-5.7**: Library must be loaded from CDN (no local build required)
- **FR-5.8**: Markdown must be parsed on display, not stored as HTML

### 3.6 Authentication (Optional)

#### 3.6.1 API Key System
- **FR-6.1**: System must support optional API key authentication
- **FR-6.2**: Authentication must be backward compatible (works without API key)
- **FR-6.3**: API key must be configurable via environment variable
- **FR-6.4**: System must display login form when API key is required

#### 3.6.2 Authentication Flow
- **FR-6.5**: Users must enter API key in login form
- **FR-6.6**: System must validate API key before granting access
- **FR-6.7**: API key must be stored in browser localStorage
- **FR-6.8**: System must handle expired or invalid API keys gracefully
- **FR-6.9**: All API requests must include API key in headers when configured

---

## 4. Technical Requirements

### 4.1 Technology Stack

#### 4.1.1 Backend
- **TR-1.1**: Flask web framework (Python 3.12+)
- **TR-1.2**: Ollama Python library for model interaction
- **TR-1.3**: No external database required (localStorage for frontend)
- **TR-1.4**: Standard library and minimal dependencies only

#### 4.1.2 Frontend
- **TR-2.1**: Vanilla JavaScript (no frameworks)
- **TR-2.2**: HTML5 and CSS3
- **TR-2.3**: Marked.js loaded from CDN
- **TR-2.4**: Browser localStorage for persistence
- **TR-2.5**: No build tools, transpilers, or bundlers

#### 4.1.3 Dependencies
- **TR-3.1**: Python dependencies: Flask >= 3.1.2, ollama >= 0.6.0
- **TR-3.2**: Development dependencies: pytest, pytest-mock, pytest-cov
- **TR-3.3**: No Node.js or npm dependencies

### 4.2 Architecture

#### 4.2.1 Server Architecture
- **TR-4.1**: Single Flask application file (`server.py`)
- **TR-4.2**: RESTful API endpoints: `/api/v1/response`, `/api/v1/models`
- **TR-4.3**: Static file serving from `static/` directory
- **TR-4.4**: Environment variable configuration (PORT, DEBUG, API_KEY)

#### 4.2.2 Client Architecture
- **TR-5.1**: Single-page application (SPA) architecture
- **TR-5.2**: State management via JavaScript variables
- **TR-5.3**: Event-driven UI updates
- **TR-5.4**: No routing library required

#### 4.2.3 Data Flow
- **TR-6.1**: Client → Flask API → Ollama → Flask API → Client
- **TR-6.2**: Context messages sent with each request
- **TR-6.3**: Full chat history stored client-side only
- **TR-6.4**: No server-side session or state management

### 4.3 API Specifications

#### 4.3.1 POST /api/v1/response
- **TR-7.1**: Accept JSON body with `prompt`, `model`, and optional `context`
- **TR-7.2**: Return JSON with `response` and `model` fields
- **TR-7.3**: Validate required fields (prompt, model)
- **TR-7.4**: Handle errors with appropriate HTTP status codes
- **TR-7.5**: Support API key authentication via `X-API-Key` header

#### 4.3.2 GET /api/v1/models
- **TR-8.1**: Return JSON with `models` array and `count`
- **TR-8.2**: Query Ollama for available models
- **TR-8.3**: Handle Ollama connection errors gracefully
- **TR-8.4**: Support API key authentication via `X-API-Key` header

### 4.4 Error Handling

#### 4.4.1 Backend Error Handling
- **TR-9.1**: Catch and handle Ollama ResponseError exceptions
- **TR-9.2**: Return appropriate HTTP status codes (400, 401, 500)
- **TR-9.3**: Provide user-friendly error messages
- **TR-9.4**: Handle invalid JSON and missing fields

#### 4.4.2 Frontend Error Handling
- **TR-10.1**: Display user-friendly error messages in chat
- **TR-10.2**: Show error pages for Ollama connection issues
- **TR-10.3**: Provide retry mechanisms for recoverable errors
- **TR-10.4**: Handle network errors gracefully
- **TR-10.5**: Validate API key before requests

### 4.5 Testing Requirements

#### 4.5.1 Test Coverage
- **TR-11.1**: Comprehensive unit tests for all API endpoints
- **TR-11.2**: Mock Ollama library to avoid external dependencies
- **TR-11.3**: Test error handling scenarios
- **TR-11.4**: Test edge cases (empty inputs, long prompts, special characters)
- **TR-11.5**: Test authentication flows

#### 4.5.2 Test Framework
- **TR-12.1**: Use pytest for test execution
- **TR-12.2**: Use pytest-mock for mocking
- **TR-12.3**: Use pytest-cov for coverage reporting
- **TR-12.4**: All tests must run without running Ollama instance

---

## 5. User Interface Requirements

### 5.1 Layout

#### 5.1.1 Overall Structure
- **UI-1.1**: Two-column layout: sidebar (280px) + main content (flexible)
- **UI-1.2**: Sidebar contains model selector, new chat button, and chat history
- **UI-1.3**: Main content contains chat messages and input area
- **UI-1.4**: Responsive design (narrow chat area on wider screens, max 800px)

#### 5.1.2 Sidebar
- **UI-2.1**: Dark theme (#2c2c2c background)
- **UI-2.2**: Model dropdown selector at top
- **UI-2.3**: "New Chat" button prominently displayed
- **UI-2.4**: Chat history list with titles and previews
- **UI-2.5**: Active chat highlighted

#### 5.1.3 Main Content
- **UI-3.1**: Light theme (#fff background)
- **UI-3.2**: Scrollable chat container
- **UI-3.3**: Fixed input area at bottom
- **UI-3.4**: Welcome message when no messages present

### 5.2 Message Display

#### 5.2.1 Message Styling
- **UI-4.1**: User messages: blue header, light gray background
- **UI-4.2**: Assistant messages: green header, slightly darker gray background
- **UI-4.3**: Clear visual distinction between user and assistant messages
- **UI-4.4**: Proper spacing and padding for readability

#### 5.2.2 Markdown Rendering
- **UI-5.1**: Code blocks with dark background (#1e1e1e)
- **UI-5.2**: Inline code with light background (#e8e8e8)
- **UI-5.3**: Tables with borders and header highlighting
- **UI-5.4**: Lists with proper indentation
- **UI-5.5**: Headers with appropriate sizing

### 5.3 Interactive Elements

#### 5.3.1 Input Area
- **UI-6.1**: Multi-line textarea for message input
- **UI-6.2**: Send button with disabled state during loading
- **UI-6.3**: Placeholder text when chat unavailable
- **UI-6.4**: Focus state styling

#### 5.3.2 Loading States
- **UI-7.1**: Animated loading indicator with dots
- **UI-7.2**: "Thinking..." text during response wait
- **UI-7.3**: Disabled send button during processing

#### 5.3.3 Error States
- **UI-8.1**: Error page for Ollama connection issues
- **UI-8.2**: Inline error messages in chat
- **UI-8.3**: Retry buttons for recoverable errors
- **UI-8.4**: Clear instructions for fixing errors

### 5.4 Login Interface

#### 5.4.1 Login Form
- **UI-9.1**: Centered login form on dedicated page
- **UI-9.2**: Password-style input for API key
- **UI-9.3**: Error message display area
- **UI-9.4**: Loading state on submit button
- **UI-9.5**: Clean, minimal design

---

## 6. Non-Functional Requirements

### 6.1 Performance

#### 6.1.1 Response Time
- **NFR-1.1**: API endpoint response time < 100ms (excluding Ollama processing)
- **NFR-1.2**: UI updates must be immediate (< 50ms)
- **NFR-1.3**: Chat history loading < 200ms

#### 6.1.2 Resource Usage
- **NFR-2.1**: Minimal memory footprint (< 50MB for Flask server)
- **NFR-2.2**: No unnecessary dependencies
- **NFR-2.3**: Efficient localStorage usage

### 6.2 Reliability

#### 6.2.1 Error Recovery
- **NFR-3.1**: System must gracefully handle Ollama disconnections
- **NFR-3.2**: System must recover from network errors
- **NFR-3.3**: No data loss on errors

#### 6.2.2 Data Persistence
- **NFR-4.1**: Chat history must persist across sessions
- **NFR-4.2**: Handle localStorage quota errors gracefully
- **NFR-4.3**: Prevent data corruption

### 6.3 Usability

#### 6.3.1 User Experience
- **NFR-5.1**: Intuitive interface requiring no documentation
- **NFR-5.2**: Clear error messages with actionable steps
- **NFR-5.3**: Responsive to user actions (< 100ms feedback)

#### 6.3.2 Accessibility
- **NFR-6.1**: Keyboard navigation support (Enter to send)
- **NFR-6.2**: Clear visual hierarchy
- **NFR-6.3**: Readable fonts and contrast ratios

### 6.4 Security

#### 6.4.1 Authentication
- **NFR-7.1**: API key authentication optional but secure when enabled
- **NFR-7.2**: API keys not exposed in logs or error messages
- **NFR-7.3**: Secure storage in browser localStorage

#### 6.4.2 Input Validation
- **NFR-8.1**: Validate all user inputs on backend
- **NFR-8.2**: Sanitize markdown output to prevent XSS
- **NFR-8.3**: Handle malicious or malformed inputs gracefully

### 6.5 Maintainability

#### 6.5.1 Code Quality
- **NFR-9.1**: Clean, readable code with minimal comments
- **NFR-9.2**: Follow Python and JavaScript best practices
- **NFR-9.3**: Comprehensive test coverage (> 80%)

#### 6.5.2 Documentation
- **NFR-10.1**: Clear README with setup instructions
- **NFR-10.2**: API documentation in code comments
- **NFR-10.3**: Testing documentation

---

## 7. Constraints and Assumptions

### 7.1 Constraints
- **C-1**: Must work with Python 3.12+
- **C-2**: Requires Ollama to be installed and running
- **C-3**: Requires at least one model pulled in Ollama
- **C-4**: Browser must support localStorage
- **C-5**: Browser must support ES6+ JavaScript
- **C-6**: No Node.js or npm available

### 7.2 Assumptions
- **A-1**: Users have basic knowledge of Python and command line
- **A-2**: Users have Ollama installed and configured
- **A-3**: Users access application from modern browsers
- **A-4**: Local Ollama instance is accessible at localhost:11434
- **A-5**: Users understand API key concept (if authentication enabled)

---

## 8. Out of Scope (v1.0)

### 8.1 Features Not Included
- Streaming responses (responses wait for completion)
- Export chat functionality (JSON/Markdown export)
- System prompt injection
- Theme customization (dark/light toggle)
- Multi-user support
- Chat search functionality
- Model configuration (temperature, top-p, etc.)
- Conversation summarization
- Full conversation history (beyond 3 messages)
- Server-side storage
- User accounts and authentication

### 8.2 Future Considerations
- Streaming responses for better UX
- Export functionality for chat backup
- Optional system prompts
- Theme customization
- Enhanced model parameters

---

## 9. Success Criteria

### 9.1 Definition of Done
- [ ] All functional requirements implemented
- [ ] All technical requirements met
- [ ] Test coverage > 80%
- [ ] Documentation complete
- [ ] Zero build tooling required
- [ ] Setup time < 5 minutes
- [ ] Works with multiple Ollama models
- [ ] Chat history persists correctly
- [ ] Error handling comprehensive
- [ ] UI is responsive and intuitive

### 9.2 Acceptance Criteria
- User can clone repository and run application in < 5 minutes
- User can select model and send first message successfully
- User can have multi-turn conversation with context
- User can create new chat and switch between chats
- User can reload page and see previous chats
- Application handles errors gracefully
- Application works without API key (backward compatible)
- Application works with API key (when configured)

---

## 10. Dependencies

### 10.1 External Dependencies
- Ollama (user-installed)
- Python 3.12+
- Modern web browser

### 10.2 Internal Dependencies
- Flask >= 3.1.2
- ollama >= 0.6.0
- pytest, pytest-mock, pytest-cov (dev)

---

## 11. Risks and Mitigations

### 11.1 Technical Risks
- **Risk**: Ollama connection failures
  - **Mitigation**: Comprehensive error handling and retry mechanisms
- **Risk**: localStorage quota exceeded
  - **Mitigation**: Limit to 50 chats, handle errors gracefully
- **Risk**: Model response timeouts
  - **Mitigation**: Clear loading indicators, error messages

### 11.2 User Experience Risks
- **Risk**: Complex setup process
  - **Mitigation**: Clear documentation, minimal dependencies
- **Risk**: Confusion about context management
  - **Mitigation**: Transparent behavior, no user configuration needed

---

## 12. Timeline and Milestones

### 12.1 Development Phases
1. **Phase 1**: Core chat functionality (message send/receive)
2. **Phase 2**: Model selection and context management
3. **Phase 3**: Chat history and persistence
4. **Phase 4**: UI polish and error handling
5. **Phase 5**: Authentication (optional feature)
6. **Phase 6**: Testing and documentation

### 12.2 Key Milestones
- M1: Basic chat working with Ollama
- M2: Model selection implemented
- M3: Context management working
- M4: Chat history persistence
- M5: UI complete and polished
- M6: Tests comprehensive
- M7: Documentation complete

---

## Appendix A: Glossary

- **LLM**: Large Language Model
- **Ollama**: Local LLM serving framework
- **Context**: Previous messages sent with each request
- **localStorage**: Browser storage API for client-side persistence
- **API Key**: Authentication token for securing endpoints
- **Markdown**: Lightweight markup language for formatting text

---

## Appendix B: References

- Ollama Documentation: https://ollama.ai/
- Flask Documentation: https://flask.palletsprojects.com/
- Marked.js Documentation: https://marked.js.org/
- Python 3.12 Documentation: https://docs.python.org/3.12/

---

**Document Status**: Approved for Development  
**Next Review**: After MVP completion

