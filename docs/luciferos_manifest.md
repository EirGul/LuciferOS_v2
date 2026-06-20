# LuciferOS Manifest v3

## Status and authority

This is the current architectural contract for LuciferOS after Milestone 140.

- Project path: `C:\Users\Eirik Gulbrandsen\developer\luciferos_v2`
- Repository: `https://github.com/EirGul/LuciferOS_v2.git`
- Branch: `main`
- Completed milestones: 1–140
- Verified test suite: 593 passed
- Last known git state: clean and pushed to `origin/main`
- Preferred repository location: `docs/luciferos_manifest.md`

This document is authoritative when project shortcuts, tests, legacy code or convenience conflict with the intended architecture.

It must be updated and committed whenever a material architectural decision changes.

---

## Mission

LuciferOS is a local-first, modular AI agent platform. It must become a fast, safe, extensible conversational assistant that can operate through CLI, API, HUD, voice and eventually a tablet dashboard.

The long-term platform includes:

- local and optional cloud-capable reasoning providers
- voice interaction and replaceable HUD/tablet interfaces
- explicit memory and learning
- permissions, confirmation gates and audit trails
- modular tools for PC control, files, browser, email, calendar, Office, smart home, camera/admin and connected devices

LuciferOS must not become:

- a fragile command script
- a thin wrapper around a single provider
- a HUD-owned application
- an uncontrolled logger or prompt-memory dump
- a collection of ad hoc patches without clear boundaries

---

## Non-negotiable architecture principles

Core must be small, deterministic, testable and interface-independent.

1. **Core is small, deterministic, testable and interface-independent.**
2. **Conversation is the default.** Commands are explicit special cases and must not hijack ordinary language through aggressive fuzzy matching.
3. **Interfaces are replaceable shells.** HUD, voice, CLI and API may collect input and render output, but do not own routing, providers, tools, memory, permissions or OS actions.
4. **Providers are backends, not LuciferOS identity.** Offline mode remains a safe default. Ollama and future cloud providers are explicit, replaceable choices.
5. **State-changing actions require policy, confirmation where appropriate and audit.**
6. **Memory is explicit, bounded, policy-aware, auditable, correctable and deletable.**
7. **No direct interface-to-tool or interface-to-memory writes.**
8. **No direct Core access to SQLite or store internals.**
9. **No provider may autonomously retrieve, mutate or broadly inspect memory.**
10. **Prefer clean refactors early over accumulating patches on a faulty foundation.**

---

## Intended runtime architecture

```text
Interface
→ API/runtime adapter
→ LuciferApp
→ Core
→ Router / Planner / Permission policy
→ Provider or Tool adapter
→ Response builder
→ Interface rendering
```

Runtime logic belongs behind application/service boundaries, never inside HUD code or one-off scripts.

Current verified local Ollama chain:

```text
HUD
→ FastAPI
→ ApiService
→ LuciferApp
→ Core
→ OllamaProvider
→ local Ollama model
```

Current local model:

```text
eirik-qwen3:latest
```

Documented runtime modes:

```text
Safe/offline: start_lucifer_api.bat
Local AI/Ollama: start_lucifer_api_ollama.bat
```

---

## Interface and HUD rules

Current and planned interfaces:

- CLI
- API
- HUD
- voice
- future tablet dashboard

Interfaces may:

- collect user input
- render response/state
- show later confirmation prompts
- display runtime/provider status returned from API/runtime

Interfaces must not:

- route intents
- select providers
- call tools directly
- write memory directly
- bypass permission policy
- execute OS actions
- own long-term state

HUD state contract:

```text
online: blue
offline: grey-blue
thinking: yellow
speaking: purple
chat/active dialog: green
error/angry: red
```

HUD is presentation-only.

---

## Provider strategy

- Default provider remains `offline` unless explicitly overridden.
- Local Ollama mode is valid through explicit runtime selection.
- Cloud providers may be optional later, but remain permission-aware and non-foundational.
- Provider selection stays outside HUD logic.
- Provider fallback must be safe and observable.
- Provider prompts must not receive raw memory records or unbounded database contents.

---

## Memory & Learning Subsystem

### Memory subsystem: core rules

Memory is a first-class LuciferOS subsystem.

Memory must not be:

- uncontrolled prompt text
- random JSON dumping
- automatic storage of everything the user says
- a hidden profile builder
- a way for an interface or provider to bypass permissions

Memory must be:

- explicit
- bounded
- scope-separated
- policy-aware
- auditable
- correctable and deletable
- separate from normal conversation unless a defined retrieval path authorizes use

Required memory types:

```text
fact
preference
project_state
correction
command_alias
relationship
task_context
user_instruction
```

Required scopes:

```text
global
project
session
interface-specific
tool-specific
```

Write rules:

- Explicit phrases such as `husk at ...` and `lær at ...` may create learning requests.
- Normal conversation is not automatically stored.
- High-impact memory requires confirmation.
- Deletes require confirmation.
- The user can inspect, correct and delete memory.
- Write/delete operations are audit-logged.

Read rules:

- Retrieval must be explicit, relevant, deterministic and bounded.
- Memory must never be dumped wholesale into provider prompts.
- Project memory must remain separated from global personal memory.
- A conversational retrieval must never create a pending action or mutate memory.
- Core must request retrieval through a narrow service boundary, never through direct store or SQLite access.

---

## Memory implementation status after M140

Memory package:

```text
lucifer_os/memory/
```

Relevant modules:

```text
models.py
store.py
sqlite_store.py
service.py
policy.py
audit.py
commands.py
resolver.py
resolution_plan.py
pending.py
selection.py
selection_audit.py
executor.py
retrieval.py
context.py
learning.py
```

### Write, correction and selection status

Implemented and tested:

- `MemoryItem`, `MemoryType`, `MemoryScope`
- `MemoryStore`, `InMemoryMemoryStore`, `SQLiteMemoryStore`
- `MemoryService`
- write/update/delete policy and audit boundaries
- explicit memory commands
- correction/delete target resolution
- pending confirmation flow
- candidate selection for ambiguous correction/delete
- complete selection audit lifecycle

Selection audit lifecycle is complete for the current phase:

```text
selection request created
selection request rejected
selection request expired
selection candidate rejected
selection candidate accepted
selection pending action prepared
selection request cancelled
```

Selection safety rules:

```text
audit delivery succeeds
→ state transition may complete

audit delivery fails
→ state is preserved
→ no pending action is created
→ no memory item is changed
```

Selection audit events use minimal bounded identifiers/reason codes and must not contain raw user text, candidate content, proposed correction text or provider prompts.

### Retrieval status

Existing retrieval components were hardened in M139–M140:

- `MemoryQuery` requires:
  - non-empty text
  - explicit scopes
  - explicit types
  - supported retrieval purpose
  - non-empty source
  - bounded result limit
  - bounded total context budget
- `MemoryRetrievalPurpose`:
  - `conversation_response`
  - `project_assistance`
  - `explicit_memory_search`
- `MemoryRetrievalPolicy` evaluates requests before `store.list()`.
- Denied retrieval must not read the store.
- `MemorySnapshot` is immutable and deliberately excludes mutable/sensitive fields such as metadata, tags and source.
- `MemorySearchResult` contains snapshot, deterministic score and matched terms.
- Ranking is deterministic: score descending, then memory id ascending.
- `MemoryContextBuilder` supports a total character budget and reports truncation.
- Core, runtime, API, HUD, voice, providers and prompts are still disconnected from retrieval.

Current conservative read-policy:

- Blocks retrieval of:
  - `command_alias`
  - `relationship`
  - `user_instruction`
- Blocks:
  - `interface-specific`
  - `tool-specific`
- Blocks `global` scope for:
  - `conversation_response`
  - `project_assistance`
- Allows `global` only for explicit memory search when all other filters are safe.

This policy is intentionally conservative and not a final trusted-project/user-context authorization model.

---

## Retrieval read-path target

The intended future read-path is:

```text
CoreRequest
→ Core decides retrieval is relevant
→ bounded MemoryQuery
→ MemoryRetrievalPolicy
→ deterministic MemoryRetrievalService
→ explicit MemoryRetrievalResult
→ retrieval audit
→ Core-owned internal context state
→ later dedicated provider-context builder
→ provider input
```

Hard rules:

- Core does not access SQLite or `MemoryStore` directly.
- Retrieval policy executes before store access.
- Providers never choose scope, type, limits or policy.
- Providers never receive raw memory records.
- A dedicated context builder, not the provider, owns formatting.
- Retrieval audit must not log memory content, raw query text or provider context by default.
- No automatic learning, vector retrieval, embeddings, semantic expansion or LLM relevance scoring in the first read-path implementation.

---

## Required retrieval implementation sequence

The next retrieval work must proceed as larger, cohesive milestones rather than small patch chains.

### Milestone 141 — Retrieval result and context contract migration

Implement this as one coordinated memory-layer migration:

```text
MemoryQuery
→ request id, explicit query/purpose/source/filter/budget fields

MemoryRetrievalService.retrieve(query)
→ MemoryRetrievalResult:
   denied | no_match | matched
   reason code
   applied scopes/types
   immutable bounded snapshots
   stable ordering
   result count
   context-budget/truncation state

MemoryContextBuilder.build(retrieval_result)
→ deterministic formatting/projection
→ uses retrieval result/query budget
→ does not own a competing policy budget
```

Rules:

- Do not introduce a parallel retrieval model beside existing `MemoryQuery`, `MemoryRetrievalService`, `MemorySearchResult` and `MemoryContextBuilder`.
- Prefer a direct migration from `search()` to `retrieve()` over preserving a long-lived legacy public API.
- `MemoryContextBuilder` becomes projection/formatting, not a separate policy authority.
- No Core/provider/API/HUD/voice/runtime changes in M141.
- No retrieval audit implementation in M141.

### Milestone 142 — Retrieval audit and complete memory read-path regression

Implement retrieval audit as one coherent behavior:

```text
retrieve(query)
→ policy evaluation
→ denied | no_match | matched
→ bounded retrieval audit event
→ return retrieval result
```

Audit must include only bounded operational metadata:

- retrieval request id
- source identifier
- purpose
- outcome
- count returned
- scopes/types applied
- bounded reason code

Audit must not include:

- memory content
- raw user query
- provider prompt/context
- hidden/inaccessible memory metadata

Dependency composition must inject one explicit policy/audit setup. Do not allow disconnected defaults to make services audit to unrelated sinks.

### Milestone 143 — Core retrieval hook without provider injection

Only after M141–M142 are green and reviewed:

```text
CoreRequest
→ Core decides if retrieval is applicable
→ bounded retrieval query
→ result retained as Core-internal state
→ normal response behavior remains unchanged
```

No provider prompt injection in M143.

Before M143, harden Core audit behavior: `request_received` currently records raw request text and metadata in its trace. That must be minimized/redacted before retrieval or memory-related state can influence Core request handling.

### Milestone 144 — Controlled provider-context injection

Only after M143:

```text
no retrieval
→ provider input unchanged

denied retrieval
→ no memory context

no match
→ no memory context

matched retrieval
→ bounded deterministic MemoryContext
→ provider receives only this dedicated context product
```

---

## Safety and permissions

- Read-only operations may be low friction only after policy allows them.
- Writes, destructive operations and external actions must be permission-gated.
- Confirmation gates are mandatory where risk requires them.
- OS, browser, email, document, smart-home, camera/admin and device actions go through tool adapters and permission policies.
- Audit records meaningful state-changing actions and bounded operational events.
- Interfaces never bypass permission or audit boundaries.

---

## Tool/plugin strategy

Future tools may include:

- local files
- browser
- email
- calendar
- Office documents
- Git/project workflows
- Home Assistant and smart home
- camera/admin
- printer/connected devices
- local OS/app control

Rules:

- tools are registered
- tools declare risk
- tools are permission-gated
- meaningful changes are audited
- tools are called through Core/runtime
- lazy loading is preferred
- interfaces do not invoke tools directly

---

## Engineering and workflow rules

- Use Windows PowerShell instructions only.
- Keep steps short and verifiable.
- Use small, testable milestones.
- Start each milestone with explicit manifest alignment.
- Run targeted tests first, then the full suite.
- Commit only after full suite passes.
- Keep the repository clean and pushed after each completed milestone.
- Prefer Markdown files for project artifacts.
- Avoid long PowerShell here-strings.
- Avoid fragile exact-block replacement commands.
- For complex edits, use a generated, syntax-checked Python patch script.
- Patch scripts must be compiled before delivery.
- Before delivering a patch, perform a pre-flight review:
  - inspect affected contracts and existing tests
  - check import/export changes
  - check test assumptions against changed values
  - validate syntax
  - verify no competing service/policy/audit defaults are introduced
- Prefer larger cohesive contract migrations over serial micro-patches when a lifecycle or read-path is already understood.
- Do not use test count alone as proof of architectural progress.
- Explicitly record deviations from the manifest and correct course early.

---

## Chat continuity rule

The assistant must actively monitor chat length and context load.

Before a technical milestone becomes unsafe to continue in the current chat:

1. stop before starting the larger change
2. create an updated Markdown transfer summary
3. include project state, test count, git state, last milestone, exact next step, architectural decisions and known risks
4. instruct the user to start a new chat with the current manifest and transfer summary

This rule exists to preserve technical precision and avoid degraded continuity.

---

## Legacy manifest compatibility contract

The following statements remain explicit compatibility requirements for the existing manifest regression tests and do not weaken the architecture defined above.

- LearningService remains a future memory-learning boundary and must not auto-store ordinary conversation.
- Permission checks are mandatory before state-changing or higher-risk actions.
- Audit logging records bounded operational and state-changing events.
- LuciferOS must not store everything the user says.
- The user must be able to delete or correct memories.
- HUD must not own routing, provider selection, permissions, tools, memory or OS actions.
- Default provider must remain offline unless explicitly overridden.

