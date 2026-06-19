# Memory Candidate Selection Lifecycle Design

## Milestone 123 status

Milestone 123 is design-only.

It must not modify MemoryCommandExecutor, MemoryCandidateSelectionRequestService, PendingMemoryActionService, IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

## Purpose

Candidate selection is an ephemeral user-control step between an ambiguous memory target and a pending correction or delete action.

A selection request must remain bounded, explicit, short-lived and bound to one concrete command context.

The selection step must not write, update or delete memory.

## Current implemented boundary

The memory layer can currently:

- create one bounded MemoryCandidateSelectionRequest
- expose candidate memory ids to a caller
- validate a selected memory id against that request
- prepare one PendingMemoryAction after a valid selection
- require separate confirmation before MemoryService executes a correction or delete

The current request store is in-memory and supports one active request only.

## Required lifecycle states

A selection request has these conceptual states:

- created
- awaiting_user_selection
- selected
- prepared_for_confirmation
- cancelled
- expired
- replaced

Only one active selection request may exist within one memory command context.

A request must not become an executable memory operation by itself.

## Request identity rule

Every selection must include:

- the active selection request id
- one concrete memory id from that request

The system must reject:

- a missing request id
- a request id that does not match the active request
- a memory id not present in the active request
- a selection result from another request

Ordinal selections such as "1" or "2" are not part of this milestone.

## Lifetime rule

Selection requests must be short-lived.

A future implementation must add an explicit expiry policy before selection is exposed through runtime or interface adapters.

Expired selection requests must be cleared and must not prepare a PendingMemoryAction.

Selection expiry must be independent from pending-action expiry.

## Replacement and cancellation rule

A new ambiguous memory command must not silently replace an active selection request in a user-facing flow.

Before runtime integration, the behavior must be made explicit through one of these safe policies:

- reject the new ambiguous command until the active selection is cancelled or completed
- require explicit cancellation before replacement
- present an explicit replacement decision bound to the active request

Cancellation must clear the selection request without changing memory and without creating a pending action.

## Selection-to-pending rule

A valid selection may prepare exactly one PendingMemoryAction.

Preparing a pending action must:

- clear the active selection request
- preserve command type, source text and selected memory id
- preserve proposed correction content for CORRECT
- preserve the separate PendingMemoryActionService confirmation gate

Selection must not call MemoryService.update_memory or MemoryService.delete_memory.

## Interface boundary

Interfaces may display bounded candidates and submit a request id plus memory id.

Interfaces must not:

- create PendingMemoryAction objects directly
- confirm a selection as memory execution
- bypass MemoryCandidateSelector
- bypass MemoryCandidateSelectionPendingActionBuilder
- bypass PendingMemoryActionService
- inject candidate lists into provider prompts

## Audit and future integration

Selection lifecycle events should become auditable before API, HUD, voice or runtime integration.

Future audit events should distinguish:

- selection request created
- selection rejected
- selection cancelled
- selection expired
- selection accepted
- pending action prepared from selection

## Non-goals

Milestone 123 must not add:

- selection lifecycle implementation
- selection expiry implementation
- selection cancellation implementation
- runtime selection commands
- IntentRouter integration
- Core integration
- API endpoints
- HUD memory panels
- provider prompt injection
- automatic memory extraction
- semantic/vector search
- OS/tool actions
- voice integration

## Next milestone direction

The next safe step is a small selection lifecycle model with explicit expiry and cancellation semantics.

Executor integration must remain bounded to the memory layer until lifecycle behavior and safety regression tests are complete.
