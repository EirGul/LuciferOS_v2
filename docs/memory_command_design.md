# Memory Command Design

## Milestone 99 status

Milestone 99 is design-only.

It must not connect memory commands to IntentRouter, Core, API, HUD, provider prompts, voice, tools, or runtime adapters.

## Purpose

User-facing memory commands let the user explicitly inspect, store, correct and delete LuciferOS memories without allowing normal conversation to become automatic memory.

Memory commands must preserve the existing memory rules:

- explicit memory operations only
- no automatic memory extraction from normal chat
- policy-gated writes, updates and deletes
- confirmation for high-impact operations
- audit events for meaningful memory operations
- bounded retrieval
- no wholesale provider prompt injection

## Command categories

LuciferOS should eventually support these memory command categories:

- remember
- list memories
- search memories
- correct memory
- delete memory
- explain memory policy
- cancel pending memory action
- confirm pending memory action

## Remember commands

Examples:

- husk at ...
- lær at ...
- remember that ...
- learn that ...

Remember commands should create a MemoryService.add_memory request.

High-impact memory types or scopes must require confirmation before storage.

Normal conversation must not be treated as a remember command.

## List and search commands

Examples:

- hva husker du
- hva husker du om LuciferOS
- vis minner
- søk i minner etter ...

List and search commands should use bounded retrieval.

They must not dump all memory into provider prompts.

Search results should be limited and clearly presented to the user.

## Correct memory commands

Examples:

- korriger minne ...
- rett minne ...
- endre minne ...
- correct memory ...

Correct memory commands should create a MemoryService.update_memory request.

Correction must preserve the memory id and update updated_at.

High-impact corrections must require confirmation.

Correction must be audit-logged.

## Delete memory commands

Examples:

- slett minne ...
- glem at ...
- delete memory ...
- forget that ...

Delete memory commands should create a MemoryService.delete_memory request.

Deletes must require confirmation.

Deletes must be audit-logged.

## Confirmation flow

Memory commands may produce pending actions.

Confirm phrases:

- ja
- bekreft
- ja utfør
- confirm

Cancel phrases:

- nei
- avbryt
- stopp
- cancel

The confirmation system must know which pending memory action is being confirmed.

Generic confirmation must not execute an unrelated or stale action.

## Routing boundary

Milestone 99 must not modify IntentRouter.

The current router is intentionally conservative.

Future memory command routing should be explicit and must not use aggressive fuzzy matching.

Words like lære, lært, husk or glem must not automatically hijack ordinary conversation.

Concrete phrases such as husk at ... and lær at ... may become explicit memory command triggers in a later milestone.

## Interface boundary

Memory commands may later be exposed through CLI, API, HUD and voice.

Interfaces must not write, update or delete memory directly.

Interfaces must call application/runtime services that use MemoryService.

HUD may display memory status later, but HUD must not own memory.

## Provider boundary

Memory commands must not inject memory into provider prompts.

Provider context injection is a separate future milestone and must remain bounded, filtered and auditable.

## Next milestone direction

After Milestone 99, the next safe step is a small memory command parser/intent design module.

That module should classify explicit memory command text without connecting it to Core, API, HUD or providers yet.
