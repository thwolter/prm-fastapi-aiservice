# AI Service

## Setup

1. Install Python 3.12 and create a virtual environment.
2. Install the project dependencies, for example using `pip install -e .`.
3. Copy `.env.example` to `.env` and fill in the required values (`OPENAI_API_KEY`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`, `SENTRY_DSN`, `SECRET_KEY`, `SERVICE_SECRET`, `OPENMETER_API_KEY`, `BACKEND_CORS_ORIGINS`).
4. (Optional) Copy `riskgpt.toml.example` to `riskgpt.toml` if you want to use the RiskGPT prompts locally.

## Development

Run the tests excluding webtests. Environment variables are loaded from
`.env.test` using `pytest-dotenv`:

```bash
pytest -m "not webtest"
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

Prompts can be defined under <https://smith.langchain.com/prompts>

### Category endpoint

Risk categories are generated via the [RiskGPT](https://pypi.org/project/riskgpt/)
library (Python 3.12+). Install it separately and provide a valid
`riskgpt.toml` configuration. Send a `CategoryRequest` to
`/api/categories/` to receive a list of categories and an optional rationale.

### Context quality endpoint

Use `/api/context/check/` with a `ContextQualityRequest` payload to analyse the
quality of a project context. The service returns a `ContextQualityResponse`
containing a quality score and rationale.

### External context endpoint

Use `/api/context/external/` with an `ExternalContextRequest` to gather relevant
external information. The endpoint returns an `ExternalContextResponse`.

### Presentation endpoint

Send a `PresentationRequest` to `/api/presentation/` to create presentation-ready
summaries. The service responds with a `PresentationResponse`.

### Risk workflow endpoint

The `/api/risk/workflow/` route executes the full risk workflow. Provide a
`RiskRequest` and receive a `RiskResponse` with references and document IDs.

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
