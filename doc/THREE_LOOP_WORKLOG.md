# QEDCalc 3-loop worklog / handoff notes

Purpose: persistent engineering handoff notes for continuing the 3-loop QED vertex project across ChatGPT sessions. This file is primarily for the assistant/maintainer, not end-user documentation.

## Working branch

- Repository: `Sanaxen/QEDCalc`
- Branch: `feature/three-loop-stage1-3`
- User environment: Windows 11 frontend, WSL/Linux for Kira/FireFly/Fermat where needed.
- Heavy computations are run by the user locally. When asking the user to run something, give copy-paste PowerShell commands in this style:

```powershell
git pull
.\run_something.bat
```

Do not ask the user to perform manual multi-step edits when a BAT/helper can be pushed instead.

## Overall 3-loop objective

Take all 72 three-loop electron-vertex diagrams through:

1. diagram expression / projected amplitude generation,
2. integral-family mapping,
3. IBP reduction,
4. master-integral basis identification,
5. coefficient synthesis onto masters,
6. master evaluation / epsilon expansion,
7. final diagram contributions to `F2(0)`,
8. full three-loop `g-2` coefficient assembly and comparison with the known result.

## 72-diagram topology inventory

`data/three_loop_topologies.json` contains all 72 diagrams and the physical/topological families:

- `quenched`: Q01-Q50 = 50 diagrams
- `vp1_insert`: VP01-VP12 = 12 diagrams
- `vp2_insert`: VP4A-VP4C = 3 diagrams
- `vp1_double`: VP22 = 1 diagram
- `external_lbl`: LBL01-LBL06 = 6 diagrams

Total = 72.

Important distinction: this physical/topological family classification is complete, but a global canonical **IBP/Kira integral-family classification** for all 72 diagrams is not yet considered complete. A later audit must determine which diagrams map to the same canonical integral family after loop-momentum relabeling/symmetries and which need distinct auxiliary propagator bases.

## Q01 status

Q01 is the representative development diagram used to harden the full pipeline before horizontal expansion to the remaining diagrams.

### Q01 target/reduction history

- Original native demand set: 910 integrals.
- Exact original target set: 944 integrals.
- Closure expansion was previously completed and audited with FireFly.
- The projected-amplitude/master-basis work produced a finalized set of 60 Q01 master forms (`final60`).
- Mandatory boundary-test union = exact944 targets U final60 = 971 targets.

### Q01 seed-boundary stability

Baseline seed scope: `(r,s,d)=(9,3,0)`.

Three independent one-axis extensions have passed:

- `r+1`: `(10,3,0)`, Kira/Fermat
  - joint mandatory targets: 971
  - `masters.final`: 117
  - final60: 60 master, 0 reduced, 0 zero, 0 unresolved
  - joint targets: 60 master, 874 reduced, 37 zero, 0 unresolved
  - Kira unreduced integrals = 0
  - stable = true

- `s+1`: `(9,4,0)`, Kira/FireFly
  - runtime about 3298.4 s
  - `masters.final`: 125
  - final60: 60 master, 0 reduced, 0 zero, 0 unresolved
  - joint targets: 60 master, 874 reduced, 37 zero, 0 unresolved
  - Kira unreduced integrals = 0
  - stable = true

- `d+1`: `(9,3,1)`, Kira/FireFly
  - runtime about 2045.2 s
  - `masters.final`: 60
  - final60: 60 master, 0 reduced, 0 zero, 0 unresolved
  - joint targets: 60 master, 874 reduced, 37 zero, 0 unresolved
  - Kira unreduced integrals = 0
  - stable = true

Combined audit also passed:

```text
QEDCalc Q01 exact944 seed-boundary complete audit
r_plus_1: r=10 s=3 d=0 solver=Kira/Fermat masters.final=117 PASS=True
s_plus_1: r=9 s=4 d=0 solver=Kira/FireFly masters.final=125 PASS=True
d_plus_1: r=9 s=3 d=1 solver=Kira/FireFly masters.final=60 PASS=True
all three axes stable: True
Q01 exact944 seed-boundary complete audit PASS
```

Conclusion: Q01 master-basis identification is considered complete for the current target set. The finalized 60 master forms are not artifacts of the baseline seed cutoff.

### FireFly lesson

A first `r9s4d0` FireFly attempt failed immediately with:

```text
FireFly info: Loading saved states
FireFly error: Validation failed: Entry 0 does not match the black-box result!
```

Cause was stale FireFly state. The FireFly runners were changed to delete stale `firefly_saves`, `ff_save`, and their dedicated FireFly `alt_dir` before a fresh run. Also, FireFly jobs disable ordinary triangular/back-substitution and enable `run_firefly: true` explicitly.

Do not regress this behavior.

### Useful Q01 runners/helpers

- `run_three_loop_q01_kira_exact944_r9s4d0_firefly_boundary_test.bat`
- `run_three_loop_q01_kira_exact944_r9s3d1_firefly_boundary_test.bat`
- `run_three_loop_q01_kira_exact944_seed_boundary_complete_audit.bat`
- `examples/three_loop_q01_kira_exact944_r10s3d0_boundary_test.py`
- `examples/three_loop_q01_kira_exact944_r9s4d0_firefly_boundary_test.py`
- `examples/three_loop_q01_kira_exact944_r9s3d1_firefly_boundary_test.py`

## Current next step

The agreed direction is:

1. Complete **Q01 coefficient synthesis onto the finalized 60 masters**.
2. Once Q01 coefficient synthesis is validated, build a **72-diagram integral-family global classification audit**.
3. Then extend the validated coefficient-synthesis pipeline across the remaining 71 diagrams by canonical integral family, rather than evaluating Q01 masters to final constants first.
4. Only after the 72-diagram/global-master picture is known, prioritize master evaluation/epsilon expansion and final `F2(0)` assembly.

This ordering is deliberate: avoid evaluating Q01 masters in isolation before knowing which masters/families are shared by the full 72-diagram problem.

## Immediate Q01 coefficient-synthesis target

Desired form:

```text
F2_Q01^(3)(0) = sum_i C_i(D) * M_i(D)
```

with coefficients collected exactly onto the finalized 60 Q01 master integrals.

Requirements for considering Q01 coefficient synthesis complete:

- consume the actual projected-amplitude reduction output, not a proxy count;
- map every surviving reduced term to one of the finalized 60 master forms;
- combine duplicate master contributions symbolically;
- retain exact rational functions of `D` / epsilon as appropriate;
- prove there are no unresolved/non-master RHS integrals;
- emit machine-readable JSON plus a readable TXT/MD summary;
- include an audit that reconstructs/checks the total from the pre-combination terms;
- avoid numerical master evaluation at this stage.

## Planned 72-diagram integral-family global classification audit

After Q01 coefficient synthesis passes, create an audit that records for every one of the 72 diagrams:

- diagram ID and physical/topological family;
- canonical integral-family ID;
- canonical propagator basis;
- loop-momentum transformation from diagram routing to canonical family;
- sign/normalization transformation, if any;
- symmetry-equivalent diagram/family representative;
- whether an existing Kira family can be reused;
- whether a new auxiliary propagator basis is required;
- projected-amplitude target statistics;
- eventual master-basis identifier.

The audit must distinguish topology-family labels (`quenched`, `vp1_insert`, etc.) from actual canonical IBP integral families.

## Interaction/operational convention

The user explicitly prefers that heavy local computations be delegated to him. The assistant should:

- implement code/helpers/BATs and push them to GitHub;
- ask for heavy local execution only when necessary;
- give execution instructions as a minimal PowerShell block, usually:

```powershell
git pull
.\<runner>.bat
```

- after the user posts a log, interpret it and immediately prepare the next code change when appropriate;
- update this worklog after material milestones, design changes, important failures/fixes, or before a likely session handoff.

## Continuity rule

When a new chat/session starts, read this file first before proposing the next step. Treat it as the persistent project handoff record. Cross-check against current branch files and current user-provided logs because this file can lag behind the latest local computation until updated.
