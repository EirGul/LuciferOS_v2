# Memory Candidate Selection Audit Delivery Design

## Milestone 129 status

Milestone 129 is design-only.

It must not modify MemoryCommandExecutor, MemoryCandidateSelectionRequestService, MemoryCandidateSelectionAuditSink, PendingMemoryActionService, MemoryService, IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

## Purpose

Milestone 126 defined what selection audit events must contain.
Milestone 127 defined immutable events.
Milestone 128 defined an audit sink contract.

Before audit emission is connected to live selection transitions, the system must define event ownership, ordering and audit-delivery failure behavior.

## Decision: fail closed for state-changing selection transitions

Selection lifecycle transitions that change active state must be fail closed when audit delivery fails.

A failed audit delivery must prevent the related state transition from completing.

This applies to:

- creating an active selection request
- cancelling an active selection request
- expiring and clearing an active selection request
- accepting a selected candidate
- clearing selection and preparing a pending action

The system must return or surface an explicit audit-delivery failure. It must not report that a selection transition completed.

## Non-state-changing rejection events

A rejection does not mutate memory or selection state.

For request rejection and candidate rejection:

- the user-facing operation remains rejected
- the audit event should still be attempted
- an audit-delivery failure must be surfaced explicitly
- audit failure must not convert a rejected operation into a successful operation
- the active selection request must remain unchanged

## Event ownership

The owner of a lifecycle transition must emit its audit event.

### MemoryCandidateSelectionRequestService owns

- selection_request_expired

The service owns expiry because it determines staleness and clears the request.

### MemoryCommandExecutor owns

- selection_request_created
- selection_request_rejected
- selection_request_cancelled
- selection_candidate_rejected
- selection_candidate_accepted
- selection_pending_action_prepared

The executor owns these transitions because it creates user-facing selection requests, processes candidate choices and transfers a valid choice into PendingMemoryActionService.

## Ordering rules

### Creating a request

1. Build the immutable selection audit event.
2. Deliver the audit event.
3. Store the active selection request.
4. Return awaiting_user_selection.

If step 2 fails, no active request is stored.

### Expiring a request

1. Detect expiry.
2. Build selection_request_expired.
3. Deliver the audit event.
4. Clear the request.
5. Return stale lifecycle status.

If step 3 fails, the stale request remains stored and no expiry result is reported as completed.

### Cancelling a request

1. Build selection_request_cancelled.
2. Deliver the audit event.
3. Clear the active request.
4. Return cancelled status.

If step 2 fails, the active request remains stored.

### Accepting a candidate and preparing pending action

1. Validate request id and selected memory id.
2. Build selection_candidate_accepted.
3. Deliver selection_candidate_accepted.
4. Build PendingMemoryAction.
5. Build selection_pending_action_prepared with its pending action id.
6. Deliver selection_pending_action_prepared.
7. Clear active selection request.
8. Store PendingMemoryAction.
9. Return pending_confirmation.

If either audit delivery fails, the active selection request remains stored and no pending action is stored.

## Sink failure representation

A future implementation must use an explicit memory-layer audit delivery error or result.

It must preserve:

- the original event action
- a bounded reason code
- no raw candidate content
- no raw source text
- no proposed correction content
- no provider prompt data

The failure representation must not be confused with a memory mutation audit event.

## Dependency rule

MemoryCandidateSelectionRequestService and MemoryCommandExecutor may depend on the selection-audit contract.

MemoryService, global memory audit, Core, interfaces and providers must remain independent of selection audit during this phase.

## Non-goals

Milestone 129 must not add:

- audit delivery implementation
- executor audit calls
- selection-service audit calls
- audit sink persistence
- audit retry queues
- global audit integration
- Core integration
- API endpoints
- HUD panels
- voice integration
- provider prompt injection
- automatic memory extraction
- semantic or vector retrieval
- OS or tool actions

## Next milestone direction

Milestone 130 should add an explicit selection-audit delivery error or result model and tests for fail-closed semantics.

Milestone 131 can then add audit emission to MemoryCandidateSelectionRequestService expiry handling.

Milestone 132 can add executor emission with the ordering rules in this document.
