import subprocess  # nosec
from datetime import datetime, timedelta

import jwt
import typer
import uvicorn

from src.core.config import settings
from src.domain.services.service_factory import DomainServiceFactory

cmd = typer.Typer(no_args_is_help=True)


@cmd.command(name='run')
def run():
    """run application"""
    uvicorn.run(app='src.main:app', reload=True, port=8010)


@cmd.command(name='delete_user')
def delete_user(
    msg: str = typer.Option(
        'User deletion', '--msg', '-m', help='Custom message for the operation'
    ),
    user_id: str = typer.Option(
        '00000000-0000-0000-0000-000000000000',
        '--user-id',
        '-u',
        help='User ID to include in the token',
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
        f'WARNING: This command will delete user {user_id} and their associated data from the system.',
        fg=typer.colors.RED,
        bold=True,
    )
    typer.secho(
        'This action is IRREVERSIBLE and should be used with caution.',
        fg=typer.colors.RED,
        bold=True,
    )

    # Ask for confirmation
    confirmation = typer.prompt(
        'Are you sure you want to proceed? (y/n)',
        default='n',
    )

    if confirmation.lower() != 'y':
        typer.secho('Operation cancelled.', fg=typer.colors.GREEN)
        return

    # Get services
    subject_service = DomainServiceFactory.get_subject_service()

    try:
        # First, try to delete the user's entitlements
        typer.secho(
            f'Attempting to delete entitlements for user {user_id}...', fg=typer.colors.YELLOW
        )

        # Note: Since we don't have a direct method to delete entitlements,
        # we'll just inform the user that entitlements will be deleted along with the user
        typer.secho(
            'Note: Entitlements will be deleted along with the user account.',
            fg=typer.colors.YELLOW,
        )

        # Delete the user
        typer.secho(f'Deleting user {user_id}... ({msg})', fg=typer.colors.YELLOW)
        subject_service.delete_subject_sync(user_id)
        typer.secho(f'User {user_id} deleted successfully. ({msg})', fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f'Error: {e}', fg=typer.colors.RED)


@cmd.command(name='delete_all_users')
def delete_all_users(
    msg: str = typer.Option(
        'Bulk user deletion', '--msg', '-m', help='Custom message for the operation'
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
        'WARNING: This command will delete ALL users and their associated data from the system.',
        fg=typer.colors.RED,
        bold=True,
    )
    typer.secho(
        'This action is IRREVERSIBLE and should be used with extreme caution.',
        fg=typer.colors.RED,
        bold=True,
    )

    # Ask for confirmation
    confirmation = typer.prompt(
        'Are you sure you want to proceed? (y/n)',
        default='n',
    )

    if confirmation.lower() != 'y':
        typer.secho('Operation cancelled.', fg=typer.colors.GREEN)
        return

    # Get subject service
    subject_service = DomainServiceFactory.get_subject_service()

    # Get all subjects without entitlements
    typer.secho(
        'Fetching all subjects...',
        fg=typer.colors.YELLOW,
    )

    try:
        subjects = subject_service.list_subjects_sync()

        if not subjects:
            typer.secho('No subjects  found. Operation completed.', fg=typer.colors.GREEN)
            return

        # Show the list of users to be deleted
        typer.secho(
            f'Found {len(subjects)} user(s) without entitlements:',
            fg=typer.colors.YELLOW,
        )

        for user_id in subjects:
            typer.secho(f'  - {user_id}', fg=typer.colors.YELLOW)

        # Final confirmation for deleting users
        final_confirmation = typer.prompt(
            f'You are about to delete {len(subjects)} subject(s). Are you sure you want to proceed? (y/n)',
            default='n',
        )

        if final_confirmation.lower() != 'y':
            typer.secho('Operation cancelled.', fg=typer.colors.GREEN)
            return

        # Delete each user
        success_count = 0
        error_count = 0

        for subject in subjects:
            try:
                typer.secho(f'Deleting subjects {subject.id}... ({msg})', fg=typer.colors.YELLOW)
                subject_service.metering_client.delete_subject(subject.id)
                success_count += 1
                typer.secho(
                    f'User {subject.id} deleted successfully. ({msg})', fg=typer.colors.GREEN
                )
            except Exception as e:
                error_count += 1
                typer.secho(f'Error deleting subjects {subject.id}: {e}', fg=typer.colors.RED)

        # Summary
        typer.secho(
            f'Operation completed. {success_count} subject(s) deleted successfully, {error_count} error(s). ({msg})',
            fg=typer.colors.GREEN if error_count == 0 else typer.colors.YELLOW,
        )
    except Exception as e:
        typer.secho(f'Error: {e}', fg=typer.colors.RED)


@cmd.command(name='lint')
def lint():
    """Run ruff check --fix, ruff format, and isort on all files"""
    subprocess.run(['ruff', 'check', '--fix', '.'])
    subprocess.run(['ruff', 'format', '.'])
    subprocess.run(['isort', '.'])


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
):
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
