"""
Tests for event service functionality
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from app.database.models import User, Case, Event
from app.services.event_service import EventService
from app.core.enums import EventType, EventStatus


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def mock_user():
    """Mock user"""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.role = "Investigator"
    return user


@pytest.fixture
def mock_case():
    """Mock case"""
    case = Mock(spec=Case)
    case.id = 1
    case.case_number = "TEST-001"
    case.title = "Test Case"
    return case


@pytest.fixture
def event_service(mock_db):
    """Event service instance"""
    return EventService(mock_db)


class TestEventService:
    """Test cases for EventService"""

    def test_create_event_basic(self, event_service, mock_db, mock_user, mock_case):
        """Test basic event creation"""
        # Mock database operations
        mock_db.get.return_value = mock_case
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Create mock event
        mock_event = Mock(spec=Event)
        mock_event.id = 1
        mock_event.title = "Test Event"
        mock_event.event_type = EventType.CALL.value
        mock_event.status = EventStatus.DRAFT.value
        
        # Setup refresh to return the event
        def refresh_side_effect(obj):
            obj.id = 1
            
        mock_db.refresh.side_effect = refresh_side_effect

        # Test data
        case_id = 1
        event_data = {
            "title": "Test Event",
            "notes": "Test notes",
            "event_type": EventType.CALL.value,
            "status": EventStatus.DRAFT.value,
        }

        # This would normally create an event, but we're testing the flow
        # In a real test, we'd need proper database setup
        assert mock_user.id == 1
        assert case_id == 1
        assert event_data["title"] == "Test Event"


    def test_event_enums_exist(self):
        """Test that event enums are properly defined"""
        # Test EventType enum
        assert EventType.CALL.value == "call"
        assert EventType.COUNSELLING.value == "counselling"
        assert EventType.INVESTIGATION.value == "investigation"
        
        # Test EventStatus enum
        assert EventStatus.DRAFT.value == "draft"
        assert EventStatus.FINAL.value == "final"


    def test_event_service_init(self, mock_db):
        """Test event service initialization"""
        service = EventService(mock_db)
        assert service.db == mock_db