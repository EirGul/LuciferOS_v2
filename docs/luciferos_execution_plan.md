# LuciferOS — Evidence-First Step-by-Step Architecture Plan
## Authoritative Evidence-First Execution Plan v1.0

**Status:** Approved governance baseline — 2026-06-20. This plan is authoritative when committed at `docs/luciferos_execution_plan.md`. No coding phase begins until the preceding gate has passed.
**Working rule:** We do not continue coding because a feature sounds useful. We first prove architecture, contracts, constraints, trust boundaries, and failure behavior.

---

## Executive decision

Do **not** start a full rewrite today.

The current repository contains useful work: package structure, automated tests, reproducible environment, offline/local provider paths, interfaces, and an isolated memory subsystem. But memory-related work advanced ahead of the composition, policy, audit, ownership, and lifecycle boundaries required for safe integration. The present live manifest is stale and does not fully express the household-first operating model.

That supports **controlled consolidation**, not blind continuation and not blind full restart.

```text
freeze feature work
→ approve target manifest and plan
→ documentation-only governance commit
→ read-only audit of actual repository against target
→ decide preserve/refactor/replace by boundary
→ build foundation gates in dependency order
→ add household capabilities as safe vertical slices
```

A package-level replacement remains allowed if evidence later proves a boundary cannot be repaired economically. A whole-repository reset is not justified until the audit exists.

---

# Operating rules for every phase

1. One phase has one architecture objective.
2. Each phase begins with written pre-flight and ends with explicit acceptance criteria.
3. Real source is inspected before any change is proposed.
4. External API/device/library assumptions are verified from primary documentation or a bounded feasibility spike.
5. Work outside the active phase is frozen.
6. Every change states manifest alignment, affected boundary, and non-goals.
7. Every side-effecting behavior is tested for allow, deny, confirm, cancel, expiry, conflict, and failure where relevant.
8. No new test/static-check debt is introduced. The inherited baseline is explicitly tracked until resolved in G2.
9. Full suite, applicable static checks, fault/privacy tests, and diff review pass before commit after G2.
10. Repository is clean after each approved phase.
11. Any material deviation has an ADR before implementation—not an explanation afterward.
12. No broad transformation scripts, guessed file contents, permanent Codex permissions, or quick patches crossing multiple architectural boundaries.
13. Code is committed only after explicit review and approval of the narrow phase scope.
14. No phase may rely on unreviewed runtime downloads, automatic plugin discovery, unbounded update channels, or undocumented key/session material. Supply-chain, transport, and recovery assumptions are evidence requirements, not implementation guesses.

---

# Governance and baseline vocabulary

## Evidence classifications for G1

Each target requirement must be classified as:

```text
IMPLEMENTED
PARTIALLY IMPLEMENTED
DECLARED BUT NOT WIRED
MISSING
CONTRADICTED
NOT YET DUE
UNVERIFIED / INSUFFICIENT EVIDENCE
```

A source file name, class name, or test name is not enough for `IMPLEMENTED`. Evidence must show relevant contract, runtime wiring, and behavior/tests at the correct boundary.

## Static-check baseline

The repository currently has two known pre-existing Ruff unused-import findings. This is baseline evidence, not accepted permanent debt.

```text
G0/G1
    Record exact baseline. Do not create any new static-check findings.

G2
    Repair or explicitly resolve the inherited findings as part of composition/contract
    consolidation, unless evidence proves a tightly-scoped exception is necessary.

After G2
    Full suite and static checks must be green without accepted inherited debt.
```

---

# G0 — Vision, manifest, governance, and documentation lock

**Codex reasoning:** High
**Code changes:** None. Documentation-only work only after explicit approval of final text.

## Objective

Turn the household vision into one authoritative target architecture, stop document drift, and preserve the historical source without mixing it with live governance.

## Work

- Finalize the proposed manifest and execution plan from the reviewed drafts.
- Preserve original v1 only as immutable historical reference.
- Replace the stale current manifest only after explicit approval.
- Create ADR/deviation template.
- Create one phase-status document: active freeze, approved phase, evidence, next gate, known risks, and baseline check status.
- Ensure document hierarchy is recorded: manifest → ADR → plan → policy/config → automation → code.

## Allowed

- Markdown governance documents.
- Read-only source inspection only when later G1 begins.
- Documentation-only commit after review and explicit approval.

## Blocked

- Memory retrieval integration.
- New tools/providers/smart-home/voice/HUD/PC-control features.
- Production refactors.
- Core behavior changes.
- Traceability audit before governance documents are approved.

## Exit gate

- One approved authoritative manifest.
- One approved authoritative execution plan.
- One documented source of truth and historical-reference rule.
- One explicit feature freeze.
- ADR/deviation process that cannot override non-negotiable manifest laws.
- Documentation-only commit approved as a separate narrow action.

---

# G1 — Read-only repository traceability and reset decision

**Codex reasoning:** High
**Code changes:** None.

## Objective

Prove what the present repository actually does versus the approved target architecture, without modifying code or documentation during the audit.

## Read-only audit areas

```text
composition root and lifecycle
LuciferApplication/public entry boundary
Core boundaries and imports
public contracts and versioning
interfaces and alternate dependency graphs
providers, registries, and adapter ownership
authorization, policy, confirmation, and action path
audit, secrets, cryptographic/key/session-material boundaries, retention, backup/restore
device enrollment, session expiry/revocation, bootstrap, and recovery boundaries
memory, learning, and provider-context boundary
automation/runtime ownership
configuration, transport, network-exposure, software provenance, dependency lock, and update paths
deployment scripts and diagnostics
tests, static checks, and reproducibility
```

## Required classification and evidence

For every target requirement:

```text
classification
manifest section
exact source/test/config paths
runtime wiring evidence
behavior/failure-test evidence
risk if retained unchanged
recommended action: preserve | isolate | refactor | remove | defer | replace
```

## Required output

- Traceability matrix with exact source/test/config paths.
- Complexity inventory: preserve / isolate / refactor / remove / defer / replace.
- Explicit evidence-based recommendation: controlled consolidation, package-level replacement, or constrained restart.
- Baseline record for tests/static checks.
- No patches, rewrites, commits, or documentation edits during the audit.

## Exit gate

- Every next code change has an evidence path and target-manifest section.
- Preserve/refactor/replace decision is written and approved.
- G2–G5 scope is confirmed or adjusted from evidence.
- No code change has been made during G1.

---

# G2 — Canonical composition, application boundary, and minimal contracts

**Codex reasoning:** High

## Objective

Create one application dependency graph and stable minimum public contracts before policy, memory, or new capabilities gain power.

## Work

- Establish one Runtime as production composition root.
- Establish one `LuciferApplication` as public use-case boundary.
- Identify and remove competing factories/composition paths.
- Ensure interface/API/CLI/HUD entry points receive completed dependencies only through the application boundary.
- Define immutable/versioned contract conventions.
- Define minimum `RequestContext`, `NormalizedRequest`, `ResponseEnvelope`, correlation, and error contracts without prematurely freezing G3/G4 semantics.
- Remove Core construction/import of concrete providers, stores, interfaces, and platform clients.
- Resolve inherited Ruff/static-check baseline debt or narrowly document its removal path within this phase.

## Allowed

- Composition-root refactor.
- Interface-adapter rewiring.
- Minimal request/response/correlation contract migration.
- Import-boundary and composition tests.
- Static-check baseline repair.

## Blocked

- New memory behavior.
- New tools/providers.
- Home Assistant integration.
- HUD/voice behavior.
- Final policy/authorization semantics beyond placeholders needed for compilation.
- Audit persistence redesign.

## Exit gate

- One tested composition owner.
- One tested LuciferApplication boundary.
- Core does not construct/import concrete providers, stores, platform clients, or interfaces.
- API/CLI/HUD routes use the same application graph where those routes exist.
- Minimal public models are immutable snapshots with versioning convention.
- Architecture tests prove no alternate production composition root.
- Full suite and static checks pass green.

---

# G3 — Household identity, authorization, policy, confirmation, and action substrate

**Codex reasoning:** High

## Objective

Add the household governance model before tools, automations, cloud routing, or memory gain power.

## Work

- Define `PrincipalType`, `Role`, `IdentityAssurance`, and `SessionAssurance` contracts.
- Define role-null and service-scope semantics so anonymous/service principals never inherit a human household role.
- Define bounded `RequestContext` including household/member/session/interface/device/room/project/privacy/classification context.
- Define canonical action sequence: capability resolution → authorization → policy → confirmation → pre-execution decision evidence/audit as policy requires → execution → outcome audit evidence.
- Replace ambiguous public `PermissionDecision` terminology with separate `AuthorizationDecision` and `PolicyDecision` contracts.
- Implement deny-by-default policy evaluation.
- Define data classification baseline and policy inputs.
- Define frozen pending-confirmation lifecycle, expiry, cancellation, revalidation, and trusted-channel requirements.
- Define low-risk runtime emergency-stop/interlock semantics separately from automation lifecycle transitions; a non-administrator stop must not alter automation definition, owner, approval, or lifecycle state.
- Define controlled local bootstrap, last-administrator protection, recovery, and break-glass boundary at contract/policy level.
- Define device enrollment, trusted-device assurance, session creation/expiry/revocation, and loss/compromise handling contracts without treating device presence as authorization.
- Test unknown, guest, restricted member, adult, administrator, service, and anonymous contexts.

## Allowed

- Household identity model without biometric authorization.
- Role/context/assurance contracts.
- Authorization, policy, and confirmation engine.
- Fake tools and controlled clocks for policy tests.
- Controlled local bootstrap/recovery and device/session lifecycle contract tests.

## Blocked

- Active automations.
- E-mail sending.
- Alarm, door, or camera control.
- Cloud private-data use.
- Memory-in-conversation.
- Voice/face authorization.
- Remote access.

## Exit gate

- Every action is evaluated with explicit context, authorization, policy, and confirmation state.
- Unknown identity is more restrictive than known identity.
- High-risk confirmation requires trusted/private session path by policy, not shared-room voice alone.
- Confirmation binds exact frozen scope and revalidates before execution.
- Last administrator cannot be removed without controlled local recovery behavior.
- Device enrollment, expiry, revocation, and recovery paths are explicit, policy-governed, and tested.
- A break-glass transition is local, scoped, time-bounded, auditable, and cannot create durable remote or hidden elevated access.
- Policy matrix tests cover allow, deny, confirm, cancel, expiry, changed precondition, revocation, failure, bounded runtime emergency-stop/interlock behavior, and rejection of unattended always-confirm automation.
- Full suite and static checks pass.

---

# G4 — Audit, secrets, configuration, retention, backup, and operational safety

**Codex reasoning:** High

## Objective

Make decisions explainable, minimized, cryptographically protected where required, recoverable, and safe before persistent household/private data, trusted LAN clients, or external tools grow.

## Work

- Define `AuditEvent`, redaction-before-persistence, retention, and critical failure semantics.
- Replace raw-text audit with redacted, bounded decision/action evidence.
- Define fail-closed audit behavior for critical state transitions and explicit degraded behavior for read-only activity.
- Establish secret-provider boundary; no secrets in source, config display, audit, normal diagnostics, or error reports.
- Define approved protection requirements for persistent private/restricted/secret data, backups, session material, enrollment credentials, and client transport beyond localhost; select concrete mechanisms only from evidence and record material decisions in ADRs.
- Define key/secret/session-material lifecycle: creation, storage, access, rotation, revocation, recovery, disposal, and failure behavior.
- Define configuration sensitivity categories and administrative change path.
- Define software provenance, dependency locking/reproducibility, artifact approval, update review, and rollback requirements. Runtime auto-installation, automatic plugin discovery, and uncontrolled update channels remain prohibited.
- Define retention/deletion/erasure behavior, backup scope, access control, restore procedure, key/secret availability during restore, and restore-test requirements.
- Add safe health diagnostics, error reporting, controlled shutdown, and migration/version compatibility expectations.
- Define time, timezone, monotonic deadline, DST, and missed-trigger conventions needed by later automations.

## Allowed

- Audit contract/storage redesign.
- Safe diagnostics and health endpoints.
- Secret/key/session-material abstraction and controlled test doubles.
- Configuration administration boundary.
- Local-client transport/session boundary design and test fixtures.
- Dependency/update provenance design and test fixtures.
- Backup/restore design and test fixtures.
- Tests for redaction, immutability, fault injection, retention, key/session revocation, restore, secure-transport failure, and update/rollback behavior.

## Blocked

- Retrieval integration that depends on legacy audit.
- New persistent domains beyond bounded migration/test scaffolding.
- Device-control features.
- Active automations.

## Exit gate

- Audit cannot persist raw conversation, sensitive payloads, credentials, or secret values by default.
- Sensitive actions have traceable but minimized audit.
- Required critical audit write is durable before the side effect or the action fails closed.
- Read-only degraded behavior is deterministic and user-visible without leakage.
- Security-sensitive configuration changes have authorization, confirmation, validation, audit, and rollback semantics.
- Required private/restricted/secret persistence, trusted-session material, and beyond-localhost client traffic have an approved, tested protection/key/session/transport baseline before use.
- Software dependencies, update sources, and artifacts have governed provenance, review, test, and rollback behavior; runtime auto-installation or auto-discovery is prohibited.
- Backup/restore requirements and tests, including key/secret availability and revocation/recovery behavior, are defined before household/private persistence expands.
- Full suite and static checks pass.

---

# G5 — Memory and learning redesign before integration

**Codex reasoning:** High

## Objective

Retain only memory and learning behavior that meets household access, classification, policy, audit, and lifecycle rules.

## Work

- Audit existing memory against G2–G4 contracts.
- Define ephemeral interaction context, conversation working context, persistent memory, and operational state boundaries.
- Introduce household/private-member ownership and optional project scopes.
- Add provenance, classification, correction, deletion, export, retention, and access control.
- Enforce provider-context boundary: provider receives only policy-selected minimized context bundle and has no memory port.
- Ensure mutable store records never escape public APIs.
- Migrate write/update/delete/selection/retrieval in coherent slices.
- Keep retrieval disconnected from Core/provider prompts until final gate.

## Allowed

- Memory contracts and store migration.
- Scoped fixtures and test data.
- Compatibility/migration strategy.
- Policy-enforced memory management.
- Correction vocabulary lifecycle.

## Blocked

- Automatic conversation storage.
- Broad prompt injection of memory.
- Provider-directed retrieval/mutation.
- “Learned” automation activation.
- Camera/audio identity storage.
- Cloud retrieval of private or broad memory domains.

## Exit gate

- One supported public memory boundary.
- Every persistent memory read/write/selection requires access context and classification.
- Private, household, project-scoped, operational, and audit data cannot mix by default.
- Correction, deletion, export, retention, and backup interaction are tested.
- Providers cannot retrieve or mutate memory directly.
- Core remains store-independent.
- Full suite and static checks pass.

---

# G6 — Local conversation backbone and response-delivery contracts

**Codex reasoning:** Medium

## Objective

Make Lucifer useful for local conversation without granting uncontrolled authority or prematurely introducing real voice infrastructure.

## Work

- Stabilize offline and local-provider conversation behavior through the composition root.
- Implement task routing: instant / local-fast / advanced request.
- Implement `ResponseEnvelope`: spoken summary text, visual summary, detailed content, delivery options, classification, confirmation state, and action status.
- Implement `CommunicationDirective` contract and delivery policy.
- Define privacy-aware profiles: normal, silent, headphones, private, shared-room, night.
- Support typed input with a **delivery contract** that may request concise speech where permitted.
- Add full-answer panel/window contract without making HUD or TTS runtime owners.
- Ensure affective adaptation never changes identity, authorization, policy, automation, or private-data rules.

## Allowed

- Local Ollama adapter through composition root.
- Safe provider fallback.
- Response delivery policy and presentation contracts.
- Text-first API/interface tests.
- Null/test delivery adapter or text simulation of spoken summary.

## Blocked

- Real TTS/ASR/microphone integration.
- Cloud private-data use by default.
- Unbounded agent loops.
- Production tools beyond demonstration/test capabilities.
- Memory prompt injection.

## Exit gate

- Instant requests need no LLM.
- Local provider failure degrades safely.
- Typed and future voice-originated requests have coherent response semantics.
- Sensitive content can be visual-only by policy.
- Delivery adaptation is explainable, user-overridable, and does not create persistent emotional profile by default.
- No real voice pipeline has been introduced outside G9.
- Full suite and static checks pass.

---

# G7 — Home Assistant gateway: observe first, then low-risk control

**Codex reasoning:** High

## Objective

Connect smart home through one bounded Home Assistant adapter, never through Core or direct LLM tool authority.

## Stage A: Read-only state

- Authenticate through secret boundary.
- Enumerate only approved entities/capabilities.
- Subscribe to state updates through bounded adapter contract.
- Render household state.
- Handle unavailable devices, reconnection, stale state, and adapter timeout.

## Stage B: Low-risk control

- Tiny allowlist of reversible actions, initially lights only.
- Policy/confirmation/audit on every call.
- Dry-run, simulation, conflict, cancellation, and precondition tests.
- Administrator-approved bounded automations only after G3–G5 and an explicit automation readiness decision.

## Blocked

- Alarm auto-control.
- Door unlock.
- Camera media access.
- Unrestricted entity control.
- Raw Home Assistant tokens/entity inventory to LLMs.
- Autonomously generated automations.

## Exit gate

- Home Assistant failure does not crash LuciferOS.
- Adapter has no Core coupling.
- Every action exposes capability/authorization/policy/confirmation/audit outcome.
- No action outside allowlist.
- Resource scope, concurrency, idempotency, and cancellation are tested.
- Full suite and static checks pass.

---

# G8 — Controlled PC and document capabilities

**Codex reasoning:** High

## Objective

Add PC assistance gradually: observe first, then reversible local actions, then external/social actions.

## Sequence

1. Read-only diagnostics: app availability, printer status, file metadata, project status.
2. Explicit local actions: open approved named app; create local document draft; save to approved folder after confirmation where policy requires.
3. External/social actions: e-mail draft; calendar proposal; print proposal.
4. Always-confirm actions: send e-mail, print, delete, Git mutation, system administration, elevation, credential/configuration changes.

## Exit gate

- Every tool declares scope, data-egress class, preconditions, risk floor, idempotency, cancellation, conflict behavior, and rollback/compensation where relevant.
- Platform implementation is adapter-only.
- Same authorization/policy/confirmation/audit path as smart home.
- Full suite and static checks pass.

---

# G9 — HUD, tablet/mobile, and voice experience

**Codex reasoning:** Medium for presentation shell; High for voice, privacy, and network integration

## Objective

Make Lucifer coherent and welcoming without making visual/voice layers runtime owners.

## Work

- Responsive web/PWA for tablet/mobile only after LAN session/enrollment boundary is approved.
- Desktop HUD as presentation client with purple neon identity.
- Conversation, status, active jobs, household state, and confirmations.
- Dedicated long-answer workspace/window.
- Print preview and explicit confirmation.
- Local voice pipeline adapter.
- Build speech around endpointing, recognition alternatives/confidence where available, optional conservative disfluency-aware normalization, household entity resolution, clarification, and explicit correction feedback.
- Maintain consented local evaluation corpus/simulator for speech/intent regressions; do not solve recognition mistakes by endlessly adding hardcoded near-word aliases.
- Room/device identity as context only, not authority.
- Test shared-room/private/headphones/night delivery behavior and voice confirmation restrictions.

## Exit gate

- HUD/tablet/voice use same application API and cannot form competing runtime graphs.
- Typed requests can receive spoken summary where policy permits.
- Details can be shown without being spoken aloud.
- Private/shared-room behavior differs and is tested.
- Known speech/intent cases demonstrate measured improvement or safe clarification without worse unsafe false-action rate.
- LAN exposure/session behavior is bounded and tested before PWA/voice-satellite use beyond local host.
- Enrolled-device revocation, session expiry, and secure-transport failure behave safely and are tested before PWA/voice-satellite use beyond local host.
- Full suite and static checks pass.

---

# G10 — Advanced providers and bounded agent workflows

**Codex reasoning:** High

## Objective

Add cloud providers and multi-step work only after policy, audit, tool, memory, and network boundaries are proven.

## Work

- Cloud providers behind data-routing policy and classification rules.
- Explicit per-request/provider approval for private, restricted, account-connected, or otherwise sensitive content.
- Bounded advanced jobs with goal, approved tools, budgets, stop conditions, retries, and review points.
- Project-scoped document analysis and coding workflows with no project-based privilege escalation.
- Provider-generated plans remain validated proposals; no direct tool authority.

## Exit gate

- No cloud call bypasses data-routing, classification, and consent policy.
- No workflow has unlimited steps, unrestricted tools, broad memory retrieval, or unbounded egress.
- External side effects remain confirmation-gated.
- Full suite and static checks pass.

---

# G11 — Biometrics, cameras, alarms, and high-risk integrations

**Codex reasoning:** High

## Objective

Only after prior gates: optional multimodal convenience and high-risk integrations.

## Rules

- Face/voice begin as presence/context assistance only.
- Biometric data is sensitive, local, protected, exportable, and deletable.
- Biometrics never independently authorize private/security-critical actions.
- Camera/alarm begin read-only or confirmation-gated.
- Each security integration has a separate threat-model ADR.
- Every high-risk confirmation path requires appropriate trusted-session assurance, not shared-room voice alone.

## Exit gate

- Realistic threat model and explicit non-biometric alternative.
- Retention/export/deletion/backup behavior in place.
- Replay/presentation risk evaluated.
- Failure, outage, and safe-state behavior tested.
- Full suite and static checks pass.

---

# G12 — Household reliability and daily operation

**Codex reasoning:** Medium

## Objective

Turn a functioning system into a household appliance.

## Work

- One-click/local service startup.
- Clear status and repair guidance.
- Config backup/restore.
- Household administrator dashboard.
- Safe update process with governed provenance, compatibility checks, staged validation, rollback, and household-readable recovery guidance.
- Offline/failure experience testing.
- Timezone/DST/missed-trigger operational verification.
- Household-facing documentation.
- Periodic restore, policy-review, automation-review, and security-recovery exercises.

## Done enough

LuciferOS is daily-use ready when local conversation works, household status is visible, approved low-risk smart-home actions work, private/shared contexts remain separated, confirmations are understandable, cloud outage does not break core use, administrators can review/disable automation, startup/recovery requires no developer work, backup/restore has been demonstrated with required key/secret material, enrolled-client revocation is usable, and updates have a tested rollback path.

---

# Required negative tests across the program

Before a phase that makes a boundary relevant can pass, add tests proving prohibited behavior cannot occur:

```text
Architecture boundary tests
    Core cannot import concrete providers, stores, OS adapters, or interfaces.

Composition tests
    Exactly one production composition root exists.

Policy matrix tests
    Same action under unknown, guest, member, admin, private/shared mode,
    local/cloud state, and required failure modes.

Contract compatibility tests
    Public contract changes require explicit version/migration handling.

Fault-injection tests
    Provider, audit store, Home Assistant, network, secret/key provider, persistence,
    secure transport, session revocation, clock, update/rollback, and dependency failure
    produce defined, safe behavior.

Transport, device, and session tests
    Unenrolled, expired, revoked, lost, or policy-incompatible devices/sessions cannot
    retain authority through cached state. Beyond-localhost traffic fails safely when
    required authenticated transport is unavailable.

Supply-chain and update tests
    Runtime cannot silently install or auto-discover unapproved code/artifacts.
    Approved update failure preserves a safe prior state or reaches a documented
    recovery state without silently broadening authority.

Privacy tests
    Sensitive content cannot leak into audit, diagnostics, cloud egress,
    or spoken summary.

Automation tests
    Scope cannot expand; expired/revoked automation cannot execute;
    unattended always-confirm capability execution, unsafe retry, and conflict behavior are rejected.
```

---

# Feature-definition checklist

Before a new capability starts, answer:

```text
1. What household outcome does this create?
2. What data does it read/create/change/transmit/retain?
3. What is the access domain, project scope, and classification?
4. What capability/tool/provider is needed?
5. What authorization and policy permit/deny it?
6. Who confirms it, through which session assurance, and what exactly is frozen?
7. What happens with unknown identity?
8. What happens if provider/device/network/audit/configuration/clock fails?
9. What are resource scope, idempotency, cancellation, and conflict behavior?
10. How is it disabled, rolled back, revoked, or deleted?
11. Does it affect device/session trust, local transport, keys/secrets, dependency/update provenance, or recovery?
12. Does it need an ADR?
```

Unknown answer means design/spike work—not production code.

---

# Cross-cutting algorithm and learning rules

Algorithms are required where they make LuciferOS more reliable, accessible, and explainable. They are not a license to hide fragile behavior behind opaque scores.

## Required decision hierarchy

```text
1. Deterministic safety, authorization, policy, and lifecycle rules
2. Explicit household configuration and approved vocabulary
3. Confidence-aware perception and candidate ranking
4. Clarification or confirmation
5. Generative reasoning for open-ended language or explanation
```

A lower layer may never override a higher layer.

## Speech and command quality protocol

Before changing speech interpretation:

```text
A. State the failure mode and intended metric.
B. Add or update consented test/simulation cases.
C. Measure baseline: recognition, intent success, clarification, unsafe-action rate,
   and end-of-speech latency where relevant.
D. Make one bounded algorithmic change.
E. Compare against baseline and inspect failures.
F. Keep only changes that improve the defined metric without worsening safety.
G. Record threshold, fallback, rollback, and data-retention behavior.
```

Hardcoded aliases are allowed only as scoped configuration for verified household entities or explicit user-confirmed corrections. They are never the primary scalability strategy.

## Affective communication boundary

Lucifer can adapt how it communicates. It cannot claim certainty about what a person feels.

Affective adaptation is:

- task-aware;
- preference-aware;
- privacy-aware;
- confidence-aware;
- reversible and user-overridable;
- excluded from authorization, policy, automation, and identity decisions.

Any future biometric or emotion-model capability requires an ADR and separate consent, retention, backup, deletion, and threat-model review.

---

# Code-delivery protocol

```text
A. Declare manifest alignment and active phase.
B. State Codex reasoning level.
C. Read-only pre-flight on actual files.
D. Write/approve contract and acceptance tests.
E. One cohesive change in dedicated branch.
F. Targeted tests, full suite, static checks, fault/privacy checks, and diff review.
G. Review results with Eirik.
H. Commit/push only after explicit approval.
I. Update phase status and any ADR.
```

No broad transformation scripts. No guessed file contents. No permanent Codex permissions. No quick patch crossing more than one architecture boundary.

---

# Immediate next step

1. Commit this approved manifest and execution plan in one controlled documentation-only governance commit.
2. Verify the resulting commit, repository status, and historical-reference integrity.
3. Run G1 as a read-only traceability audit against this approved target and the fixed governance baseline commit.
4. Decide controlled consolidation versus limited package replacement from evidence.
5. Begin G2 only after the decision is documented and approved.
