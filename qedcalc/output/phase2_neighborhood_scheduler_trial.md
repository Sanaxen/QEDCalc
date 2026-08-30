# QEDCalc phase-2 neighborhood scheduler trial

## 1. Phase-1 baseline

Phase-1 seeds: **114**.

Phase-1 pivots: **823**.

Terminal residue kinds: **6**.

## 2. Incremental extension

New candidate seeds are not evaluated by rebuilding the full 906-row system. Each candidate contributes only its own IBP rows, which are reduced through the existing 823 phase-1 pivots before new pivots are selected.

## 3. Candidate pool

Candidate neighborhood seeds from sectors 96 and 80: **22**.

Candidates that directly pivot at least one known terminal residue: **7**.

- `(-1, 0, 0, 0, 0, 1, 2)`: direct blocked-target impact = **22**, new pivots = **7**, terminal residues hit = **1**
- `(0, -1, 0, 0, 0, 1, 2)`: direct blocked-target impact = **22**, new pivots = **8**, terminal residues hit = **1**
- `(0, 0, 0, -1, 0, 1, 2)`: direct blocked-target impact = **22**, new pivots = **8**, terminal residues hit = **1**
- `(-1, 0, 0, 0, 1, 0, 2)`: direct blocked-target impact = **17**, new pivots = **7**, terminal residues hit = **1**
- `(0, 0, 0, -1, 1, 0, 2)`: direct blocked-target impact = **17**, new pivots = **7**, terminal residues hit = **1**
- `(0, 0, 0, 0, 2, 0, 2)`: direct blocked-target impact = **6**, new pivots = **4**, terminal residues hit = **1**
- `(0, 0, 0, 0, 1, 0, 3)`: direct blocked-target impact = **6**, new pivots = **8**, terminal residues hit = **1**
- `(0, 0, 0, 0, 0, 2, 2)`: direct blocked-target impact = **0**, new pivots = **4**, terminal residues hit = **0**
- `(0, 0, 0, 0, 3, 0, 3)`: direct blocked-target impact = **0**, new pivots = **4**, terminal residues hit = **0**
- `(0, 0, 0, 0, 0, 1, 3)`: direct blocked-target impact = **0**, new pivots = **8**, terminal residues hit = **0**

## 4. Greedy phase-2 batch

Selected seeds: **2**.

Union of targets blocked by directly hit residues: **26**.

- `(-1, 0, 0, 0, 0, 1, 2)`: direct impact = **22**, hit residues = `[(0, 0, 0, 0, 0, 1, 2)]`
- `(-1, 0, 0, 0, 1, 0, 2)`: direct impact = **17**, hit residues = `[(0, 0, 0, 0, 1, 0, 2)]`

The covered-target count is a scheduling metric, not a claim that those targets are already fully reduced. Full recursive target reduction is deferred until the small batch has been accepted.

Ranking CSV: `output/ladder_phase2_neighborhood_seed_ranking.csv`
