"""
Shared pytest fixtures and configuration for the test suite.
"""
import pytest
import ollama
import os
from unittest.mock import patch
from server import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_ollama_chat():
    """Mock ollama.chat function."""
    with patch('server.ollama.chat') as mock_chat:
        yield mock_chat


@pytest.fixture
def mock_ollama_list():
    """Mock ollama.list function."""
    with patch('server.ollama.list') as mock_list:
        yield mock_list


@pytest.fixture
def mock_ollama_response_error(monkeypatch):
    """Create and patch a mock ResponseError class."""
    class MockResponseError(Exception):
        pass
    
    monkeypatch.setattr(ollama, 'ResponseError', MockResponseError)
    return MockResponseError


@pytest.fixture
def api_key(monkeypatch):
    """Set API_KEY for tests by patching server.API_KEY directly."""
    import server
    test_api_key = 'test-api-key-123'
    original_key = server.API_KEY
    server.API_KEY = test_api_key
    yield test_api_key
    # Restore original API_KEY
    server.API_KEY = original_key


@pytest.fixture
def api_headers(api_key):
    """Return headers with API key for test requests."""
    return {'X-API-Key': api_key}

