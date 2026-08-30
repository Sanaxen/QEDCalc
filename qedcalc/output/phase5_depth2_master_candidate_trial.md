# QEDCalc phase-5 depth-2 master-candidate audit

## 1. Scope

This audit strengthens the v0.36 bounded first-neighborhood test without claiming a global master-integral proof.

For each of the three provisional local master candidates, QEDCalc tests canonical seeds obtained by moving one admissible integral-family index two steps in the same direction. This directional depth-2 domain is deliberately smaller than the full Cartesian degree-2 seed domain and avoids opening an uncontrolled Laporta system.

## 2. Independent exact-rational probes

The same phase-2 seed domain was rebuilt independently at three exact-rational kinematic points:

- `(D,z)=(37/10,2/5)`
- `(D,z)=(41/11,3/7)`
- `(D,z)=(29/8,-1/3)`

Each probe produced **837** baseline pivots.

## 3. Directional depth-2 results

- `(0, 1, 0, 0, 1, 0, 2)`: first-neighbor pivots = **0/7**; directional depth-2 seeds = **7**; pivoting seeds across the three probes = **0, 0, 0**.
- `(0, 1, 1, 1, 0, 1, 1)`: first-neighbor pivots = **0/7**; directional depth-2 seeds = **5**; pivoting seeds across the three probes = **0, 0, 0**.
- `(0, 1, 1, 1, 1, 0, 2)`: first-neighbor pivots = **0/7**; directional depth-2 seeds = **7**; pivoting seeds across the three probes = **0, 0, 0**.

All three candidates remain non-pivoting in the tested directional depth-2 domain at all three independent exact-rational probes.

## 4. Interpretation

The evidence is stronger than the v0.36 first-neighborhood audit, but it is still bounded. The three integrals are therefore promoted only to **depth-2-stable provisional master candidates**, not to globally proven master integrals.

CSV: `output/ladder_phase5_depth2_master_candidates.csv`
