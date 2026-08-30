# QEDCalc residue-aware closure scheduler trial

## 1. Purpose

This trial ranks terminal non-candidate residues by the number of corrected ordinary-ladder targets they block, aggregates them by sector, and adds only the residue seeds themselves before any neighborhood expansion.

## 2. Baseline

Canonical corrected targets: **40**.

Protected stable candidate basis: **6**.

Baseline seeds: **84**.

Baseline IBP rows: **666**.

Baseline pivots at the exact probe: **598**.

Baseline residue-bearing targets: **28**.

## 3. Highest-impact residue sectors

- sector 96: blocked targets = **22**, residues = **1**, new direct seeds = **1**, score = **22**
- sector 80: blocked targets = **17**, residues = **1**, new direct seeds = **1**, score = **17**
- sector 66: blocked targets = **6**, residues = **1**, new direct seeds = **1**, score = **6**
- sector 70: blocked targets = **6**, residues = **1**, new direct seeds = **1**, score = **6**
- sector 94: blocked targets = **6**, residues = **1**, new direct seeds = **1**, score = **6**
- sector 110: blocked targets = **6**, residues = **1**, new direct seeds = **1**, score = **6**
- sector 38: blocked targets = **6**, residues = **2**, new direct seeds = **2**, score = **3**
- sector 50: blocked targets = **6**, residues = **2**, new direct seeds = **2**, score = **3**

The first two useful sectors are sector 96 and sector 80. Sector 82 has high impact but its terminal residue is already present in the baseline seed set, so it receives zero new-seed priority.

## 4. Phase-1 bounded direct-residue insertion

New terminal-residue seeds selected: **30**.

Seeds after phase 1: **114**.

IBP rows after phase 1: **906**.

Pivots after phase 1: **823**.

Residue-bearing targets after phase 1: **27**.

Additional fully closed targets: **1**.

## 5. Interpretation

The direct-residue phase remains computationally controlled and avoids the large blow-up seen when all degree-1 residue neighborhoods are inserted simultaneously. It also produces additional pivots and closes one more corrected target in this trial.

The next scheduler phase should recompute terminal residues on the enlarged seed system and expand only the best remaining residue sector neighborhood, under a strict new-seed budget.

Residue profile CSV: `output/ladder_residue_impact_profile.csv`

Sector priority CSV: `output/ladder_residue_sector_priority.csv`
