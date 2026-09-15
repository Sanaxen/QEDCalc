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

Current Q01 evidence records the validated `Q01_full` Kira family, target counts, and `Q01_final60`, but the explicit denominator-basis/routing map has not yet been committed as canonical registry data. Therefore its status is deliberately `pipeline_validated_mapping_incomplete`, not `confirmed`.

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
3. Run the 72-diagram integral-family global audit and inspect its candidate-class inventory.
4. Promote candidate classes to proven canonical Kira families by deriving/recording explicit denominator bases and loop-momentum transforms, starting with Q01 and then family representatives.
5. Reuse each proven family mapping for symmetry-equivalent diagrams where the transformation is explicitly verified.
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

Q01 is now registered as canonical family `Q01_full` with the exact 12-propagator Kira basis, identity loop routing, the physical-sign/permutation relation to native QEDCalc denominators, and the exact native-ISP bridge. This closes the previous `pipeline_validated_mapping_incomplete` state for Q01.

## 2026-09-15 Q01-family equivalence mapper / audit: IMPLEMENTED

The next horizontal-family step has been implemented in:

- `three_loop/q01_family_equivalence.py`
- `examples/three_loop_q01_family_equivalence_audit.py`
- `run_three_loop_q01_family_equivalence_audit.bat`

The mapper takes only diagrams in Q01's structural candidate class and performs:

```text
diagram topology
 -> reflection / signed loop-momentum relabel candidate generation
 -> physical propagator bijection to Q01
 -> exact SymPy equality against Q01 Kira P1..P12
 -> sign / propagator permutation audit
 -> exact ISP bridge audit
 -> confirmed Q01_full reuse only if every check passes
```

Important: topology similarity alone never promotes a diagram. The open-line reflection also carries the external transformation `p -> p+q`, `q -> -q`; signed loop permutations are enumerated explicitly. The three Kira auxiliaries are pulled back through the candidate transformation and then checked against Q01 P10-P12, while the native ISP scalar products are checked independently.

The Q01 structural skeleton has a reflected Q41 candidate. An independent algebra sanity check of that candidate gives the expected reflection map `k -> r`, `l -> l`, `r -> k`, `p -> p+q`, `q -> -q`, with the nine physical denominator permutation `[6,5,4,3,2,1,9,8,7]`; the committed BAT is the authoritative repository audit and should be run in the normal Windows `.venv` environment before the global classification registry is promoted beyond Q01.

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

A new executable registry overlay is committed in `three_loop/canonical_family_registry.py`. The 72-diagram global audit now reruns the equivalence mapper during promotion and records the exact witness in each confirmed diagram record. The global audit must now show two confirmed mappings, Q01 and Q41, while the remaining diagrams stay candidate-only until similarly proven.

Next command:

```powershell
git pull
.\run_three_loop_72_integral_family_global_audit.bat
```

After that PASS, continue horizontally by selecting the next structural candidate class representative and applying the same exact canonical-family mapping discipline.
