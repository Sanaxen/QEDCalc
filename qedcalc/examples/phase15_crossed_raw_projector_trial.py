from pathlib import Path
import sympy as sp
from qedcalc.parser.qed_latex import parse_loop_integral_latex
from qedcalc.operations.crossed_ladder import (
    analyze_raw_crossed_ladder,
    derive_crossed_scalar_product_rules_from_family,
    crossed_general_q_projector_result,
)
from qedcalc.operations.ladder import write_ladder_general_q_integral_table_csv

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'input'/'crossed_ladder_2loop_bare.tex').read_text(encoding='utf-8')
raw=analyze_raw_crossed_ladder(parse_loop_integral_latex(source))
result=crossed_general_q_projector_result(raw)
csv_path=write_ladder_general_q_integral_table_csv(result.integral_table,ROOT/'output'/'crossed_corrected_spin_sum_95_coefficients.csv')
rules=derive_crossed_scalar_product_rules_from_family()
lines=['# Phase 15: crossed-ladder raw corrected-projector bridge','',
       'The complete bare crossed-ladder LaTeX input is parsed directly. The fourth electron denominator is p-l, not p-k, so a dedicated scalar-product basis is derived rather than reusing the ordinary-ladder family.','',
       f'Electron labels: `{raw.electron_labels}`','',
       f'Bare family index: `{raw.base_integral_index.as_tuple()}`','',
       '## Derived scalar-product rules','']
for k,v in rules.items():
    lines += ['$$',sp.latex(k)+r'='+sp.latex(v),'$$','']
lines += ['## Corrected spin-sum projector','',
          f'Generated scalar-integral monomials: **{len(result.integral_table)}**.','',
          f'CSV: `{csv_path.relative_to(ROOT)}`','',
          'The next stage is crossed-family symmetry/zero-sector analysis and bounded IBP/Laporta closure.','']
(ROOT/'output'/'phase15_crossed_raw_projector_trial.md').write_text('\n'.join(lines),encoding='utf-8')
print('Phase-15 crossed raw projector: PASS')
print('monomials:',len(result.integral_table))
print('CSV:',csv_path)
