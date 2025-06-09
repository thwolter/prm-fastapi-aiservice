"""Validation utilities for API models."""
from src.utils import logutils
from typing import Type

from fastapi import HTTPException
from pydantic import BaseModel, ValidationError

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
        HTTPException: If validation fails.
    """
    try:
        return model(**data.model_dump())
    except ValidationError as ve:
        logger.warning(f"Validation error: {ve.errors()}")
        raise HTTPException(status_code=422, detail=f'Validation Error: {ve.errors()}')