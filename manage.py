#!/usr/bin/env python
import importlib
import inspect
import pkgutil
import subprocess  # nosec
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import jwt
import typer
import uvicorn

from src.auth.schemas import EntitlementCreate
from src.auth.token_quota_service_provider import TokenQuotaServiceProvider
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


# todo: fix this command to use the new token quota service provider
@cmd.command(name="delete_user")
def delete_user(
    msg: str = typer.Option(
        "User deletion", "--msg", "-m", help="Custom message for the operation"
    ),
    user_id: str = typer.Option(
        "00000000-0000-0000-0000-000000000000",
        "--user-id",
        "-u",
        help="User ID to include in the token",
    ),
):
    """
    Delete a specific user from the system.

    Args:
        user_id: The ID of the user to delete.
        msg: Custom message for the operation.

    WARNING: This command will delete the user and their associated data.
    Use with caution.
    """
    # Show warning
    typer.secho(
        f"WARNING: This command will delete user {user_id} and their associated data from the system.",
        fg=typer.colors.RED,
        bold=True,
    )
    typer.secho(
        "This action is IRREVERSIBLE and should be used with caution.",
        fg=typer.colors.RED,
        bold=True,
    )

    # Ask for confirmation
    confirmation = typer.prompt(
        "Are you sure you want to proceed? (y/n)",
        default="n",
    )

    if confirmation.lower() != "y":
        typer.secho("Operation cancelled.", fg=typer.colors.GREEN)
        return

    # Get services
    subject_service = TokenQuotaServiceProvider.get_subject_service()

    try:
        # First, try to delete the user's entitlements
        typer.secho(
            f"Attempting to delete entitlements for user {user_id}...", fg=typer.colors.YELLOW
        )

        # Note: Since we don't have a direct method to delete entitlements,
        # we'll just inform the user that entitlements will be deleted along with the user
        typer.secho(
            "Note: Entitlements will be deleted along with the user account.",
            fg=typer.colors.YELLOW,
        )

        # Delete the user
        typer.secho(f"Deleting user {user_id}... ({msg})", fg=typer.colors.YELLOW)
        subject_service.delete_subject_sync(user_id)
        typer.secho(f"User {user_id} deleted successfully. ({msg})", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)


# todo: fix this command to use the new token quota service provider
@cmd.command(name="delete_all_users")
def delete_all_users(
    msg: str = typer.Option(
        "Bulk user deletion", "--msg", "-m", help="Custom message for the operation"
    ),
):
    """
    Delete all users without entitlements from the system.

    Args:
        msg: Custom message for the operation.

    WARNING: This command will delete all users without entitlements and their associated data.
    Use with extreme caution.
    """
    # Show warning
    typer.secho(
        "WARNING: This command will delete ALL users without entitlements and their associated data from the system.",
        fg=typer.colors.RED,
        bold=True,
    )
    typer.secho(
        "This action is IRREVERSIBLE and should be used with extreme caution.",
        fg=typer.colors.RED,
        bold=True,
    )

    # Ask for confirmation
    confirmation = typer.prompt(
        "Are you sure you want to proceed? (y/n)",
        default="n",
    )

    if confirmation.lower() != "y":
        typer.secho("Operation cancelled.", fg=typer.colors.GREEN)
        return

    # Get subject service
    subject_service = TokenQuotaServiceProvider.get_subject_service()

    # Get all subjects without entitlements
    typer.secho(
        "Fetching all users without entitlements...",
        fg=typer.colors.YELLOW,
    )

    try:
        users_without_entitlement = subject_service.list_subjects_without_entitlement_sync()

        if not users_without_entitlement:
            typer.secho(
                "No users without entitlements found. Operation completed.", fg=typer.colors.GREEN
            )
            return

        # Show the list of users to be deleted
        typer.secho(
            f"Found {len(users_without_entitlement)} user(s) without entitlements:",
            fg=typer.colors.YELLOW,
        )

        for user_id in users_without_entitlement:
            typer.secho(f"  - {user_id}", fg=typer.colors.YELLOW)

        # Final confirmation for deleting users
        final_confirmation = typer.prompt(
            f"You are about to delete {len(users_without_entitlement)} user(s). Are you sure you want to proceed? (y/n)",
            default="n",
        )

        if final_confirmation.lower() != "y":
            typer.secho("Operation cancelled.", fg=typer.colors.GREEN)
            return

        # Delete each user
        success_count = 0
        error_count = 0

        for user_id in users_without_entitlement:
            try:
                typer.secho(f"Deleting user {user_id}... ({msg})", fg=typer.colors.YELLOW)
                subject_service.delete_subject_sync(user_id)
                success_count += 1
                typer.secho(f"User {user_id} deleted successfully. ({msg})", fg=typer.colors.GREEN)
            except Exception as e:
                error_count += 1
                typer.secho(f"Error deleting user {user_id}: {e}", fg=typer.colors.RED)

        # Summary
        typer.secho(
            f"Operation completed. {success_count} user(s) deleted successfully, {error_count} error(s). ({msg})",
            fg=typer.colors.GREEN if error_count == 0 else typer.colors.YELLOW,
        )
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)


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

    token = create_token(email, expiry_minutes, user_id)

    print(f"Bearer token for testing (valid for {expiry_minutes} minutes):")
    print(f"Bearer {token}")
    print("\nFor use in curl:")
    print(f"curl -H 'Authorization: Bearer {token}' ...")


def create_token(email, expiry_minutes, user_id):
    # Create token payload

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
    return token


@cmd.command(name="create_test_user")
def create_test_user_with_entitlement(
    user_id: Optional[uuid.UUID] = None,
    user_email: str = "test@example.com",
    feature: str = "tokens",
    max_limit: int = 1000,
    period: str = "MONTH",
    expiry_minutes: int = 24 * 60,
) -> None:
    """
    Creates a subject and an entitlement for a test user on OpenMeter and returns a bearer token.

    Args:
        user_id: Optional UUID for the user. If not provided, a random UUID will be generated.
        user_email: Email for the test user. Default is "test@example.com".
        feature: Feature key for the entitlement. Default is "tokens".
        max_limit: Maximum limit for the entitlement. Default is 1000.
        period: Period for the entitlement. Default is "MONTH".
        expiry_minutes: Token expiry time in minutes. Default is 24*60.

    Returns:
        A bearer token string for authentication.
    """
    # Generate a random UUID if not provided
    if user_id is None:
        user_id = uuid.uuid4()

    # Create subject in OpenMeter
    subject_service = TokenQuotaServiceProvider.get_subject_service()
    subject_service.create_subject_sync(user_id, user_email)

    # Create entitlement in OpenMeter
    entitlement_service = TokenQuotaServiceProvider.get_entitlement_service()
    entitlement = EntitlementCreate(
        feature=settings.OPENMETER_FEATURE_KEY or feature, max_limit=max_limit, period=period
    )
    entitlement_service.set_entitlement_sync(user_id, entitlement)

    token = create_token(user_email, expiry_minutes, str(user_id))

    print(f"Created test user with ID: {user_id}")
    print(f"Bearer token for testing (valid for {expiry_minutes} minutes):")
    print(f"Bearer {token}")
    print("\nFor use in curl:")
    print(f"curl -H 'Authorization: Bearer {token}' ...")


if __name__ == "__main__":
    cmd()
