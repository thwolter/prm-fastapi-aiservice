"""
API router for subject-related endpoints.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.dependencies import get_subject_service
from src.domain.models import Subject
from src.domain.services import SubjectService
from src.utils.exceptions import ResourceNotFoundException

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject: Subject,
    request: Request,
    subject_service: SubjectService = Depends(get_subject_service),
):
    """
    Create a new subject.
    """
    try:
        await subject_service.create_subject(subject.id, subject.email)
        return {"message": "Subject created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subject: {str(e)}",
        )


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: UUID, subject_service: SubjectService = Depends(get_subject_service)
):
    """
    Delete a subject.
    """
    try:
        await subject_service.delete_subject(subject_id)
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete subject: {str(e)}",
        )


@router.get("/", response_model=List[dict])
async def list_subjects(
    subject_service: SubjectService = Depends(get_subject_service),
):
    """
    List all subjects.
    """
    try:
        return await subject_service.list_subjects()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list subjects: {str(e)}",
        )


@router.get("/without-entitlement", response_model=List[UUID])
async def list_subjects_without_entitlement(
    subject_service: SubjectService = Depends(get_subject_service),
):
    """
    List all subjects without an entitlement.
    """
    try:
        return await subject_service.list_subjects_without_entitlement()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list subjects without entitlement: {str(e)}",
        )
