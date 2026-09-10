# Q01 Kira backend

## Purpose

The native Python IBP backend reached an impractical memory regime while refreshing same-sector support for the Q01 four-line source sector.  The optional Kira backend is therefore introduced as an acceleration path for large three-loop IBP systems while keeping the native backend for independent structural checks and smaller reductions.

The first milestone is deliberately small: export a Kira-native family for the already studied Q01 four-line sector, run a minimal WSL smoke reduction, and compare its behavior with the native QEDCalc results before increasing the seed limits.

## Source sector

The QEDCalc physical source-sector mask is

```text
(1,0,1,0,1,1,0,0,0)
```

so the active physical denominators are `D1,D3,D5,D6`.

For Kira these four lines are moved to the first four propagator positions.  The dedicated benchmark therefore uses Kira top sector `15`.

## Kira propagator order

```text
Kira 1  <- QEDCalc D1
Kira 2  <- QEDCalc D3
Kira 3  <- QEDCalc D5
Kira 4  <- QEDCalc D6
Kira 5  <- QEDCalc D2
Kira 6  <- QEDCalc D4
Kira 7  <- QEDCalc D7
Kira 8  <- QEDCalc D8
Kira 9  <- QEDCalc D9
Kira 10 <- (k-r)^2
Kira 11 <- (l+q)^2
Kira 12 <- (r+q)^2
```

Kira uses inverse propagators of the form `momentum^2-mass^2`.  The first nine QEDCalc physical denominators use the opposite sign convention, hence

```text
Kira_Pi = -QEDCalc_Dj
```

for the corresponding physical line.

## Why D10-D12 are changed

The native QEDCalc family uses the linear ISP denominators

```text
D10 = k.r
D11 = l.q
D12 = q.r
```

Kira is designed around quadratic inverse propagators.  The Kira backend therefore replaces those three linear ISP basis elements by quadratic auxiliary inverse propagators.  The exact relations are

```text
QEDCalc_D10 = (Kira_P7 + Kira_P9 - Kira_P10)/2
QEDCalc_D11 = (Kira_P11 - Kira_P8 - z*m2)/2
QEDCalc_D12 = (Kira_P12 - Kira_P9 - z*m2)/2
```

The resulting twelve Kira inverse propagators span the same twelve-dimensional loop scalar-product space.  `three_loop.kira_backend.validate_q01_kira_basis()` checks this algebraically by requiring full rank 12.

This is **not** an index-by-index identification of the old QEDCalc D10-D12 powers with Kira indices 10-12.  Any amplitude or reduction table crossing the backend boundary must apply the basis transformation explicitly.  The generated `qedcalc_kira_manifest.json` records this requirement.

## Generated project

The smoke exporter creates

```text
output/kira_q01_4line_smoke/
    config/
        integralfamilies.yaml
        kinematics.yaml
    jobs.yaml
    qedcalc_kira_manifest.json
```

The default smoke limits are

```text
r = 4
s = 0
d = 0
```

and back substitution is disabled.  This is intentional: the first run validates WSL/Kira availability, YAML syntax, topology definition, kinematics, symmetry setup, equation generation, and triangular reduction without immediately attempting a large production system.

## Windows / WSL bridge

`three_loop.kira_wsl` converts the Windows checkout path with `wslpath`, verifies that `kira` is available on the default WSL `PATH`, executes Kira in that WSL environment, and writes the combined Kira output to

```text
output/kira_q01_4line_smoke/kira_run.log
```

This avoids manually copying files between Windows and WSL.  Kira works directly on the project directory through the WSL-mounted Windows filesystem for the initial smoke benchmark.

## Validation commands

Export only:

```powershell
git pull
./run_three_loop_q01_kira_export_smoke.bat
```

WSL/Kira smoke run:

```powershell
./run_three_loop_q01_kira_wsl_smoke.bat
```

A successful exporter must report a basis rank of `12/12`.

A successful WSL smoke run must end with

```text
Q01 Kira WSL smoke PASS
```

and produce `qedcalc_kira_run_summary.json` plus `kira_run.log`.

## Next steps after the smoke run

1. Record the installed Kira version and actual output layout.
2. Add an importer for that output rather than guessing a version-specific format in advance.
3. Add explicit QEDCalc-to-Kira numerator expansion for the linear ISP basis transformation.
4. Increase `r,s,d` gradually and measure wall time and peak memory.
5. Compare Kira master counting and reductions against the native finite-field structural checks already completed for Q01.
6. Only after those checks, use Kira as the production IBP backend for the remaining Q01 reduction and later Q02-Q72 families.
