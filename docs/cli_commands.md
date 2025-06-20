# CLI Commands

This document describes the command-line interface (CLI) commands available in the `manage.py` script.

## Run

```bash
python manage.py run
```

Runs the application using Uvicorn server with hot reload enabled.

**Purpose**: Start the development server for the AI service.

**Parameters**: None

**Example**:
```bash
python manage.py run
```

## Lint

```bash
python manage.py lint
```

Runs code quality tools on all files in the project.

**Purpose**: Ensure code quality and consistency by running linting and formatting tools.

**Parameters**: None

**Details**:
- Runs `ruff check --fix` to check and automatically fix issues
- Runs `ruff format` to format code according to project standards
- Runs `isort` to sort imports

**Example**:
```bash
python manage.py lint
```

## Create Test Token

```bash
python manage.py create_test_token [OPTIONS]
```

Creates a valid bearer token for testing purposes.

**Purpose**: Generate a JWT token using the same parameters used for validation in the application.

**Parameters**:
- `--user-id, -u`: User ID to include in the token (default: "00000000-0000-0000-0000-000000000000")
- `--email, -e`: Email to include in the token (default: "test@example.com")
- `--expiry, -x`: Token expiry time in minutes (default: 60)

**Example**:
```bash
python manage.py create_test_token --user-id "123e4567-e89b-12d3-a456-426614174000" --email "user@example.com" --expiry 120
```
