"""
Event-related Pydantic schemas for request/response validation

Key features include:
- Event creation and management for adhoc case-related events
- Event type management with predefined categories (Call, Counselling, Investigation)
- Event status tracking and audit logging
- Integration with case management system
- Evidence and task linking capabilities
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .user_schema import User
from ..core.enums import EventType, EventStatus


# Event Schemas
class EventBase(BaseModel):
    title: str
    notes: Optional[str] = None
    event_type: str = EventType.CALL.value
    status: str = EventStatus.DRAFT.value
    event_date: Optional[datetime] = None


class EventCreate(EventBase):
    case_id: int


class EventUpdate(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    event_type: Optional[str] = None
    status: Optional[str] = None
    event_date: Optional[datetime] = None


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: int

    # Relationships
    creator: User


class EventAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    action: str
    changed_by_id: int
    changed_at: datetime

    # Relationships
    changed_by: User


# Filter schemas
class EventFilter(BaseModel):
    case_id: Optional[int] = None
    event_type: Optional[str] = None
    status: Optional[str] = None
    created_by_id: Optional[int] = None
    skip: int = 0
    limit: int = 100