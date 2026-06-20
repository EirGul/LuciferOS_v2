# LuciferOS v2

Fresh start for LuciferOS v2.

Project root:
C:\Users\Eirik Gulbrandsen\developer\LuciferOS_v2

Principles:
- Clean v2 codebase
- No mixing with old prototype
- Core first
- Modular, testable, cross-platform architecture
- Voice, HUD, API and CLI are interfaces, not Core

Current milestone:
- Milestone 1: clean repo and package skeleton

## Development environment

The bootstrap environment is verified with CPython 3.13.13.

```powershell
uv sync --group dev
uv run pytest -q
uv run ruff check .
```

## Project documentation

- [LuciferOS Manifest](docs/luciferos_manifest.md)
- [Runtime Modes](docs/runtime_modes.md)
- [Memory Architecture](docs/memory_architecture.md)

The manifest defines the architectural boundaries, memory and learning requirements, provider strategy, safety rules, and long-term goals for LuciferOS.

The runtime modes document explains the verified safe/offline and local Ollama API startup modes.

The memory architecture document explains the isolated memory subsystem, policy gate, audit model, retrieval contract, context builder, and current non-integration boundaries.
