"""
Wellbeing record management service for client support.

This module handles all wellbeing record business logic including creation,
updating, and management of client wellbeing records with associated treatment
plans and actions. Provides secure operations with case access control and
integration with task system for treatment actions.
"""

from typing import List, Optional

from app import schemas
from app.core.dependencies import check_case_access
from app.core.exceptions import (
    ResourceNotFoundException,
    ValidationException,
)
from app.core.utils import get_utc_now
from app.database import models
from app.database.db_utils import transaction
from app.schemas import wellbeing_schema
from app.services.entity_service import EntityService
from app.services.task_service import TaskService
from sqlmodel import Session, select


class WellbeingService:
    def __init__(self, db: Session):
        self.db = db

    async def get_wellbeing_records(
        self,
        current_user: models.User,
        filters: wellbeing_schema.WellbeingRecordFilter = None,
    ) -> List[models.WellbeingRecord]:
        """Get wellbeing records with optional filtering"""
        if filters is None:
            filters = wellbeing_schema.WellbeingRecordFilter()

        query = select(models.WellbeingRecord)

        if filters.case_id:
            check_case_access(self.db, filters.case_id, current_user)
            query = query.where(models.WellbeingRecord.case_id == filters.case_id)

        if filters.client_entity_id:
            query = query.where(models.WellbeingRecord.client_entity_id == filters.client_entity_id)

        if filters.current_status:
            query = query.where(models.WellbeingRecord.current_status == filters.current_status)

        query = query.offset(filters.skip).limit(filters.limit)
        result = self.db.exec(query)
        records = list(result)

        # Check case access for each record if no case_id filter was provided
        if not filters.case_id:
            accessible_records = []
            for record in records:
                try:
                    check_case_access(self.db, record.case_id, current_user)
                    accessible_records.append(record)
                except:
                    continue
            return accessible_records

        return records

    async def get_wellbeing_record_with_details(
        self,
        record_id: int,
        current_user: models.User,
    ) -> wellbeing_schema.WellbeingRecordWithDetails:
        """Get a wellbeing record with full entity and treatment action details"""
        record = await self.get_wellbeing_record(record_id, current_user)

        # Get client entity details
        entity_service = EntityService(self.db)
        client_entity = await entity_service.get_entity(record.client_entity_id, current_user)

        # Get treatment actions (tasks related to this wellbeing record)
        task_service = TaskService(self.db)
        treatment_actions = await task_service.get_tasks(
            filters=schemas.TaskFilter(
                case_id=record.case_id,
                limit=1000  # Get all treatment actions for this record
            ),
            current_user=current_user
        )

        # Filter tasks that are treatment actions for this specific client
        # We can identify treatment actions by custom_fields containing wellbeing_record_id
        client_treatment_actions = [
            task for task in treatment_actions
            if (task.custom_fields and 
                task.custom_fields.get("wellbeing_record_id") == record.id and
                task.custom_fields.get("is_treatment_action") is True)
        ]

        return wellbeing_schema.WellbeingRecordWithDetails(
            **record.model_dump(),
            client_entity=schemas.Entity.model_validate(client_entity),
            treatment_actions=client_treatment_actions
        )

    async def get_wellbeing_record(
        self,
        record_id: int,
        current_user: models.User,
    ) -> models.WellbeingRecord:
        """Get a single wellbeing record"""
        record = self.db.get(models.WellbeingRecord, record_id)
        if not record:
            raise ResourceNotFoundException("Wellbeing record not found")

        check_case_access(self.db, record.case_id, current_user)
        return record

    async def create_wellbeing_record(
        self,
        wellbeing_record: wellbeing_schema.WellbeingRecordCreate,
        current_user: models.User,
    ) -> models.WellbeingRecord:
        """Create a new wellbeing record"""
        check_case_access(self.db, wellbeing_record.case_id, current_user)

        # Verify the client entity exists and is a person with is_client=True
        await self._validate_client_entity(wellbeing_record.client_entity_id, current_user)

        with transaction(self.db):
            db_record = models.WellbeingRecord(
                case_id=wellbeing_record.case_id,
                client_entity_id=wellbeing_record.client_entity_id,
                assessment_date=wellbeing_record.assessment_date,
                treatment_plan=wellbeing_record.treatment_plan,
                current_status=wellbeing_record.current_status,
                notes=wellbeing_record.notes,
                created_by_id=current_user.id,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            )

            self.db.add(db_record)

        self.db.refresh(db_record)
        return db_record

    async def update_wellbeing_record(
        self,
        record_id: int,
        wellbeing_update: wellbeing_schema.WellbeingRecordUpdate,
        current_user: models.User,
    ) -> models.WellbeingRecord:
        """Update a wellbeing record"""
        record = await self.get_wellbeing_record(record_id, current_user)

        with transaction(self.db):
            update_data = wellbeing_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if field != "updated_at":
                    setattr(record, field, value)
            
            record.updated_at = get_utc_now()
            self.db.add(record)

        self.db.refresh(record)
        return record

    async def delete_wellbeing_record(
        self,
        record_id: int,
        current_user: models.User,
    ) -> None:
        """Delete a wellbeing record"""
        record = await self.get_wellbeing_record(record_id, current_user)

        with transaction(self.db):
            self.db.delete(record)

    async def create_treatment_action(
        self,
        record_id: int,
        task_create: schemas.TaskCreate,
        current_user: models.User,
    ) -> models.Task:
        """Create a treatment action (task) for a wellbeing record"""
        record = await self.get_wellbeing_record(record_id, current_user)

        # Ensure the task is created in the same case as the wellbeing record
        if task_create.case_id != record.case_id:
            raise ValidationException("Treatment action must be in the same case as the wellbeing record")

        # Add wellbeing-specific metadata to the task
        if not task_create.custom_fields:
            task_create.custom_fields = {}
        
        task_create.custom_fields.update({
            "wellbeing_record_id": record.id,
            "is_treatment_action": True,
            "client_entity_id": record.client_entity_id
        })

        # Create the task using the task service
        task_service = TaskService(self.db)
        return await task_service.create_task(task_create, current_user)

    async def get_client_entities(
        self,
        case_id: int,
        current_user: models.User,
    ) -> List[models.Entity]:
        """Get all client entities (person entities with is_client=True) for a case"""
        check_case_access(self.db, case_id, current_user)

        entity_service = EntityService(self.db)
        all_entities = await entity_service.get_case_entities(
            case_id=case_id,
            current_user=current_user,
            entity_type="person",
            limit=1000  # Get all person entities
        )

        # Filter for client entities
        client_entities = [
            entity for entity in all_entities
            if entity.data.get("is_client") is True
        ]

        return client_entities

    async def _validate_client_entity(
        self,
        client_entity_id: int,
        current_user: models.User,
    ) -> None:
        """Validate that the entity is a person with is_client=True"""
        entity_service = EntityService(self.db)
        entity = await entity_service.get_entity(client_entity_id, current_user)

        if entity.entity_type != "person":
            raise ValidationException("Client entity must be a person entity")

        if not entity.data.get("is_client"):
            raise ValidationException("Entity must have is_client=True to be used for wellbeing records")