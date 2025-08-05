"""
Event management service for Owlculus OSINT case management.

This module handles all event-related business logic including event creation,
management, audit logging, and integration with the case management system.
Provides structured event logging for adhoc case-related activities with
comprehensive audit tracking.

Key features include:
- Event creation and management with type classification
- Audit logging for all event changes
- Case-based event organization and access control
- Event filtering and querying capabilities
- Integration with evidence and task management
"""

from datetime import datetime
from typing import List, Optional

from app.core.enums import EventStatus
from app.core.exceptions import (
    BaseException,
    ResourceNotFoundException,
    ValidationException,
)
from app.core.logging import get_security_logger
from app.database import models
from sqlmodel import Session, select


class EventService:
    def __init__(self, db: Session):
        self.db = db

    async def get_events(
        self,
        *,
        current_user: models.User,
        case_id: Optional[int] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        created_by_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[models.Event]:
        """Get events with optional filtering"""
        query = select(models.Event)
        
        if case_id:
            query = query.where(models.Event.case_id == case_id)
        if event_type:
            query = query.where(models.Event.event_type == event_type)
        if status:
            query = query.where(models.Event.status == status)
        if created_by_id:
            query = query.where(models.Event.created_by_id == created_by_id)
            
        query = query.offset(skip).limit(limit).order_by(models.Event.event_date.desc())
        
        events = self.db.exec(query).all()
        return events

    async def get_event(self, event_id: int, *, current_user: models.User) -> models.Event:
        """Get a single event by ID"""
        event = self.db.get(models.Event, event_id)
        if not event:
            raise ResourceNotFoundException(f"Event with ID {event_id} not found")
        return event

    async def create_event(
        self,
        case_id: int,
        event_data: dict,
        *,
        current_user: models.User,
    ) -> models.Event:
        """Create a new event"""
        # Verify case exists
        case = self.db.get(models.Case, case_id)
        if not case:
            raise ResourceNotFoundException(f"Case with ID {case_id} not found")

        # Set event_date to now if not provided
        if not event_data.get("event_date"):
            event_data["event_date"] = datetime.utcnow()

        # Create event
        event = models.Event(
            case_id=case_id,
            created_by_id=current_user.id,
            **event_data
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        # Create audit log entry
        await self._create_audit_log(event.id, "created", current_user.id)

        get_security_logger().info(
            f"Event created",
            extra={
                "event_id": event.id,
                "case_id": case_id,
                "user_id": current_user.id,
                "event_type": event.event_type,
            }
        )

        return event

    async def update_event(
        self,
        event_id: int,
        update_data: dict,
        *,
        current_user: models.User,
    ) -> models.Event:
        """Update an existing event"""
        event = await self.get_event(event_id, current_user=current_user)

        # Update fields
        for field, value in update_data.items():
            if hasattr(event, field):
                setattr(event, field, value)

        event.updated_at = datetime.utcnow()

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        # Create audit log entry
        await self._create_audit_log(event.id, "updated", current_user.id)

        get_security_logger().info(
            f"Event updated",
            extra={
                "event_id": event.id,
                "user_id": current_user.id,
                "updated_fields": list(update_data.keys()),
            }
        )

        return event

    async def delete_event(
        self,
        event_id: int,
        *,
        current_user: models.User,
    ) -> bool:
        """Delete an event"""
        event = await self.get_event(event_id, current_user=current_user)

        # Create audit log entry before deletion
        await self._create_audit_log(event.id, "deleted", current_user.id)

        self.db.delete(event)
        self.db.commit()

        get_security_logger().info(
            f"Event deleted",
            extra={
                "event_id": event_id,
                "user_id": current_user.id,
            }
        )

        return True

    async def get_audit_logs(
        self,
        event_id: int,
        *,
        current_user: models.User,
    ) -> List[models.EventAuditLog]:
        """Get audit logs for an event"""
        # Verify event exists
        await self.get_event(event_id, current_user=current_user)

        query = select(models.EventAuditLog).where(
            models.EventAuditLog.event_id == event_id
        ).order_by(models.EventAuditLog.changed_at.desc())

        audit_logs = self.db.exec(query).all()
        return audit_logs

    async def link_evidence(
        self,
        event_id: int,
        evidence_id: int,
        *,
        current_user: models.User,
    ) -> bool:
        """Link evidence to an event"""
        # Verify event exists
        event = await self.get_event(event_id, current_user=current_user)
        
        # Verify evidence exists and belongs to the same case
        evidence = self.db.get(models.Evidence, evidence_id)
        if not evidence:
            raise ResourceNotFoundException(f"Evidence with ID {evidence_id} not found")
        
        if evidence.case_id != event.case_id:
            raise ValidationException("Evidence and event must belong to the same case")

        # Check if link already exists
        existing_link = self.db.exec(
            select(models.EventEvidenceLink).where(
                models.EventEvidenceLink.event_id == event_id,
                models.EventEvidenceLink.evidence_id == evidence_id,
            )
        ).first()
        
        if existing_link:
            return True  # Already linked

        # Create link
        link = models.EventEvidenceLink(
            event_id=event_id,
            evidence_id=evidence_id,
            created_by_id=current_user.id,
        )

        self.db.add(link)
        self.db.commit()

        get_security_logger().info(
            f"Evidence linked to event",
            extra={
                "event_id": event_id,
                "evidence_id": evidence_id,
                "user_id": current_user.id,
            }
        )

        return True

    async def unlink_evidence(
        self,
        event_id: int,
        evidence_id: int,
        *,
        current_user: models.User,
    ) -> bool:
        """Unlink evidence from an event"""
        # Verify event exists
        await self.get_event(event_id, current_user=current_user)

        # Find and remove link
        link = self.db.exec(
            select(models.EventEvidenceLink).where(
                models.EventEvidenceLink.event_id == event_id,
                models.EventEvidenceLink.evidence_id == evidence_id,
            )
        ).first()

        if link:
            self.db.delete(link)
            self.db.commit()

            get_security_logger().info(
                f"Evidence unlinked from event",
                extra={
                    "event_id": event_id,
                    "evidence_id": evidence_id,
                    "user_id": current_user.id,
                }
            )

        return True

    async def get_linked_evidence(
        self,
        event_id: int,
        *,
        current_user: models.User,
    ) -> List[models.Evidence]:
        """Get evidence linked to an event"""
        # Verify event exists
        await self.get_event(event_id, current_user=current_user)

        # Get linked evidence
        query = (
            select(models.Evidence)
            .join(models.EventEvidenceLink)
            .where(models.EventEvidenceLink.event_id == event_id)
        )

        evidence = self.db.exec(query).all()
        return evidence

    async def create_task_from_event(
        self,
        event_id: int,
        task_data: dict,
        *,
        current_user: models.User,
    ) -> models.Task:
        """Create a task from an event"""
        event = await self.get_event(event_id, current_user=current_user)

        # Create task with event reference
        task = models.Task(
            case_id=event.case_id,
            source_event_id=event_id,
            assigned_by_id=current_user.id,
            **task_data
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        get_security_logger().info(
            f"Task created from event",
            extra={
                "event_id": event_id,
                "task_id": task.id,
                "user_id": current_user.id,
            }
        )

        return task

    async def _create_audit_log(
        self,
        event_id: int,
        action: str,
        user_id: int,
    ) -> models.EventAuditLog:
        """Create an audit log entry"""
        audit_log = models.EventAuditLog(
            event_id=event_id,
            action=action,
            changed_by_id=user_id,
        )

        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)

        return audit_log