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
