"""
Wellbeing record schemas for client wellbeing support.

This module provides data validation and serialization for wellbeing records,
including treatment plans, assessment tracking, and status management for
clients requiring wellbeing support in OSINT investigations.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .entity_schema import Entity
from .task_schema import TaskResponse
from .user_schema import User
from ..core.utils import get_utc_now


class WellbeingRecordBase(BaseModel):
    treatment_plan: Optional[str] = None
    current_status: str = Field(default="Active")
    notes: Optional[str] = None


class WellbeingRecordCreate(WellbeingRecordBase):
    case_id: int
    client_entity_id: int
    assessment_date: datetime = Field(default_factory=get_utc_now)


class WellbeingRecordUpdate(BaseModel):
    treatment_plan: Optional[str] = None
    current_status: Optional[str] = None
    notes: Optional[str] = None
    assessment_date: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=get_utc_now)


class WellbeingRecordResponse(WellbeingRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    client_entity_id: int
    assessment_date: datetime
    created_at: datetime
    updated_at: datetime
    created_by_id: int

    # Relationships
    creator: Optional[User] = None


class WellbeingRecordWithDetails(WellbeingRecordResponse):
    """Wellbeing record with full entity and task details"""
    client_entity: Optional[Entity] = None
    treatment_actions: List[TaskResponse] = []


# Filter schemas
class WellbeingRecordFilter(BaseModel):
    case_id: Optional[int] = None
    client_entity_id: Optional[int] = None
    current_status: Optional[str] = None
    skip: int = 0
    limit: int = 100