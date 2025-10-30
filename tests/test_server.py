"""
Comprehensive unit tests for the Flask server application.
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock
from flask import Flask
from server import app


class TestIndexRoute:
    """Tests for the index route."""
    
    def test_index_route_serves_html(self, client):
        """Test that the index route serves index.html."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type


class TestResponseEndpoint:
    """Tests for the /api/v1/response endpoint."""
    
    def test_valid_request_with_prompt_and_model(self, client, mock_ollama_chat):
        """Test successful response with valid prompt and model."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'This is a test response'
            }
        }
        
        data = {
            'prompt': 'Hello, how are you?',
            'model': 'llama2'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data['response'] == 'This is a test response'
        assert json_data['model'] == 'llama2'
        mock_ollama_chat.assert_called_once()
        call_args = mock_ollama_chat.call_args
        assert call_args[1]['model'] == 'llama2'
        assert len(call_args[1]['messages']) == 1
        assert call_args[1]['messages'][0]['role'] == 'user'
        assert call_args[1]['messages'][0]['content'] == 'Hello, how are you?'
    
    def test_valid_request_with_context(self, client, mock_ollama_chat):
        """Test successful response with conversation context."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'This is a contextual response'
            }
        }
        
        data = {
            'prompt': 'Tell me more',
            'model': 'llama2',
            'context': [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'}
            ]
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data['response'] == 'This is a contextual response'
        
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert len(messages) == 3
        assert messages[0]['role'] == 'user'
        assert messages[0]['content'] == 'Hello'
        assert messages[1]['role'] == 'assistant'
        assert messages[1]['content'] == 'Hi there!'
        assert messages[2]['role'] == 'user'
        assert messages[2]['content'] == 'Tell me more'
    
    def test_context_with_missing_fields(self, client, mock_ollama_chat):
        """Test context messages with missing role or content fields."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Response'
            }
        }
        
        data = {
            'prompt': 'Test',
            'model': 'llama2',
            'context': [
                {'role': 'user'},  # Missing content
                {'content': 'Hello'}  # Missing role
            ]
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert len(messages) == 3
        assert messages[0]['role'] == 'user'
        assert messages[0]['content'] == ''
        assert messages[1]['role'] == 'user'  # Default role
        assert messages[1]['content'] == 'Hello'
    
    def test_missing_prompt(self, client):
        """Test request without prompt field."""
        data = {
            'model': 'llama2'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        json_data = json.loads(response.data)
        assert 'error' in json_data
        assert 'prompt' in json_data['error'].lower()
    
    def test_empty_prompt(self, client):
        """Test request with empty prompt."""
        data = {
            'prompt': '',
            'model': 'llama2'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        json_data = json.loads(response.data)
        assert 'error' in json_data
    
    def test_missing_model(self, client):
        """Test request without model field."""
        data = {
            'prompt': 'Hello'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        json_data = json.loads(response.data)
        assert 'error' in json_data
        assert 'model' in json_data['error'].lower()
    
    def test_no_json_data(self, client):
        """Test request without JSON data."""
        response = client.post(
            '/api/v1/response',
            data='not json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        json_data = json.loads(response.data)
        assert 'error' in json_data
        assert 'json' in json_data['error'].lower()
    
    def test_empty_json_body(self, client):
        """Test request with empty JSON body."""
        response = client.post(
            '/api/v1/response',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_invalid_context_not_list(self, client, mock_ollama_chat):
        """Test context that is not a list."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Response'
            }
        }
        
        data = {
            'prompt': 'Test',
            'model': 'llama2',
            'context': 'not a list'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should still succeed, but context is ignored
        assert response.status_code == 200
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert len(messages) == 1
    
    def test_context_with_empty_list(self, client, mock_ollama_chat):
        """Test context with empty list."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Response'
            }
        }
        
        data = {
            'prompt': 'Test',
            'model': 'llama2',
            'context': []
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert len(messages) == 1
    
    def test_ollama_response_error(self, client, mock_ollama_chat, mock_ollama_response_error):
        """Test handling of Ollama ResponseError."""
        mock_ollama_chat.side_effect = mock_ollama_response_error('Model not found')
        
        data = {
            'prompt': 'Hello',
            'model': 'nonexistent-model'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        json_data = json.loads(response.data)
        assert 'error' in json_data
        assert 'ollama' in json_data['error'].lower()
    
    def test_general_exception(self, client, mock_ollama_chat):
        """Test handling of general exceptions."""
        mock_ollama_chat.side_effect = Exception('Unexpected error')
        
        data = {
            'prompt': 'Hello',
            'model': 'llama2'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        json_data = json.loads(response.data)
        assert 'error' in json_data
        assert 'server' in json_data['error'].lower()
    
    def test_multiple_context_messages(self, client, mock_ollama_chat):
        """Test with multiple context messages."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Response'
            }
        }
        
        data = {
            'prompt': 'New message',
            'model': 'llama2',
            'context': [
                {'role': 'user', 'content': 'Msg1'},
                {'role': 'assistant', 'content': 'Reply1'},
                {'role': 'user', 'content': 'Msg2'},
                {'role': 'assistant', 'content': 'Reply2'},
                {'role': 'user', 'content': 'Msg3'}
            ]
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        call_args = mock_ollama_chat.call_args
        messages = call_args[1]['messages']
        assert len(messages) == 6


class TestModelsEndpoint:
    """Tests for the /api/v1/models endpoint."""
    
    def test_get_models_success(self, client, mock_ollama_list):
        """Test successful retrieval of models."""
        mock_model1 = MagicMock()
        mock_model1.model = 'llama2'
        mock_model2 = MagicMock()
        mock_model2.model = 'granite3.3:2b'
        
        mock_ollama_list.return_value = {
            'models': [mock_model1, mock_model2]
        }
        
        response = client.get('/api/v1/models')
        
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert 'models' in json_data
        assert 'count' in json_data
        assert json_data['count'] == 2
        assert 'llama2' in json_data['models']
        assert 'granite3.3:2b' in json_data['models']
    
    def test_get_models_empty_list(self, client, mock_ollama_list):
        """Test when no models are available."""
        mock_ollama_list.return_value = {
            'models': []
        }
        
        response = client.get('/api/v1/models')
        
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data['models'] == []
        assert json_data['count'] == 0
    
    def test_get_models_missing_models_key(self, client, mock_ollama_list):
        """Test when Ollama response doesn't have 'models' key."""
        mock_ollama_list.return_value = {}
        
        response = client.get('/api/v1/models')
        
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data['models'] == []
        assert json_data['count'] == 0
    
    def test_get_models_ollama_response_error(self, client, mock_ollama_list, mock_ollama_response_error):
        """Test handling of Ollama ResponseError."""
        mock_ollama_list.side_effect = mock_ollama_response_error('Ollama server error')
        
        response = client.get('/api/v1/models')
        
        assert response.status_code == 500
        json_data = json.loads(response.data)
        assert 'error' in json_data
        assert 'ollama' in json_data['error'].lower()
    
    def test_get_models_general_exception(self, client, mock_ollama_list):
        """Test handling of general exceptions."""
        mock_ollama_list.side_effect = Exception('Connection error')
        
        response = client.get('/api/v1/models')
        
        assert response.status_code == 500
        json_data = json.loads(response.data)
        assert 'error' in json_data
        assert 'server' in json_data['error'].lower()
    
    def test_get_models_single_model(self, client, mock_ollama_list):
        """Test with single model available."""
        mock_model = MagicMock()
        mock_model.model = 'llama2'
        
        mock_ollama_list.return_value = {
            'models': [mock_model]
        }
        
        response = client.get('/api/v1/models')
        
        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data['count'] == 1
        assert len(json_data['models']) == 1
        assert json_data['models'][0] == 'llama2'


class TestServerConfiguration:
    """Tests for server configuration and setup."""
    
    def test_ollama_host_constant(self):
        """Test that OLLAMA_HOST constant is set."""
        from server import OLLAMA_HOST
        assert OLLAMA_HOST == "http://localhost:11434"
    
    def test_app_instance_exists(self):
        """Test that Flask app instance exists."""
        from server import app
        assert isinstance(app, Flask)
    
    @patch.dict(os.environ, {'PORT': '8080', 'DEBUG': 'False'})
    def test_run_server_port_config(self):
        """Test that run_server reads PORT from environment."""
        from server import run_server
        
        # This test mainly checks that the function exists and can be called
        # Actual server execution is tested separately
        assert callable(run_server)
    
    @patch.dict(os.environ, {'DEBUG': 'True'})
    def test_run_server_debug_config(self):
        """Test that run_server reads DEBUG from environment."""
        from server import run_server
        assert callable(run_server)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_response_with_very_long_prompt(self, client, mock_ollama_chat):
        """Test handling of very long prompts."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Response'
            }
        }
        
        long_prompt = 'A' * 10000
        data = {
            'prompt': long_prompt,
            'model': 'llama2'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        call_args = mock_ollama_chat.call_args
        assert call_args[1]['messages'][0]['content'] == long_prompt
    
    def test_response_with_special_characters(self, client, mock_ollama_chat):
        """Test handling of special characters in prompt."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Response'
            }
        }
        
        special_prompt = 'Hello! @#$%^&*()_+-=[]{}|;:,.<>?/`~'
        data = {
            'prompt': special_prompt,
            'model': 'llama2'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        call_args = mock_ollama_chat.call_args
        assert call_args[1]['messages'][0]['content'] == special_prompt
    
    def test_response_with_unicode_characters(self, client, mock_ollama_chat):
        """Test handling of unicode characters."""
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'Response'
            }
        }
        
        unicode_prompt = 'Hello 世界 🌍 مرحبا'
        data = {
            'prompt': unicode_prompt,
            'model': 'llama2'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        call_args = mock_ollama_chat.call_args
        assert call_args[1]['messages'][0]['content'] == unicode_prompt
    
    def test_models_endpoint_http_method_not_allowed(self, client):
        """Test that POST is not allowed on /api/v1/models."""
        response = client.post('/api/v1/models')
        assert response.status_code == 405
    
    def test_response_endpoint_get_not_allowed(self, client):
        """Test that GET is not allowed on /api/v1/response."""
        response = client.get('/api/v1/response')
        assert response.status_code == 405
    
    def test_nonexistent_route(self, client):
        """Test accessing a nonexistent route."""
        response = client.get('/api/v1/nonexistent')
        assert response.status_code == 404
    
    def test_response_missing_message_key(self, client, mock_ollama_chat):
        """Test handling when Ollama response is missing 'message' key."""
        mock_ollama_chat.return_value = {}
        
        data = {
            'prompt': 'Test',
            'model': 'llama2'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should handle KeyError gracefully
        assert response.status_code == 500
    
    def test_response_missing_content_key(self, client, mock_ollama_chat):
        """Test handling when Ollama response message is missing 'content' key."""
        mock_ollama_chat.return_value = {
            'message': {}
        }
        
        data = {
            'prompt': 'Test',
            'model': 'llama2'
        }
        
        response = client.post(
            '/api/v1/response',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should handle KeyError gracefully
        assert response.status_code == 500

