# LuciferOS Manifest

## Purpose

LuciferOS is a local-first, modular AI agent platform. It is designed to become a fast, safe, extensible personal assistant that can operate through multiple interfaces such as HUD, voice, CLI and API.

LuciferOS must not be built as a fragile command script or a thin wrapper around one external assistant. The system must have its own Core, own runtime model, own provider abstraction, own permission layer, own audit trail, and eventually its own memory and learning subsystem.

## Core Principles

- Core must be small, deterministic, testable and interface-independent.
- Voice, HUD, CLI and API are replaceable interfaces.
- Providers are replaceable backends, not the identity of LuciferOS.
- Offline mode must remain available as the safe default.
- Ollama and other model providers must be explicit runtime/provider choices.
- Tools and platform actions must be modular and permission-gated.
- HUD must not own routing, provider selection, permissions, tools, memory or OS actions.
- All meaningful state-changing actions must be auditable.
- The system must prefer explicit intent over aggressive fuzzy command matching.
- Commands are special cases; conversation is the default interaction model.

## Runtime Architecture

LuciferOS should follow this boundary:

- Interface receives user input.
- API or runtime converts input into a Core request.
- Core handles routing, planning, permissions and provider/tool selection.
- Providers generate language responses when needed.
- Tools perform controlled actions only through explicit permission boundaries.
- Interfaces render the result without owning business logic.

Current verified chain:

- HUD
- FastAPI
- ApiService
- LuciferApp
- Core
- OllamaProvider
- Local Ollama model

## Provider Strategy

- Default provider must remain offline unless explicitly overridden.
- Local Ollama mode is valid and should be available through explicit startup/runtime selection.
- Future cloud providers may be added, but must remain optional and permission-aware.
- Provider choice must stay outside HUD logic.
- Provider status may be displayed in HUD, but HUD must only display status returned from API/runtime.

## HUD Strategy

- HUD is a visual control and feedback surface.
- HUD may display API status, provider status, adapter status, face state, chat output and future system panels.
- HUD must not become the Core.
- HUD must not directly call tools, select providers, write memory or execute OS actions.
- HUD face states should remain presentation-only.

Current visual state contract:

- online: blue
- offline: grey-blue
- thinking: yellow
- speaking: purple
- chat/active dialog: green
- error/angry: red

## Memory & Learning Subsystem

LuciferOS must include memory and learning as a first-class subsystem, but it must not be implemented as random prompt text or uncontrolled JSON dumping.

Memory must be its own architecture layer:

- MemoryService
- MemoryStore
- LearningService
- Retrieval/context injection
- Permission checks
- Audit logging

Core may request relevant memory before provider calls, but Core must not directly own storage details.

LuciferOS must support at least these memory types:

- fact
- preference
- project_state
- correction
- command_alias
- relationship
- task_context
- user_instruction

Memory must support at least these scopes:

- global
- project
- session
- interface-specific
- tool-specific

Each stored memory item should include:

- id
- type
- scope
- content
- source
- confidence
- created_at
- updated_at
- tags
- audit reference where relevant

Learning rules:

- LuciferOS must not store everything the user says.
- Explicit phrases like 'husk at' and 'lær at' may create durable memory.
- Sensitive or high-impact memory must require confirmation.
- The user must be able to ask what Lucifer remembers.
- The user must be able to delete or correct memories.
- Memory writes must be audit-logged.
- Memory retrieval must be relevant and bounded, not a full dump into every prompt.
- Project memory must be separated from global personal memory.

Memory is required for the long-term goal, but full memory implementation should be built only after the current Core/API/HUD/provider foundation is stable.

## Safety and Permissions

- Read-only operations may be allowed with low friction.
- Write operations must be permission-gated.
- Destructive operations must require explicit confirmation.
- OS, browser, email, document, smart-home and camera actions must go through tool adapters and permission policies.
- Audit logs must record meaningful state-changing actions.
- The user must remain in control of memory, tools and external actions.

## Long-Term Capability Goals

LuciferOS should eventually support:

- natural conversation
- local voice assistant
- visual HUD with animated face
- local memory and learning
- local Ollama/provider routing
- smart-home control through Home Assistant or equivalent
- PC control through permission-gated tools
- browser workflows
- email workflows
- Office/document workflows
- calendar workflows
- camera/admin functionality later
- tablet dashboard/control surface

These capabilities must be added through modules and adapters, not by bloating Core.

## Current Development Discipline

- Small milestones.
- Tests before committing.
- Commit and push only when tests pass.
- Keep git clean between milestones.
- Avoid fragile architecture shortcuts.
- Prefer explicit, testable interfaces over hidden coupling.
- Update this manifest when a new architectural requirement becomes fundamental.
