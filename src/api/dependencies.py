"""
Dependencies for FastAPI.
"""

from uuid import UUID

from src.services.metering_service import MeteringService


def get_metering_service() -> MeteringService:
    """
    Get a MeteringService instance.

    Returns:
        A MeteringService instance.
    """
    return MeteringService()


# For testing purposes
_test_request = None


def setup_for_testing(test_user_id: UUID) -> None:
    """
    Set up the dependencies for testing with a test user ID.

    Args:
        test_user_id: The test user ID to use.
    """
    global _test_request
    # Create a mock request with the test user ID
    from fastapi import Request

    _test_request = Request(
        scope={
            'type': 'http',
            'method': 'POST',
            'path': '/test',
            'headers': [(b'accept', b'application/json')],
            'state': {
                'token': 'test_token',
                'user_id': test_user_id,
            },
        }
    )
