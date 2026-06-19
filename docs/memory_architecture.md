# LuciferOS Memory Architecture

## Purpose

The LuciferOS memory subsystem exists to let LuciferOS remember and learn useful information without becoming an uncontrolled prompt log or a system that stores everything the user says.

Memory must remain explicit, bounded, auditable and permission-aware.

## Current Status

The memory subsystem currently provides architecture foundation only.

Implemented:

- Memory models
- In-memory store
- Memory service
- Explicit learning service
- Memory policy boundary
- Memory operation result
- Memory audit event model
- In-memory memory audit sink
- Memory retrieval contract
- Memory context builder

Not implemented yet:

- Persistent database storage
- Core integration
- API integration
- HUD integration
- Provider prompt-context injection
- Automatic memory extraction from normal chat
- Global audit-log integration
- User-facing memory management commands

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

MemoryStore is the storage interface. InMemoryMemoryStore is only a temporary in-memory implementation for tests and early development.

### service.py

Defines:

- MemoryService
- MemoryOperationResult

MemoryService is the main application-facing memory service.

MemoryService must not blindly store or delete memory. It evaluates operations through MemoryPolicy and records memory audit events through MemoryAuditSink.

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
- MemoryDeleteRequest
- MemoryDecision
- MemoryPolicy

MemoryPolicy decides whether memory operations are allowed, rejected, or require confirmation.

High-impact memory types or scopes require confirmation before storage.

Deletes require confirmation.

### audit.py

Defines:

- MemoryAuditAction
- MemoryAuditEvent
- MemoryAuditSink
- InMemoryMemoryAuditSink

Memory audit events record write/delete requests, rejections, confirmation requirements and completed operations.

This is not yet connected to the global LuciferOS audit system.

### retrieval.py

Defines:

- MemoryQuery
- MemorySearchResult
- MemoryRetrievalService

Retrieval is explicit, filtered and limited. It supports filtering by text, type, scope and limit.

Memory retrieval must not dump all memories into provider prompts.

### context.py

Defines:

- MemoryContext
- MemoryContextBuilder

MemoryContextBuilder converts selected retrieval results into a short, bounded text context suitable for future provider use.

It includes only type, scope and memory content. It intentionally avoids raw metadata and audit details.

## Boundary Rules

- Memory is its own subsystem.
- Core must not directly own memory storage details.
- API must not bypass MemoryService.
- HUD must not write memory directly.
- Providers must not receive unbounded memory dumps.
- Memory writes must pass through policy.
- Memory deletes must pass through policy.
- Memory operations must create audit events.
- Automatic memory from normal chat is not allowed at this stage.

## Future Integration Order

Planned safe order:

1. Persistent MemoryStore backend.
2. User-facing memory commands.
3. Core-level memory retrieval hook.
4. Controlled provider-context injection.
5. API/HUD memory visibility.
6. Global audit integration.

Do not connect memory directly to provider prompts before retrieval, context limits, policy and audit behavior are stable.

## Design Principle

LuciferOS memory should make the assistant more useful over time, but never at the cost of user control, transparency, safety or architectural boundaries.
