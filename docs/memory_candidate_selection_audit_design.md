# Memory Candidate Selection Audit Design

## Milestone 126 status

Milestone 126 is design-only.

It must not modify MemoryCommandExecutor, MemoryCandidateSelectionRequestService, PendingMemoryActionService, MemoryService, MemoryAuditSink, IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

## Purpose

Memory candidate selection is a meaningful safety state transition.

The audit contract must make selection lifecycle behavior observable without turning candidate selection into a memory write, without exposing memory content unnecessarily and without coupling the memory layer to any interface.

## Manifest alignment

The manifest requires meaningful state-changing actions to be auditable.

Selection lifecycle changes state but must remain separate from memory write and delete audit events until a small, explicit selection-audit contract is implemented.

This milestone defines that contract only.

## Event ownership

Future selection audit events belong to the memory subsystem.

They must be emitted by the memory-layer component that owns the lifecycle transition.

Interfaces may display audit-derived status later, but they must not create or mutate selection audit events directly.

## Required event actions

A future implementation must support these selection audit actions:

- selection_request_created
- selection_request_rejected
- selection_request_cancelled
- selection_request_expired
- selection_candidate_rejected
- selection_candidate_accepted
- selection_pending_action_prepared

The action name must describe the lifecycle event, not imply that a memory item was changed.

## Minimal audit fields

Each selection audit event must contain only the minimum fields needed for traceability:

- event id
- timestamp
- action
- selection request id when available
- command type
- selected memory id when a candidate was accepted
- pending action id when a pending action was prepared
- reason or bounded outcome code
- source identifier for the owning memory component

The event must not require raw candidate content, full source text or proposed correction content.

## Privacy and content rules

Selection audit must not store:

- all candidate memory contents
- raw user command text by default
- proposed correction content by default
- provider prompts
- full memory-store snapshots
- interface-local presentation state

A future debugging mode may require separate explicit policy before any additional content is recorded.

## Lifecycle mapping

The intended event mapping is:

- ambiguous target creates selection request -> selection_request_created
- active selection blocks a new ambiguous request -> selection_request_rejected
- invalid request id or candidate id -> selection_candidate_rejected
- valid candidate id is bound to active request -> selection_candidate_accepted
- valid selection creates a PendingMemoryAction -> selection_pending_action_prepared
- user cancels active request -> selection_request_cancelled
- TTL clears active request -> selection_request_expired

Selection expiry and cancellation must never create a memory update or delete event.

## Ordering rules

For a valid selection that creates a pending action:

1. selection_candidate_accepted is emitted.
2. selection_pending_action_prepared is emitted.
3. the later confirmation or cancellation of the pending action remains governed by the existing pending-action and MemoryService audit behavior.

No selection audit event may claim that memory changed before confirmation reaches MemoryService.

## Failure and safety rules

A failed audit write must not silently be interpreted as a completed memory change.

Before implementation, the project must decide whether selection audit failure:

- rejects the selection transition, or
- records a local audit delivery failure through a separate safe mechanism.

That policy is intentionally not selected in this milestone.

Selection audit must not bypass MemoryPolicy, PendingMemoryActionService or MemoryService.

## Non-goals

Milestone 126 must not add:

- selection audit implementation
- MemoryAuditAction enum changes
- MemoryAuditSink changes
- executor audit calls
- persistent audit storage
- global audit integration
- Core integration
- API endpoints
- HUD panels
- provider prompt injection
- automatic memory extraction
- semantic or vector retrieval
- OS or tool actions
- voice integration

## Next milestone direction

The next safe milestone is a small memory-layer selection audit event model.

It must be independent from MemoryService write/delete audit events and must preserve the minimal-data contract in this document.
