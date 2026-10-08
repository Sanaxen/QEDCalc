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
