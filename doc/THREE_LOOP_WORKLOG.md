# QEDCalc 3-loop worklog / handoff notes

Purpose: persistent engineering handoff notes for continuing the 3-loop QED vertex project across ChatGPT sessions.

## Working branch and operating convention

- Repository: `Sanaxen/QEDCalc`
- Branch: `feature/three-loop-stage1-3`
- User environment: Windows 11 frontend, WSL/Linux for Kira/FireFly/Fermat.
- Heavy computations are run by the user locally.
- Assistant implements helpers/APIs/audits/BATs and pushes them.
- Prefer minimal local commands:

```powershell
git pull
.\run_something.bat
```

Do not ask for manual multi-step edits when a helper/BAT can be pushed.

## Overall objective

Take all 72 three-loop electron-vertex diagrams through projected-amplitude generation, canonical integral-family mapping, IBP reduction, master-basis identification, exact master-coefficient synthesis, master evaluation / epsilon expansion, diagram `F2(0)` values, and the full three-loop `g-2` coefficient.

## 72-diagram inventory and canonical-family status

`data/three_loop_topologies.json` contains:

- quenched Q01-Q50 = 50
- VP1 insert VP01-VP12 = 12
- VP2 insert VP4A-VP4C = 3
- VP1 double VP22 = 1
- external LBL LBL01-LBL06 = 6

Total = 72.

The exact canonical-family autodiscovery / registry work is complete for all 72 diagrams. There are 45 canonical Kira families in total. The family classification is based on explicit denominator bases and exact momentum-map witnesses, not topology similarity alone.

## Master-basis schedule status after Q02 promotion

Completed canonical families:

- `Q01_full -> Q01_final60`, diagrams Q01/Q41
- `Q02_full -> Q02_final17`, diagrams Q02/Q45
- `Q08_full -> Q08_final12`, diagrams Q08/Q48
- `Q10_full -> Q10_final13`, diagrams Q10/Q50

Expected schedule summary after the Q02 promotion audit:

```text
canonical families: 45
master-basis complete families: 4
master-basis pending families: 41
complete diagram coverage: 8
pending diagram coverage: 64
next pending family: Q05_full
```

The pending-family schedule is a practical heuristic: multi-diagram quenched first, then multi-diagram VP1, singleton quenched, singleton VP1, VP2/VP22, external LBL; within a tier, fewer unique physical denominators first. It is not a Kira-runtime prediction.

## Q01 reference pipeline: COMPLETE / PASS

Q01 was used to harden the full reduction and coefficient-synthesis pipeline.

- native projected demand: 910
- exact Kira target set: 944
- final master basis: `Q01_final60`
- boundary mandatory union: exact944 U final60 = 971
- baseline seed: r9s3d0
- r+1 r10s3d0: final60 all masters; 971 classified; unreduced=0
- s+1 r9s4d0 FireFly: final60 all masters; 971 classified; unreduced=0
- d+1 r9s3d1 FireFly: final60 all masters; 971 classified; unreduced=0
- combined seed-boundary audit: PASS

Exact coefficient synthesis also passed. The reusable API in `three_loop/master_coefficient_api.py` reproduced all 60 Q01 coefficients exactly with Fermat, mismatches=0, and no extra nonzero masters.

Important architectural split:

```text
canonical family
 -> stable final master basis
 -> family-specific projected-amplitude / bridge artifacts
 -> reusable master_coefficient_api
 -> exact coefficients
```

The reusable API does not launch the projected trace or Kira solve; it consumes their artifacts.

## Q08 master basis: COMPLETE / PASS

`Q08_full` covers Q08/Q48.

- 7 unique physical denominators + 5 auxiliaries
- baseline r7s3d0 -> 12 masters
- r8s3d0, r7s4d0, r7s3d1 one-axis extensions all passed
- final basis: `Q08_final12`

## Q10 master basis: COMPLETE / PASS

`Q10_full` covers Q10/Q50.

- 7 unique physical denominators + 5 auxiliaries
- baseline r7s3d0 -> 13 masters
- r8s3d0, r7s4d0, r7s3d1 one-axis extensions all passed
- final basis: `Q10_final13`

## Q02 canonical family

`Q02_full` covers Q02/Q45.

Physical-family facts:

- 9 raw physical denominators
- exact duplicate D4=D6
- raw-to-unique mapping: `[1,2,3,4,5,4,6,7,8]`
- 8 unique physical denominators, rank 8
- auxiliaries: `(k-r)^2`, `(l-r)^2`, `(l+q)^2`, `(r+q)^2`
- total canonical denominators: 12, rank 12
- top sector: 255
- no partial fraction / family split required

Q45 exact witness:

```text
reflection: True
loop transform: {'k': 'l', 'l': 'r', 'r': 'k'}
external transform: {'p': 'p+q', 'q': '-q'}
physical -> canonical: [4, 5, 4, 3, 2, 1, 7, 8, 6]
P1..P12 exact: True
```

## Q02 master-basis discovery: COMPLETE / PASS

The first ordinary Kira baseline run was stopped by the user after more than four hours because the reduction was progressing too slowly. The ordinary boundary batch was never run. The Q02 work then switched to an isolated Kira+FireFly path.

### FireFly baseline and first one-axis tests

FireFly baseline:

```text
seed r8s3d0
master count: 63
internal audit errors: 0
PASS
runtime: 2244.1 s
```

Initial one-axis master sets:

```text
r8s3d0: 63 masters
r9s3d0: 63 masters, retained baseline 63/63
r8s4d0: 75 masters, retained baseline 52/63
r8s3d1: 55 masters, retained baseline 31/63
```

The r/s/d tests showed that literal `masters.final` membership is seed-dependent for Q02. The s+1 and d+1 subset audits therefore failed scientifically even though Kira/FireFly completed correctly. This ruled out promoting the initial 63 forms as `Q02_final63`.

### Four-seed master-set union

The four sets were compared explicitly:

```text
master counts: 63, 63, 75, 55
intersection across all four: 31
union across all four: 110
r8s3d0 vs r9s3d0: intersection 63
r8s3d0 vs r8s4d0: intersection 52
r8s3d0 vs r8s3d1: intersection 31
r8s4d0 vs r8s3d1: intersection 31
```

The 110-form union was then treated as one mandatory target set so that all candidate masters were tested in the same reduction context.

### Mandatory-union reduction

The first preflight correctly detected that fixed r9s4d1 did not cover all union targets because a target with d=2 was present. The helper was changed to derive max(r), max(s), max(d) automatically from the mandatory target list.

The resulting common context was r9s4d2:

```text
mandatory union targets: 110
envelope seed: r9s4d2
master count: 17
internal audit errors: 0
PASS
runtime: 367.5 s
```

This produced the candidate basis `Q02_final17`.

### Final17 closure / stability tests

The same 110 mandatory targets and candidate 17 forms were tested at three one-axis extensions of r9s4d2:

```text
r10s4d2:
  masters.final = 17
  final17 = master 17, reduced 0, zero 0, unresolved 0
  stable = True

r9s5d2:
  masters.final = 17
  final17 = master 17, reduced 0, zero 0, unresolved 0
  stable = True

r9s4d3:
  masters.final = 17
  final17 = master 17, reduced 0, zero 0, unresolved 0
  union target status = master 31, reduced 79, zero 0, unresolved 0
  stable = True
  execution pass = True
```

Aggregate result:

```text
candidate master basis: Q02_final17
stable under tested one-axis extensions: True
internal audit errors: 0
QEDCalc Q02 final17 FireFly boundary aggregate audit PASS
```

Therefore `Q02_full -> Q02_final17` is formally promoted.

## FireFly operational rule

A stale FireFly save previously caused:

```text
Validation failed: Entry 0 does not match the black-box result!
```

FireFly runners must clean stale state before a fresh run, including as applicable:

```text
firefly_saves
ff_save
firefly_saves_alt
results
sectormappings
tmp
pyred
```

Do not regress this cleanup behavior.

## Stage-2 reusable master-basis API

The family/seed preparation, Kira project generation, master parsing, one-axis boundary comparison, union/intersection construction, and explicit-target envelope calculation are reusable in `three_loop/master_basis_api.py`.

The generic Stage-2 validation over all 45 canonical families passed 45/45. Keep the deliberate operational restriction: do not switch to an unattended all-family batch runner until Q05 plus another 2-3 families have exercised the common API successfully in real Kira/FireFly runs.

## Q05 master-basis discovery: IN PROGRESS

`Q05_full` covers Q05/Q42.

The baseline r8s3d0 reduction completed with 43 masters and passed its generic finalize audit. The generic one-axis boundary batch then completed with the following result:

```text
baseline r8s3d0 : 43
r9s3d0          : 43  retained 43/43  stable=True
r8s4d0          : 67  retained 38/43  stable=False
r8s3d1          : 37  retained 31/43  stable=False
intersection    : 31
union           : 78
internal errors : 0
boundary aggregate audit: PASS
```

Therefore the literal baseline set must NOT be promoted as `Q05_final43`. Q05 is another seed-dependent representative family like Q02.

The boundary audit generated:

```text
output/three_loop_integral_family_audit/q05_full_firefly_r8s3d0_master_union_targets.txt
```

with 78 mandatory union targets.

### Generic mandatory-union continuation

The Q02 strategy has now been lifted into the common Stage-2 path rather than copied into a Q05-only script.

Reusable pieces already present in `three_loop/master_basis_api.py`:

- `render_jobs_yaml(..., mandatory_file=...)` / Kira `select_mandatory_list`
- `export_kira_project(..., mandatory_file=...)`
- `integral_complexity(...)`
- `required_envelope(targets, floor=...)`

New generic runner:

```text
examples/three_loop_master_basis_union_reduction.py
run_three_loop_master_basis_union_reduction.bat
```

Its prepare phase:

1. reads the boundary-generated union target file;
2. validates family ID and 12 indices for every target;
3. removes duplicate targets deterministically;
4. derives the required max r/s/d envelope automatically, with the baseline seed as a floor;
5. exports one common Kira project using the union as `select_mandatory_list`;
6. writes a target SHA-256 so finalize rejects a changed target set.

Its finalize phase records the candidate `masters.final`, candidate master count/copy, target count/hash, required envelope, and audit JSON/TXT.

The immediate next heavy computation is the Q05 78-target common-context reduction. Only after that returns a candidate `Q05_finalNN` should the generic final-boundary closure at envelope r+1/s+1/d+1 be prepared and run.

## Current next sequence

1. Pull the branch and run the generic Q05 mandatory-union reduction:

```powershell
.\run_three_loop_master_basis_union_reduction.bat Q05_full r8s3d0 firefly
```

2. Record the automatically selected envelope and candidate master count from the final audit. Do not promote the candidate yet.
3. Implement/use the generic candidate-closure runner to test the same 78 union targets plus the candidate basis at the envelope's r+1, s+1, and d+1 boundaries.
4. Promote `Q05_full -> Q05_finalNN` only if all closure audits pass with no unresolved targets and the candidate basis remains stable.
5. Then exercise the same common API on another 2-3 pending families before enabling an unattended all-family batch runner.
6. After enough families have stable bases, demonstrate cross-family reuse of `master_coefficient_api` on Q08 or Q10 before scaling coefficient synthesis across all diagrams.
7. Master evaluation / epsilon expansion has not started and remains a likely major research bottleneck.
8. Only after the global family/master picture is sufficiently stable should the 72-diagram total `F2(0)` be assembled.

## Continuity rule

At the start of a new chat/session, read this file first, then inspect the current branch and newest user-provided local logs. Update this worklog after meaningful milestones, design changes, important failures/fixes, or likely session handoffs.

---
