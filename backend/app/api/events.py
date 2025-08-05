"""
Event Management API for Owlculus OSINT Platform.

This module provides comprehensive event management capabilities for OSINT investigations,
enabling structured logging of adhoc case-related events and activities.

Key features include:
- Event creation and management with type classification
- Audit logging for complete event history tracking
- Case-integrated event tracking with proper access controls
- Event filtering and querying for comprehensive case review
- Integration with evidence and task management systems
"""

from typing import List

from app import schemas
from app.core.dependencies import (
    check_case_access,
    get_current_user,
)
from app.core.exceptions import (
    AuthorizationException,
    BaseException,
    ResourceNotFoundException,
    ValidationException,
)
from app.database.connection import get_db
from app.database.models import User
from app.services.event_service import EventService
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlmodel import Session

router = APIRouter()


@router.get("/", response_model=List[schemas.EventResponse])
async def list_events(
    filters: schemas.EventFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EventService(db)
    if filters.case_id:
        try:
            check_case_access(db, filters.case_id, current_user)
        except AuthorizationException:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this case",
            )
        except ResourceNotFoundException as e:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e)
            )

    try:
        events = await service.get_events(
            current_user=current_user,
            case_id=filters.case_id,
            event_type=filters.event_type,
            status=filters.status,
            created_by_id=filters.created_by_id,
            skip=filters.skip,
            limit=filters.limit,
        )
        return events
    except BaseException as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/", response_model=schemas.EventResponse)
async def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check case access
    try:
        check_case_access(db, event.case_id, current_user)
    except AuthorizationException:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this case",
        )
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e)
        )

    service = EventService(db)
    try:
        return await service.create_event(
            case_id=event.case_id,
            event_data=event.model_dump(exclude={"case_id"}),
            current_user=current_user,
        )
    except BaseException as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{event_id}", response_model=schemas.EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EventService(db)
    try:
        event = await service.get_event(event_id, current_user=current_user)
        try:
            check_case_access(db, event.case_id, current_user)
        except AuthorizationException:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this case",
            )
        except ResourceNotFoundException as e:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e)
            )
        return event
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))
    except BaseException as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/{event_id}", response_model=schemas.EventResponse)
async def update_event(
    event_id: int,
    updates: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EventService(db)
    try:
        event = await service.get_event(event_id, current_user=current_user)
        check_case_access(db, event.case_id, current_user)
    except AuthorizationException:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this case",
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))

    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    try:
        return await service.update_event(
            event_id, update_data, current_user=current_user
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))
    except BaseException as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EventService(db)
    try:
        event = await service.get_event(event_id, current_user=current_user)
        check_case_access(db, event.case_id, current_user)
    except AuthorizationException:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this case",
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        success = await service.delete_event(event_id, current_user=current_user)
        if success:
            return {"message": "Event deleted successfully"}
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))
    except BaseException as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{event_id}/audit-logs", response_model=List[schemas.EventAuditLogResponse])
async def get_event_audit_logs(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EventService(db)
    try:
        event = await service.get_event(event_id, current_user=current_user)
        check_case_access(db, event.case_id, current_user)
    except AuthorizationException:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this case",
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        audit_logs = await service.get_audit_logs(event_id, current_user=current_user)
        return audit_logs
    except BaseException as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/{event_id}/evidence/{evidence_id}")
async def link_evidence_to_event(
    event_id: int,
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EventService(db)
    try:
        event = await service.get_event(event_id, current_user=current_user)
        check_case_access(db, event.case_id, current_user)
    except AuthorizationException:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this case",
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        success = await service.link_evidence(
            event_id, evidence_id, current_user=current_user
        )
        if success:
            return {"message": "Evidence linked to event successfully"}
    except BaseException as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{event_id}/evidence/{evidence_id}")
async def unlink_evidence_from_event(
    event_id: int,
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EventService(db)
    try:
        event = await service.get_event(event_id, current_user=current_user)
        check_case_access(db, event.case_id, current_user)
    except AuthorizationException:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this case",
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        success = await service.unlink_evidence(
            event_id, evidence_id, current_user=current_user
        )
        if success:
            return {"message": "Evidence unlinked from event successfully"}
    except BaseException as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{event_id}/evidence", response_model=List[schemas.Evidence])
async def get_event_linked_evidence(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EventService(db)
    try:
        event = await service.get_event(event_id, current_user=current_user)
        check_case_access(db, event.case_id, current_user)
    except AuthorizationException:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this case",
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        evidence = await service.get_linked_evidence(event_id, current_user=current_user)
        return evidence
    except BaseException as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/{event_id}/create-task", response_model=schemas.TaskResponse)
async def create_task_from_event(
    event_id: int,
    task_data: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EventService(db)
    try:
        event = await service.get_event(event_id, current_user=current_user)
        check_case_access(db, event.case_id, current_user)
    except AuthorizationException:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this case",
        )
    except ResourceNotFoundException as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        task = await service.create_task_from_event(
            event_id, task_data.model_dump(), current_user=current_user
        )
        return task
    except BaseException as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )