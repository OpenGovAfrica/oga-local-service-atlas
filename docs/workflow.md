## Report Workflow State Machine

This document describes the workflow for `Report` entities, including allowed states, valid transitions, and how invalid transitions are prevented.

The goals of the workflow are:

- **Explicitness** – Every report has a clearly defined state.
- **Auditability** – State changes are validated and logged.
- **Separation of concerns** – Citizen submission, moderation, and resolution are distinct phases.

---

## States

The `ReportState` enum in `apps.reports.models` defines the allowed states:

- `submitted` – A report has been created by a citizen, official, or NGO.
- `under_review` – A moderator or reviewer is actively assessing the report.
- `verified` – The report has been checked and confirmed as accurate.
- `rejected` – The report has been reviewed and deemed invalid or inappropriate.
- `resolved` – The underlying issue has been addressed or closed.

At creation time:

- `current_state` defaults to `submitted`.

---

## Allowed Transitions

Valid transitions are defined centrally in `VALID_STATE_TRANSITIONS` in `apps.reports.models`:

- **Submitted → Under Review**
  - A report enters the moderation queue.
- **Under Review → Verified**
  - The report is accepted as valid.
- **Under Review → Rejected**
  - The report is rejected; an optional `rejection_reason` may be recorded.
- **Verified → Resolved**
  - The issue described in the report has been addressed or otherwise resolved.

There are **no** allowed transitions:

- Out of `rejected` – once rejected, a report stays rejected (it may be superseded by a new report if circumstances change).
- Out of `resolved` – resolved reports remain resolved (they form part of the historical audit trail).

Diagram:

```text
submitted ──► under_review ──► verified ──► resolved
                    │
                    └────────► rejected
```

---

## System‑Driven vs Reviewer‑Driven Transitions

All transitions are currently **reviewer‑driven** and require authenticated API calls:

- `POST /api/v1/reports/{id}/transition/`
  - Body:
    - `new_state` – one of `under_review`, `verified`, `rejected`, `resolved`.
    - `reason` – optional text; used as `rejection_reason` when transitioning to `rejected`.
  - Permissions:
    - Requires authentication (`IsAuthenticated`).

Typical flows:

- **Submitted → Under Review**
  - Triggered when a moderator picks up a new report for assessment.
- **Under Review → Verified / Rejected**
  - Triggered after the moderator evaluates evidence and context.
- **Verified → Resolved**
  - Triggered when a responsible actor (e.g., local authority, operations team) confirms that the issue is addressed.

Future phases may introduce:

- Automated/system‑driven transitions (e.g., auto‑resolving after integration with external maintenance systems).
- Additional states (e.g., `escalated`, `needs_more_info`) with corresponding business rules.

Any such changes must update:

- `ReportState` and `VALID_STATE_TRANSITIONS` in code.
- This document (`docs/workflow.md`) with the new states and rules.

---

## Enforcement and Validation

### Model‑Level Enforcement

The `Report` model provides:

- `can_transition_to(new_state: str) -> bool`
  - Checks whether a transition from `current_state` to `new_state` is allowed according to `VALID_STATE_TRANSITIONS`.
- `transition_to(new_state: str) -> None`
  - Validates the transition using `can_transition_to`.
  - Raises `ValidationError` if the transition is not allowed.
  - Updates:
    - `current_state` – new state.
    - `last_activity_at` – timestamp of the change.

This ensures that **any** path that uses `transition_to` (including admin interfaces and background jobs) respects the workflow rules.

### API‑Level Enforcement

The `ReportViewSet` in `apps.reports.views` exposes a `transition` action:

- Uses `ReportStateTransitionSerializer` to:
  - Restrict `new_state` to known, non‑initial states.
  - Validate request payload.
- Calls `report.transition_to(new_state)`:
  - On success:
    - Returns a success message and updated `current_state`.
  - On `ValidationError`:
    - Returns HTTP 400 with an error message describing the invalid transition and listing valid options from the current state.

This combination guarantees that:

- Clients cannot force illegal transitions via the API.
- The workflow remains auditable and predictable.

---

## Workflow‑Related Metadata

Additional fields on `Report` support workflow and auditability:

- `reported_at` – when the report was first submitted.
- `last_activity_at` – when the report was last changed (including transitions).
- `rejection_reason` – optional text explaining why a report was rejected.
- `reporter_type`, `reporter`, and `is_anonymous` – provenance of who submitted the report.

When changing workflow behavior, contributors must:

- Ensure these fields remain consistent with the new logic.
- Update the OpenAPI documentation (via DRF Spectacular).
- Update this document (`docs/workflow.md`) and `docs/ARCHITECTURE.md` as needed.

