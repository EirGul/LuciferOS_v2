# Memory Command Execution Design

## Milestone 107 status

MemoryCommandExecutor now exists as an isolated memory-layer component.

It must not connect memory command execution to IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

## Purpose

Memory command execution translates parsed MemoryCommand objects into safe MemoryService operations.

The executor must not bypass MemoryService, MemoryPolicy or MemoryAuditSink.

## Current implemented executor behavior

The current MemoryCommandExecutor can:

- execute remember commands through MemoryService.add_memory
- create pending remember actions when MemoryService requires confirmation
- list memories with max_results bounds
- search memories with bounded substring matching
- prepare correction commands as pending actions when an explicit memory id exists
- prepare delete commands as pending actions when an explicit memory id exists
- explain memory policy with a read-only response
- confirm one concrete pending action
- cancel one concrete pending action
- execute confirmed pending remember actions
- execute confirmed pending correction actions
- execute confirmed pending delete actions
- reject normal conversation as not_memory_command

## Execution boundary

MemoryCommandExecutor belongs to the memory layer only.

It is not a runtime router.

It is not a Core integration.

It is not an API handler.

It is not a HUD controller.

It is not a provider prompt builder.

It is not a tool or OS action executor.

## Safety rules

- Interfaces must not write memory directly.
- Interfaces must not update memory directly.
- Interfaces must not delete memory directly.
- Executor logic must call MemoryService.
- Executor logic must preserve policy decisions.
- Executor logic must preserve audit events.
- Executor logic must not inject memory into provider prompts.
- Executor logic must not call tools or OS actions.
- Normal conversation must not be stored automatically.

## Pending actions

Some memory commands produce a pending action instead of executing immediately.

Pending actions are used for:

- high-impact remember commands
- correction commands
- delete commands
- ambiguous future correction targets
- ambiguous future delete targets

A pending action includes:

- action type
- memory command type
- target memory id when known
- proposed content when relevant
- source text
- created timestamp
- confirmation requirement
- human-readable explanation

## Confirmation behavior

Confirmation is bound to one concrete pending action.

Generic confirmation phrases such as ja, bekreft or confirm must not execute unrelated actions.

Stale pending actions must not execute.

Confirming a pending action clears it before execution.

The same pending action must not execute twice.

Cancel commands clear the pending action without changing memory.

Confirm after cancel must not execute anything.

Cancel after confirm must not execute anything.

## Correct and delete target resolution

Correct and delete commands must not guess the target memory item.

They may prepare execution only when the command contains an explicit memory id.

Future resolver milestones may allow correction or deletion when:

- the user has selected one memory from a bounded result list
- a previous search produced exactly one safe candidate and the user confirms it

If multiple candidates exist, the system must ask the user to choose.

If no candidate exists, the system must report that no matching memory was found.

## Read-only operations

List, search and explain-policy commands are read-only.

Read-only operations do not require confirmation.

Read-only operations must remain bounded.

Read-only operations must not dump all memory into provider prompts.

## Current regression guarantees

The test suite currently verifies that:

- confirm cannot execute the same pending action twice
- stale pending actions execute nothing
- cancel after confirm executes nothing
- confirm after cancel executes nothing
- unknown memory ids do not create false correction success
- unknown memory ids do not report deleted success
- ordinary conversation is not treated as a memory command
- empty search commands are rejected

## Non-goals

The executor currently does not add:

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

The next safe step is to add a small memory command resolver design.

That resolver should define how selected memories become explicit memory ids without guessing.

Runtime integration should still wait until command execution, pending confirmation and target resolution are documented and tested.

## Historical Milestone 101 compatibility notes

Milestone 101 is design-only.

Pending actions are required for:

- high-impact remember commands
- high-impact correction commands
- all delete commands
- ambiguous correction targets
- ambiguous delete targets

Confirmation must be bound to one concrete pending action.

Milestone 101 must not add:

- runtime execution
- Core integration
- API endpoints
- HUD memory panels
- provider prompt injection
- automatic memory extraction
- semantic/vector search
- OS/tool actions
