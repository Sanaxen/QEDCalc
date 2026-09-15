# QEDCalc 3-loop worklog / handoff notes

Purpose: persistent engineering handoff notes for continuing the 3-loop QED vertex project across ChatGPT sessions. This file is primarily for the assistant/maintainer.

## Working branch and operating convention

- Repository: `Sanaxen/QEDCalc`
- Branch: `feature/three-loop-stage1-3`
- User environment: Windows 11 frontend, WSL/Linux for Kira/FireFly/Fermat.
- Heavy computations are run by the user locally.
- Assistant implements helpers/APIs/audits/BATs and pushes them.
- When local execution is needed, give a minimal copy-paste PowerShell block:

```powershell
git pull
.\run_something.bat
```

Do not ask for manual multi-step edits when a helper/BAT can be pushed.

## Overall objective

Take all 72 three-loop electron-vertex diagrams through projected-amplitude generation, canonical integral-family mapping, IBP reduction, master-basis identification, exact master-coefficient synthesis, master evaluation/epsilon expansion, diagram `F2(0)` values, and the full three-loop `g-2` coefficient.

## 72-diagram physical topology inventory

`data/three_loop_topologies.json` is the source inventory:

- `quenched`: Q01-Q50 = 50
- `vp1_insert`: VP01-VP12 = 12
- `vp2_insert`: VP4A-VP4C = 3
- `vp1_double`: VP22 = 1
- `external_lbl`: LBL01-LBL06 = 6

Total = 72.

Important: this physical/topological classification is complete. It must not be confused with a proven canonical **IBP/Kira integral-family** classification, which additionally needs an explicit denominator basis and a loop-momentum transformation.

## Q01 reduction / master-basis status: COMPLETE

Q01 is the reference diagram used to harden the pipeline before horizontal expansion.

- native projected demand set: 910 integrals
- exact Kira target set: 944 integrals
- finalized basis: `final60`
- boundary mandatory union: exact944 U final60 = 971 targets
- baseline seed: `(r,s,d)=(9,3,0)`

Three one-axis boundary tests passed:

- r+1 `(10,3,0)`, Kira/Fermat: `masters.final=117`; final60 all masters; 971 classified; unreduced=0.
- s+1 `(9,4,0)`, Kira/FireFly: `masters.final=125`; final60 all masters; 971 classified; unreduced=0; runtime about 3298.4 s.
- d+1 `(9,3,1)`, Kira/FireFly: `masters.final=60`; final60 all masters; 971 classified; unreduced=0; runtime about 2045.2 s.

Combined seed-boundary audit passed. The final60 basis is therefore treated as stable for the tested one-axis extensions and Q01 master identification is complete for the current target set.

### FireFly lesson

A stale FireFly save caused `Validation failed: Entry 0 does not match the black-box result!`. FireFly runners now remove stale `firefly_saves`, `ff_save`, and dedicated alt dirs before a fresh run. Do not regress this.

## Q01 exact coefficient synthesis: COMPLETE / PASS

Validated path:

```text
910 native projected terms
 -> 944 exact Kira targets
 -> d+1 r9s3d1 Kira/FireFly reduction
 -> final60
 -> exact Fermat coefficient synthesis
```

User-reported final synthesis:

```text
nonzero master forms after cancellation: 60
nonzero final60 coefficients: 60
nonzero extra master coefficients: 0
Q01 projected-amplitude final60 coefficient synthesis PASS
Q01 d+1 Fermat coefficient synthesis PASS
```

The target representation is

```text
F2_Q01^(3)(0) = sum_i C_i(D) M_i(D), i=1..60.
```

Do not numerically evaluate the masters yet; first establish the global 72-diagram family/master picture.

### Coefficient-synthesis lessons

- SymPy `cancel/together` is too memory-heavy for large three-loop aggregation (observed about 10-12 GB and a stall).
- Fermat 7.9b via WSL is the preferred exact rational-function backend.
- The s+1 `(9,4,0)` solve has 125 genuine masters; its 65 non-final60 masters are not expected to cancel merely because final60 is the preferred Q01 basis.
- The d+1 `(9,3,1)` solve has exactly the finalized 60 masters and is the correct completed Q01 reduction for the final coefficient artifact.
- Direct Fermat stdin/stdout works reliably; internal Fermat redirection stalled and prompt/timing noise must be stripped.

## Reusable master-coefficient API: VALIDATED / PASS

Common code is in:

- `three_loop/master_coefficient_api.py`

It separates diagram/family artifact preparation from reusable machinery for native-to-Kira expansion, Kira FORM reduction resolution, master contribution collection, Fermat canonicalization, and final-basis closure audit. It deliberately does not launch the projected trace or Kira solve.

Validation runner:

- `run_three_loop_q01_master_coefficient_api_validation.bat`

User-reported API validation:

```text
compared 60/60; mismatches=0
API reduction masters: 60
API nonzero final coefficients: 60
API extra nonzero masters: 0
reference coefficient mismatches: 0
Q01 reusable master-coefficient API validation PASS
```

This closes the Q01 prototype-to-reusable-API transition. Q01 through the common API is algebraically identical to the prior PASS reference, coefficient by coefficient using Fermat.

## 72-diagram integral-family global classification audit: IMPLEMENTED, FIRST PASS

Files:

- `three_loop/integral_family_classification.py`
- `examples/three_loop_72_integral_family_global_audit.py`
- `run_three_loop_72_integral_family_global_audit.bat`

The first global audit is intentionally conservative. It builds structural candidate classes for all 72 diagrams using topology data, quotienting obvious open-line reflection and dummy photon-label permutations where appropriate. These classes are **scheduling hints**, not claims of canonical IBP equivalence.

A canonical mapping is called `confirmed` only when both are present:

1. an explicit canonical propagator basis;
2. a proven loop-momentum transformation to that basis.

The audit emits JSON and TXT under:

```text
output/three_loop_integral_family_audit/
```

It reports separately:

- `audit_pass`: internal 72-diagram inventory and candidate-partition consistency;
- `classification_complete`: true only when all 72 diagrams have proven canonical mappings.

Do not treat `audit_pass=true` as meaning all canonical Kira families are already known.

## Current next sequence

1. Q01 final60 coefficient synthesis: **COMPLETE / PASS**.
2. Q01 reusable API equivalence validation: **COMPLETE / PASS**.
3. Q01/Q41 canonical family `Q01_full`: **COMPLETE / PASS**.
4. Q02/Q45 canonical family `Q02_full`: **ALGEBRAIC FAMILY COMPLETE / PASS**; Kira reduction/master basis not yet run.
5. Continue unresolved quenched structural classes with the same executable canonical-family proof discipline.
6. Extend projected-amplitude -> Kira -> master coefficients across Q02-Q72 through the reusable API.
7. Build a mapping/audit between QEDCalc global masters and published three-loop `g-2` master integrals (Laporta basis where applicable) as an external cross-check.
8. Only after the global family/master picture is stable, evaluate masters / epsilon-expand / assemble total `F2(0)`.

## Canonical family audit record requirements

For every diagram retain:

- diagram ID and physical/topological family;
- structural candidate class;
- canonical integral-family ID;
- canonical propagator basis;
- loop-momentum transformation;
- sign/normalization transformation;
- symmetry-equivalent representative;
- whether an existing Kira family can be reused;
- whether a new auxiliary basis is required;
- projected-amplitude target statistics;
- master-basis identifier;
- explicit evidence/status so topology similarity is never mistaken for a proof.

## Continuity rule

At the start of a new chat/session, read this file before proposing the next step, then cross-check the branch and the newest user-provided local logs. Update this worklog after meaningful milestones, design changes, important failures/fixes, or likely session handoffs.

## 2026-09-15 Q01 canonical-family promotion: COMPLETE / PASS

The explicit Q01 denominator basis / routing evidence was committed and the global 72-diagram audit was rerun successfully.

```text
Q01 canonical family confirmed
72図 audit:
  candidate_only = 71
  confirmed = 1
  internal audit errors = 0
  PASS
```

Q01 is now registered as canonical family `Q01_full` with the exact 12-propagator Kira basis, identity loop routing, the physical-sign/permutation relation to native QEDCalc denominators, and the exact native-ISP bridge.

## 2026-09-15 Q41 -> Q01_full equivalence: COMPLETE / PASS

User-local authoritative audit passed:

```text
candidate IDs: ['Q01', 'Q41']
confirmed Q01_full reuse: ['Q01', 'Q41']
Q41 reflection: True
Q41 loop transform: {'k': 'r', 'l': 'l', 'r': 'k'}
Q41 external transform: {'p': 'p+q', 'q': '-q'}
Q41 physical permutation: [6, 5, 4, 3, 2, 1, 9, 8, 7]
Q41 P1..P12 exact: True
Q41 ISP bridge exact: True
internal audit errors: 0
PASS
```

This is a full algebraic equivalence proof at the integral-family level, not a topology-only inference. Q41 therefore reuses `Q01_full` and `Q01_final60`; no new Kira family or auxiliary basis is needed.

## 2026-09-15 72-diagram global registry after Q01/Q41: COMPLETE / PASS

User-local global audit passed:

```text
classification status counts: {'candidate_only': 70, 'confirmed': 2}
confirmed canonical mappings: 2
canonical registry:
  Q01_full -> Q01, Q41
internal audit errors: 0
PASS
```

## 2026-09-15 Q02/Q45 canonical family bootstrap: COMPLETE / PASS

The next unresolved quenched structural class was Q02/Q45. The first bootstrap exposed an important distinction: the nine topology-level physical denominators have scalar-product rank 8 because D4 and D6 are not merely linearly related but exactly identical.

The final deduplicating audit passed:

```text
representative: Q02
family candidate: Q02_full
candidate IDs: ['Q02', 'Q45']
Q01 reuse under current scope: False
new family required under current scope: True
raw physical propagators: 9
raw physical SP rank: 8
physical rank deficiency: 1
duplicate physical groups: [[4, 6]]
raw physical -> unique mapping: [1, 2, 3, 4, 5, 4, 6, 7, 8]
unique physical propagators: 8
unique physical SP rank: 8
duplicate-only rank deficiency: True
selected auxiliary count: 4
selected auxiliaries: ['(k-r)^2', '(l-r)^2', '(l+q)^2', '(r+q)^2']
canonical denominator count: 12
canonical SP rank: 12/12
Kira ready: True
requires partial fraction / family split: False
physical relation: D4 - D6 = 0
Q02 confirmed_algebraic_equivalence
Q45 confirmed_algebraic_equivalence
internal audit errors: 0
PASS
```

Q02 therefore defines a new Kira-ready 12-denominator canonical family `Q02_full` made from eight unique physical denominators plus four quadratic auxiliaries. No partial fraction or family split is required. Native physical powers that map to the same canonical denominator must be added; in particular D4 and D6 both map to canonical physical denominator 4.

The reflected Q45 witness is:

```text
reflection: True
loop transform: {'k': 'l', 'l': 'r', 'r': 'k'}
external transform: {'p': 'p+q', 'q': '-q'}
physical -> canonical: [4, 5, 4, 3, 2, 1, 7, 8, 6]
P1..P12 exact: True
```

`three_loop/canonical_family_registry.py` now reruns this bootstrap audit before promoting Q02/Q45 into the global registry. `Q02_full` is Kira-ready but does not yet have a computed master basis; `master_basis_id` remains null until the Q02 Kira reduction is actually run and audited.

Next command:

```powershell
git pull
.\run_three_loop_72_integral_family_global_audit.bat
```

Expected global status after this promotion:

```text
candidate_only = 68
confirmed = 4
canonical registry:
  Q01_full -> Q01, Q41
  Q02_full -> Q02, Q45
```

## 2026-09-16 Q08 baseline master audit: PIPELINE CONTRACT FIXED; LOCAL RERUN PENDING

The first user-local Q08/Q48 baseline run at seed `r7s3d0` reached sectorwise triangular reduction in about 116.2 s, but the finalize audit failed because no `masters.final` artifact existed.

This failure must **not** be interpreted as a Q08 reduction failure or a bad canonical family. The prepare step had exported `run_back_substitution: false` while the finalize step explicitly required Kira's `masters.final`. The pipeline therefore stopped one stage earlier than its own audit contract required.

The baseline prepare path now exports with back substitution enabled. Q08 runtime cleanup already removes stale `results`, `sectormappings`, `tmp`, `firefly_saves`, and `pyred` state before a fresh run, so the Q01 stale-FireFly lesson is preserved for Q08 as well.

Current Q08 status:

```text
canonical family: Q08_full
covered diagrams: Q08, Q48
baseline seed: r7s3d0
baseline master audit: rerun pending after back-substitution fix
r+1 boundary r8s3d0: NOT YET VERIFIED
s+1 boundary r7s4d0: NOT YET VERIFIED
d+1 boundary r7s3d1: NOT YET VERIFIED
master-basis stability: NOT YET CLAIMED
```

For the follow-up boundary work, prefer the proven Q01 strategy: use FireFly for the expensive boundary reductions where appropriate, clean stale FireFly save state before each run, and only promote a Q08 master basis after the baseline and all three one-axis boundary audits have been compared successfully.
