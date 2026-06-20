# LuciferOS — Phase Status

**Effective status:** This document takes effect when committed together with the authoritative manifest and execution plan.
**Current project phase after this governance commit:** **G1 — Read-only repository traceability and reset decision**
**Code changes authorized:** No. G1 is read-only.
**Feature freeze:** Active.

## Authoritative governance sources

| Document | Repository path | Status |
|---|---|---|
| Household-first architecture | `docs/luciferos_manifest.md` | Authoritative manifest v1.0 |
| Dependency-aware development order | `docs/luciferos_execution_plan.md` | Authoritative execution plan v1.0 |
| Original fresh-start baseline | `docs/reference/luciferos_manifest_original_v1.md` | Immutable historical reference |
| Architecture decision records | `docs/decisions/ADR-000-template.md` | Governing template |

The original reference must remain byte-identical. Its existence and checksum must be verified locally before this governance commit is created.

## Governance source provenance

The approved source candidates used to produce the authoritative documents were:

```text
manifest candidate: luciferos_manifest_vnext_household_draft_v4_1.md
SHA-256: 0d111ca41ab623781a1f9c08a95043f0f777ef5bb1f9366a2374cddc2028eb8f

execution-plan candidate: luciferos_step_by_step_architecture_plan_draft_v4_1.md
SHA-256: 64ad898c312cdd475f1069aaf27cb0b5ece31f4c96b9b734dd6fe2630c96756a
```

The authoritative documents differ from the approved candidates only by:
1. conversion from draft/release-candidate status to authoritative v1.0 status;
2. updating the plan’s immediate-next-step section for the approved governance commit; and
3. clarifying that a non-administrator runtime emergency stop is an execution interruption/interlock, not an automation lifecycle change, with matching G3 test requirements.

## G1 objective

Produce evidence of how the actual repository conforms or fails to conform to the authoritative manifest. G1 must not modify code, configuration, tests, documentation, Git history, branches, or dependencies.

## G1 required evidence

For every relevant target requirement:

```text
classification
manifest section
exact source/test/config path
runtime-wiring evidence
behavior/failure-test evidence
risk if retained unchanged
recommended action: preserve | isolate | refactor | remove | defer | replace
```

Allowed classifications:

```text
IMPLEMENTED
PARTIALLY_IMPLEMENTED
DECLARED_NOT_WIRED
MISSING
CONTRADICTED
NOT_YET_DUE
UNVERIFIED_INSUFFICIENT_EVIDENCE
```

## Known constraints and active blocks

Blocked until G1 decision and the relevant phase gate:

- feature development;
- memory retrieval integration;
- new providers, tools, Home Assistant, HUD, voice, PC-control, biometrics, or advanced-agent work;
- production refactors;
- runtime/config/dependency changes;
- destructive Git operations;
- Codex write tasks.

Allowed in G1:

- read-only inspection;
- test/static-check execution that does not modify tracked files;
- documentation of audit results only after the audit is complete and approved as a separate action.

## Pre-G1 verification required

Before the G1 audit starts, record and verify:

```text
repository root
current branch
HEAD commit
working-tree status
remote tracking status
authoritative document hashes
historical-reference checksum
test/static-check baseline commands and results
```

## Next gate

G1 ends only after an evidence-based preserve/isolate/refactor/remove/defer/replace recommendation is documented and approved. G2 begins only after that decision.
