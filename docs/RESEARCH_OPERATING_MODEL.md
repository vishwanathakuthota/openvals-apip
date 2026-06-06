# Research Operating Model

Status: Beta framework  
Owner: OpenVals  
Scope: Research operations for company validation and real-data evidence workflows.

## Purpose

The Research Operations Framework coordinates how OpenVals analysts move companies from research queue intake to published validation. It connects company validation, source approval, evidence collection, reviewer workflow, assignment, audit trails, and progress metrics.

## Research Statuses

APIP uses these external statuses:

- Not Started
- Researching
- Evidence Collected
- Under Review
- Approved
- Published

Internally these are stored as normalized keys: `not_started`, `researching`, `evidence_collected`, `under_review`, `approved`, and `published`.

## Operating Workflow

1. Research Queue
   - Each tracked company receives one queue item.
   - Queue items store status, priority, assignment, reviewer, progress, coverage, and notes.

2. Company Research Status
   - Analysts move a company through the status sequence as evidence matures.
   - Status updates write to the research audit trail.

3. Evidence Collection
   - Evidence records link queue items to approved or pending sources.
   - Each evidence record stores collection status, approval status, coverage score, collector, reviewer, notes, and timestamps.

4. Source Approval Workflow
   - Reviewers approve, verify, or reject evidence.
   - Approved or verified evidence promotes its linked source to approved status.
   - Rejected evidence marks the linked source rejected for that review path.

5. Reviewer Workflow
   - Queue items store an assigned researcher and reviewer.
   - Evidence records store reviewer notes and review timestamps.

6. Evidence Coverage Dashboard
   - Coverage score uses the real-data source tier model.
   - The dashboard tracks average evidence coverage across queue items.

7. Validation Dashboard
   - Company validation remains the canonical OpenVals score layer.
   - Research operations feed validation readiness and auditability.

8. Research Audit Trail
   - Assignment, status updates, evidence collection, and evidence review write audit entries.
   - Audit entries include actor, queue item, previous status, next status, notes, metadata, and timestamp.

9. Assignment System
   - Admins can assign a researcher and reviewer.
   - Default seed assignment uses the APIP admin account for beta initialization.

10. Research Progress Metrics
   - Total queue items
   - Status counts
   - Assigned and unassigned items
   - Average progress percentage
   - Average evidence coverage score
   - Collected evidence count
   - Approved evidence count

## API Endpoints

Public API:

- `GET /api/v1/research-operations`
- `GET /api/v1/research-operations/{queue_item_id}`

Admin API:

- `GET /api/v1/admin/research-queue`
- `GET /api/v1/admin/research-progress`
- `GET /api/v1/admin/research-audit`
- `PATCH /api/v1/admin/research-queue/{queue_item_id}/assign`
- `PATCH /api/v1/admin/research-queue/{queue_item_id}/status`
- `POST /api/v1/admin/research-queue/{queue_item_id}/evidence`
- `PATCH /api/v1/admin/research-evidence/{evidence_id}/review`

## Dashboard

The admin portal includes a Research Operations dashboard with:

- Queue table
- Company research status
- Assigned researcher
- Reviewer
- Evidence coverage score
- Progress percentage
- Evidence count
- Progress metric cards
- Assignment and status controls

## Audit Events

Research audit action examples:

- `research_queue.seeded`
- `research.assigned`
- `research.status_updated`
- `research.evidence_collected`
- `research.evidence_reviewed`

These events are stored in `research_audit_trail` and exposed through `/api/v1/admin/research-audit`.
