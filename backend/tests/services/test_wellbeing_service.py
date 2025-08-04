"""
Tests for wellbeing service functionality.
"""

import pytest
from datetime import datetime
from sqlmodel import Session, select

from app.core.exceptions import ResourceNotFoundException, ValidationException
from app.database.models import Entity, WellbeingRecord
from app.schemas.entity_schema import EntityCreate, PersonData
from app.schemas.wellbeing_schema import WellbeingRecordCreate, WellbeingRecordUpdate
from app.services.entity_service import EntityService
from app.services.wellbeing_service import WellbeingService


class TestWellbeingService:
    """Test wellbeing service operations"""

    @pytest.fixture
    async def client_entity(self, session: Session, test_case, admin_user):
        """Create a client entity for testing"""
        entity_service = EntityService(session)
        
        person_data = PersonData(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            is_client=True
        )
        
        entity_create = EntityCreate(
            entity_type="person",
            data=person_data.model_dump()
        )
        
        return await entity_service.create_entity(
            case_id=test_case.id,
            entity=entity_create,
            current_user=admin_user
        )

    @pytest.fixture
    async def non_client_entity(self, session: Session, test_case, admin_user):
        """Create a non-client entity for testing"""
        entity_service = EntityService(session)
        
        person_data = PersonData(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            is_client=False
        )
        
        entity_create = EntityCreate(
            entity_type="person",
            data=person_data.model_dump()
        )
        
        return await entity_service.create_entity(
            case_id=test_case.id,
            entity=entity_create,
            current_user=admin_user
        )

    async def test_create_wellbeing_record_success(self, session: Session, test_case, admin_user, client_entity):
        """Test successful wellbeing record creation"""
        wellbeing_service = WellbeingService(session)
        
        record_create = WellbeingRecordCreate(
            case_id=test_case.id,
            client_entity_id=client_entity.id,
            treatment_plan="Weekly counseling sessions",
            current_status="Active",
            notes="Initial assessment completed"
        )
        
        record = await wellbeing_service.create_wellbeing_record(
            wellbeing_record=record_create,
            current_user=admin_user
        )
        
        assert record.id is not None
        assert record.case_id == test_case.id
        assert record.client_entity_id == client_entity.id
        assert record.treatment_plan == "Weekly counseling sessions"
        assert record.current_status == "Active"
        assert record.notes == "Initial assessment completed"
        assert record.created_by_id == admin_user.id

    async def test_create_wellbeing_record_invalid_client(self, session: Session, test_case, admin_user, non_client_entity):
        """Test wellbeing record creation with non-client entity fails"""
        wellbeing_service = WellbeingService(session)
        
        record_create = WellbeingRecordCreate(
            case_id=test_case.id,
            client_entity_id=non_client_entity.id,
            treatment_plan="Treatment plan",
            current_status="Active"
        )
        
        with pytest.raises(ValidationException, match="must have is_client=True"):
            await wellbeing_service.create_wellbeing_record(
                wellbeing_record=record_create,
                current_user=admin_user
            )

    async def test_get_wellbeing_record(self, session: Session, test_case, admin_user, client_entity):
        """Test retrieving a wellbeing record"""
        wellbeing_service = WellbeingService(session)
        
        # Create a record first
        record_create = WellbeingRecordCreate(
            case_id=test_case.id,
            client_entity_id=client_entity.id,
            treatment_plan="Treatment plan",
            current_status="Active"
        )
        
        created_record = await wellbeing_service.create_wellbeing_record(
            wellbeing_record=record_create,
            current_user=admin_user
        )
        
        # Retrieve the record
        retrieved_record = await wellbeing_service.get_wellbeing_record(
            record_id=created_record.id,
            current_user=admin_user
        )
        
        assert retrieved_record.id == created_record.id
        assert retrieved_record.case_id == test_case.id
        assert retrieved_record.client_entity_id == client_entity.id

    async def test_get_nonexistent_wellbeing_record(self, session: Session, admin_user):
        """Test retrieving non-existent wellbeing record fails"""
        wellbeing_service = WellbeingService(session)
        
        with pytest.raises(ResourceNotFoundException, match="Wellbeing record not found"):
            await wellbeing_service.get_wellbeing_record(
                record_id=99999,
                current_user=admin_user
            )

    async def test_update_wellbeing_record(self, session: Session, test_case, admin_user, client_entity):
        """Test updating a wellbeing record"""
        wellbeing_service = WellbeingService(session)
        
        # Create a record first
        record_create = WellbeingRecordCreate(
            case_id=test_case.id,
            client_entity_id=client_entity.id,
            treatment_plan="Initial plan",
            current_status="Active"
        )
        
        created_record = await wellbeing_service.create_wellbeing_record(
            wellbeing_record=record_create,
            current_user=admin_user
        )
        
        # Update the record
        record_update = WellbeingRecordUpdate(
            treatment_plan="Updated treatment plan",
            current_status="On Hold",
            notes="Updated notes"
        )
        
        updated_record = await wellbeing_service.update_wellbeing_record(
            record_id=created_record.id,
            wellbeing_update=record_update,
            current_user=admin_user
        )
        
        assert updated_record.treatment_plan == "Updated treatment plan"
        assert updated_record.current_status == "On Hold"
        assert updated_record.notes == "Updated notes"
        assert updated_record.updated_at > created_record.updated_at

    async def test_get_client_entities(self, session: Session, test_case, admin_user, client_entity, non_client_entity):
        """Test getting client entities for a case"""
        wellbeing_service = WellbeingService(session)
        
        client_entities = await wellbeing_service.get_client_entities(
            case_id=test_case.id,
            current_user=admin_user
        )
        
        # Should only return the client entity, not the non-client entity
        assert len(client_entities) == 1
        assert client_entities[0].id == client_entity.id
        assert client_entities[0].data["is_client"] is True

    async def test_delete_wellbeing_record(self, session: Session, test_case, admin_user, client_entity):
        """Test deleting a wellbeing record"""
        wellbeing_service = WellbeingService(session)
        
        # Create a record first
        record_create = WellbeingRecordCreate(
            case_id=test_case.id,
            client_entity_id=client_entity.id,
            treatment_plan="Treatment plan",
            current_status="Active"
        )
        
        created_record = await wellbeing_service.create_wellbeing_record(
            wellbeing_record=record_create,
            current_user=admin_user
        )
        
        # Delete the record
        await wellbeing_service.delete_wellbeing_record(
            record_id=created_record.id,
            current_user=admin_user
        )
        
        # Verify it's gone
        with pytest.raises(ResourceNotFoundException):
            await wellbeing_service.get_wellbeing_record(
                record_id=created_record.id,
                current_user=admin_user
            )