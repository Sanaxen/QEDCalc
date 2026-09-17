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

## Current next sequence

1. Run `run_three_loop_master_basis_schedule_audit.bat` after the Q02 registry promotion. Expected: 45 families, 4 complete, 41 pending, 8 diagrams covered, 64 pending, next `Q05_full`.
2. If the schedule audit passes, proceed to stable master-basis identification for `Q05_full` using the now-proven strategy: cheap ordinary Kira where appropriate, FireFly when the family becomes expensive, and mandatory-union reduction if literal master sets change with seed.
3. After enough families have stable bases, demonstrate cross-family reuse of `master_coefficient_api` on Q08 or Q10 before scaling coefficient synthesis across all diagrams.
4. Master evaluation / epsilon expansion has not started and remains a likely major research bottleneck.
5. Only after the global family/master picture is sufficiently stable should the 72-diagram total `F2(0)` be assembled.

## Continuity rule

At the start of a new chat/session, read this file first, then inspect the current branch and newest user-provided local logs. Update this worklog after meaningful milestones, design changes, important failures/fixes, or likely session handoffs.

---

## LATEST HANDOFF UPDATE — 2026-09-17 JST

This section supersedes the older `Current next sequence` above where they conflict.

### Current stage summary

```text
Stage 1: 72 diagrams -> canonical families
  COMPLETE
  72/72 diagrams confirmed
  45 canonical families
  effectively API-structured already via autodiscovery + canonical registry

Stage 2: stable master-basis identification
  4/45 families formally complete
  Q01_final60, Q02_final17, Q08_final12, Q10_final13
  reusable API work added and now under live validation

Stage 3: exact master coefficients
  Q01 complete
  reusable master_coefficient_api exists and exact Q01 regression passed

Stage 4: master evaluation / epsilon expansion
  NOT STARTED

Stage 5: 72-diagram assembly / total 3-loop g-2
  NOT STARTED
```

### Q05 baseline result — PASS

`Q05_full` covers Q05/Q42.

Family facts:

- 9 raw physical denominators
- duplicate D2=D4
- raw-to-unique mapping: `[1,2,3,2,4,5,6,7,8]`
- 8 unique physical denominators
- 4 auxiliaries: `(k-l)^2`, `(l-r)^2`, `(l+q)^2`, `(r+q)^2`
- 12 total canonical denominators
- top sector 255
- baseline seed r8s3d0

Authoritative local baseline result:

```text
Total time: 1246.3 s
canonical family: Q05_full
covered diagrams: ['Q05', 'Q42']
seed: r8s3d0
top sector: 255
master count: 43
master-basis status: baseline candidate; boundary audits pending
internal audit errors: 0
QEDCalc Q05 r8s3d0 baseline Kira audit PASS
```

Do NOT promote `Q05_final43` yet. Boundary audits are still required.

### Reusable Stage-2 API status

New reusable core:

- `three_loop/master_basis_api.py`
- `examples/three_loop_master_basis_pipeline.py`
- generic seed runner: `run_three_loop_master_basis_seed.bat`
- generic boundary comparison: `examples/three_loop_master_basis_boundary_audit.py`
- generic three-boundary runner: `run_three_loop_master_basis_boundaries.bat`

The API centralizes:

- FamilySpec generation from canonical registry
- quenched / VP1 / VP2-VP22 / LBL physical-propagator reconstruction
- exact duplicate collapse
- deterministic auxiliary completion
- Kira `integralfamilies.yaml` generation
- Kira `kinematics.yaml` generation
- ordinary Kira / FireFly job generation
- stale runtime cleanup
- `masters.final` parsing
- r/s/d one-axis seed generation
- master-set comparison / intersection / union
- target-envelope r/s/d analysis

Important design rule: the canonical registry is expensive to build. Reuse one registry snapshot within long validation/batch processes; do not rebuild all 72-diagram autodiscovery for every FamilySpec.

### Reusable API validation — PASS

The initial validation implementation appeared hung because it rebuilt the 72-diagram registry roughly 50 times. It was fixed to build the registry once and reuse it, with live progress output.

Authoritative validation result:

```text
Q02_full dedicated regression: PASS
Q05_full dedicated regression: PASS
all canonical family specs: 45/45 PASS
internal audit errors: 0
QEDCalc reusable master-basis API validation PASS
```

This confirms all 45 canonical families can be represented by the reusable Stage-2 FamilySpec/Kira-input path.

### Q05 generic boundary result — COMPLETE / PASS, UNION REQUIRED

The user completed:

```powershell
.\run_three_loop_master_basis_boundaries.bat Q05_full r8s3d0 firefly
```

Authoritative aggregate result:

```text
family: Q05_full
diagrams: ['Q05', 'Q42']
baseline seed: r8s3d0
baseline masters: 43
boundary solver: firefly
r9s3d0: masters=43 retained=43/43 stable=True
r8s4d0: masters=67 retained=38/43 stable=False
r8s3d1: masters=37 retained=31/43 stable=False
intersection across available sets: 31
union across available sets: 78
stable under tested one-axis extensions: False
union reduction needed: True
internal audit errors: 0
QEDCalc generic master-basis boundary aggregate audit PASS
```

The d+1 `r8s3d1` FireFly run alone reported:

```text
Total time: 16302.4 s
master count: 37
QEDCalc generic master-basis finalize audit PASS
```

The generated union target file is:

```text
output/three_loop_integral_family_audit/q05_full_firefly_r8s3d0_master_union_targets.txt
```

Scientific interpretation: Q05 is another Q02-type representative-drift case. This is NOT a generic-API failure. The generic path correctly detected the instability and generated the 78-target union automatically. Do NOT promote `Q05_final43`, `Q05_final67`, or `Q05_final37`.

### Immediate Q05 next step

Use the Q02-proven common-context strategy, but implement it generically rather than adding Q05-only code:

```text
78 union targets
 -> derive required common r/s/d envelope automatically
 -> one mandatory-union Kira+FireFly reduction
 -> obtain candidate finalNN master basis
 -> test candidate basis under common-envelope r+1 / s+1 / d+1
 -> promote Q05 only if all final closure tests pass
```

The exact Kira mandatory-target/job semantics must be taken from the already successful Q02 union/final17 implementation rather than guessed from a new abstraction.

### Planned rollout before unattended full-batch execution

The user explicitly wants unattended operation eventually, but do NOT switch to it yet.

Agreed plan:

1. Complete Q05 generic union/common-context rescue and final-basis closure.
2. Run another 2-3 families through the reusable Stage-2 path, likely starting with Q07 and Q09 according to schedule.
3. Fix any API/runtime issues found during those live trials.
4. Only after this proving period, start unattended all-family execution.

The user asked to be told explicitly which BAT to run at each appropriate time. Do not ask them to run the all-family controller prematurely.

### Batch/checkpoint/runtime-estimator groundwork already added

Groundwork has been implemented but is NOT yet approved for full unattended use:

- `three_loop/master_basis_batch.py`
- `examples/three_loop_master_basis_batch_controller.py`
- `run_three_loop_master_basis_all.bat`

Intended future capabilities:

- execution queue from master-basis schedule
- detect/reuse existing PASS artifacts
- checkpoint per family/seed
- stop on failure
- resume from selected family
- record measured runtimes
- estimate remaining low/median/high wall time
- eventually automate union/final-boundary rescue too

Current safety behavior for unstable families is to checkpoint and stop cleanly when union reduction is needed. Generic fully automatic union/final-boundary rescue is not yet considered proven for unattended operation.

### Future unattended-operation policy

Once Q05 + about 2-3 additional families validate the generic path, the intended workflow is:

```text
family baseline
 -> r/s/d boundaries
 -> stable? promote candidate path
 -> unstable? union/common-context rescue
 -> final-basis closure
 -> checkpoint PASS
 -> next family
```

If a later API fix affects only orchestration/audit logic, reuse expensive Kira artifacts where scientifically valid. If a fix changes FamilySpec/denominator construction or reduction inputs, determine the earliest affected family and resume/recompute from there rather than blindly trusting earlier results.

Runtime estimation should use measured local history and report broad ranges rather than false precision because Kira/FireFly runtime can vary sharply by family/seed. The Q05 d+1 run of 16302.4 s is an important new runtime sample.

### Immediate next action for the next assistant/session

1. Read this file first.
2. Treat the Q05 boundary run as COMPLETE and PASS at the audit level, but unstable at the master-representative level.
3. Inspect/reuse the proven Q02 mandatory-union and final17 closure implementation.
4. Implement the same common-context union + final-boundary path generically.
5. Push the generic Q05 union runner before asking the user to run anything.
6. Do not start Q07 or the unattended all-family controller until Q05 has a formally stable final basis.
7. Update this worklog again after the union reduction result and after final closure/promotion.
