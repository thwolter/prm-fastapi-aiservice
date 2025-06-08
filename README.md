# AI Service

## Setup

1. Install Python 3.12 and create a virtual environment.
2. Install dependencies using `pip install -r requirements.txt`.
3. Copy `riskgpt.toml.example` to `riskgpt.toml` and adjust the configuration values according to your environment.
4. Provide an `.env` file with the required API keys.

## Development

Run the tests excluding webtests:

```bash
pytest -m "not webtest"
```

Prompts can be defined under <https://smith.langchain.com/prompts>

