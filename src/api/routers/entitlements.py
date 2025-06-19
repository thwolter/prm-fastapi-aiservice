"""
API router for entitlement-related endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.dependencies import get_entitlement_service
from src.core.config import settings
from src.domain.models import Entitlement, EntitlementCreate
from src.domain.services import EntitlementService
from src.utils.exceptions import ResourceNotFoundException

router = APIRouter(prefix="/entitlements", tags=["Entitlements"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_entitlement(
    entitlement: EntitlementCreate,
    request: Request,
    subject_id: UUID = None,
    entitlement_service: EntitlementService = Depends(get_entitlement_service),
):
    """
    Create a new entitlement for a subject.
    """
    try:
        # If subject_id is provided, use it instead of the one from the request
        if subject_id:
            entitlement_service.user_id = subject_id

        await entitlement_service.set_entitlement(entitlement)
        return {"message": "Entitlement created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create entitlement: {str(e)}",
        )


@router.get("/{feature_key}", response_model=Entitlement)
async def get_entitlement(
    feature_key: str,
    request: Request,
    subject_id: UUID = None,
    entitlement_service: EntitlementService = Depends(get_entitlement_service),
):
    """
    Get an entitlement for a subject.
    """
    try:
        # If subject_id is provided, use it instead of the one from the request
        if subject_id:
            entitlement_service.user_id = subject_id

        return await entitlement_service.get_entitlement_value(feature_key)
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entitlement for feature {feature_key} not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get entitlement: {str(e)}",
        )


@router.get("/check/{feature_key}", response_model=bool)
async def check_entitlement(
    feature_key: str,
    request: Request,
    subject_id: UUID = None,
    entitlement_service: EntitlementService = Depends(get_entitlement_service),
):
    """
    Check if a subject has access to a feature.
    """
    try:
        # If subject_id is provided, use it instead of the one from the request
        if subject_id:
            entitlement_service.user_id = subject_id

        return await entitlement_service.has_access(feature_key)
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entitlement for feature {feature_key} not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check entitlement: {str(e)}",
        )


@router.get("/token-quota/status", response_model=bool)
async def get_token_quota_status(
    request: Request,
    subject_id: UUID = None,
    entitlement_service: EntitlementService = Depends(get_entitlement_service),
):
    """
    Check if a subject has access to the token quota feature.
    """
    try:
        # If subject_id is provided, use it instead of the one from the request
        if subject_id:
            entitlement_service.user_id = subject_id

        return await entitlement_service.get_token_entitlement_status(
            feature_key=settings.OPENMETER_FEATURE_KEY
        )
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token quota entitlement not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check token quota entitlement: {str(e)}",
        )
