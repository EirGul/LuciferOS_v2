# Memory Candidate Selection Audit Contract

## Milestone 137 status

Milestone 137 locks the completed memory selection audit contract with documentation and regression tests.

It must not modify production selection behavior, MemoryService, global memory audit, IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

## Scope

This contract covers only the bounded memory candidate-selection lifecycle used by ambiguous CORRECT and DELETE commands.

It does not add automatic memory extraction, semantic retrieval, vector search, provider context injection, user-interface integration or runtime command routing.

## Lifecycle

The supported selection lifecycle is:

```text
ambiguous target
→ selection request created
→ user selects or cancels
→ valid selection prepares a pending action
→ separate confirmation may later mutate memory
```

A selection request is never a memory mutation.

## Audited actions

The selection audit action set is complete:

- selection_request_created
- selection_request_rejected
- selection_request_expired
- selection_candidate_rejected
- selection_candidate_accepted
- selection_pending_action_prepared
- selection_request_cancelled

## Ownership

MemoryCandidateSelectionRequestService owns:

- selection_request_expired

MemoryCommandExecutor owns:

- selection_request_created
- selection_request_rejected
- selection_candidate_rejected
- selection_candidate_accepted
- selection_pending_action_prepared
- selection_request_cancelled

## Minimal event fields

Events contain only:

- immutable event id
- timestamp
- action
- source identifier
- selection request id when relevant
- command type when relevant
- selected memory id only for an accepted candidate or pending preparation
- pending action id only after preparation
- bounded reason code

Events must not contain candidate content, raw user command text, proposed correction text, provider prompts or interface display state.

## Ordering rules

### New ambiguous request

```text
build selection_request_created
→ deliver audit
→ store active request
→ return awaiting_user_selection
```

### Candidate rejection

```text
validate request id and candidate id
→ deliver selection_candidate_rejected
→ retain active request
→ return rejected
```

### Candidate acceptance

```text
validate request id and candidate id
→ deliver selection_candidate_accepted
→ build PendingMemoryAction
→ deliver selection_pending_action_prepared
→ clear active request
→ store pending action
→ return pending_confirmation
```

### Cancellation

```text
deliver selection_request_cancelled
→ clear active request
→ return cancelled_user_selection
```

### Expiry

```text
detect stale request
→ deliver selection_request_expired
→ clear active request
→ return stale lifecycle result
```

## Fail-closed rule

For every state-changing selection transition:

```text
audit delivery succeeds
→ transition completes

audit delivery fails
→ transition does not complete
→ active selection remains when one existed
→ no pending action is created
→ no memory item is changed
```

A rejected operation remains rejected if its audit delivery fails. Audit failure must never convert a rejected selection into an accepted one.

## Memory mutation boundary

Selection audit does not claim that a memory item changed.

Memory update or delete can occur only later through the existing pending confirmation path and MemoryService.

Selection cancellation, expiry, rejection and pending preparation must not update or delete a memory item.

## Completion criteria

The selection audit subsystem is complete for the current memory-layer phase when:

- all seven lifecycle actions are represented by immutable events
- events use minimal bounded fields
- event delivery has explicit success/failure results
- state-changing transitions are fail closed
- selection expiry, creation, rejection, acceptance, preparation and cancellation are regression-tested
- selection remains isolated from Core, provider prompts, API, HUD, voice and runtime
