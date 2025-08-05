"""
Wellbeing API endpoints for client wellbeing support management.

This module provides REST API endpoints for managing client wellbeing records,
treatment plans, and treatment actions. Integrates with the case management
system to provide comprehensive client support functionality.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user, get_db, no_analyst
from ..core.exceptions import ResourceNotFoundException, ValidationException
from ..database.models import User
from ..schemas import wellbeing_schema, task_schema
from ..services.wellbeing_service import WellbeingService

router = APIRouter(tags=["wellbeing"])


@router.get("/records", response_model=List[wellbeing_schema.WellbeingRecordResponse])
@no_analyst()
async def get_wellbeing_records(
    case_id: Optional[int] = None,
    current_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get wellbeing records with optional filtering"""
    try:
        wellbeing_service = WellbeingService(db)
        
        filters = wellbeing_schema.WellbeingRecordFilter(
            case_id=case_id,
            current_status=current_status,
            skip=skip,
            limit=limit
        )
        
        records = await wellbeing_service.get_wellbeing_records(
            current_user=current_user,
            filters=filters
        )
        
        return [wellbeing_schema.WellbeingRecordResponse.model_validate(record) for record in records]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve wellbeing records: {str(e)}"
        )


@router.get("/records/{record_id}", response_model=wellbeing_schema.WellbeingRecordWithDetails)
@no_analyst()
async def get_wellbeing_record_details(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a wellbeing record with full details including client entity and treatment actions"""
    try:
        wellbeing_service = WellbeingService(db)
        return await wellbeing_service.get_wellbeing_record_with_details(
            record_id=record_id,
            current_user=current_user
        )
        
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve wellbeing record: {str(e)}"
        )


@router.post("/records", response_model=wellbeing_schema.WellbeingRecordResponse)
@no_analyst()
async def create_wellbeing_record(
    wellbeing_record: wellbeing_schema.WellbeingRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new wellbeing record"""
    try:
        wellbeing_service = WellbeingService(db)
        record = await wellbeing_service.create_wellbeing_record(
            wellbeing_record=wellbeing_record,
            current_user=current_user
        )
        
        return wellbeing_schema.WellbeingRecordResponse.model_validate(record)
        
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create wellbeing record: {str(e)}"
        )


@router.put("/records/{record_id}", response_model=wellbeing_schema.WellbeingRecordResponse)
@no_analyst()
async def update_wellbeing_record(
    record_id: int,
    wellbeing_update: wellbeing_schema.WellbeingRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a wellbeing record"""
    try:
        wellbeing_service = WellbeingService(db)
        record = await wellbeing_service.update_wellbeing_record(
            record_id=record_id,
            wellbeing_update=wellbeing_update,
            current_user=current_user
        )
        
        return wellbeing_schema.WellbeingRecordResponse.model_validate(record)
        
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update wellbeing record: {str(e)}"
        )


@router.delete("/records/{record_id}")
@no_analyst()
async def delete_wellbeing_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a wellbeing record"""
    try:
        wellbeing_service = WellbeingService(db)
        await wellbeing_service.delete_wellbeing_record(
            record_id=record_id,
            current_user=current_user
        )
        
        return {"message": "Wellbeing record deleted successfully"}
        
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete wellbeing record: {str(e)}"
        )


@router.post("/records/{record_id}/treatment-actions", response_model=task_schema.TaskResponse)
@no_analyst()
async def create_treatment_action(
    record_id: int,
    task_create: task_schema.TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a treatment action (task) for a wellbeing record"""
    try:
        wellbeing_service = WellbeingService(db)
        task = await wellbeing_service.create_treatment_action(
            record_id=record_id,
            task_create=task_create,
            current_user=current_user
        )
        
        return task_schema.TaskResponse.model_validate(task)
        
    except (ResourceNotFoundException, ValidationException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create treatment action: {str(e)}"
        )


@router.get("/cases/{case_id}/client-entities")
@no_analyst()
async def get_case_client_entities(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all client entities for a case"""
    try:
        wellbeing_service = WellbeingService(db)
        client_entities = await wellbeing_service.get_client_entities(
            case_id=case_id,
            current_user=current_user
        )
        
        return [
            {
                "id": entity.id,
                "entity_type": entity.entity_type,
                "data": entity.data,
                "created_at": entity.created_at,
                "updated_at": entity.updated_at
            }
            for entity in client_entities
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve client entities: {str(e)}"
        )