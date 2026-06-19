# Memory Persistence Design

## Current status after Milestone 97

LuciferOS now has an isolated persistent memory foundation.

Implemented:

- SQLiteMemoryStore
- shared MemoryStore contract tests
- add/get/list/update/delete support
- MemoryService support for SQLite persistence
- policy-gated update/correction flow
- audit events for update/correction
- persistence across new SQLite store instances

Still intentionally not implemented:

- Core memory integration
- API memory endpoints
- HUD memory editing
- provider prompt injection
- automatic memory extraction
- voice memory commands
- semantic or vector retrieval
- PC-control memory integration

## Purpose

LuciferOS needs durable memory without turning memory into uncontrolled prompt text, random JSON dumping, or automatic logging of everything the user says.

Persistent memory must preserve the existing memory architecture:

- explicit writes only
- policy-gated writes, updates and deletes
- audit events for meaningful changes
- bounded retrieval
- separated scopes
- deletable and correctable records
- no wholesale prompt injection

## Store strategy

The durable backend is SQLite.

Reasons:

- local-first
- deterministic
- available without server infrastructure
- transactional
- easy to back up
- portable across Windows, Linux and macOS
- suitable for structured memory records and audit metadata

JSON may be used only for temporary debug or export flows.

JSON must not become the primary durable memory backend.

## Store contract

Persistent stores must implement the MemoryStore interface.

The MemoryStore contract supports:

- add
- get
- list
- update
- delete

The existing InMemoryMemoryStore must remain valid and useful for tests, temporary sessions and offline safe mode.

Persistent storage must not require changes to Core, HUD, API, providers or runtime adapters.

## SQLite durable fields

SQLiteMemoryStore preserves:

- memory id
- memory type
- memory scope
- content
- source
- confidence
- tags
- metadata
- creation timestamp
- update timestamp

The store supports project-scoped memory separately from global memory.

## Persistence behavior

The persistent store supports:

- create memory item
- retrieve memory item by id
- list memory items
- update or correct memory item
- delete memory item
- preserve metadata and timestamps

Destructive deletes must remain policy-gated before the store is called.

Corrections and updates must remain policy-gated before the store is called.

## SQLite table

The SQLite table is named memory_items.

The table includes stable columns for:

- id
- content
- memory_type
- scope
- source
- confidence
- tags_json
- metadata_json
- created_at
- updated_at

Indexes support lookup/filtering by:

- scope
- memory_type
- created_at

Semantic or vector search is intentionally out of scope at this stage.

## Boundaries

The persistence layer must not add:

- provider prompt injection
- automatic memory extraction
- API memory endpoints
- HUD memory editing
- Core memory retrieval hooks
- voice memory commands
- semantic or vector retrieval
- PC-control memory integration

## Next milestone direction

After Milestone 98, the next safe step is user-facing memory command design.

Do not connect memory to provider prompts yet.

Do not expose memory editing through HUD or API before command semantics, confirmation behavior and audit expectations are clear.


## Historical Milestone 92 wording

Milestone 92 is design-only.

This sentence is preserved as historical architecture wording. The implementation has since advanced through SQLiteMemoryStore and service-level persistence tests.

The preferred durable backend is SQLite.

Persistent stores must implement the existing MemoryStore interface.

It must not connect memory to Core, API, HUD, provider prompts, voice, tools, or runtime adapters.
