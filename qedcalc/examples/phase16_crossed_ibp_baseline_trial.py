from pathlib import Path
import sympy as sp
from qedcalc.operations.ladder import load_ladder_coefficient_table
from qedcalc.operations.crossed_ladder import crossed_ladder_ibp_family
from qedcalc.operations.ibp import (
    IntegralIndex, generate_ibp_system, prune_zero_sectors,
    specialize_ibp_system, laporta_forward_eliminate, write_laporta_rule_checkpoint,
)

ROOT=Path(__file__).resolve().parents[1]
D,z,m2=sp.symbols('D z m2')
table=load_ladder_coefficient_table(ROOT/'output'/'crossed_corrected_spin_sum_95_coefficients.csv')
targets=tuple(IntegralIndex(i.as_tuple()) for i in table)
family=crossed_ladder_ibp_family(D,z,m2)
equations=prune_zero_sectors(family,generate_ibp_system(family,targets))
probe={D:sp.Rational(37,10),z:sp.Rational(2,5),m2:1}
rules=laporta_forward_eliminate(specialize_ibp_system(equations,probe))
write_laporta_rule_checkpoint(ROOT/'data'/'crossed_phase16_baseline_rules.json', rules, metadata={'probe': {'D':'37/10','z':'2/5','m2':'1'}, 'targets': len(targets), 'equations': len(equations)})
lhs={r.lhs for r in rules}
rhs_integrals=set()
for r in rules:
    rhs_integrals.update(r.rhs)
terminal=rhs_integrals-lhs
pivot_targets=tuple(t for t in targets if t in lhs)
remaining=tuple(t for t in targets if t not in lhs)
OUT=ROOT/'output'/'phase16_crossed_ibp_baseline_trial.md'
lines=['# Phase 16: crossed-ladder bounded IBP baseline','',
       'The 95 corrected crossed-ladder projector targets are used directly as a bounded seed set at one exact-rational generic probe. No floating-point rank test is used.','',
       f'Probe: `$D=37/10$, $z=2/5$, $m^2=1$`.','',
       f'- Projector targets: **{len(targets)}**',
       f'- IBP equations after zero-sector pruning: **{len(equations)}**',
       f'- Laporta pivots: **{len(rules)}**',
       f'- Projector targets already pivoted: **{len(pivot_targets)}**',
       f'- Projector targets not yet pivoted: **{len(remaining)}**',
       f'- Direct terminal RHS integrals in this bounded system: **{len(terminal)}**','',
       'This is a baseline diagnostic, not a completed reduction. The next phase should rank terminal residues by blocked-target impact and expand only the highest-impact crossed sectors.','']
OUT.write_text('\n'.join(lines),encoding='utf-8')
print('Phase-16 crossed IBP baseline: PASS')
print('equations',len(equations),'pivots',len(rules),'target pivots',len(pivot_targets),'remaining',len(remaining),'direct terminals',len(terminal))
print('Output:',OUT)
