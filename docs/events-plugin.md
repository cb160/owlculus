# Events Plugin Documentation

The Events plugin provides comprehensive event management capabilities for OSINT investigations, enabling structured logging of adhoc case-related events and activities.

## Features

### Event Management
- **Event Types**: Call, Counselling, Investigation
- **Event Status**: Draft, Final
- **Event Details**: Title, notes, custom date/time
- **User Tracking**: Automatic creator tracking
- **Case Integration**: Events are linked to specific cases

### Evidence Linking
- Link evidence files to events for better organization
- Many-to-many relationship between events and evidence
- Track who linked evidence and when
- View all evidence linked to an event

### Task Creation
- Create tasks directly from events
- Automatic task generation with event context
- Traceability: tasks maintain reference to source event
- Pre-filled task details based on event information

### Audit Logging
- Complete audit trail for all event changes
- Track who created, updated, or deleted events
- Timestamped history of all modifications
- No data content stored in audit logs (only actions)

## API Endpoints

### Core Event Operations
- `GET /api/events` - List events with filtering
- `POST /api/events` - Create new event
- `GET /api/events/{id}` - Get specific event
- `PUT /api/events/{id}` - Update event
- `DELETE /api/events/{id}` - Delete event

### Evidence Linking
- `POST /api/events/{id}/evidence/{evidence_id}` - Link evidence to event
- `DELETE /api/events/{id}/evidence/{evidence_id}` - Unlink evidence from event
- `GET /api/events/{id}/evidence` - Get all evidence linked to event

### Task Creation
- `POST /api/events/{id}/create-task` - Create task from event

### Audit Logging
- `GET /api/events/{id}/audit-logs` - Get audit history for event

## Usage Examples

### Creating an Event
```json
POST /api/events
{
  "case_id": 1,
  "title": "Client phone call",
  "notes": "Discussed case details and next steps",
  "event_type": "call",
  "status": "final",
  "event_date": "2024-01-15T10:30:00Z"
}
```

### Linking Evidence
```json
POST /api/events/1/evidence/5
```

### Creating Task from Event
```json
POST /api/events/1/create-task
{
  "title": "Follow-up on phone call",
  "description": "Contact client for additional information",
  "priority": "high",
  "due_date": "2024-01-20T17:00:00Z"
}
```

## Database Schema

### Event Table
- `id` - Primary key
- `case_id` - Foreign key to case
- `title` - Event title
- `notes` - Optional event notes
- `event_type` - call, counselling, investigation
- `status` - draft, final
- `event_date` - When the event occurred
- `created_at` - When record was created
- `updated_at` - When record was last updated
- `created_by_id` - Foreign key to user

### EventAuditLog Table
- `id` - Primary key
- `event_id` - Foreign key to event
- `action` - created, updated, deleted
- `changed_by_id` - Foreign key to user
- `changed_at` - When the change occurred

### EventEvidenceLink Table
- `event_id` - Foreign key to event (composite primary key)
- `evidence_id` - Foreign key to evidence (composite primary key)
- `created_at` - When link was created
- `created_by_id` - Foreign key to user who created link

### Task Enhancement
- `source_event_id` - Optional foreign key to event (for traceability)

## Frontend Components

### CaseEvents.vue
Main events view for a case with:
- Event listing table with filtering
- Create/edit event dialog
- Audit log viewer
- Evidence linking interface
- Task creation from events

### EventForm.vue
Form component for creating/editing events with:
- Event type selection
- Status management
- Date/time picker
- Notes field
- Validation

### Event Store (eventStore.js)
Pinia store for event management:
- CRUD operations
- Evidence linking
- Task creation
- Audit log retrieval
- Error handling

## Access Control

Events inherit case-based access control:
- Users can only access events for cases they have access to
- Event operations require case access permissions
- Evidence linking validates both event and evidence belong to same case
- Audit logs are visible to users with event access

## Integration Points

### Cases
- Events are case-specific
- Case access controls apply to events
- Events appear in case management interface

### Evidence
- Evidence can be linked to multiple events
- Events can have multiple pieces of evidence
- Cross-referencing for better investigation tracking

### Tasks
- Tasks can be created from events for follow-up actions
- Task maintains reference to source event
- Workflow integration for investigation processes

### Users
- Event creator tracking
- Audit log attribution
- Permission-based access

## Future Enhancements

Potential future improvements:
- Event templates for common event types
- Bulk event operations
- Event search and filtering
- Event notifications
- Event scheduling/reminders
- Integration with calendar systems
- Export capabilities
- Custom event types per organization