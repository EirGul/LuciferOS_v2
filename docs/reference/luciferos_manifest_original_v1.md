# LuciferOS v2 — Manifest for ny start

Oppdatert: 2026-06-17
Ny prosjektmappe: `C:\Users\Eirik Gulbrandsen\developer\LuciferOS_v2`
Formatregel: **kun Markdown-filer (`.md`) som standard**
Status: **Dette er styringsdokumentet for fresh coding av LuciferOS v2**

---

## 1. Kortversjon i dagligtale

LuciferOS skal bygges på nytt fra friske øyne.

Målet er ikke å lage en tilfeldig chatbot, og heller ikke å bygge videre på en prototype som nesten er riktig. Målet er å bygge en rask, trygg, lokal-first AI-agentplattform som kan vokse over tid uten at kjernen blir full av patcher.

Lucifer skal etter hvert kunne være en personlig assistent som kan samtale, styre PC-en, håndtere filer, bruke nettleser, lage dokumenter, hjelpe med e-post, koble seg mot smart-hjem, bruke kamera/printer/enheter og kjøre på Windows, Linux og macOS.

Men starten skal være mye smalere:

**Første mål er en solid Core.**

Core skal være hjernen og kontrolltårnet. Voice, HUD, API og CLI skal være utskiftbare grensesnitt. Modeller som Ollama, DeepSeek, Claude, OpenAI eller Kimi skal være providers. Handlinger som filer, apps, e-post, browser, Office og Home Assistant skal være tools. Windows/Linux/macOS-forskjeller skal ligge i platform adapters.

Lucifer skal være rask i hverdagen. Enkle kommandoer skal ikke vente på en stor AI-modell. Tunge analyser skal bare brukes når det faktisk trengs.

---

## 2. Absolutt beslutning: ny v2-start

LuciferOS v2 skal starte i ny mappe:

```text
C:\Users\Eirik Gulbrandsen\developer\LuciferOS_v2
```

Gammel prototype skal ikke blandes inn i ny kode.

Gammel LuciferOS/OpenJarvisVoice-kode kan brukes som referanse for læring, men skal ikke kopieres ukritisk inn i v2.

Regel:

```text
Ny kodebase skal være ren.
Gammel prototype skal være referanse, ikke fundament.
```

---

## 3. Hva LuciferOS skal bli

LuciferOS skal være:

```text
lokal personlig AI-agentplattform
+ PC-agent
+ samtaleassistent
+ smart-home logikklag
+ prosjektadmin
+ digital arbeidsflytassistent
```

Langsiktig skal Lucifer kunne:

* samtale naturlig
* forstå forskjell på samtale, kommando, handling og usikkerhet
* kjøre lokalt så langt det er mulig
* bruke lokal modell via Ollama eller tilsvarende
* bruke eksterne modeller bare når det trengs
* støtte DeepSeek, Claude, OpenAI, Kimi eller andre providers senere
* åpne og bruke apper
* lese og skrive filer
* lage og redigere dokumenter
* bruke nettleser
* lage e-postutkast
* sende e-post etter eksplisitt bekreftelse
* bruke kalender senere
* styre Home Assistant/smart-hjem senere
* bruke kamera/printer/skanner senere
* ha trusted project-modus
* kjøre på Windows, Linux og macOS
* kunne flyttes til for eksempel Linux-server eller Mac mini/Mac M4 senere

---

## 4. Hva LuciferOS ikke skal være

LuciferOS skal ikke være:

```text
en stor monolitt
en tilfeldig chatbot med tools
en wrapper rundt OpenJarvis
en LLM som får styre PC-en direkte
en Windows-only løsning
en tung agent som må tenke lenge på alt
et system der core.py endres hver gang vi legger til noe nytt
```

LuciferOS skal heller ikke bygge inn voice/HUD direkte i Core. Voice og HUD skal være utskiftbare interfaces.

---

## 5. Hovedprinsipp

Lucifer Core skal være:

```text
liten
deterministisk
rask
trygg
modulær
testbar
cross-platform
utvidbar via kontrakter
```

Core skal styre flyten:

```text
input
→ normalisering
→ lærte korrigeringer
→ intent/router
→ planner
→ permission check
→ tool/provider via registry
→ audit trace
→ strukturert response
```

Core skal ikke være stedet der all spesiallogikk samles.

---

## 6. Core skal inneholde

LuciferOS v2 Core skal bestå av disse hoveddelene:

```text
LuciferRuntime
ConfigLoader
PlatformDetection
ProviderRegistry
ToolRegistry
AdapterRegistry
IntentRouter
Planner
PermissionEngine
AuditTrace
State/Session
ResponseBuilder
```

### 6.1 LuciferRuntime

Runtime bygger systemet.

Runtime skal:

* lese config
* oppdage operativsystem
* registrere platform adapter
* registrere providers
* registrere tools
* validere systemstatus
* starte Core med ferdige avhengigheter

Runtime bygger. Core orkestrerer.

### 6.2 ConfigLoader

Config skal styre hvilke providers, tools og adapters som er aktive.

Config skal kunne inneholde:

* default provider
* default model
* aktive providers
* aktive tools
* API-key miljøvariabelnavn
* risk levels
* confirmation rules
* platform settings
* audit/logging
* performance settings

Feil eller manglende config skal gi trygg fallback.

### 6.3 ProviderRegistry

Providers er modell-/svarmotorer.

Eksempler:

* offline
* ollama
* deepseek
* claude
* openai
* kimi
* lokal Apple/MLX-provider senere

Core skal ikke importere DeepSeek, Claude eller Ollama direkte.

Ny provider skal kunne legges til med:

```text
ny provider-fil
config-entry
test
```

Ikke omskriving av Core.

### 6.4 ToolRegistry

Tools er handlinger Lucifer kan utføre.

Eksempler:

* `app.open`
* `file.read`
* `file.write`
* `git.status`
* `browser.open`
* `email.draft`
* `email.send`
* `office.create_document`
* `home_assistant.turn_on_light`

Tools skal ha metadata:

* navn
* beskrivelse
* capability
* risk level
* platform support
* krever bekreftelse
* krever credential
* dry-run support
* input schema
* output schema

Core skal ikke ha en hardkodet liste som:

```python
self.tools = [WindowsTools(), FileTools(), DevTools()]
```

Det var nyttig i prototype, men er feil grunnmur for v2.

### 6.5 PlatformAdapter

LuciferOS skal kunne kjøre på Windows, Linux og macOS.

Core skal aldri kalle direkte:

```text
notepad.exe
powershell
bash
zsh
osascript
xdg-open
open -a
```

Core skal be om en plattformuavhengig handling:

```text
open_app("text_editor")
```

Adapter oversetter:

```text
Windows → notepad.exe
macOS   → open -a TextEdit
Linux   → xdg-open / valgt editor
```

OS-forskjeller skal ligge i adapters, ikke i Core.

### 6.6 PermissionEngine

PermissionEngine er obligatorisk mellom plan og handling.

Risikomodell:

```text
Risk 0 — samtale
Risk 1 — trygg lokal handling
Risk 2 — endrende lokal handling
Risk 3 — ekstern eller irreversibel handling
Risk 4 — admin/trusted project
```

Handlinger skal ikke utføres uten riktig permission.

### 6.7 AuditTrace

Alt viktig skal logges strukturert:

* input
* normalisert input
* intent
* plan
* permission decision
* confirmation request
* provider selected
* tool selected
* tool args
* tool result
* error
* final response

Ingen viktig handling uten audit event.

### 6.8 ResponseBuilder

Core skal returnere strukturert respons:

```text
voice_summary
visual_text
visual_channel
requires_confirmation
risk_level
action
trace_id
```

Voice får kort svar. HUD/terminal/API/dokument får langt svar.

---

## 7. Hva Core aldri skal inneholde

Core skal ikke inneholde:

* Windows-spesifikke kommandoer
* Linux-spesifikke kommandoer
* macOS-spesifikke kommandoer
* voice/mikrofon/audio
* HUD-layout
* API-serverdetaljer
* direkte DeepSeek/Claude/OpenAI/Kimi-kode
* direkte Home Assistant-logikk
* e-postimplementasjon
* Office-implementasjon
* browser automation
* hardkodet provider-liste
* hardkodet tool-liste
* API keys
* hemmeligheter
* agent-loop som standard

---

## 8. Ytelsesprinsipp: Lucifer skal være kjapp

Lucifer skal ikke være tung å starte eller treg å bruke.

LuciferOS skal ha tre hastighetsnivåer:

```text
1. Instant path
   Enkle kommandoer uten LLM.

2. Local fast path
   Vanlig samtale med lokal rask provider.

3. Advanced path
   Tung analyse, større resonnementer, coding, dokumentanalyse.
```

Enkle kommandoer skal ikke bruke LLM:

* status
* hjelp
* avbryt
* ja utfør
* bekreft ja utfør
* åpne app
* git status
* vis providers
* vis tools

Regler:

```text
Core skal starte uten aktiv LLM.
Tools/providers skal lazy-loades.
Provider metadata kan lastes raskt.
Tung kode lastes først når den trengs.
Default lokal provider kan holdes varm.
Advanced providers brukes bare eksplisitt.
Agent-loop brukes bare i advanced mode.
```

Lucifer skal være:

```text
dynamisk i struktur
konservativ i runtime
```

Mange muligheter i systemet, men få ting aktive per request.

---

## 9. Sikkerhetsprinsipp

Lucifer skal være trygg før den er mektig.

Sikkerhet betyr ikke at alt skal være tregt. PermissionEngine skal være rask og deterministisk.

Regler:

```text
Samtale kan være rask.
Handling må være kontrollert.
Risikohandling må være bekreftet.
Ekstern handling må være eksplisitt bekreftet.
Admin/trusted project krever ekstra tydelighet.
```

LLM skal ikke få direkte tool-kontroll.

Modellen kan foreslå. Core bestemmer.

---

## 10. Cross-platform-prinsipp

LuciferOS skal kunne kjøres på:

* Windows
* Linux
* macOS
* mulig Mac mini/Mac M4
* mulig Linux-server senere

Men ikke alt er likt på alle plattformer.

Derfor:

```text
Core skal være plattformuavhengig.
OS-spesifikke ting skal ligge i adapters.
Voice/HUD/API/CLI skal være interfaces.
```

Portabilitetsnivåer:

```text
Level 0: Core portable
Level 1: CLI portable
Level 2: API/HUD portable
Level 3: model providers portable
Level 4: file/dev tools mostly portable
Level 5: app control adapter-based
Level 6: GUI automation OS-specific
Level 7: voice/camera/printer OS-specific
```

---

## 11. Interface-prinsipp

Voice, HUD, CLI og API er bare grensesnitt.

De skal:

```text
ta imot input
sende input til Core
vise/spille av respons
```

De skal ikke:

```text
eie routing
eie permissions
eie tool execution
eie providervalg
```

Første interface bør være CLI.

Voice og HUD kommer senere når Core er solid.

---

## 12. Provider-prinsipp

Providers skal være utskiftbare.

Provider-kontrakt bør ha:

```text
name
kind
health()
answer()
supports_streaming
requires_api_key
supports_vision
supports_tools
cost_profile
```

Men provider skal ikke utføre handlinger på PC-en.

Handlinger går via tools og permissions.

---

## 13. Tool-prinsipp

Tools skal være kontrollerte handlingsmoduler.

Tool skal ikke være fri kode som modellen kan bruke ukritisk.

Tool må ha:

```text
klar capability
input schema
risk level
platform support
confirmation policy
audit metadata
dry-run support
test
```

Ny tool skal kunne legges til uten Core-endring.

---

## 14. Advanced mode

Advanced mode er for tunge oppgaver:

* dyp analyse
* coding/refaktorering
* dokumentanalyse
* planlegging over mange steg
* eksterne modeller
* agent-loop
* multi-step reasoning

Advanced mode skal ikke være standard.

Eksempler:

```text
“åpne notisblokk”
→ instant path

“hva mener du om dette?”
→ local fast path

“gjør avansert analyse av hele prosjektet”
→ advanced path
```

---

## 15. Foreslått ny mappestruktur

```text
LuciferOS_v2/
    README.md
    docs/
        LuciferOS_manifest_v1.md
        LuciferOS_transfer_summary_v1.md

    lucifer_os/
        __init__.py

        core/
            core.py
            runtime.py
            config.py
            events.py
            errors.py

        routing/
            intent.py
            router.py

        planning/
            plan.py
            planner.py

        permissions/
            risk.py
            engine.py
            confirmation.py

        registries/
            provider_registry.py
            tool_registry.py
            adapter_registry.py

        providers/
            base.py
            offline.py
            ollama.py

        tools/
            base.py
            app.py
            file.py
            dev.py

        platform/
            detection.py
            capabilities.py

        adapters/
            base.py
            windows.py
            macos.py
            linux.py

        memory/
            learning_store.py
            memory_store.py

        audit/
            audit_log.py
            trace.py

        response/
            response.py
            builder.py

        interfaces/
            cli.py
            api.py
            voice.py
            hud.py

    config/
        lucifer.yaml
        providers.yaml
        tools.yaml
        permissions.yaml

    tests/
```

---

## 16. Første milestones for ny start

### Milestone 0 — Manifest og overføring

* ferdig manifest
* ferdig chattesammendrag
* ny mappe bestemt
* ingen kode ennå

### Milestone 1 — Clean repo og package skeleton

* opprette `LuciferOS_v2`
* git init
* minimal Python package
* README
* tests folder
* ingen features

### Milestone 2 — Runtime + config + platform detection

* Runtime starter
* config loader
* platform detection
* status viser OS og config
* tester

### Milestone 3 — Registries

* ProviderRegistry
* ToolRegistry
* AdapterRegistry
* registrere metadata
* ingen tung lazy-load ennå
* tester

### Milestone 4 — Offline provider + response model

* offline provider
* strukturert response
* CLI test interface
* ingen Ollama ennå

### Milestone 5 — Routing + planning

* intent router
* planner
* samtale vs handling vs confirmation
* ingen model-agent-loop

### Milestone 6 — Permissions + audit

* risk levels
* confirmation flow
* audit trace
* dry-run

### Milestone 7 — Basic tools via registry

* app tool
* file tool
* dev/git status
* platform adapter boundary

### Milestone 8 — Ollama provider

* lokal provider
* fallback
* optional warmup/keep-alive
* ikke tung default hvis ikke konfigurert

### Milestone 9 — Status/diagnostics

* vis aktive providers
* vis aktive tools
* vis platform capabilities
* vis config
* vis performance mode

### Milestone 10 — Første API/HUD/voice vurdering

Ikke implementer voice/HUD før Core er stabil.

---

## 17. Regler for videre arbeid

* Kun Markdown-filer som standard.
* Ikke DOCX/PDF med mindre eksplisitt bedt om.
* Ikke bland gammel og ny kode.
* Ikke lag store PowerShell here-strings.
* Ikke gi Linux/bash når bruker jobber i PowerShell.
* Bruk små, verifiserte PowerShell-kommandoer.
* Bruk nedlastbare `.md` eller små patchfiler ved behov.
* Test etter hver liten milestone.
* Commit etter hver fungerende milestone.
* Stopp og vurder arkitektur hvis Core begynner å få for mye ansvar.

---

## 18. Brutal sannhet som skal styre prosjektet

Det er bedre å bruke tid på riktig Core nå enn å spare tid og ende med en nesten-riktig assistent som må patches i stykker.

LuciferOS v2 skal ikke imponere først med mange features.

Den skal imponere med:

```text
riktig struktur
rask respons
trygg handling
klar arkitektur
lett utvidelse
cross-platform design
testbarhet
```

Når dette sitter, kan Lucifer vokse raskt uten å kollapse.
