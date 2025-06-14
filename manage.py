#!/usr/bin/env python
import importlib
import inspect
import pkgutil
import subprocess  # nosec
from pathlib import Path

import typer
import uvicorn

from src.core.config import settings

cmd = typer.Typer(no_args_is_help=True)


@cmd.command(name="run")
def run():
    """run application"""
    uvicorn.run(app="src.main:app", reload=True, port=8010)


@cmd.command(name="migrate")
def migrate():
    process = subprocess.Popen(
        ["alembic", "upgrade", "head"], stdout=subprocess.PIPE, shell=False
    )  # nosec
    print(process.communicate()[0])


@cmd.command(name="makemigrations")
def makemigrations(
    msg: str = typer.Option("autogenerate", "--msg", "-m", help="message"),
):
    process = subprocess.Popen(
        ["alembic", "revision", "--autogenerate", "-m", f"{msg}"],
        stdout=subprocess.PIPE,
        shell=False,
    )  # nosec
    print(process.communicate()[0])


@cmd.command(name="createuser")
def createuser():
    pass


@cmd.command(name="lint")
def lint():
    """Run ruff check --fix, ruff format, and isort on all files"""
    subprocess.run(["ruff", "check", "--fix", "."])
    subprocess.run(["ruff", "format", "."])
    subprocess.run(["isort", "."])


@cmd.command(name="list-prompts")
def list_prompts():
    """List all prompt names from services"""
    services = []
    prompt_names = []

    # Discover and import all service modules
    package_dir = Path(__file__).resolve().parent / "src" / "risk"
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        if module_name.endswith("service"):
            module = importlib.import_module(f"src.risk.{module_name}")
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.endswith("Service"):
                    services.append(obj)

    # Collect prompt names from services
    for service in services:
        if hasattr(service, "prompt_name"):
            prompt_names.append(service.prompt_name)
        if hasattr(service, "prompt_name_category") and hasattr(service, "prompt_name_categories"):
            prompt_names.append(service.prompt_name_category)
            prompt_names.append(service.prompt_name_categories)

    for prompt in prompt_names:
        print(prompt)


@cmd.command(name="create_test_token")
def create_test_token(
    user_id: str = typer.Option(
        "00000000-0000-0000-0000-000000000000",
        "--user-id",
        "-u",
        help="User ID to include in the token",
    ),
    email: str = typer.Option(
        "test@example.com", "--email", "-e", help="Email to include in the token"
    ),
    expiry_minutes: int = typer.Option(60, "--expiry", "-x", help="Token expiry time in minutes"),
):
    """
    Create a valid bearer token for testing.
    This generates a JWT token using the same parameters used for validation.
    """

    # Create token payload
    from datetime import datetime, timedelta

    import jwt

    expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expiry,
        "aud": settings.AUTH_TOKEN_AUDIENCE,
    }

    # Encode the token
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.AUTH_TOKEN_ALGORITHM,
    )

    print(f"Bearer token for testing (valid for {expiry_minutes} minutes):")
    print(f"Bearer {token}")
    print("\nFor use in curl:")
    print(f"curl -H 'Authorization: Bearer {token}' ...")


if __name__ == "__main__":
    cmd()
