# QEDCalc 3-loop worklog / handoff notes

Purpose: persistent engineering handoff notes for continuing the 3-loop QED vertex project across ChatGPT sessions.

## Working branch and operating convention

- Repository: `Sanaxen/QEDCalc`
- Branch: `feature/master-basis-initiate-only`
- User environment: Windows 11 frontend, WSL/Linux for Kira/FireFly/Fermat.
- Heavy computations are run by the user locally.
- Assistant implements helpers/APIs/audits/BATs and pushes them.
- Prefer minimal local commands:

```powershell
git pull
.\run_something.bat
```

Do not ask for manual multi-step edits when a helper/BAT can be pushed.

## Scientific deliverable: 72-diagram IBP reduction reference

A central purpose of this project is not only to reproduce the final analytic
three-loop electron g-2 coefficient, but to leave behind a trustworthy,
diagram-by-diagram IBP/master-reduction reference for all 72 three-loop vertex
diagrams.

This is an important deliverable in its own right. A future researcher or
developer attempting the same calculation should be able to compare their
result against a known audited reference instead of discovering only at the very
end that an earlier family mapping, seed choice, IBP reduction, master basis, or
coefficient reduction was wrong.

The intended value of the archive is therefore:

- provide a concrete correctness reference for each of the 72 diagrams;
- make intermediate mistakes detectable before the final 72-diagram sum;
- allow independent implementations to compare exact reductions family by family
  and diagram by diagram;
- preserve the canonical family, stable master basis, and exact reduction
  provenance needed to reproduce the calculation;
- act as a practical guide for later researchers rather than only a record of
  the final g-2 number.

The final project must therefore preserve, for every diagram, enough information
to reconstruct and audit the IBP reduction path. At minimum this includes:

```text
diagram
 -> canonical integral family
 -> exact integral / target set
 -> promoted stable master basis
 -> exact master-coefficient reduction
 -> provenance / audit artifacts
```

Where practical, the archive should include both machine-readable output and a
human-readable explanation. The 72-diagram exact master-coefficient archive
described later in this worklog is the formal realization of this objective.

The project should not treat a successful final numerical/analytic sum as
sufficient evidence by itself. Intermediate family/master/reduction results must
remain independently checkable so that an error cannot stay hidden until the
last stage.

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

## Q18 no-reduction diagnosis: all mandatory targets are masters

A dedicated diagnostic established the actual cause of the repeated Q18 union-reduction stop.

Observed facts:

```text
mandatory targets: 38
prepared/source targets identical: True
all target sectors covered by physical top sector 255
Kira mandatory-list length: 38
Kira reported master integrals: 38
Kira then printed: No integrals to reduce, skipping this family.
```

Therefore the sector configuration was not the cause. Kira had classified every mandatory union target as a master integral, leaving no non-master integral to reduce. In this valid completion mode Kira does not emit `masters.final`, while QEDCalc previously assumed that file must always exist.

The generic master-basis code now recognizes this mode conservatively. It accepts a missing `masters.final` only when a completed Kira log explicitly contains the no-reduction marker, reports exactly the mandatory target count as masters, and lists exactly the same mandatory integral set. The inferred master set is then carried forward with provenance `kira-no-reduction-all-masters`.

This support was added consistently to mandatory-union finalize, candidate closure, and the authoritative no-rerun closure re-audit.

Relevant commits:

```text
09662505563437216c4119860f4b0ece007581c8  generic verified no-reduction/all-masters handling
ae8b52814c1a5b93aacd61fd9672c605d2d98a3f  union finalize support
8c085da8f5960e7e838ca159b71e76f1fa8e3888  candidate closure support
d49157530d9fb00dfb2533ae6b0f117aa50e93df  no-rerun re-audit support
```

The earlier target/top-level-sector extensions remain harmless general support but were not the root fix for Q18.

## Q18 iterative candidate refinement

After the Q18 all-masters/no-reduction union case was handled correctly, candidate closure exposed a second, genuinely mathematical seed-dependence:

```text
candidate envelope: r8s3d0
candidate masters: 38

r9s3d0 -> 38 masters
r8s4d0 -> 38 masters
r8s3d1 -> 3 masters + 35 resolved non-masters
```

Therefore the 38-form candidate is not stable. The d+1 boundary is a strictly stronger reduction context and supplies a new 3-master candidate basis.

The unattended controller has been generalized to perform iterative candidate refinement. When the authoritative no-rerun closure audit fails but a completed boundary run supplies a strict subset of the current candidate masters with exact mandatory-list agreement, that smaller master set is promoted to the next candidate, the common envelope is advanced to that boundary seed, and closure is repeated. This may iterate multiple times until one-axis extensions no longer change the candidate basis.

For Q18 the expected next step is:

```text
38 masters at r8s3d0
  -> refine to 3 masters at r8s3d1
  -> closure at r9s3d1 / r8s4d1 / r8s3d2
  -> refine again if needed
  -> promotion-ready only after stable closure
```

Relevant commits:

```text
9a7f157b6db1ee8d8e6f040f12ac2c818dc2e60a  closure prefers newest refined candidate audit
9f9bb4b80a227ec83a33f34c63721f32eb92a160  iterative candidate refinement in unattended controller
```

## Status-display cleanup: COMPLETE

The checkpoint status display has been updated so historical failures no longer
look like active blockers. It now separates:

- checkpoint entries still marked `running`;
- unresolved error entries;
- superseded error entries belonging to families that are already ready;
- the next auto-resume family.

A stale historical Q03 FireFly running entry is explicitly identified as stale
because Q03 is already formally complete. At the latest check:

```text
auto-resume family: Q04_full
unresolved historical/error entries: 0
```

Raw checkpoint history is preserved for provenance.


## Current next sequence

Current formal master-basis status:

```text
26/45 canonical families complete
52/72 diagrams covered
Q03_full -> Q03_final136 formally promoted
next auto-resume family: Q04_full
```

The active Stage-2 strategy is now masters-first with FireFly fallback:

```text
masters baseline
  -> masters boundary-r / boundary-s / boundary-d
  -> boundary audit
     -> stable: promotion-ready
     -> seed-dependent:
          masters mandatory union
          -> masters candidate closure
          -> stable: promotion-ready
          -> otherwise FireFly fallback/refinement
```

Completed seed reuse is keyed by `family + seed + solver`, preventing an older
FireFly result from silently satisfying an initiate-only `masters` step.

The next unattended test is one canonical family only:

```powershell
git pull
.\run_three_loop_master_basis_all.bat resume 1
```

At present this should start from `Q04_full`.

After each family reaches promotion-ready status, inspect the generated
`three_loop_<family>_promotion_ready.json` artifact and apply the reviewed
registry promotion in Git. Continue until all 45 canonical families have stable
promoted master bases.

Exact coefficient synthesis is still complete only for Q01. The 72-diagram
exact master-coefficient archive, master evaluation / epsilon expansion,
renormalized diagram F2(0), category subtotals, literature comparison, and full
three-loop sum remain later stages.

### Deliberately deferred work

Further expansion of the formal input -> graph -> canonical-family front-end
remains on hold until the 45-family master-basis stage is complete. Deferred
items are:

- additional raw-LaTeX -> graph automation;
- deeper integration of the front-end with master-basis reporting;
- construction of the final all-in-one three-loop report runner;
- non-maintenance documentation expansion for that front-end.

This is the only intentional implementation hold currently recorded in this
worklog.


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


---

## 2026-09-21: formal 72-diagram input -> graph -> canonical-family bridge added

Purpose: restore the missing reproducible front half of the three-loop pipeline while the existing master-basis computation continues independently.

Current long-running computation remains unchanged:

```powershell
.\run_three_loop_master_basis_all.bat resume 4
```

Added formal inputs:

```text
input/three_loop/
  Q01.tex ... Q50.tex
  VP01.tex ... VP12.tex
  VP4A.tex VP4B.tex VP4C.tex
  VP22.tex
  LBL01.tex ... LBL06.tex
  manifest.json
```

Input count:

```text
50 + 12 + 3 + 1 + 6 = 72
```

Each .tex contains the complete amplitude taken from
`3loop_vertex_72_complete_equations.md` plus reviewed provenance metadata:

- diagram ID
- physical family
- source document
- graph metadata

`manifest.json` records SHA-256 for all 72 formal inputs.

Added bridge/audit implementation:

```text
three_loop/input_pipeline.py
examples/three_loop_input_to_family_audit.py
run_three_loop_input_to_family_audit.bat
tests/test_three_loop_input_pipeline.py
doc/three_loop_input_to_family_pipeline.md
```

Canonical front-half flow is now:

```text
3loop_vertex_72_complete_equations.md
  -> input/three_loop/*.tex
  -> formal input graph metadata
  -> exact audit against data/three_loop_topologies.json
  -> existing global classification
  -> existing canonical-family autodiscovery / registry
  -> 45 canonical integral families
  -> existing master-basis pipeline
```

Direct source-vs-registry verification performed during implementation:

```text
source sections          : 72
registry diagrams        : 72
exact graph matches      : 72/72
mismatches               : 0
physical-family counts   : quenched 50 / VP1 12 / VP2 3 / VP22 1 / LBL 6
```

Important scope:

The v1 bridge does not claim arbitrary raw-LaTeX -> Feynman-graph inference.
The reviewed topology metadata is stored together with each complete amplitude
and is independently checked against the executable 72-diagram topology
registry. This provides continuous provenance now and a 72-case regression
oracle for a future raw-LaTeX graph recognizer.

The new audit does not launch Kira/FireFly and does not modify current
master-basis artifacts. It is therefore a front-end provenance layer, not a
replacement for the running `resume 4` computation.

The intended reproducible path is now:

```text
source amplitude
 -> formal input
 -> graph
 -> topology registry
 -> canonical family
 -> IBP/master-basis stage
 -> stable master basis
 -> master evaluation
 -> renormalization
 -> 72-diagram sum
 -> final analytic three-loop coefficient
```


---

## 2026-09-21: formal input-to-family follow-up placed on hold until 72-diagram master-basis completion

The formal 72-diagram input -> graph -> canonical-family front-end has been connected and documented, but further work on this topic is intentionally paused for now.

Current priority is to let the existing 72-diagram master-basis processing complete:

```powershell
.\run_three_loop_master_basis_all.bat resume 4
```

Until the full `run_three_loop_master_basis_all.bat` processing over the 72-diagram workload is complete, do not expand or restructure the new input-to-family pipeline further.

In particular, defer:

- additional raw-LaTeX -> graph automation,
- further integration of the front-end pipeline with master-basis reporting,
- construction of the final all-in-one three-loop report runner,
- additional documentation expansion beyond maintenance fixes.

After the 72-diagram master-basis processing is complete, resume this topic and connect the completed master-basis results to the already established provenance chain:

```text
formal input
 -> graph
 -> topology registry
 -> canonical family
 -> completed master basis
 -> later master evaluation / renormalization / final sum
```

This hold is deliberate so that the currently running master-basis computation remains the main execution priority and is not disturbed by unrelated pipeline restructuring.


---

## 2026-10-01: master-basis speed redesign — initiate-only discovery

Q03_full exposed a severe scaling problem in the Stage-2 master-basis discovery
path. A FireFly run reached about 1.25 million interpolation functions and ran
for more than ten days before an external power loss stopped the process.

The expensive step was not mathematically necessary for the baseline/boundary
purpose. Kira's documented best-practice workflow states that when the goal is
only to determine the master-integral list, the job may stop after
`run_initiate: true` with both triangular reduction and back substitution
disabled. Kira determines and reports the master list before forward
elimination.

A dedicated optimization branch was created:

```text
feature/master-basis-initiate-only
```

New solver mode:

```text
masters
```

For this mode the generated Kira job uses:

```yaml
run_symmetries: true
run_initiate: true
run_triangular: false
run_back_substitution: false
run_firefly: false
```

The unattended Stage-2 controller now uses `masters` for the four routine
master-discovery seeds:

```text
baseline
boundary-r
boundary-s
boundary-d
```

Existing completed FireFly audits remain reusable. Full FireFly reduction is
still retained for the stages that genuinely require reduction/classification
information:

```text
mandatory-union reduction
candidate closure
authoritative no-rerun closure verification
```

The generic master parser accepts either the historical `masters.final`
artifact or Kira initiate-only `master` / `masters` output. The boundary
audit accepts the new solver mode and compares the resulting master sets in the
same way as before.

The intended impact is to remove FireFly rational-function interpolation from
ordinary baseline/boundary master discovery. In a Q03-like case this avoids the
1,254,743-function interpolation phase entirely if Kira initiate completes as
documented.

Validation policy:

1. Run one known completed family with `masters`.
2. Compare the initiate-only master set against the existing FireFly master set.
3. If identical, run Q03_full through the new path.
4. Keep FireFly only for union/closure stages that require actual reductions.

This optimization is prioritized over thread-count increases because the
current workstation is already memory constrained; additional FireFly threads
could increase paging and reduce effective throughput.


## Masters-first initiate-only Stage-2 acceleration

A severe Q03 performance case motivated separating master-basis discovery from the
later coefficient reduction problem. The original Q03 FireFly baseline had run
for more than ten days without completing. Kira initiate-only master discovery
(`solver=masters`) was validated first against already-known families.

Validation against prior FireFly results:

```text
Q08 r7s3d0  : 12 masters  (matches Q08_final12)

Q02 r8s3d0  : 63 masters
Q02 r9s3d0  : 63 masters
Q02 r8s4d0  : 75 masters
Q02 r8s3d1  : 55 masters
```

All Q02 counts exactly reproduce the previously observed FireFly seed results.

Q03 initiate-only discovery:

```text
r9s3d0   -> 844 masters
r10s3d0  -> 844 masters
r9s4d0   -> 1499 masters
r9s3d1   -> 454 masters

intersection -> 139
union        -> 1896
```

The common mandatory-union context required envelope `r9s4d2`. Initiate-only
processing of the 1896 union targets produced a 136-master candidate basis.

The candidate was then tested with the same mandatory closure target set at all
three one-axis extensions:

```text
r10s4d2 -> 136/136 retained, new=0
r9s5d2  -> 136/136 retained, new=0
r9s4d3  -> 136/136 retained, new=0
```

Therefore the existing one-axis Stage-2 closure criterion is satisfied and
`Q03_full -> Q03_final136` is promotion-ready.

The production strategy is now hybrid rather than FireFly-free:

```text
master discovery:
  masters baseline
  -> masters one-axis boundaries
  -> stable: promotion-ready

seed-dependent family:
  masters union
  -> masters candidate closure
  -> stable: promotion-ready

initiate-only failure or unstable closure:
  -> FireFly union/refinement/closure fallback

later exact reduction / coefficient reconstruction:
  -> Kira + FireFly remains available and expected
```

FireFly is intentionally retained for the work it is best suited to: actual
large rational-function reductions and coefficient reconstruction. The new
initiate-only path avoids paying that cost merely to identify a stable master
basis.

Batch-controller safeguards added with this change:

- completed seed reuse is keyed by `family + seed + solver`, so an old FireFly
  result cannot silently satisfy a new `masters` step;
- union and candidate closure run `masters` first;
- existing completed initiate-only union/closure audits are reused;
- if initiate-only rescue does not stabilize, the controller falls back to the
  existing FireFly refinement path.


### Q03 formal promotion

The reviewed promotion-ready artifact for Q03 passed the masters-first one-axis
closure with the same 136-master set at `r10s4d2`, `r9s5d2`, and
`r9s4d3`. The executable canonical registry now records:

```text
Q03_full -> Q03_final136
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### Q04 formal promotion

Q04_full covers Q04/Q46. The masters-first rescue path produced a
92-master candidate at envelope `r9s4d2` from a union of 1826 targets.

The candidate closure passed at all three one-axis extensions:

```text
r10s4d2 -> 92 masters, retained 92/92, new=0
r9s5d2  -> 92 masters, retained 92/92, new=0
r9s4d3  -> 92 masters, retained 92/92, new=0
```

Aggregate closure result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

Therefore the executable canonical registry now records:

```text
Q04_full -> Q04_final92
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### Q06 formal promotion

Q06_full covers Q06/Q44. The masters-first rescue path produced a
91-master candidate at envelope `r9s4d2` from a union of 1051 targets.

The candidate closure passed at all three one-axis extensions:

```text
r10s4d2 -> 91 masters, retained 91/91, new=0
r9s5d2  -> 91 masters, retained 91/91, new=0
r9s4d3  -> 91 masters, retained 91/91, new=0
```

Aggregate closure result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

Therefore the executable canonical registry now records:

```text
Q06_full -> Q06_final91
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### Q11 formal promotion

Q11_full covers Q11/Q31. The masters-first rescue path produced a
129-master candidate at envelope `r9s4d2` from a union of 1461 targets.

The candidate closure passed at all three one-axis extensions:

```text
r10s4d2 -> 129 masters, retained 129/129, new=0
r9s5d2  -> 129 masters, retained 129/129, new=0
r9s4d3  -> 129 masters, retained 129/129, new=0
```

Aggregate closure result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

Therefore the executable canonical registry now records:

```text
Q11_full -> Q11_final129
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### Q13 formal promotion

Q13_full covers Q13/Q33. The first masters-first common-context candidate was
230 masters at envelope `r9s4d2`. Its closure exposed a genuine strict-subset
refinement:

```text
r10s4d2 -> 229 masters, retained 229/230, new=0
r9s5d2  -> 229 masters, retained 229/230, new=0
r9s4d3  -> 230 masters, retained 230/230, new=0
```

The controller therefore refined the candidate from 230 to 229 masters and
advanced the common envelope to `r10s4d2` instead of immediately falling back
to FireFly.

The refined 229-master candidate then passed closure at all three one-axis
extensions:

```text
r11s4d2 -> 229 masters, retained 229/229, new=0
r10s5d2 -> 229 masters, retained 229/229, new=0
r10s4d3 -> 229 masters, retained 229/229, new=0
```

Aggregate result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

Therefore the executable canonical registry now records:

```text
Q13_full -> Q13_final229
```

Q13 also validates iterative initiate-only candidate refinement in production.
The refined closure is computationally heavy, particularly the s+1 direction,
so future performance work should consider whether every refinement round needs
all three full boundary jobs without weakening the scientific closure criterion.

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### Q14 formal promotion

Q14_full covers Q14/Q36. The masters-first rescue path produced a
202-master candidate at envelope `r9s4d2` from a union of 1796 targets.

The candidate closure passed at all three one-axis extensions:

```text
r10s4d2 -> 202 masters, retained 202/202, new=0
r9s5d2  -> 202 masters, retained 202/202, new=0
r9s4d3  -> 202 masters, retained 202/202, new=0
```

Aggregate closure result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

Therefore the executable canonical registry now records:

```text
Q14_full -> Q14_final202
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### Q15 formal promotion

Q15_full covers Q15/Q32. The masters-first rescue path produced an
86-master candidate at envelope `r9s4d2` from a union of 636 targets.

The candidate closure passed at all three one-axis extensions:

```text
r10s4d2 -> 86 masters, retained 86/86, new=0
r9s5d2  -> 86 masters, retained 86/86, new=0
r9s4d3  -> 86 masters, retained 86/86, new=0
```

Aggregate closure result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

Therefore the executable canonical registry now records:

```text
Q15_full -> Q15_final86
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### Q16 formal promotion

Q16_full covers Q16/Q34. Its masters-first path required iterative refinement.
The final candidate was 203 masters at envelope `r10s4d2`.

The refined candidate closure passed at all three one-axis extensions:

```text
r11s4d2 -> 203 masters, retained 203/203, new=0
r10s5d2 -> 203 masters, retained 203/203, new=0
r10s4d3 -> 203 masters, retained 203/203, new=0
```

Aggregate closure result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

The final refinement closure itself took about 5h32m, while the user's total
wall-clock time for the Q16 completion was about 12 hours. This reinforces the
Q13 observation that refinement-round s+1 closure can dominate runtime.

Therefore the executable canonical registry now records:

```text
Q16_full -> Q16_final203
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### Q19 formal promotion

Q19_full covers Q19/Q39. The masters-first rescue path produced a
121-master candidate at envelope `r9s4d2` from a union of 1234 targets.

The candidate closure passed at all three one-axis extensions:

```text
r10s4d2 -> 121 masters, retained 121/121, new=0
r9s5d2  -> 121 masters, retained 121/121, new=0
r9s4d3  -> 121 masters, retained 121/121, new=0
```

Aggregate closure result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

Therefore the executable canonical registry now records:

```text
Q19_full -> Q19_final121
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### Q24 formal promotion

Q24_full covers Q24/Q26. Its masters-first path required iterative refinement,
with the final candidate at envelope `r10s4d2`.

The refined 271-master candidate passed closure at all three one-axis
extensions:

```text
r11s4d2 -> 271 masters, retained 271/271, new=0
r10s5d2 -> 271 masters, retained 271/271, new=0
r10s4d3 -> 271 masters, retained 271/271, new=0
```

Aggregate result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

The final candidate-closure round took about 19h18m. Total wall-clock time for
Q24 was substantially longer because the family had already spent many hours in
earlier stages. Q24 is therefore the current worst-case performance reference
for the masters-first closure pipeline.

During Q24, WSL2 was configured with about 32 GB RAM and 128 GB swap. The WSL
`swap.vhdx` occupied about 128 GB on C:, while QEDCalc output had grown to
about 42 GB. After the run ended the swap VHDX disappeared and C: free space
recovered to about 267 GB. This confirms that the large temporary WSL swap area
was the main source of the acute disk-pressure episode, not only persistent
QEDCalc output.

Therefore the executable canonical registry now records:

```text
Q24_full -> Q24_final271
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### VP03 formal promotion

VP03_full covers VP03/VP11. The baseline masters initiate-only run at
`r7s3d0` produced 17 masters.

The one-axis boundary audit gave:

```text
r8s3d0 -> 17 masters, retained 17/17, stable=True
r7s4d0 -> 37 masters, retained 17/17, stable=True
r7s3d1 -> 17 masters, retained 17/17, stable=True
intersection across available sets: 17
union across available sets: 37
union reduction needed: False
internal audit errors: 0
PASS
```

The larger literal set at `r7s4d0` does not invalidate the baseline basis:
all 17 baseline masters are retained at every tested one-axis extension, so the
boundary audit classifies the family as stable without mandatory-union rescue.

Therefore the executable canonical registry now records:

```text
VP03_full -> VP03_final17
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### VP04 formal promotion

VP04_full covers VP04/VP12. The baseline masters initiate-only run at
`r7s3d0` produced 15 masters.

The one-axis boundary audit was completely stable:

```text
r8s3d0 -> 15 masters, retained 15/15, stable=True
r7s4d0 -> 15 masters, retained 15/15, stable=True
r7s3d1 -> 15 masters, retained 15/15, stable=True
intersection across available sets: 15
union across available sets: 15
union reduction needed: False
internal audit errors: 0
PASS
```

Therefore the executable canonical registry now records:

```text
VP04_full -> VP04_final15
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### VP01 formal promotion

VP01_full covers VP01/VP10. The masters-first rescue path produced a
28-master candidate at envelope `r8s4d2` from a union of 340 targets.

The candidate closure passed at all three one-axis extensions:

```text
r9s4d2 -> 28 masters, retained 28/28, new=0
r8s5d2 -> 28 masters, retained 28/28, new=0
r8s4d3 -> 28 masters, retained 28/28, new=0
```

Aggregate closure result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

Therefore the executable canonical registry now records:

```text
VP01_full -> VP01_final28
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


### Q22 formal promotion

Q22_full covers Q22/Q25. The reviewed FireFly iterative refinement artifact
proposes `Q22_final14` at envelope `r8s3d2`.

The no-rerun closure re-audit verifies all three one-axis extensions with the
same 14-master candidate and exact mandatory-list agreement:

```text
r9s3d2 -> 14 masters, stable=True
r8s4d2 -> 14 masters, stable=True
r8s3d3 -> 14 masters, stable=True
missing candidate masters: 0
extra masters: 0
missing mandatory targets: 0
extra mandatory targets: 0
resolved nonmasters: 54 at each boundary
stable under one-axis extensions: True
errors: []
audit_pass: True
```

Therefore the executable canonical registry now records:

```text
Q22_full -> Q22_final14
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.

Q18_full and Q20_full remain promotion-ready but are intentionally not promoted
in this review step until their referenced closure re-audit payloads are
inspected directly.


### Q20 formal promotion

Q20_full covers Q20/Q40. The reviewed FireFly iterative refinement artifact
proposes `Q20_final1` at envelope `r8s3d1`.

The no-rerun closure re-audit verifies all three one-axis extensions with the
same single-master candidate and exact mandatory-list agreement:

```text
r9s3d1 -> 1 master, stable=True
r8s4d1 -> 1 master, stable=True
r8s3d2 -> 1 master, stable=True
missing candidate masters: 0
extra masters: 0
missing mandatory targets: 0
extra mandatory targets: 0
resolved nonmasters: 38 at each boundary
stable under one-axis extensions: True
errors: []
audit_pass: True
```

Therefore the executable canonical registry now records:

```text
Q20_full -> Q20_final1
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.

Q18_full remains promotion-ready but is intentionally not promoted until its
referenced closure re-audit payload is inspected directly.


### Q18 formal promotion

Q18_full covers Q18/Q38. The reviewed FireFly iterative refinement artifact
proposes `Q18_final3` at envelope `r8s3d1`.

The no-rerun closure re-audit verifies all three one-axis extensions with the
same 3-master candidate and exact mandatory-list agreement:

```text
r9s3d1 -> 3 masters, stable=True
r8s4d1 -> 3 masters, stable=True
r8s3d2 -> 3 masters, stable=True
missing candidate masters: 0
extra masters: 0
missing mandatory targets: 0
extra mandatory targets: 0
resolved nonmasters: 35 at each boundary
stable under one-axis extensions: True
errors: []
audit_pass: True
```

Therefore the executable canonical registry now records:

```text
Q18_full -> Q18_final3
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.

The previously promotion-ready Q18/Q20/Q22 families have now all been reviewed
and formally promoted.


### VP02 formal promotion

VP02_full covers VP02/VP09. The masters-first rescue path produced a
30-master candidate at envelope `r8s4d2` from 409 union targets.

The candidate closure passed at all three one-axis extensions:

```text
r9s4d2 -> 30 masters, retained 30/30, new=0
r8s5d2 -> 30 masters, retained 30/30, new=0
r8s4d3 -> 30 masters, retained 30/30, new=0
```

Aggregate closure result:

```text
stable under tested one-axis extensions: True
internal audit errors: 0
PASS
```

Therefore the executable canonical registry now records:

```text
VP02_full -> VP02_final30
```

Formal master-basis progress is now 26/45 canonical families and 52/72 diagrams.


## 2026-10-07 VP05 masters-first refinement / WSL handoff

Current formal master-basis progress remains:

```text
26 / 45 canonical families
52 / 72 diagrams
```

VP05_full covers VP05/VP06.

### Union-reduction result

For baseline `r8s3d0`, the mandatory union contains 530 targets and requires
envelope `r8s4d2`.

The masters initiate-only union run once returned a non-zero Kira exit after
the useful master list had already been written. Reusing
`results/VP05_full/masters` and running finalize without rerunning Kira gave:

```text
mandatory targets: 530
required envelope: r8s4d2
candidate master count: 64
audit PASS
```

Therefore the valid first candidate is 64 masters at `r8s4d2`.

### 64-master candidate closure

The one-axis closure result is:

```text
r9s4d2 -> 63 masters, retained 63/64, missing=1, new=0, refinement=True
r8s5d2 -> 63 masters, retained 63/64, missing=1, new=0, refinement=True
r8s4d3 -> 64 masters, retained 64/64, missing=0, new=0, stable=True
```

Thus the 64-master candidate is not final. Two independent one-axis extensions
expose the same strict-subset size, so VP05 has a valid 64 -> 63 iterative
refinement signal.

The controller now recovers such a refinement directly from the existing
closure audit instead of rerunning the union stage.

### 63-master closure and heavy r8s6d2 boundary

The next candidate closure includes a heavy `r8s6d2` boundary. This boundary
became much slower than previous VP05 runs, with individual
`Generate equations for topology VP05_full, sector ...` lines taking several
minutes in some sectors.

One attempt terminated before a reusable master list was created. The log ended
after:

```text
Kira starts the reduction of the topology: VP05_full

***** Select equations recursively ************************
length of mandatory list: 530
Algebraic reconstruction is switched off.
```

Since no initiate-only master list existed for that attempt, the boundary could
not be reused scientifically.

The masters-only closure runner was changed so that one failed boundary no
longer immediately aborts the remaining closure boundaries. It preserves the
failed boundary, continues the other boundaries, and leaves the aggregate audit
to decide whether another direction exposes a further strict-subset refinement.

The controller was also changed so that an incomplete masters closure does not
automatically fall back to FireFly union reduction.

Relevant commits on `feature/master-basis-initiate-only`:

```text
d78484947a8b44df032b0e00267ec9c7966bf51c
  reuse completed initiate-only master lists after late Kira exit

f7b6a9986d121a5f77eabd8d4abf065a1b9b1d2c
  resume masters closure from reusable boundary results

2395cf2aca172b976937551f9b43b4b557ebf04d
  prefer passing master-basis audits over failed reruns

d5a2d137f17ab96921c48f15e7fdf9340dba365c
  recover masters refinement from closure before union rerun

256b32801df05380597e351f412a86d72f82fa1e
  stop on incomplete masters closure instead of FireFly fallback

94e98c5077a01562b180fde5a596d5fe3812cf2b
  continue remaining masters closure boundaries after individual failure
```

Important local-state note: one unwanted FireFly/union fallback occurred before
the final `94e98c5` changes had been pulled locally. A later `git pull`
fast-forwarded the local branch from `d5a2d13` to `94e98c5`; the local files
were then verified to contain both:

```text
Preserving all masters results; do not fall back to FireFly automatically.
Preserving this failed boundary and continuing remaining masters closures.
```

Therefore any earlier post-failure return to union reduction should not be used
as evidence of the current controller behavior.

### WSL resource correction

A separate configuration mistake was found in `%USERPROFILE%/.wslconfig`.

The previous setting was:

```ini
[wsl2]
memory=32GB
swap=10485760000
```

The bare numeric swap value is only about 10 GB, not 100 GB. Runtime inspection
confirmed about 9.8 GiB swap.

The file was edited directly to request 100 GB swap, WSL was shut down and
restarted, and the active configuration was verified as:

```text
Mem:  about 31 GiB
Swap: 100 GiB
```

The Windows WSL Settings UI had not produced the intended swap size, so the
direct `.wslconfig` edit is the authoritative setup for this run.

The dmesg captured after restart contained WSLg/dxgkrnl warnings and journal
recovery messages, but no preserved OOM evidence from the earlier failed Kira
run. Because WSL had restarted, the previous kernel log cannot be used to rule
OOM in or out for that earlier attempt.

### Resume point

Use the current branch without switching:

```text
feature/master-basis-initiate-only
```

The next normal entry point is:

```powershell
.\run_three_loop_master_basis_all.bat resume 1
```

Expected logic:

1. reuse the existing VP05 64 -> 63 refinement evidence;
2. do not rerun the already-valid 530-target union merely because a later closure boundary failed;
3. continue the 63-master candidate closure;
4. reuse any boundary that already has a validated initiate-only master list;
5. if one boundary fails before producing a master list, preserve it and continue the remaining boundaries;
6. if another boundary exposes a strict subset, promote that subset and continue iterative refinement;
7. promote VP05 only after a candidate is stable under all required one-axis checks.

Do not formally register `VP05_finalN` yet. The valid state at handoff is:
64-master union candidate -> proven 63-master refinement -> 63-master closure
still in progress.


### 2026-10-07 VP05 closure-target optimization: 530 -> 63

A key performance/interpretation correction was made after reviewing the VP05
history around the 64 -> 63 refinement.

Observed evidence:

```text
initial candidate at r8s4d2: 64 masters
r9s4d2: 63/64 retained, one candidate disappears
r8s5d2: 63/64 retained, one candidate disappears
r8s4d3: 64/64 retained
```

The resulting refined candidate file contains exactly 63 masters.

The later closure jobs had still been using the original 530 union targets as
their mandatory list. This caused very large Kira equation-generation jobs and
made it difficult to distinguish a true mathematical instability from an
incomplete run caused by resource exhaustion or the earlier WSL swap
misconfiguration.

The important interpretation change is:

- the 530-target union reduction remains the proof that the original union target
  set reduces into the candidate basis;
- after a strict-subset refinement has already been established, the next
  one-axis stability test only needs to check whether the refined candidate
  masters remain masters in the stronger envelopes;
- therefore the refinement-stage candidate closure should use the refined
  candidate list itself as the mandatory list instead of replaying all 530 union
  targets.

Implementation change on branch
`feature/master-basis-initiate-only`:

```text
examples/three_loop_master_basis_candidate_closure.py
```

The resolver now selects:

```text
initial union candidate closure:
  closure_mode = union-plus-candidate

refinement-stage closure:
  closure_mode = refined-candidate-only
```

Relevant commits:

```text
bbeeef559db5271db242f299ee0eac2f33c44131
  optimize refined master-basis closure targets

f89b24352c9074c11aa53d1e3ed477e5bcbb828a
  fix refined closure mode propagation
```

The VP05 prepare step was rerun successfully and verified:

```text
family: VP05_full
candidate envelope: r8s5d2
union targets: 530
candidate masters: 63
closure mode: refined-candidate-only
closure targets: 63
mandatory target sectors:
[73, 78, 79, 101, 109, 116, 117, 118, 126, 127, 199, 201, 202, 203,
 204, 205, 206, 207, 228, 229, 230, 231, 234, 237, 238, 239]
Kira top-level sectors: [255]
boundaries:
  r9s5d2
  r8s6d2
  r8s5d3
```

This is a major turning point for VP05. The previous heavy r8s6d2 run used 530
mandatory targets and reached severe paging/swap pressure. The new run will test
the same three refinement boundaries using only the 63 refined masters.

Do not use the earlier incomplete r8s5d2/r9s5d2/r8s6d2 runs as evidence of
mathematical instability. They were incomplete Kira runs, not completed closure
proofs.

Current next step:

```powershell
.\run_three_loop_master_basis_candidate_closure.bat VP05_full r8s3d0 masters
```

Expected validation target:

```text
r9s5d2 -> 63 masters
r8s6d2 -> 63 masters
r8s5d3 -> 63 masters
```

If all three are stable, VP05 can then be considered for formal promotion to a
63-master final basis. Until that verification completes, do not register
`VP05_final63`.


### 2026-10-08 VP05 63-master closure: one boundary passes, two resource-exhausted

The optimized 63-target closure was executed for the refined VP05 candidate.

Aggregate audit:

```text
family: VP05_full
candidate envelope: r8s5d2
union targets: 530
candidate masters: 63
closure targets: 63

r9s5d2: masters=63 stable=True
  retained candidate: 63/63
  missing candidate masters: 0
  new masters: 0
  refinement candidate: False

r8s6d2: no masters.final, initiate-only master list, or verified no-reduction master set found
r8s5d3: no masters.final, initiate-only master list, or verified no-reduction master set found

stable under tested one-axis extensions: False
internal audit errors: 2
```

Interpretation:

- r9s5d2 is a completed positive stability check for the 63-master candidate.
- r8s6d2 and r8s5d3 are NOT mathematical instability results. They are incomplete
  Kira computations with no reusable master list, so those directions remain
  unproven.
- During the heavy run, swap usage exceeded 180 GB while CPU utilization remained
  very low. Therefore simply repeating the same full Kira closure at r8s6d2 or
  r8s5d3 is not an acceptable strategy on the current machine.
- The 530 -> 63 mandatory-target optimization reduced the target count and sector
  count, but the r8s6d2/r8s5d3 envelopes themselves still generate an
  impractically large IBP system.

Do not register VP05_final63 yet.

Next development objective: obtain the missing s- and d-direction stability
evidence for the 63-master candidate without replaying the full
equation-generation workload at r8s6d2 and r8s5d3. Prefer a targeted masters/rank
or candidate-only proof over increasing swap or rerunning the same closure.


### 2026-10-08 VP05 refined-sector closure still stalls at sector 204

The refinement-stage closure was rerun after two reductions in workload:

1. mandatory targets reduced from 530 to the 63 refined candidate masters;
2. Kira top-level sectors reduced from the full family top sector `[255]` to
   the refined candidate maximal sectors `[127, 239]`.

The run correctly started with:

```text
length of mandatory list: 63
Generate equations for topology VP05_full, sector 73 (1 of 91)
```

This reduced the number of generated sectors from the earlier 94/142-scale
runs, and initially swap usage stabilized around 75 GB.

However the run later stalled at:

```text
Generate equations for topology VP05_full, sector 204 (28 of 91)
```

with no progress for about 2.5 hours.

Resource observation at that point:

```text
WSL memory: ~31 GB, effectively at limit
configured memory limit: 30 GB
swap: ~130 GB and still elevated
configured swap limit: 200 GB
CPU utilization: ~5%
```

The swap curve rose from roughly 75 GB to roughly 130 GB while the same sector
remained active, indicating paging/thrashing rather than productive CPU-bound
reduction.

Conclusion:

- the 530 -> 63 target reduction helped but was not sufficient;
- restricting top-level sectors to [127,239] also helped but was not sufficient;
- sector 204 in the r8s6d2-style refinement envelope remains pathological on
  the current machine;
- simply increasing swap further or repeating the same Kira closure is not an
  acceptable path.

Current scientifically valid status remains:

```text
r9s5d2 -> 63 masters, stable=True
r8s6d2 -> unproven (resource-incomplete)
r8s5d3 -> unproven (resource-incomplete)
```

Do not register `VP05_final63` yet.

Next objective: replace the remaining full-envelope Kira closure with a more
targeted stability proof for the 63 candidate masters, preferably avoiding
full recursive equation generation through the pathological sector 204.


### 2026-10-08 VP05 targeted sector-local closure strategy

After the refined 63-target closure still stalled at sector 204 with heavy
paging, the remaining proof strategy was changed again.

New method:

- keep the already-proven full-union reduction and the 64 -> 63 refinement;
- group the 63 refined candidate masters by their exact sector;
- for one stronger seed, create one small initiate-only Kira project per exact
  candidate sector;
- use only that sector's candidate integrals as mandatory targets;
- set both `reduce_sectors` and the family `top_level_sectors` to that exact
  sector;
- aggregate the retained candidate masters across all sector-local projects.

This avoids asking one Kira process to construct the full recursive system for
all candidate sectors at once, especially the pathological sector-204 branch.

New files:

```text
examples/three_loop_master_basis_candidate_sector_closure.py
run_three_loop_master_basis_candidate_sector_closure.bat
```

Relevant commits:

```text
235facd2d3f0272e5d329c731f3d890a037a4ebf
  Add sector-local refined master closure

625736eec3ab480b1967019d2c20c39c1c5a26bf
  Add sector-local closure runner
```

Validation rule:

Do NOT use the sector-local result as new evidence immediately. First validate
the method on `r9s5d2`, where the previous full closure already established:

```text
63 masters
retained 63/63
stable=True
```

Run:

```powershell
.\run_three_loop_master_basis_candidate_sector_closure.bat VP05_full r8s3d0 r9s5d2
```

Only if the sector-local audit independently retains all 63 candidates should
the same method be applied to the resource-blocked `r8s6d2` and `r8s5d3`
directions.

VP05 is still not formally promotable at this point.


### 2026-10-08 sector-local validation failed without preferred masters

The first sector-local validation was intentionally run on the already-known
stable boundary `r9s5d2`.

Result:

```text
candidate masters: 63
candidate sectors: 26
retained candidate total: 50/63
missing candidate masters: 13
stable under sector-local closure: False
internal audit errors: 11
```

This does NOT overturn the existing full-closure result
`r9s5d2 -> 63/63 stable=True`.

Interpretation: independently initiated sector-local Kira projects are free to
choose different but equivalent master bases. Therefore literal membership of
the original candidate integrals in each local `masters` list is not a valid
stability criterion unless the basis choice is fixed.

The sector-local method in its initial form is rejected as a proof method.

Kira supports `preferred_masters`, which must be supplied before the reduction
and is specifically intended to prefer a chosen master basis. The local
strategy is therefore revised as follows:

- each exact-sector project still contains only that sector's refined candidate
  targets;
- the same target list is also written as a `preferred_masters` file;
- the generated Kira job points to that file before `run_initiate`;
- the method must again reproduce the known `r9s5d2 = 63/63` result before it
  can be used for `r8s6d2` or `r8s5d3`.

Implementation commits:

```text
3374e0ea73a4761461144f5f1ae5c22c56ba40ee
  Support preferred masters in Kira project export

56120861c719aefb8d2fb53e06a1e23592725b57
  Pin sector-local closure to preferred candidate masters
```

Do not use the earlier 50/63 sector-local audit as mathematical evidence against
the 63-master candidate.


### 2026-10-09 preferred-masters sector-local validation succeeds

The revised sector-local closure with Kira `preferred_masters` was rerun on the
already-known stable boundary `r9s5d2`.

Result:

```text
retained candidate total: 63/63
missing candidate masters: 0
stable under sector-local closure: True
internal audit errors: 0
```

This exactly reproduces the previous full-closure result for `r9s5d2`.

Therefore the preferred-masters sector-local method is now validated as a
scientifically acceptable lightweight closure test for the refined 63-master
candidate.

The earlier 50/63 result from the unpinned sector-local run was a basis-choice
artifact, not evidence of true instability.

Next proof steps are now authorized:

```powershell
.\run_three_loop_master_basis_candidate_sector_closure.bat VP05_full r8s3d0 r8s6d2
.\run_three_loop_master_basis_candidate_sector_closure.bat VP05_full r8s3d0 r8s5d3
```

If both directions also return:

```text
retained candidate total: 63/63
missing candidate masters: 0
stable under sector-local closure: True
internal audit errors: 0
```

then all three one-axis extensions will have positive stability evidence and
VP05 can proceed to formal promotion as a 63-master basis.


### 2026-10-09 resource behavior of validated r9s5d2 sector-local run

The successful preferred-masters sector-local validation run for `r9s5d2`
also showed substantially improved memory behavior compared with the previous
monolithic closure.

Observed from the WSL memory/swap monitor:

```text
configured WSL memory limit: 30 GB
memory peak: ~29.37 GB
configured swap limit: 200 GB
swap peak: ~6.97 GB
swap at end: ~0 GB
```

The physical-memory curve repeatedly rises and falls between per-sector Kira
projects instead of remaining pinned while swap accumulates.  Swap usage stays
small and is released again.

This is qualitatively different from the failed monolithic closure, where swap
grew to roughly 130 GB while sector 204 remained stalled for hours.

Conclusion: the preferred-masters sector-local decomposition is not only
validated against the known 63/63 master result, but also removes the severe
paging/thrashing behavior on the current machine.


### 2026-10-09 r8s6d2 sector-local run hits a new pathological branch

After validating the preferred-masters sector-local method on `r9s5d2`, the
same method was applied to `r8s6d2`.

The run progressed through the first ten local projects but stalled in:

```text
[11/26] Kira project
Generate equations for topology VP05_full, sector 197 (4 of 12)
```

with no visible progress for about one hour.

Observed resource state:

```text
WSL memory: ~29.2 GB / 30 GB
swap: ~94.6 GB / 200 GB and rising
CPU: low
```

The memory graph remained pinned near the physical limit while swap grew
monotonically, unlike the successful `r9s5d2` validation where swap peaked at
only ~7 GB and was released between projects.

Conclusion:

- preferred-masters sector-local decomposition is valid and efficient for
  `r9s5d2`;
- `r8s6d2` still contains an intrinsically pathological local branch;
- the current blocking point is inside the 11th local project, where Kira is
  generating sector 197 as part of a 12-sector recursive system;
- continuing by consuming more swap is not acceptable;
- the next optimization must target this individual local project/recursive
  branch rather than reverting to larger closure runs.

The run should be stopped at this point. Completed earlier local projects should
be preserved and reused; do not recompute them unnecessarily.


### 2026-10-09 resume support and single-sector ordering probe

After stopping the `r8s6d2` sector-local run at project 11/26, the workflow was
hardened so completed local projects are preserved.

Resume behavior:

- completed exact-sector projects are detected by matching both the mandatory
  target file and preferred-master file and by finding a usable master result;
- reusable projects are not regenerated or cleaned;
- only incomplete projects are printed to the BAT runner;
- displayed progress keeps the original global index, e.g. the resumed run
  continues at `[11/26]` rather than `[1/16]`.

Implementation commits:

```text
41f4b814befb24395c46e2db94aa458b3c8eb063
  Resume sector-local closure from completed projects

5fae228d6123985a13143426cfc6483f73a0f69e
  Preserve global sector progress indices on resume

011cc9a3e6c8cf4a20cdff448f115649a8333882
  Show global sector index when resuming local closure
```

The blocking project is exact sector 199; during its recursive equation
generation Kira stalls in subsector 197 at the `r8s6d2` envelope.

Because this local project already contains only one candidate target, further
target splitting is impossible.  The next optimization axis is Kira integral
ordering.  Kira provides eight predefined orderings and explicitly recommends
testing different orderings because runtime and memory can vary strongly.

A single-sector probe runner was added:

```text
run_three_loop_master_basis_candidate_sector_probe.bat
```

Commit:

```text
0f8b2cfa4f4abfa45606bab1959b313aaa4c9d0c
  Add single-sector Kira ordering probe
```

First probe:

```powershell
.\run_three_loop_master_basis_candidate_sector_probe.bat VP05_full r8s3d0 r8s6d2 199 5
```

This cleans and reruns only the failed sector-199 project's runtime outputs.
All already-completed sector-local projects remain untouched.

Ordering 5 is chosen first because it retains the scalar-product-vs-dot
preference of the default ordering 1 while changing sector ordering so
subsectors of the declared top-level sector are preferred over outside sectors
with the same number of lines.

Do not resume the full 26-project run until this probe is evaluated.


### 2026-10-09 sector-199 ordering-5 probe still thrashes

The targeted probe for the pathological `r8s6d2`, exact-sector-199 project was
run with Kira integral ordering 5.

Compared with the default ordering, it progressed further inside the problematic
recursive branch:

```text
default-like run: sector 197 (4 of 12)
ordering 5 probe: sector 197 (7 of 12)
```

However the ordering-5 probe then remained at sector 197 for roughly two hours.

Observed resource state:

```text
WSL memory: ~29.1 / 30 GB
swap: ~100 GB and rising/plateaued at very high usage
CPU: ~1.4%, peak ~7.2%
```

Conclusion:

- ordering 5 improves equation-generation progress, so integral ordering does
  matter for this pathological branch;
- nevertheless it still becomes paging dominated and is not acceptable as the
  production proof path;
- stop the ordering-5 probe rather than consuming more swap.

Next targeted experiment: rerun only the same exact-sector-199 project with
integral ordering 6.  Orderings 5 and 6 share the line-count/top-level-sector
sector ordering, while changing the dot-vs-irreducible-scalar-product
complexity preference.  Since preferred masters are already pinned, this is
being tested as an equation-generation/performance optimization, not as a
change to the intended candidate basis.

Command after stopping ordering 5:

```powershell
.\run_three_loop_master_basis_candidate_sector_probe.bat VP05_full r8s3d0 r8s6d2 199 6
```

Do not resume the full 26-project run yet.


### 2026-10-09 sector-199 ordering-6 probe also stalls

The same targeted exact-sector-199 probe was repeated with Kira integral
ordering 6 after ordering 5 had stalled.

Observed:

```text
Generate equations for topology VP05_full, sector 197 (7 of 12)
```

remained unchanged for more than one hour.

Resource state was again paging dominated:

```text
WSL memory: ~29.2 / 30 GB
swap: ~100 GB
CPU: ~3%, low overall utilization
```

This is essentially the same failure mode as ordering 5.  The probe was stopped.

Conclusion:

- changing only the Kira integral ordering is insufficient;
- orderings 5 and 6 both reach sector 197 (7 of 12) and then become
  memory/swap dominated;
- do not continue with long unattended runs or simply consume more swap;
- do not spend time brute-forcing orderings 7/8 unless later evidence suggests
  a specific reason.

Next strategy: avoid generating the full initiate system for the exact-sector-199
candidate.  Build a direct reducibility test for the single candidate integral,
using the minimum necessary relation/target context, and use that to determine
whether it remains independent at the `r8s6d2` envelope.


### 2026-10-09 direct single-candidate reducibility probe

After ordering 5 and 6 both stalled in the same exact-sector-199 branch, the
strategy was changed from "discover the complete local master set" to "directly
test the one blocking candidate".

The new direct probe:

- identifies the single refined candidate in exact sector 199;
- selects only that integral as the mandatory reduction target;
- deliberately excludes that target from `preferred_masters`;
- keeps only already-known refined candidate masters from proper subsectors of
  sector 199 as preferred masters;
- runs an ordinary Kira reduction, so a successful reduction produces an
  explicit relation rather than merely a master-list membership test.

This changes the question from:

```text
What is the entire master set of sector 199 at r8s6d2?
```

to:

```text
Does this one sector-199 candidate reduce to the already-known lower-sector
candidate basis at r8s6d2?
```

New files:

```text
examples/three_loop_master_basis_candidate_direct_reducibility.py
run_three_loop_master_basis_candidate_direct_reducibility.bat
```

Commits:

```text
2676837f8de310b3c4e87f7b58c55d97f2d13353
  Add direct single-candidate reducibility probe

5225a400a079a957bde5a0fa252dcc84b34747cd
  Add direct reducibility runner
```

First run:

```powershell
.\run_three_loop_master_basis_candidate_direct_reducibility.bat VP05_full r8s3d0 r8s6d2 199 5
```

Ordering 5 is retained for the first direct test because it progressed farther
than the default ordering in the previous initiate-only probe.  The important
change is not the ordering; it is the removal of the target itself from the
preferred basis and the restriction of preferred masters to proper subsectors.

Interpretation:

- `conclusion: reducible` means the sector-199 candidate is not a master in
  this stronger envelope and the 63-master basis needs refinement.
- `conclusion: retained-master` after a completed reduction means it remains
  independent in this direct proper-subsector context.
- if equation generation still reaches the same paging-dominated sector-197
  bottleneck, this approach is insufficient and the next step must be shell /
  user-defined-system generation rather than another long Kira run.


### 2026-10-09 direct single-candidate reduction still reaches sector-197 bottleneck

The direct reducibility probe for the single exact-sector-199 candidate was run
at `r8s6d2` with ordering 5.

Despite selecting only one mandatory target and excluding that target from
`preferred_masters`, Kira again entered the same recursive equation-generation
branch:

```text
Generate equations for topology VP05_full, sector 197 (7 of 12)
```

Resource state at the observation point:

```text
WSL memory: ~29.3 / 30 GB
swap: >100 GB
CPU: ~3%
```

This shows that the bottleneck is not caused primarily by the number of mandatory
targets or by preferred-master basis selection.  It is inside Kira's ordinary
IBP/equation generation for the r8s6d2 sector-199 -> sector-197 branch itself.

Conclusion:

- stop the direct Kira reduction probe;
- do not continue trying ordinary Kira initiate/reduction variants for this
  branch;
- the next implementation must avoid regenerating the full recursive sector-197
  system.

Next direction: generate only the incremental `s=6` shell relative to the
already-covered `r8s5d2` envelope, and feed those additional relations into a
user-defined / externally prepared linear system (or an equivalent targeted
rank test).  The old s<=5 system should be treated as already established
context rather than regenerated.


### 2026-10-09 incremental s=6 shell audit implemented

The direct single-candidate Kira reduction still regenerated the same pathological
sector-197 system, so the next step now avoids Kira entirely at first.

A QEDCalc-side incremental shell enumerator was added to compare two seed
envelopes and list only integrals newly admitted by the stronger seed.

For the blocked boundary:

```text
r8s5d2 -> r8s6d2
```

this isolates the new `s=6` shell while treating the previously established
`s<=5` domain as existing context.

New files:

```text
examples/three_loop_master_basis_incremental_shell.py
run_three_loop_master_basis_incremental_shell.bat
```

Commits:

```text
83f34f4fe3955eae7afc028f11880cb6bafe1055
  Add incremental seed-shell audit

a68e2e5856d0e020c367a3e1d062d6e9d0d61c17
  Add incremental seed-shell runner
```

First diagnostic run:

```powershell
.\run_three_loop_master_basis_incremental_shell.bat VP05_full r8s5d2 r8s6d2 199
```

This does not launch Kira. It enumerates the new shell for sector 199 and all of
its subsectors using the same QEDCalc r/s/d complexity convention and writes a
JSON/TXT audit.

The immediate goal is to measure the actual size and sector distribution of the
new s=6 shell before designing an external/user-defined rank system.  No further
large Kira run should be started until this audit is inspected.


### 2026-10-09 candidate-centered incremental-shell audit

The first incremental-shell audit showed that the full `r8s5d2 -> r8s6d2`
difference under top sector 199 is still very large:

```text
sectors with new integrals: 31
new integrals total: 868824
sector 197: 25740
sector 199: 19404
```

Thus simply externalizing the whole new `s=6` shell would still create an
unnecessarily large system.

The next diagnostic narrows this shell around the single exact-sector-199
candidate in 12-dimensional propagator-index space.  It reports only new-shell
integrals within a chosen L1 distance of the candidate.

Radius interpretation:

```text
radius 1: single-index shifts
radius 2: also includes +e_i-e_j style two-index shifts
```

This is only a sizing/graph-neighborhood diagnostic, not yet an IBP proof.

New files:

```text
examples/three_loop_master_basis_candidate_neighborhood.py
run_three_loop_master_basis_candidate_neighborhood.bat
```

Commits:

```text
a0785b9f6b6d5a789620c5e7faf532d0b2ab2303
  Add candidate-centered shell neighborhood audit

c77a49d4e0e364c27572fe9c7e2ea2bb8dde0e85
  Add candidate neighborhood audit runner
```

First run:

```powershell
.\run_three_loop_master_basis_candidate_neighborhood.bat VP05_full r8s3d0 r8s5d2 r8s6d2 199 2
```

The purpose is to determine whether the 45,144 new integrals in sectors
197+199, and the 868,824-shell total, collapse to a small candidate-centered set
that is practical for an exact targeted IBP relation generator.


### 2026-10-09 candidate-neighborhood radius-2 audit was below the s-shell lower bound

The first candidate-centered shell audit returned:

```text
target: VP05_full[1,1,1,0,0,0,1,1,0,0,0,0]
radius: 2
nearby incremental integrals: 0
```

This zero result is expected and does not imply that the new shell is
disconnected from the candidate.

The target has complexity:

```text
r5s0d0
```

while the stronger boundary differs from the already-covered domain only by:

```text
s <= 5  ->  s <= 6
```

Therefore every newly admitted integral has total negative-index degree
`s=6`, so its L1 index distance from an `s=0` candidate is at least 6.
A radius-2 search was below this rigorous lower bound.

The neighborhood audit was updated to print the candidate complexity and the
minimum L1 distance implied by the s-bound.

Commit:

```text
a9dad27bc3a8469ef6ba57f8eca87b70f69c42fb
  Report minimum candidate-to-shell distance
```

The next meaningful diagnostic is radius 6:

```powershell
.\run_three_loop_master_basis_candidate_neighborhood.bat VP05_full r8s3d0 r8s5d2 r8s6d2 199 6
```

Radius 6 isolates the shortest possible newly admitted s=6 shell around the
sector-199 candidate.  This should be inspected before implementing any exact
targeted IBP generator.


### 2026-10-09 native-QEDCalc IBP candidate probe

The radius-6 candidate-centered shell audit reduced the new `s=6` domain from
868,824 integrals to:

```text
924 nearby incremental integrals
all in exact sector 199
```

Rather than feeding those 924 directly to Kira, the existing native QEDCalc IBP
engine is now reused.

Relevant existing functionality in `qedcalc.operations.ibp`:

```text
generate_ibp_system
bounded_seed_domain
specialize_ibp_system
laporta_forward_eliminate
reduce_integral
```

A generic bridge from canonical three-loop `FamilySpec` objects to QEDCalc's
native `IntegralFamily` representation was added, including exact reconstruction
of the complete scalar-product basis from the 12 Kira propagators.

New files:

```text
three_loop/native_ibp_family.py
examples/three_loop_master_basis_candidate_native_ibp_probe.py
run_three_loop_master_basis_candidate_native_ibp_probe.bat
```

Commits:

```text
64e866babf4ee7691014405fe06dd2243d14fb9a
  Add generic native IBP bridge for three-loop families

4838de93a550a7c6e8f2fee3ef46efb8ab453975
  Add native IBP candidate reducibility probe

61bfd5cd600eb4251fceead85de6b51a6eb620ed
  Add native IBP candidate probe runner
```

Probe logic:

- target: the single refined candidate in exact sector 199;
- the other 62 refined candidates are protected from elimination;
- generate a bounded native-IBP neighborhood around the target;
- specialize coefficients at two independent exact-rational generic points;
- perform sparse forward Laporta elimination;
- recursively reduce the target;
- call it a positive reducibility witness only if the target reduces entirely to
  protected refined candidates at both probe points.

An unsolved target is explicitly treated as inconclusive, not as proof that the
target is a master.

Start conservatively with degree 3:

```powershell
.\run_three_loop_master_basis_candidate_native_ibp_probe.bat VP05_full r8s3d0 199 3
```

Do not jump directly to degree 6.  Inspect seed/equation/integral counts and
target status first, then raise the degree only as justified by the observed
growth.


### 2026-10-10 native IBP degree-3 probe was CPU-bound for >11 hours

The first native-QEDCalc IBP probe at degree 3 was observed after more than
11 hours with no console progress.

Windows process state showed:

```text
python.exe still running
CPU time: ~11h42m
threads: 1
private memory: ~2.2 GB
overall CPU: <1% to a few percent on a many-core machine
```

This indicates a live but effectively single-threaded symbolic bottleneck, not
paging/thrashing.

Code inspection found a major avoidable cost in
`qedcalc.operations.ibp.generate_ibp_system`: the reduced directional
derivative `v.dD_a/dk`, which is independent of the seed integral powers, was
being recomputed by SymPy for every seed.

For degree 3 around the five-line target, the bounded seed domain contains about
455 seeds.  Repeating the same denominator/loop/vector symbolic derivative work
hundreds of times is therefore unnecessarily expensive.

Optimization implemented:

- add `IBPTemplate`;
- compile all seed-independent reduced directional derivatives once per family;
- generate each seed's IBP rows by inexpensive index shifts from those templates;
- avoid full simplify/factor during row generation;
- add visible progress messages for family construction, template compilation,
  seed count, equation generation, pruning, and each generic-point elimination.

Commits:

```text
e438747525253607e065e2460b60d208748a46e3
  Compile IBP derivative templates once per family

5ae45b76440e9de5f6eb99cee38525eee930fe43
  Show native IBP probe progress
```

The old >11-hour process should be stopped.  After pulling these changes, rerun
the same degree-3 probe.  The new progress output will identify whether the next
bottleneck is template compilation or sparse elimination.


### 2026-10-10 native IBP elimination bottleneck moved to sparse Laporta

After derivative-template compilation, the degree-3 native probe progressed to:

```text
[native-ibp] probe 1: eliminate 6825 equations...
```

and then became effectively single-core CPU bound.  This confirmed that the
dominant cost had moved from IBP equation generation to symbolic sparse Laporta
elimination.

Two optimizations were implemented:

1. Numeric rational coefficients now bypass `sympy.cancel()` in the generic
   sparse path.
2. A dedicated finite-field sparse Laporta backend was added for generic-rank /
   reducibility diagnostics.  Each rational probe is mapped to a large prime
   field and eliminated with Python integer modular arithmetic.

The native candidate probe now uses two independent rational probe points and
two large primes.  A positive result is treated as a finite-field generic-rank
reducibility witness, not yet as a symbolic coefficient identity.

Commits:

```text
72534c7bc06734440000475a81c5ab67dccceda5
  Avoid symbolic cancellation for numeric IBP probes

7dd1495fbcbff256c7e723ba319e778724df02c0
  Add finite-field sparse IBP elimination

904f800e479f528aaa6b50db6162ca78290111d1
  Use finite-field elimination in native IBP probe
```

The previous symbolic elimination run should be stopped and the same degree-3
probe rerun after pulling these changes.


### 2026-10-10 native finite-field degree-3 candidate probe completes

After switching the native sparse Laporta stage to finite-field arithmetic, the
degree-3 sector-199 probe completed successfully.

Result:

```text
seed count: 455
symbolic equations: 6825
symbolic integrals: 9825

probe 1:
  prime: 2147483647
  rules: 6410
  target_solved: False
  residual: 1
  protected: 0
  unprotected: 1
  reducible_to_protected_basis: False

probe 2:
  prime: 2147483629
  rules: 6410
  target_solved: False
  residual: 1
  protected: 0
  unprotected: 1
  reducible_to_protected_basis: False

status: unsolved-in-finite-neighborhood
audit pass: False
```

The identical rank/pivot outcome at two independent probe points/primes is a
good consistency check for the finite-field implementation.  However,
`target_solved=False` is explicitly inconclusive: degree 3 does not provide
enough local IBP closure to reduce the target, but it does not establish the
target as a master.

Next step: increase the bounded native-IBP neighborhood to degree 4.

For the 12 available index-shift directions, the bounded multiset seed count is
expected to grow from 455 at degree 3 to roughly 1820 at degree 4, giving about
27300 raw IBP equations (15 equations per seed).  This is substantially larger
but is now handled by the finite-field backend rather than symbolic rational
elimination.

Run:

```powershell
.\run_three_loop_master_basis_candidate_native_ibp_probe.bat VP05_full r8s3d0 199 4
```

Interpretation remains unchanged: only a consistent explicit reduction to the
protected refined basis is positive reducibility evidence; an unsolved degree-4
target remains inconclusive.


### 2026-10-10 degree-4 native finite-field elimination still too slow

The degree-4 native probe reached:

```text
seed count: 1820
raw equations: 27300
integrals after zero-sector prune: 32733
probe 1: eliminate 27300 equations over F_2147483647...
```

and remained in that elimination stage for about seven hours.

Observed resource behavior:

```text
CPU: ~3.6% of 28 logical CPUs, effectively one saturated logical core
memory peak: ~2.7 GB
current memory: ~1.6 GB
swap-equivalent/page-file usage: ~3.2 GB
```

This is not a memory/swap bottleneck.  It is a single-core sparse-elimination
algorithm bottleneck.

The run should be stopped rather than continued.

A target-connected row-pruning stage was added.  Before finite-field Laporta,
QEDCalc now constructs the bipartite equation/integral graph, floods from the
single sector-199 target, and discards every equation in disconnected
components.  Such disconnected rows cannot contribute to a reduction witness
for the target.

Commits:

```text
448c40cf9f779457d2992846445fa088b95ffc05
  Add target-connected finite-field row pruning

5a476ecfe3a0f634e49c1727d61f74b958377f5c
  Prune native IBP probe to target-connected rows
```

After pulling, rerun degree 4 and inspect:

```text
[native-ibp] probe 1: target-connected prune from 27300 equations...
[native-ibp] probe 1: connected equations=...
```

If the connected count remains close to 27300, this graph-component pruning is
insufficient and the next optimization must reduce the elimination algorithm
itself rather than the row set.


### 2026-10-10 connected-component pruning did not reduce degree-4 system

The target-connected graph pruning was tested on the degree-4 finite-field
system and returned:

```text
target-connected prune from 27300 equations
connected equations=27300
```

Therefore the entire degree-4 equation set belongs to the same connected
component as the sector-199 target.  Connectivity alone cannot reduce the
system.

A stricter Laporta-order-aware diagnostic was added:

- discard rows whose hardest integral is below the target rank;
- process only rows capable of contributing to the target pivot or harder pivots;
- stop the finite-field forward elimination immediately when the target itself
  becomes a pivot.

This answers the narrower first question, "does degree 4 contain a reduction
pivot for the target?", without completing all lower-rank reductions.

Commits:

```text
1d936e5027f9f3b4c4057e459bcd07c9cb7302b6
  Add target-rank and early-stop finite-field Laporta

96f29563b4c279e3945a35a7cfbf5b857d5fc872
  Use target-rank pivot search in native IBP probe
```

After pulling, rerun degree 4 and inspect:

```text
[native-ibp] probe 1: connected equations=27300
[native-ibp] probe 1: rank-floor equations=...
[native-ibp] probe 1: pivot search over F_2147483647...
```

If the rank-floor count drops substantially, this should be much cheaper than
the previous full 27300-row elimination.  If the target pivot is still absent,
degree 4 remains inconclusive.  If a target pivot is found, a second stage is
still required to determine whether its RHS reduces entirely to the protected
refined basis.


### 2026-10-10 rank-floor row pruning also did not reduce degree-4 system

The next degree-4 diagnostic reported:

```text
connected equations=27300
rank-floor equations=27300
```

Therefore every row contains at least one integral whose Laporta rank is at or
above the sector-199 target.  Row-level rank pruning cannot reduce the system.

The pivot-existence diagnostic was therefore tightened at the column level.
For the narrow question "does the target acquire a pivot?", columns strictly
below the target rank cannot affect elimination of the target or any harder
column.  Those lower-rank columns are now projected out before finite-field
elimination.  Protected refined-candidate columns are retained regardless of
rank.

This projection is used only for target-pivot existence.  It is not used to
reconstruct a final reduction relation, because lower-rank RHS terms would be
needed for that second stage.

Commits:

```text
1c75cd7787b3023f702365d24ed3915ae8276f2f
  Project finite-field pivot search to target-rank columns

b4c2a2d5ec3e7860fd563026560c95732e3cf8cd
  Use target-rank column projection in native IBP probe
```

After pulling and rerunning degree 4, inspect:

```text
[native-ibp] probe 1: rank projection columns=<after>/<before> nnz=<after>/<before>
```

A large reduction in columns or nonzeros should substantially reduce sparse
finite-field fill-in.  If the projection still leaves nearly the full matrix,
the next step is an on-demand target-column elimination strategy rather than a
full-row forward Laporta pass.


### 2026-10-10 degree-4 target-rank column projection results and target-only pivot search

The degree-4 column projection reduced the finite-field system from:

```text
columns: 32733 -> 16923
nnz:     403916 -> 328568
```

This is approximately a 48% column reduction but only a 19% nonzero reduction.
Therefore substantial sparse fill-in can still remain, and the full forward
Laporta pass may still take hours.

A new target-only sparse row-echelon search was added.  For each row it reduces
only the hardest currently-unprotected column until that column is either
eliminated by an existing pivot or becomes a new pivot.  It does not recursively
substitute lower solved columns unless they later become leading.  The search
stops immediately when the sector-199 target itself becomes a pivot.

This stage deliberately answers only target-pivot existence.  Even if both
finite-field probes find the target pivot, a separate RHS reduction is required
before claiming reduction to the 62 protected refined candidates.

Commits:

```text
b3e47c02b94fd31a699cc50819dfbf13cfbccc02
  Add target-only sparse finite-field pivot search

9744878ca249cfd27fddbeeadc78397ca853bae8
  Use target-only pivot search in native IBP probe
```


### 2026-10-11 degree-4 target-only probe completes; degrees <6 cannot test the new s=6 boundary

The optimized degree-4 target-only finite-field probe completed consistently:

```text
degree: 4
seed count: 1820
symbolic equations: 27300
symbolic integrals: 32733

probe 1:
  rules: 15373
  target_solved: False

probe 2:
  rules: 15373
  target_solved: False

status: target-pivot-not-found-in-finite-neighborhood
audit pass: False
```

The two independent finite-field probes agree exactly.

Important interpretation correction:

The sector-199 refined candidate is

```text
VP05_full[1,1,1,0,0,0,1,1,0,0,0,0]
complexity: r5s0d0
```

and it is already known to survive as a master in the full/common
`r8s5d2` closure.  The unresolved question is only whether extending
`s <= 5` to `s <= 6` introduces a new relation that removes this candidate.

Therefore any genuinely new information capable of changing the master status
must involve the newly admitted `s=6` layer.  In candidate-centered L1 index
distance, the minimum distance from this `s=0` target to that new layer is 6.

Consequences:

- degree 3 and degree 4 probes are useful implementation/rank consistency tests,
  but cannot directly exercise the new `s=6` boundary;
- degree 5 is also not the decisive next test;
- blindly running degree 5 would add substantial cost without reaching the
  actual new boundary;
- the next algorithm should formulate an incremental rank/update problem using
  the already-established `s<=5` system plus only the new `s=6` information,
  rather than recomputing all bounded neighborhoods through degree 6.

Do not launch a full degree-5 native probe as the next step.


### 2026-10-11 switch from full degree-N probes to streaming incremental shell pivots

The degree-4 target-only finite-field probe completed consistently:

```text
probe 1: rules=15373 target_solved=False
probe 2: rules=15373 target_solved=False
status: target-pivot-not-found-in-finite-neighborhood
```

The key interpretation is that the unresolved boundary is specifically
`s<=5 -> s<=6`.  Since the target has `s=0` and is already a master in the
full/common `r8s5d2` closure, degrees below 6 cannot directly exercise the
newly admitted s=6 layer.  Therefore a monolithic degree-5 run is not useful as
the next decisive test.

A streaming incremental native-IBP driver was added instead.

It processes exact bounded seed shells degree-by-degree:

```text
degree 0 shell
degree 1 shell
...
degree 6 shell
```

and, within each shell, processes small seed batches (default 250).  Finite-field
pivot maps are carried forward between batches/degrees rather than recomputing
the whole degree-N system from scratch.

Important properties:

- symbolic IBP equations are generated only for the current batch;
- each batch is projected to target-rank columns;
- two independent finite-field probes maintain separate pivot maps;
- checkpoint state is written after every batch using compressed pickle;
- interrupted runs resume from the saved degree/offset;
- the run stops early if both probes obtain a target pivot;
- even a positive pivot result is still only stage 1; a separate RHS reduction
  is required before claiming reduction to the protected refined basis.

New files:

```text
examples/three_loop_master_basis_candidate_incremental_native_ibp.py
run_three_loop_master_basis_candidate_incremental_native_ibp.bat
```

Supporting change:

```text
d7ba755c2bff44b69a9c1de1c84c60edb4712d07
  Allow incremental finite-field pivot continuation

580a2739a81a336da6f982490050702aa7a12b5f
  Add streaming incremental native IBP pivot audit

7c40dae73ba85053842c751532c6a5b108edec49
  Add incremental native IBP runner
```

Recommended run:

```powershell
.\run_three_loop_master_basis_candidate_incremental_native_ibp.bat VP05_full r8s3d0 199 6 250
```

Do not run the monolithic degree-5 probe next.


### 2026-10-13 incremental native IBP scaling became non-viable; inspect reusable Kira reduction artifacts

The streaming incremental native-IBP run remained numerically stable, but its
wall-clock scaling degraded severely as the accumulated pivot set grew.

Observed degree-5 batch timing for 250 seeds:

```text
earlier: ~30 minutes
later:   ~1.5 hours
current: ~4 hours
```

At the time of reassessment the run was around:

```text
degree 5: batch 2250:2500/4368
```

The increasing cost is consistent with sparse fill-in: each new batch is being
reduced against a progressively larger pivot map, so per-batch work is not
constant.  Since degree 6 contains a much larger exact shell, extrapolating the
current trend gives a weeks-scale run rather than a few days.

The current Python incremental elimination should therefore be stopped.  Its
checkpoint remains available, so no completed work is lost.

Before attempting further native elimination, inspect whether earlier successful
Kira s<=5 projects retained actual reduction artifacts (`kira.db`,
`results/<family>/id2int`, reduction tables), not only master lists.  If such
artifacts exist, they can potentially supply the already-known lower-shell
reduction and avoid rebuilding degree 0..5 pivots in Python.

New diagnostic:

```text
examples/three_loop_kira_reduction_artifact_audit.py
run_three_loop_kira_reduction_artifact_audit.bat
```

Commits:

```text
55592a5d6aabf5a77608b50c0186fcc337fc0c4d
  Add Kira reduction artifact audit

c01adbc18746872414d81c3f681350755acab19d
  Add Kira reduction artifact audit runner
```

Recommended next command after stopping the current incremental run:

```powershell
.\run_three_loop_kira_reduction_artifact_audit.bat VP05_full
```

Do not launch degree 6 or continue the weeks-scale Python pivot accumulation
until this artifact audit is inspected.


### 2026-10-13 correction: bare kira.db is not evidence of reusable reduction rules

The first Kira artifact audit reported 49 projects with
`reusable_reduction_artifacts=True`.  This criterion was too permissive because
it treated the mere existence of `kira.db` as reusable reduction evidence.

That is incorrect for masters-only/initiate-only projects.  For example the
known VP05 candidate-closure runs at r8s5d2/r9s5d2 have:

```text
run_triangular: false
run_back_substitution: false
kira.db: present
id2int: absent
result reduction tables: absent
```

Such a database may contain initialization / sector / master-identification
state without containing reusable triangular reduction rules.

The artifact audit was made conservative:

- explicit `id2int + result reduction table` is accepted as reusable reduction
  evidence;
- a bare `kira.db` is not;
- every `kira.db` is opened read-only through SQLite when possible;
- table names and row counts are reported for schema-level inspection;
- triangular/back-substitution projects without exported result tables are
  flagged for database-content review, not automatically accepted.

Commit:

```text
0ce7a010ca6ff3c551bc4419299cc2869ff03787
  Make Kira reduction artifact audit conservative
```

Priority projects for deep inspection:

```text
kira_vp05_full_masters_candidate_closure_r8s3d0_r8s5d2
kira_vp05_full_masters_candidate_sector_closure_r8s3d0_r9s5d2_sec199
kira_vp05_full_masters_candidate_direct_reducibility_r8s3d0_r8s6d2_sec199
```

Do not assume the earlier "49 reusable projects" result is valid.


### 2026-10-13 Kira DB audit: r8s5d2 contains 34,167 EQUATION rows

Deep artifact inspection changed the picture:

```text
kira_vp05_full_masters_candidate_closure_r8s3d0_r8s5d2
  kira.db size: 2,998,272 bytes
  tables:
    EQUATION: 34167 rows
    INTEGRALORDERING: 1
    VERSION: 1
    WEIGHTBITS: 1
```

By contrast:

```text
r9s5d2 sector-199 local closure:
  EQUATION: 0 rows

r8s6d2 sector-199 direct reducibility:
  no EQUATION table
```

Therefore the best reuse candidate is the monolithic r8s5d2 candidate-closure
database.  Although it has no exported reduction table/id2int and cannot yet be
called a reusable completed reduction, it does retain a substantial equation
store.

A read-only database table inspector was added to reveal the EQUATION schema,
column types, indexes, and sample values.  This is the next decision point:
if Kira's stored equations can be decoded/mapped back to integral IDs, QEDCalc
may reuse the established s<=5 equation system instead of rebuilding degree
0..5 pivots in Python.

New files:

```text
examples/three_loop_kira_db_inspect.py
run_three_loop_kira_db_inspect.bat
```

Commits:

```text
2ee64141568fe45b3e6191e554831b1cbf08c564
  Add read-only Kira DB table inspector

ae1aaa7ab018f584c03bbb7ebe95cfadde1e730a
  Add Kira DB inspector runner
```

Recommended command:

```powershell
.\run_three_loop_kira_db_inspect.bat candidate_closure_r8s3d0_r8s5d2 EQUATION 5
```


### 2026-10-13 Kira r8s5d2 DB contains no nontrivial reusable IBP equations

Detailed inspection of

```text
kira_vp05_full_masters_candidate_closure_r8s3d0_r8s5d2/results/kira.db
```

showed:

```text
EQUATION rows: 34167
AUXILIARY=1: 34167
LENGTH=1: 34167
LENGTH>1: 0
AUXILIARY=0: 0
sector 199: 0
COEFFICIENT: 1 in sampled rows
ID == ARRAYID in sampled rows
```

Therefore these records are not the nontrivial IBP reduction/equation system
needed to seed the native solver.  The Kira-DB reuse route is abandoned for this
project.

The next rescue path exploits a previously measured geometric fact: the new
s=6 shell contains 868,824 integrals globally, but only 924 are at the minimum
L1 distance 6 from the sector-199 target, all in sector 199.  This motivates a
fixed-sector numerator-simplex probe.

The probe keeps all positive powers equal to the target and varies only the
seven zero-power indices with total numerator degree s=0..6.  This reaches the
new s=6 boundary directly without the much larger bounded degree domain that
also varies positive powers/dots.

For seven numerator slots, the complete simplex through s=6 has only:

```text
sum_{s=0}^6 C(s+6,6) = C(13,7) = 1716 seeds
```

The s=6 shell itself has:

```text
C(12,6) = 924 seeds
```

This is a diagnostic, not a proof of stability: failure to find a target pivot
is inconclusive because d>0 / positive-power variations are omitted.  A target
pivot found consistently in both finite fields is useful evidence and would
trigger the RHS-reduction stage.

New files:

```text
examples/three_loop_master_basis_candidate_sector199_numerator_probe.py
run_three_loop_master_basis_candidate_sector_numerator_probe.bat
```

Commits:

```text
4c366397e70fb2b23d33581b6199934c642ef631
  Add fixed-sector numerator simplex IBP probe

408881c49c94700e825cf41da9e9ba3a23f5d8b6
  Add fixed-sector numerator probe runner
```

Recommended run:

```powershell
.\run_three_loop_master_basis_candidate_sector_numerator_probe.bat VP05_full r8s3d0 199 6
```


### 2026-10-13 fixed-sector native probe also develops catastrophic fill-in; switch to restricted FireFly

The fixed-sector numerator-simplex native probe initially progressed in minutes
per row, but by:

```text
[sector-numerator] probe 1: rows=7000/25740 pivots=6999
```

the cost had degraded to roughly 30 minutes per row.

This confirms that the dominant problem is not only seed-domain size; the
Python sparse elimination itself develops severe fill-in as the pivot set grows.
Continuing the remaining ~18,700 rows is not practical.

The native probe should be stopped.

A new restricted Kira/FireFly rescue path was added.  It is deliberately much
smaller than the earlier full r8s6d2 direct-reducibility attempt:

```text
family: VP05_full
sector: 199
target: VP05_full[1,1,1,0,0,0,1,1,0,0,0,0]
r: 5
s: 6
d: 0
mandatory targets: 1
top-level sectors: [199]
solver: FireFly
```

Rationale:

- r=5 is the target's positive-line count;
- d=0 forbids dotted positive propagators;
- s=6 reaches exactly the unresolved numerator boundary;
- only the target itself is selected as mandatory;
- known proper-subsector refined candidates are supplied as preferred masters;
- FireFly performs the finite-field reconstruction rather than QEDCalc's
  increasingly expensive Python pivot accumulation.

This does not recreate the 1716 numerator-simplex seeds as an explicit
mandatory list.  Instead Kira is asked to generate the exact restricted
sector-199 r5s6d0 IBP problem while only the target is mandatory.  This keeps
the reduction objective minimal while still allowing the s=6 relations needed
for the target.

New files:

```text
examples/three_loop_master_basis_candidate_firefly_numerator.py
run_three_loop_master_basis_candidate_firefly_numerator.bat
```

Commits:

```text
cd73e1f0b4dd88366b241af17a611f0dbe9f753e
  Add restricted FireFly numerator rescue probe

aa52bc617000343b14c4160407cb8cb6d8fe3452
  Add restricted FireFly numerator runner
```

Recommended run:

```powershell
.\run_three_loop_master_basis_candidate_firefly_numerator.bat VP05_full r8s3d0 199 6 5
```

If Kira equation generation again stalls before FireFly begins, then the
remaining bottleneck is Kira's IBP generation even in the r5s6d0 restriction,
and a different generator/reduction strategy will be required.


### 2026-10-13 restricted r5s6d0 sector-199 Kira/FireFly probe completes: target retained as master

The restricted rescue run completed successfully:

```text
family: VP05_full
sector: 199
seed: r5s6d0
mandatory targets: 1
target:
  VP05_full[1,1,1,0,0,0,1,1,0,0,0,0]
```

Kira generated the complete restricted equation system over the 12 relevant
sectors:

```text
848812 equations
  463807 zero
  385005 independent

3971838 independent coefficients
```

Master identification then gave:

```text
Number of master integrals: 1
VP05_full[1,1,1,0,0,0,1,1,0,0,0,0] # 199

No integrals to reduce, skipping this family.
```

QEDCalc audit:

```text
master count: 1
target classification:
  master: 1
  reduced: 0
  zero: 0
  unresolved: 0

conclusion:
  retained-master-in-restricted-r5s6d0-probe

audit pass: True
```

Total Kira runtime:

```text
3173.5 s ~= 52.9 min
```

Interpretation:

- This is a strong positive result for the previously unresolved numerator
  boundary: allowing s=6 at fixed sector 199, minimal r=5, and d=0 does NOT
  generate a relation that removes the target.
- FireFly reconstruction itself was not needed, because after Kira initiate /
  master identification the sole mandatory target was already classified as a
  master and Kira reported "No integrals to reduce".
- This does NOT yet prove stability in the full r8s6d2 envelope.  The restricted
  probe deliberately excludes positive-power/dot extensions (r>5 or d>0) and
  broader sector contexts.
- The weeks-scale native-Python pivot accumulation should remain abandoned.
  Kira's native master-identification route is dramatically more efficient for
  this question.

Next decision point: determine the smallest additional Kira boundary tests
needed to bridge the remaining gap from restricted r5s6d0 sector-199 stability
to the full r8s6d2 closure, without returning to the pathological monolithic
r8s6d2 run.


### 2026-10-13 next restricted boundary test: r6s6d1

After the successful r5s6d0 sector-199 restricted probe, the next boundary test
is the one-dot extension:

```text
sector: 199
target: VP05_full[1,1,1,0,0,0,1,1,0,0,0,0]
seed: r6s6d1
```

For this target there are five positive propagator lines. Therefore:

```text
d=0 -> r=5
d=1 -> r=6
d=2 -> r=7
```

The restricted FireFly helper/runner now accepts an explicit `max_d` and sets
`r = positive_line_count + d`.

Commits:

```text
6aa06e45e20c105b8c24d4e64180c4bd2fad4f4f
  Allow dot-degree boundary in restricted FireFly probe

db2e523a6f879bf8ba63f174da27819cf74702bd
  Pass dot degree to restricted FireFly runner
```

Recommended next command:

```powershell
.\run_three_loop_master_basis_candidate_firefly_numerator.bat VP05_full r8s3d0 199 6 1 5
```

If this retains the target as a master, proceed next to r7s6d2 using max_d=2.


### 2026-10-13 restricted r6s6d1 sector-199 probe also retains target as master

The second restricted boundary test completed successfully:

```text
seed: r6s6d1
sector: 199
target:
  VP05_full[1,1,1,0,0,0,1,1,0,0,0,0]
```

Kira statistics:

```text
3,762,370 equations
  2,607,385 zero
  1,154,985 independent

5,494,264 independent coefficients
```

Master identification:

```text
Number of master integrals: 1
VP05_full[1,1,1,0,0,0,1,1,0,0,0,0] # 199

No integrals to reduce, skipping this family.
```

QEDCalc classification:

```text
master: 1
reduced: 0
zero: 0
unresolved: 0
audit pass: True
```

Total runtime:

```text
17926.5 s ~= 4.98 h
```

The printed conclusion string still said
`retained-master-in-restricted-r5s6d0-probe`; this was only a reporting bug.
The actual manifest/test seed was r6s6d1. The helper was corrected to include
the actual dynamic seed tag in the conclusion.

Commit:

```text
52485cf7fd2ffacdad60ac7c621effd9958887de
  Fix restricted FireFly audit conclusion seed label
```

Next restricted boundary:

```text
r7s6d2
```

Recommended command after pulling:

```powershell
.\run_three_loop_master_basis_candidate_firefly_numerator.bat VP05_full r8s3d0 199 6 2 5
```


### 2026-10-13 final fallback policy: no hardware escalation; literature reconstruction/citation instead

Project policy clarification:

Increasing hardware resources (for example moving the calculation to a
64/128-GB machine or external compute system) is NOT an available fallback for
this project.

The final escalation ladder for the remaining three-loop master-basis families
is therefore:

1. ordinary masters-first / initiate-only Kira;
2. one-axis boundary checks and candidate refinement;
3. preferred-master and sector-local decomposition;
4. restricted target-specific Kira problems;
5. Kira/FireFly finite-field reduction on the smallest justified boundary;
6. if direct computation remains infeasible on the available hardware,
   reconstruct the result from published literature where possible.

The literature fallback must be handled conservatively:

- first search for a published integral family / master basis / reduction table
  that can be mapped to the QEDCalc topology;
- document the propagator and sector mapping explicitly;
- independently verify every part that can still be checked locally
  (topology, denominator family, symmetry/equivalence, sector membership,
  master count, normalization conventions, etc.);
- distinguish a literature-derived master basis from a QEDCalc-computed one;
- if only a published final result is available and the diagram-level master
  basis cannot be reconstructed independently, state that limitation rather
  than implying an in-house derivation.

For the final 72-diagram documentation, any such exceptional case must be
labelled explicitly, for example:

```text
Computation status: literature-derived / independently mapped
Reason: direct IBP master-basis computation exceeded the available local
hardware resources.
Source: <paper / ancillary file / database>
Verification performed: <topology/family/sector/symmetry checks>
Remaining limitation: <what could not be independently recomputed>
```

The goal remains to produce a reproducible 72-diagram master-integral record.
Literature citation is the last resort only after the computational reduction
strategies above have been exhausted.


### 2026-10-14 restricted r7s6d2 sector-199 probe completes: target still retained as master

The final restricted sector-199 boundary probe completed successfully:

```text
seed: r7s6d2
sector: 199
target:
  VP05_full[1,1,1,0,0,0,1,1,0,0,0,0]
```

Kira statistics:

```text
10,367,327 equations
  7,779,231 zero
  2,588,096 independent

6,012,213 independent coefficients
```

Master identification:

```text
Number of master integrals: 1
VP05_full[1,1,1,0,0,0,1,1,0,0,0,0] # 199

No integrals to reduce, skipping this family.
```

QEDCalc classification:

```text
master: 1
reduced: 0
zero: 0
unresolved: 0
conclusion: retained-master-in-restricted-r7s6d2-probe
audit pass: True
```

Total runtime:

```text
40553.4 s ~= 11.26 h
```

Observed resources:

```text
WSL memory: at configured 30 GB ceiling
swap peak/use: approximately 130 GB
```

Combined restricted sector-199 evidence is now:

```text
r5s6d0 -> retained master
r6s6d1 -> retained master
r7s6d2 -> retained master
```

Interpretation:

- For the sector-199 target, the complete restricted path through the required
  s=6 and d<=2 boundary retains the target as a master.
- Because sector 199 has five positive propagators, d=2 corresponds to r=7;
  there is no need to push this exact sector to r=8 merely to satisfy the
  global r8 envelope.
- This is strong sector-local evidence for stability of the problematic
  candidate under the unresolved s/d boundary.
- It is still not, by itself, a proof of the entire VP05_full r8s6d2 global
  closure because other candidate sectors / cross-sector contexts remain.
- Resource scaling is now severe (30 GB RAM ceiling, ~130 GB swap). Do not widen
  this particular sector-199 restricted problem further.

Next VP05 decision:
1. treat sector 199 as locally closed for the r8s6d2 boundary;
2. apply the same minimal restricted-boundary logic only to remaining unresolved
   candidate sectors rather than rerunning the monolithic r8s6d2 job;
3. separately resolve the r8s5d3 one-axis boundary;
4. only after those sector-local checks are complete, decide whether VP05_final63
   can be registered.


### 2026-10-14 sector-local closure can reuse mathematically equivalent restricted audits

After the successful sector-199 restricted sequence

```text
r5s6d0 -> retained master
r6s6d1 -> retained master
r7s6d2 -> retained master
```

the generic r8s6d2 sector-local closure was updated to recognize a passing
restricted exact-sector audit as equivalent evidence when the requested r
ceiling is redundant under the d ceiling.

For a fixed sector:

```text
r = n_positive_lines + d
```

because each positive propagator contributes one baseline power and every
additional positive power contributes one unit of d.

Therefore the effective r ceiling for an exact-sector Seed(r,s,d) is

```text
effective_r = min(r, n_positive_lines + d)
```

For sector 199, the target has five positive lines.  Thus for requested
r8s6d2:

```text
effective_r = min(8, 5 + 2) = 7
```

so the passing r7s6d2 restricted audit covers the exact-sector r8s6d2 boundary.

Implementation:

- prepare/reuse checks now look for a matching passing restricted FireFly audit;
- print-projects skips such sectors;
- finalize records them as
  `restricted-equivalent-firefly-audit`;
- no manual skip list is used; the equivalence is derived from the target
  sector and Seed(r,s,d).

Commit:

```text
976dab6a89f14e430bd7e337862931ad50d26705
  Reuse equivalent restricted audits in sector closure
```

Recommended resume command:

```powershell
.\run_three_loop_master_basis_candidate_sector_closure.bat VP05_full r8s3d0 r8s6d2
```

Expected behavior: previously completed sectors and sector 199 are skipped;
the next unresolved candidate sector should be sector 201.


### 2026-10-14 restricted r6s6d2 sector-201 probe completes quickly: target retained as master

The next unresolved VP05 sector, 201, was tested with the effective exact-sector
boundary derived from four positive lines and d<=2:

```text
effective seed: r6s6d2
sector: 201
target:
  VP05_full[1,0,0,1,0,0,1,1,0,0,0,0]
preferred proper-subsector masters: 1
```

Kira statistics:

```text
3,692,826 equations
  2,815,099 zero
  877,727 independent

2,054,689 independent coefficients
```

Master identification:

```text
Number of master integrals: 1
VP05_full[1,0,0,1,0,0,1,1,0,0,0,0] # 201

No integrals to reduce, skipping this family.
```

QEDCalc audit:

```text
master: 1
reduced: 0
zero: 0
unresolved: 0
conclusion: retained-master-in-restricted-r6s6d2-probe
audit pass: True
```

Total runtime:

```text
3427.2 s ~= 57.1 min
```

Interpretation:

- sector 201 is now locally closed for the requested r8s6d2 boundary because
  its four positive lines imply effective_r=min(8,4+2)=6;
- the restricted Kira/FireFly route is substantially more efficient here than
  the earlier monolithic/sector-local r8s6d2 approach;
- continue the remaining unresolved VP05 candidate sectors with the same
  effective-boundary logic rather than launching the original full sector-local
  seed whenever possible.


### 2026-10-14 sector 202 exposes multi-target refined-candidate case

The first restricted probe attempt for sector 202 stopped before Kira because the
runner still assumed exactly one refined candidate per sector:

```text
ValueError: sector 202 must contain exactly one refined candidate; found 3
```

This is not a physics/reduction failure.  It is a runner limitation.

The restricted FireFly runner was generalized to support every refined
candidate in the selected exact sector as mandatory targets in one project.

For a fixed exact sector, the effective positive-power envelope is computed from
the sector bit count rather than from one candidate:

```text
n_positive_lines = bit_count(sector)
effective r = n_positive_lines + d
```

The audit now records:

- `targets`
- `target_count`
- aggregate target classification
- success only when every target is classified as master/reduced/zero

The sector-local closure reuse logic was also extended to accept a passing
multi-target restricted audit when all targets remain masters.

Commits:

```text
07e6982d66a39e38116d825dcee1841cb761ebae
  Support multiple refined targets in restricted sector probe

532ac67d0eba7377508c29d5175ff064159182f9
  Reuse multi-target restricted sector audits
```


### 2026-10-15 sector 202 restricted r6s6d2: master identification succeeds, late Kira reduction fails

The multi-target restricted sector-202 probe reached master identification
successfully before Kira exited nonzero during the later reduction phase.

Observed resource pressure:

```text
WSL memory: at 30 GB ceiling
swap: rose to approximately 230 GB
CPU: low single-digit utilization
```

Kira equation-generation/master-identification output:

```text
5,351,958 equations
  4,254,335 zero
  1,097,623 independent

7,237,092 independent coefficients

Number of master integrals: 4
VP05_full[0,0,0,1,0,0,1,1,0,0,0,0]    # 200
VP05_full[0,1,0,1,0,0,1,1,0,0,0,0]    # 202
VP05_full[-2,1,0,1,0,0,1,1,0,0,0,0]   # 202
VP05_full[-1,1,0,1,-1,0,1,1,0,0,0,0]  # 202
```

The three refined sector-202 mandatory targets are all present in the identified
master list.  The fourth master is the proper-subsector sector-200 master.

After this, Kira restarted equation generation for the reduction stage and then
exited with code 15.  Therefore this is treated as a late reduction/resource
failure, not a failure of master identification.

The runner was updated so that when Kira exits nonzero after such a late stage,
QEDCalc automatically attempts `--finalize`.  If the already-written master
identification output is sufficient to classify every mandatory target, the
restricted audit is salvaged and the run returns success.

Commit:

```text
51883752da08e5ca3cfddbbd2ded632fbe231839
  Salvage restricted audits after late Kira failure
```

For the current already-computed sector-202 project, do NOT rerun the expensive
Kira job.  Pull the update and invoke the Python finalize step directly against
the existing project context.


### 2026-10-15 sector 202 finalize correction: two refined targets unresolved; force preferred refined basis

The direct finalize of the existing sector-202 restricted project produced:

```text
targets: 3
  VP05_full[0,1,0,1,-1,-1,1,1,0,0,0,0]
  VP05_full[0,1,0,1,-2,0,1,1,0,0,0,0]
  VP05_full[0,1,0,1,0,0,1,1,0,0,0,0]

master count: 4
target classification:
  master: 1
  reduced: 0
  zero: 0
  unresolved: 2

audit pass: False
```

Therefore the earlier interpretation that all three refined candidates were
present in Kira's master list was incorrect.  Kira had selected a different
sector-202 master basis:

```text
VP05_full[0,1,0,1,0,0,1,1,0,0,0,0]
VP05_full[-2,1,0,1,0,0,1,1,0,0,0,0]
VP05_full[-1,1,0,1,-1,0,1,1,0,0,0,0]
```

plus one proper-subsector sector-200 master.

This indicates a basis rotation rather than an established loss of master
dimension.  However, because the later reduction failed under extreme swap
pressure, the two original refined candidates remain unclassified and the
sector-202 audit must NOT be marked passing yet.

The restricted runner is now changed so that every exact-sector refined target
is supplied both as a mandatory target and as a preferred master.  Known proper
subsector refined candidates are also included.  This asks Kira to retain the
original refined basis directly instead of choosing an arbitrary equivalent
basis and then requiring an expensive reduction to map back to it.

Commits:

```text
2ece1d0827b9feea50318cd3d2d2313c96e56345
  Prefer refined targets in multi-target restricted probes

68f24a8035cd9dff575ef0495d9e8114f6dc0b18
  Fix restricted probe preferred-master context
```

Next action: rerun the same sector-202 restricted command after git pull.  The
existing project directory and Kira database are intentionally not deleted by
the runner's runtime cleanup, so reusable equation-state may remain available,
but no speedup is assumed.


### 2026-10-15 sector 202 preferred-basis retry: switch multi-target probe to initiate-only masters mode

A retry with the refined sector-202 targets also supplied as preferred masters
exited before producing any usable master list:

```text
ValueError: VP05_full: no masters.final, initiate-only master list, or verified
no-reduction master set found
ERROR: Kira exited with code 1 and the partial result could not be finalized.
```

The multi-target restricted probe is therefore changed again.

For one-target sectors the original FireFly route remains useful because Kira
often identifies the target as a master and reports "No integrals to reduce".

For multi-target sectors, however, the current scientific question is only
whether the refined targets can themselves be selected as a master basis at the
restricted exact-sector boundary.  A downstream reduction is unnecessary and
can cause extreme swap growth merely to convert between equivalent master
bases.

New policy:

```text
1 target   -> solver=firefly
>1 targets -> solver=masters (initiate-only)
```

The multi-target project still uses:

- the exact-sector restricted r/s/d boundary;
- all refined exact-sector targets as mandatory targets;
- the same targets as preferred masters;
- any known proper-subsector refined masters as additional preferred masters.

The expected output is now only Kira master identification; no FireFly,
triangular solve, or back substitution is requested.

Commit:

```text
a2e265b0de61872982f3b545982d0e982e635948
  Use initiate-only masters mode for multi-target restricted probes
```


### 2026-10-15 sector 202 code-1 retry: isolate preferred-master project from stale FireFly DB

The multi-target initiate-only retry still exited with code 1 before producing a
master list.  Review of the runner showed that the project directory was still
the same one previously used for the FireFly run:

```text
kira_vp05_full_firefly_numerator_r8s3d0_r6s6d2_sec202
```

Runtime cleanup intentionally preserves `kira.db`.  That behavior is correct
for resuming the same Kira job, but not when changing the job semantics from:

```text
solver=firefly
no exact-sector preferred refined basis
```

to:

```text
solver=masters (initiate-only)
exact-sector refined targets also supplied as preferred masters
```

To avoid any stale-database/configuration interaction, multi-target
preferred-master probes now use a separate project namespace:

```text
kira_<family>_preferred_masters_<baseline>_<seed>_sec<sector>
```

while single-target FireFly probes retain the existing
`firefly_numerator` project namespace.

For VP05 sector 202 the new project is therefore:

```text
kira_vp05_full_preferred_masters_r8s3d0_r6s6d2_sec202
```

This guarantees a fresh Kira database for the initiate-only preferred-basis
test without deleting or modifying the valuable previous FireFly project.

Commit:

```text
aa3488558270b4484746fa55074afd4b11af6330
  Isolate multi-target preferred-master Kira projects
```


### 2026-10-15 sector 202 reinterpretation: initiate-stage master list is sufficient to classify missing mandatory targets

Kira's documented master-identification semantics resolve the apparent
sector-202 ambiguity without another expensive reduction.

Kira reports the master list after mandatory equation selection and before
forward elimination.  A selected mandatory integral appears in that master list
if no reduction formula was found for it.  Therefore, for the exact mandatory
target set used by the sector-202 restricted project:

- mandatory target present in the reported master list -> retained master;
- mandatory target absent from the reported master list -> Kira found a
  reduction relation during initiate/equation selection.

This means the earlier QEDCalc classification

```text
master=1, unresolved=2
```

was too conservative because it required exported reduction tables for the two
non-master mandatory targets even though Kira had already completed the
master-selection stage.

The restricted audit code now upgrades such unresolved mandatory targets to
`reduced` when a valid non-empty Kira master list exists for the exact
mandatory set.

Because the later preferred-master experiments did not produce usable master
lists, finalize also falls back to the earlier restricted FireFly project that
did successfully reach Kira master identification.

Expected sector-202 audit after the patch:

```text
master: 1
reduced: 2
zero: 0
unresolved: 0
audit pass: True
```

This does not claim that the original three refined candidates are all retained
as the same basis.  It says instead that, at restricted r6s6d2, one remains a
master and two have initiate-stage reduction relations into the newly identified
master basis.  The sector-202 basis therefore needs to be updated/refined rather
than forcing the old three-candidate basis.

Commits:

```text
092d838927e9f4f693e2dd97986db88ce4f24f03
  Classify missing mandatory targets from Kira initiate master lists

c26614b8df1930c86dba9b5639763e6c04220afd
  Salvage legacy restricted master list for multi-target audits
```


### 2026-10-15 VP05 sector 202 recovered master-identification evidence

The original sector-202 Kira runtime files were removed by later retries, but
the previously observed master-identification result is preserved in the
restricted probe code as a narrowly-scoped recovery record for
VP05_full / r8s3d0 / r6s6d2 / sector 202.

The recovery is used only when the current mandatory target set exactly matches
the recorded target set and is labeled
`recovered-kira-terminal-master-identification`.

Commit: `d15ca9779db0e718abaaeb682ba36512b7d3048e`.


### 2026-10-15 VP05 sector 202 restricted audit passes with basis refinement

Recovered/finalized restricted audit:

```text
family: VP05_full
baseline seed: r8s3d0
restricted seed: r6s6d2
sector: 202
targets: 3
master count: 4
target classification:
  master: 1
  reduced: 2
  zero: 0
  unresolved: 0
conclusion: all-targets-classified-in-restricted-r6s6d2-probe
audit pass: True
```

Interpretation:

- the original three refined sector-202 candidates are not all retained as the
  preferred basis at the stronger exact-sector boundary;
- one candidate remains a master;
- two candidates have Kira initiate-stage reduction relations;
- the sector-202 master space remains nontrivial, but the refined candidate
  basis must be updated using the newly identified sector-202 masters rather
  than treating the old three targets as stable masters;
- no further expensive sector-202 Kira rerun is required for the r8s6d2
  exact-sector check.

The preserved Kira master-identification output for this probe contained one
proper-subsector master (sector 200) and three sector-202 masters.  The next
step is therefore basis refinement/union update, not another reduction attempt.


### 2026-10-15 VP05 sector 202: audited candidate representative replacement helper

Added `examples/three_loop_master_basis_candidate_sector_refine.py` and
`run_three_loop_master_basis_candidate_sector_refine.bat` to carry the
restricted Kira master-identification evidence into the *candidate master
list*. The helper is strictly guarded:

- requires the locally persisted, passing restricted audit for the exact
  family / baseline / r6s6d2 / sector 202;
- matches the old exact-sector candidate set to the recovered terminal evidence;
- uses only the three same-sector masters, explicitly excluding the sector-200
  proper-subsector master;
- refuses duplicate representatives, any candidate-cardinality change, or
  a change to the set of candidate sectors;
- creates a proposed candidate file and JSON provenance report;
- `--apply` additionally saves a one-time backup and updates the original
  candidate file referenced by the passing refinement audit.

The expected local outcome is sector 202: three candidates -> three
masters, leaving 63 global candidates if the preceding 63-candidate file
has not changed. **This is a representative replacement, not a proof of
global 63-dimensional IBP closure or numerical coefficients.**

Windows commands (in the repository root):

```powershell
git pull
.\run_three_loop_master_basis_candidate_sector_refine.bat
.\run_three_loop_master_basis_candidate_sector_refine.bat --apply
```

The first call performs a guarded dry-run and outputs the proposed master
list and report. The second makes the audited update; do not run it until
the dry-run output is checked. No Kira computation is launched here.

Once this has been applied and the 63-candidate sectors reviewed, continue
sector 203 with the restricted exact-sector boundary: popcount(203)=5,
effective_r=7, hence r7s6d2, MAX_S=6, MAX_D=2, ORDERING=5.

```powershell
.\run_three_loop_master_basis_candidate_firefly_numerator.bat VP05_full r8s3d0 203 6 2 5
```

The missing r8s5d3 direction is a separate pending boundary. No VP05
final master basis is promoted until the necessary closure evidence passes.


### 2026-10-15 sector 203 immediate code-1: isolated bounded A/B diagnostic

After sector-202 basis replacement (63 -> 63 candidates), the sector-203
r7s6d2 multi-target initiate-only project exited code 1 at early equation
selection (sector 73, 1/14). There was no observed memory/swap spike. Kira 3.1
itself starts normally. Its exact failure cause is still unknown.

Added:
- `examples/three_loop_sector203_diagnostic.py`
- `run_three_loop_sector203_diagnostic.bat`

The diagnostic clones only source YAML and target text files into two *new*
project directories. It does not copy `kira.db`, results, or other old runtime
state. It executes identical seed and ordering with/without preferred masters,
each under a strict 90-second `timeout`, retaining independent
`diagnostic.log` files. Exit 124 denotes a timeout and must not be interpreted
as successful master identification or as a Kira failure.

Run once:
```powershell
git pull
.\run_three_loop_sector203_diagnostic.bat
```

Inspect the last 40 lines of each diagnostic log and the printed exit codes.
The original sector-203 project and the successful sector-202 candidate
replacement remain unchanged. No full retry until root cause is established.


### 2026-10-15 VP05 sector 203 single-target staged diagnostics

The preferred-free four-target r7s6d2 diagnostic reached sector 73 (1/14)
and timed out after 90 seconds (exit 124), rather than giving an immediate
Kira failure. This does not establish that preferred masters cause an error
or that the four-target seed is infeasible.

Added `examples/three_loop_sector203_single_target.py` and
`run_three_loop_sector203_single_target.bat`. Each invocation clones only
the configuration and selects one of four original sector-203 mandatory targets
in a fresh, uniquely named Kira project, without preferred masters. The
target is checked against its r/s/d envelope. Valid stages are r5s6d0,
r6s6d1, r7s6d2. Each run has a 90-second limit and records Kira's exit
status separately. Existing master lists, candidate files, and databases
are not modified.

First lightweight diagnostic:
```powershell
git pull
.\run_three_loop_sector203_single_target.bat 1 r5s6d0
```

Timeout 124 is inconclusive, not a failure of IBP reducibility. A single
target result cannot prove four-target combined closure or the final r7s6d2
boundary; later stages and joint consistency must still be verified.


### 2026-10-15 VP05 sector 203 monitored Kira resource guard

Four isolated r5s6d0 one-target 90-second probes all reached sector 200
(2/14), then returned exit 124 (timeout), with no master list established.
Historical Kira computations experienced rapid swap growth after the last
`Generate equations` line; 240 GiB is the maximum possible user swap
provision, currently 230 GiB. Avoid assuming that sector-progress log lines
measure solver completion.

Added a monitored WSL Python 3 runner (standard library only):
`scripts/sector203_monitored_kira.py`, an isolated project preparer
`examples/three_loop_sector203_monitored_prepare.py`, and Windows launcher
`run_three_loop_sector203_monitored.bat`.

Initial controls: 30-minute wall clock maximum, 5-second metrics interval,
swap warning at 210 GiB and automatic TERM/KILL stop at 220 GiB. Reports
`monitored_metrics.jsonl`, `monitored_kira.log`, and
`monitored_exit.json`; records observed RAM, swap, Kira main process
CPU%, and last Kira sector line. CPU% of main PID is not system-wide
28-thread utilization. The guard acts at sampling intervals, so thresholds
are not an absolute hard cgroup memory limit. Kira exits due to timeout
or swap guard are not scientific reduction failures.

The preparer copies only YAML and one-target mandatory text from the
previously prepared diagnostic into a new monitored project, without
copying the old Kira database or modifying sector-202 results.

First monitored local run:
```powershell
git pull
.\run_three_loop_sector203_monitored.bat 1 r5s6d0
```

No master basis promotion is implied by a completed diagnostic alone.

### 2026-10-15 Sector 203 monitored runner console adjustment

The user already has a separate WSL RAM/swap/CPU dashboard; repeating sampled JSON
on the console is distracting. Updated `scripts/sector203_monitored_kira.py`
to keep `monitored_metrics.jsonl` on disk but print Kira log lines as they
arrive (including `Generate equations ... sector N (k of total)`). Swap warning,
automatic stop at 220 GiB, and 1800-second wall-time guard remain unchanged.
The revised code applies to newly prepared monitored projects; an already
running project has its own earlier copied runner and is not modified.

### 2026-10-15 sector203 monitor wall-time setting revised

The monitored t1 r5s6d0 run reached sector 202 (11/14) and was terminated by the prior 1800-second timer (`time_stop`, code -15). Observed peak swap ~36.86 GiB and RAM ~29.35 GiB, much lower than swap stop (220 GiB). This timeout was artificial, not a Kira failure or evidence of stalled solve. The monitored Python runner now defaults to `--max-seconds 0` (no time limit); the BAT explicitly passes 0. Swap guard at 220 GiB, warning 210 GiB, 5-second samples, log streaming, and unique per-run output directories remain. A specific positive `--max-seconds` can still be supplied manually for bounded experiments. Do not claim that a terminated run can resume from its final log line: the next invocation creates a fresh Kira project.

### 2026-10-16 VP05 sector 203 one-target r5s6d0 monitored completion

User reports first single-target `r5s6d0` monitored run completed normally: Kira `Total time (31658.1 s)`, monitor elapsed `31683.9 s`, `reason=kira_exit`, `kira_returncode=0`, and final displayed sector `203 (14 of 14)`. This establishes completion of this restricted one-target initiate-only job, **not** the identity or number of masters, nor full four-target r7s6d2 closure. Inspect Kira `results/masters.final`, `kira.log`, and the run manifest before selecting the next expensive calculation. No master basis has been promoted by this report.

### 2026-10-16 sector 203 read-only comparison result

Read-only `examples.three_loop_sector203_result_audit` against completed t1 `r5s6d0` Kira log and 63 refined candidates: 10 Kira masters overall, sector composition 73:1, 201:1, 202:3, 203:5. Existing refined candidate file has 4 sector-203 representatives. Two exact matches: `VP05_full[1,1,0,1,-1,0,1,1,0,0,0,0]`, `VP05_full[1,1,0,1,0,0,1,1,0,0,0,0]`. Three sector-203 masters are only in the Kira result and two candidates only in original list. These arise under different target/seed scopes: they cannot be equated or used to replace the 4-candidate set without a common-system rank/target audit at adequate boundary. No candidate modifications. Preserve completed ~8.8-hour Kira workspace for database reuse investigation.

### 2026-10-16 saved Kira SYSTEM read-only inventory

User confirmed fourteen `tmp/VP05_full/SYSTEM_VP05_full_<sector>.gz` files contain `Eq` records with encoded integral IDs, coefficients and sector labels, but the encoding is not yet verified. Added `examples/three_loop_sector203_system_inventory.py` to inventory equation counts, terms, distinct internal IDs, and referenced sector distributions without invoking Kira or changing candidate lists. Do not claim that a compressed SYSTEM dump is the full original 5.2M-coefficient system or that integral IDs can be decoded without documented verification.

### 2026-10-16 sector 203 saved SYSTEM inventory actual results

The user ran the read-only `examples.three_loop_sector203_system_inventory` on the completed `r5s6d0` target-1 project. Fourteen `SYSTEM_*.gz` files decoded into exactly **3317 equation records**, **31556 term occurrences**, with **zero parsing errors**, matching the previous Kira log's `Number of selected equations to reduce: 3317 equations`. Sector 203 file: 258 equations, 3124 terms, 551 distinct internal integral IDs. Term sector labels: 203=2366, 202=160, 201=101, 200=2, 195=171, 194=1, 139=245, 75=78. Sector 202 file: 303 equations, 3184 terms, 498 unique internal IDs. These are *selected/regenerated equations*, not the entirety of the ~5.22-million independent coefficients. Numerical IDs are not decoded or mapped to particular candidate integrals yet. Avoid treating this as a complete rank or reducibility proof for the existing four sector-203 candidate integrals, and preserve source project intact.

### 2026-10-16 VP05 sector 203 weight-to-integral mapping audit

Implemented `examples/three_loop_sector203_weight_audit.py` for read-only Kira integral-weight decoding. Uses the public GPL-3.0+ `pyred_weight.py` by BootLoops-ai/kira as an **external explicitly supplied local dependency**, not vendored into the MIT QEDCalc tree. Reads the completed `r5s6d0` sector203 project's `results/kira.db` WEIGHTBITS/INTEGRALORDERING, validates ordering=5 and `config/integralfamilies.yaml` top sector=203, then decodes all `(weight, sector)` terms from the 3317 saved SYSTEM equations. Requires exact sector and encode/decode round-trip for every ID before interpreting four candidate matches. Reports candidate weight and presence in the selected SYSTEM and equations head set, with no assumption that absence implies irreducibility or a final full 4-target r7s6d2 result. No new Kira calculation or candidate modifications.

### 2026-10-16 sector203 external weight codec mismatch investigation

Initial externally supplied codec audit reported 3838 `(weight, sector)` pairs, with **3526 global decoding mismatches**, despite apparently matching four sector-203 candidate encoded weights. These matches must **not** be promoted to reduction claims until sector-ID reconciliation. Adjusted `examples/three_loop_sector203_weight_audit.py` to report mismatch counts and decoded-sector distributions per recorded sector, and to test candidate presence using the exact `(encoded_weight, 203)` pair rather than decoded tuple membership (which could be inconsistent). Mismatches still result in explicit failure. This is a *diagnosis only*; preserve original Kira data and 63 candidate set.

### 2026-10-16 weight decoding sector-rank permutation diagnosis

The user reported 3838 term-weight/sector pairs and 3526 mismatches from the default external pyred weight codec. These errors are systematically sector-dependent: all 312 recorded sector-203 pairs decode to 203, while each other recorded sector decodes uniformly to a different sector (e.g. 67->137, 73->11, 201->75, 202->195). This is consistent with differing sector rank conventions. All four existing sector-203 candidate encoded `(weight,203)` pairs are present in saved SYSTEM; candidates 1 and 3 not in the resulting 10-master list, candidates 2 and 4 are. Candidate 1 is an equation head. Do NOT claim reducibility until algebraic relation verified. Updated `examples/three_loop_sector203_weight_audit.py` to check a unique and injective recorded-sector to default-codec-sector rank mapping for all saved terms, using decode/encode round trips, without altering source files or the 63-master list. This is an *observational reconciliation*, not a proof of the engine's global ranking rule.

### 2026-10-16 sector 203 observed rank remap passes; extract candidate equations

User's rerun of weight audit verified 3838/3838 selected SYSTEM weight-sector pairs with an injective observed sector-remap and 0 remap errors. Default raw decoder still mismatches 3526 proper-subsector pairs; do not mistake this empirical map for full global Kira sector ordering implementation. All four sector-203 candidate weights appear in selected SYSTEM data. Added `examples/three_loop_sector203_equation_extract.py` to read only the saved 3317 `SYSTEM_*.gz` equation records and report, per candidate, equation occurrences, equation-head count, and a limited sample of raw coefficient/weight/sector terms. It performs no reductions and changes no basis.

### 2026-10-16 sector203 four-candidate selected-equation audit

Read-only `three_loop_sector203_equation_extract` scanned 3317 saved SYSTEM equation records. Counts by four existing sector-203 candidates (candidate order from refined 63-list): #1 `VP05_full[1,1,0,1,-1,-1,1,1,0,0,0,0]` appears in 46 equations, and is an equation head once, but is not in the 10-master list; #2 `VP05_full[1,1,0,1,-1,0,1,1,0,0,0,0]` appears in 57 equations, no heads, and is listed as a master; #3 `VP05_full[1,1,0,1,-2,0,1,1,0,0,0,0]` appears in 32 equations, no heads, and is not listed as a master; #4 `VP05_full[1,1,0,1,0,0,1,1,0,0,0,0]` appears in 35 equations, no heads, and is listed as a master. Candidate #1 head equation has coefficients -2 (candidate #1), -1 (candidate #3), (-z+4) (candidate #2), plus other sector-203 and lower-sector terms. One equation and absence from the master list are NOT sufficient to prove that #3 is reducible to the current 10 masters. Further targeted algebra/rank audit is needed. r5s6d0 one-target result is not r7s6d2 four-target closure; keep 63 refined candidate basis unchanged.

### 2026-10-16 saved SYSTEM finite-field rank diagnostic

Added `examples/three_loop_sector203_ffrank_audit.py`, a read-only sparse modular Gaussian-elimination diagnostic over the 3317 *selected* SYSTEM equations at `r5s6d0`, evaluating `z=17` modulo prime 1000003. The audit adds the five recorded sector-203 masters to the equation row span, then tests each of the four candidate unit vectors for rank increases. It deliberately keeps all lower sectors as formal variables because the sector-rank codec mapping for lower sectors remains unresolved. Rank tests characterize only the span of **saved selected equations plus the five sector203 master vectors** at this finite-field point; they do NOT prove full IBP reduction, exact symbolic basis identity, four-target rank, or `r7s6d2` closure. Configurable sparse fill cap aborts safely; no Kira run or candidate-file mutation. Run with `.\\.venv\\Scripts\\python.exe -m examples.three_loop_sector203_ffrank_audit --codec-file output\\tools\\pyred_weight.py`. Do not start the next 8h Kira job before reviewing this read-only audit.

### 2026-10-16 sector203 saved selected-system finite-field rank results

User ran `three_loop_sector203_ffrank_audit` at prime 1000003, z=17, d=7. All 3317 selected equations were linearly independent in the sampled field (rank 3317). All five sector203 Kira masters individually raised rank by one relative to the selected-equation row space. After adjoining those five, existing candidates #2 and #4 did not raise rank (both are those masters), while candidate #1 `VP05_full[1,1,0,1,-1,-1,1,1,0,0,0,0]` and #3 `VP05_full[1,1,0,1,-2,0,1,1,0,0,0,0]` each raised rank when tested separately. This means the saved selected equations plus sector203 master vectors do not suffice to establish their reduction at this evaluation point. It does *not* prove candidate #1/#3 are true IBP masters or that the existing 63-candidate basis is invalid: the saved system is a subset selected for only mandatory target #1, and no complete target-specific reduction or r7s6d2 closure was computed. Keep candidate list unchanged. Avoid redundant target2/target4 reruns; next investigate source project's selected equations and rank deficiency/possible Kira target extension with DB reuse before expensive reruns.

### 2026-10-16 All-ten-master selected-system finite-field audit

After the 3317 selected SYSTEM equations had rank 3317 at prime 1000003, z=17, d=7, the earlier sparse-rank script found candidates #1/#3 outside the row span plus five sector203 masters. Added `examples/three_loop_sector203_ffrank_all_masters.py` to use the **observed one-to-one sector rank permutation** in Kira's SYSTEM records to encode all 10 recorded master names, including proper subsectors 73, 201, 202. The new read-only rank audit explicitly adds all ten master unit vectors and then tests all four candidate vectors, reporting rank increments and which masters actually appear in the saved SYSTEM. Does not require every master to appear in selected equations. Results apply only to saved one-target r5s6d0 equations at a single finite-field point; they cannot establish the global r7s6d2 closure or replace the 63 refined candidate file. Command: `python -m examples.three_loop_sector203_ffrank_all_masters --codec-file output/tools/pyred_weight.py`.

### 2026-10-16 sector203 all-10-master finite-field result

User's read-only run of `three_loop_sector203_ffrank_all_masters` at p=1000003, z=17, d=7: the 3317 saved selected SYSTEM equations had rank 3317. Adjoining all 10 Kira-reported master unit vectors (sector composition 73:1, 201:1, 202:3, 203:5) increased rank on every insertion. **All four existing sector203 candidate unit vectors subsequently had rank increment false**, i.e. are in the linear span of those 3317 sampled equations plus all ten masters. This resolves the *sampled selected-system span* failure observed with only five sector203 masters: lower-sector masters are necessary. It does NOT establish symbolic reduction, the original full four-target system, r7s6d2 closure, or independence of the four existing sector203 candidates as a basis. Preserve 63 candidate set and completed Kira directory; next objective is extracting explicit target-to-master modular relations and checking additional evaluation points.

### 2026-10-16 sector203 candidate quotient-rank multi-point follow-up

Added read-only `examples/three_loop_sector203_candidate_quotient_rank.py`. Computes rank modulo the selected 3317 saved SYSTEM equations for four sector203 candidate vectors, then tests the five sector203 Kira master vectors after adjoining the candidates at three finite-field points `(z,d)=(17,7),(29,11),(37,13)` with prime 1000003. Also checks each candidate's span after adjoining five sector203 masters. This tests *quotient vector-space ranks*; it does not reconstruct an explicit reduction coefficient matrix, include all lower-sector masters in that comparison, or prove exact symbolic or r7s6d2 closure. Existing source Kira directory and candidate list remain unchanged. Command: `.\\.venv\\Scripts\\python.exe -m examples.three_loop_sector203_candidate_quotient_rank --codec-file output\\tools\\pyred_weight.py`.

### 2026-10-16 three-point candidate-rank audit and lower-sector quotient correction

User's `three_loop_sector203_candidate_quotient_rank.py` produced identical outcomes at (z,d)=(17,7),(29,11),(37,13), p=1000003: saved equation rank 3317; all 4 candidate vectors independent modulo saved equations; adding 5 sector203 masters increases rank by 3; the five upper-master increments after candidates are [false,true,false,true,true]; candidates #1/#3 are not in the span of saved equations plus only the five upper masters. This MUST NOT be interpreted as a seven-dimensional sector203 master space: five lower-sector master directions were omitted. Earlier audit with all ten masters had all four candidates in span. Implemented `examples/three_loop_sector203_lower_quotient_rank.py` to first quotient by saved equations AND the five lower-sector masters (73/201/202), then compare the four candidate and five upper-master unit vectors at the same three evaluation points using validated empirical sector-rank remap. Read-only, no Kira run, no candidate-file update; does not prove symbolic or r7s6d2 closure.

### 2026-10-16 VP05_full sector203 lower-sector-quotiented rank result

User executed `examples/three_loop_sector203_lower_quotient_rank.py` at three finite-field samples (z,d)=(17,7),(29,11),(37,13), prime 1000003. All results identical: saved equation rank 3317; five lower-sector master unit vectors each raise rank; four existing sector203 candidate unit vectors each raise rank after adjoining lower masters (candidate rank 4); five Kira sector203 masters have rank 5 in that quotient. Adding Kira upper masters to four candidates yields increments `[false,true,false,false,false]`, hence adding **`VP05_full[1,1,-1,1,0,0,1,1,0,0,0,0]`** (second upper-sector Kira master in listed insertion order) raises rank by one and completes a rank-5 span in these sampled selected equations. All four candidates lie in the combined 10-master span. This identifies a *provisional fifth candidate* for sector203, not a proven global master basis or r7s6d2 closure. Do not modify the existing 63-candidate master list until further validation across required envelope/sectors; keep long-running Kira jobs paused.

### 2026-10-16 provisional 64-candidate VP05 sector203 validation

Created `examples/three_loop_sector203_provisional64.py`, a safety-gated tool that loads the existing refined 63-candidate file (checks count and duplicates), and checks provisional `VP05_full[1,1,-1,1,0,0,1,1,0,0,0,0]` is new. Using saved 3317 target-one `r5s6d0` Kira SYSTEM equations, measured Kira weight-sector map, all five lower-sector masters, and the candidate four plus proposed fifth, it computes ranks at finite-field points `(z,d)=(17,7),(29,11),(37,13)` over 1000003. Only when the five candidate rank increments all succeed and adding five sector203 Kira masters yields no additional direction at all three points does it create **a separate** 64-entry file at `output/three_loop_integral_family_audit/vp05_full_masters_r8s3d0_union_r8s5d2_provisional64_masters.txt`. Existing 63-list and completed Kira project are unchanged. This remains PROVISIONAL: sampled selected equations do not prove symbolic closure or r7s6d2 envelope stability. Tool deliberately refuses overwrite if provisional output already exists.

### 2026-10-16 Provisional 64-candidate creation succeeded

User ran `examples/three_loop_sector203_provisional64.py` successfully: `status=PASS_PROVISIONAL_ONLY`; output was created separately at `output/three_loop_integral_family_audit/vp05_full_masters_r8s3d0_union_r8s5d2_provisional64_masters.txt` (64 candidates). All three points `(z,d)=(17,7),(29,11),(37,13)` over p=1000003 gave `candidate_rank=5`, candidate insert increments `[true,true,true,true,true]`, and adding the five sector203 Kira masters yielded no additional direction `[false,false,false,false,false]`. The provisional extra integral is `VP05_full[1,1,-1,1,0,0,1,1,0,0,0,0]`. This validates equality of sampled sector203 quotient spans in the selected `r5s6d0` SYSTEM only; **does not certify `r7s6d2` closure, other required sectors, or symbolic identities**. The refined 63-master source file must remain unchanged. Next decide minimal scoped r7s6d2 checks using saved evidence; do not restart global `resume 1` just because this local test passed.

### 2026-10-16 Provisional64 r7s6d2 sector203 isolated preflight

Added `examples/three_loop_sector203_provisional64_r7_prepare.py` to prepare, but **not execute**, a new isolated `VP05_full` sector203 r7s6d2 initiate-only Kira project for the five provisional candidate integrals and matching proper-subsector preferred masters. This checks original 63 unique items, provisional 64 unique items, and exact expected appended fifth candidate. The fresh project is named `output/kira_vp05_full_provisional64_sec203_r7s6d2_provisional64_dryprep`, refuses overwrite, and writes a JSON preflight manifest. No Kira run has yet been authorized; estimated potential memory/runtime at r7s6d2 remains unknown and may be very large. Do NOT restart `resume 1`. Before running Kira, inspect jobs.yaml and resource implications; keep the earlier successful 8h48m result intact.

### 2026-10-16 VP05 sector203 provisional64 staged r6s6d1 guarded probe

Created `examples/three_loop_sector203_provisional64_stage_prepare.py`: fresh, isolated `r6s6d1` / `r7s6d2` initiate-only sector203 preparation; validates intact 63 + appended provisional 64 candidate files; 5 mandatory sector203 targets, 10 preferred exact/subsector candidates; copies monitoring runner to fresh project; checks job bounds; refuses existing project path. PREPARATION DOES NOT START KIRA. Added explicitly invoked `run_three_loop_sector203_provisional64_monitored.bat <project_path>` with 7200s wall-clock cap, 150GiB swap warning and 170GiB swap stop; refuses existing monitor outputs. Initial instruction: run only the preparation command for r6s6d1 and inspect manifest first; do NOT restart resume 1 or immediately run r7s6d2. Prior r5s6d0 one-target calculation took 8h48m; 2h cap may terminate inconclusively. These are experimental, not final master basis certification.

### 2026-10-16 r6s6d1 provisional64 sector203 trial stopped at sector139

User halted monitored five-target `VP05_full` sector203 `r6s6d1` trial (`output/kira_vp05_full_provisional64_sec203_r6s6d1_20261016_090739_388470`) after prolonged `Generate equations ... sector 139 (13 of 14)` with RAM ~29 GB, swap ~120 GB, CPU ~3-7%, and SSD 100% active. `pgrep` thereafter found no Kira or monitor processes. Inspection of the complete stopped project showed no `tmp/VP05_full/SYSTEM_*.gz` data; largest file was `monitored_metrics.jsonl` ~0.56MB, sector mappings ~0.07MB, `results/kira.db` ~0.03MB, and short logs. Thus no reusable serialized selected IBP equations are evident, and master identification was not reached. Treat as *incomplete due to memory/I/O resource pressure*, not a failed candidate basis. Do not repeat the same five-target r6s6d1 run or attempt global resume 1. Preserve original directory. Prioritize designing reduced lower-sector/sector139 targeted computations or source-level performance mitigation based on evidence before running another heavy job.

### 2026-10-16 Offline sector139 seed-pressure diagnostic

Added `examples/three_loop_sector139_seed_pressure_audit.py` to compute *combinatorial integral index counts* (not IBP equation counts) for each of the 14 sectors encountered by the stopped VP05_full sector203 trial, with seed bounds r5s6d0, r6s6d1 and r7s6d2, and to summarize the existing `monitored_metrics.jsonl`. For sector139 (4 positive lines, 8 nonpositive slots, s<=6), the allowed index tuples count is 3003 at r5s6d0, 15015 at r6s6d1, and 45045 at r7s6d2, before symmetries or Kira equation generation; factor 5 and 3 increases respectively. These combinatorial counts alone do not explain Kira's extreme CPU/SSD bottleneck, nor predict equation counts, memory or runtime. The script is read-only and starts no Kira job. User should run its offline summary before any new experiment; maintain 63 original and provisional64 lists intact.

### 2026-10-16 sector139 pressure audit results (user run)

Offline combinatorial counts across the 14 sectors: r5s6d0=56,771, r6s6d1=245,531 (4.33x), r7s6d2=661,661 (11.65x baseline). Exact sector139: 3,003 / 15,015 / 45,045; sector203: 1,716 / 10,296 / 36,036. These count possible index tuples under seed bounds, NOT actual generated IBP equations or runtime. Stopped r6s6d1 five-target trial had 3165 monitoring samples over 15,834.1 seconds (4.40h); peak swap 124.19 GiB, last swap ~120.02GiB, RAM used ~29.14/29.37GiB, last Kira sector139 (13/14). Last-sector sample durations at nominal 5-second monitoring interval: sector202 2018 (~168min), sector195 577 (~48min), sector139 295 (~25min), sector201 81 (~7min). The bottleneck therefore starts notably earlier than sector139: sector202 dominates observed log residence. Monitoring counts are only time spent with a given last-sector label, NOT precise active computation time. Avoid relaunching r6s6d1/r7s6d2 full 14-sector setup. Next work should investigate source-level seed constraints and per-sector workload, preferentially using existing audit and no new multi-hour run.

### 2026-10-16 Kira 3 subsector seed truncation investigation

Kira 3 literature documents `truncate_sp: - {topologies: [VP05_full], l: N}` in the `reduce_sectors` job (next to `reduce` / `select_integrals`), with sub-sector numerator cap `s <= max(1, t-l+1, s_max,sector)`; user-selected sector203 retains its explicit s=6 and inherited proper subsectors may be truncated. See Kira 3 article `Kira 3: Integral reduction with efficient seeding and optimized equation selection` section 3.1.2. Added `examples/three_loop_sector203_truncate_sp_preflight.py` to inspect the stopped r6s6d1 project's jobs.yaml and mandatory five list and create **non-executable** `jobs.truncate_sp_l{2,3,4,5}.preview.yaml` next to it; estimates per-sector index tuple counts at the hypothetical reduced numerator caps. This is a non-destructive, offline planning step with no Kira invocation, no edit to jobs.yaml, and no changes to candidates or previous Kira results. The new feature can yield extra apparent masters if too aggressive and MUST NOT be promoted without a future measured and audited restricted run. Further identify suitable l by weighing sector202/139 growth, then only if worthwhile generate a separate fresh test project.

### 2026-10-16 truncate_sp dry-run output and preview syntax correction

User's offline preflight: at r6s6d1 the 14-sector index proxy falls from 245,531 untruncated to 16,181 (l=2), 11,741 (l=3), 10,841 (l=4/5); sector202 and sector139 each drop from 15,015 to 825/225/45 for l=2/3/4, while mandatory sector203 remains 10,296. These are only index counts, not equations/timings. Compare progressively from l=2; l=4/5 may omit high-numerator lower-sector relations and risks false masters. On reading the published Kira 3 usage syntax, corrected the preview template from an unsupported topology-object list to `truncate_sp: [1: l]` under the reduction job. Corrected outputs now use distinct `jobs.truncate_sp_l{l}.v2.preview.yaml` filenames to preserve the original v1 previews; neither version is executable by the project runner. Need still validate YAML parsing with the actual installed Kira 3.1 before any heavy trial.

### 2026-10-16 Kira 3 truncate_sp syntax correction after user preview

User reported generated preview contains `truncate_sp: [1: 2]`. Checked published Kira 3 paper (Comput. Phys. Commun., *Kira 3: Integral reduction with efficient seeding and optimized equation selection*, sec. 3.1.2), which specifies job option as `truncate_sp:\n  - {topologies: [topo7], l: 3}` within `reduce_sectors`; that is the safest documented machine-readable form for QEDCalc. Presentation slides use `truncate_sp: [l: 5]` shorthand, but `[1: 2]` is not justified as the topology-indexed published example and should NOT be used for our next experiment. Restored topology-object form, now outputting `jobs.truncate_sp_l{l}.v3.preview.yaml` (no overwrite of old previews or jobs.yaml). Still no Kira execution; check actual Kira 3.1 parsing on an isolated project before heavy initiate job. Index counts remain only offline heuristic.

### 2026-10-16 isolated truncate_sp l2 preflight

Following the user's execution of corrected v3 offline previews, added `examples/three_loop_sector203_truncate_sp_l2_prepare.py`. Calls the existing validated provisional64 isolated project preparation with a fresh timestamped run ID, then only on the NEW project's jobs.yaml inserts documented Kira 3 `truncate_sp:\n  - {topologies: [VP05_full], l: 2}`. Preserves old failed r6s6d1 project, original jobs, all candidate lists and prior r5s6d0 output. The new project is preparation-only, NOT a Kira execution. Next inspect the job and verify actual installed Kira 3.1 accepts the schema before any expensive run.

### 2026-10-17 VP05_full sector203 r6s6d1 truncate_sp l=2 COMPLETE

User reports successful clean end of monitored Kira run in `output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734` with `MONITOR_RESULT={"reason":"kira_exit","kira_returncode":0,"elapsed_s":95063.9,"last_sector":["203","14","14"],"success":true}`. Kira total time 95062.0s (~26h24m22s); 2678 selected equations. First recursive generation/selection: 314253 equations (119693 zero, 194560 independent), solve backward 11403.8 seconds (~3h10m), equation table 305896 independent coefficients. Kira reported 5 masters for its selected system: one sector201 `VP05_full[1,0,0,1,0,0,1,1,0,0,0,0]` and four sector203 `VP05_full[1,1,-1,1,0,0,1,1,0,0,0,0]`, `VP05_full[1,1,0,1,-1,-1,1,1,0,0,0,0]`, `VP05_full[1,1,0,1,-1,0,1,1,0,0,0,0]`, `VP05_full[1,1,0,1,-2,0,1,1,0,0,0,0]`. Original fourth candidate `VP05_full[1,1,0,1,0,0,1,1,0,0,0,0]` absent from reported master list. Kira then did another 14-sector pass (~10 minutes by user observation), output `Number of selected equations to reduce: 0`, `2678 equations: 0 zero + 2678 independent`, `master integrals which should be avoided`, `Regenerate`, and after another 14-sector pass output `Number of selected equations to reduce: 2678 equations` before finishing. Peak chart RAM ~20.92 GB, swap near zero at observation; final peak across run not yet verified from full monitor. This is successful **Kira execution** with a restricted/truncated system, NOT a proof that all 64 provisional candidates form a valid global basis or that the r5s6d0 ten-master closure is equivalent. Retain all result files for read-only audit; avoid rerun until inspecting `results/masters.final`, result DB and monitored log.

### 2026-10-17 VP05 truncate_sp l2 saved SYSTEM finite-field CONDITIONAL audit

User ran `examples.three_loop_sector203_l2_saved_equation_rank --points 1` on completed project. The 2678 saved SYSTEM equations have rank 2678 at p=1000003, (z,d)=(17,7). Ten short integral IDs `(1,202),(2,202),(3,202),(4,73),(5,201),(6..10,203)` sector-match exactly the ten entries in `results/preferredMasters` *by list position*; order within sectors is **not verified**. Under the explicit unverified alias hypothesis ID n == preferredMasters nth entry, all five mandatory integrals lie in span(saved equations + five reported selected masters) at this sample, including original candidate4 as short ID10, with no rank increase. Four other targets are already among those masters, so their zero increments are tautological. This conditional rank result is NOT a proof of symbolic reduction, not evidence of global 64-master sufficiency and not a verified alias map. Previous direct full-weight probe falsely labeled candidate4 independent because short IDs were treated as different columns; script now guards unresolved aliases. Next inexpensive step: test further finite-field points and/or extract Kira source-level short ID semantics, but do not rerun Kira. Completed run preserved.

### 2026-10-17 Three-point conditional finite-field audit of completed l2 SYSTEM

User-supplied log for `examples.three_loop_sector203_l2_saved_equation_rank --points 3`: each of (z,d)=(17,7),(29,11),(37,13) at p=1000003 produced 2678 saved equations and rank 2678. The 5 reported masters each add rank 1. Under *unverified* hypothesis that Kira short ID n matches preferredMasters row n (10/10 sector tags match), all 5 mandatory integrals have zero rank increment after saved equations + the 5 masters, including original candidate4 as ID10. For the other four mandatory integrals this zero increment is tautological, because they are already among the added masters. Candidate4 membership is a nontrivial conditional numerical result but NOT independently validated alias assignment, symbolic reduction, or complete r7s6d2/64-master closure. Preserve run; no new heavy Kira computation. Next prioritize establishing source-level short-ID semantics; until then retain CONDITIONAL label.

### 2026-10-17 PyRed preferred master short-weight assignment traced to source

User checked checked-out GitLab Kira `release` source `src/pyred/integrals.cpp`: `TopoConfigData::import_basis` at ~1166 reads preferred basis integrals sequentially, placing no-coefficient lines with `basis_igls.push_back(igl)` and no intervening sorting; `Integral::setup` assigns `s_preferred_masters.igls = std::move(pref_basis.first)` (~1457); `Integral::set_preferred_masters` iterates `s_preferred_masters.igls` and maps each nontrivial weight to `Weight(++mapped_weight)` (~1492-1524). This strongly supports positional aliases ID1..ID10 in this user's all-single-integral `results/preferredMasters` file (ID6=added candidate5, ID7=original1, ID8=original2, ID9=original3, ID10=original4). All ten recorded alias-sector pairs agree with these entries. Caveat: release source checkout is not yet confirmed byte-for-byte to match installed Kira 3.1 binary; skipped weights/trivial integrals could alter positions, though ten-for-ten observed mapping strongly constrains that. Existing 3-point rank results now rest on a source-grounded alias rule *conditional on matching build*. Crucially, candidate4 inclusion in saved equations + selected masters at 3 points remains finite-field selected-system evidence only, not a symbolic identity or global master-basis closure.

### 2026-10-17 VP05 sector203 candidate4 sampled reduction coefficients (user local run)

Added read-only `examples/three_loop_sector203_l2_finite_field_reduction.py` (commit `56be1e5`). User successfully ran `--points 1` and `--points 3` on preserved l2 project (2678 equations, rank 2678 at all 3 points, p=1000003). Alias mapping inferred from Kira PyRed release source and project preferredMasters positional list: master IDs 5 sector201, IDs 6-9 sector203, candidate4 ID10 sector203. Sampled reduction of original candidate4 I10 was only in I5 and I6: `I10 = C(z,d)*(I6-I5) mod 1000003`; coefficients C are 176471 at (17,7), 482760 at (29,11), 513515 (= -486488 symmetric) at (37,13). IDs 7,8,9 coefficient 0 at all three points. This is strong finite-field evidence of a two-master symbolic relation, but no general rational C(z,d) reconstructed and no symbolic verification yet, no global VP05 master closure. Preserve original candidate sets and results. Next: look for direct low-term symbolic relation or exact coefficient reconstruction using saved selected equations, avoiding Kira rerun.

### 2026-10-17 VP05 candidate4 verification 11/11 and exact-structure next step

User ran `--verify-formula` at (z,d)=(31,5),(41,9),(43,17),(53,19), p=1000003. All four returned `pass:true`, 2678/2678 rank, I5 coefficient = +2/z, I6 coefficient = -2/z, I7-I9 zero. Combining earlier seven grid points gives 11/11 numerical consistency with polynomial relation `z*I10 + 2*I6 - 2*I5 = 0`. This is evidence in a single prime field, NOT an exact polynomial certificate. New `--prime 1000033` option allows independent characteristic checks without Kira rerun. The planned follow-on remains exact symbolic membership/reduction certificate from saved selected equations, followed by global master basis closure verification.

### 2026-10-17 VP05 candidate4 independent second-prime confirmation

User executed `python -m examples.three_loop_sector203_l2_finite_field_reduction --verify-formula --prime 1000033`. All four new evaluations `(z,d)=(31,5),(41,9),(43,17),(53,19)` returned `VERIFY_FORMULA pass=true` for conjecture `z*I10 + 2*I6 - 2*I5 = 0`; 2678 equations and rank 2678 at each evaluation, coefficients of I7/I8/I9 zero. Along with 11 tests in field 1000003, total 15 evaluated runs over two prime fields support the conjecture. Script's `coefficient_symmetric` display initially hardcoded original PRIME, resulting in wrong signed display at p=1000033 but coefficient_mod_p and pass checks were correct. Fixed display in commit `69ffb18`. Still NOT an exact symbolic certificate and NOT global 64-master closure; no registry promotion.

### 2026-10-17 VP05 candidate4 finite-field provenance subset preflight

Added read-only `examples/three_loop_sector203_l2_witness_subset.py` (commit `ff4985b`). Rather than immediately attempting potentially explosive full symbolic elimination over 2678 equations, this script tracks finite-field Gaussian-elimination row provenance at z=17,d=7 over p=1000003 (same established full-rank probe), with caps on coefficient fill and row support. It reconstructs the polynomial target `17*I10 + 2*I6 - 2*I5` as a combination of ORIGINAL serialized equations and verifies the original-row combination exactly modulo p. It prints row IDs and modular coefficients for a candidate exact symbolic subsystem. This is only a modular certificate and does not prove the symbolic z,d relation; code not yet exercised against user's local saved SYSTEM data. Do not rerun Kira; next collect runtime/support size, then decide feasibility of selective symbolic solve.

### 2026-10-17 IMPORTANT CORRECTION: VP05 candidate4 coefficient sign

User's first run of `examples.three_loop_sector203_l2_witness_subset` raised `Proposed relation did not reduce to zero: remaining 2 terms`. Code inspection discovered a sign error in earlier `examples/three_loop_sector203_l2_finite_field_reduction.py`: `reduce_vector({I10:1})` subtracts row combinations to leave `remainder`, so `I10 = remainder` modulo the system; its reported coefficient previously used `-remainder`, wrongly reversing all master coefficients. Consequently prior claimed `z*I10 +2*I6 -2*I5=0` had WRONG sign. Correct candidate is `z*I10 -2*I6 +2*I5=0`, equivalently `I10=(2/z)*(I6-I5)`. Earlier `VERIFY_FORMULA pass=true` tested the SAME wrong sign convention and is not an independent confirmation of the claimed sign; however sampled finite-field span/rank and structural two-master evidence remain valid. Corrected printed coefficient signs and `verify-formula` expected C to +2/z (commit `ee7c7b6`), corrected witness target vector to `17*I10-2*I6+2*I5` (commit `fa05117`). Re-run after pulling, verify original equation-combination provenance before asserting modular certificate. Symbolic identity/global basis remain open. Older worklog entries must be interpreted using this explicit superseding correction.

### 2026-10-17 VP05 provenance target trace sign fix

User ran `examples.three_loop_sector203_l2_witness_subset`: all 2678 rows independently pivoted; proposed corrected relation reduced to zero, but direct reconstruction check raised `AssertionError: Provenance check against original equations failed`. Root cause: target trace starts as empty, Gaussian elimination updates trace by subtracting pivot provenance, therefore after zero remainder the target is `-sum(trace[i]*original_equation[i])`, not `+sum`. Training pivots initialized with `{row_id:1}` remain correctly signed; only target reconstruction and serialized provenance weights require negation. Patched in commit `f0a6cca`. This is an unexecuted fix until user runs it; symbolic identity still not established. Prior initial positive-sign conjecture is superseded by corrected `z*I10 -2*I6 +2*I5 = 0`.

### 2026-10-17 VP05 candidate4 modular equation-combination certificate SUCCESS

User ran corrected `python -m examples.three_loop_sector203_l2_witness_subset` and obtained rank progress through all 2678/2678 saved equations, `WITNESS_SUBSET` with `support_count=528` and `verified_against_original_rows=true` at p=1000003, (z,d)=(17,7). Thus `17*I10 - 2*I6 + 2*I5` is demonstrably in the row span of 528 of the original serialized equations in this finite field. This is a genuine original-row modular linear combination; not a symbolic proof over Q(z,d), not a minimal subset, and not global VP05 closure. Added optional `--save-subset` (latest commit `3602a6b`) to export all 528 rows with the ORIGINAL symbolic coefficient text and the modular witness multipliers to separate timestamped audit JSON files under `output/three_loop_integral_family_audit/`; requires user execution and audit of exported data. All existing Kira outputs remain read-only. Next perform exact symbolic combination/elimination over selected subsystem, with resource caps and independent symbolic residual verification.

### 2026-10-17 VP05 528-row exact-text export confirmed; standalone replay preflight

User successfully executed `examples.three_loop_sector203_l2_witness_subset --save-subset`, producing `output/three_loop_integral_family_audit/vp05_candidate4_witness_20261017_183832.equations.json` and matching `.modular_witness.json`; output has rank=2678, support_count=528, verified_against_original_rows=true. The `.equations.json` export retains original symbolic coefficient strings `z,d`; the modular witness records GF(1000003) multipliers. Source equation identifiers may repeat, so pair strictly using `row_index`, file name and equation ID. Added `examples/three_loop_sector203_l2_symbolic_preflight.py` (commit `dfec5e7`) for a read-only *independent* replay of exported exact coefficient text evaluated at z=17,d=7, modulo 1000003, plus 528-row symbolic sparsity audit. This preflight does not prove an identity over Q(z,d). It is a safe input-integrity gate before capped symbolic Gaussian elimination. The user has not yet executed this new script.

### 2026-10-17 VP05 exact symbolic elimination bounded diagnostic prepared

User `SYMBOLIC_PREFLIGHT` on saved 528-row exact-coefficient export passed `modular_exact_text_replay_pass=true`: rows=528, distinct columns=756, total terms=3769, max row terms=24; 348 terms contain z and 177 contain d. Added `examples/three_loop_sector203_l2_symbolic_elimination.py` (commit `bcaf8c3`), a read-only exact SymPy Q(z,d) elimination experiment with strict per-row/trace/character caps, default 40 rows and PARTIAL_ONLY result. If full 528 rows eventually process, the script tries target `z*I10-2*I6+2*I5` and independently replays the original symbolic equations before EXACT_CERTIFICATE_PASS. **No symbolic proof has been obtained; code untested locally**. First run `python -m examples.three_loop_sector203_l2_symbolic_elimination --max-rows 40`. Increase scope only based on observed fill/time. No Kira rerun, no registry promotion.

### 2026-10-21 VP05 Fermat arithmetic probe following symbolic-elimination slowdown

User stopped SymPy exact sparse elimination after `rows=440/528` with >10h without progress; peak expression lengths ~7908 (equation), ~7823 (provenance), and low memory use. Do not rerun the current full SymPy elimination. Added `examples/three_loop_sector203_fermat_probe.py` (commit `3de6016`, output parser fix `6959113`), an initial read-only WSL Fermat microbenchmark using exported saved symbolic VP05 equations. It submits a batch of rational arithmetic expressions to Fermat and compares results at up to two finite-field evaluation points with the existing AST parser; benchmark also times SymPy algebra. It is NOT a Fermat IBP elimination, is NOT exact proof, and has not yet been tested against the user's actual WSL Fermat executable. Run `python -m examples.three_loop_sector203_fermat_probe --rows 40 --samples 10` first, inspect output/protocol; then compare larger sample sizes and develop a persistent Fermat-backed elimination only after correctness/protocol confirmation. No Kira reruns or basis registration.

### 2026-10-21 VP05 Fermat in-process row-update pilot

The previous Fermat 500-expression probe passed finite-field sampled checks: Fermat 4.043 s including WSL startup, SymPy 0.971 s algebra only; not an apples-to-apples comparison and expressions too simple for late-stage symbolic IBP elimination. Added `examples/three_loop_sector203_fermat_row_pilot.py` (commit `47f338f`): select two actual saved witness rows with common columns, build an IBP-like update `v[k] := v[k] - fac*b[k]` repeated inside a SINGLE Fermat process, and finite-field-check final coefficients at up to three points. This is a limited arithmetic/performance pilot, **not Gaussian elimination or an exact IBP certificate**. Protocol not yet run on user's installation. First test `python -m examples.three_loop_sector203_fermat_row_pilot --updates 20 --columns 8`. Do not restart slow full SymPy elimination, Kira, or promote VP05 basis.

### 2026-10-21 First bounded multi-row Fermat Gaussian elimination pilot

User's `three_loop_sector203_fermat_row_pilot` passed: 4 columns x 20 updates, three independent prime evaluations verified, Fermat including WSL startup 1.5063 s. Added `examples/three_loop_sector203_fermat_gaussian_pilot.py` (commit `5e17663`): construct pivot/order schedule from finite-field arithmetic for actual exported IBP rows, require the same schedule at three independent prime evaluation points, perform actual sparse coefficient elimination and pivot normalization as rational functions in ONE Fermat subprocess, and independently compare all emitted entries against finite-field eliminations at those points. Read-only, defaults to 12 rows and caps to 30, does NOT track symbolic original-equation certificates or prove target identity. Not yet run against user's Fermat installation: test `python -m examples.three_loop_sector203_fermat_gaussian_pilot --rows 12`. Only scale if crosschecks pass; do not restart Kira or full SymPy 528-row run. If Fermat syntax/output trouble, inspect first interpreter error instead of estimating performance.

### 2026-10-21 Fermat Gaussian pilot 12-row pass and 20-row implicit-product parser fix

User: 12 rows, rank 12, 8 eliminations, 23 columns, 51 outputs, passed three finite-field primes in 2.171 s including WSL start. 20 and 30 row tests aborted while Python parsed Fermat notation `((-z)d+2z+2)/(2z)` at row 13 / integral key `(47864189681668,138)`; this is valid Fermat shorthand for multiplication, not demonstrated algebraic mismatch. Added `explicit_multiplication()` via SymPy's implicit-multiplication parser before invoking existing safe finite-field AST evaluator (commits `2825afe`, `be563f4`) and a regression check on the actual failing expression. Re-run 20, then 30 row pilots. Pilot is a numerical cross-check of rational elimination, not a Q(z,d) certificate for I10. No full 528-row run or master registry promotion yet.

### 2026-10-21 Fermat 30-row repeat PASS; capped up-to-100 preflight enabled

User repeated `three_loop_sector203_fermat_gaussian_pilot --rows 30`: rank=30, 33 elimination operations, 52 integral columns, 3-prime PASS_SAMPLED in 4.254 s including WSL start (earlier 30-row 0.095 s, anomalous; do not infer stable speedup). Modified script (commit `8b6b67f`) to allow up to 100 rows with `--preflight-only`, command and output caps (`--max-commands 4500`, `--max-outputs 1000`). The preflight constructs the planned Fermat command script but DOES NOT execute it, reports estimated commands/outputs, and supports safe sizing before 50/75/100 actual runs. **No 100-row Fermat pass or exact symbolic certificate yet.** Recommended next `python -m examples.three_loop_sector203_fermat_gaussian_pilot --rows 100 --preflight-only`; do not increase resource caps blindly. No Kira rerun.

### 2026-10-21 Fermat 75-row PASS; 100-row sparse-pivot/output pilot

User's 50-row and 75-row Fermat pilot both passed sampled equality at primes 1000003/1000033/1000037. 50 rows: 103 eliminations, 623 outputs, 1.707s; 75 rows: 145 eliminations, 871 outputs, 0.111s (wall-time anomaly, do not rely on that number). 100-row preflight previously 8059 commands/1548 outputs over default limits. Added `--prune-eliminated-pivots` to omit only columns mathematically equal to zero after normalized pivot cancellation (not zero at a single finite-field sample), plus `--verify-last-rows N` to reduce expensive output while preserving all internal row elimination. This partial-output mode validates only last N emitted rows at independent finite-field points and **is not all-row verification or an exact symbolic certificate**. Commit `8117005`. New code untested in user's WSL Fermat. First test small 30-row with pruning and all outputs; then `--rows 100 --preflight-only --prune-eliminated-pivots --verify-last-rows 10`; do not blindly raise caps, avoid full SymPy re-run and Kira.

### 2026-10-21 Fermat 160-row preflight with dependency-based dead-row pruning

User confirmed 100 rows all-output preflight: 5220 commands, 961 outputs, over 4500 command cap. Last-5-row output preflight: 4349 commands, 90 outputs, within caps. Instead of blindly raising caps, updated `examples/three_loop_sector203_fermat_gaussian_pilot.py` (commit `f55bbdf`) to permit up to 160 rows and add opt-in `--prune-dead-rows`: compute backwards transitive closure of scheduled row-owner dependencies from verification rows, and omit Fermat computation of rows not needed in that closure. This does not discard integral coefficients based on finite-field zeros. Independent modular replay now similarly restricts to live dependency rows, while pivot schedule is still checked at three points. **Unverified on user's Windows/WSL Fermat**; start with 30-row all-output regression and 100-row last-10-output regression, then `--rows 160 --prune-eliminated-pivots --prune-dead-rows --verify-last-rows 10 --preflight-only`. Keep command/output caps; preflight is only command-count estimate and not a symbolic proof. Full 528-row exact symbolic certificate remains open.

### 2026-10-21 Native Fermat array/loop pilot before 160-row rework

160-row last-10-output Fermat Gaussian preflight with pivot- and dependency-pruning still requires 17,118 scalar interpreter commands for 955 planned row eliminations and 576 outputs (76 live rows); it exceeds existing command cap of 4500. **Do not run full 160 rows or blindly increase cap.** Fermat manual documents native arrays `[v] := [(...)]` and `for j = 1,n do ... od` loops. Added read-only `examples/three_loop_sector203_fermat_array_loop_pilot.py` (commit `7c5a5ee`), using actual exported witness row coefficients: initialize two Fermat arrays, perform 20 row updates using one loop command per update in a single WSL process, parse output, check three independent finite-field points. This is a prototype for replacing thousands of scalar update statements, **not yet exercised on user's Fermat version**, and not a multirow Gaussian elimination or exact IBP certificate. Run `python -m examples.three_loop_sector203_fermat_array_loop_pilot --updates 20`; fix syntax/protocol as needed before adapting full engine. Source: Robert H. Lewis Fermat User's Guide array and loop syntax. No Kira runs or registry changes.

### 2026-10-21 Fermat Gaussian native-row-array mode (experimental)

User confirmed Fermat native array/loop pilot 4 coefficients ×100 updates, 3-prime PASS_SAMPLED, 111 submitted commands, 2.223 s including WSL startup. Integrated optional `--array-loop-rows` in `examples/three_loop_sector203_fermat_gaussian_pilot.py` (commit `ac1c8e6`). This builds a full fixed-column Fermat array for each live row, applies each pivot subtraction and normalization as ONE Fermat loop statement, retains sparse expected supports for output selection, and uses the preexisting three-prime modular comparisons. It reports dense `array_cells` and enforces `--max-array-cells 20000` as an additional cap; dense loops can be more computationally expensive even with fewer submitted commands. **Mode is not yet tested on user's Fermat install**. Recommended first `--rows 30 --array-loop-rows --prune-eliminated-pivots`; then preflight `--rows 100 --array-loop-rows --prune-eliminated-pivots --prune-dead-rows --verify-last-rows 10 --preflight-only`, and 160 preflight only after the 30-row PASS. No exact symbolic certificate, no 528-row run or Kira restart.

### 2026-10-21 Compact sparse Fermat arrays: opt-in 320-row pilot

User confirmed native dense-array Gaussian 100-row and 160-row runs PASS_SAMPLED with 3 independent finite-field points, last 10 rows verified (100: 860 submitted commands, 12960 cells; 160: 2142 commands, 18240 cells). Added `--sparse-array-rows` opt-in mode and lifted pilot maximum to 320 rows (commits `f2b5b2e`, `1c5a420`). Per live row, compact Fermat array stores union of original, encountered owner support and pivot keys; elimination constructs per-operation destination/source index arrays and uses Fermat loop to update these matched entries. Row normalization is a compact-array loop. Columns are removed from expected support only by exact pivot cancellation, NEVER finite-field sample zeros. Existing three-prime output checking and array-cell/command/output caps remain. Mutually exclusive with dense `--array-loop-rows`; requires `--prune-eliminated-pivots`. **This sparse mode is untested in user's Fermat installation, particularly nested indexed access `r[d[j]]`; do not run 320-row Fermat calculation before passing 30-row and 100-row sampled regression tests and 320-row preflight.** Suggested: `python -m examples.three_loop_sector203_fermat_gaussian_pilot --rows 30 --sparse-array-rows --prune-eliminated-pivots`; then 160-row preflight `--prune-dead-rows --verify-last-rows 10`, then 320-row preflight. These are not proof of candidate relation or a complete 528-row certificate.

### 2026-10-21 320-row modular pivot divergence diagnostic

User ran compact sparse-array preflight with 160 rows: rank160, 955 scheduled operations, 76 live rows, 2184 Fermat array cells, 3476 submitted commands, 576 emitted coefficients, `within_caps=true` (preflight only, NOT Fermat execution). At 320 rows, schedule comparison fails across 3 finite-field points before preflight sizing: `FERMAT_GAUSS_PILOT_ERROR different pivot schedules across primes`. This is NOT evidence Fermat failed or symbolic relations differ, and not reason to force the first sample's schedule. Updated `three_loop_sector203_fermat_gaussian_pilot.py` (commit `eac65be`) to print `FERMAT_GAUSS_PIVOT_MISMATCH` with earliest differing row, both evaluation points, selected leads and operation tails; keeps hard stop. User should `git pull` then rerun 320-row `--preflight-only` to supply this diagnostic. Investigate unlucky modular specializations vs structurally different pivot schedules before further work; no 320-row execution and no Kira re-run.

### 2026-10-21 320-row pivot-schedule mismatch localized to row 204

User's 320-row modular preflight failed at 0-based row203. At baseline (p=1000003,z=17,d=7) the row had 59 elimination operations; at (p=1000033,z=29,d=11) it had 60, **but the final pivot key `[165513007333377,202]` was the same**. This indicates a transient elimination trace mismatch, potentially due to specialization-dependent zero coefficients; it does not establish differing final ranks. Added `common_operation_prefix`, `first_baseline_op`, `first_different_op` and near-divergence operation windows to `FERMAT_GAUSS_PIVOT_MISMATCH` (commit `94f47f4`). Must not disable cross-prime checks or assume a pivot schedule is generically valid without evidence. Ask user to `git pull` and rerun identical 320-row preflight; no full Fermat 320 run until resolution. Note 160-row sparse mode has only preflight validation so far, not a `PASS_SAMPLED` execution.

### 2026-10-21 320-row divergence at row204 operation21

Additional user diagnostic: at zero-based row203, after first 20 identical eliminations, baseline (p=1000003,z=17,d=7) next operation uses owner131 key `[165494753984514,202]`, while second sample (p=1000033,z=29,d=11) uses owner129 key `[165494753984513,202]`. Baseline 59 operations vs 60; final pivot same. This suggests but does not establish that one sampled coefficient vanishes accidentally. Instrumented further (`e53c73b`) to replay the shared 20 operations in both fields and print both candidate pivot coefficient residues. Still hard stops without running Fermat. Explicitly distinguish sampled zero from identically zero; avoid overriding schedule check until resolved. Request repeat 320-row preflight after `git pull` and examine `candidate_pivot_values_after_common_prefix`.

### 2026-10-21 Bounded finite-field specialization search for 320-row schedule

User's row204 diagnostic established candidate coefficient `[165494753984513,202]` after 20 shared eliminations has value 0 at (p=1000003,z=17,d=7) but 123902 at (p=1000033,z=29,d=11); this is an evaluation-specialization zero, not a rational-function identity. Added opt-in `--auto-points` to `examples/three_loop_sector203_fermat_gaussian_pilot.py` (commit `e13b84f`): deterministically try bounded distinct-prime modular evaluation points, group by identical **full elimination trace**, and select only when 3 points agree. Explicitly fail if no 3-point group; print selected points and number of checked candidates. Selected points also used for independent output replay, avoiding the previous hardcoded bad baseline. **Untested in user's Windows environment**. Do not claim 3-point agreement proves symbolic pivots are nonzero generically or yields an exact IBP certificate; keep full Fermat run blocked until 30-row sparse-array regression and preflight sizing. Suggested diagnostic: `python -m examples.three_loop_sector203_fermat_gaussian_pilot --rows 320 --sparse-array-rows --prune-eliminated-pivots --prune-dead-rows --verify-last-rows 10 --auto-points --preflight-only`.

### 2026-10-21 Packed per-row index maps for 320-row sparse Fermat preflight

User measured 320-row/1 final-row preflight 27376 commands, 25724 coefficient cells, 269 outputs and 281 live rows; last-3 rows 27973 commands, 26231 cells, 796 outputs. Thus lowering verification output cannot solve heavy dependency. Added opt-in `--packed-sparse-maps` (requires `--sparse-array-rows`): concatenate all elimination-specific source/destination index mappings for each live row into one pair of Fermat index arrays, and issue two index-array assignments per row instead of two for every elimination. Each elimination still captures factor then updates its precomputed segment in a Fermat loop, preserving operation order and all 3-point checks; see commits `0d2a3aa`, `08a0caa`. Logs `packed_map_cells` and caps these separately via `--max-map-cells` (default 100000). This reduces *submitted commands*, not necessarily runtime, symbolic expression swell, total index storage, or coefficient array cells; dense maps may remain memory-heavy. **Experimental: not verified on user's Fermat version**. Test 30-row sampled correctness before packed 320-row `--auto-points --preflight-only`; do not raise caps or run 320-row Fermat until sufficient safety review. No Kira or 528-row proof.

### 2026-10-21 Packed map Fermat parser fix

User's first 30-row `--sparse-array-rows --packed-sparse-maps` run failed before verification: Fermat reported `*** Inappropriate symbol: D1`, stating array names must start with lower case letter. Updated `examples/three_loop_sector203_fermat_gaussian_pilot.py` (commit `81a2c7a`) to use lowercase `dm{row}` and `sm{row}` consistently in map array assignment and loop references. This is a parser fix; packed-mode correctness remains untested until user reruns the **30-row** case. Do not proceed to 320-row Fermat execution; await PASS_SAMPLED and subsequent preflight sizing. No changes to source witness or Kira.

### 2026-10-21 Packed index-map reuse across Fermat row eliminations

320-row / one-verified-row preflight with `--packed-sparse-maps`: 14,700 submitted commands, 25,724 coefficient-array cells, and 791,660 index-map cells *summed across all per-row maps* (6,732 planned elimination operations), exceeding command and memory caps. Introduced opt-in `--reuse-packed-maps` (commit `6b79777`) to overwrite/reuse one pair of lower-case Fermat index arrays `[dm]`, `[sm]` for each successive live row instead of retaining named arrays `[dm0]`, `[dm1]`, etc. The reported `packed_map_cells` becomes the **maximum per-row map cells**, while `packed_map_cells_written` explicitly reports the sum of assignments across the entire script. This reduces peak mapped array storage only **if Fermat array reassignment replaces old storage appropriately**; it does not reduce the number of Fermat commands or the total number of index entries sent to the interpreter. First run 30-row `--sparse-array-rows --packed-sparse-maps --reuse-packed-maps --prune-eliminated-pivots` with all-row 3-prime verification. If pass, run 320-row `--auto-points --verify-last-rows 1 --prune-dead-rows --preflight-only`. Do NOT run 320-row computation (14,700 commands still above 4,500); do not raise caps or claim symbolic proof. Next substantive optimization must address operation count, indexing instruction count, and coefficient expression growth.

### 2026-10-21 Fermat native outer control-loop prototype

After 30-row `--reuse-packed-maps` PASS_SAMPLED at 3 primes, prototype `--loop-control-rows` added to `three_loop_sector203_fermat_gaussian_pilot.py` (commit `27aae04`). It requires `--sparse-array-rows --packed-sparse-maps --reuse-packed-maps --prune-eliminated-pivots`. Uses Fermat's `%[row+1] := [rROW]` pointer-to-array table (documented by Robert Lewis) and reused per-row metadata `[ow]` owner pointer IDs, `[pv]` pivot indices, `[lo]` and `[hi]` packed-map intervals. A nested Fermat outer loop performs row operations sequentially, including a factor capture before indexed coefficient updates; coefficient row normalization and independent 3-prime replay are unchanged. Reports `loop_control_rows` and `control_cells` and includes metadata in cap. **This syntax and behavior is NOT tested in user's WSL environment**, especially pointer expressions `%[ow[t]][sm[j]]` and multiline nested `for`; test only 30 rows first and resolve any Fermat parser errors before larger preflight. Native loop cuts *submitted commands*, not the 6732 arithmetic operations nor coefficient-array cells (25,724 estimated at 320 rows). 320-row Fermat execution remains BLOCKED; no cap increases or symbolic proof claim.

### 2026-10-21 Nested Fermat control-loop terminal continuation fix

User's 30-row `--loop-control-rows` run failed with `pv[t]` and `lo[t]` array-index-out-of-bounds, followed by unexpected `od` because the outer loop was emitted as four distinct interactive input commands. Fermat requires backtick continuation for multiline terminal input; added trailing backticks and a semicolon between factor assignment and nested loop (commit `770c7b8`). This is a Fermat parser/protocol hypothesis guided by its user guide, **not yet verified in WSL**. Re-run the same 30-row test only. If `PASS_SAMPLED` occurs, then explore 320-row preflight, but do not attempt full 320 calculation or relax storage caps. Full 528 symbolic certificate remains outstanding.

### 2026-10-21 Coefficient-array lifetime analysis for 320-row sparse Fermat

User's 320-row `--loop-control-rows` preflight reached 3667 commands (under cap4500), 25724 total coefficient cells (over cap20000), 22146 maximum packed-index map cells and 404 control cells; 281 needed rows for the last row's verification. Added optional `--analyze-row-lifetimes` (commit `a7ccd8a`) to preflight only, requiring `--sparse-array-rows --prune-dead-rows`. It computes each live row's last use from the fixed modular elimination schedule, keeps verification rows through output emission, and simulates allocations/releases to report `peak_live_cells`, row of peak, total allocated cells, and rows/cells potentially releasable before output. **No actual Fermat row freeing, reassignment or memory reclamation is implemented yet**. The measured lifetime peak is an abstract upper bound for retained coefficient entries, not evidence of actual Fermat RSS, and ignores symbolic expression size. 30/160/320 data integrity remains unchanged. Recommend user run original 320-row preflight with `--analyze-row-lifetimes` and share `FERMAT_GAUSS_LIFETIMES`. Do not run 320-row Fermat computation yet, and do not raise caps.

### 2026-10-21 Experimental Fermat coefficient-row cancellation after last use

The 320-row dependency-lifetime preflight estimated peak 14,179 simultaneous coefficient cells vs 25,724 cumulative allocated, with 280 of 281 live row arrays potentially releasable before final output. Implemented opt-in `--release-dead-rows` (commit `b509f8c`), gated on `--sparse-array-rows --prune-dead-rows --loop-control-rows`; calculates the last scheduled consumer of every live owner row, retains final verification rows, and emits Fermat's documented `@([rN])` array-cancel command **only after** the last dependent row has been fully processed and normalized. This is an experimental runtime feature: whether pointers `%[i]` retain reference to cancelled arrays or prevent memory reclamation must be verified separately. It does **not** automatically relax 20,000 array-cell cap; the existing total-allocation accounting remains and blocks 320-row run. First run 30-row sampled verification, with `--prune-dead-rows`, before adapting accounting or attempted 320-row execution; if a parser/pointer error occurs fix on small case. No exact symbolic proof yet.

### 2026-10-21 Sparse pivot-column explicit zeroing (untested)

160-row, last-10 verification: dense `--array-loop-rows` with `--max-outputs 1200` passed sampled independent 3-prime verification, but packed sparse failed at row 154, key `(47864189943809,138)`, Fermat value 201551 vs modular 0 modulo 1000003. Failure persisted with/without `--release-dead-rows`, `--loop-control-rows`, and `--reuse-packed-maps`, so root is in shared sparse implementation or sparsity assumptions, not those later options. Commit `9ede35b` now **explicitly assigns eliminated pivot slot to zero after each sparse row subtraction** for individual index maps, packed index maps, and native loop-controlled elimination. Factor is captured before zeroing; owner row untouched. This is a diagnostic hypothesis, NOT an established root-cause fix. Re-test only 160 rows with `--sparse-array-rows --packed-sparse-maps --prune-eliminated-pivots --prune-dead-rows --verify-last-rows 10` first. If failure persists, compare unpacked sparse and/or add controlled per-row symbolic/modular probe; do not advance to 320. Native nested Fermat syntax has not been retested after adding the pivot assignment.

### 2026-10-21 Cancellation-aware coefficient cell cap preflight

User reports all three 160-row sparse regressions PASS_SAMPLED after explicit pivot-column zeroing: packed reused, native Fermat loops, and native loops with row release. Commit `8801a16` now automatically computes dependency-lifetime live-peak cells when `--release-dead-rows` is enabled, reports `peak_array_cells_estimate` and `array_cap_basis` alongside cumulative `array_cells`, and bases the `--max-array-cells` *coefficient-entry accounting guard* on the estimated live peak only in release mode. Default mode still uses cumulative allocation. `FERMAT_GAUSS_PREFLIGHT.within_caps` uses the same basis. This does NOT assert or check physical Fermat process memory/RSS: pointer aliases, expression growth and allocator retention may be substantially larger. The previous 320 preflight estimated peak 14179 vs cumulative 25724 under a 20000 cap; the new accounting should be checked again because explicit pivot zeroing added Fermat commands. Run 320 with `--release-dead-rows --analyze-row-lifetimes --preflight-only` ONLY first, inspect all caps and commands and do not run full 320 Fermat until separately assessed. No proof of exact rational-function identity.

### 2026-10-21 320-row sampled validation and 528-row preflight gate

User reported **PASS_SAMPLED** for 320-row sparse-array Fermat elimination with `--packed-sparse-maps --reuse-packed-maps --loop-control-rows --release-dead-rows --prune-eliminated-pivots --prune-dead-rows --verify-last-rows 1 --auto-points`. Its preceding preflight had 320 rows, 466 distinct columns, rank 320, 6732 scheduled eliminations, 4174 Fermat commands, 269 emitted coefficients, 281 live rows, lifetime estimate 14179 coefficient cells vs cumulative 25724, 22146 packed map cells and 404 control cells; 280 scheduled row releases. **Only last row's coefficient outputs** were checked at 3 independent modular points; this is not a proof over Q(z,d), not an exhaustive verification of all 320 rows, and physical memory usage was not measured.

Commit `1839db3` extends parser upper bound from 320 to **528 rows**, and distinct column guard from 600 to **800** (original full witness has ~756 columns), *strictly for preflight*. It explicitly rejects all actual Fermat runs above 320, even if normal accounting estimates fall within configured caps. Default `--max-rows 320` remains intact and must be overridden using `--max-rows 528`. Next commands should use `--rows 400 --max-rows 528 --preflight-only` and subsequently `--rows 528 --max-rows 528 --preflight-only` with all proven 320 flags and `--auto-points --analyze-row-lifetimes`, inspecting pivot-schedule consistency, peak coefficient and map cells, command/output caps. Full 528 can have substantially higher symbolic expression and pointer retention costs; do not lift the explicit preflight gate without review. Need later a certifying exact-identity reconstruction; PASS_SAMPLED remains only sampled validation.

### 2026-10-21 400/528-row preflight results (user WSL)

Both runs were **PRE-FLIGHT ONLY** with auto-selected common modular pivot trace at `(1000037,21,15)`, `(1000081,25,23)`, `(1000117,29,31)`, rank equal to number of rows, not an exact Q(z,d) proof. Flags: sparse packed maps, reuse, native loop, last-use cancellation, pivot pruning, dead-row pruning, verify last 1, lifetime analysis.

| metric | 400 rows | 528 rows |
|---|---:|---:|
| columns | 601 | 756 |
| operations | 11,866 | 18,171 |
| live rows | 375 | 526 |
| commands | 5,746 | 7,989 |
| outputs | 392 | 505 |
| coefficient total cells | 48,142 | 77,393 |
| estimated coefficient live peak | 35,800 | 56,821 |
| packed map peak | 53,694 | 85,364 |
| control cells | 616 | 900 |
| total map entries written | 2,259,354 | 5,242,782 |
| scheduled row releases | 374 | 525 |
| within_caps | false | false |

Caps remain commands 4500, live coefficient cells 20000, map+control 100000, outputs 1000. **Do not override caps or remove >320 preflight gate.** Next focus: reduce coefficient live peak by changing elimination order or staged exact computations / dependency reductions, and reduce generated commands; investigate target relation via smaller support/certificate. 320 row last-row 3-point PASS_SAMPLED remains a sampled result only.

### 2026-10-21 Targeted row-space diagnostic (new read-only tool)

Added `examples/three_loop_sector203_target_rowspace_audit.py` (`5324cb8`). It reads the preserved 528-row equation witness (no Fermat/Kira calls), tests explicit target combination `z*(10,203) -2*(6,203)+2*(5,201)` at the three 528-preflight sample points, and reports direct support rows, modular rank, target echelon remainder, and target-membership sampled. **Crucial guard**: short IDs are hypotheses inferred from *another* saved Kira preferredMasters mapping; their equivalence to the packed witness JSON keys is NOT verified. If any target key is absent from the JSON, diagnostic prints `TARGET_ROWSPACE_BLOCKED` without claiming independence or failure of the physics relation; resolve alias mapping first. `--target-term KEY SECTOR COEFF` allows explicit alternate keys but coefficient evaluator intentionally only supports z/-2/2 in this narrow audit. This is a sampled row-space test, not an exact Q(z,d) proof; even success may require rows beyond this 528-row subset. The original 528-row preflight is above caps and remains runtime-blocked.

### 2026-10-21 Target rowspace success and provenance tracing

User ran `three_loop_sector203_target_rowspace_audit --rows 528`: all three points `(1000037,21,15),(1000081,25,23),(1000117,29,31)` yielded rank528, `target_in_rowspace=true`, zero remainder, 107 target elimination steps, 42 original equations directly touching target keys. These are finite-field results and alias mapping is still unverified. Commit `e6681ae` extends diagnostic to track each normalized pivot row as a modular linear combination of ORIGINAL saved IBP rows, obtain target's coefficient certificate, and independently reconstruct the exact sampled target vector from raw equations. Outputs certificate support row IDs/count and `certificate_original_equation_replay_verified`. Run again at 528 rows; interpret count as the actual nonzero support of modular certificate, not 107 elimination steps. No rational-function symbolic proof yet; full 528 Fermat remains blocked.

### 2026-10-21 528-row modular target provenance result: full support

User-provided `log(6).txt` reports for all three preflight points `(1000037,21,15)`, `(1000081,25,23)`, `(1000117,29,31)`: rank 528 of 528 original equations, target sampled remainder zero after 107 echelon reductions, `certificate_original_equation_replay_verified=true`, **`certificate_support_count=528` and row IDs exactly 0..527**. This means the 528 sampled equation rows are linearly independent and the representation of the target in their span is UNIQUE at each sampled field point. Since every one of the 528 coefficients in that unique representation is nonzero, **no strict subset of these same 528 original rows can reproduce the target at any of those three points**. This is stronger than merely saying a chosen elimination schedule needs 528; changing pivot order alone cannot reduce original-row support within this fixed independent system. It does not rule out alternate equations from a larger Kira system, other representation bases, or special symbolic structure; nor does it establish the integral key aliases or exact Q(z,d) identity. Future strategy should seek different equations or exact certificate over all 528 rows and optimize target-specific symbolic computation, rather than claim a 107-original-row certificate is possible just from rerouting elimination. Keep >320 Fermat runtime gate active until scope/memory are addressed.

### 2026-10-21 Full sampled certificate coefficient export

Added `--export-certificate PATH` to `examples/three_loop_sector203_target_rowspace_audit.py` (`0540b16`). Previously the code calculated all 528 original-equation coefficients for each of three finite-field points but displayed only 12 samples. The opt-in export now writes all coefficient vectors (rows 0..527), input point triples, alias-warning and source metadata as JSON, **only if all sampled target vectors replay-verify exactly against original equations**. The JSON is finite-field sample data for future rational-function reconstruction; no lifting, interpolation, generic identity, or exact proof claimed. No Kira/Fermat launched. Recommended Windows invocation: `python -m examples.three_loop_sector203_target_rowspace_audit --rows 528 --export-certificate output/three_loop_integral_family_audit/vp05_target_certificate_samples.json`. Future stage should add independently verified exact rational-function coefficient reconstruction with degree-bound/extra-prime checks, not mistake three evaluation points for enough data.

### 2026-10-21 Incremental finite-field coefficient samples and holdouts

User confirmed export of three replay-verified points (528 original-equation coefficients each). Commit `2172c5c` extends `examples/three_loop_sector203_target_rowspace_audit.py` with `--extra-points N`, `--holdout-points N`, and `--append-certificate`. Evaluates distinct deterministic checked-prime points, preserves original three point values, recomputes repeated points and checks coefficients before merge, validates original-row count, target, prior source path or SHA256, and uses atomic JSON replacement. Each exported sample has a `role` (`training` or `holdout`); old samples without role are treated as training; no rational-function interpolation/exact proof yet. Input sample JSON without SHA is accepted only when source path matches and overlapping original points' entire vectors agree. Do not claim a holdout is a rigorous polynomial identity test. Initial bounded test: `python -m examples.three_loop_sector203_target_rowspace_audit --rows 528 --extra-points 2 --holdout-points 1 --append-certificate --export-certificate output/three_loop_integral_family_audit/vp05_target_certificate_samples.json`. This is finite-field only and may be CPU-heavy. Do not launch full Kira/Fermat.

### 2026-10-21 Silent no-op fix in incremental sample collection

User reported `python -m examples.three_loop_sector203_target_rowspace_audit --rows 528 --extra-points 2 --holdout-points 1 --append-certificate ...` immediately returned no output with EXIT_CODE=0; Python `-c` printed normally. Root cause: `--append-certificate` implementation inadvertently removed the terminal `if __name__ == '__main__': main()` invocation. Commit `8e81212` restores it and fixes atomic JSON writer's trailing newline escape. The previously uploaded JSON has only three original samples and was not modified by silent no-op. User must git pull then rerun. This was an assistant-introduced regression; no additional points were computed.

### 2026-10-21 Target modular certificate coefficient grouping

Added `examples/three_loop_sector203_target_coefficient_structure.py` (`5f9cf86`), reading prior JSON with 5 training + 1 holdout point, reporting exactly matching residue-signature groups and small rational proportional pairs (numerator/denominator bounded 4 by default) separately testing each against holdout. Optional full JSON report path. No rerun of Kira/Fermat or modular elimination; no symbolic proof. Windows command: `python -m examples.three_loop_sector203_target_coefficient_structure --output output/three_loop_integral_family_audit/vp05_target_coefficient_structure.json`. Identified equalities are numerical hypotheses only, and holdout checks are not algebraic identities.

### 2026-10-21 Coefficient structure result and proportional class closure

User ran 5 training +1 holdout coefficient audit: 528 original-row coefficients collapsed to 280 distinct training signatures; 79 nontrivial equality groups covering 327 rows; 3445 small rational proportional pairs (bound 4); zero failures on holdout for both equal and ratio candidates. All finite-field hypotheses; exact rational-function identities not yet proven. Commit `171ad22` adds weighted-disjoint-set closure of holdout-confirmed equality and proportional relationships, reports `proportional_class_count`, representative, ratios-to-representative, largest class, and consistency contradictions; full groups included in JSON. Next command: `python -m examples.three_loop_sector203_target_coefficient_structure --output output/three_loop_integral_family_audit/vp05_target_coefficient_structure.json`. Do not infer number of independent symbolic functions until this report returns; independent point does not prove identity.

### 2026-10-21 166 modular proportional groups and off-grid validation

User's coefficient structure audit yielded `proportional_class_count=166`, largest 68, `proportional_class_inconsistencies=0`, and 0 equality/ratio holdout failures (528 coefficients; 79 equal groups; 3445 small-ratio pairs). These are **finite-field candidate groups**, not exact functional identities. Crucial geometry caveat: the original 3 samples `(z,d)=(21,15),(25,23),(29,31)` lie on `d=2*z-27`, while subsequent 3 `(31,37),(33,41),(35,45)` lie on `d=2*z-25`. Testing only on these lines can admit accidental equalities of distinct bivariate rational functions. Commit `5a406f3` adds `--offgrid-holdouts N` (max 8) to existing target audit: chooses deterministic distinct prime fields above 1001000, with noncollinear `(z,d)=(19+17i,53+11i)`, validated as not on legacy lines; samples have role holdout, append safely. Run `python -m examples.three_loop_sector203_target_rowspace_audit --rows 528 --offgrid-holdouts 2 --append-certificate --export-certificate output/three_loop_integral_family_audit/vp05_target_certificate_samples.json`, then rerun `three_loop_sector203_target_coefficient_structure` to test previous hypotheses against new points. All runs still finite-field only and do not prove Q(z,d) identity; 528 symbolic Fermat remains gated.

### 2026-10-21 Off-grid holdout validation: 166 classes remain

User's `log(10).txt` reports `training_points=5`, `holdout_points=3` (including 2 intentionally off-grid), `proportional_class_count=166`, largest class 68, `proportional_class_inconsistencies=0`, `equal_failed=0`, `ratio_failed=0`. Equality groups 79 (327 total rows), 280 distinct training signatures, 3445 small-rational pair hypotheses (bound 4). Because training points are unchanged, equality/ratio candidates are unchanged; the two extra off-line holdouts provide stronger **numerical** validation, not symbolic proof. Next proposed symbolic reduction: for each proportional group G_g, build H_g = sum_{i in G_g} r_i E_i with exact rational r_i, and search for a 166-unknown rational-function certificate against original target. Crucially this depends on unproven coefficient-proportionality hypotheses; require exact equation replay over Q(z,d) before claiming success.

### 2026-10-21 Experimental 166-class equation compression audit

Added `examples/three_loop_sector203_target_compression_audit.py` (`51f7c8b`). Reads the preserved 528 equation witness, 8-point sampled target certificate, and candidate proportional partition (166 classes). For each sampled prime it constructs H_g = sum_i r_i E_i with sampled original equation vectors, computes class representatives f_g, checks c_i == r_i f_g at each sample, reconstructs target by sum_g f_g H_g, and reports compressed nonzero term counts / maximum row length against original 528-row input. This does NOT yet export explicit symbolic H_g and is not an exact Q(z,d) proof. Run `python -m examples.three_loop_sector203_target_compression_audit --output output/three_loop_integral_family_audit/vp05_target_compression_audit.json`. Do not lift Fermat >320 runtime guard. Compare compressed terms and verify all samples before attempting exact symbolic H_g or functional interpolation.

### 2026-10-21 Compression audit outcome: 166 rows, 1985 sampled terms

User's `TARGET_COMPRESSED_AUDIT` for all 8 preserved points: original 528 equations / 3769 original terms; compressed 166 equations / **1985 nonzero sampled terms at each point**, 166 nonempty compressed rows, max compressed row terms 183. `all_ratios_valid=true` and `all_reconstructed=true` at all eight points including three holdouts (two off initial sampling lines). Equation reduction 68.6%, nonzero term reduction 47.3%. This is strong modular consistency but **NOT** a symbolic Q(z,d) certificate; avoid enabling 528 row full Fermat run or claiming symbolic coefficients reconstructed. Next engineering milestone: form exact H_g by rational weighted addition of ORIGINAL symbolic coefficients; verify exact support and complexity, then pursue representative-function rational reconstruction and exact target replay. Sampling preserves no guarantee of exact structural cancellation or 166-row symbolic span.

### 2026-10-21 Exact symbolic compression construction pilot

Added `examples/three_loop_sector203_target_symbolic_compression.py` (`02f3df4`). Reads original preserved 528-row witness plus 166 candidate proportional groups, constructs each H_g = sum_i r_i E_i as an exact Q(z,d) rational-weighted equation using SymPy `cancel`, outputs symbolic coefficient JSON and checks coefficient-level replay for every group at two finite-field points, with progress every 20 groups. Includes safeguards for inconsistent/overlapping partitions and per-group input term cap (default 5000). **Exactness concerns the H_g linear combination ONLY.** The proposed target coefficient ratios r_i are still modular hypotheses; compression alone does not prove zI10-2I6+2I5=0 over Q(z,d). Symbolic simplification may be CPU-heavy, and output is not yet benchmarked. Local invocation: `python -m examples.three_loop_sector203_target_symbolic_compression`; inspect `TARGET_SYMBOLIC_COMPRESS_CHECK` and `TARGET_SYMBOLIC_COMPRESS_EXPORTED`. Preserve original witness and Fermat >320 full-run gate.

### 2026-10-21 Symbolic compression run succeeded (user local)

`python -m examples.three_loop_sector203_target_symbolic_compression` completed all 166 groups with progress through 160; produced `output/three_loop_integral_family_audit/vp05_target_symbolic_compressed.equations.json`. `TARGET_SYMBOLIC_COMPRESS_EXPORTED`: original_rows=528, compressed_rows=166, original_terms=3769, compressed_terms=1985, target_identity_proven=false. Both full coefficient replay checks passed: `(p,z,d)=(1000037,21,15)` and `(1001003,19,53)` for all 166 compressed equations. This is exact *construction* of rationally weighted linear combinations H_g from original IBP equations, and sampled numerical replay; **not** an exact certificate that target is in the Q(z,d)-span of these 166 equations. Next verify modular rank and target membership for compressed symbolic rows across new off-grid points, then plan Fermat/rational-function target certificate with explicit resource preflights.

### 2026-10-21 Compressed 166-row modular target preflight

Added `examples/three_loop_sector203_target_compressed_preflight.py` (`95731c9`). Reads local saved exact H_g symbolic-combination JSON, measures column count, structural terms, modular echelon rank and elimination operations, checks target `z*(10,203)-2*(6,203)+2*(5,201)` in compressed 166-row span at four modular points (two existing, one off-grid, one extra), and performs coefficient provenance replay. Reports a deliberately limited **operation-only** cap: not Fermat command count, symbolic growth, RSS or a license to run Fermat. Source still has unverified alias mapping; target membership is finite-field only. Run `python -m examples.three_loop_sector203_target_compressed_preflight`. Do not lift 528 original-row Fermat runtime block based solely on this report.

### 2026-10-21 Compressed 166-row modular preflight succeeded locally

User ran `python -m examples.three_loop_sector203_target_compressed_preflight`: input 166 rows, 400 columns, 1985 terms. All four points `(1000037,21,15)`, `(1001003,19,53)`, `(1001107,36,64)`, `(1002101,47,83)` reported rank 166, exactly 1745 modular echelon operations, target z I10 - 2 I6 + 2 I5 in rowspace, zero remainder, 27 target elimination steps, 166 nonzero original-compressed-row certificate coefficients, and replay verification true. Summary: `all_rank_166=true`, `all_target_in_rowspace=true`, `all_replayed=true`, `all_under_operation_cap=true`, `proof=false`. Compared with original 528-row case (18171 operations), modular operation reduction is about 90.4%. **These metrics are NOT a Fermat runtime preflight; symbolic coefficient growth and resource usage are unmeasured.** Next phase: adapt Fermat pilot to accept compressed witness format and run its preflight-only size/resource audit before enabling a strictly capped experimental symbolic run. The original 528-row Fermat gate remains in effect; alias mapping and Q(z,d) target identity still unproven.


### 2026-10-21 Session restart: safe compressed Fermat resource preflight

On resuming from the 166-row / 400-column / 1985-term modular preflight, confirmed that `examples/three_loop_sector203_fermat_gaussian_pilot.py` already supports an explicit `--equations` file, `--rows 166`, sparse-array modes, and `--preflight-only`. No new Kira/Fermat calculation has been executed in this session. Run the following **resource-estimate-only** command on the user's Windows checkout (active branch `feature/master-basis-initiate-only`):

```powershell
git pull
python -m examples.three_loop_sector203_fermat_gaussian_pilot --equations output/three_loop_integral_family_audit/vp05_target_symbolic_compressed.equations.json --rows 166 --max-rows 320 --preflight-only --prune-eliminated-pivots --sparse-array-rows --packed-sparse-maps --reuse-packed-maps --loop-control-rows --prune-dead-rows --verify-last-rows 1 --analyze-row-lifetimes
```

Inspect `FERMAT_GAUSS_PILOT_START`, `FERMAT_GAUSS_LIFETIMES`, and `FERMAT_GAUSS_PREFLIGHT` for operations, emitted outputs, commands, peak live cells and caps. The last-row verification is a **planning proxy only**, not proof of target membership; symbolic Fermat cost is not inferred from 1745 modular operations. Do not launch full symbolic run or loosen caps until preflight figures are reviewed. Next implement an exact **target-only** elimination/certificate path that proves `z I_(10,203) - 2 I_(6,203) + 2 I_(5,201) = 0` by symbolic zero residual; preserve the original 528-row provenance and verify alias assumptions separately.


### 2026-10-21 One-command VP05 compressed Fermat preflight runner

Added `run_vp05_target_fermat_preflight.bat` (commit `d4761a9`) to run the existing 166-row Gaussian pilot in **preflight-only** mode against `output/three_loop_integral_family_audit/vp05_target_symbolic_compressed.equations.json`. It checks the local JSON exists, selects compatible modular schedules using `--auto-points`, estimates last-row backward dependency closure, sparse arrays/maps and live-cell occupancy, and propagates a nonzero exit code on error. It **does not start Fermat/Kira** and **does not prove** the target identity; last-row verification is a resource-planning proxy only. The runner has not yet been tested on the user's locally generated 166-row JSON. Next user command: `git pull` then `.\run_vp05_target_fermat_preflight.bat`; inspect `FERMAT_GAUSS_PREFLIGHT` and lifetime summaries before deciding whether to engineer a target-only exact certificate path. The original 528-row >320 Fermat guard remains unchanged.


### 2026-10-21 VP05 166-row Fermat resource preflight results (user local)

The user ran `run_vp05_target_fermat_preflight.bat` on the actual compressed symbolic JSON. The preflight returned successfully, but `within_caps=false`; **no Fermat/Kira launched**.

```text
selected points: (1000033,19,11), (1000037,21,15), (1000039,23,19)
rank=166; distinct schedules seen=2; 3 matching points selected
rows=166; columns=400; modular elimination operations=1745
verification: last row only; output coefficients=370
backward dependency live rows=162
Fermat commands=2320
allocated array cells=30788 (cap 20000)
packed map cells=44198 (cap 100000); control cells=444
lifetime-analysis live-cell peak=27863 (row 162, 138 live rows)
releasable rows=161; releasable cells total=30407
with --release-dead-rows: NOT tested; no actual memory reclamation proven
within_caps=false; result=ESTIMATE_ONLY; proof=false
```

Interpretation: the original array cap is exceeded by 10788 cells (53.94%). Even the purely modeled lifetime-based peak of 27863 cells exceeds the same 20000-cell cap by 7863 cells (39.315%). Thus **merely enabling experimental row release would not pass the existing cap**. The 27863 figure is an accounting estimate, not RSS or Fermat allocation measurement. Also, verifying the last row is not a certificate for the specific target. Do not raise `--max-array-cells`, run the 166-row symbolic pilot, or imply 1745 modular operations represent Fermat expression growth. Next work: engineer target-specific backward reachability, output only a target residual/certificate (rather than 370 final-row coefficients), and repeat the non-executing resource preflight. Then separately validate pointer aliasing and row-release correctness on a tiny symbolic run before considering an exact VP05 target run. Preserve original 528-row provenance and the outstanding integral-key alias caveat.


### 2026-10-21 VP05 target-only dependency-scope preflight implemented

Added `examples/three_loop_sector203_target_scope_preflight.py` and `run_vp05_target_scope_preflight.bat` (commits `a35445b`, `3ab8964`, `70fb723`). The new script reads the user's local compressed symbolic 166-row equations, performs four independent finite-field checks, derives each sampled target-elimination pivot-owner trace, walks the owner-row backward-dependency graph in the matching modular row-echelon schedule, and prints dependency-row counts, dependency operations, estimated retained-array cells and a hypothetical live-cell peak. It writes `output/three_loop_integral_family_audit/vp05_target_scope_preflight.json`. **No Fermat or Kira call is made.** These are finite-field scheduling hypotheses, not authorization to prune any rows symbolically; pointwise-zero factors may be generically nonzero. Exact target identity and integral-key aliases are still unresolved. Next local command:

```powershell
git pull
.\run_vp05_target_scope_preflight.bat
```

Compare `VP05_TARGET_SCOPE_POINT` across points, especially pivot schedule agreement and dependency-row/operation counts. An absent or different sampled pivot schedule must be handled conservatively before implementing target-only Fermat execution. The new tool has not yet been run on the user's local 166-row JSON.


### 2026-10-21 VP05 target-only scope audit result: no row pruning

User ran the target-only scope preflight against the local 166-row compressed exact-combination witness. Four points `(1000037,21,15)`, `(1001003,19,53)`, `(1001107,36,64)`, and `(1002101,47,83)` agreed: rank=166, target elimination steps=27 and direct pivot owners=27, but backward dependency closure consumes **all 166 rows** and **1745 elimination operations**. Each point reported exact modular target replay true, full pivot schedules equal, allocated structural support-cell estimate 30987, hypothetical row-release peak 27093 (row index 162), both above existing 20000 cap. Target output union is 400 columns. No Fermat launched; no proof of the exact Q(z,d) target identity. Conclusion: row-dependency pruning with this schedule provides no gain; do not pursue 27-row-only symbolic computation without a different valid certificate/strategy. Next explore sparse symbolic live-memory reduction or certificate-first algorithms with bounded preflight and correctness guards, while retaining caps and alias caveats.


### 2026-10-21 VP05 166-row symbolic memory pressure profiler

Added `examples/three_loop_sector203_memory_pressure_audit.py` (`b15677b`) and `run_vp05_memory_pressure_audit.bat` (`2871871`). Four-point static audit reconstructs symbolic allocated-support sets per row using the existing Gaussian pilot's pivot scheduling conventions, tracks each row's last consumer, and records full/candidate-released live-cell peaks and the largest contributors. Saves `output/three_loop_integral_family_audit/vp05_memory_pressure_profile.json`. No Fermat/Kira, no increase to 20000-cell safety cap, no target identity proof. The previous target-only dependency scope still requires all 166 rows. The new profile is for identifying high-impact memory optimization candidates rather than guessing that row release alone is sufficient. Need user local run: `git pull`, then `.\run_vp05_memory_pressure_audit.bat`. Confirm the profile's static accounting against the earlier 30788 / 27093-27863-cell preflights. If values differ, diagnose support-estimator conventions before permitting any large Fermat run. The peak is not measured RSS, and release semantics remain unverified.


### 2026-10-21 VP05 memory pressure profile: measured static output and accounting mismatch

User ran `run_vp05_memory_pressure_audit.bat` on the compressed 166-row symbolic input. At all four points `(1000037,21,15)`, `(1001003,19,53)`, `(1001107,36,64)`, `(1002101,47,83)`: rank 166, same modular schedule, `allocated_cells_total=31840`, `lifetime_peak_cells=27863`, `peak_row=162`, `peak_live_rows=138`, `above_cap_allocated=11840`, `above_cap_even_if_released=7863`. No Fermat/Kira run; no exact target proof.

The profile's allocated 31840 differs from the Fermat pilot preflight 30788 and target-scope preflight 30987; the 27863 live peak agrees with the Fermat pilot's lifetime-only estimate, while target-scope estimated 27093 under a different structural accounting convention. These numbers must **not** be silently combined or treated as actual memory consumption. The newer profiler includes structural pivot/support bookkeeping that may differ from the exact Fermat array map allocation. Diagnose row-by-row support convention discrepancies against `three_loop_sector203_fermat_gaussian_pilot.py`; use the pilot's own exact mapped-cell count as authoritative for its current generated script. Even optimistic 27863 cells exceed 20000 cap. Keep full symbolic VP05 execution blocked; continue with accurately reconciled structural accounting and alternative algorithm design. The JSON with per-row contributors is local-only: `output/three_loop_integral_family_audit/vp05_memory_pressure_profile.json`.


### 2026-10-21 Cell-accounting reconciliation audit introduced

Added `examples/three_loop_sector203_cell_accounting_reconciliation.py` and `run_vp05_cell_accounting_reconciliation.bat`. This reconstructs the existing Fermat Gaussian pilot's full-row sparse array maps and contrasts that accounting with the memory-pressure profiler and target-scope support-only estimator on the same four prime points. Detailed per-row pilot map sizes and summaries are exported to `output/three_loop_integral_family_audit/vp05_cell_accounting_reconciliation.json`. Crucial distinction: original pilot `--verify-last-rows 1 --prune-dead-rows` only included a 162-row backward closure (30788 cells), whereas the full-target closure includes all 166 rows; these are different comparison scopes. The target-scope estimator counts normalized surviving support, not every allocated pivot/intermediate cell. The new audit must be run locally before treating any cross-tool discrepancy as resolved. No Fermat/Kira launched; 20000-cell cap remains; symbolic proof and alias mapping remain pending.

Run:
```powershell
git pull
.\run_vp05_cell_accounting_reconciliation.bat
```


### 2026-10-21 VP05 exact-map cell reconciliation: local PASS, symbolic scale still blocked

User returned `VP05_CELL_RECONCILE_POINT` at four points `(1000037,21,15)`, `(1001003,19,53)`, `(1001107,36,64)`, `(1002101,47,83)`. All rank=166 and identical echelon schedule. All four report:

```text
pilot_sparse_allocated_cells = 31840
memory_profiler_allocated_cells = 31840
memory_profiler_minus_pilot = 0
pilot_sparse_lifetime_peak_cells = 27863
memory_profiler_peak_cells = 27863
pilot_peak_row = 162 (zero-based); live rows = 138
target_scope_allocated_cells = 30987
target_scope_peak_cells = 27093
target_scope_minus_pilot = -853
pilot_above_20000 = true
pilot_release_peak_above_20000 = true
all_schedules_match_first = true
fermat_executed = false; proof = false
```

The difference of 853 cells is between `target_scope` normalized support accounting and the actual pilot sparse-map allocation, which retains intermediate/pivot keys. The earlier pilot's 30788 cells covered just the 162-row closure of the *last-row output*, not the entire 166-row target dependency set; this should not be compared as a same-scope estimate. Reconciled full-row memory accounting is 31840 cells, with a hypothetical peak of 27863 on row-release. Both exceed the unchanged 20000 safety cap. No proof that Fermat will actually reclaim memory, nor any actual RAM/RSS measurement. Do not lift large symbolic execution gate. Next implementation should seek a provably equivalent lower-storage exact elimination or target-certificate method, with correctness audited first on small rows and explicit target residual/alias verification.


### 2026-10-21 Experimental incremental storage candidate, no Fermat execution

Implemented `examples/three_loop_sector203_incremental_storage_preflight.py` and `run_vp05_incremental_storage_preflight.bat` (commits `f635059`, `5c1edc1`, `ec732bf`). The tool compares the existing Fermat pilot's all-166-row sparse map (31840 allocated, 27863 hypothetical released peak from user results) to a **candidate** footprint that reserves initial and normalized supports but hopes to use a separate scalar for temporary pivot factors rather than retaining all eliminated-pivot column slots indefinitely. It uses the same four independently replayed modular pivot schedules and never calls Fermat/Kira. This is exploratory planning, **not** a safe upper bound: intermediate symbolic supports and actual Fermat allocation may exceed the candidate; executable row maps and exact replay are not implemented. A passing 20000-cell candidate estimate must NOT authorize a large symbolic run.

Next command:
```powershell
git pull
.\run_vp05_incremental_storage_preflight.bat
```

If reduction is material, next engineering stage is a true small-scale incremental sparse row executor with per-operation symbolic support bookkeeping and exact/Fermat replay compared to the existing pilot, plus explicit array/release semantics checks before any 166-row execution. Keep alias and exact Q(z,d) target certificate unresolved.


### 2026-10-21 Incremental storage preflight outcome: insufficient gain

User ran `run_vp05_incremental_storage_preflight.bat`. All four finite-field points reported the same schedule and:
```text
pilot_total=31840; pilot_peak=27863
persistent_candidate_total=31143; persistent_candidate_peak=27232
potential_allocated_cell_reduction=697
potential_peak_cell_reduction=631 (~2.26%)
candidate_within_20000=false
transient_pivot_key_count_total=697
fermat_executed=false; proof=false; implementation_ready=false
```
Thus simply separating transient pivot coefficients has limited projected benefit and still exceeds the 20000-cell guard by 7232 even with optimistic release assumptions. Do not implement this experimental layout as the primary scaling fix or raise the resource cap on the strength of this estimate. Prefer a distinct target-certificate algorithm with a bounded no-Fermat preflight, preserving exact original-row provenance and independently verifying the rational-function target identity and integral-key aliases before claiming proof.


### 2026-10-21 VP05 dual certificate-first modular feasibility

After the incremental sparse-storage candidate reduced only 631 peak cells (27863 to 27232; still above the 20000 guard, user-supplied 4-point log), focus shifts from sparse-row tweaks to certificate-first feasibility. Added `examples/three_loop_sector203_dual_certificate_preflight.py` and `run_vp05_dual_certificate_preflight.bat`. This computes finite-field row-provenance certificates for the **166 compressed equations**, replays their target reconstruction independently, and measures support density and stability over four points. It is intentionally **not** rational-function coefficient reconstruction and does not run Fermat/Kira. A dense 166-entry modular certificate or unstable support would discourage naive sparse certificate recovery; a sparse stable one warrants an exact-Q(z,d) method but is still not proof. Remember compressed rows are exact linear combinations of original 528 IBP rows; any eventual symbolic certificate must replay through the original rows with exact arithmetic, and sector alias mapping is unresolved.

Local:
```powershell
git pull
.\run_vp05_dual_certificate_preflight.bat
```
Look for `VP05_DUAL_CERT_POINT` and `VP05_DUAL_CERT_SUMMARY`; JSON: `output/three_loop_integral_family_audit/vp05_dual_certificate_preflight.json`. No relaxation of symbolic execution caps.


### 2026-10-21 VP05 dual certificate preflight local results

User reports all four sampled primes `(1000037,21,15)`, `(1001003,19,53)`, `(1001107,36,64)`, `(1002101,47,83)` return rank=166, target remainder size 0, certificate support=166/166, zero certificate rows=0, and `replay_verified=true`. `support_stable_across_points=true`, `symbolic_certificate_found=false`, `alias_mapping_verified=false`, `fermat_executed=false`, `proof=false`. Dense certificate rules out gains from **simple sparsity of this computed basis certificate**; it does not prove every possible certificate or another row basis must use 166 entries. Next focus on rational-function reconstruction of certificate coefficients from fresh evaluations (with independent held-out modular tests), exact `Q(z,d)` identity replay, and lifting the 166 compressed combination coefficients to the original 528 IBP equations. Guard against interpolation degree bounds, unlucky specializations, and the unresolved alias map. No large Fermat execution until certified resources.


### 2026-10-21 VP05 compressed certificate sample archive (6 points)

Implemented `examples/three_loop_sector203_certificate_sample_export.py` and `run_vp05_certificate_sample_export.bat` to export the complete 166-component finite-field certificate at each of four training points `(1000037,21,15)`, `(1001003,19,53)`, `(1001107,36,64)`, `(1002101,47,83)` and two separate holdouts `(1003001,17,71)`, `(1004027,43,29)`. The script validates rank and independently replays target reconstruction against all compressed rows at each point before atomic JSON output; includes SHA256 of local compressed source to protect against stale mixup. Output: `output/three_loop_integral_family_audit/vp05_compressed_certificate_samples.json`. No Fermat/Kira and **no rational-function reconstruction/proof yet**. Six individual finite-field samples do not suffice to assert a multivariate rational function without degree bounds and independent symbolic equality. Sample archive and its holdouts should not be reused as training points in a future reconstruction validation; use additional unseen points thereafter. The integral aliasing warning remains.

Local command:
```powershell
git pull
.\run_vp05_certificate_sample_export.bat
```


### 2026-10-21 VP05 compressed modular certificate sample export PASS

User executed `run_vp05_certificate_sample_export.bat`. All 4 training points `(1000037,21,15)`, `(1001003,19,53)`, `(1001107,36,64)`, `(1002101,47,83)` and 2 reserved holdouts `(1003001,17,71)`, `(1004027,43,29)` passed modular target replay. Each sample has all 166 nonzero coefficients. Output `output/three_loop_integral_family_audit/vp05_compressed_certificate_samples.json` SHA256 of source compressed symbolic equations `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. `fermat_executed=false`, `proof=false`. This confirms six consistent numerical certificates but does not bound rational-function degrees, show unique interpolation, verify exact zero over Q(z,d), or establish integral alias mapping. Before interpolation implementation, design a bounded-degree or adaptive reconstruction using sufficiently many distinct points, independent fresh holdouts, and exact symbolic replay.


### 2026-10-21 VP05 rational-certificate interpolation point budget

Added `examples/three_loop_sector203_certificate_reconstruction_design.py` and `run_vp05_certificate_reconstruction_design.bat`. Reads the six user-exported full 166-component finite-field certificate vectors; checks completeness, uniqueness and source digest presence, groups samples by prime and tabulates projective polynomial coefficient counts for bivariate rational ansatz with numerator/denominator total degrees 0..6. For degree bounds (n,d), unknown coefficients up to scale = (n+1)(n+2)/2 + (d+1)(d+2)/2 - 1; this is a **generic point-count lower bound, not an identification guarantee** (shared factors/exceptional points/denominator zeros must be checked). All six existing points use different primes; therefore they cannot be naively fed into interpolation as a grid over one field. Next must collect a same-prime z,d grid with independent holdouts, then CRT/rational lifting as needed and exact symbolic replay. No Fermat/Kira run, no symbolic proof, unresolved sector alias mapping.

Local:
```powershell
git pull
.\run_vp05_certificate_reconstruction_design.bat
```
Output `VP05_RECON_DESIGN_SUMMARY`, `VP05_RECON_DEGREE` and JSON `output/three_loop_integral_family_audit/vp05_certificate_reconstruction_design.json`. No 166-row symbolic execution has been authorized.


### 2026-10-21 VP05 rational reconstruction design PASS and same-prime sampling implemented

User ran `run_vp05_certificate_reconstruction_design.bat`. Results: six saved certificate samples, four training plus two holdouts, all six in **different** prime fields (`max_training_points_at_one_prime=1`). All 166 coefficients included, `models_count=49`. Generic projective coefficient counts for (numerator,total denominator degree) equal bounds: (1,1)->5, (2,2)->11, (3,3)->19, (4,4)->29, (6,6)->55. Suggested points with eight holdouts: 13,19,27,37,63. These are generic unknown-count lower bounds; must verify interpolation matrix rank, degree bounds, denominator nonzeros, and independent checks. No exact symbolic proof.

New `examples/three_loop_sector203_same_prime_certificate_samples.py` and `run_vp05_same_prime_certificate_samples.bat` collect 19 training + 8 reserved holdout coefficient vectors from a single prime `1000037` at distinct deterministic two-variable points (bounded 120 attempts), checking rank=166 and independently replaying target at every accepted point. Save source-SHA256-anchored JSON `output/three_loop_integral_family_audit/vp05_same_prime_certificate_samples.json` atomically. The sampling grid is for eventual bounded-degree (3,3) hypotheses and may still be degenerate; rank test for interpolation is a separate future step. The 8 holdouts must not be used for fitting. No Fermat/Kira, no proof and no cap changes.

Local:
```powershell
git pull
.\run_vp05_same_prime_certificate_samples.bat
```
Look for `VP05_SAME_PRIME_PROGRESS`, `VP05_SAME_PRIME_SUMMARY`. Sampling work is finite-field computations, potentially longer than earlier 4-point checks.


### 2026-10-21 VP05 same-prime degree-3 interpolation trial implemented

Added `examples/three_loop_sector203_certificate_interpolation_trial.py` and `run_vp05_certificate_interpolation_trial.bat`. For each of 166 compressed certificate coefficients, fit an **independent homogeneous rational ansatz over one prime**: numerator and denominator polynomial total degrees <=3, 10 monomials each, 20 coefficients up to overall scaling = 19 degrees of freedom. Uses training rows only to solve a 19x20 homogeneous modular linear system; accepts a hypothesis only with a **one-dimensional kernel** (rank 19), denominator nonzero at each training point, and all 8 saved holdout values satisfied. Rejects underdetermined/nonunique or singular candidates; prints the number of holdout passes, failures and nonunique/singular rows, and persists the candidate coefficient vectors in `output/three_loop_integral_family_audit/vp05_certificate_interpolation_trial.json`. *Modular hypotheses, even if all holdouts pass, are not exact Q(z,d) reconstruction, cannot prove the target relation, and cannot certify sector alias mapping.* No Fermat/Kira and no memory-cap relaxation.

The preceding 27-sample generation has not yet been confirmed by the user in this session. To run this trial, first get valid same-prime sample JSON from `run_vp05_same_prime_certificate_samples.bat`, then run `run_vp05_certificate_interpolation_trial.bat`. Performance is finite-field 166x modest dense 19x20 elimination; no large symbolic elimination.


### 2026-10-21 VP05 27-point interpolation failure diagnosed: sampling geometry rank deficient

User ran original same-prime sampling: 19 training + 8 holdouts at p=1000037, no rejected points, source SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. Degree-3 rational interpolation returned `holdout_pass=0`, `holdout_fail=0`, `nonunique=166`, `singular_training=0`. **This is not 166 failed holdouts**: no candidate passed the one-dimensional kernel requirement, so no holdouts were reached.

Important cause: legacy points `z=17+37*i+11*i^2, d=29+61*i+7*i^3 (mod p)` lie on a single parametrized algebraic curve. Reproducing their first 19 training points, the degree<=3 monomial evaluation matrix has rank **9/10**, so the points cannot identify all degree-3 bivariate polynomial coefficients, irrespective of the certificate data. Other non-uniqueness (lower true degrees / common factors) remains possible even with full-rank sampling.

Added `examples/three_loop_sector203_interpolation_rank_diagnostic.py` and `run_vp05_interpolation_rank_diagnostic.bat` for direct rank/kernel histograms. Modified `three_loop_sector203_same_prime_certificate_samples.py` with `--grid-v2` and separate-output requirement; new 2D Cartesian-style grid uses `z=17+37*(i%5)`, `d=29+61*(i//5)` mod p, giving a verified **10/10 degree-3 monomial evaluation rank for the first 19 points**. Added runners `run_vp05_same_prime_certificate_grid_v2.bat` and `run_vp05_interpolation_grid_v2.bat` (the latter runs rank diagnostic then trial and retains separate JSON outputs). Original archive is not overwritten. No Fermat/Kira, no exact proof; 20000 symbolic cap unchanged.

Next local:
```powershell
git pull
.\run_vp05_same_prime_certificate_grid_v2.bat
.\run_vp05_interpolation_grid_v2.bat
```
Holdouts remain separate; require rank-aware model diagnosis, not blanket degree inflation, if nullity is still >1.


### 2026-10-21 VP05 corrected 2D-grid interpolation results

User executed `run_vp05_same_prime_certificate_grid_v2.bat`: p=1000037, 19 training and 8 holdouts, no rejected points; compressed source SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. Then `run_vp05_interpolation_grid_v2.bat`: degree=3, monomial evaluation rank=10/10 (no grid deficiency), kernel nullity histogram `{1:93,2:56,3:1,4:7,6:5,7:3,10:1}`. Of 166 compressed certificate components, **55** one-dimensional rational ansatz candidates passed all eight holdouts, **38** were unique on training points but failed holdouts, **73** were nonunique and were not holdout-tested. No singular-training cases. Sample SHA256 `378559de8c0bfc52aa4bb10e6733f006618c7df817c5e1ee1f17a071864adf9a`. `all_holdouts_pass=false,proof=false,fermat_executed=false`.

The 55 are finite-field hypotheses, not exact rational coefficient proofs. Important: `nonunique` does not imply higher minimal degree; polynomial gcd/common-factor normalization and adaptive (numerator_degree,denominator_degree) fitting should be attempted. For 38 failures, consider genuinely higher degrees, additional independent training/holdout points and evaluation design. Avoid approving large symbolic Fermat; keep 20000-cell guard. Eventually verify reconstructed coefficients over Q(z,d), replay certificate against compressed rows and original 528 equations, and resolve integral-key aliases.

### 2026-10-21 VP05 adaptive certificate degree fitting results

User ran `run_vp05_certificate_adaptive_degree.bat` with p=1000037, 19 training and 8 holdouts. Result: `resolved_finite_field=125`, `unresolved=41`, all results finite-field hypotheses, not exact Q(z,d) proof. Degree-pair histogram (numerator,denominator): `(0,2):1`, `(3,3):41`, `(0,1):1`, `(1,3):24`, `(2,3):45`, `(1,2):8`, `(0,3):2`, `(1,1):2`, `(0,0):1`. Previous fixed-(3,3) trial passed only 55, with 38 failed holdouts and 73 nonunique. Input sample SHA256 `378559de8c0bfc52aa4bb10e6733f006618c7df817c5e1ee1f17a071864adf9a`; equation SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. Next: diagnose 41 unresolved separately (nullity, holdout failures, denominator singularity) and gather additional fresh same-prime genuinely 2D points; avoid extrapolating that degree >=4 is necessary. Preserve original 8 holdouts for out-of-sample checks. Fermat/Kira not run, proof=false.

### 2026-10-21 VP05 unresolved adaptive certificate fitting diagnostic

After 125/166 finite-field candidate coefficients passed eight holdouts with adaptive numerator/denominator degrees up to 3, 41 remain unresolved. Added `examples/three_loop_sector203_adaptive_unresolved_diagnostic.py` and `run_vp05_adaptive_unresolved_diagnostic.bat`. The audit reads the existing adaptive-result JSON and corrected same-prime grid-v2 JSON, enforces source SHA256 equality and exactly 166 distinct row IDs, and classifies the unresolved rows using their saved nonunique-model and holdout-failure counters into only_nonunique, only_holdout_failure, both, and other. These are classifications of attempted ansatz fits, not proven causes or rational degree lower bounds. Does not rerun the 166 coefficient fits or start Fermat/Kira. Next user command: `git pull` then `.\run_vp05_adaptive_unresolved_diagnostic.bat`; inspect `VP05_UNRESOLVED_DIAGNOSTIC`. No exact Q(z,d) certificate, original 528-row replay, or sector alias proof yet; 20000-cell symbolic cap unchanged.

### 2026-10-21 VP05 unresolved 41 adaptive coefficients classified

User ran `run_vp05_adaptive_unresolved_diagnostic.bat`. Of 41 unresolved coefficient rows, classification by **attempted-model counters**: `only_nonunique=2`, `only_holdout_failure=0`, `both=39`, `other=0`. Every unresolved row has at least one nonunique candidate; 39 also had other models producing a unique fit that failed the 8 held-out points. These are not mathematical proofs of a minimum rational-function degree; they reflect only the model pairs explored using 19 training points. Source sample digest `378559de8c0bfc52aa4bb10e6733f006618c7df817c5e1ee1f17a071864adf9a`. Next prefer new, geometrically independent same-prime training samples, holding the original 8 out entirely, and rank/degree diagnostics before extending models. Retain the 125 earlier holdout-passing finite-field candidates for independent checking. Fermat/Kira not run; exact symbolic proof and alias mapping remain unresolved.

### 2026-10-21 Extend same-prime VP05 certificate training (grid-v3)

Added `examples/three_loop_sector203_certificate_extend_training.py` and `run_vp05_extend_training_grid_v3.bat`. The former reads the previously replay-verified grid-v2 sample archive (19 training, 8 reserved holdouts), verifies its compressed-equation SHA256 against the local 166-row input, creates 20 extra independent same-prime training evaluations using a shifted 7-column grid, checks each through full modular certificate replay and rank=166, and writes a separate grid-v3 JSON (39 training, **original eight holdouts left unchanged**) atomically. It never overwrites v2. The runner then invokes the existing adaptive numerator/denominator (0..3) fitter against grid-v3 and outputs a separate adaptive grid-v3 JSON. The user has NOT yet run this new workflow. No Fermat/Kira, no exact Q(z,d) certificate or alias proof. The 125/166 previous successes and 41 unresolved (2 only nonunique, 39 mixed nonunique and failed candidates) motivated collecting more training points before increasing polynomial degree.

Next user command:
```powershell
git pull
.\run_vp05_extend_training_grid_v3.bat
```
Look for `VP05_TRAIN_EXTEND_SUMMARY` and `VP05_ADAPTIVE_DEGREE_SUMMARY` and compare to previous resolved_finite_field=125. The original eight holdouts remain reserved and should not enter the fitting equations.

### 2026-10-21 VP05 grid-v3 extra training reveals non-generalizing candidates

User ran grid-v3 workflow: 20/20 new same-prime training points accepted, rejected=0; resulting archive p=1000037, 39 training, original 8 holdouts unchanged, sample digest `26d9a35f3d2578bc3231395fe724e540d979657ea3c29d4d2f4926bd93248929`, original equations digest `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. Adaptive degree pairs <=3 now pass **94/166**, 72 unresolved, versus 125/166 and 41 unresolved for 19 training. Degree histogram: `(0,2):1, (0,1):1, (1,3):24, (2,3):45, (1,2):8, (0,3):2, (1,1):2, (0,0):1, (3,3):9, (2,2):1`. In particular (3,3) passing candidates fell 41 -> 9. This suggests many prior degree-(3,3) candidates overfit 19 training points and 8 holdouts or lost one-dimensional kernel because of low-degree common factors; neither cause is yet distinguished row-by-row. Additional training improves the diagnostic even if accepted candidate count falls. Need row-wise comparison and nullspace-rank classification, and potentially 2D unisolvent point design and gcd normalization. No Fermat/Kira, symbolic proof=false.

### 2026-10-21 VP05 row-wise grid-v2 versus grid-v3 comparison

Added `examples/three_loop_sector203_adaptive_grid_comparison.py` and `run_vp05_adaptive_grid_comparison.bat` to compare all 166 rows in the two saved adaptive outputs. The tool checks SHA256 links back to both grid-v2/grid-v3 sample archives, confirms every original point (including all eight holdouts with preserved roles and coefficients) appears unchanged in grid-v3, and classifies transitions into pass_to_unresolved, unresolved_to_pass, pass_to_pass and unresolved_to_unresolved. For each v3-unresolved row, it recomputes the full (3,3) finite-field fit on 39 training points and reports status/nullity/rank plus earlier v2 model degree and stored v3 fit counters. This is a **diagnostic only**, not a rational-function proof; no Fermat/Kira execution. The local source archives are required and no outcome is asserted until user runs the new script.

Run `git pull` and `.\run_vp05_adaptive_grid_comparison.bat`. Look for `VP05_GRID_COMPARE_SUMMARY` and `VP05_GRID_COMPARE_UNRESOLVED`; detailed output in `output/three_loop_integral_family_audit/vp05_adaptive_grid_comparison.json`. Preserve the 20,000-cell Fermat safety guard and unresolved integral-key alias mapping.

### 2026-10-21 VP05 grid-v2/v3 rowwise outcome confirmed

User ran `run_vp05_adaptive_grid_comparison.bat`: `pass_to_unresolved=32`, `unresolved_to_pass=1`, `pass_to_pass=93`, `unresolved_to_unresolved=40`; total 166. Thus v2=125 passing, v3=94 passing, net -31. All 8 original holdouts preserved unchanged and v3 training=39 at p=1000037. **All 72 v3 unresolved coefficients had `degree_3_3_status=nonunique`** under 39 training points, rather than uniquely fitted degree-(3,3) models that merely failed holdouts. This does *not* imply degree bound 3 is false; possible polynomial common-factor nonidentifiability and/or special finite-field grid geometry. Next use a 2D grid that is unisolvent at higher polynomial degrees or compare full monomial evaluation rank and homogeneous nullities before more training or degree increase. Fermat/Kira not run, proof=false, 20000-cell cap remains.

### 2026-10-21 VP05 grid-v3 identifiability diagnostic implemented

Added `examples/three_loop_sector203_identifiability_diagnostic.py` and `run_vp05_identifiability_diagnostic.bat` to quantify the degree-3 bivariate polynomial evaluation rank across all 39 grid-v3 training points and the 20-column homogeneous rational-fit kernel rank/nullity for each of the 166 certificate coefficients. The previous comparison showed 72/72 grid-v3 unresolved coefficients were nonunique at (3,3), but did not determine whether polynomial monomial rank was deficient. This new report distinguishes a polynomial-grid rank defect from residual rational representation nonuniqueness, and archives per-row nullities. It does not determine polynomial gcds or prove an exact Q(z,d) identity. No Fermat/Kira; symbolic 20000-cell cap unchanged. Run `git pull` then `.\run_vp05_identifiability_diagnostic.bat`; inspect `VP05_IDENTIFIABILITY_SUMMARY` and `output/three_loop_integral_family_audit/vp05_identifiability_diagnostic.json`.

### 2026-10-21 Critical correction: VP05 nullity zero means degree-(3,3) model infeasible

User's grid-v3 identifiability log: 39 training points at p=1000037, degree=3, monomial evaluation rank=10/10, and 166 rational homogeneous model kernel nullities `{0:72, 1:80, 3:10, 6:3, 10:1}`. Thus **72 rows have a zero-dimensional kernel, i.e. no nonzero (3,3) coefficient pair fits all 39 sampled equations**, NOT a nonunique model. Prior scripts labeled all nullities !=1 as `nonunique`, conflating impossible fits (nullity 0) with genuinely ambiguous fits (nullity >1). Important correction to prior handoff and interpretation: the 72 unresolved rows are incompatible with degree-(3,3) on the 39 sampled points, barring faults in sample/certificate generation. Degree-4+ or different model forms must be examined with sufficient independent samples and a safe bounded algorithm. Full rank of the 10-monomial polynomial evaluation matrix does not by itself prove every rational fit identifiable. Updated identifiability diagnostic output to explicitly count nullity-zero coefficients in commit `7d6a646`. Fermat/Kira not run; no exact Q(z,d) identity proof or integral alias proof.

### 2026-10-21 VP05 rational higher-degree sampling budget preflight

Added `examples/three_loop_sector203_high_degree_budget.py` and `run_vp05_high_degree_budget.bat`. The user-confirmed 39 training + 8 holdout finite-field sample archive yielded a (3,3) homogeneous kernel dimension of zero for 72 certificate coefficients (an infeasible sampled ansatz, not nonuniqueness). The new read-only preflight tabulates degree pairs from (3,3) to (6,6), projective polynomial coefficient counts, generic minimum extra training points beyond 39, and polynomial evaluation matrix ranks for both numerator and denominator. For equal-degree pairs, theoretical coefficient counts: (3,3)=19; (4,4)=29; (5,5)=41 (at least 2 more training points); (6,6)=55 (at least 16 more). These are necessary generic counts, NOT sufficient conditions and do not prove any certificate coefficient exists in a model. Holdouts stay reserved; no Fermat/Kira or exact rational proof. Next local:
```powershell
git pull
.\run_vp05_high_degree_budget.bat
```
Inspect `VP05_HIGH_DEGREE_BUDGET_MODEL` and `VP05_HIGH_DEGREE_BUDGET_SUMMARY` before degree growth/sampling choices.

### 2026-10-21 VP05 degree-(4,4) finite-field trial

User's high-degree budget preflight on grid-v3: 39 training, 8 reserved holdouts; polynomial evaluation ranks full for (3,3):10/10, (4,4):15/15, (5,5):21/21, (6,6):28/28. Projective coefficient counts 19,29,41,55 respectively; (4,4) is point-count feasible with 39 training, (5,5) and (6,6) need at least 2 and 16 extra generically. Added `examples/three_loop_sector203_certificate_degree4_trial.py` and `run_vp05_certificate_degree4_trial.bat` to test only the 72 v3-unresolved components with separate (4,4) numerator/denominator degree bounds, require a unique nonzero finite-field kernel solution and check all 8 holdouts; preserve the original 94 prior verified finite-field candidates in the accounting. Output `output/three_loop_integral_family_audit/vp05_certificate_degree4_trial.json`. This is strictly modular feasibility, not proof of exact Q(z,d) coefficients, and no Fermat/Kira. Run `git pull` then `.\run_vp05_certificate_degree4_trial.bat`, inspect `VP05_DEGREE4_TRIAL`.

### 2026-10-21 VP05 degree-(4,4) finite-field trial local result

User ran `run_vp05_certificate_degree4_trial.bat` with p=1000037, 39 training and the original 8 held-out evaluation points. Targeted 72 v3-unresolved coefficients; `holdout_pass=19`, `nonunique=53` (the fitter's legacy generic label for any nullity !=1, including nullity zero), no reported holdout failures. Previously 94 lower-degree fits passed; combined provisional finite-field candidates =113/166, unresolved=53. Source grid-v3 SHA256 `26d9a35f3d2578bc3231395fe724e540d979657ea3c29d4d2f4926bd93248929`. Next must report exact nullity histogram (0 vs >1) for the 53 and avoid blindly increasing degree; also watch for 39-point grid effects. No Fermat/Kira, exact Q(z,d) proof=false, aliases unresolved.

### 2026-10-21 VP05 degree-(4,4) kernel nullity diagnostic

Following user result 19 degree-(4,4) holdout passes and 53 legacy `nonunique` statuses (113 combined provisional passes), added `examples/three_loop_sector203_degree4_kernel_diagnostic.py` and `run_vp05_degree4_kernel_diagnostic.bat`. They reuse 39 grid-v3 training samples, verify digest against the saved degree-4 trial, and compute homogeneous rank/nullity for each of the 72 attempted rows at exactly (4,4). Distinguish nullity=0/no nonzero fit, nullity=1/projectively unique, and nullity>1/representation nonunique; verify status consistency with original trial and output per-row details and histogram. No extra modular sample generation or Fermat/Kira, no Q(z,d) proof. Next run `git pull`, `.\run_vp05_degree4_kernel_diagnostic.bat` and inspect `VP05_DEGREE4_KERNEL_DIAGNOSTIC`.

### 2026-10-21 VP05 degree-(4,4) kernel diagnosis completed locally

User reran corrected `run_vp05_degree4_kernel_diagnostic.bat`. At prime=1000037 with 39 training points and original 8 held-out points, among 72 degree-(4,4) tested coefficients: homogeneous kernel nullity 0 for **53** (`no_nonzero_fit`), nullity 1 for **19** (`projectively_unique`), and nullity >1 for **0**. Grid-v3 digest `26d9a35f3d2578bc3231395fe724e540d979657ea3c29d4d2f4926bd93248929`. The 19 unique candidates also previously passed held-out finite-field evaluation, so overall provisional 113/166 holdout-passing candidates, 53 unresolved at (4,4). The failure is degree-bounded incompatibility on sampled data, not representation ambiguity. Next prepare extra independent same-prime training samples while keeping eight original holdouts untouched, then test (5,5), with at least 41 projective coefficients and sufficient surplus training points for stability. No exact rational proof, no Fermat/Kira.

### 2026-10-21 VP05 grid-v4 63-point training and degree-(5,5) trial implemented

After p=1000037 degree-(4,4) diagnostics confirmed 53/72 targeted rows have zero-dimensional kernel (model infeasible), the next bounded workflow is implemented. Parameterized `examples/three_loop_sector203_certificate_extend_training.py` for user-selected shifted lattice. Added `run_vp05_certificate_degree5_grid_v4.bat`: reads grid-v3 39 training plus untouched 8 holdouts, generates and fully replays 24 additional valid same-prime evaluations on a distinct 11-column lattice (`z=31+43*(i%11), d=59+71*(i//11)`), writes separate grid-v4 file with 63 training + 8 held-out points, then runs `examples/three_loop_sector203_certificate_degree5_trial.py`. The latter checks archive lineage/SHA256 and v3 sample identity, revalidates **all 113** prior degree<=4 held-out-passing candidates on the **new 24 training points** (some may be invalidated), and attempts (5,5) rational interpolation only for the 53 prior unresolved rows against 63 training points with the 8 holdouts reserved. It reports both newly passing and invalidated previous fits: do NOT add 53 trial passes to 113 without checking `combined_validated_pass`. No Fermat/Kira or exact Q(z,d) proof. User has not yet run grid-v4. Next `git pull`, `.\run_vp05_certificate_degree5_grid_v4.bat`; inspect `VP05_TRAIN_EXTEND_SUMMARY` and `VP05_DEGREE5_TRIAL`.

### 2026-10-21 VP05 grid-v4 degree-(5,5) local result: 158/166

User ran `run_vp05_certificate_degree5_grid_v4.bat`: 24 new same-prime training evaluations accepted without rejection; 63 total training, eight original holdouts preserved, grid-v4 sample digest `2cb2f161788bc18b554601dddb96536d550d058c8156d38b4665f60f54586481`. All **113/113** earlier degree<=4 passing candidates held on the 24 new training points (invalidated=0). Of the remaining 53, the degree-(5,5) trial passed all eight holdouts for **45**, with **8** legacy `nonunique` statuses, giving **158/166** currently valid finite-field candidates and eight unresolved. Still no exact rational reconstruction or symbolic proof. Crucially, the fitter's status `nonunique` covers **both nullity=0 (no fit) and nullity>1 (ambiguous)**; classify the last eight by computing their homogeneous kernel ranks/nullities at degree-(5,5), before choosing next degree or more samples. p=1000037; Fermat/Kira not executed.

### 2026-10-21 VP05 eight-residual degree5 kernel classification and degree6 trial

After grid-v4 degree-(5,5) gave 45 new holdout passes and preserved all 113 prior candidates, 158/166 finite-field models pass, with eight residual legacy `nonunique` statuses. Added `examples/three_loop_sector203_certificate_degree6_residual.py` and `run_vp05_certificate_degree6_residual.bat`. Reuses exactly 63 training and eight held-out same-prime points, checks the saved degree5 trial archive SHA256, recomputes (5,5) homogeneous kernel nullity for each of the eight, and **only for nullity-zero rows** computes degree-(6,6) kernel rank/nullity and fits/validates a unique degree6 candidate if found. Reports per-row nullities and new holdout-passing count; does not generate samples or run Fermat/Kira, and no exact rational reconstruction/proof. User run: `git pull`, `.\run_vp05_certificate_degree6_residual.bat`; review `VP05_DEGREE6_RESIDUAL_SUMMARY` and `output/three_loop_integral_family_audit/vp05_certificate_degree6_residual_trial.json`.

### 2026-10-21 VP05 finite-field certificate interpolation covers all 166 coefficients

User ran `run_vp05_certificate_degree6_residual.bat` using 63 grid-v4 training points and eight untouched held-out points at p=1000037, archive SHA256 `2cb2f161788bc18b554601dddb96536d550d058c8156d38b4665f60f54586481`. All eight previously unresolved degree-(5,5) components have kernel nullity zero at (5,5), kernel nullity one at (6,6), and passed all eight finite-field holdouts. `degree6_new_pass=8`, `combined_provisional_pass=166`: all 166 compressed-row certificate coefficient functions now have finite-field hypotheses: 94 from adaptive degree<=3, 19 at (4,4), 45 at (5,5), eight at (6,6). Prior 113 candidate models passed all 24 additional grid-v4 evaluations. **This is NOT an exact rational-function reconstruction or symbolic proof of the original 528 IBP equations.** Next prioritize certificate model aggregation and independent additional primes/points, then rational reconstruction and exact compressed/original equation replay. Preserve 20,000-cell Fermat safety cap; no Fermat/Kira execution.

### 2026-10-21 VP05 166 coefficient finite-field certificate assembly

With 166/166 degree<=6 coefficient models passed the eight held-out same-prime evaluations, added `examples/three_loop_sector203_modular_certificate_assemble.py` and `run_vp05_modular_certificate_assemble.bat` to integrate archived model outputs (adaptive degree<=3:94, degree4:19, degree5:45, degree6:8) into one deterministic JSON mapping compressed row IDs 0..165 to numerator/denominator finite-field coefficient vectors. The assembler validates archived SHA256 links to grid-v3/v4, preservation of every original sample, unique model ownership of every row, and **replays every candidate at all 71 grid-v4 points** (63 training + eight heldouts), including denominator nonzero and exact sampled certificate value match. It writes `output/three_loop_integral_family_audit/vp05_modular_certificate_assembled.json` only after complete replay. Note: this remains a single-prime modular certificate model, not an exact rational lift or IBP symbolic identity. Run `git pull`, `.\run_vp05_modular_certificate_assemble.bat`. Next step independent new-prime checks, then rational reconstruction and original 528-equation replay; no Fermat/Kira and 20,000-cell cap unchanged.

### 2026-10-21 VP05 assembled modular certificate local success

User ran `run_vp05_modular_certificate_assemble.bat`; `VP05_MODULAR_CERTIFICATE_ASSEMBLY` reported p=1000037, 166/166 coefficient models, 63 training samples and all 8 heldouts replayed, `complete_sample_replay_passed=true`, origin histogram adaptive=94, degree4=19, degree5=45, degree6=8. Equations SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`, samples SHA256 `2cb2f161788bc18b554601dddb96536d550d058c8156d38b4665f60f54586481`. The four input artifact digests were also recorded in the assembled output. Local output: `output/three_loop_integral_family_audit/vp05_modular_certificate_assembled.json`. This is a complete **single-prime finite-field replay**, not an exact characteristic-zero certificate or proof for all symbolic kinematics and not yet validated against original 528 IBP equations. Do not naively substitute coefficient residues from p=1000037 into a different prime. Next: independent-prime sample and fit, rational lift/reconstruction (multiple primes if necessary), and exact row replay, preserving 20000-cell Fermat cap.

### 2026-10-21 VP05 independent-prime coefficient refit implemented

After the user reported full 166/166 assembled certificate sample replay at p=1000037 (63 training + 8 holdouts), added `examples/three_loop_sector203_independent_prime_certificate.py` and `run_vp05_independent_prime_certificate.bat`. This bounded test reads the local compressed 166-equation archive and the assembled certificate, verifies source SHA256, and uses a different prime p=1001003 for independently replayed modular IBP certificates on 70 training points plus 10 untouched holdouts from a new 13-column two-variable lattice. It re-solves each of 166 rational models using ONLY the original numerator and denominator degree bounds (does not transfer coefficients between primes), and separately checks 10 holdouts. Output is `output/three_loop_integral_family_audit/vp05_independent_prime_certificate.json` with individual fits, statuses, fresh sample checks and provenance. WARNING: with 70 training points all 166 models can be evaluated, but special-prime behavior and fitted-model nonuniqueness are possible; this is not cross-characteristic-zero proof and rational lifting remains pending. User has not yet run the new batch. Next local: `git pull`, `.\run_vp05_independent_prime_certificate.bat`. No Fermat/Kira; 20,000-cell exact-symbolic safety cap unchanged.

### 2026-10-21 VP05 independent prime p=1001003 result and residual audit

User ran `run_vp05_independent_prime_certificate.bat`: all 80 sample points accepted (70 training + 10 holdouts, rejected=0), 166 certificate coefficient models independently refitted by their original degree pairs at p=1001003. **158** passed all 10 held-out samples and **8** returned the legacy `nonunique` status; original model was 166/166 passes at p=1000037. Re-evaluation from fresh independent-prime modular IBP rows is stronger evidence but not rational lift or exact Q(z,d) proof. Added `examples/three_loop_sector203_independent_prime_residual_audit.py` and `run_vp05_independent_prime_residual_audit.bat` to inspect saved failed row IDs, degrees and kernel nullities (zero-vs-multiple) without recomputing the 80 expensive sample certificates. Local follow-up: `git pull`; `.\run_vp05_independent_prime_residual_audit.bat`. No Fermat/Kira; symbolic 20000-cell cap remains.

### 2026-10-21 VP05 second-prime degree6 residuals are ambiguous, not infeasible

User ran `run_vp05_independent_prime_residual_audit.bat` at p=1001003 (70 training, 10 holdouts). Exactly eight unpassed rows, IDs `[21,32,44,91,92,110,113,153]`, all using original degree pair `(6,6)` and all categorized `nonunique_representation` (homogeneous kernel nullity >1), **none** nullity=0. The other 158/166 degree-specific models passed holdouts; first-prime complete 166/166 modular replay remains intact. Residual-audit source SHA256 `412ab9e2e9bb3692549c265b75c105387330aa4575eef834003cbad8c38e90f0`. Interpret properly: this is ambiguous coefficient representation under the second-prime training design, not evidence that the rational functions fail to exist. Next diagnose exact nullity per row and whether multiple kernel vectors yield identical rational values on reserved validation points (cross-products or sampled values), then choose an independent training geometry / normalization if needed; never force a random kernel vector to pass. Single or two-prime modular evidence does not equal characteristic-zero proof. No Fermat/Kira.

### 2026-10-21 VP05 second-prime 8-row functional ambiguity test

After p=1001003 independent-prime audit found eight degree-(6,6) rows `[21,32,44,91,92,110,113,153]` with nonunique rational coefficient representation, implemented `examples/three_loop_sector203_second_prime_functional_ambiguity.py` and `run_vp05_second_prime_functional_ambiguity.bat`. Prior independent-prime output omitted raw 80 sampled coefficient vectors, so this script deterministically reevaluates the original 13-column lattice at 70 training + 10 holdout positions, checks rank=166 and certificate replay at every point, and then computes the full homogeneous nullspace basis for each residual row. At each reserved holdout it tests whether the numerator/denominator evaluation linear forms agree with the observed coefficient value for **every basis vector**, and whether any denominator is nonzero. Reports rowwise kernel dimension and number of functionally forced heldouts. This is a finite-field identifiability diagnostic, not a characteristic-zero rational function proof; a successful check does not select a unique polynomial representation. Command `git pull` then `.\run_vp05_second_prime_functional_ambiguity.bat`. This step redoes 80 modular certificate calculations, without Fermat/Kira; original 20,000-cell exact symbolic cap unchanged.

### 2026-10-21 VP05 second-prime degree6 ambiguity traced to grid geometry

User ran `run_vp05_second_prime_functional_ambiguity.bat`; 80 independently re-evaluated modular certificates, all eight residual degree-(6,6) coefficient rows (`21,32,44,91,92,110,113,153`) reported `training_nullspace_not_function_fixed` at held-out points. Key structural issue: original second-prime lattice uses **13 columns** and 70 training points, giving only **six distinct d-coordinates** (`i//13=0..5`). The nonzero degree-six polynomial `prod_{j=0}^{5}(d-(83+79*j))` vanishes identically at all training points, so polynomial evaluation itself has a null direction and any degree-(6,6) numerator/denominator fit can acquire spurious null vectors. Thus the observed ambiguity is consistent with grid geometry, not yet evidence of true rational-function ambiguity. Updated `examples/three_loop_sector203_independent_prime_certificate.py` to parameterize `--columns`, default 9 and reject training lattices with fewer than seven d-levels. Added `run_vp05_independent_prime_grid9.bat` for a fresh p=1001003 refit using a **9-column lattice** (70 training points sample eight distinct d-levels), with a separate result JSON. Original 13-column result remains untouched. Next user: `git pull`, `.\run_vp05_independent_prime_grid9.bat`; inspect `VP05_INDEPENDENT_PRIME_SUMMARY`. No characteristic-zero proof or Fermat/Kira.

### 2026-10-21 VP05 second-prime grid9: 161/166; degree-six geometry audit added

User ran corrected 9-column second-prime p=1001003 test: 70 training + 10 holdouts, 80 valid points, rejected=0, `holdout_pass=161`, legacy `nonunique=5`, versus 158/166 for original 13-column arrangement. Equations SHA256 unchanged `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. This supports a grid-geometry explanation for at least some ambiguity, but five rows remain unresolved; cannot conclude 166/166 at the second prime. Added `examples/three_loop_sector203_grid9_rank_audit.py` and `run_vp05_independent_prime_grid9_rank_audit.bat`: using the 9-column point coordinates and the saved fit output, computes degree-six polynomial monomial rank (28 basis terms), and reports the exact five residual row IDs, original degree pairs and kernel nullities (0/no nonzero fit vs >1/nonunique). No expensive modular IBP rerun; no Fermat/Kira and no exact proof. Run `git pull` then `.\run_vp05_independent_prime_grid9_rank_audit.bat`, inspect `VP05_GRID9_RANK_AUDIT`.

### 2026-10-21 VP05 grid9 rank audit: 5 residual degree6 models have nullity 4

User ran `run_vp05_independent_prime_grid9_rank_audit.bat` at p=1001003: with 70 training and 10 holdouts on the 9-column grid, degree-six polynomial monomial evaluation rank **28/28** (nullity=0). The second-prime candidate tally is 161/166 holdout passes. Five residual rows `[21,32,44,110,113]` all have homogeneous rational (6,6) coefficient kernel nullity **4**, classified as nonunique representations, not zero-kernel/infeasible models. Audit source SHA256 `46062a682548194135c9882017d85caf478a92adc005974fcd6aba13190d8367`. The polynomial grid has no degree-six monomial deficiency; however, a full polynomial rank does not guarantee the rational kernel is one-dimensional. Next inspect the 4D rational nullspace and its possible common polynomial factors and/or further sample identifiability. Do not assert an exact rational identity or 166/166 second-prime result yet; Fermat/Kira unused.

### 2026-10-21 VP05 five-row second-prime kernel factor audit implementation

With the 9-column grid at p=1001003 giving monomial degree-six rank 28/28 but five residual rows `[21,32,44,110,113]` with homogeneous kernel dimension four, added `examples/three_loop_sector203_grid9_kernel_factor_audit.py` and `run_vp05_grid9_kernel_factor_audit.bat`. Since the earlier independent-prime trial did not retain raw sample certificates, this tool deterministically recomputes the original 70 training + 10 holdout points and replays modular certificate rank=166, then constructs all four rational-kernel basis vectors for each of five rows, computes polynomial numerator/denominator gcd degrees over F_1001003 for every nonzero-denominator basis vector, and checks whether the entire training nullspace forces observed values at all ten holdouts. Important limitation: gcd of separate basis vectors is not proof of one unique reduced rational function; report explicitly qualifies this. No exact Q(z,d) reconstruction; no Fermat/Kira. Run `git pull` then `.\run_vp05_grid9_kernel_factor_audit.bat`, inspect `VP05_GRID9_FACTOR_AUDIT` and JSON `output/three_loop_integral_family_audit/vp05_grid9_kernel_factor_audit.json`.

### 2026-10-21 VP05 second-prime grid9 GCD summary next step

User's grid9 kernel-factor audit: five residual rows 21,32,44,110,113 have nullity four and all ten independent-prime holdout values are forced by their training nullspaces. This confirms sampled-value agreement for all 166 rows at the second prime, but not uniqueness as rational functions or exact symbolic proof. Added `examples/three_loop_sector203_grid9_gcd_summary.py` and `run_vp05_grid9_gcd_summary.bat` to report actual numerator/denominator gcd degrees and reduced degree pairs for each of the 20 stored basis vectors from the previous JSON without repeating 80 modular calculations. This does not construct canonical rational functions or lift coefficients to Q. Run `git pull` and `.\run_vp05_grid9_gcd_summary.bat`. Next review resulting degree distributions before attempting normalized cross-prime model reconciliation. No Fermat/Kira.

### 2026-10-21 VP05 five-row basis GCD summary observed

User ran `run_vp05_grid9_gcd_summary.bat` for five second-prime residual rows `[21,32,44,110,113]`. Each row has four nullspace basis vectors with gcd-degree histogram `{0:3, 1:1}`; across 20 basis vectors, 15 are coprime pairs and five have a linear numerator/denominator common factor. In **each** row, the stored basis-vector numerator/denominator degree pairs after reduction are `(6,4),(6,5),(5,5),(6,6)`. Factor-audit digest `6041b1bf12542ecc1c754aa1bd2a8f2155ac2c01db91f5e248a6cad1b7498395`. This proves only the gcd properties of *chosen nullspace basis vectors*, not that they determine one canonical reduced rational function. Next compare reduced rational fractions of the basis vectors by exact polynomial cross-multiplication over F_1001003 and characterize combinations; do not assume basis vectors represent identical functions from 10 holdouts alone. No Q(z,d) lift or symbolic proof; no Fermat/Kira.

### 2026-10-21 VP05 second-prime rational cross-product identity audit

The five ambiguous grid9 second-prime coefficient rows `[21,32,44,110,113]` each have a four-dimensional homogeneous kernel and basis-vector gcd pattern `{0:3,1:1}`. Added `examples/three_loop_sector203_grid9_kernel_cross_product.py` and `run_vp05_grid9_kernel_cross_product.bat` to compute the 4 basis vectors from the 70 training sample modular certificates and compare all six basis pairs per row as **polynomial identities in F_1001003[z,d]** by checking `P_i Q_j - P_j Q_i == 0` (30 cross-products total), rather than merely agreeing at 10 holdouts. Per-pair results include degree and term count when nonzero. Refuses basis vectors with identically zero denominators. This audit does not prove characteristic-zero rational identities or original 528-row IBP equations. Run `git pull`, `.\run_vp05_grid9_kernel_cross_product.bat`; inspect `VP05_GRID9_CROSS_PRODUCT`. No Fermat/Kira.

### 2026-10-21 VP05 grid9 cross-product audit: 30/30 distinct

User ran `run_vp05_grid9_kernel_cross_product.bat`: 70 training modular certificate samples successfully replayed at p=1001003. For five residual degree-(6,6) coefficient rows `[21,32,44,110,113]`, each 4D homogeneous kernel was analyzed; **all 30 pairwise polynomial cross-products** `P_i Q_j - P_j Q_i` were nonzero in F_p[z,d]. Therefore the *chosen four nullspace basis fractions* represent different rational functions, despite their agreement with observations at all ten holdout points. This establishes genuine finite-field global ambiguity of the interpolation under current sample constraints; individual basis GCD reduction is insufficient. Next add further genuinely new off-grid training points, retain previous holdouts and inspect kernel nullity drop; no exact characteristic-zero or 528 original IBP proof, no Fermat/Kira.

### 2026-10-21 VP05 five residual kernels: off-grid sampling implemented

After 30/30 pairwise cross-products of degree-(6,6) kernel basis rational functions were nonzero at p=1001003, added `examples/three_loop_sector203_grid9_offgrid_kernel_shrink.py` and `run_vp05_grid9_offgrid_kernel_shrink.bat`. The bounded workflow replays the original 70 grid9 training + 10 reserved holdout modular certificates (rank=166, replay checked), collects 12 new off-grid independent training points with a shifted polynomial coordinate sequence, and reports nullity changes of the five ambiguous compressed-certificate rows `[21,32,44,110,113]` after each addition. If a row's nullity falls to one, it runs degree-(6,6) fitting against all 82 training samples and checks the original ten holdouts; otherwise reports zero-kernel or residual ambiguity. Output is a new JSON with per-point nullities and per-row status. No original holdout is trained on. No Fermat/Kira or characteristic-zero proof. Next local: `git pull`, `.\run_vp05_grid9_offgrid_kernel_shrink.bat`; inspect `VP05_OFFGRID_KERNEL_SHRINK`. Do not claim second-prime 166 unique coefficient models before this succeeds.

### 2026-10-21 VP05 second prime reaches 166/166 projectively unique modular fits

User ran `run_vp05_grid9_offgrid_kernel_shrink.bat`: the 80 original p=1001003 grid9 certificate evaluations replayed; 12 new off-grid training points accepted (rejected=0), original ten holdouts untouched. For residual coefficient rows `[21,32,44,110,113]` all (6,6) kernel nullities fell from 4 to **1 after just three new points**, remained 1 through twelve, and all five resulting unique candidates passed ten holdouts. Thus the second-prime account is 161 originally unique passing models plus five recovered passing models = **166/166**; first prime p=1000037 had already passed 166/166. Equations SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`, grid9 trial digest `46062a682548194135c9882017d85caf478a92adc005974fcd6aba13190d8367`. Local result: `output/three_loop_integral_family_audit/vp05_grid9_offgrid_kernel_shrink.json`. This is excellent independent modular evidence but not a cross-prime coefficient normalization, rational lift to Q(z,d), or exact original 528-row IBP replay; Fermat/Kira not run and 20,000-cell symbolic cap retained. Next aggregate second-prime 161 base fits and five recovered models, then compare canonical degree/scaling, pursue CRT/rational lifting and exact symbolic replay.

### 2026-10-21 VP05 two-prime coefficient model alignment

User's `run_vp05_grid9_offgrid_kernel_shrink.bat` completed at p=1001003: for five residual rows `[21,32,44,110,113]`, 12 additional off-grid training points reduced all homogeneous rational nullities from four to one (by the first three points), and all five uniquely refitted (6,6) models passed ten original untouched holdouts. Therefore each of two primes p=1000037 and p=1001003 now has 166/166 individually holdout-passing projectively unique rational coefficient candidates. Added `examples/three_loop_sector203_two_prime_model_alignment.py` and `run_vp05_two_prime_model_alignment.bat` to assemble 161 second-prime grid9 models plus five independently recovered offgrid models, verify hash lineage and 166 distinct row IDs, normalize each rational numerator/denominator projectively by a deterministic nonzero denominator coefficient, and compare degrees/pivot indices with first-prime assembled models. Stores normalized coefficient arrays and provenance in `output/three_loop_integral_family_audit/vp05_two_prime_model_alignment.json`. A common projective pivot permits coordinatewise CRT at subsequent stages; it does not itself prove a characteristic-zero rational model. No Fermat/Kira or full original IBP replay. Run `git pull` and `.\run_vp05_two_prime_model_alignment.bat`; inspect `VP05_TWO_PRIME_MODEL_ALIGNMENT` and pivot mismatch count.

### 2026-10-21 VP05 all 166 cross-prime pivots aligned; CRT feasibility audit implemented

User ran `run_vp05_two_prime_model_alignment.bat`, confirming 166/166 model rows have `common_projective_pivot` across p=1000037 and p=1001003 (zero mismatches); the second-prime models comprise 161 grid9 fits plus five offgrid recoveries. The coefficient alignment file is local `output/three_loop_integral_family_audit/vp05_two_prime_model_alignment.json`; SHA256 sources: first `7a6fd29100a01e938e54df3ab89bc725a2a429ed26a9edcf9516f64d4f561e7b`, second `46062a682548194135c9882017d85caf478a92adc005974fcd6aba13190d8367`, offgrid `dedc4ae1179dc24ac4b8a15bab44befa5413c6db52e8e23818cff086ed0e09df`. Added `examples/three_loop_sector203_two_prime_crt_audit.py` and `run_vp05_two_prime_crt_audit.bat`, performing coefficientwise CRT and bounded rational reconstruction with bound `floor(sqrt((p*q-1)/2))` for 166 aligned normalized rational model pairs, always checking both prime residues and coprime numerator/denominator. It counts recoverable vs unresolved coefficients and complete vs incomplete rows; results are *tentative only* and do not prove coefficient heights or any characteristic-zero rational function. No original IBP replay or Fermat/Kira. Run `git pull`, `.\run_vp05_two_prime_crt_audit.bat`; inspect `VP05_TWO_PRIME_CRT_AUDIT`.

### 2026-10-21 VP05 two-prime CRT audit and independent third-prime test

User ran `run_vp05_two_prime_crt_audit.bat`: the two-prime product is `1001040037111`; all 4251 coefficient positions returned bounded rational candidates and all 166 normalized row models were complete, audit alignment SHA256 `2deda5f48839d27add3b03b0e3c373dd6092580e738757be63fe047bcf4f4511`. Critically, this does **not** establish true characteristic-zero coefficients: modular reconstruction within a generous bound may return spurious rationals. Implemented `examples/three_loop_sector203_crt_third_prime_check.py` and `run_vp05_crt_third_prime_check.bat` for a fresh prime p=1001107 at three off-grid (z,d) points, with independent compressed-IBP rank/replay-verified modular dual certificate generation and predictions from all 166 rational candidate P/Q. Outputs rowwise mismatches and undefined denominators, and only declares success if all 498 comparisons match. New work has NOT yet run locally. Next `git pull`, `.\run_vp05_crt_third_prime_check.bat`, review `VP05_CRT_THIRD_PRIME_SUMMARY`. No Fermat/Kira, no exact Q(z,d) identity, original 528-row proof unresolved.

### 2026-10-21 VP05 CRT reconstruction candidates pass third-prime holdout

User ran `run_vp05_crt_third_prime_check.bat` at independent p=1001107. The fresh points `(z,d)=(301,503),(409,651),(539,833)` each gave 166 matches, zero mismatches and zero undefined denominator results. Total **498/498 coefficient-value comparisons passed**, with fresh rank/replay-verified compressed IBP certificates at the third prime. Source CRT audit SHA256 `0a9072d4c216d396a9973205588edef4725fe15347d33b2916e31e129ce63600`; equations SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. This is a significant independent finite-field confirmation of 4251 tentative coefficient rationals for 166 functions, not an exact identity over Q(z,d) or original 528-row proof. Next execute deterministic exact rational-function identity against the 166 compressed symbolic equations, with explicit resource limits and hash provenance, before labeling an exact IBP proof. Fermat/Kira have not run.

### 2026-10-21 VP05 exact compressed-certificate symbolic pilot

The independently tested p=1001107 third-prime CRT validation returned 498/498 coefficient-value matches across three points with no undefined predictions (third-prime CRT SHA256 `0a9072d4c216d396a9973205588edef4725fe15347d33b2916e31e129ce63600`). Added `examples/three_loop_sector203_exact_compressed_certificate_replay.py` and `run_vp05_exact_compressed_certificate_pilot.bat` as the next *strict* step. This bounded pilot constructs the 166 reconstructed Q(z,d) candidate certificate functions, then computes exact `target - sum_r certificate_r * compressed_equation_r` independently column-by-column using SymPy rational arithmetic. Each column is marked `exact_zero` only when the exact symbolic numerator is identically zero; `exact_nonzero` and `inconclusive` are separate statuses. Default pilot checks five lightest-incidence columns, keeps a 20000 source-input-term cap, writes per-column results and provenance, and **never claims a full proof until all compressed columns are checked and exactly zero**. The per-column clock guard checks elapsed time after evaluation rather than forcibly interrupting SymPy, so treat it as a retrospective performance gate, not a hard timeout. This does NOT replay all original 528 equations or establish the integral alias mapping. No Fermat/Kira. Next run `git pull`, `.\run_vp05_exact_compressed_certificate_pilot.bat`; inspect `VP05_EXACT_COMPRESSED_REPLAY`.

### 2026-10-21 VP05 first five exact compressed-column identity checks passed

User ran `run_vp05_exact_compressed_certificate_pilot.bat`: five lightest-incidence compressed columns each yielded SymPy exact `exact_zero`, with timings 0.013, 0.006, 0.033, 0.012 and 0.027 seconds; no nonzero or inconclusive results. Source contains 166 compressed rows, 400 columns and 1985 equation terms. CRT SHA256 `0a9072d4c216d396a9973205588edef4725fe15347d33b2916e31e129ce63600`, compressed equations SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. Only **5/400** columns have exact proof so far; remaining 395 untested. All five tested columns have only two input equation terms; do not extrapolate execution times to high-incidence columns. Next perform incremental larger bounded exact replay, stopping on any nonzero or resource limit. Full 528 original-row and integral alias verification remain pending. No Fermat/Kira.

### 2026-10-21 VP05 50-column exact compressed-certificate replay

User uploaded the output log from `python -m examples.three_loop_sector203_exact_compressed_certificate_replay --max-columns 50 --max-input-terms 20000`. All **50/50** selected columns returned `exact_zero`; zero `exact_nonzero` and zero `inconclusive`. The 50th column `(6,203)` has three input equation terms; first 49 have two. These exact SymPy checks cover **50 of 400 compressed integral columns (12.5%)**; 350 remain unverified. The compressed source contains 166 rows and 1985 input terms. Source CRT SHA256 `0a9072d4c216d396a9973205588edef4725fe15347d33b2916e31e129ce63600` and equations SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. `exact_compressed_certificate_verified=false`, original-528 replay and integral-alias mapping remain unchecked; no Fermat/Kira. Next use staged 100/200/400 column replay while monitoring the per-column retrospective runtime guard; avoid assuming heavy columns perform like incidence-2 columns.

### 2026-10-21 VP05 100/400 exact compressed-column replay

User uploaded log from `python -m examples.three_loop_sector203_exact_compressed_certificate_replay --max-columns 100 --max-input-terms 20000`. Result: **100 `exact_zero`**, zero `exact_nonzero`, zero `inconclusive`. All 100 checked columns have incidence 2 or 3, and maximum reported per-column duration is about 0.122 seconds. 300/400 columns remain unchecked. Input: 166 compressed rows, 1985 equation terms; CRT SHA256 `0a9072d4c216d396a9973205588edef4725fe15347d33b2916e31e129ce63600`, equation SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. `exact_compressed_certificate_verified=false`; original 528 equation replay and integral alias mapping unverified. Next trial `--max-columns 200 --max-input-terms 20000` and inspect exact statuses before increasing further. No Fermat/Kira.

### 2026-10-21 VP05 200/400 exact compressed-certificate replay

User uploaded exact replay log for `--max-columns 200 --max-input-terms 20000`. Result: **200/200 `exact_zero`**, zero `exact_nonzero`, zero `inconclusive`; checked columns include incidence four. Remaining 200 compressed integral columns are not yet checked. Input still 166 rows, 400 columns, 1985 terms; CRT SHA256 `0a9072d4c216d396a9973205588edef4725fe15347d33b2916e31e129ce63600`, equation SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. `exact_compressed_certificate_verified=false` is correct until all 400 columns pass; original 528-equation replay and integral alias mapping remain pending. Next trial `--max-columns 400 --max-input-terms 20000`, being aware that high-incidence columns may be much costlier and the per-column duration guard is retrospective, not an interrupt. No Fermat/Kira.

### 2026-10-21 VP05 full exact compressed replay

User's 400-column run reports `exact_zero=400`, `exact_compressed_certificate_verified=true`, no nonzero or inconclusive columns. There are 166 compressed equations and 1985 input terms. The reconstructed rational certificate is established over Q(z,d) for the compressed equation system. Remaining: original 528-row lineage and integral alias mapping. Neither Fermat nor Kira was used.

### 2026-10-21 VP05 original-528 exact lineage audit pilot implemented

Following 400/400 exact-zero compressed symbolic certificate replay, added `examples/three_loop_sector203_original_528_exact_lineage_audit.py` and `run_vp05_original_528_exact_lineage_pilot.bat`. The new verifier reads the original 528-row witness path recorded in the compressed archive, the 166 proportional-class weight groups and 166 compressed equations. It first checks disjoint/exhaustive original-row coverage and representative weights, then for selected groups recomputes each weighted original coefficient column, subtracts the saved compressed coefficient and tests the exact residual in Q(z,d) via SymPy. Default five groups, with `--max-groups 166` for all groups if the pilot passes. The global 20,000 input-term cap is retained. This tests algebraic original-row lineage, not integral alias/physical interpretation; Fermat/Kira not run. Run `git pull` and `.\run_vp05_original_528_exact_lineage_pilot.bat`; inspect `VP05_ORIGINAL_528_LINEAGE`.

### 2026-10-21 VP05 original 528-row lineage: first five exact matches

User ran `run_vp05_original_528_exact_lineage_pilot.bat`. Groups 0-4 each returned `exact_match`, comprising respectively 68, 36, 33, 20, and 17 original equations (174 in total) and 258, 129, 76, 63, and 73 inspected integral columns. Complete structural partition of all 528 original rows into 166 disjoint groups passed (`group_partition_exact=true`). Only five groups were verified algebraically; `exact_lineage_verified=false` correctly remains pending 161 groups. Compressed SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`, weights SHA256 `40b06af2af0e3f1763bb703b52196147af042f46a1f88aaef2780326bdaef807`, original source SHA256 `3235c536ee1db51ffb0810c8bc67b6006e11711224a06fca90147b44c8dc7fce`, 3769 original terms. Run `python -m examples.three_loop_sector203_original_528_exact_lineage_audit --max-groups 166 --max-source-terms 20000` for complete exact lineage. Integral alias mapping remains unverified. No Fermat/Kira.

### 2026-10-21 VP05 full exact original-528 lineage verified

User completed `python -m examples.three_loop_sector203_original_528_exact_lineage_audit --max-groups 166 --max-source-terms 20000`. Results: `groups_checked=166`, `group_verdicts={"exact_match":166}`, `group_partition_exact=true`, `exact_lineage_verified=true`; 528 original rows, 166 exact weighted compression groups, 3769 original terms. Original SHA256 `3235c536ee1db51ffb0810c8bc67b6006e11711224a06fca90147b44c8dc7fce`, groups SHA256 `40b06af2af0e3f1763bb703b52196147af042f46a1f88aaef2780326bdaef807`, compressed SHA256 `905d64eb4156b7e332d0445193c851d6a683ef89582df9de0a79612929a3d9fc`. Combined with prior 400/400 exact-zero Q(z,d) compressed certificate, this provides a rigorous algebraic certificate of target membership in the span of the saved original 528 IBP equations, under their current encoded integral labels. The integral alias/weight codec mapping to physical Feynman integrals is still unverified; do NOT present that physical interpretation as proven. No Fermat/Kira executed. Next task: audit codec/alias mapping and archive a machine-verifiable exact 528-row expanded certificate with provenance and compactness checks.

### 2026-10-21 VP05 target weight codec / alias diagnostic implemented

Following `exact_lineage_verified=true` for all 166 groups covering the saved original 528 IBP equations, added `examples/three_loop_sector203_target_codec_alias_audit.py` and `run_vp05_target_codec_alias_audit.bat`. The audit requires the external GPL `pyred_weight.py`, reads the actual Kira project `results/kira.db` (integral ordering 5, topsector 203) and exact compressed input, decodes and re-encodes the three target keys `(10,203),(6,203),(5,201)`, and reports decoded 12-indices, decoded mathematical sectors, original recorded sectors, source presence and round-trip results. Recorded proper-subsector ranks MUST NOT be assumed equal to the physical sector bitmask; comparison is diagnostic. An optional expectation JSON with `targets:[{key:[weight,sector],exponents:[12 integers]}, ...]` enables strict checks against externally justified expected exponents. The audit deliberately leaves `integral_alias_mapping_verified=false` when explicit expected aliases have not been provided. Even expectation-matching only validates weight/exponent mapping, not propagator momentum routing; external integral-family config/topology proof remains necessary. Run `git pull`, then `.\run_vp05_target_codec_alias_audit.bat "C:\path\to\pyred_weight.py"` using the existing external codec. No Fermat/Kira execution.

### 2026-10-21 VP05 target alias audit: codec namespace mismatch

User ran `run_vp05_target_codec_alias_audit.bat` and all three target keys `(10,203),(6,203),(5,201)` were present in compressed equations, but external `WeightCodec.decode` failed: `weight 10: ppw 10 out of range (1 comps)`, likewise 6 and 5. Thus **these first key components must NOT be treated as established Kira weights**. This does not contradict 400/400 exact compressed certificate replay or 166/166 exact original-528 lineage; both proofs operate on internal stored column keys. Added `examples/three_loop_sector203_target_key_namespace_diagnostic.py` and `run_vp05_target_key_namespace_diagnostic.bat` to inspect original witness metadata and ID distributions without using the external codec. Next reconstruct and independently verify the missing mapping between saved witness internal column IDs and physical VP05 12-index integrals before making physical-identity claims. Run `git pull` and `.\run_vp05_target_key_namespace_diagnostic.bat`; inspect `VP05_TARGET_KEY_NAMESPACE`. Original physical alias mapping remains unverified.

### 2026-10-21 VP05 small target key raw SYSTEM provenance

User's witness-namespace diagnostic: 528 saved original equations with 756 distinct column keys, small first components {3,4,5,6,8,10} mixed with very large keys; three target keys `(10,203),(6,203),(5,201)` are present in 29, 7 and 10 saved original rows respectively. The witness JSON has only `scope` metadata, insufficient to interpret small IDs as Kira codec weights. A naive Kira decode of 10,6,5 raises `ppw ... out of range (1 comps)`. Created `examples/three_loop_sector203_target_raw_system_id_audit.py` and `run_vp05_target_raw_system_id_audit.bat` to look for these exact pairs directly in saved raw `SYSTEM_VP05_full_*.gz` files, inspect original token fields and occurrences, and distinguish source transcription from physical exponent interpretation. Run `git pull` then `.\run_vp05_target_raw_system_id_audit.bat`. Prior exact algebraic results 400/400 compressed columns and 166/166 original compression groups remain valid for stored keys; physical alias mapping **not verified**.

### 2026-10-21 VP05 target aliases absent as literal raw SYSTEM keys

User ran `run_vp05_target_raw_system_id_audit.bat`: 14 raw SYSTEM gz files, 3317 equations, 31556 terms; raw occurrence count ZERO for all three target pairs `(10,203),(6,203),(5,201)`, although saved 528-row witness contains 29, 7 and 10 occurrences respectively. The literal key namespace differs or the witness derivation/source set differs; do not equate these keys with physical integral IDs without a verified transform. Exact 400/400 compressed-column identity and 166/166 original-witness lineage are valid algebraically for saved witness data, but source Kira-to-witness provenance is NOT yet established. Next find producer of `vp05_candidate4_witness_*.equations.json`, locate any remapping/column-alias table and verify exact raw-to-export lineage; explicitly avoid claiming physical VP05 identity proven.

### 2026-10-21 Original witness producer search

After the raw SYSTEM audit reported zero literal occurrences for `(10,203),(6,203),(5,201)` among 3317 equations, implemented `examples/three_loop_sector203_witness_producer_trace.py` and `run_vp05_witness_producer_trace.bat`. This diagnostic searches repository sources (excluding generated outputs) for witness exporter code, selected-SYSTEM input paths and row/column conversion logic, listing file/line matches while retaining original SHA256. The diagnostic does not infer a mapping or revise the exact algebraic checks. Next run `git pull` and `.\run_vp05_witness_producer_trace.bat`; review top source candidates to identify whether the witness came from a different project or a transformed namespace, then implement exact raw-SYSTEM provenance validation. Physical alias verification remains pending.

### 2026-10-21 VP05 source-project mismatch resolved; exact SYSTEM replay implemented

The witness producer was identified unambiguously as `examples/three_loop_sector203_l2_witness_subset.py`, whose default original project is `output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734`, containing **2678** SYSTEM equations. Previous raw target-key audit incorrectly inspected the different `r5s6d0` project (3317 SYSTEM equations), so its zero target-key results cannot be used to draw conclusions about the 528-row witness. Producer saves literal `fields[2]`/`fields[3]` directly as column keys, not remapped values. Implemented `examples/three_loop_sector203_original_raw_system_exact_replay.py` and `run_vp05_original_raw_system_exact_replay.bat`: checks all 528 selected row_index records against the exact 2678 original SYSTEM records including file name, equation ID, number/order of terms, raw weight-sector key and coefficient strings. Fail-closed on mismatches, reports target occurrences and SHA256. Run `git pull` then `.\run_vp05_original_raw_system_exact_replay.bat`. If successful, the saved 528-row witness provenance from this raw Kira SYSTEM source is independently established. Physical exponent/propagator mapping still requires independent correct-project codec verification; do not conflate these layers.

### 2026-10-21 VP05 528-row raw SYSTEM replay passed

Correct L2 producer project has 2678 equations in 14 SYSTEM files. The exact transcription replay confirmed all 528 selected rows, all 3769 terms, zero mismatches (`exact_source_transcription_verified=true`). Target key counts in raw source: (10,203)=37, (6,203)=24, (5,201)=51. Selected rows: 29, 7, 10. This completes literal source linkage for the previously verified 166-group compressed and 400-column rational certificate. Correct-project codec/exponent mapping and propagator semantics remain unverified.

### 2026-10-21 Correct-project VP05 target codec audit

Updated `examples/three_loop_sector203_target_codec_alias_audit.py` to use the correct `r6s6d1_truncate_sp_l2` witness-producer project by default (importing `DEFAULT` from `three_loop_sector203_l2_witness_subset`), rather than the unrelated older `r5s6d0` project. Added source guard: exactly 2678 SYSTEM records and all three target keys present in raw terms before attempting database codec decoding. Project provenance to original 528 rows is already exact (528 rows, 3769 terms). The corrected codec audit has **not yet run**; check results after user runs `.\run_vp05_target_codec_alias_audit.bat <external pyred_weight.py path>`. No physical 12-exponent mapping is claimed until codec and explicit topology alignment are verified.

### 2026-10-21 VP05 codec decode still fails with correct L2 SYSTEM project

Correct L2 source has 2678 equations and all three target keys, but `WeightCodec.decode` reports `ppw 10/6/5 out of range (1 comps)` for the three small target integer IDs. Previous and present audit DB SHA256 are both `d63e6452b1c8c6ccdf337719cdcd8312d9c0ff1c06df73dc83286353f1bf56ee`; changing project path therefore did not establish a different codec database. This is a remaining namespace/codec issue, **not** evidence of physical alias decoding. Added `examples/three_loop_sector203_codec_namespace_probe.py` and `run_vp05_codec_namespace_probe.bat` to compare small and large SYSTEM IDs, report database bit metadata and decode/encode results under the same configuration. Next run `git pull` and `.\run_vp05_codec_namespace_probe.bat <path-to-pyred_weight.py>`. Correct-origin 528-row/3769-term transcription, 166/166 compression, and 400/400 certificate remain exact in raw saved key space; physical-integral semantics unverified.

### 2026-10-21 Small-weight codec investigation

The L2 source has 2954 distinct key pairs. A sample of 80 gave 70 successful codec round trips and 10 decoding errors, including target weights 5, 6 and 10. Added `examples/three_loop_sector203_small_weight_diagnostic.py` and `run_vp05_small_weight_diagnostic.bat` to inspect the external codec's decode conditions and the exact use of small IDs in stored SYSTEM records. No physical mapping is claimed yet.

### 2026-10-21 VP05 small-ID versus master-list diagnostic

The small-weight source diagnostic found exactly raw values 1..10 failing the external weight decoder, while larger encoded integral weights often round-trip. The codec reports `ppw out of range (1 comps)` on these small IDs. Added `examples/three_loop_sector203_master_slot_diagnostic.py` and `run_vp05_master_slot_diagnostic.bat` to compare the actual L2 project's `results/VP05_full/masters`, correctly encoded master weights, raw SYSTEM head/term keys, and small-ID range. A matching count is not sufficient to establish which master a small slot denotes. Physical alias mapping remains unverified; previously established raw 528-row transcription and symbolic certificate remain valid.

### 2026-10-21 Small SYSTEM identifier classification

Correct L2 `results/VP05_full/masters` contains 5 masters, while raw SYSTEM features small key IDs 1..10. Therefore small IDs are not simply 1-based positions in this five-item master list. External weight codec cannot decode IDs 1..10, but handles many large integral weights. Added `examples/three_loop_sector203_small_id_provenance_inventory.py` and `run_vp05_small_id_provenance_inventory.bat` to examine saved Kira configuration/results metadata for explicit conventions. Do not equate small IDs to physical integrals without source-supported mapping; algebraic certificate stays verified for raw encoded columns.

### 2026-10-21 VP05 small-ID metadata inventory result

User ran the L2 project metadata inventory. Found only `config/integralfamilies.yaml` (`top_level_sectors: [203]`), `config/kinematics.yaml`, and five-line `results/VP05_full/masters`. No explicit mapping from raw SYSTEM small IDs 1..10 to physical 12-index integrals was established. The search was limited to those candidate files; it is NOT an exhaustive Kira source/database audit. Next investigate SYSTEM output encoding conventions or other source-side metadata rather than assuming master-list ordinal positions. Exact symbolic SYSTEM-row identity remains verified; physical interpretation remains pending.

### 2026-10-21 VP05 Kira database small-ID schema audit

Metadata inventory showed no explicit mapping of raw SYSTEM small IDs 1..10. Added read-only SQLite schema inspection `examples/three_loop_sector203_kiradb_id_schema_audit.py` and `run_vp05_kiradb_id_schema_audit.bat`, targeting the exact L2 `results/kira.db` with `mode=ro` and `PRAGMA query_only=ON`. It lists schema tables/views, columns, and names suggestive of integral/weight/sector/master metadata, but does not guess any numeric mapping. Next run `git pull` and `.\run_vp05_kiradb_id_schema_audit.bat` to determine if schema contains an explicit mapping table. Physical interpretation still unverified, while saved formal certificate remains exact.

### 2026-10-21 VP05 Kira EQUATION samples

Added `examples/three_loop_sector203_kiradb_equation_sample.py` and `run_vp05_kiradb_equation_sample.bat` for read-only bounded inspection of the correct L2 `results/kira.db` EQUATION table. Samples up to 12 records (ID, ARRAYID, AUXILIARY, SECTOR, LENGTH, short coefficient prefix), plus aggregate counts grouped by sector and auxiliary flag. This does not infer mappings; next compare observed record structure with source SYSTEM to investigate small IDs 1..10. Run `git pull`, then `.\run_vp05_kiradb_equation_sample.bat`. Physical integral identification remains unverified; saved symbolic relation remains exact in SYSTEM key namespace.

### 2026-10-21 VP05 small SYSTEM ID source audit

Kira L2 `kira.db` EQUATION table is empty (0 rows). Small raw weights 1..10 remain distinct from the externally decoded large integral weights. Added `examples/three_loop_sector203_small_system_id_source_audit.py` and `run_vp05_small_system_id_source_audit.bat`: bounded read-only inventory of small-ID distribution by saved SYSTEM sector and filenames, plus Kira job/config/results evidence of preferred masters, basis or weight settings. Do not infer any mapping from list positions or numeric proximity. Kira documentation allows explicit user weights and describes distinct enumeration in selected contexts, but those facts do not establish the meaning of this project's IDs. The exact 528-row source lineage and algebraic certificate remain valid; physical integral mapping remains unverified.

### 2026-10-21 VP05 small-ID sector structure and equation-role audit

The L2 SYSTEM diagnostic reports small IDs 1,2,3 restricted to recorded sector 202, ID 4 to 73, ID 5 to 201, and IDs 6..10 to 203, with occurrence counts 34,15,39,150,51,24,21,38,24,37 respectively. These values do not correspond simply to the five entries of `results/VP05_full/masters`. Added `examples/three_loop_sector203_small_id_equation_role_audit.py` and `run_vp05_small_id_equation_role_audit.bat` to analyze per-equation co-occurrence and raw head relationships (read-only, original 2678 SYSTEM rows). This is structural diagnostic evidence only, not a verified mapping to physical integral exponent tuples. Run `git pull`, then `.\run_vp05_small_id_equation_role_audit.bat`. 

### 2026-10-21 VP05 two-term bridges for small IDs

The user-supplied `VP05_SMALL_ID_EQUATION_ROLE` log shows small integral keys 1..10 occur as RHS/SYSTEM term variables but never as equation heads. In particular (5,201) occurs in some two-term rows with one ordinary large encoded weight, including heads 166576011608064 (sector 139) and 166026255794176 (sector 195). These rows can constrain small IDs by exact linear proportionality to large-weight integrals; do **not** assume coefficient=1, uniqueness, or universal equality without checking the coefficients and alternative bridges. Added `examples/three_loop_sector203_small_id_two_term_bridges.py` and `run_vp05_small_id_two_term_bridges.bat` to inspect exact original two-term raw SYSTEM equations, preserving their literal coefficients and equation provenance. Next run `git pull` then `.\run_vp05_small_id_two_term_bridges.bat`. The physical small-ID-to-12-index mapping is still unverified; earlier algebraic certificate in raw SYSTEM columns remains intact.

### 2026-10-21 VP05 exact 2-term alias bridges found

User's two-term SYSTEM bridge output: 357 original two-term equations; small IDs 4 and 5 have bridges, but target IDs 6 and 10 have none. A literal source equation `I_(5,201) - I_(166026255794176,195) = 0` establishes equality inside the saved SYSTEM variable algebra; large key `166026255794176` was previously codec-encoded from `VP05_full[1,0,0,1,0,0,1,1,0,0,0,0]`. Other equalities link ID 5 to different large weights via sector symmetries; these are not necessarily a unique decoded exponent tuple. Added `examples/three_loop_sector203_small_id_exact_alias_bridges.py` and `run_vp05_small_id_exact_alias_bridges.bat` to reparse exact two-term equations and verify unit-sign equality plus Kira decode/encode roundtrips for large integral keys. It does not assume different but equal integral exponent tuples must coincide, nor claim target IDs 6/10 resolved. Run `git pull` and `.\run_vp05_small_id_exact_alias_bridges.bat <pyred_weight.py>`. Separate Feynman propagator convention check remains.


### 2026-10-21 VP05 exact alias result and multi-term scope audit

The user ran `VP05_EXACT_ALIAS_BRIDGES` on 2678 source equations using `output/tools/pyred_weight.py` (codec SHA256 5669d9e935786066d21d9e8a17f6a749cdc85f548d31d149a02abad6a82b80a6, DB SHA256 d63e6452b1c8c6ccdf337719cdcd8312d9c0ff1c06df73dc83286353f1bf56ee). Target `(5,201)` has three direct unit-sign equalities with decoded large weights and codec roundtrip; selected alias exponents `[0,1,0,1,0,0,1,1,0,0,0,0]`. `(6,203)` and `(10,203)` have no direct unit-sign bridges, so remain unmapped. `physical_propagator_mapping_verified=false`. A non-mutating follow-up `examples/three_loop_sector203_small_id_multiterm_scope.py` plus `run_vp05_small_id_multiterm_scope.bat` records every original equation incident on target keys, literal coefficients, neighbouring small IDs, and bounded incidence graph scope. It performs NO linear elimination and its graph connections do NOT imply equality. Run `git pull` and `.\run_vp05_small_id_multiterm_scope.bat`. Review JSON and decide next targeted exact elimination/proof approach without repeating the previous expensive full symbolic solve.


### 2026-10-21 VP05 unresolved small-ID multi-term incidence result

`VP05_SMALL_ID_MULTITERM_SCOPE`: from 2678 source SYSTEM rows, `(10,203)` occurs in 37 rows and `(6,203)` in 24 rows, co-occurring in 7 rows. `(8,203)` co-occurs in 7 rows with `(10,203)` and 11 rows with `(6,203)`. Two-hop incidence sets are large (890 and 702 rows respectively). Co-occurrence does not imply linear dependence or a physical alias. To avoid an expensive full rational elimination, a read-only necessary-support peeling preflight was added: `examples/three_loop_sector203_small_id_support_peeling.py` with `run_vp05_small_id_support_peeling.bat`. It inspects only the direct-row union for `(10,203)` and `(6,203)` and retains `(5,201)` as a symbolic protected anchor; iteratively removes equations containing a variable unique in that restricted row set. It cannot prove an alias; discarded rows might be usable after adding further equations. Run `git pull`, `.\run_vp05_small_id_support_peeling.bat`; inspect summary and surviving exact equations before selecting a larger scoped linear-algebra proof.


### 2026-10-21 VP05 direct support peeling exhausted

User-run `VP05_SMALL_ID_SUPPORT_PEELING` found 54 unique direct rows incident on `(6,203)` or `(10,203)`; iterative structural peeling removed all 54 in six rounds (29,14,3,3,3,2). No target-support rows survive within the direct-only subset. This does NOT disprove full SYSTEM relations, because other rows can cancel variables unique to that subset. Added a read-only expansion comparison `examples/three_loop_sector203_small_id_expanded_support.py` and `run_vp05_small_id_expanded_support.bat`: compares direct-only, one-variable-incidence expansion, and full 2678-row SYSTEM using the same necessary-support peeling rule, storing surviving row provenance. No symbolic elimination or physical alias is claimed. Next: git pull; run_vp05_small_id_expanded_support.bat; inspect scope counts, choose smallest nontrivial candidate scope for subsequent exact reduction.


### 2026-10-21 VP05 expanded support and modular follow-up

User ran `VP05_SMALL_ID_EXPANDED_SUPPORT`: direct 54 rows -> 0 after peeling; one-variable expansion 964 rows / 1926 variables -> 466 surviving rows / 676 variables, retaining 21 occurrences of `(6,203)` and 34 of `(10,203)`; entire 2678 rows -> 2639 surviving. These are only support diagnostics. Added `examples/three_loop_sector203_small_id_expanded_modular.py` and `run_vp05_small_id_expanded_modular.bat` to test the 466 surviving rows in two finite fields, comparing individual small-ID unit vectors and the previously investigated target combination `z I(10,203) - 2 I(6,203) + 2 I(5,201)`; track modular original-SYSTEM replay and certificate provenance. Full-system modular test is opt-in via `--include-full-system` to avoid heavy processing. Results remain sampled, not an exact symbolic or physical alias proof. Next: `git pull`; `.\run_vp05_small_id_expanded_modular.bat` and review `VP05_SMALL_ID_MODULAR_POINT`/summary output.


### 2026-10-21 VP05 466-row local modular rowspace negative result

User ran `VP05_SMALL_ID_MODULAR_POINT` on the peeled 466-row one-variable-expanded scope at points (1000037,21,15) and (1001003,19,53). Both ranks were 466. Neither target unit vector `(10,203)` nor `(6,203)` nor the combination `z I(10,203) - 2 I(6,203) + 2 I(5,201)` belongs to the sampled rowspace of this restricted subsystem. For `(10,203)` remainder size was 38 and target combination 39; `(6,203)` was untouched (size 1). `sampled_replays_pass=true` is vacuous here: no successful membership certificate was produced, so it is NOT a positive replay. The 166-row compressed combination had previously passed modular rowspace tests, but comparison requires careful matching of source systems and mappings. Next use existing opt-in full original SYSTEM modular audit (no new code): `git pull` and `.\run_vp05_small_id_expanded_modular.bat --include-full-system`. This tests the peeled 2639-row scope plus 466-row scope at both points; avoid interpreting any failure as proof of generic nonmembership, and do not repeat expensive symbolic elimination. Full-system test may be costlier; stop if resource use is excessive.


### 2026-10-21 VP05 full SYSTEM target certificate replay and ID comparison

User full-scope modular audit: on two points `(1000037,21,15)` and `(1001003,19,53)`, peeled full SYSTEM retained 2639 equations (rank 2639) and the target `z I(10,203)-2 I(6,203)+2 I(5,201)` is in the sampled rowspace with exact modular replay against 528 original SYSTEM equations. Single-ID tests remain outside sampled rowspace. The peeled 466-row local scope does not contain the target combination. The same count 528 as the earlier candidate witness is NOT yet proof of identical equation IDs. Added read-only `examples/three_loop_sector203_certificate_provenance_compare.py` and `run_vp05_certificate_provenance_compare.bat`. The audit locates the latest `vp05_candidate4_witness_*.equations.json`, checks original SYSTEM `(file,equation_id)` identities, compares source coefficient text, computes set intersections for both modular points and independently replays the saved new modular coefficients. It does not claim symbolic proof. Run `git pull`; `.\run_vp05_certificate_provenance_compare.bat`; inspect `VP05_CERTIFICATE_PROVENANCE_COMPARE`.


### 2026-10-21 VP05 provenance comparison duplicate-head fix

The first `run_vp05_certificate_provenance_compare.bat` stopped at `Duplicated SYSTEM (file,equation_id) identities`: original SYSTEM equation headers are not unique within a file. This was a faulty comparator assumption, not evidence that the modular target certificate failed. Updated comparator to validate old witness rows using their stable original 0-based `row_index` and exact coefficients. For legacy modular results lacking row_index, duplicate heads with identical raw rows may still replay safely, but do not establish exact row-ID equality; duplicate heads with different contents are explicitly reported as unresolved. Future modular JSON now exports original `row_index` for every coefficient. First retry only `git pull` and the provenance comparison BAT; if ambiguity remains, regenerate with the existing full-system modular batch and rerun comparison. No physical alias/symbolic claim.


### 2026-10-21 VP05 certificate comparison: 278 legacy ambiguous source rows

User `VP05_CERTIFICATE_PROVENANCE_COMPARE` reports 551 duplicate `(file,equation_id)` head groups across 2678 SYSTEM rows. All 528 old witness rows validate by their original `row_index` and exact term strings. Legacy full modular certificates each contain 528 saved coefficients: 250 unambiguous identities match old witness, but 278 entries have duplicate heads that cannot safely be assigned to unique rows from the saved JSON. Thus comparison/replay from saved legacy coefficients is unresolved, NOT evidence of a failed original replay. The expanded modular code already exports original row indices in newer versions. Added `--full-only` to run just two-point full-system target-combination modular certificates without repeating the 466-row local tests or separate single-ID tests; fixed comparator's exact-support test to use validated explicit row indices even when headers are duplicated. Next execute `git pull`, `.\run_vp05_small_id_expanded_modular.bat --full-only`, `.\run_vp05_certificate_provenance_compare.bat`. This overwrites the prior expanded modular JSON with full-only entries; source provenance/replay is the goal, not a symbolic proof.


### 2026-10-21 VP05 528-row certificate provenance: exact support identity PASS

User reran full-only modular certificate with explicit original SYSTEM row indices, then provenance comparison. Full peeled SYSTEM: 2639 rows, rank 2639 at both (1000037,21,15) and (1001003,19,53); target `z I(10,203)-2 I(6,203)+2 I(5,201)` is in sampled rowspace with remainder zero and exact modular original-row replay at both points. Each modular certificate uses 528 rows. The older saved `vp05_candidate4_witness_20261017_183832.equations.json` contains 528 source rows all matched by row_index and exact coefficient text. At both points `exact_support_identity_verified=true`, `full_row_index_intersection=528`, `full_row_index_only_new=0`, `full_row_index_only_old=0`, `replay_from_saved_coefficients_verified=true`, `unresolved_ambiguous_count=0`. This resolves the 278 duplicate-head ambiguities. Proven fact: equality of the original 528-row support sets, not equality of point-dependent certificate multipliers nor a symbolic rational-function identity or physical aliases. Next use the already saved exact 528-row witness and 166-row compressed symbolic data to pursue the bounded exact symbolic target certificate, with independent replay against original 528 rows; avoid repeating 2678-row full elimination and costly SymPy full elimination.


### 2026-10-21 VP05 exact symbolic target readiness gate

528 original SYSTEM rows and the new two-point full-system certificate use exactly the same 528 original row indices. This is a support/provenance identity, not an exact symbolic coefficient certificate. Existing `three_loop_sector203_target_scope_preflight.py` and `three_loop_sector203_fermat_gaussian_pilot.py` provide modular pivot schedule/resource estimators, but the Fermat pilot is explicitly capped to 320 rows for execution and must not be treated as a completed 166-row target-only exact proof. Added `examples/three_loop_sector203_exact_target_readiness.py` and `run_vp05_exact_target_readiness.bat` to validate the saved 166-row compressed symbolic dataset against the saved 528-row witness presence; test four finite-field schedules, target membership, modular replay, dependency/cell budgets and print `VP05_EXACT_TARGET_READINESS`. No Kira, FireFly, Fermat, or expensive SymPy exact elimination is invoked. A PASS is only scheduling readiness, not a proof that sampled zeros persist symbolically or that compressed linear-combination provenance has been symbolically replayed against the original 528 rows. Next run `git pull` and `.\run_vp05_exact_target_readiness.bat`, inspect output before authorizing bounded target-only exact symbolic engine work.


### 2026-10-21 VP05 32k-cell preflight PASS; Fermat pilot compatibility next

User reran exact target readiness with `--max-cells 32000`: all four finite-field points rank 166, target remainder 0, replay true, 166 dependency rows, 27 target owners, estimated cumulative 30987 cells and peak 27093, `PREFLIGHT_PASS_NOT_PROOF`. The cap change does not bound rational expression swell or prove symbolic identities. Reviewed existing Fermat Gaussian pilot: it supports 166 input rows and a `--preflight-only` mode. Added `run_vp05_fermat_compressed_pilot_preflight.bat` to exercise that pilot specifically on saved 166-row compressed equations with no Fermat invocation, `--auto-points`, row-lifetime preflight, and 32000-cell cap. Next run `git pull` then `.\run_vp05_fermat_compressed_pilot_preflight.bat`; inspect command/output/map/cell caps and compatibility before any actual exact run. Pilot's ordinary output is row-echelon validation, not yet a direct symbolic target certificate nor an exact replay through compressed row-combination provenance to the 528 source rows.


### 2026-10-21 VP05 Fermat 166-row pilot cap diagnosis

User `FERMAT_GAUSS_PREFLIGHT`: matched a rank-166 pivot schedule at (1000033,19,11), (1000037,21,15), (1000039,23,19); 166 rows/400 columns; 1745 elimination operations; 31840 sparse-array cells <= 32000 but 40214 generated commands > 4500 cap and 30987 row-echelon coefficient outputs > 1000 cap. Row lifetime analysis showed 0 releasable rows before verification outputs when requesting all rows. This is a preflight only, with no Fermat exact calculation. Updated `run_vp05_fermat_compressed_pilot_preflight.bat` with `--verify-last-rows 1` to measure how much generic echelon-output reduction helps, retaining all other safety caps and `--preflight-only`. This tests a diagnostic last row and is NOT the sought target-specific 3-term certificate; further target-specific extraction and symbolic replay are required. Next: git pull; rerun same batch; inspect `FERMAT_GAUSS_PREFLIGHT`, especially commands/outputs/live rows and cap status.


### 2026-10-21 VP05 Fermat one-row output preflight

With `--verify-last-rows 1`, user measured 166-row / 400-column / rank-166 pilot, 1745 modular scheduled eliminations, 370 output coefficients, 9330 script commands, 30788 allocated sparse array entries, 27863 estimated peak live entries, and 161 rows hypothetically releasable before outputs (memory release not active). `within_caps=false` because command count exceeds 4500 despite output/cell caps passing. It is a last-echelon-row diagnostic, not the desired three-term target certificate. Updated BAT to preflight existing `--packed-sparse-maps --reuse-packed-maps --loop-control-rows` implementation, which moves scheduled elimination control into Fermat loops to reduce generated commands, while keeping `--preflight-only` (no Fermat execution). Next run git pull and same BAT, examine command counts, map cells, memory and caps; continue to target-specific symbolic certificate and original 528-row exact replay rather than treating generic last-row verification as proof.


### 2026-10-21 VP05 166-row Fermat loop-control preflight PASS

User ran `run_vp05_fermat_compressed_pilot_preflight.bat`: 166 rows / 400 columns, rank 166, 1745 elimination operations, 370 outputs, 2320 generated commands (down from 9330), 30788 sparse array cells, 44198 packed-map cells + 444 control cells, all within configured command/output/array/map caps (`within_caps=true`). Three independent sample points share one schedule. Lifetime analysis estimates 27863 peak live cells, but memory reclamation is not implemented and physical RSS is not measured. `ESTIMATE_ONLY` means no Fermat execution and no symbolic or 528-row exact replay proof. Crucially, `--verify-last-rows 1` only checks the last echelon row, NOT target-combination identity. Future next step: target-specific exact certificate generation with symbolic checks for modular-zero pivots and provenance replay, using a small explicitly capped smoke test before any potentially expensive full run. Do not represent this pilot as exact VP05 target proof.


### 2026-10-21 VP05 target-only certificate reverse-substitution stage

After reducing the 166-row compressed Fermat pilot's generic output to 370 coefficients and reducing the generated command count to 2320 (preflight only), implemented `examples/three_loop_sector203_target_reverse_certificate.py` and `run_vp05_target_reverse_certificate.bat`. This read-only, no-Fermat first stage constructs the target-specific modular certificate with reverse substitution through normalized elimination rows. Given E_i=(R_i-sum_{j<i} f_ij E_j)/n_i and target T=sum_i g_i E_i, descend rows to obtain C_i=g_i/n_i, then update g_j-=C_i f_ij; independently replay sum_i C_i R_i == T in each of four finite fields. Saves the full pivot schedule, target owner sequence, modular certificate vectors, and source digest. A PASS is a finite-field certificate trace only: sampled zero factors cannot be used as unconditional symbolic zeros, and no exact rational-function or original 528-row symbolic replay is claimed. Next run git pull and `run_vp05_target_reverse_certificate.bat`. The next implementation phase is a bounded Fermat exact execution of this trace with exact zero/divisor checks and source-row provenance replay. No large exact calculation is run in this commit.


### 2026-10-21 VP05 target reverse certificate 4-point PASS and bounded exact prefix smoke

User `VP05_TARGET_REVERSE_POINT`: at (1000037,21,15), (1001003,19,53), (1001107,36,64), (1002101,47,83), each compressed 166-row matrix has rank 166; target uses 27 echelon pivots, reverse certificate has nonzero coefficients on all 166 original compressed rows, and replay of linear combination over each field succeeded. Shared complete pivot schedule and target owner order PASS; symbolic proof remains false. Added `examples/three_loop_sector203_exact_prefix_smoke.py` and `run_vp05_exact_prefix_smoke.bat`: bounded 1..5 row SymPy rational-function prefix replays each exact normalized pivot as a symbolic linear combination of original compressed source rows, checks equality of exact leading pivots against sampled schedule, requires source SHA256 match with saved reverse plan. Default 3 rows; soft operation budget 30 sec. This is a small integration smoke test only, NOT proof of target or original 528-row exact replay and not a full Fermat execution. Next run git pull and `.\run_vp05_exact_prefix_smoke.bat`, review VP05_EXACT_PREFIX_ROW/SUMMARY. Expand to exact Fermat target-specific certificate only after symbolic prefix behavior is established.


### 2026-10-21 VP05 exact prefix smoke 3/3 PASS; identify first nontrivial elimination

User `VP05_EXACT_PREFIX_ROW` for rows 0/1/2: normalized columns 183,54,29 respectively, one original source row each, exact symbolic replay passed. These tests cover only standalone pivot normalization, not elimination with previous pivot rows. Added `examples/three_loop_sector203_exact_elimination_probe.py` and `run_vp05_exact_elimination_probe.bat`, a no-Fermat read-only inspection of the saved four-point shared modular schedule to locate the first row with nonzero scheduled elimination operations, its owner list, and minimum prefix length needed for a nontrivial exact smoke. Does not claim symbolic target proof. Next: git pull; run_vp05_exact_elimination_probe.bat; determine an appropriately bounded exact elimination test rather than blindly increasing prefix size.


### 2026-10-21 VP05 first nontrivial exact pivot test (six rows)

User `VP05_EXACT_ELIMINATION_PROBE`: first scheduled nontrivial elimination is zero-based row 5, one operation using owner row 2, lead `[47313359732737,194]`; 122/166 rows have at least one scheduled pivot elimination. Previously the 3-row SymPy exact smoke only checked standalone normalizations. Raised exact-prefix smoke hard row cap from 5 to 6 and changed its BAT default to `--rows 6`, retaining exact symbolic normalized-row/source-row replay and per-operation soft timeout check. No Fermat invocation or 166-row symbolic proof. Next run git pull; `.\run_vp05_exact_prefix_smoke.bat`, confirm row 5 `pivot_elimination_operations=1` and symbolic replay verified.


### 2026-10-21 VP05 six-row exact symbolic source replay PASS; seven-row next

User 6-row exact SymPy smoke: all six normalized rows replay symbolically against original compressed source rows. Row index 5 has one genuine elimination using two original source equations, 100 columns after normalization, `symbolic_source_replay_verified=true`. This is a real rational-function pivot-subtraction check but not the 166-row target identity or original 528-row replay. The next row (index 6) has two scheduled eliminations, with owners 2 and 5; raised bounded smoke hard limit to 7 and BAT default to seven rows for chained elimination verification. No full Fermat invocation and no claim of target proof.


### 2026-10-21 VP05 seven-row exact symbolic chained elimination PASS

User log: `VP05_EXACT_PREFIX_ROW` for indices 0..6 all report `symbolic_source_replay_verified=true`. Index 5 performed one pivot elimination and replayed a combination of two original compressed equations; index 6 performed two chained pivot eliminations, had 112 normalized columns, support of three compressed source rows, and exact symbolic replay passed. `VP05_EXACT_PREFIX_SUMMARY` reports 7/7 rows verified. This validates local SymPy rational-function pivot/replay mechanics but does not establish the 166-row target identity nor replay against the original 528 SYSTEM witness. Avoid treating further small-prefix successes as proof of full identity. Next engineering step should shift from repeatedly increasing the bounded prefix toward target-specific exact certificate with robust resource limits and exact provenance checking.


### 2026-10-21 VP05 guarded exact target certificate engine added

After the seven-row symbolic pivot/source replay passed, introduced `examples/three_loop_sector203_exact_target_engine.py` and `run_vp05_exact_target_engine.bat`. The new engine consumes saved four-point shared finite-field elimination schedule and exact 166-row compressed coefficients. In a separate process with wall-clock timeout (120 s default, max 3600), it recomputes every actual rational-function pivot factor/divisor using SymPy, rejects symbolic schedule discrepancies, performs exact target elimination, reverse-solves 166 compressed-row certificate multipliers, and checks the original 166 compressed equations reproduce `z I(10,203)-2 I(6,203)+2 I(5,201)` exactly. Default batch runs only 7-row exact prefix integration check. FULL mode is explicit opt-in `--full` and is potentially very expensive even with a subprocess timeout; no full run was performed by assistant. Important scope: even a full PASS would establish only compressed 166-row symbolic identity; exact symbolic lifting to all 528 original SYSTEM source rows through compressed-combination provenance remains an independent requirement, as does physical exponent mapping. Next git pull; run `run_vp05_exact_target_engine.bat` for guarded prefix. Do not run `--full` yet until the prefix integration is confirmed and resource behavior evaluated.
