# LLM Chatbot Web UI

A minimalistic, lightweight web interface for chatting with local LLM models via Ollama. Built with Python and Flask for extremely easy setup without requiring Node.js or complex build tools.

![Screenshot](readme-media/screenshot.jpg)

## Overview

This project provides a clean, mobile-inspired chat interface for interacting with your local Ollama models. The entire application is built with pure Python (Flask backend) and vanilla JavaScript (frontend), making it incredibly simple to set up and run. No npm, webpack, or other JavaScript build tools required!

## Features

### 🤖 **Chat with Local Models**
Interact with any Ollama model installed on your system through a clean, intuitive chat interface.

![Chat Interface](readme-media/anim-chat-main.gif)

### 🎯 **Model Selection**
Easily switch between different models with a dropdown selector that automatically populates with your available Ollama models.

![Model Selection](readme-media/anim-model-select.gif)

### 💬 **Contextual Conversations**
The chatbot maintains conversation context by sending the last 3 messages with each new prompt, enabling coherent multi-turn conversations.

![Chat Context](readme-media/anim-chat-context.gif)

### 📚 **Chat History**
Save and load previous conversations. All chats are stored in your browser's local storage and can be accessed anytime.

![Previous Chats](readme-media/anim-previous-chats.gif)

### ✨ **Additional Features**
- **Auto-generated Titles**: Conversations are automatically titled based on the first message
- **Markdown Support**: Responses are rendered with full markdown support including code blocks, tables, and lists
- **Clean UI**: Minimalistic design inspired by modern chat applications
- **Responsive Layout**: Adapts to both desktop and mobile screens
- **No Database Required**: Uses browser local storage for chat history

## Prerequisites

- **Python 3.12+** (recommended)
- **Ollama** installed and running on your system
- **uv** (Python package manager) - optional but recommended

## Installation

### Installing Ollama

If you haven't installed Ollama yet, follow the official installation guide:

👉 [Ollama Installation Documentation](https://ollama.ai/download)

After installation, make sure Ollama is running:
```bash
ollama serve
```

You should also have at least one model installed. For example:
```bash
ollama pull llama2
ollama pull granite3.3:2b
```

### Setting Up the Project

#### **Option 1: Using uv (Recommended)**

1. **Install uv** if you haven't already:
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone or download this repository**:
   ```bash
   git clone <repository-url>
   cd ollama-webui-llm
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Run the server**:
   ```bash
   uv run python server.py
   ```

#### **Option 2: Using pip**

1. **Clone or download this repository**:
   ```bash
   git clone <repository-url>
   cd ollama-webui-llm
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # Or if using pyproject.toml:
   pip install -e .
   ```

4. **Run the server**:
   ```bash
   python server.py
   ```

## Usage

1. **Start the server** (if not already running):
   ```bash
   # With uv
   uv run python server.py
   
   # Or with standard Python
   python server.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Select a model** from the dropdown in the left sidebar

4. **Start chatting!** Type your message and press Enter or click Send

## Configuration

The server can be configured using environment variables:

- `PORT`: Server port (default: 5000)
  ```bash
  PORT=8080 python server.py
  ```

- `DEBUG`: Enable/disable debug mode (default: True)
  ```bash
  DEBUG=False python server.py
  ```

- Ollama is expected to run on `http://localhost:11434` (default Ollama port)

## API Endpoints

The application exposes the following REST API endpoints:

### `POST /api/v1/response`
Send a prompt to an Ollama model and receive a response.

**Request body:**
```json
{
  "prompt": "Your question here",
  "model": "llama2",
  "context": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ]
}
```

**Response:**
```json
{
  "response": "Model's response",
  "model": "llama2"
}
```

### `GET /api/v1/models`
Get a list of available Ollama models.

**Response:**
```json
{
  "models": ["llama2", "granite3.3:2b", "..."],
  "count": 2
}
```

**Response:**
```json
{
  "summary": "Conversation summary",
  "model": "granite3.3:2b"
}
```

## Project Structure

```
ollama-webui-llm/
├── server.py              # Flask backend server
├── static/
│   ├── index.html        # Main HTML page
│   ├── style.css         # Stylesheet
│   └── app.js            # Frontend JavaScript
├── pyproject.toml        # Python project configuration
└── README.md             # This file
```

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check that Ollama is accessible at `http://localhost:11434`
- Verify you have models installed: `ollama list`

### No Models Available
- Install a model: `ollama pull llama2`
- Restart the server after installing new models

### Port Already in Use
- Change the port: `PORT=8080 python server.py`
- Or stop the process using port 5000

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Powered by [Ollama](https://ollama.ai/)