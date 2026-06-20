# Memory Core Retrieval Design

## Milestone 138 status

Milestone 138 is design-only.

It must not modify LuciferCore, CoreRequest, CoreResponse, runtime, IntentRouter, Planner, ResponseBuilder, provider adapters, provider prompts, API, HUD, voice, tools, memory write flows, or selection-audit behavior.

## Purpose

This document defines the safe read-path required before LuciferOS may use stored memory during ordinary conversation.

Memory retrieval must remain explicit, bounded, policy-aware, auditable and independent from the existing memory write, correction, delete, selection and confirmation flows.

## Core principle

The Core must request a bounded memory retrieval result through a narrow interface.

The Core must not:

- access SQLite directly
- inspect MemoryStore internals
- receive the entire memory database
- decide memory policy itself
- mutate memory as part of retrieval
- pass raw memory records directly to a provider prompt

## Intended future flow

```text
CoreRequest
→ MemoryRetrievalService
→ retrieval policy evaluation
→ bounded retrieval query
→ type and scope filtering
→ ranked MemoryRetrievalResult
→ Core-owned response context decision
→ later provider context builder
```

No provider-context injection is part of this milestone.

## Retrieval request contract

A future MemoryRetrievalRequest must include only:

- request id
- query text or normalized query
- approved retrieval purpose
- allowed scopes
- allowed memory types
- bounded maximum result count
- bounded maximum context character budget
- source identifier
- explicit user or runtime context when required by policy

A retrieval request must reject:

- empty query text
- no allowed scope
- no allowed memory type
- non-positive result count
- non-positive context budget
- unsupported retrieval purpose

## Retrieval purposes

Initial supported purposes should be limited to:

- conversation_response
- project_assistance
- explicit_memory_search

The read-path must not support implicit learning, auto-store, background profiling, hidden personalization or provider-side autonomous retrieval.

## Policy boundary

MemoryRetrievalService must evaluate whether a request is allowed before reading records.

Policy must be able to deny retrieval based on:

- purpose
- scope
- memory type
- caller/source identity
- future sensitivity classification
- future trusted-project context

A denied retrieval must return an explicit bounded result and must not leak inaccessible memory metadata or contents.

## Scope and type filtering

Retrieval must filter before ranking and before context construction.

The initial order is:

```text
policy allow
→ scope filter
→ type filter
→ deterministic relevance filter
→ bounded ranking
→ context budget truncation
```

Global memory must not automatically override project or user-context boundaries.

Project-scoped memory must not be returned outside an approved project context.

## Bounded relevance

The first retrieval implementation must remain deterministic.

Allowed initial relevance methods:

- normalized exact match
- bounded substring matching
- controlled keyword overlap
- stable ordering with explicit tie-breaking

Not allowed in the first implementation:

- embeddings
- vector database retrieval
- LLM relevance scoring
- semantic expansion
- fuzzy automatic scope inference
- broad database dumping

## Retrieval result contract

A future MemoryRetrievalResult must distinguish:

- allowed
- denied
- no_match
- matched

It must contain:

- bounded reason code
- result count
- selected memory identifiers
- selected immutable memory items only when allowed
- applied scope and type filters
- whether the character budget caused truncation
- no raw hidden-memory metadata

The result must not mutate MemoryStore, MemoryService or selection state.

## Context budget

Retrieval must apply a strict character budget after filtering and ranking.

The budget must be configured by Core or a dedicated retrieval policy, not chosen by a provider.

The result must preserve stable ordering and stop before exceeding the configured budget.

A single oversized memory item must be skipped or explicitly represented as omitted; it must not cause the full budget to be exceeded.

## Audit boundary

Retrieval use must become auditable before it is exposed to provider prompts, API, HUD, voice or runtime adapters.

Future retrieval audit should include:

- retrieval request id
- source identifier
- purpose
- allowed or denied outcome
- count returned
- scopes and types applied
- bounded reason code
- no memory content by default
- no full query text by default

This milestone does not implement retrieval audit.

## Separation from write flows

Read retrieval is independent from:

- remember
- correct
- delete
- pending confirmation
- candidate selection
- selection audit
- memory write audit

A conversational retrieval must never create a pending action or mutate memory.

## Interface and provider boundary

API, HUD, CLI and voice may later request retrieval only through the Core.

Providers may later receive a bounded context product only through a dedicated context builder.

Interfaces and providers must not:

- query MemoryStore directly
- bypass retrieval policy
- set their own scopes or result limits
- inspect denied records
- write retrieved content into audit events
- use retrieval to trigger memory writes

## Non-goals

Milestone 138 must not add:

- MemoryRetrievalRequest implementation
- MemoryRetrievalService implementation
- Core integration
- provider context injection
- provider prompt modification
- API endpoints
- HUD panels
- runtime command routing
- retrieval audit implementation
- semantic or vector retrieval
- embeddings
- auto-store or learning
- memory migration
- changes to selection or confirmation behavior

## Next milestone direction

Milestone 139 should add immutable retrieval request and result models in the memory layer only.

Milestone 140 can add deterministic retrieval policy and service behavior.

Core integration must not begin until retrieval contracts, policy behavior, bounded budgets and regression tests are complete.
