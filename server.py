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
        "context": [] (optional list of previous messages)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        prompt = data.get('prompt')
        model = data.get('model')
        context_messages = data.get('context', [])
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' field"}), 400
        
        if not model:
            return jsonify({"error": "Missing 'model' field"}), 400
        
        # Build messages array with context
        messages = []
        
        # Add context messages (last 3 messages from conversation history)
        if context_messages and isinstance(context_messages, list):
            for msg in context_messages:
                messages.append({
                    'role': msg.get('role', 'user'),
                    'content': msg.get('content', '')
                })
        
        # Add current user prompt
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        # Query Ollama with full conversation context
        response = ollama.chat(
            model=model,
            messages=messages
        )
        
        return jsonify({
            "response": response['message']['content'],
            "model": model
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
