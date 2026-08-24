# QEDCalc phase-4 local master-candidate trial

## 1. Residues entering phase 4

Remaining genuine terminal residue kinds after factorized lower-sector recognition: **3**.

- `(0, 1, 0, 0, 1, 0, 2)` blocks **18** target(s).
- `(0, 1, 1, 1, 0, 1, 1)` blocks **6** target(s).
- `(0, 1, 1, 1, 1, 0, 2)` blocks **6** target(s).

## 2. First-neighborhood diagnostic checkpoint

- `(0, 1, 0, 0, 1, 0, 2)`: tested **7** new canonical first-neighbor seeds; pivoting neighbors = **0**; locally irreducible = **True**.
- `(0, 1, 1, 1, 0, 1, 1)`: tested **7** new canonical first-neighbor seeds; pivoting neighbors = **0**; locally irreducible = **True**.
- `(0, 1, 1, 1, 1, 0, 2)`: tested **7** new canonical first-neighbor seeds; pivoting neighbors = **0**; locally irreducible = **True**.

The checkpoint was generated from the v0.35 phase-2 triangular rule set using the generic `diagnose_first_neighbor_irreducibility()` algorithm. It is a bounded local IBP diagnostic, not a proof of global master-integral status.

## 3. Provisional basis expansion

Original corrected non-factorized candidate basis: **6**.

Additional locally irreducible candidates: **3**.

Provisional non-factorized basis size: **9**.

After admitting these three residues provisionally, the previously reported phase-3 non-basis terminal-residue set is exhausted, so all 40 corrected canonical targets are closed with respect to this provisional basis plus known factorized lower sectors.

CSV: `output/ladder_phase4_local_master_candidates.csv`
