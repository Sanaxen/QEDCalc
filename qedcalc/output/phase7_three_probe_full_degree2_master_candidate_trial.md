# QEDCalc phase-7 three-probe full degree-2 master-candidate audit

## 1. Purpose

This audit repeats the complete bounded degree-2 Cartesian test at three independent exact-rational probes. The first-neighbor and same-direction depth-2 classes had already been checked at all three probes; this phase completes the mixed two-direction class at probes 2 and 3.

## 2. Portable baseline checkpoints

- probe `{'D': '37/10', 'z': '2/5', 'm2': '1'}`: **837** baseline pivots.
- probe `{'D': '41/11', 'z': '3/7', 'm2': '1'}`: **837** baseline pivots.
- probe `{'D': '29/8', 'z': '-1/3', 'm2': '1'}`: **837** baseline pivots.

All three independently rebuilt baseline systems contain **837 pivots**.

## 3. Full mixed degree-2 results

### Candidate 1: `(0, 1, 0, 0, 1, 0, 2)`

- probe1: mixed seeds **18**, candidate pivot = **False**.
- probe2: mixed seeds **18**, candidate pivot = **False**, batch new pivots **123**.
- probe3: mixed seeds **18**, candidate pivot = **False**, batch new pivots **123**.

### Candidate 2: `(0, 1, 1, 1, 0, 1, 1)`

- probe1: mixed seeds **10**, candidate pivot = **False**.
- probe2: mixed seeds **10**, candidate pivot = **False**, batch new pivots **80**.
- probe3: mixed seeds **10**, candidate pivot = **False**, batch new pivots **80**.

### Candidate 3: `(0, 1, 1, 1, 1, 0, 2)`

- probe1: mixed seeds **21**, candidate pivot = **False**.
- probe2: mixed seeds **21**, candidate pivot = **False**, batch new pivots **166**.
- probe3: mixed seeds **21**, candidate pivot = **False**, batch new pivots **166**.

## 4. Interpretation

All three provisional candidates remain non-pivoting throughout the complete bounded degree-2 Cartesian neighborhood at all three independent exact-rational probes. This is stronger evidence than a single-probe bounded audit, but it is still not a global mathematical proof of master-integral status.

## 5. Performance improvement

Incremental Laporta reduction now reuses one persistent recursive reduction cache for all new IBP rows. This removes repeated reconstruction of the 837-rule recursion graph and makes the multi-probe mixed-domain audit practical.

CSV: `output/ladder_phase7_three_probe_full_degree2_audit.csv`
