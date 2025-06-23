from contextlib import contextmanager
from typing import Iterator
from uuid import UUID

from azure.core.exceptions import ResourceNotFoundError

from src.utils import logutils
from src.utils.exceptions import ResourceNotFoundException

logger = logutils.get_logger(__name__)


@contextmanager
def handle_resource_not_found(user_id: UUID) -> Iterator[None]:
    try:
        yield
    except ResourceNotFoundError as e:
        logger.error(f'Subject {user_id}: {e}')
        raise ResourceNotFoundException(detail='Subject not found')
