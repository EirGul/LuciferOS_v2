# Memory Target Resolver Design

## Milestone 111 status

MemoryTargetResolver now exists as an isolated memory-layer model.

It must not connect target resolution to IntentRouter, Core, API, HUD, provider prompts, voice, tools, runtime adapters, or MemoryCommandExecutor.

## Purpose

Memory target resolution defines how user-facing correction and delete requests may safely become one explicit memory id.

The resolver must prevent guessing.

The resolver must protect against changing or deleting the wrong memory.

## Current implemented resolver behavior

The current MemoryTargetResolver can:

- represent target resolution outcomes
- represent memory target candidates
- represent target resolution results
- validate candidate reason and score
- validate safe resolution invariants
- resolve explicit memory ids against a bounded candidate list
- resolve query text through normalized content substring matching
- return no_match when nothing is safe
- return single_safe_match when exactly one bounded content match exists
- return multiple_candidates when more than one bounded content match exists
- bound candidate processing with max_candidates

## Current resolver boundaries

MemoryTargetResolver belongs to the memory layer only.

It does not execute memory changes.

It does not call MemoryService.update_memory.

It does not call MemoryService.delete_memory.

It does not call MemoryCommandExecutor.

It does not inject memory into provider prompts.

It does not mutate MemoryItem objects.

## Resolution outcomes

A resolver result supports these outcomes:

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

Current implementation supports explicit id matching and single safe content-query matching only.

## Ambiguity rules

If no candidate exists, the resolver returns no_match.

If multiple candidates exist, the resolver returns multiple_candidates.

Multiple candidates are never safe_for_confirmation.

If confidence is low, a future implementation must ask the user to choose.

If the query matches sensitive or high-impact memory, a future implementation must still require confirmation before change.

## Bounded candidate rule

Resolver input must be bounded.

Resolver output must be bounded.

The resolver must never dump the entire memory store into a provider prompt.

The resolver must prefer deterministic matching before any future semantic matching.

The current resolver processes only candidates inside max_candidates.

## Deterministic matching first

Current resolver implementation uses deterministic matching only:

- explicit memory id match
- normalized content substring match

The current resolver does not match tags.

The current resolver does not match metadata.

Semantic or vector matching is out of scope for the current resolver implementation.

## User selection flow

When multiple candidates exist, the user must select one candidate explicitly.

Selection must bind to a concrete memory id.

Selection must create or update a pending action, not execute immediately.

The pending action must still require confirmation for correction or deletion.

User selection flow is not implemented yet.

## Current regression guarantees

The test suite currently verifies that:

- empty memory id returns no_match
- empty candidate list returns no_match
- metadata is not matched before metadata matching is implemented
- tags are not matched before tag matching is implemented
- multiple candidates are never safe_for_confirmation
- explicit-id resolution respects max_candidates
- query resolution respects max_candidates
- safe result invariant requires selected_memory_id
- resolver does not mutate memory items

## Non-goals

The resolver currently does not add:

- executor integration
- IntentRouter integration
- Core integration
- API endpoints
- HUD memory panels
- provider prompt injection
- automatic memory extraction
- semantic/vector search
- tag matching
- metadata matching
- OS/tool actions
- voice integration

## Historical Milestone 108 compatibility notes

Milestone 108 is design-only.

It must not connect target resolution to IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

Initial resolver implementation should use deterministic matching only:

- exact memory id match
- exact content substring match
- normalized content substring match
- tag match
- metadata field match

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

The next safe step is to design how resolver results may be used to prepare pending correction and delete actions.

Runtime integration should still wait until resolver-to-executor behavior is documented and tested.

Semantic or vector matching is out of scope for the first resolver implementation.
