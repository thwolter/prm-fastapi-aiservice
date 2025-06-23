# AI Service

## Setup

1. Install Python 3.12 and create a virtual environment.
2. Install the project dependencies, for example using `pip install -e .`.
3. Copy `.env.example` to `.env` and fill in the required values (`OPENAI_API_KEY`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`, `SENTRY_DSN`, `SECRET_KEY`, `SERVICE_SECRET`, `OPENMETER_API_KEY`, `BACKEND_CORS_ORIGINS`).
4. (Optional) Copy `riskgpt.toml.example` to `riskgpt.toml` if you want to use the RiskGPT prompts locally.

Testing
Local OpenMeter Instance
Some tests require a local OpenMeter instance. To set up a local OpenMeter instance:

Clone the OpenMeter repository:

git clone git@github.com:openmeterio/openmeter.git
cd openmeter/quickstart
Launch OpenMeter and its dependencies:

docker compose up -d
The local OpenMeter instance will be available at http://localhost:8888. This URL is already configured in the .env file.

No bearer token is required for the local instance and the `OPENMETER_API_KEY`
environment variable can be omitted when running tests locally.

Running Tests
poetry run pytest
To run only the integration tests:

poetry run pytest -m integration

### Local OpenMeter Testing

For integration tests that require OpenMeter, we provide a set of fixtures that connect to the local OpenMeter instance:

#### Basic OpenMeter Fixtures:
- `local_openmeter_clients`: Provides sync and async clients configured for the local instance
- `test_subject_id`: Generates a unique subject ID for testing
- `local_meter`: Creates a meter in the local OpenMeter instance
- `local_feature`: Creates a feature linked to the meter
- `local_entitlement`: Creates an entitlement for the test subject with an initial balance of 1000 tokens
- `local_metering_service`: Provides a MeteringService instance configured to use the local OpenMeter instance

#### Token Consumption Testing Fixtures:
- `local_metering_client`: Creates an async OpenMeter client for token testing
- `local_meter_for_tokens`: Creates a meter specifically for token consumption testing
- `local_feature_for_tokens`: Creates a feature for token consumption testing
- `local_subject_for_tokens`: Creates a subject for token consumption testing
- `local_entitlement_for_tokens`: Creates an entitlement with configurable token balance
- `local_auth_headers`: Creates authentication headers for the test user

To use these fixtures in your tests, mark them with `@pytest.mark.integration`:

```python
# Basic usage
@pytest.mark.integration
@pytest.mark.asyncio
async def test_token_consumption(local_metering_service, test_subject_id):
    # Check entitlement
    entitlement = await local_metering_service.check_entitlement(uuid.UUID(test_subject_id))
    assert entitlement["has_access"] is True

    # Your test code here

# Token consumption testing with default token balance (10000)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_with_tokens(local_entitlement_for_tokens, local_auth_headers):
    # Test with sufficient tokens
    # ...

# Token consumption testing with zero token balance
@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize('local_entitlement_for_tokens', [0], indirect=True)
async def test_without_tokens(local_entitlement_for_tokens, local_auth_headers):
    # Test with insufficient tokens
    # ...
```

See `tests/e2e/test_risk_definition_check_token_consumption.py` for complete examples.


### Testing APIs without Protection

In the local environment (`ENVIRONMENT=local` in `.env`), API authentication and metering protections are automatically disabled. This allows you to test the APIs without needing to provide authentication tokens or worrying about token quota limitations.

This feature is:
- Only enabled in the local environment
- Automatically disabled in staging and production environments
- Indicated by a warning log message at application startup

To use this feature:
1. Ensure your `.env` file has `ENVIRONMENT=local` (this is the default for local development)
2. Start the application normally
3. Make API requests without authentication tokens

### OpenMeter Integration Test

The `tests/e2e/test_risk_definition_check_token_consumption.py` module exercises a local
OpenMeter instance for token consumption testing. It verifies that a test subject with
sufficient tokens can access the risk definition check endpoint, while a subject with
insufficient tokens is rejected. The tests demonstrate how token consumption affects
the balance and access permissions. Ensure the local instance is running
and that the connection details match the values in `.env` before running
the tests.

## Authentication

In staging and production environments you must provide a valid JSON Web Token in the request headers. The API expects the following format:

```http
Authorization: Bearer <jwt>
```

The [`TokenExtractionMiddleware`](docs/authentication.md) extracts and validates this token. When `ENVIRONMENT=local`, the middleware injects dummy credentials so you can call the API without a token.

## Documentation

The project documentation is built with MkDocs and can be found in the `docs` directory. To view the documentation locally, run:

```bash
mkdocs serve
```

Then open http://127.0.0.1:8000/ in your browser.

The documentation includes:
- General information about the AI Service
- Detailed explanation of how services and routes are defined, discovered, and registered
- A comprehensive list of improvement tasks for the project
