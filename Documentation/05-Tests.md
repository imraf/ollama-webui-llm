# Tests

## Overview

The application includes a comprehensive test suite using pytest. All tests mock the Ollama library, so no running Ollama instance is required. The test suite covers API endpoints, authentication, error handling, edge cases, and server configuration.

## Test Structure

### Test Files

- `tests/test_server.py` - Main test file with all test cases
- `tests/conftest.py` - Shared pytest fixtures and configuration
- `tests/__init__.py` - Package initialization

### Test Fixtures

Fixtures are defined in `conftest.py`:

```11:58:tests/conftest.py
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
```

**Fixtures:**
- `client`: Flask test client with testing configuration
- `mock_ollama_chat`: Mocks `ollama.chat()` function
- `mock_ollama_list`: Mocks `ollama.list()` function
- `mock_ollama_response_error`: Mocks Ollama ResponseError exception
- `api_key`: Sets test API key and restores after test
- `api_headers`: Returns headers dict with API key

## Test Classes and Expected Results

### TestIndexRoute

Tests for the index route that serves the HTML page.

**Test Cases:**

#### test_index_route_serves_html

**Purpose:** Verify the index route serves HTML content.

**Test:**
```15:19:tests/test_server.py
    def test_index_route_serves_html(self, client):
        """Test that the index route serves index.html."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type
```

**Expected Result:**
- Status code: `200`
- Content type contains: `'text/html'`

### TestResponseEndpoint

Tests for the `/api/v1/response` POST endpoint. Contains 15+ test cases covering various scenarios.

#### test_valid_request_with_prompt_and_model

**Purpose:** Test successful response with valid prompt and model.

**Expected Result:**
- Status code: `200`
- Response contains: `{"response": "This is a test response", "model": "llama2"}`
- `ollama.chat()` called once with correct model and single message
- Message role is `'user'` with correct content

#### test_valid_request_with_context

**Purpose:** Test successful response with conversation context.

**Expected Result:**
- Status code: `200`
- Response contains expected response text
- `ollama.chat()` called with 3 messages (2 context + 1 current)
- Context messages properly formatted with roles and content

#### test_context_with_missing_fields

**Purpose:** Test context messages with missing role or content fields.

**Expected Result:**
- Status code: `200`
- Missing fields default appropriately (`role` defaults to `'user'`, `content` defaults to `''`)
- All messages still sent to Ollama

#### test_missing_prompt

**Purpose:** Test request without prompt field.

**Expected Result:**
- Status code: `400`
- Error message contains: `'prompt'` (case-insensitive)

#### test_empty_prompt

**Purpose:** Test request with empty prompt string.

**Expected Result:**
- Status code: `400`
- Error message present in response

#### test_missing_model

**Purpose:** Test request without model field.

**Expected Result:**
- Status code: `400`
- Error message contains: `'model'` (case-insensitive)

#### test_no_json_data

**Purpose:** Test request without JSON data.

**Expected Result:**
- Status code: `400`
- Error message contains: `'json'` (case-insensitive)

#### test_empty_json_body

**Purpose:** Test request with empty JSON body.

**Expected Result:**
- Status code: `400`

#### test_invalid_context_not_list

**Purpose:** Test context that is not a list (e.g., string).

**Expected Result:**
- Status code: `200`
- Context is ignored, only current prompt sent

#### test_context_with_empty_list

**Purpose:** Test context with empty list.

**Expected Result:**
- Status code: `200`
- Only current prompt sent (no context messages)

#### test_ollama_response_error

**Purpose:** Test handling of Ollama ResponseError.

**Expected Result:**
- Status code: `500`
- Error message contains: `'ollama'` (case-insensitive)

#### test_general_exception

**Purpose:** Test handling of general exceptions.

**Expected Result:**
- Status code: `500`
- Error message contains: `'server'` (case-insensitive)

#### test_multiple_context_messages

**Purpose:** Test with multiple context messages (5 messages).

**Expected Result:**
- Status code: `200`
- All 6 messages sent (5 context + 1 current)

### TestModelsEndpoint

Tests for the `/api/v1/models` GET endpoint.

#### test_get_models_success

**Purpose:** Test successful retrieval of models.

**Expected Result:**
- Status code: `200`
- Response contains: `{"models": ["llama2", "granite3.3:2b"], "count": 2}`
- All model names present in response

#### test_get_models_empty_list

**Purpose:** Test when no models are available.

**Expected Result:**
- Status code: `200`
- Response contains: `{"models": [], "count": 0}`

#### test_get_models_missing_models_key

**Purpose:** Test when Ollama response doesn't have 'models' key.

**Expected Result:**
- Status code: `200`
- Response contains: `{"models": [], "count": 0}`

#### test_get_models_ollama_response_error

**Purpose:** Test handling of Ollama ResponseError.

**Expected Result:**
- Status code: `500`
- Error message contains: `'ollama'` (case-insensitive)

#### test_get_models_general_exception

**Purpose:** Test handling of general exceptions.

**Expected Result:**
- Status code: `500`
- Error message contains: `'server'` (case-insensitive)

#### test_get_models_single_model

**Purpose:** Test with single model available.

**Expected Result:**
- Status code: `200`
- Response contains: `{"models": ["llama2"], "count": 1}`

### TestServerConfiguration

Tests for server configuration and setup.

#### test_ollama_host_constant

**Purpose:** Test that OLLAMA_HOST constant is set.

**Expected Result:**
- `OLLAMA_HOST == "http://localhost:11434"`

#### test_app_instance_exists

**Purpose:** Test that Flask app instance exists.

**Expected Result:**
- `app` is an instance of `Flask`

#### test_run_server_port_config

**Purpose:** Test that run_server reads PORT from environment.

**Expected Result:**
- `run_server` is callable
- Function exists and can be called

#### test_run_server_debug_config

**Purpose:** Test that run_server reads DEBUG from environment.

**Expected Result:**
- `run_server` is callable

### TestAuthRequiredEndpoint

Tests for the `/api/v1/auth-required` detection endpoint.

#### test_auth_required_endpoint_no_api_key

**Purpose:** Verify endpoint returns `auth_required: false` when no `API_KEY` is configured.

**Expected Result:**
- Status code: `200`
- JSON: `{ "auth_required": false }`

#### test_auth_required_endpoint_with_api_key

**Purpose:** Verify endpoint returns `auth_required: true` when `API_KEY` is set.

**Expected Result:**
- Status code: `200`
- JSON: `{ "auth_required": true }`

#### test_auth_required_endpoint_always_public

**Purpose:** Ensure endpoint never returns 401 even when other endpoints are protected.

**Expected Result:**
- Status code: `200`
- Accessible without `X-API-Key` header

### TestEdgeCases

Tests for edge cases and boundary conditions.

#### test_response_with_very_long_prompt

**Purpose:** Test handling of very long prompts (10,000 characters).

**Expected Result:**
- Status code: `200`
- Full prompt sent to Ollama unchanged

#### test_response_with_special_characters

**Purpose:** Test handling of special characters in prompt.

**Expected Result:**
- Status code: `200`
- Special characters preserved in request

#### test_response_with_unicode_characters

**Purpose:** Test handling of unicode characters.

**Expected Result:**
- Status code: `200`
- Unicode characters preserved in request

#### test_models_endpoint_http_method_not_allowed

**Purpose:** Test that POST is not allowed on `/api/v1/models`.

**Expected Result:**
- Status code: `405` (Method Not Allowed)

#### test_response_endpoint_get_not_allowed

**Purpose:** Test that GET is not allowed on `/api/v1/response`.

**Expected Result:**
- Status code: `405` (Method Not Allowed)

#### test_nonexistent_route

**Purpose:** Test accessing a nonexistent route.

**Expected Result:**
- Status code: `404` (Not Found)

#### test_response_missing_message_key

**Purpose:** Test handling when Ollama response is missing 'message' key.

**Expected Result:**
- Status code: `500`
- KeyError handled gracefully

#### test_response_missing_content_key

**Purpose:** Test handling when Ollama response message is missing 'content' key.

**Expected Result:**
- Status code: `500`
- KeyError handled gracefully

### TestApiKeyAuthentication

Tests for API key authentication. Requires `api_key` fixture (sets API_KEY).

#### test_response_endpoint_missing_api_key

**Purpose:** Test that `/api/v1/response` returns 401 without API key.

**Expected Result:**
- Status code: `401`
- Error message contains: `'api key'` (case-insensitive)

#### test_response_endpoint_invalid_api_key

**Purpose:** Test that `/api/v1/response` returns 401 with invalid API key.

**Expected Result:**
- Status code: `401`
- Error message contains: `'api key'` (case-insensitive)

#### test_models_endpoint_missing_api_key

**Purpose:** Test that `/api/v1/models` returns 401 without API key.

**Expected Result:**
- Status code: `401`
- Error message contains: `'api key'` (case-insensitive)

#### test_models_endpoint_invalid_api_key

**Purpose:** Test that `/api/v1/models` returns 401 with invalid API key.

**Expected Result:**
- Status code: `401`
- Error message contains: `'api key'` (case-insensitive)

#### test_index_route_no_auth_required

**Purpose:** Test that index route doesn't require API key.

**Expected Result:**
- Status code: `200`
- Content type contains: `'text/html'`

#### test_response_endpoint_valid_api_key

**Purpose:** Test that `/api/v1/response` works with valid API key.

**Expected Result:**
- Status code: `200`
- Request succeeds with valid key

#### test_models_endpoint_valid_api_key

**Purpose:** Test that `/api/v1/models` works with valid API key.

**Expected Result:**
- Status code: `200`
- Response contains models list

## Running Tests

### Install Test Dependencies

**With uv:**
```bash
uv sync --extra dev
```

**With pip:**
```bash
pip install pytest pytest-mock pytest-cov
```

### Run All Tests

```bash
pytest tests/test_server.py -v
```

### Run with Coverage

```bash
pytest tests/test_server.py --cov=server --cov-report=html
```

### Run Specific Test Class

```bash
pytest tests/test_server.py::TestResponseEndpoint -v
```

### Run Specific Test

```bash
pytest tests/test_server.py::TestResponseEndpoint::test_valid_request_with_prompt_and_model -v
```

## Test Coverage

The test suite includes **40+ test cases** covering (with new auth detection tests):

- **Index Route**: HTML file serving
- **Response Endpoint**: 
  - Valid requests with/without context
  - Input validation (missing fields, empty values)
  - Error handling (Ollama errors, general exceptions)
  - Edge cases (long prompts, special characters, unicode)
  - Invalid JSON and HTTP method restrictions
- **Models Endpoint**:
  - Successful model retrieval
  - Empty model lists
  - Error handling scenarios
- **API Key Authentication**:
  - Missing API key handling
  - Invalid API key handling
  - Valid API key acceptance
  - Backward compatibility (no API key set)
- **Server Configuration**: Environment variables and constants
- **Auth Detection Endpoint**: Presence, behavior with/without `API_KEY`, public accessibility
- **Edge Cases**: Boundary conditions and error paths

## Mocking Strategy

### Why Mock Ollama?

- **No External Dependencies**: Tests don't require running Ollama instance
- **Faster Execution**: No network calls or model loading
- **Deterministic**: Predictable test results
- **Isolated**: Tests focus on application logic, not Ollama behavior

### How Mocking Works

The `mock_ollama_chat` and `mock_ollama_list` fixtures use `unittest.mock.patch` to replace Ollama functions:

```20:23:tests/conftest.py
@pytest.fixture
def mock_ollama_chat():
    """Mock ollama.chat function."""
    with patch('server.ollama.chat') as mock_chat:
        yield mock_chat
```

Tests can then configure mock return values:

```27:31:tests/test_server.py
        mock_ollama_chat.return_value = {
            'message': {
                'content': 'This is a test response'
            }
        }
```

## Best Practices

### Test Organization

- Tests grouped by endpoint/feature in classes
- Descriptive test names explaining what is tested
- Each test is independent and can run in isolation

### Assertions

- Clear assertions with specific expected values
- Status codes verified explicitly
- Response structure validated
- Mock call arguments verified

### Fixtures

- Shared fixtures reduce code duplication
- Fixtures handle setup/teardown automatically
- API key fixture restores original value after test

## Related Documentation

- [Backend Setup](03-Backend-Setup.md) - Server architecture
- [API Key System](04-API-Key-System.md) - Authentication implementation
- [Error Handling](09-Error-Handling.md) - Error management patterns

