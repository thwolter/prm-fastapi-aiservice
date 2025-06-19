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

## Create Test User

```bash
python manage.py create_test_user [OPTIONS]
```

Creates a subject and an entitlement for a test user on OpenMeter and returns a bearer token.

**Purpose**: Set up a test user with appropriate entitlements for testing the application.

**Parameters**:
- `user_id`: Optional UUID for the user. If not provided, a random UUID will be generated.
- `user_email`: Email for the test user. (default: "test@example.com")
- `feature`: Feature key for the entitlement. (default: "tokens")
- `max_limit`: Maximum limit for the entitlement. (default: 1000)
- `period`: Period for the entitlement. (default: "MONTH")
- `expiry_minutes`: Token expiry time in minutes. (default: 24*60 = 1440 minutes/24 hours)

**Example**:
```bash
python manage.py create_test_user --user_email "tester@example.com" --max_limit 2000 --period "WEEK"
```

The command will output:
- The created user ID
- A bearer token for testing
- An example curl command using the token