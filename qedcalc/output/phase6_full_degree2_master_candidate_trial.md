# QEDCalc phase-6 full degree-2 Cartesian master-candidate audit

## 1. Scope

This audit completes the bounded degree-2 Cartesian neighborhood at the primary exact-rational probe. The previously tested first-neighbor and same-direction depth-2 sectors are supplemented by all remaining mixed two-direction degree-2 seeds.

The 837-pivot primary-probe Laporta rule set is loaded from a portable JSON checkpoint rather than rebuilt from scratch.

Checkpoint probe: `{'D': '37/10', 'z': '2/5', 'm2': '1'}`; stored pivots: **837**.

## 2. Results

- `(0, 1, 0, 0, 1, 0, 2)`: new full degree-2 seeds = **32** (first **7**, directional **7**, mixed **18**); mixed pivoting seeds = **0**; full degree-2 pivoting seeds = **0**.
- `(0, 1, 1, 1, 0, 1, 1)`: new full degree-2 seeds = **19** (first **4**, directional **5**, mixed **10**); mixed pivoting seeds = **0**; full degree-2 pivoting seeds = **0**.
- `(0, 1, 1, 1, 1, 0, 2)`: new full degree-2 seeds = **33** (first **5**, directional **7**, mixed **21**); mixed pivoting seeds = **0**; full degree-2 pivoting seeds = **0**.

At the primary probe, all three candidates remain non-pivoting throughout the complete bounded degree-2 Cartesian neighborhood after symmetry canonicalization and removal of seeds already present in the 116-seed baseline.

## 3. Interpretation

This is stronger than the directional depth-2 audit because the mixed two-direction seed class is now exhausted at the primary probe. It is still not a global proof of master-integral status: an independent reduction system or a wider seed domain remains desirable.

CSV: `output/ladder_phase6_full_degree2_master_candidates.csv`
