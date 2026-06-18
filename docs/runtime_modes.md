# LuciferOS Runtime Modes

LuciferOS currently supports two verified API runtime modes.

## 1. Safe / Offline Mode

Start script:

    start_lucifer_api.bat

Expected provider:

    offline

Purpose:

- Safe default mode.
- Does not require Ollama or external model access.
- Useful for API/HUD testing when provider behavior must be deterministic.
- Must remain available as the default fallback mode.

Health check:

    Invoke-RestMethod -Uri "http://127.0.0.1:8787/health"

Expected health value:

    provider_name : offline

## 2. Local AI / Ollama Mode

Start script:

    start_lucifer_api_ollama.bat

Expected provider:

    ollama

Purpose:

- Runs LuciferOS API with the local Ollama provider.
- Enables local model responses through API and HUD.
- Keeps provider selection explicit instead of changing the safe default.
- Preserves the Core/API/provider boundary.

Health check:

    Invoke-RestMethod -Uri "http://127.0.0.1:8787/health"

Expected health value:

    provider_name : ollama

Chat smoke test:

    $body = @{
        text = "Hei Lucifer, svar kort på norsk: fungerer API med Ollama?"
        metadata = @{
            source = "runtime-mode-smoke"
        }
    } | ConvertTo-Json -Depth 5

    Invoke-RestMethod -Uri "http://127.0.0.1:8787/chat" -Method Post -ContentType "application/json; charset=utf-8" -Body $body

Expected result:

- Response should not be the offline fallback.
- Response should come from the local Ollama provider.
- HUD should display provider: ollama when API is started in Ollama mode.

## Boundary Rules

- HUD may display runtime status, but must not choose providers.
- Provider selection belongs to API/runtime configuration.
- Core must remain interface-independent.
- Offline mode must remain available.
- Ollama mode must remain explicit.
- Runtime mode changes must not bypass permissions, audit, tools, memory rules, or Core boundaries.

## Current Verified Chain

    HUD -> FastAPI -> ApiService -> LuciferApp -> Core -> OllamaProvider -> local Ollama model
