# AI Service

## Setup

1. Install Python 3.12 and create a virtual environment.
2. Install dependencies using `pip install -r requirements.txt`.
3. Copy `riskgpt.toml.example` to `riskgpt.toml` and adjust the configuration values according to your environment.
4. Provide an `.env` file with the required API keys.

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

