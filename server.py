from flask import Flask, request, jsonify, send_from_directory
import ollama
import os

app = Flask(__name__)

# Ollama configuration
OLLAMA_HOST = "http://localhost:11434"


@app.route('/')
def index():
    """Serve the main HTML page (to be created later)"""
    return send_from_directory('static', 'index.html')


@app.route('/api/v1/response', methods=['POST'])
def get_response():
    """
    Query Ollama with a user prompt and return the response.
    Expected JSON body:
    {
        "prompt": "user prompt text",
        "model": "model name",
        "context": "optional context" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        prompt = data.get('prompt')
        model = data.get('model')
        context = data.get('context', '')
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' field"}), 400
        
        if not model:
            return jsonify({"error": "Missing 'model' field"}), 400
        
        # Build the full prompt with context if provided
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        # Query Ollama
        response = ollama.chat(
            model=model,
            messages=[
                {
                    'role': 'user',
                    'content': full_prompt
                }
            ]
        )
        
        return jsonify({
            "response": response['message']['content'],
            "model": model
        }), 200
        
    except ollama.ResponseError as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/v1/compact', methods=['POST'])
def compact_messages():
    """
    Summarize a list of previous messages using Granite 3.2 8b model.
    Expected JSON body:
    {
        "messages": [
            {"role": "user", "content": "message 1"},
            {"role": "assistant", "content": "response 1"},
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        messages = data.get('messages')
        
        if not messages:
            return jsonify({"error": "Missing 'messages' field"}), 400
        
        if not isinstance(messages, list):
            return jsonify({"error": "'messages' must be a list"}), 400
        
        # Format the conversation history
        conversation_text = ""
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            conversation_text += f"{role.capitalize()}: {content}\n\n"
        
        # Create summarization prompt
        summarization_prompt = f"""Please provide a concise summary of the following conversation. 
Focus on the key points, questions asked, and answers provided.

Conversation:
{conversation_text}

Summary:"""
        
        # Query Ollama with Granite 3.2 8b model
        response = ollama.chat(
            model='granite3.2:8b',
            messages=[
                {
                    'role': 'user',
                    'content': summarization_prompt
                }
            ]
        )
        
        return jsonify({
            "summary": response['message']['content'],
            "model": "granite3.2:8b"
        }), 200
        
    except ollama.ResponseError as e:
        return jsonify({"error": f"Ollama error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/v1/models', methods=['GET'])
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


def run_server():
    """Run the Flask development server"""
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Flask server on http://localhost:{port}")
    print(f"Ollama host: {OLLAMA_HOST}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == "__main__":
    run_server()
