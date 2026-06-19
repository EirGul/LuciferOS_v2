# Memory Target Resolver Design

## Milestone 108 status

Milestone 108 is design-only.

It must not connect target resolution to IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

## Purpose

Memory target resolution defines how user-facing correction and delete requests may safely become one explicit memory id.

The resolver must prevent guessing.

The resolver must protect against changing or deleting the wrong memory.

## Current executor boundary

MemoryCommandExecutor currently prepares correction and delete actions only when a MemoryCommand contains an explicit memory id.

Commands without an explicit memory id are rejected before execution.

This is intentional.

## Resolver responsibility

A future MemoryTargetResolver may:

- accept a bounded candidate list
- accept a user query
- compare query text against memory content and metadata
- return zero, one, or many candidate memories
- mark whether resolution is safe for confirmation
- produce a user-facing explanation

The resolver must not execute memory changes.

The resolver must not call MemoryService.update_memory.

The resolver must not call MemoryService.delete_memory.

The resolver must not inject memory into provider prompts.

## Resolution outcomes

A resolver result must support these outcomes:

- no_match
- single_safe_match
- multiple_candidates
- unsafe_ambiguous_match
- explicit_id_match

## Safe execution rule

Correction and deletion may be prepared only when one concrete memory id is selected.

One concrete memory id may come from:

- an explicit memory id in the command
- a user-selected item from a bounded result list
- a resolver result with exactly one safe candidate

## Ambiguity rules

If no candidate exists, the system must report that no matching memory was found.

If multiple candidates exist, the system must ask the user to choose.

If confidence is low, the system must ask the user to choose.

If the query matches sensitive or high-impact memory, the system must require confirmation before change.

## Bounded candidate rule

Resolver input must be bounded.

Resolver output must be bounded.

The resolver must never dump the entire memory store into a provider prompt.

The resolver must prefer deterministic matching before any future semantic matching.

## Deterministic matching first

Initial resolver implementation should use deterministic matching only:

- exact memory id match
- exact content substring match
- normalized content substring match
- tag match
- metadata field match

Semantic or vector matching is out of scope for the first resolver implementation.

## User selection flow

When multiple candidates exist, the user must select one candidate explicitly.

Selection must bind to a concrete memory id.

Selection must create or update a pending action, not execute immediately.

The pending action must still require confirmation for correction or deletion.

## Non-goals

Milestone 108 must not add:

- resolver implementation
- executor integration
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

The next safe step is a small isolated MemoryTargetResolver model and result type.

That model should be tested without connecting it to MemoryCommandExecutor, Core, API, HUD, providers, tools or runtime.
