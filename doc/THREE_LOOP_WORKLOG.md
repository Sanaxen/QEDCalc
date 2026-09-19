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

## Master-basis schedule status after Q09 promotion

Completed canonical families:

- `Q01_full -> Q01_final60`, diagrams Q01/Q41
- `Q02_full -> Q02_final17`, diagrams Q02/Q45
- `Q05_full -> Q05_final13`, diagrams Q05/Q42
- `Q07_full -> Q07_final25`, diagrams Q07/Q47
- `Q08_full -> Q08_final12`, diagrams Q08/Q48
- `Q09_full -> Q09_final17`, diagrams Q09/Q49
- `Q10_full -> Q10_final13`, diagrams Q10/Q50
- `Q12_full -> Q12_final24`, diagrams Q12/Q35
- `Q17_full -> Q17_final23`, diagrams Q17/Q37

Expected schedule summary after the Q09 promotion audit:

```text
canonical families: 45
master-basis complete families: 9
master-basis pending families: 36
complete diagram coverage: 18
pending diagram coverage: 54
next pending family: determined by the updated schedule audit
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

The generic Stage-2 validation over all 45 canonical families passed 45/45.

The earlier deliberate restriction against unattended all-family execution has now been lifted. Q05, Q07, and Q09 exercised the common API in real Kira/FireFly runs, including two independent seed-dependent families (Q07 and Q09) that successfully traversed baseline -> boundaries -> mandatory union -> candidate closure -> no-rerun re-audit.

The unattended controller in `examples/three_loop_master_basis_batch_controller.py` now:
- uses FireFly for both baseline and boundary seed runs;
- reuses existing successful seed audits/checkpoints;
- prints empirical median/range runtime estimates and an estimated finish time before each seed run;
- automatically enters mandatory-union reduction when the boundary audit is unstable;
- automatically runs candidate closure;
- treats the text-equation closure audit as provisional and always follows it with the authoritative no-rerun completion re-audit;
- stops only on a genuine failed reduction/audit;
- writes a `three_loop_<family>_promotion_ready.json` artifact for every scientifically proven family;
- does not edit the executable canonical registry during a long unattended computation. Registry promotions remain reviewed Git changes after the generated proof artifacts are inspected.

The top-level runner is:

```powershell
.\run_three_loop_master_basis_all.bat plan [START_FAMILY] [MAX_FAMILIES]
.\run_three_loop_master_basis_all.bat run [START_FAMILY] [MAX_FAMILIES]
.\run_three_loop_master_basis_all.bat status
.\run_three_loop_master_basis_all.bat resume [MAX_FAMILIES]
```

Unattended resume is now automatic. `resume` with no family argument scans promotion-ready artifacts, checkpoint state, and existing successful seed audits, then starts from the first unfinished pending family. The user does not need to know which family was active when a PC reboot, console close, or other interruption occurred.

`MAX_FAMILIES` is a strict safety cap on how many canonical families may be processed in one unattended batch. Canonical families are the Stage-2 execution units and are never split. A value of 5 therefore selects at most five unfinished canonical families, regardless of how many original Feynman diagrams those families cover. For the current schedule, starting at `Q12_full` with a cap of 5 selects `Q12_full`, `Q17_full`, `Q18_full`, `Q20_full`, and `Q22_full`. These five families currently cover ten original diagrams in total.

Examples:

```powershell
.\run_three_loop_master_basis_all.bat plan Q12_full 5
.\run_three_loop_master_basis_all.bat run Q12_full 5
.\run_three_loop_master_basis_all.bat status
.\run_three_loop_master_basis_all.bat resume
.\run_three_loop_master_basis_all.bat resume 5
```

The initial total ETA covers currently pending baseline/boundary seed runs. Union/candidate-closure rescue time is added only when a family proves unstable.

## Q05 master-basis discovery: COMPLETE / PASS

`Q05_full` covers Q05/Q42.

The baseline r8s3d0 reduction completed with 43 masters. Its one-axis boundary comparison showed seed-dependent representatives:

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

Therefore the literal baseline set was not promoted. The 78-form union was reduced in a common mandatory context and produced a 13-master candidate. Final guard auditing then established the promoted basis:

```text
canonical family : Q05_full
final basis      : Q05_final13
baseline         : r8s0d8
guards           : r9s0d8 / r8s1d8 / r8s0d9
all guards       : stable=True
candidate masters: 13/13
non-master       : 65
unresolved       : 0
extra masters    : 0
mandatory mismatch: 0
master shift violation: 0
internal errors  : 0
```

The registry and master-basis schedule already contain `Q05_full -> Q05_final13`. Q05 requires no further Kira run.

## Q07 master-basis discovery: COMPLETE / PASS

`Q07_full` covers Q07/Q47.

Baseline FireFly reduction:

```text
seed: r8s3d0
master count: 43
runtime: 883.3 s
audit: PASS
```

One-axis boundary comparison:

```text
r9s3d0 : 43 masters, retained 43/43, stable=True
r8s4d0 : 53 masters, retained 35/43, stable=False
r8s3d1 : 40 masters, retained 30/43, stable=False
intersection: 30
union: 71
internal audit errors: 0
boundary aggregate audit: PASS
```

Therefore the literal 43-master baseline was not promoted. The 71-form union was reduced in the common mandatory context:

```text
mandatory targets: 71
required envelope: r8s4d2
candidate master count: 25
runtime: 258.7 s
audit: PASS
```

The first generic candidate-closure audit reported 46 unresolved non-master targets at each guard even though all 25 candidate masters were retained. This was a text-export classification limitation rather than a failed reduction. The no-rerun re-audit then verified the exact mandatory lists and completed Kira logs directly:

```text
guards: r9s4d2 / r8s5d2 / r8s4d3
masters.final: 25 / 25 / 25
candidate masters retained: 25/25 on all guards
resolved non-masters: 46 on all guards
extra masters: 0
mandatory mismatches: 0
internal audit errors: 0
stable under tested one-axis extensions: True
re-audit: PASS
```

Therefore `Q07_full -> Q07_final25` is formally promoted.

## Q09 master-basis discovery: COMPLETE / PASS

`Q09_full` covers Q09/Q49.

Baseline FireFly reduction:

```text
seed: r8s3d0
master count: 43
runtime: 1223.1 s
audit: PASS
```

One-axis boundary comparison:

```text
r9s3d0 : 43 masters, retained 43/43, stable=True
r8s4d0 : 43 masters, retained 43/43, stable=True
r8s3d1 : 42 masters, retained 32/43, stable=False
intersection: 32
union: 53
internal audit errors: 0
boundary aggregate audit: PASS
```

Therefore the literal 43-master baseline was not promoted. The 53-form union was reduced in the common mandatory context:

```text
mandatory targets: 53
required envelope: r8s3d2
candidate master count: 17
audit: PASS
```

The first generic candidate-closure audit again classified all non-master mandatory targets as unresolved because no human-readable reduction equation was emitted, while all 17 candidate masters were retained. The no-rerun re-audit verified the completed Kira reductions directly:

```text
guards: r9s3d2 / r8s4d2 / r8s3d3
masters.final: 17 / 17 / 17
candidate masters retained: 17/17 on all guards
resolved non-masters: 36 on all guards
extra masters: 0
mandatory mismatches: 0
internal audit errors: 0
stable under tested one-axis extensions: True
re-audit: PASS
```

Therefore `Q09_full -> Q09_final17` is formally promoted.

## Q12 master-basis discovery: COMPLETE / PASS

`Q12_full` covers Q12/Q35 and is currently the first pending family.

Baseline FireFly reduction is complete:

```text
seed: r8s3d0
master count: 82
audit: PASS
```

The one-axis FireFly boundary stage is also complete:

```text
r9s3d0 : 82 masters, retained 82/82, stable=True
r8s4d0 : 82 masters, retained 82/82, stable=True
r8s3d1 : 66 masters, retained 63/82, stable=False
intersection across available sets: 63
union across available sets: 85
stable under tested one-axis extensions: False
union reduction needed: True
internal audit errors: 0
boundary aggregate audit: PASS
```

Therefore the literal 82-form baseline set was not promoted. Q12 is seed-dependent in the tested d+1 direction. The unattended controller entered the generic mandatory-union rescue path over the 85-form union and produced a 24-master candidate basis. The authoritative no-rerun closure re-audit passed, and the family was promoted:

```text
Q12_full -> Q12_final24
proof mode: mandatory-union-plus-no-rerun-closure
audit pass: True
```

Q12 is formally complete.

## Q17 master-basis discovery: PROMOTION READY / PASS

`Q17_full` covers Q17/Q37.

The unattended Stage-2 controller completed the full seed-dependent rescue path. The initial text-equation candidate-closure audit reported unresolved non-master targets and returned a soft failure, but all candidate masters were retained. The authoritative no-rerun completion re-audit then verified the completed Kira reductions directly:

```text
candidate envelope: r8s3d2
union targets: 90
candidate masters: 23
guards: r9s3d2 / r8s4d2 / r8s3d3

all guards:
  masters.final: 23
  candidate masters retained: 23/23
  resolved non-masters: 67
  extra masters: 0
  mandatory mismatches: 0
  Kira completed: True
  stable: True

internal audit errors: 0
no-rerun closure re-audit: PASS
```

Promotion-ready result:

```text
Q17_full -> Q17_final23
```

The executable canonical registry now contains `Q17_full -> Q17_final23` together with `Q12_full -> Q12_final24`.

## Q18 unattended union-reduction stop and generic fix

During an unattended `resume 4` batch beginning at `Q18_full`, the Q18 mandatory-union reduction stopped with:

```text
No integrals to reduce, skipping this family.
ValueError: Q18_full: expected one masters.final, found 0
```

The generic mandatory-list path was still constraining the Kira `reduce` block to the canonical top sector only, even though the explicit mandatory union targets can live entirely in lower sectors. In that situation Kira can legitimately find no selected integral inside the requested reduction sector and therefore emit no `masters.final`.

The generic master-basis API was changed so mandatory-list jobs can specify the actual sector set of the explicit targets. The mandatory-union and candidate-closure helpers now derive the sector IDs from the positive indices of their target integrals and pass those sectors to Kira. Ordinary baseline/boundary jobs remain unchanged and still use the canonical top sector.

Relevant commits:

```text
a76c90faf7f62c24f4b8d7804c9c73e763c0ad85  target-sector support in master_basis_api
20ff1c9a651e81877aeb210a7731a76200bc6637  mandatory union uses actual target sectors
f792c9c7af8e1adf3e16f75a96b5fa12218ef121  candidate closure uses actual target sectors
```

After pulling these changes, the unattended batch should be resumed rather than restarted from scratch. Existing Q18 baseline/boundary audits remain reusable; the failed union reduction is regenerated and rerun with the corrected sector selection.

## Q18 mandatory-sector follow-up fix

The first target-sector fix was insufficient: Q18 still produced `No integrals to reduce`. The remaining issue is that Kira's family definition still exposed only the original physical `top_level_sectors`. Mandatory union targets may contain positive powers on auxiliary propagators, placing them in sectors that are not subsectors of the physical top sector.

Kira requires such higher/different sectors to be included in the integral family's `top_level_sectors` when they are to participate in symmetry/reduction. The generic API now supports overriding `top_level_sectors` for mandatory-list jobs. Union reduction and candidate closure derive the target sectors, compute the maximal sector cover together with the physical top sector, and emit those sectors in both the family definition and the reduction job.

Relevant commits:

```text
7278d700e50c829665bfa93ce92d6f991ad0bd60  allow mandatory jobs to extend Kira top-level sectors
f51bacc99478f246f4aa992c887cd026b6c538ec  expose union target sectors as Kira top levels
4017e54a708d9c3537ed6ca4815dee13532ae8ae  extend closure top levels likewise
```

Baseline/boundary jobs remain unchanged.

## Current next sequence

1. Pull the branch:

```powershell
git pull
```

2. Before starting unattended computation, inspect a deliberately small Q12-and-later batch. The recommended first cap is 5 canonical families:

```powershell
.\run_three_loop_master_basis_all.bat plan Q12_full 5
```

This command does not start Kira. It should show the existing Q12 r8s3d0 baseline as already satisfied and list Q12 boundary-r/s/d as the first missing seed steps. The strict five-family cap should select the first five unfinished canonical families beginning at Q12_full: Q12_full, Q17_full, Q18_full, Q20_full, and Q22_full. The plan also reports how many original diagrams those selected families cover and prints low/median/high seed-stage runtime estimates.

3. If the plan is correct, start that limited unattended Stage-2 run:

```powershell
.\run_three_loop_master_basis_all.bat run Q12_full 5
```

The controller now executes the complete per-family decision tree automatically:

```text
existing result reuse
  -> missing baseline/boundary FireFly runs
  -> boundary audit
     -> stable: promotion-ready artifact -> next family
     -> unstable: mandatory union
                  -> candidate closure
                  -> no-rerun closure re-audit
                  -> promotion-ready artifact
                  -> next family
```

A genuine Kira/audit failure or external interruption leaves checkpoint/runtime history and successful audit artifacts in place. The family name does not need to be known. Resume automatically with:

```powershell
.\run_three_loop_master_basis_all.bat resume
```

To keep the resumed unattended block small, apply a fresh strict family cap, for example:

```powershell
.\run_three_loop_master_basis_all.bat resume 5
```

Status only:

```powershell
.\run_three_loop_master_basis_all.bat status
```

4. The unattended runner deliberately does not rewrite `canonical_family_registry.py`. After one or more families reach promotion-ready status, inspect their generated `three_loop_<family>_promotion_ready.json` artifacts and apply reviewed registry promotions in Git.

5. Current formal master-basis status is 9/45 canonical families and 18/72 diagrams. Q12 and Q17 are now formally promoted.

6. Exact coefficient synthesis is complete only for Q01. Cross-family coefficient-API validation remains a later stage after enough master bases are promoted.

7. Master evaluation / epsilon expansion has not started and remains a likely major research bottleneck.

8. Only after the global family/master picture is sufficiently stable should the 72-diagram total `F2(0)` be assembled.

## Agreed post-master-basis roadmap

After all 45 canonical families have stable promoted master bases, an additional formal deliverable is a per-diagram exact master-coefficient archive for all 72 diagrams. This archive supplements, and does not replace, the primary project objective: deriving and reproducing the analytic three-loop electron g-2 result.

The intended pipeline is:

```text
45 canonical families: stable master bases
  -> 72 individual diagrams: exact master coefficients
  -> 72-diagram coefficient archive (JSON + human-readable Markdown)
  -> master integral evaluation / epsilon expansion
  -> per-diagram renormalized F2(0)
  -> category subtotals
  -> literature comparison at the category / diagram-set level
  -> full 72-diagram three-loop g-2 assembly
```

Each individual diagram must retain a relation of the form

```text
F2_diagram^(3)(D) = sum_j c_diagram,j(D) * M_family,j(D)
```

with the following metadata fixed alongside it:
- diagram ID;
- canonical family;
- promoted master-basis ID;
- exact master-integral exponent vectors;
- canonical propagator basis;
- dimensional convention D=4-2 epsilon;
- normalization / mass / sign conventions;
- exact coefficient expressions;
- source artifacts / audit provenance.

The archive should be generated in both machine-readable JSON and human-readable Markdown. It is an additional reusable and independently auditable intermediate dataset for future calculations. The main scientific endpoint remains the analytic evaluation and assembly of the complete three-loop electron g-2 coefficient.

Literature validation is expected primarily at grouped levels because published three-loop g-2 calculations generally report diagram sets / topology classes rather than all 72 individual master decompositions. Therefore the validation hierarchy is:

```text
Level 1: per-diagram exact master-coefficient identities
Level 2: category / literature diagram-set subtotals
Level 3: published analytic/numerical subtotal comparison
Level 4: full three-loop coefficient comparison
```

The per-diagram Level-1 archive is a QEDCalc deliverable even where no published per-diagram reference exists.

## Continuity rule

At the start of a new chat/session, read this file first, then inspect the current branch and newest user-provided local logs. Update this worklog after meaningful milestones, design changes, important failures/fixes, or likely session handoffs.

---
