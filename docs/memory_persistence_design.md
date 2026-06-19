# Memory Persistence Design

## Milestone 92 status

This document defines the persistence design for the LuciferOS memory subsystem.

Milestone 92 is design-only.

It must not connect memory to Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

## Purpose

LuciferOS needs durable memory without turning memory into uncontrolled prompt text, random JSON dumping, or automatic logging of everything the user says.

Persistent memory must preserve the existing memory architecture:

- explicit writes only
- policy-gated writes and deletes
- audit events for meaningful changes
- bounded retrieval
- separated scopes
- deletable and correctable records
- no wholesale prompt injection

## Store strategy

The preferred durable backend is SQLite.

Reasons:

- local-first
- deterministic
- available without server infrastructure
- transactional
- easy to back up
- portable across Windows, Linux, and macOS
- suitable for structured memory records and audit metadata

JSON may be used only for temporary debug or export flows.

JSON must not become the primary durable memory backend.

## Store contract

Persistent stores must implement the existing MemoryStore interface.

The existing InMemoryMemoryStore must remain valid and useful for tests, temporary sessions, and offline safe mode.

Persistent storage must not require changes to Core, HUD, API, providers, or runtime adapters.

## Required durable fields

A persistent MemoryItem record must preserve:

- memory id
- memory type
- memory scope
- content
- metadata
- creation timestamp
- update timestamp when applicable
- deletion state or deletion timestamp when applicable

The store must support project-scoped memory separately from global memory.

## Persistence behavior

The persistent store must support:

- create memory item
- retrieve memory item by id
- list memory items
- search memory items through the retrieval layer
- update or correct memory item
- delete memory item
- preserve audit-relevant metadata

Delete behavior must be explicit.

Destructive deletes must remain policy-gated before the store is called.

## SQLite design direction

The likely SQLite table should be named memory_items.

The table should include stable columns for:

- id
- memory_type
- scope
- content
- metadata_json
- created_at
- updated_at
- deleted_at

Indexes should support lookup by:

- id
- memory_type
- scope
- created_at
- deleted_at

Semantic or vector search is intentionally out of scope for Milestone 92.

## Boundaries

Milestone 92 must not add:

- provider prompt injection
- automatic memory extraction
- API memory endpoints
- HUD memory editing
- Core memory retrieval hooks
- voice memory commands
- semantic or vector retrieval
- PC-control memory integration

## Next implementation milestone

Milestone 93 may introduce a SQLiteMemoryStore implementation behind the existing MemoryStore interface.

Milestone 93 should keep InMemoryMemoryStore unchanged and should test both stores against the same behavior where practical.
