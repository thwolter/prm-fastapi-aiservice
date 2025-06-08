# AI Service

## Setup

1. Install Python 3.12 and create a virtual environment.
2. Install the project dependencies, for example using `pip install -e .`.
3. Copy `.env.example` to `.env` and fill in the required values (`OPENAI_API_KEY`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`, `SENTRY_DSN`, `SECRET_KEY`, `OPENMETER_API_KEY`).
4. (Optional) Copy `riskgpt.toml.example` to `riskgpt.toml` if you want to use the RiskGPT prompts locally.

## Development

Run the tests excluding webtests. Environment variables are loaded from
`.env.test` using `pytest-dotenv`:

```bash
pytest -m "not webtest"
```

Prompts can be defined under <https://smith.langchain.com/prompts>

### Category endpoint

Risk categories are generated via the [RiskGPT](https://pypi.org/project/riskgpt/)
library (Python 3.12+). Install it separately and provide a valid
`riskgpt.toml` configuration. Send a `CategoryRequest` to
`/api/categories/` to receive a list of categories and an optional rationale.

