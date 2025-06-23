#!/usr/bin/env python3
import subprocess  # nosec
from datetime import datetime, timedelta

import jwt
import typer
import uvicorn

from src.core.config import settings

cmd = typer.Typer(no_args_is_help=True)


@cmd.command(name='run')
def run() -> None:
    """run application"""
    uvicorn.run(app='src.main:app', reload=True, port=8010)


@cmd.command(name='lint')
def lint() -> None:
    """Run ruff check --fix, ruff format, and isort on all files"""
    subprocess.run(['ruff', 'check', '--fix', '.'])
    subprocess.run(['ruff', 'format', '.'])
    subprocess.run(['isort', '.'])
    subprocess.run(['mypy', '.'])


@cmd.command(name='create_token')
def create_token(
    user_id: str = typer.Option(
        '00000000-0000-0000-0000-000000000000',
        '--user-id',
        '-u',
        help='User ID to include in the token',
    ),
    email: str = typer.Option(
        'test@example.com', '--email', '-e', help='Email to include in the token'
    ),
    expiry_minutes: int = typer.Option(60, '--expiry', '-x', help='Token expiry time in minutes'),
) -> None:
    """
    Create a valid bearer token for testing.
    This generates a JWT token using the same parameters used for validation.
    """

    expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    payload = {
        'sub': user_id,
        'email': email,
        'exp': expiry,
        'aud': settings.AUTH_TOKEN_AUDIENCE,
    }
    # Encode the token
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.AUTH_TOKEN_ALGORITHM,
    )

    print(f'Bearer token for testing (valid for {expiry_minutes} minutes):')
    print(f'Bearer {token}')
    print('\nFor use in curl:')
    print(f"curl -H 'Authorization: Bearer {token}' ...")


if __name__ == '__main__':
    cmd()
