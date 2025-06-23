# Test Fixtures

This directory contains fixtures for testing the application. Fixtures are reusable pieces of test setup code that can be shared across multiple tests.

## Fixture Organization

The fixtures are organized by functionality:

- **auth.py**: Authentication-related fixtures
- **environment.py**: Environment configuration fixtures
- **local_openmeter.py**: OpenMeter fixtures for integration testing, including fixtures for token consumption testing
- **service_handler.py**: Service handler fixtures for mocking and configuring the ServiceHandler class
- **test_clients.py**: TestClient fixtures for making HTTP requests to the application

## Common Fixtures

### TestClient

The primary fixture for making HTTP requests to the application is `test_client`, which is defined in `test_clients.py`:

```python
@pytest.fixture
def test_client(auth_headers):
    """
    Create a TestClient instance with authentication headers.

    This is the primary client fixture that should be used by all tests
    that need to make HTTP requests to the application.
    """
    with TestClient(app) as client:
        client.headers.update(auth_headers)
        yield client
```

This fixture creates a TestClient instance with authentication headers, which can be used to make authenticated requests to the application.

### Authentication

The `auth_headers` fixture provides authentication headers for making authenticated requests:

```python
@pytest.fixture
def auth_headers(auth_token):
    """
    Return headers with a valid JWT token.
    """
    return {'Authorization': f'Bearer {auth_token}'}
```

### Environment

The `override_settings` fixture temporarily overrides configuration settings for tests:

```python
@pytest.fixture(autouse=True)
def override_settings(request):
    """
    Temporarily override config settings for each test.
    """
    # ...
```

## Integration Testing

For integration tests, use the `@pytest.mark.integration` marker to indicate that the test should use the actual services instead of mocks:

```python
@pytest.mark.integration
def test_something():
    # This test will use the actual services
    # ...
```

### OpenMeter Fixtures

The `local_openmeter.py` file provides fixtures for testing with a local OpenMeter instance:

- **Basic OpenMeter Fixtures**:
  - `local_openmeter_clients`: Provides sync and async clients for the local OpenMeter instance
  - `test_subject_id`: Generates a unique subject ID for testing
  - `local_meter`: Creates a meter in the local OpenMeter instance
  - `local_feature`: Creates a feature linked to the meter
  - `local_entitlement`: Creates an entitlement for the test subject
  - `local_metering_service`: Provides a MeteringService instance configured to use the local OpenMeter

- **Token Consumption Testing Fixtures**:
  - `local_metering_client`: Creates an async OpenMeter client for token testing
  - `local_meter_for_tokens`: Creates a meter specifically for token consumption testing
  - `local_feature_for_tokens`: Creates a feature for token consumption testing
  - `local_subject_for_tokens`: Creates a subject for token consumption testing
  - `local_entitlement_for_tokens`: Creates an entitlement with configurable token balance
  - `local_auth_headers`: Creates authentication headers for the test user

Example usage:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_token_consumption(local_entitlement_for_tokens, local_auth_headers):
    # Test with default token balance (10000)
    # ...

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize('local_entitlement_for_tokens', [0], indirect=True)
async def test_insufficient_tokens(local_entitlement_for_tokens, local_auth_headers):
    # Test with zero token balance
    # ...
```

## Usage Examples

### Basic Test

```python
def test_something(test_client):
    response = test_client.get('/api/some-endpoint/')
    assert response.status_code == 200
    # ...
```

### Integration Test

```python
@pytest.mark.integration
def test_something_with_real_services(test_client):
    response = test_client.get('/api/some-endpoint/')
    assert response.status_code == 200
    # ...
```

### Mocking a Service

```python
def test_something_with_mock(test_client, configure_mock_handle):
    # Configure the mock to return a specific response
    configure_mock_handle(return_value=some_response)

    response = test_client.get('/api/some-endpoint/')
    assert response.status_code == 200
    # ...
```
