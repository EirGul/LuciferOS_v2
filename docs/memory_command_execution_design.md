# Memory Command Execution Design

## Milestone 101 status

Milestone 101 is design-only.

It must not connect memory command execution to IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

## Purpose

Memory command execution is the future layer that will translate parsed MemoryCommand objects into safe MemoryService operations.

The executor must not bypass MemoryService, MemoryPolicy or MemoryAuditSink.

## Execution boundary

A future MemoryCommandExecutor may execute:

- remember commands through MemoryService.add_memory
- list commands through bounded memory listing or retrieval
- search commands through MemoryRetrievalService
- correct commands through MemoryService.update_memory
- delete commands through MemoryService.delete_memory
- explain policy commands through a read-only policy explanation response
- confirm or cancel commands through a pending-action mechanism

Milestone 101 must not implement this executor yet.

## Safety rules

- Interfaces must not write memory directly.
- Interfaces must not update memory directly.
- Interfaces must not delete memory directly.
- Executor logic must call MemoryService.
- Executor logic must preserve policy decisions.
- Executor logic must preserve audit events.
- Executor logic must not inject memory into provider prompts.
- Executor logic must not call tools or OS actions.

## Pending actions

Some memory commands may produce a pending action instead of executing immediately.

Pending actions are required for:

- high-impact remember commands
- high-impact correction commands
- all delete commands
- ambiguous correction targets
- ambiguous delete targets

A pending action must include:

- action type
- memory command type
- target memory id when known
- proposed content when relevant
- source text
- created timestamp
- confirmation requirement
- human-readable explanation

## Confirmation rules

Confirmation must be bound to one concrete pending action.

Generic confirmation phrases such as ja, bekreft or confirm must not execute unrelated actions.

Stale pending actions must not execute.

Cancel commands must clear the pending action without changing memory.

## Correct and delete target resolution

Correct and delete commands must not guess the target memory item.

They may execute only when one of these is true:

- the command contains an explicit memory id
- the user has selected one memory from a bounded result list
- a previous search produced exactly one safe candidate and the user confirms it

If multiple candidates exist, the system must ask the user to choose.

If no candidate exists, the system must report that no matching memory was found.

## Read-only operations

List, search and explain-policy commands are read-only.

Read-only operations should not require confirmation.

Read-only operations must remain bounded and must not dump all memory into prompts.

## Non-goals

Milestone 101 must not add:

- runtime execution
- Core integration
- API endpoints
- HUD memory panels
- provider prompt injection
- automatic memory extraction
- semantic/vector search
- OS/tool actions

## Next milestone direction

After Milestone 101, the next safe step is a small pending memory action model.

That model should remain isolated from Core, API, HUD and providers.
