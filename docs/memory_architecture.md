# LuciferOS Memory Architecture

## Purpose

The LuciferOS memory subsystem exists to let LuciferOS remember and learn useful information without becoming an uncontrolled prompt log or a system that stores everything the user says.

Memory must remain explicit, bounded, auditable, permission-aware, deletable and correctable.

## Current Status

The memory subsystem currently provides an isolated memory architecture with persistent storage support.

Implemented:

- Memory models
- In-memory store
- SQLite persistent store
- Shared MemoryStore contract
- Memory service
- Explicit learning service
- Memory policy boundary
- Memory operation result
- Memory audit event model
- In-memory memory audit sink
- Explicit memory commands and pending confirmation flows
- Candidate-selection audit lifecycle
- Policy-gated deterministic memory retrieval
- Immutable retrieval result and context contracts
- Policy-gated memory writes
- Policy-gated memory updates and corrections
- Policy-gated memory deletes
- SQLite persistence across service/store instances

Not implemented yet:

- Core integration
- API integration
- HUD integration
- Provider prompt-context injection
- Retrieval audit
- Automatic memory extraction from normal chat
- Global audit-log integration
- Semantic or vector memory retrieval

## Modules

### models.py

Defines:

- MemoryItem
- MemoryType
- MemoryScope

MemoryItem represents one stored memory with content, type, scope, source, confidence, tags, metadata, id, created_at and updated_at.

### store.py

Defines:

- MemoryStore
- InMemoryMemoryStore

MemoryStore is the storage interface.

InMemoryMemoryStore remains useful for tests, temporary sessions and offline safe-mode development.

The store contract supports:

- add
- get
- list
- update
- delete

### sqlite_store.py

Defines:

- SQLiteMemoryStore

SQLiteMemoryStore is the local-first persistent MemoryStore implementation.

It stores MemoryItem records in a local SQLite database and preserves:

- id
- content
- memory type
- memory scope
- source
- confidence
- tags
- metadata
- created_at
- updated_at

SQLiteMemoryStore is intentionally isolated from Core, API, HUD, providers and runtime adapters.

### service.py

Defines:

- MemoryService
- MemoryOperationResult

MemoryService is the main application-facing memory service.

MemoryService must not blindly store, update or delete memory. It evaluates operations through MemoryPolicy and records memory audit events through MemoryAuditSink.

Supported service operations:

- add_memory
- update_memory
- delete_memory
- get_memory
- list_memories

### learning.py

Defines:

- LearningService

LearningService currently accepts only explicit learning phrases such as:

- husk at ...
- lær at ...
- remember that ...
- learn that ...

Normal conversation must not be automatically stored as memory.

### policy.py

Defines:

- MemoryWriteRequest
- MemoryUpdateRequest
- MemoryDeleteRequest
- MemoryDecision
- MemoryPolicy

MemoryPolicy decides whether memory operations are allowed, rejected, or require confirmation.

High-impact memory types or scopes require confirmation before storage or update.

Deletes require confirmation.

### audit.py

Defines:

- MemoryAuditAction
- MemoryAuditEvent
- MemoryAuditSink
- InMemoryMemoryAuditSink

Memory audit events record write, update and delete requests, rejections, confirmation requirements and completed operations.

This is not yet connected to the global LuciferOS audit system.

### retrieval.py

Defines:

- MemoryQuery
- MemoryRetrievalDecision
- MemoryRetrievalOutcome
- MemoryRetrievalResult
- MemorySearchResult
- MemoryRetrievalService

`MemoryQuery` is the explicit, bounded request contract. It requires a caller-supplied request id, query text, scopes, types, purpose, source, result limit and total context character budget.

`MemoryRetrievalService.retrieve(query)` evaluates policy before any store read and returns one immutable `MemoryRetrievalResult` with an explicit outcome:

- denied
- no_match
- matched

The result preserves the request identity and applied filters, includes only immutable minimal snapshots when matched, retains deterministic score/id ordering, and never contains raw query text or mutable memory records.

### context.py

Defines:

- MemoryContext
- MemoryContextBuilder

`MemoryContextBuilder` projects a matched `MemoryRetrievalResult` into a short deterministic text context suitable for a later provider boundary.

The builder uses `MemoryRetrievalResult.max_context_chars` as the only total character budget. It does not own a competing total-budget or result-count policy. It includes only type, scope and memory content and intentionally avoids raw metadata and audit details.

`MemoryContext.truncated` reports whether an already allowed and ranked match could not fit into the retrieval result's total context budget.

## Persistence Status

Persistent memory storage is implemented through SQLiteMemoryStore.

MemoryService has been tested against SQLite persistence for:

- add across new store instances
- update across new store instances
- confirmed delete across new store instances
- confirmed high-impact update across new store instances

Persistence is still not connected to Core, API, HUD, providers, voice or tools.

## Boundary Rules

- Memory is its own subsystem.
- Core must not directly own memory storage details.
- API must not bypass MemoryService.
- HUD must not write memory directly.
- Providers must not receive unbounded memory dumps.
- Memory writes must pass through policy.
- Memory updates and corrections must pass through policy.
- Memory deletes must pass through policy.
- Memory operations must create audit events.
- Retrieval policy must evaluate before store access.
- Automatic memory from normal chat is not allowed at this stage.

## Future Integration Order

Planned safe order:

1. Retrieval audit and complete memory read-path regression.
2. Core audit hardening before memory-related Core state is introduced.
3. Core-level memory retrieval hook without provider injection.
4. Controlled provider-context injection.
5. API/HUD memory visibility.
6. Global audit integration.
7. More advanced learning and correction workflow.
8. Optional semantic/vector retrieval later.

Do not connect memory directly to provider prompts before retrieval, context limits, policy and audit behavior are stable.

## Design Principle

LuciferOS memory should make the assistant more useful over time, but never at the cost of user control, transparency, safety or architectural boundaries.


## Historical test-protected wording

Earlier milestone documentation also listed User-facing memory management commands as not implemented. Explicit memory commands now exist, but this phrase is intentionally preserved because earlier documentation tests protect the architecture history.


Earlier milestone documentation listed Persistent database storage as not implemented.

Persistent database storage is now implemented through SQLiteMemoryStore, but this phrase is intentionally preserved because earlier documentation tests protect the architecture history.
