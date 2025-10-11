# Trojan Wellbeing Case Management Specification

## 1. Product Vision
- **Purpose**: Deliver a focused case management system for small teams who need fast capture, triage, and collaboration without heavy platform overhead.
- **Guiding Principles**
  - Prefer clear, auditable case records over automation breadth.
  - Keep the UI task-oriented: capture → collaborate → report.
  - Ship opinionated defaults that can be customized later, not an extensive settings surface up front.

## 2. Target Users & Personas
- **Administrator**: Creates users and manages system
- **Lead Investigator**: Creates cases, client information, legal and intelligence records
- **Investigator**: Read and write access to cases for assigned clients
- **Viewer/Client** (optional stretch): Read-only access to curated reports or redacted evidence bundles.
- **Wellbeing professional**: Read/Write access to well-being pages for assigned clients

Role permissions should follow least privilege; no nested role hierarchies required initially.

## 3. Primary Use Cases
1. **Create and structure a case** with client context, checklist of questions, and a lightweight timeline.
2. **Capture evidence** quickly from:
   - Manual upload of files / notes.
4. **Track progress** via simple task list (to-do / in progress / done) tied to the case.
5. **Generate a briefing packet** (markdown or PDF export) summarizing findings, evidence, and outstanding tasks.

## 4. Feature Scope
### 4.1 Case Management
- Minimal schema: case number, title, description, status, tags, client reference.
- Automatic case number generator with simple prefix + increment (configurable).
- Case dashboard: key facts, latest evidence, open tasks, recent automation runs.

### 4.2 Evidence Handling
- Evidence types: `file`, `text note`.
- Folder hierarchy is optional; default to flat list with tagging.
- Metadata captured automatically (creator, timestamp).
- Render inline previews for text/HTML and images; download link for other binary files.

### 4.3 Entities
- Supported entity types at launch: `Person`, `Domain`,  `Email`, `Company`.
- Each entity has attributes (name/value pairs) plus analyst notes.

### 4.4 Tasks & Collaboration
- Case-level task board with statuses: `Todo`, `Doing`, `Done`.
- Assignable to users; due date optional.
- Comment thread per task for clarification.
- Activity log (case timeline) auto-appends significant events (new evidence, enrichment run, task status change).

### 4.5 Reporting & Export
- One-click export of case summary to Markdown; optional PDF via wkhtmltopdf or similar.
- Export includes case metadata, entity list, evidence table, task status, enrichment results.
- Ability to mark evidence/entities as “exclude from report”.

### 4.6 Authentication & Access
- JWT-backed session management with refresh token.
- Roles: `Lead`, `Analyst`, `Viewer`.
- Use oauth identity providers

### 4.7 Wellbeing Security
 - Wellbeing records need to be kept secure to prevent any unautorised access
 - Data should be encrypted with wellbeing professional providing a key to decrypt (or similar)
 - Wellbeing professional may grant another wellbeing professional access to the data as well - need a mechanism so only folks with relevant token/key can access data

## 5. Deferred / Nice-to-Have Features
- Complex folder templates for evidence.
- Fine-grained ACLs per evidence item.

## 6. Architecture Overview
- **Tech Stack**: FastAPI + pydantic + Jinja + htmx + Alpine + Tailwind. DB agnostic - but start with SQLite.
- **Deployment**: one app container and either sqlite or another db through a connection string. May want to deploy to a platform like fly.io or similar to keep cost of use down

## 7. Data Model Draft
- **User**: username, email, password_hash, role, is_active.
- **Case**: id, case_number, title, description, status, tags, client_name, created_by, created_at.
- **CaseMember**: user_id, case_id, role (Lead/Analyst/Viewer).
- **Evidence**: id, case_id, type, title, description, content_path or text_body created_at, created_by, tags, include_in_report.
- **Entity**: id, case_id, type, attributes (JSON), notes, created_at.
- **Task**: id, case_id, title, description, status, assignee_id, due_date, created_at.
- **ActivityLog**: id, case_id, entry_type, payload (JSON), created_by, created_at.
- **Wellbeing**: id, case_id, client_id, assessment_date, wellbeing_score, notes, interventions (JSON), follow_up_date, created_by, created_at.

## 9. Security & Compliance Notes
- All evidence uploads stored with SHA256 checksum and size for tamper detection.
- Access control enforced per case membership; enrichments must check access before execution.
- Provide audit log export for compliance; redact sensitive API keys from logs.
- Option to deploy with local object storage (minio) when S3 not available.

## 10. Operational Considerations
- **Logging**: Structured JSON logs with correlation IDs per request.
- **Configuration**: `.env` support for database URL, JWT secret, plugin API keys; optional admin UI later.
- **Testing**: Unit tests for services + API integration tests; end-to-end smoke via Playwright covering login → create case → upload evidence → export.
- **Performance**: Target <200ms for primary read/write operations under typical small-team load (<10 concurrent users).

## 11. Open Questions
1. A single org sufficient?
2. Should evidence storage support external object store (S3) immediately?
5. What level of report customization (branding, templates) is expected initially?

