# AI Service

## Setup

1. Install Python 3.12 and create a virtual environment.
2. Install the project dependencies, for example using `pip install -e .`.
3. Copy `.env.example` to `.env` and fill in the required values (`OPENAI_API_KEY`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`, `SENTRY_DSN`, `SECRET_KEY`, `SERVICE_SECRET`, `OPENMETER_API_KEY`, `BACKEND_CORS_ORIGINS`).
4. (Optional) Copy `riskgpt.toml.example` to `riskgpt.toml` if you want to use the RiskGPT prompts locally.

## Development

Run the tests excluding webtests. Environment variables are loaded from
`.env.test` using `pytest-dotenv`:

The `.env.test` file does not include an OpenMeter API key. When running the
quota service tests you must provide `OPENMETER_API_KEY` via an external
environment variable.

```bash
pytest -m "not webtest"
```

To execute the webtests (which interact with OpenMeter's sandbox), set
`OPENMETER_SANDBOX_API_KEY` and run pytest with the `--webtest` flag:

```bash
OPENMETER_SANDBOX_API_KEY=<your_key> pytest --webtest
```

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
