# LuciferOS Transfer Summary after Milestone 91

## Purpose

Use this to continue LuciferOS development in a new chat without losing context.

It captures the project goal, current architecture, repository state, completed milestones, coding method that worked, PowerShell pitfalls, and the recommended next milestone.

## User workflow preferences

- Respond in Norwegian.
- Be direct, blunt and practical.
- Use Windows PowerShell commands.
- One milestone at a time.
- Small, testable steps.
- Start technical milestones with manifest/architecture check.
- Include A/B troubleshooting.
- Do not assume direct file access.
- User runs commands and pastes output.
- Keep git clean after each milestone.
- Use Markdown project artifacts by default.
- Avoid fragile multi-line exact replacement patches.
- Avoid long here-strings.

## Project location and repo

Local path:

    C:\Users\Eirik Gulbrandsen\developer\luciferos_v2

Repository:

    https://github.com/EirGul/LuciferOS_v2.git

Branch:

    main

Last known state:

    Milestone 1–91 complete
    Tests: 230 passed
    Git: clean
    GitHub: origin/main up to date

## High-level goal

LuciferOS is a local-first modular AI agent platform. It should become a conversational assistant with local runtime, HUD, voice, memory, permissions, audit, smart-home integration and later PC-control.

It must not become a fragile script, a thin provider wrapper, a HUD-owned app, or an uncontrolled memory/logger.

## Current architecture

Intended flow:

    Interface
    -> API/runtime adapter
    -> LuciferApp
    -> Core
    -> Router / Planner / Permission policy
    -> Provider or Tool adapter
    -> Response builder
    -> Interface rendering

Verified Ollama/HUD chain:

    HUD
    -> FastAPI
    -> ApiService
    -> LuciferApp
    -> Core
    -> OllamaProvider
    -> local Ollama model

## Runtime modes

Documented in:

    docs/runtime_modes.md

Safe/offline mode:

    start_lucifer_api.bat
    provider: offline

Local AI/Ollama mode:

    start_lucifer_api_ollama.bat
    provider: ollama

Current local model:

    eirik-qwen3:latest

Good PowerShell JSON smoke pattern:

    $body = @{
        text = "Hei Lucifer"
        metadata = @{
            source = "api-smoke"
        }
    } | ConvertTo-Json -Depth 5

    Invoke-RestMethod -Uri "http://127.0.0.1:8787/chat" -Method Post -ContentType "application/json; charset=utf-8" -Body $body

Do not use raw JSON strings for PowerShell API tests.

## HUD status

HUD is under:

    hud/

Verified:

- API health check.
- Chat to API.
- Runtime/provider status display.
- Adapter status display.
- Face states.
- HUD works against API in Ollama mode.

Face state contract:

    online: blue
    offline: grey-blue
    thinking: yellow
    speaking: purple
    chat/active dialog: green
    error/angry: red

HUD must remain presentation-only.

## Docs status

Current docs:

    docs/luciferos_manifest.md
    docs/runtime_modes.md
    docs/memory_architecture.md
    README.md

README links to manifest, runtime modes and memory architecture.

## Memory subsystem status

Memory package:

    lucifer_os/memory/

Implemented files:

    __init__.py
    models.py
    store.py
    service.py
    learning.py
    policy.py
    audit.py
    retrieval.py
    context.py

Implemented concepts:

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

Current behavior:

- Explicit learning phrases are recognized: `husk at`, `lær at`, `remember that`, `learn that`.
- Normal conversation is not automatically stored.
- Writes pass through MemoryPolicy.
- Empty memory is rejected.
- High-impact memory requires confirmation.
- Deletes require confirmation.
- Operations produce audit events.
- Retrieval is filtered and limited.
- Context builder produces bounded context.
- No provider prompt injection yet.
- No persistent store yet.

Do not connect memory to provider prompts yet.

## Milestone history summary

Milestone 1–28: Core/config/providers/adapters, LuciferApp, routing/planning/permissions/audit foundations.

Milestone 29–44: API schema, service, server, client, startup/check scripts and environment override basics.

Milestone 45–69: HUD client/controller/preview/static graphical HUD/face states/colors/design contract.

Milestone 70: Provider/chat reality check.

Milestone 71: Local Ollama model set to `eirik-qwen3:latest`; Python cache removed from tracking.

Milestone 72: API provider override with `LUCIFER_PROVIDER`.

Milestone 73: API Ollama smoke passed.

Milestone 74: `start_lucifer_api_ollama.bat`.

Milestone 75: Ollama API start script smoke passed.

Milestone 76: HUD smoke test against API in Ollama mode passed.

Milestone 77: HUD runtime provider/status visibility.

Milestone 78: Browser smoke test of provider/status badges passed.

Milestone 79: Manifest created with memory architecture requirement.

Milestone 80: Manifest protection tests.

Milestone 81: Runtime modes documentation.

Milestone 82: README links to manifest and runtime docs.

Milestone 83: Memory subsystem skeleton.

Milestone 84: Memory policy boundary.

Milestone 85: MemoryPolicy enforced in MemoryService.

Milestone 86: Memory audit event model.

Milestone 87: MemoryAuditSink connected to MemoryService.

Milestone 88: Memory retrieval contract.

Milestone 89: Memory context builder.

Milestone 90: Memory architecture documentation.

Milestone 91: README links to memory architecture docs.

## Coding method that worked

Reliable method:

1. Define one milestone.
2. State manifest check.
3. Create/overwrite small files.
4. Add tests immediately.
5. Run full pytest.
6. Commit only after tests pass.
7. Push.
8. Confirm git clean.

Good file-writing pattern:

    $path = Join-Path (Resolve-Path ".\some_existing_folder") "file.py"

    $lines = @(
    'line 1',
    'line 2'
    )

    [System.IO.File]::WriteAllLines($path, $lines, [System.Text.UTF8Encoding]::new($false))

For root files:

    $path = Join-Path (Resolve-Path ".") "file.ext"

For existing files:

    $path = Resolve-Path ".\README.md"
    $text = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($path, $text, [System.Text.UTF8Encoding]::new($false))

Git pattern:

    py -m pytest
    git add .\relevant_path_1 .\relevant_path_2
    git commit -m "Milestone XX: concise description"
    git push
    git status

## PowerShell lessons learned

### Avoid Markdown triple backticks inside double-quoted PowerShell strings

PowerShell uses backtick as escape. This caused parser errors.

Bad:

    $lines = @(
    "```text",
    "something",
    "```"
    )

Better: use indented Markdown code blocks in generated docs:

    $lines = @(
    'Example:',
    '',
    '    start_lucifer_api.bat'
    )

### Do not use raw JSON strings for Invoke-RestMethod

Bad:

    $body = '{"text":"Hei Lucifer"}'

Good:

    $body = @{
        text = "Hei Lucifer"
        metadata = @{ source = "api-smoke" }
    } | ConvertTo-Json -Depth 5

### Avoid fragile multi-line `.Replace()`

Exact multi-line replacements failed when the text did not match exactly.

Better:

- Overwrite small files completely.
- Use small targeted replacements only with unique one-line anchors.
- Verify with `Select-String` when needed.

### Always reset `$path`

Never rely on an old `$path` value.

### Do not use `Resolve-Path` on new files

Bad:

    Resolve-Path ".\tests\new_file.py"

Good:

    Join-Path (Resolve-Path ".\tests") "new_file.py"

### Avoid huge here-strings

Use line arrays and `WriteAllLines` instead.

### Run commands separately

Do not accidentally append `py -m pytest` after a file write call.

### Tests must isolate environment variables

`LUCIFER_PROVIDER=ollama` made an offline API test fail. Fix tests by explicit provider:

    client = TestClient(create_api_app(provider_name='offline'))

### Keep Python cache ignored

`.gitignore` should include:

    __pycache__/
    *.pyc
    *.pyo
    *.pyd

## First command in next chat

    cd "C:\Users\Eirik Gulbrandsen\developer\luciferos_v2"
    git status
    py -m pytest

Expected:

    nothing to commit, working tree clean
    230 passed

## Recommended next milestone

Milestone 92: Persistent MemoryStore design.

Recommended scope:

- Decide persistence strategy.
- Define requirements before implementation.
- Keep Core/API/HUD untouched.
- Keep `InMemoryMemoryStore` working.
- Prefer SQLite eventually for durable memory.
- JSON can be used only as temporary/debug store.

Do not jump yet to provider prompt injection, automatic memory extraction, HUD memory editing, API memory endpoints, semantic/vector memory, PC control or voice memory commands.

## Remote access note

Remote access was discussed but not made part of Core.

Conclusion:

- The Windows workstation must be on because it contains the project, Ollama and GPU.
- Windows is currently Home, so built-in Microsoft RDP host is not available.
- Safer remote setup: VPN first, then remote desktop/service access.
- Do not expose RDP directly to internet.
- Remote infrastructure is outside LuciferOS Core.

## Transfer phrase for next chat

We are continuing LuciferOS_v2 from Milestone 91. Project path is `C:\Users\Eirik Gulbrandsen\developer\luciferos_v2`, repo `https://github.com/EirGul/LuciferOS_v2.git`, branch `main`. Last known status: 230 passed, git clean, docs and memory architecture committed. Follow the manifest strictly. Use small PowerShell-safe milestones with A/B troubleshooting. Next planned milestone is Milestone 92: Persistent MemoryStore design.
