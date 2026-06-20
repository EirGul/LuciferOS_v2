# LuciferOS — Household AI Operating Assistant
## Authoritative Manifest v1.0

**Status:** Approved governance baseline — 2026-06-20. This document is authoritative when committed at `docs/luciferos_manifest.md`. It governs all later phases until formally amended under Section 0.
**Purpose:** Define the target architecture and governance for LuciferOS as a private, local-first household AI operating assistant.
**Historical reference:** `docs/reference/luciferos_manifest_original_v1.md` remains preserved, unchanged, and non-authoritative.
**Scope:** One trusted household. LuciferOS is not public SaaS, enterprise multi-tenancy, or an unrestricted general-purpose agent.

---

## 0. Authority, document hierarchy and change control

The authoritative design hierarchy shall be:

```text
1. Approved LuciferOS manifest
2. Approved Architecture Decision Records (ADRs)
3. Approved execution plan
4. Approved household policy and security configuration
5. Approved automation definitions
6. Source code, tests and runtime configuration
```

Rules:

- An ADR may clarify, narrow, sequence, or document a decision within the approved manifest.
- An ADR may not override a non-negotiable manifest law.
- A proposed ADR that requires a manifest breach must first trigger an explicit manifest amendment and approval.
- Configuration may instantiate policy but may not redefine non-negotiable architectural laws.
- Automation definitions may use capabilities approved by policy; they may not create new authority.
- The repository must have one live manifest and one live execution plan. Historical source material belongs in `docs/reference/` only.
- A source file, a named test, or a partially wired component is not proof of conformance. Architectural compliance requires evidence of contracts, runtime wiring, boundary tests, and relevant failure behavior.

---

## 1. Mission

LuciferOS shall be a trusted household AI operating assistant for Eirik and household members. It shall support natural conversation, study and work support, household coordination, smart-home control, local PC workflows, documents, and carefully bounded device integrations.

LuciferOS shall be:

- local-first;
- fast in everyday use;
- safe before autonomous;
- conversational before command-driven;
- modular without becoming a distributed-systems project;
- private by default;
- usable by household members without developer knowledge;
- able to use cloud AI only through explicit data-routing policy and consent;
- explainable, controllable, and recoverable as it gains capability.

LuciferOS is not a chatbot with unrestricted tools. It is a household control plane coordinating identity, context, reasoning, policy, capabilities, devices, memory, and response delivery.

---

## 2. Household-first operating model

LuciferOS is for one trusted household and its members, rooms, devices, routines, and projects.

```text
Household
├── members and roles
├── rooms and zones
├── enrolled devices and interfaces
├── shared routines and approved automations
├── household/shared knowledge
├── private member contexts
├── optional project scopes
└── operational and audit state
```

The platform shall not implement public sign-up, subscriptions, generic customer administration, or enterprise tenancy. Household facts must be configuration or governed data, never hardcoded in Core.

A project is a **scope**, not an access domain or privilege. A project may be private to one member or shared by household members; its access domain remains private-member or household as determined by policy.

---

## 3. Non-negotiable architectural laws

1. **Runtime builds. LuciferApplication is the single public use-case boundary. Core orchestrates completed dependencies.**
2. **Core stays small, deterministic in control flow, testable, and platform-independent.**
3. **Conversation is the default; commands and actions are explicit special cases.**
4. **LLMs and other probabilistic systems may suggest and reason; they never have direct authority to act.**
5. **Every side-effecting action follows one canonical path: capability resolution → authorization → policy → confirmation where required → pre-execution decision evidence/audit as policy requires → execution → outcome audit.**
6. **Interfaces, satellites, providers, tools, automations, and adapters may not bypass LuciferApplication/Core to call tools, memory, OS capability, or policy-sensitive stores directly.**
7. **No provider may autonomously retrieve, mutate, or broadly inspect memory. Providers receive only policy-selected, minimized context bundles.**
8. **Providers, tools, interfaces, and adapters are added through contracts and explicit registration, not Core rewrites or automatic plugin discovery.**
9. **Local household operation must degrade safely when internet, cloud AI, or external integrations are unavailable.**
10. **Learning does not grant authority. Recognition does not grant permission. Advanced reasoning does not bypass policy.**
11. **No new automation activates, changes, expands, or reactivates without explicit household-administrator approval.**
12. **Material architecture deviations require a written decision record before implementation.**
13. **Algorithms must be measurable, confidence-aware, explainable at the relevant layer, and reversible where possible; hardcoded utterance growth is not an architecture strategy.**
14. **All external content and observations are untrusted input until validated through bounded contracts and policy.**
15. **No public internet exposure, port forwarding, public tunnel, or remote-control channel exists by default.**
16. **A project, trusted room, observed voice, observed face, or device presence must never elevate authorization by itself.**
17. **Before private, restricted, or secret data persists or trusted sessions operate beyond localhost, LuciferOS must have an approved cryptographic protection, key-management, and secure-transport baseline.**
18. **No runtime component may silently download, install, discover, or execute unapproved code, plugins, models, or dependency updates. Software provenance and update integrity are governed capabilities.**
19. **Break-glass and recovery are exceptional local security procedures: scoped, time-bounded, auditable, revocable, and never a routine remote-access path.**

---

## 4. Local-first definition and network boundary

“Local-first” has four required meanings:

```text
Local execution
    Core, policy, confirmation, audit boundary, and local tools can function
    without internet access.

Local data
    Household, private-member, project-scoped, operational, and audit data
    are stored locally by default.

Local network
    Interfaces and integrations communicate only over explicitly approved
    household-local network paths and authenticated sessions.

Cloud egress
    Data leaves the household only through a policy-approved named provider,
    a declared purpose, scoped/minimized content, and required consent.
```

Rules:

- Loss of internet must not disable local safety checks, local status, confirmation lifecycle, audit decisions, or approved low-risk local household functions.
- LAN access requires explicit device enrollment or authenticated session design before it is enabled beyond the local host.
- Beyond localhost, sensitive requests, responses, session material, and administrative controls must use an approved authenticated and cryptographically protected transport design. Local-network membership alone is not trust or authorization.
- The exact transport, certificate, and key-storage mechanism is a G4 security decision: it must be selected from evidence, documented in an ADR where material, tested for expiry/revocation/failure, and must not be guessed into the foundation manifest.
- Remote access is out of foundation scope and requires a separate ADR, threat model, explicit household approval, and testable revocation path.
- Home Assistant, tablets, voice satellites, desktop HUDs, and other clients are local-network peers or clients; none becomes an independent policy, memory, provider-selection, or tool-execution authority.

---

## 5. Architecture and ownership boundaries

```text
Interface / client
→ interface adapter
→ LuciferApplication
→ Core orchestration
→ ports for policy, memory context, providers, tools, audit and delivery
→ concrete adapters
→ local or external systems
```

### 5.1 Runtime owns

Runtime is the only production composition root. It owns:

- configuration loading and validation;
- secret-provider wiring;
- platform detection;
- dependency composition and explicit registration;
- startup, shutdown, health, diagnostics, and migration coordination;
- service lifecycle and controlled recovery mode;
- one canonical dependency graph.

Runtime must not contain conversation policy, household role logic, provider prompts, or tool-specific business rules.

### 5.2 LuciferApplication owns

LuciferApplication is the single public use-case boundary for API, CLI, HUD, tablet/PWA, voice, and automation triggers. It owns:

- request-scope creation;
- ingress validation and request normalization handoff;
- correlation/request IDs and bounded context propagation;
- calling Core with completed dependencies;
- returning a structured `ResponseEnvelope`;
- preventing interfaces from constructing competing graphs or direct service access.

LuciferApplication does not create a second composition root and does not embed concrete platform/provider/store implementation.

### 5.3 Core owns

Core owns deterministic control-plane behavior:

- request normalization and bounded routing;
- planning coordination;
- capability resolution;
- authorization and policy invocation;
- confirmation state transitions;
- orchestration of provider/tool ports;
- response assembly;
- trace correlation and outcome coordination.

Core must not import concrete providers, persistent stores, Home Assistant clients, OS adapters, UI frameworks, microphone/audio engines, or interface implementations.

### 5.4 Interfaces own

Interfaces own:

- capture of typed, voice, GUI, or API input;
- rendering response, status, and confirmation prompts;
- local presentation preferences;
- secure session interaction as designed by the identity boundary.

Interfaces may not own provider selection, tool execution, memory writes, policy decisions, OS actions, automation execution, or long-lived runtime state.

### 5.5 Adapters own

Adapters own protocol translation, bounded integration behavior, concrete error mapping, and resource-level precondition checks for systems such as Windows/Linux/macOS, Home Assistant, Ollama/cloud AI, storage, printers, cameras, voice engines, and UI delivery channels.

Adapters may not implement household policy, role interpretation, authorization, or independent orchestration.

---

## 6. Canonical contracts and action path

Public architecture boundaries shall use typed, versioned, immutable snapshots. Public contracts include:

```text
RequestContext
NormalizedRequest
IdentityObservation
IntentDecision
Plan
CapabilityRequest
AuthorizationDecision
PolicyDecision
ConfirmationRequest
ConfirmationGrant
ExecutionRequest
ExecutionResult
ResponseEnvelope
AuditEvent
SpeechRecognitionResult
CommunicationDirective
CorrectionProposal
DecisionEvidence
```

Arbitrary dictionaries may exist inside adapters but shall not be public contracts between architecture layers.

Every request must carry bounded context:

```text
household_id
principal_id or anonymous principal
principal_type
role when a human household role is assigned
service_scope_reference when principal_type is service
identity_assurance
session_id
session_assurance
interface_id
device_id
room_or_zone when known
project_id when applicable
privacy_mode
data_classification
request_id
trace_id
platform
```

### 6.1 Canonical action path

```text
1. Capability resolution
   Is there a bounded capability matching the request and target scope?

2. Authorization decision
   Does the principal/session have standing to request this capability?

3. Policy decision
   Does current household policy permit the action considering role, assurance,
   data classification, risk, time, target, state, and context?

4. Confirmation grant
   Where required, has the correct actor given explicit approval for the exact,
   frozen action within the valid session and expiry window?

5. Pre-execution decision evidence
   Record decision evidence before execution. When policy requires durable pre-execution
   audit, persistence must succeed before the side effect; otherwise G4 failure semantics apply.

6. Execution
   Does the adapter execute the same validated action after rechecking necessary
   preconditions?

7. Outcome audit evidence
   What was requested, decided, confirmed, executed, denied, canceled, or failed
   without persisting unnecessary sensitive content?
```

A lower layer may never override a higher layer. A provider output, free-text instruction, tool result, or automation proposal is not a capability grant, authorization decision, policy decision, or confirmation.

### 6.2 Frozen confirmation requirement

A confirmation request must bind at least:

```text
capability/tool identifier
validated arguments
affected resource scope
principal and session
policy/decision version or decision hash
risk and data classification
relevant preconditions
expiry
```

On confirmation, the system must validate session validity, expiry, policy, and necessary preconditions again before execution. A confirmation cannot approve altered arguments, expanded scope, or a substituted action.

---

## 7. Identity, privacy, access, and recovery

### 7.1 Principal model

LuciferOS distinguishes:

```text
Principal type
    human_member | service | anonymous

Role
    household_administrator | adult_member | restricted_member | guest

Identity assurance
    authenticated | trusted_personal_device | observed | unknown

Session assurance
    normal | elevated | expired | revoked
```

`unknown` is an assurance state, not a role. `service` is a principal type, not a household role. Human roles are optional and apply only to `human_member` principals. Service principals use an explicit policy-bound service scope; anonymous principals have no role or service scope.

Roles are policy inputs, not blanket grants. Unknown identity is valid but restrictive.

### 7.2 Multimodal observations

Voice, face recognition, device presence, room presence, and conversational context may be used for greeting, language choice, low-risk personalization, or context hints. They are observations with source and confidence, not independent authority.

They must not independently authorize private data, security systems, cameras, personal e-mail, administrator actions, role elevation, or high-risk device control.

High-risk actions require an appropriate trusted-session path, such as an authenticated personal device, passkey/PIN, or concrete confirmation through a private trusted channel. Shared-room voice confirmation is never sufficient for doors, alarms, credentials, role changes, private data, financial commitments, or administration.

### 7.3 Bootstrap and recovery

- LuciferOS must never have zero household administrators.
- The last administrator cannot be removed or degraded without a controlled local recovery process.
- The first administrator is created only through controlled local bootstrap mode.
- Recovery requires physical/local host access and a separately designed recovery mechanism; it must not create a hidden remote-access path.
- Service principals may never approve automations, manage human roles, elevate permissions, or access private-member scope by default.
- Bootstrap, recovery, role changes, and security-sensitive session changes are security-relevant events and are auditable with minimized evidence.
- A break-glass or recovery transition is local-only, scoped to the minimum recovery purpose, time-bounded, and requires explicit exit/cleanup behavior. It may not create a reusable remote pathway or silently grant a durable elevated session.
- Recovery design must state how affected sessions, device enrollments, credentials, and approval grants are revoked, re-established, or rotated after the incident.

### 7.4 Device enrollment and session lifecycle

A device may contribute trusted-personal-device assurance only after explicit enrollment under household policy. Enrollment is not authorization; it is one bounded assurance signal.

The device and session model must define:

```text
device identifier and owner/principal binding
approved interface and permitted network scope
enrollment approval and audit evidence
session creation, assurance level, expiry, renewal, and inactivity timeout
loss, compromise, revocation, and re-enrollment behavior
administrator and member visibility appropriate to privacy policy
```

Rules:

- A lost, revoked, expired, or policy-incompatible device/session must not retain authority through cached state.
- Revocation must invalidate or render unusable active session material within a defined and testable bound.
- Device/session identifiers and assurance metadata are operational/security data; they are not household memory and must not expose private content in normal diagnostics.
- A trusted personal device may strengthen assurance only within the policy-approved scope. It never bypasses confirmation, data classification, or high-risk restrictions.

---

## 8. Data domains, classification, memory, and learning

### 8.1 Access domains and project scope

```text
Household domain
    Shared rooms, devices, approved routines, shared information, and shared projects.

Private-member domain
    Personal preferences, tasks, documents, account-connected data, and private projects.

Operational domain
    Device state, active sessions, pending confirmations, health, jobs, and approved automation state.

Audit domain
    Minimal decision/action evidence, separated from memory and ordinary conversation content.
```

`project_id` is an optional scope layered onto household or private-member ownership. Data may not move automatically between private and household domains. Explicit sharing creates a new destination record with provenance and policy, not a silent merge.

### 8.2 Data classification

Every request, context bundle, response, audit event, and egress decision shall use a minimum classification:

```text
operational
household
private_member
restricted
secret
```

Rules:

- Output inherits at least the highest relevant input classification.
- A provider cannot lower classification.
- A response classified `private_member` or higher is visual-only by default in shared-room mode unless explicit policy allows otherwise.
- Cloud egress is evaluated against classification and purpose, not merely the apparent tool type.
- Audit stores classification and opaque references rather than raw sensitive content.

### 8.3 Memory lifecycle

LuciferOS distinguishes:

```text
Ephemeral interaction context
    Exists only for active request/session and expires automatically.

Conversation working context
    Bounded short-lived continuity context; not a transcript archive or long-term memory.

Persistent memory
    Explicitly saved or confirmed knowledge with ownership, provenance, access policy,
    retention, correction, export, and deletion behavior.

Operational state
    Pending confirmations, jobs, automation state, device state, and health;
    not personal memory.
```

Memory is not a transcript, a prompt dump, or a hidden profile builder.

Every persistent record requires:

```text
namespace
household/member ownership
optional project scope
source and provenance
confidence
created/updated timestamps
retention/deletion rule
access policy
correction history
```

A provider has no direct memory client, store handle, broad retrieval capability, or mutation authority. Core/Application selects and supplies a minimized `ContextBundle` only after access and policy evaluation. Providers may propose a memory operation; only the canonical action path may execute it.

### 8.4 Learning and corrections

Lucifer may identify patterns and propose preferences, corrections, routines, and automations. It may not silently turn observations into permanent memory, authority, or active automation.

Confirmed speech or interpretation corrections may become scoped, attributable, reversible, reviewable, and deletable member/household vocabulary data. They are configuration/data, never new hardcoded Core branches.

---

## 9. Trust boundaries and untrusted input

The following are untrusted input regardless of whether they originate locally or externally:

```text
typed text
speech recognition output
document and file content
webpage and e-mail content
Home Assistant entity names and state
provider/cloud output
tool output
plugin metadata
imported configuration
camera/audio-derived observations
```

Rules:

- No textual instruction, model response, document content, Home Assistant state, or tool result is authority to execute a side effect.
- Only a validated `CapabilityRequest` progressing through the canonical action path may cause a side effect.
- Tool outputs must be treated as data, not executable instructions.
- LLM-generated plans are proposals and must be validated against tool schemas, target scopes, authorization, policy, confirmation, and budgets.
- No automatic plugin discovery or runtime loading of arbitrary third-party code is permitted in foundation architecture.

---

## 10. Risk, policy, and confirmation

A single fixed numerical risk scale is insufficient as a sole authorization mechanism. Policy shall evaluate at least:

```text
Effect
    read | write | actuate | delete | administer

Data sensitivity
    operational | household | private_member | restricted | secret

Reach
    local process | local device | household LAN | external service | public

Reversibility
    reversible | compensatable | irreversible | uncertain

Security impact
    none | access change | credential change | physical security

Physical impact
    none | low-risk device | safety-relevant | security-critical
```

The system may derive a user-facing `risk_level`, but a tool’s declared risk is a minimum floor. Context may strengthen requirements; it may not weaken them.

### Always-confirm actions

The following always require concrete confirmation through a policy-appropriate trusted channel:

- send e-mail, messages, posts, or shared documents;
- purchases, bookings, payments, or financial commitments;
- unlock a door, garage, or gate;
- disable an alarm or alter security posture;
- delete private data;
- share camera, microphone, biometric, household, or private data;
- change credentials, roles, network settings, or administrator configuration;
- physically print;
- destructive Git actions, system administration, elevation, reset, or recovery actions;
- external/cloud processing of private or higher-classified content unless explicit policy and consent allow it.

Always-confirm capabilities are not eligible for unattended automation in the foundation architecture. Administrator approval to create or activate an automation is never a substitute for a per-instance concrete confirmation. Any future exception requires an explicit manifest amendment, a separate ADR, and a threat model for that capability category.

An explicit request may be sufficient for a low-risk, reversible local action only when policy says so. It is never automatically sufficient for high-risk, external, private, security-relevant, or irreversible action.

---

## 11. Autonomy and automation governance

LuciferOS follows:

```text
Lucifer observes
→ Lucifer proposes
→ an administrator approves a bounded structured rule
→ Lucifer executes only the approved rule version
→ Lucifer records outcomes and may recommend review
```

Automation flow:

```text
natural-language proposal
→ canonical structured rule
→ administrator review
→ approved immutable rule version
→ bounded execution
```

Only a household administrator may approve, activate, modify, expand, suspend, revoke, or reactivate an automation. Other household members may create proposals only.

Every automation includes:

```text
stable id
owner and approving administrator
purpose
trigger and conditions
actions and affected resources
risk and data classification
approved scope and explicit exceptions
service-principal identity
idempotency and retry policy
expiry/review date
disable/rollback path
audit policy
status and immutable rule version
```

Automation states:

```text
draft
→ proposed
→ approved_disabled
→ active
→ suspended
→ expired
→ revoked
```

Rules:

- An active automation has the minimum necessary service-principal scope.
- An automation cannot execute an always-confirm capability unattended.
- An automation has no free LLM planning, broad memory retrieval, dynamic tool discovery, or authority to expand itself at runtime.
- Non-idempotent or uncertain actions are not retried automatically.
- Explicit human action normally has priority over automation for the same resource scope, subject to safety policy.
- Loss of required policy, credential, audit capability, or necessary precondition moves an automation to safe suspended/failed behavior.
- Every person may cancel their own active request. A non-administrator may invoke a bounded runtime emergency stop for an active low-risk execution only. It interrupts the current execution and may create a temporary safety interlock; it does not change the automation definition, owner, approval, or lifecycle state. Only a household administrator may clear an interlock, reactivate, or alter the automation.

---

## 12. Performance and operating modes

```text
Instant path
    Deterministic, no LLM. Status, confirmations, known household commands,
    capability checks, and low-latency local actions.

Local fast path
    Local provider for normal conversation and bounded reasoning.
    No unrestricted agent loop.

Advanced path
    Explicitly selected deeper reasoning, coding, document analysis, or cloud AI.
    It has a goal, tool allowlist, time/step/cost budgets, stop conditions,
    data-routing policy, and approval gates.
```

Rules:

- Core starts without loading a model.
- Heavy modules lazy-load only when needed.
- Cloud use is opt-in by policy, classification, provider, purpose, and request context.
- Provider failure never breaks instant household functions.
- Agent loops are never the default execution model.
- A cloud provider is never a tool executor and never receives raw secrets, unrestricted memory domains, audit data, raw camera/microphone material, or uncontrolled tool payloads.

### Cloud routing baseline

```text
Default
    No cloud request.

Generic/non-sensitive content
    May be permitted by explicit member/household policy to a named provider
    for a defined purpose.

Private, household-sensitive, account-connected, restricted, or secret content
    Requires stricter policy and concrete per-request consent before egress.

Secrets, credentials, raw audit, whole memory domains, raw biometric data,
raw camera/audio material, and unrestricted tool payloads
    Must not be sent to cloud providers.
```

---

## 13. Providers, tools, adapters, concurrency, and time

### 13.1 Providers

Provider declarations include:

```text
provider_id
kind and local/cloud classification
health/availability
supported modalities
streaming and planning support
cost profile
data-handling classification
required credentials
timeouts and fallback eligibility
```

Initial order:

1. offline/system response;
2. local Ollama-compatible provider;
3. cloud adapters only after data-routing policy, consent, and audit boundaries exist.

### 13.2 Tools

A tool is a bounded capability, never arbitrary code execution. It declares:

```text
tool_id and capability
input/output contract version
risk and side-effect class
data-egress class
platform support
required authorization and credentials
resource scope
preconditions
dry-run behavior
timeout and cancellation behavior
idempotency class
conflict behavior
rollback/compensation where relevant
audit category
```

No hidden “last write wins” behavior is allowed among voice, tablet, desktop, automation, background job, or Home Assistant state update for the same resource scope. Tools and policies must define conflict, cancellation, and revalidation behavior before active device control is introduced.

### 13.3 Smart-home gateway

Home Assistant is the first smart-home gateway, not Lucifer Core. A dedicated adapter must discover only approved capabilities, subscribe to bounded state, expose bounded actions, and translate approved actions into Home Assistant calls. It must never expose raw credentials or unrestricted entity inventory to an LLM.

### 13.4 Time and schedules

- Household timezone is explicit configuration.
- Persisted timestamps use UTC.
- Human scheduling interpretation uses household timezone.
- Timeout/deadline behavior uses monotonic clocks where feasible.
- Daylight-saving transitions, clock drift, and missed triggers require defined behavior.
- Every automation must define whether a missed trigger runs late, is skipped, or requires review.

---

## 14. Audit, secrets, cryptographic protections, configuration, retention, and resilience

Audit exists for accountability, debugging, policy review, recovery, and security investigation—not surveillance.

Audit records minimized decision/action metadata such as:

```text
trace id
event type
timestamp
actor/context reference
selected capability/provider
policy decision
confirmation state
outcome/error class
correlation identifiers
data classification
```

By default, audit must not persist raw conversations, prompts, credentials, private documents, full e-mail bodies, camera media, raw microphone data, or unrestricted tool payloads.

Rules:

- Redaction occurs before persistence, not as later cleanup.
- Audit events use opaque references, classifications, hashes, and decision results where practical rather than raw sensitive data.
- Audit is append-only within its retention period.
- Critical state transitions fail closed when durable audit evidence is required before the side effect.
- Read-only work may use explicitly designed degraded behavior and must report safe status without leaking sensitive information.
- Audit retention and access are explicitly policy-governed. Administrative access is not a license to inspect private content that should never have been stored.
- Secret values are outside source control, configuration display, normal diagnostics, and audit.

### 14.1 Cryptographic protection, keys, and session material

Before LuciferOS persists private, restricted, or secret data; stores backups containing such data; or accepts trusted sessions beyond localhost, it must have an approved security design that covers:

```text
protection of persistent data and backups appropriate to the threat model
separation of data from secret/key material where feasible
secret/key creation, storage, access, rotation, revocation, backup, recovery, and disposal
protection of session tokens, enrollment credentials, confirmation grants, and recovery artifacts
approved authenticated transport for client/session traffic beyond localhost
failure behavior when required key, secret, certificate, or secure transport is unavailable
```

Rules:

- Exact algorithms, credential stores, certificate handling, and key providers are implementation decisions for G4; they require evidence, compatibility review, test coverage, and an ADR when the choice materially affects portability, recovery, or threat exposure.
- Host protections, including operating-system account controls or disk protection, may contribute to defense in depth but do not replace application authorization, policy, classification, audit, or session controls.
- Secret/key material, session tokens, recovery artifacts, and unredacted enrollment credentials must never be emitted through normal logs, diagnostics, audit events, or provider context.
- A lost or compromised device, credential, or key must have a documented and testable revocation/recovery path before it can be relied on for trusted operation.

### 14.2 Software provenance, dependency, and update governance

LuciferOS treats code, dependencies, models, plugins, configuration bundles, and updates as supply-chain inputs with security impact.

Rules:

- Production runtime must not silently install packages, fetch executable code, auto-discover unapproved plugins, or activate a newly downloaded model/provider/tool without an explicit governed change.
- Dependencies, runtime packages, and approved model/tool artifacts must have recorded provenance and reproducible version selection appropriate to the deployment. Lock files, checks, or equivalent evidence are required where the ecosystem supports them.
- Updates must be explicit, reviewable, testable, auditable, and reversible. An update may not silently broaden capabilities, cloud routing, network exposure, data retention, or authorization scope.
- Security-sensitive updates or artifact-source changes require administrator authorization, explicit confirmation, pre-change validation, rollback preparation, and clear restart/reload semantics.
- Supply-chain checks must be practical for a household-managed system. LuciferOS must not introduce enterprise infrastructure merely to satisfy this rule; the implementation must remain proportionate and locally operable.

### Configuration as an administrative capability

Security-sensitive configuration includes provider activation, cloud routing, allowlists, Home Assistant scope, administrator roles, network binding, transport/certificate settings, key/secret-provider wiring, audit policy, confirmation policy, tool enablement, artifact sources, and update channels.

Changes require:

```text
administrator authorization
explicit confirmation
pre-change validation
audit
rollback path
clear reload/restart semantics
```

### Retention, deletion, backup, and restore

Before persistent household/private data grows, LuciferOS must define:

- export scope and authorization;
- deletion and erasure behavior;
- backup retention after primary deletion;
- approved cryptographic/key and session-material protection strategy appropriate to the deployment;
- backup access control and the relationship between primary deletion, backup retention, and recovery keys;
- restore procedure, periodic restore tests, and a documented test of key/secret availability during restore;
- minimal audit evidence that deletion was processed without retaining deleted content.

---

## 15. Unified interaction and delivery

A member may interact through voice, typed chat, PC, tablet, mobile, HUD, CLI, or API. Conversation/context is shared only where policy permits; private and shared contexts are never merged automatically.

Each response may include:

```text
spoken_summary
visual_summary
detailed_content
delivery_options
privacy classification
requires_confirmation
risk level
action status
trace id
```

On a trusted personal PC, typed and spoken input may both receive a concise spoken summary when policy/profile permits. Long answers should offer a dedicated visual panel/window. Sensitive material defaults to visual-only or neutral acknowledgement.

Interaction profiles:

```text
normal
silent
headphones
private
shared-room
night mode
```

Profiles affect delivery, never authorization, data classification, risk, or automation scope.

---

## 16. Interfaces and experience

Interfaces are replaceable:

```text
CLI
local API
responsive web/PWA for tablet/mobile
desktop HUD
voice satellite
future native shells
```

The purple neon face and HUD are product identity and presentation. HUD may show conversation, household status, active jobs, confirmations, diagnostics, and long-form output. HUD must not own routing, provider selection, permission/authorization, memory mutation, tool execution, automation execution, or long-lived runtime state.

There is one authoritative application runtime even when clients, satellites, or presentation shells multiply.

---

## 17. Algorithmic reasoning, speech resilience, and affective communication

LuciferOS shall use algorithms where they produce measurable reliability, safety, accessibility, or performance gains. It shall not substitute growing collections of brittle phrase lists, fuzzy aliases, or hidden heuristics for a defined decision process.

### 17.1 Algorithm classes and authority

```text
Deterministic algorithms
    Routing thresholds, authorization/policy evaluation, confirmation state machines,
    retry/backoff, retention, scheduling, and rollback rules.

Probabilistic perception
    Speech recognition, entity resolution, speaker/face observations,
    conversational-friction signals, and optional vision/audio interpretation.
    These always carry confidence and uncertainty.

Generative reasoning
    Local or cloud models used for conversation, explanation, candidate interpretation,
    planning, and drafting.
```

No probabilistic or generative output independently grants identity, permission, automation authority, or high-risk tool execution.

### 17.2 Speech resilience and disfluency support

```text
audio
→ endpointing / turn-taking profile
→ speech recognition with alternatives and confidence where available
→ optional conservative disfluency-aware normalization
→ household vocabulary and entity resolution
→ contextual intent candidates
→ policy-aware decision: execute / confirm / clarify / ask to repeat
→ explicit correction feedback
```

Rules:

- Preserve original transcript/equivalent evidence only for the active interaction unless the user opts into retained correction data.
- Do not auto-correct text into a new meaning merely because similarity is high.
- Use dialogue, room/device context, and approved vocabulary for bounded disambiguation.
- Ambiguous, low-confidence, or higher-risk requests clarify or confirm.
- Confirmed corrections are scoped configuration data, not new Core branches.
- Evaluation uses consented local corpus/simulation and operational measures, not anecdotes alone.

### 17.3 Affective communication, not emotion claims

LuciferOS may adapt delivery to task context, explicit preference, and cautiously inferred interaction signals. It must not claim knowledge of a person’s true emotional state, diagnose mood/health, manipulate users, or present simulated inner emotion as fact.

It may adjust:

```text
tone
brevity
speech rate and pause tolerance
structure
explanation depth
clarification strategy
spoken versus visual delivery
```

Affective signals are advisory only. They may not alter identity assurance, authorization, policy, risk, automation scope, or access to private data.

No persistent emotional profile, raw audio/video retention for affect analysis, or biometric/emotion-model use exists by default. Any future use requires separate threat-model ADR, local processing preference, retention rule, explicit household approval, and deletion/export path.

---

## 18. Operations, deployment, and diagnostics

Initial deployment uses one household-controlled local host. Core and adapters remain cross-platform by design, but simultaneous production support for Windows, Linux, and macOS is not required initially.

Operational goals:

- one clear start path;
- controlled local bootstrap and recovery;
- health checks and safe diagnostics;
- graceful startup/shutdown;
- safe provider/device fallback;
- backup/export/restore plan;
- secret isolation and key/session-material lifecycle controls;
- migration/version compatibility;
- governed dependency/update provenance and rollback;
- household-readable status;
- no normal-use dependency on terminal commands.

Do not introduce microservices, external event brokers, containers, vector databases, distributed schedulers, unrestricted plugin marketplaces, or native mobile apps unless a documented requirement proves one-runtime architecture insufficient.

---

## 19. Evidence before code

Every material change follows:

```text
1. Define outcome and non-goals.
2. Inspect real source and contracts.
3. Verify external assumptions from primary documentation or a bounded spike.
4. Write contract, acceptance criteria, threat/failure behavior, and rollback path.
5. Implement one cohesive vertical slice.
6. Run targeted tests, full suite, static checks, and relevant fault/privacy tests.
7. Review diff and runtime behavior against this manifest.
8. Commit only approved scope.
9. Update decision register and phase-status documentation.
```

### Architecture Decision Records

An ADR is mandatory before changing a non-negotiable rule, adding a runtime owner, persistent store, cloud flow, identity mechanism, network exposure, remote access, security integration, or expanding permission/scope.

Each ADR contains:

```text
decision
context and evidence
alternatives rejected
manifest rule affected
security/privacy/performance impact
migration and rollback
tests/acceptance criteria
approver
review or expiry date
```

---

## 20. Solid-foundation gate

Feature work resumes only when:

- one runtime composition root and one public LuciferApplication boundary exist;
- public contracts are typed, bounded, versioned, and immutable;
- capability resolution, authorization, policy, confirmation, execution, and audit are separate;
- household request context has roles, assurance, data classification, and deny-by-default behavior;
- audit is redacted, minimized, and has deterministic critical-failure behavior;
- memory has ownership, access control, lifecycle, and provider-boundary enforcement;
- interfaces cannot create competing dependency graphs;
- Core has no direct provider/store/platform/interface coupling;
- configuration and network-exposure changes follow administrative safeguards;
- full suite runs in reproducible environment;
- static checks have no accepted inherited debt after the foundation correction phase;
- a provider/tool/interface can be added without Core rewrite;
- architecture, privacy, fault-injection, and policy-matrix tests prove the negative boundaries;
- documentation reflects actual code and decisions.

---

## 21. Explicit non-goals before foundation is passed

Do not build before relevant gates are complete:

- unrestricted PC/browser agent;
- face/voice identity system;
- automatic alarm or door control;
- broad cloud-memory retrieval;
- native mobile apps;
- multi-agent orchestration;
- default vector database;
- microservice/event-bus architecture;
- enterprise identity management;
- always-on household profiling;
- public remote access;
- autonomous automation generation or expansion.

---

## 22. Governing principle

LuciferOS becomes more capable only when it becomes more explainable, controllable, private, and recoverable.

A feature that cannot state its owner, data scope, classification, capability, authorization path, policy path, confirmation behavior, audit behavior, failure mode, concurrency behavior, and rollback/deletion path is not ready for implementation.
