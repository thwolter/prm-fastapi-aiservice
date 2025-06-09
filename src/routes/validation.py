"""Validation utilities for API models."""
from src.utils import logutils
from typing import Type

from pydantic import BaseModel, ValidationError

from src.utils.exceptions import ValidationException

logger = logutils.get_logger(__name__)


def validate_model(data, model: Type[BaseModel]) -> BaseModel:
    """
    Validate data against a Pydantic model.

    Args:
        data: The data to validate.
        model: The Pydantic model to validate against.

    Returns:
        The validated model instance.

    Raises:
        ValidationException: If validation fails.
    """
    try:
        return model(**data.model_dump())
    except ValidationError as ve:
        logger.warning(f"Validation error: {ve.errors()}")
        raise ValidationException(detail=f'Validation Error', errors=ve.errors())
