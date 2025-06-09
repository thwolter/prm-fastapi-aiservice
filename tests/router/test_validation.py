"""Tests for the validation module."""
import pytest
from fastapi import HTTPException
from pydantic import BaseModel

from src.routes.validation import validate_model


class TestModel(BaseModel):
    """Test model for validation tests."""
    name: str
    age: int


class TestValidation:
    """Tests for the validation module."""

    def test_validate_model_valid(self):
        """Test that validate_model works with valid data."""
        # Create a model with valid data
        model = TestModel(name="Test", age=30)

        # Validate the model
        validated = validate_model(model, TestModel)

        # Check that the validated model is correct
        assert validated.name == "Test"
        assert validated.age == 30

    def test_validate_model_invalid(self):
        """Test that validate_model raises an HTTPException with invalid data."""
        # Create a model with invalid data
        class InvalidModel(BaseModel):
            name: str

        model = InvalidModel(name="Test")

        # Validate the model - should raise an HTTPException
        with pytest.raises(HTTPException) as excinfo:
            validate_model(model, TestModel)

        # Check that the exception has the correct status code and detail
        assert excinfo.value.status_code == 422
        assert "Validation Error" in excinfo.value.detail
