# LuciferOS Manifest v2

## Status

Architectural contract for LuciferOS after Milestone 91.

- Project path: `C:\Users\Eirik Gulbrandsen\developer\luciferos_v2`
- Repository: `https://github.com/EirGul/LuciferOS_v2.git`
- Branch: `main`
- Last known milestone: 1–91 complete
- Last known tests: 230 passed
- Last known git state: clean and pushed

Preferred repo location:

    docs/luciferos_manifest.md

This manifest should be committed and pushed whenever it changes materially.

## Purpose

LuciferOS is a local-first, modular AI agent platform. It is designed to become a fast, safe, extensible personal assistant that can operate through HUD, voice, CLI, API and eventually a tablet dashboard.

LuciferOS must not become a fragile command script, a thin wrapper around one provider, or a UI-driven system where HUD owns routing, tools, memory, provider choice or permissions.

LuciferOS must have its own Core, runtime model, provider abstraction, permission layer, audit trail, memory/learning subsystem and modular tool architecture.

## Core Principles

- Core must be small, deterministic, testable and interface-independent.
- Conversation is the default interaction model.
- Commands are explicit special cases.
- Aggressive fuzzy command matching must not hijack normal conversation.
- Voice, HUD, CLI and API are replaceable interfaces.
- Providers are replaceable backends, not the identity of LuciferOS.
- Offline mode must remain available as the safe default.
- Ollama and other providers must be explicit runtime/provider choices.
- Tools and platform actions must be modular and permission-gated.
- HUD must not own routing, provider selection, permissions, tools, memory or OS actions.
- All meaningful state-changing actions must be auditable.
- The user must remain in control of memory, tools and external actions.

## Runtime Architecture

Intended flow:

    Interface
    -> API/runtime adapter
    -> LuciferApp
    -> Core
    -> Router / Planner / Permission policy
    -> Provider or Tool adapter
    -> Response builder
    -> Interface rendering

Current verified local Ollama chain:

    HUD
    -> FastAPI
    -> ApiService
    -> LuciferApp
    -> Core
    -> OllamaProvider
    -> local Ollama model

Runtime logic belongs behind application/service boundaries, not inside HUD or scripts.

## Provider Strategy

- Default provider must remain `offline` unless explicitly overridden.
- Local Ollama mode is valid and available through explicit startup/runtime selection.
- Cloud providers may be added later, but must remain optional and permission-aware.
- Provider choice must stay outside HUD logic.
- Provider status may be displayed in HUD, but HUD must only display status returned from API/runtime.
- Provider fallback must be safe and observable.

Current verified modes:

    Safe/offline: start_lucifer_api.bat
    Local AI/Ollama: start_lucifer_api_ollama.bat

Current local model:

    eirik-qwen3:latest

## Interface Strategy

Interfaces are replaceable shells around the Core/runtime.

Current/planned interfaces:

- CLI
- API
- HUD
- Voice
- Future tablet dashboard

Rules:

- Interfaces may collect user input and display state.
- Interfaces may show confirmation prompts later.
- Interfaces must not own provider routing.
- Interfaces must not bypass permissions.
- Interfaces must not call tools directly.
- Interfaces must not write memory directly.
- Interfaces must not execute OS actions directly.

## HUD Strategy

HUD is a visual control and feedback surface.

HUD may display API status, provider status, adapter status, face state, chat output and future system panels.

HUD must not directly route intents, select providers, write memory, execute tools, perform OS actions, bypass permissions or own long-term state.

Current visual state contract:

    online: blue
    offline: grey-blue
    thinking: yellow
    speaking: purple
    chat/active dialog: green
    error/angry: red

## Memory & Learning Subsystem

Memory and learning are first-class LuciferOS subsystems.

Memory must not be uncontrolled prompt text, random JSON dumping, or automatic storage of everything the user says. Memory must be explicit, bounded, auditable, permission-aware, deletable, correctable and separated by scope.

Current implemented memory modules:

    lucifer_os/memory/models.py
    lucifer_os/memory/store.py
    lucifer_os/memory/service.py
    lucifer_os/memory/learning.py
    lucifer_os/memory/policy.py
    lucifer_os/memory/audit.py
    lucifer_os/memory/retrieval.py
    lucifer_os/memory/context.py

Current implemented concepts:

- MemoryItem
- MemoryType
- MemoryScope
- MemoryStore / InMemoryMemoryStore
- MemoryService / MemoryOperationResult
- LearningService
- MemoryPolicy / MemoryDecision
- MemoryWriteRequest / MemoryDeleteRequest
- MemoryAuditEvent / MemoryAuditAction
- MemoryAuditSink / InMemoryMemoryAuditSink
- MemoryQuery / MemorySearchResult / MemoryRetrievalService
- MemoryContext / MemoryContextBuilder

Required memory types:

- fact
- preference
- project_state
- correction
- command_alias
- relationship
- task_context
- user_instruction

Required scopes:

- global
- project
- session
- interface-specific
- tool-specific

Learning rules:

- LuciferOS must not store everything the user says.
- Explicit phrases like `husk at ...` and `lær at ...` may create learning requests.
- High-impact memory must require confirmation.
- Deletes must require confirmation.
- The user must be able to ask what Lucifer remembers.
- The user must be able to delete or correct memories.
- Memory writes and deletes must be audit-logged.
- Retrieval must be relevant and bounded.
- Memory must never be dumped wholesale into provider prompts.
- Project memory must be separated from global personal memory.

Current memory state after Milestone 91:

- Memory subsystem exists.
- Policy gate exists.
- Audit events exist.
- Retrieval contract exists.
- Context builder exists.
- Memory documentation exists.
- Memory is not yet integrated into Core/API/HUD/provider prompts.
- No persistent database backend exists yet.
- No automatic memory extraction exists.

This separation is intentional.

## Memory Integration Order

Future order:

1. Persistent MemoryStore backend design.
2. Persistent MemoryStore implementation.
3. User-facing memory commands.
4. Confirmation flow for writes/deletes.
5. Core-level retrieval hook.
6. Controlled provider-context injection.
7. API/HUD memory visibility.
8. Global audit integration.
9. More advanced learning/correction workflow.
10. Optional semantic/vector retrieval later.

Do not connect memory directly to provider prompts before retrieval, context limits, policy and audit behavior are stable.

## Safety and Permissions

- Read-only operations may be low friction.
- Write operations must be permission-gated.
- Destructive operations must require explicit confirmation.
- OS, browser, email, document, smart-home and camera actions must go through tool adapters and permission policies.
- Audit logs must record meaningful state-changing actions.
- No interface may bypass permissions.

## Tool and Plugin Strategy

Future tools should support local files, browser, email, calendar, Office documents, Git/project work, Home Assistant/smart-home, camera/admin, printer/connected devices and local OS/app control.

Rules:

- Tools must be registered.
- Tools must declare risk.
- Tools must be permission-gated.
- Tools must audit meaningful changes.
- Tools must be callable through Core/runtime, not directly from HUD.
- Tools must be lazy-loaded where possible.

## Smart-Home Goal

Preferred model:

    Tablet dashboard / HUD
    -> LuciferOS API/Core
    -> Tool adapters
    -> Home Assistant or equivalent
    -> physical smart-home devices

LuciferOS should reason and coordinate. Home Assistant or equivalent should control physical devices.

## PC-Control Goal

LuciferOS should eventually become a local PC-operating assistant: apps, browser, email, Office documents, local files, project workflows, camera/printer/connected devices later.

PC-control must use tools/adapters, permission gates and audit. It must not be patched into fuzzy command matching.

## Voice Strategy

Voice is a future replaceable interface.

- Voice must not own Core logic.
- Voice should give short spoken responses.
- Longer responses should go to visual/document channels.
- Wake/sleep behavior should be explicit and testable.
- Voice command matching must not override normal conversation.

## Remote Access / Development Infrastructure

Remote access is useful for development and operation, but it is not part of LuciferOS Core.

Rules:

- Do not expose RDP or development services directly to the public internet.
- Preferred model: VPN first, then Remote Desktop or service access.
- WireGuard or equivalent VPN is acceptable infrastructure.
- Router/VPN infrastructure must remain outside LuciferOS Core.
- LuciferOS must not depend on one specific VPN product.
- Remote access is for development/operation, not Core runtime logic.

## Development Discipline

- Small milestones.
- One responsibility per milestone.
- Tests before committing.
- Commit and push only when tests pass.
- Keep git clean between milestones.
- Use Markdown documents for project artifacts by default.
- Avoid fragile architecture shortcuts.
- Prefer explicit, testable interfaces over hidden coupling.
- Use Windows PowerShell carefully and verify syntax.
- Avoid large risky PowerShell here-strings.
- Prefer small file overwrites for testable modules.
- Prefer safe line arrays with single-quoted strings for generated files.
- Avoid Markdown triple backticks inside PowerShell double-quoted strings.

## Current Documentation Files

    docs/luciferos_manifest.md
    docs/runtime_modes.md
    docs/memory_architecture.md
    README.md

README should link to the docs above.

## Non-Negotiables

- Do not make HUD the Core.
- Do not dump all memory into prompts.
- Do not auto-store everything the user says.
- Do not bypass policy for memory writes/deletes.
- Do not expose remote desktop/dev services directly to the internet.
- Do not make Ollama the invisible default.
- Do not add PC-control without tool permissions and audit.
- Do not confuse development tooling with LuciferOS runtime.
- Do not build a brittle local prototype when the goal is a durable local platform.

## Test-Protected Architecture Requirements

The following exact requirements are intentionally preserved because tests protect them:

- Memory & Learning Subsystem
- MemoryService
- MemoryStore
- LearningService
- Permission checks
- Audit logging
- LuciferOS must not store everything the user says.
- The user must be able to delete or correct memories.
- Core must be small, deterministic, testable and interface-independent.
- HUD must not own routing, provider selection, permissions, tools, memory or OS actions.
- Default provider must remain offline unless explicitly overridden.
