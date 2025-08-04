"""
Wellbeing plugin for client wellbeing support management.

This plugin provides comprehensive wellbeing record management for clients,
including assessment tracking, treatment plan management, and treatment action
coordination. Integrates with the existing task system to provide seamless
case management for client wellbeing support.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional

from app.core.dependencies import get_db
from app.database import models
from app.plugins.base_plugin import BasePlugin
from app.schemas import wellbeing_schema
from app.services.wellbeing_service import WellbeingService
from sqlalchemy.orm import Session


class WellbeingPlugin(BasePlugin):
    """Plugin for managing client wellbeing records and treatment plans"""

    def __init__(self, display_name: Optional[str] = None, db_session: Optional[Session] = None):
        super().__init__(display_name or "Wellbeing Support", db_session)
        self.description = "Manage client wellbeing records, treatment plans, and treatment actions"
        self.category = "Wellbeing"
        self.evidence_category = "Other"
        self.save_to_case = False  # This plugin manages data, doesn't produce evidence
        
        # Define plugin parameters
        self.parameters = {
            "action": {
                "type": "select",
                "description": "Action to perform",
                "options": [
                    {"value": "list_records", "label": "List Wellbeing Records"},
                    {"value": "create_record", "label": "Create Wellbeing Record"},
                    {"value": "update_record", "label": "Update Wellbeing Record"},
                    {"value": "get_client_entities", "label": "Get Client Entities"},
                    {"value": "create_treatment_action", "label": "Create Treatment Action"}
                ],
                "required": True
            },
            "case_id": {
                "type": "number",
                "description": "Case ID for wellbeing operations",
                "required": True
            },
            "record_id": {
                "type": "number",
                "description": "Wellbeing record ID (required for update and treatment action creation)",
                "required": False
            },
            "client_entity_id": {
                "type": "number",
                "description": "Client entity ID (required for record creation)",
                "required": False
            },
            "treatment_plan": {
                "type": "text",
                "description": "Treatment plan details",
                "required": False
            },
            "current_status": {
                "type": "select",
                "description": "Current status of wellbeing record",
                "options": [
                    {"value": "Active", "label": "Active"},
                    {"value": "On Hold", "label": "On Hold"},
                    {"value": "Completed", "label": "Completed"},
                    {"value": "Discontinued", "label": "Discontinued"}
                ],
                "default": "Active",
                "required": False
            },
            "notes": {
                "type": "text",
                "description": "Additional notes about the wellbeing record",
                "required": False
            },
            "task_title": {
                "type": "string",
                "description": "Title for treatment action task",
                "required": False
            },
            "task_description": {
                "type": "text",
                "description": "Description for treatment action task",
                "required": False
            },
            "task_priority": {
                "type": "select",
                "description": "Priority for treatment action task",
                "options": [
                    {"value": "Low", "label": "Low"},
                    {"value": "Medium", "label": "Medium"},
                    {"value": "High", "label": "High"},
                    {"value": "Critical", "label": "Critical"}
                ],
                "default": "Medium",
                "required": False
            },
            "assigned_to_id": {
                "type": "number",
                "description": "User ID to assign treatment action to",
                "required": False
            }
        }

    def parse_output(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse plugin output (not used for this management plugin)"""
        return None

    async def run(
        self, params: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute wellbeing plugin operations"""
        if not params:
            yield {"error": "No parameters provided"}
            return

        action = params.get("action")
        if not action:
            yield {"error": "Action parameter is required"}
            return

        case_id = params.get("case_id")
        if not case_id:
            yield {"error": "Case ID is required"}
            return

        # Use injected session if available, otherwise get a new one
        if self._db_session:
            db = self._db_session
            close_session = False
        else:
            db = next(get_db())
            close_session = True

        try:
            wellbeing_service = WellbeingService(db)

            if action == "list_records":
                async for result in self._list_records(wellbeing_service, params):
                    yield result
            elif action == "create_record":
                async for result in self._create_record(wellbeing_service, params):
                    yield result
            elif action == "update_record":
                async for result in self._update_record(wellbeing_service, params):
                    yield result
            elif action == "get_client_entities":
                async for result in self._get_client_entities(wellbeing_service, params):
                    yield result
            elif action == "create_treatment_action":
                async for result in self._create_treatment_action(wellbeing_service, params):
                    yield result
            else:
                yield {"error": f"Unknown action: {action}"}

        except Exception as e:
            yield {"error": f"Plugin execution error: {str(e)}"}
        finally:
            if close_session:
                db.close()

    async def _list_records(
        self, 
        wellbeing_service: WellbeingService, 
        params: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """List wellbeing records"""
        try:
            filters = wellbeing_schema.WellbeingRecordFilter(
                case_id=params.get("case_id"),
                current_status=params.get("current_status"),
                skip=params.get("skip", 0),
                limit=params.get("limit", 100)
            )

            records = await wellbeing_service.get_wellbeing_records(
                current_user=self._current_user,
                filters=filters
            )

            yield {
                "type": "info",
                "message": f"Found {len(records)} wellbeing records"
            }

            for record in records:
                yield {
                    "type": "data",
                    "data": {
                        "record_id": record.id,
                        "client_entity_id": record.client_entity_id,
                        "assessment_date": record.assessment_date.isoformat(),
                        "treatment_plan": record.treatment_plan,
                        "current_status": record.current_status,
                        "notes": record.notes,
                        "created_at": record.created_at.isoformat(),
                        "updated_at": record.updated_at.isoformat()
                    }
                }

        except Exception as e:
            yield {"error": f"Failed to list records: {str(e)}"}

    async def _create_record(
        self, 
        wellbeing_service: WellbeingService, 
        params: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Create a wellbeing record"""
        try:
            client_entity_id = params.get("client_entity_id")
            if not client_entity_id:
                yield {"error": "Client entity ID is required for record creation"}
                return

            record_create = wellbeing_schema.WellbeingRecordCreate(
                case_id=params["case_id"],
                client_entity_id=client_entity_id,
                treatment_plan=params.get("treatment_plan"),
                current_status=params.get("current_status", "Active"),
                notes=params.get("notes")
            )

            record = await wellbeing_service.create_wellbeing_record(
                wellbeing_record=record_create,
                current_user=self._current_user
            )

            yield {
                "type": "success",
                "message": f"Created wellbeing record {record.id}",
                "data": {
                    "record_id": record.id,
                    "client_entity_id": record.client_entity_id,
                    "current_status": record.current_status
                }
            }

        except Exception as e:
            yield {"error": f"Failed to create record: {str(e)}"}

    async def _update_record(
        self, 
        wellbeing_service: WellbeingService, 
        params: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Update a wellbeing record"""
        try:
            record_id = params.get("record_id")
            if not record_id:
                yield {"error": "Record ID is required for updates"}
                return

            update_data = {}
            if "treatment_plan" in params:
                update_data["treatment_plan"] = params["treatment_plan"]
            if "current_status" in params:
                update_data["current_status"] = params["current_status"]
            if "notes" in params:
                update_data["notes"] = params["notes"]

            if not update_data:
                yield {"error": "No update data provided"}
                return

            record_update = wellbeing_schema.WellbeingRecordUpdate(**update_data)

            record = await wellbeing_service.update_wellbeing_record(
                record_id=record_id,
                wellbeing_update=record_update,
                current_user=self._current_user
            )

            yield {
                "type": "success",
                "message": f"Updated wellbeing record {record.id}",
                "data": {
                    "record_id": record.id,
                    "current_status": record.current_status,
                    "updated_at": record.updated_at.isoformat()
                }
            }

        except Exception as e:
            yield {"error": f"Failed to update record: {str(e)}"}

    async def _get_client_entities(
        self, 
        wellbeing_service: WellbeingService, 
        params: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Get client entities for a case"""
        try:
            client_entities = await wellbeing_service.get_client_entities(
                case_id=params["case_id"],
                current_user=self._current_user
            )

            yield {
                "type": "info",
                "message": f"Found {len(client_entities)} client entities"
            }

            for entity in client_entities:
                entity_data = entity.data
                yield {
                    "type": "data",
                    "data": {
                        "entity_id": entity.id,
                        "first_name": entity_data.get("first_name"),
                        "last_name": entity_data.get("last_name"),
                        "email": entity_data.get("email"),
                        "phone": entity_data.get("phone"),
                        "is_client": entity_data.get("is_client", False)
                    }
                }

        except Exception as e:
            yield {"error": f"Failed to get client entities: {str(e)}"}

    async def _create_treatment_action(
        self, 
        wellbeing_service: WellbeingService, 
        params: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Create a treatment action for a wellbeing record"""
        try:
            record_id = params.get("record_id")
            if not record_id:
                yield {"error": "Record ID is required for treatment action creation"}
                return

            task_title = params.get("task_title")
            task_description = params.get("task_description")
            
            if not task_title or not task_description:
                yield {"error": "Task title and description are required"}
                return

            # Import here to avoid circular imports
            from app.schemas.task_schema import TaskCreate

            task_create = TaskCreate(
                case_id=params["case_id"],
                title=task_title,
                description=task_description,
                priority=params.get("task_priority", "Medium"),
                assigned_to_id=params.get("assigned_to_id")
            )

            task = await wellbeing_service.create_treatment_action(
                record_id=record_id,
                task_create=task_create,
                current_user=self._current_user
            )

            yield {
                "type": "success",
                "message": f"Created treatment action task {task.id}",
                "data": {
                    "task_id": task.id,
                    "title": task.title,
                    "priority": task.priority,
                    "status": task.status,
                    "assigned_to_id": task.assigned_to_id
                }
            }

        except Exception as e:
            yield {"error": f"Failed to create treatment action: {str(e)}"}