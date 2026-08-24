from pathlib import Path
import sympy as sp

from qedcalc.operations.ladder_assembly import (
    compose_ladder_projector_with_reduction,
    ladder_basis_z_pole_residues,
    ladder_projector_leading_z_pole_cancellation,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'phase12_ladder_assembly_trial.md'
D,z = sp.symbols('D z')
m2 = sp.Integer(1)

assembly = compose_ladder_projector_with_reduction(
    ROOT/'data'/'ladder_corrected_spin_sum_72_coefficients.csv',
    ROOT/'data'/'ladder_corrected_40target_12basis_symbolic_reduction.csv',
)
residues = ladder_basis_z_pole_residues(assembly.basis_coefficients, z)
leading = ladder_projector_leading_z_pole_cancellation(
    assembly.basis_coefficients, D=D, mass_squared=m2, z=z,
)
assert leading == 0

lines = [
    '# Phase 12: ordinary-ladder projector/reduction assembly', '',
    'The corrected 72 raw projector monomials are first canonicalized under the ordinary-ladder graph symmetries and then composed with the exact 40-target x 12-basis symbolic IBP matrix.', '',
    f'- Corrected raw monomials: **72**',
    f'- Symmetry-canonical targets: **{len(assembly.canonical_target_coefficients)}**',
    f'- Terminal basis size: **{len(assembly.basis_coefficients)}**', '',
    '## Leading z-pole audit', '',
    'Several individual basis coefficients contain a simple magnetic-projector pole `1/z`. No `1/z^2` pole remains after composition.', '',
]
for i,r in enumerate(residues):
    if r != 0:
        lines += [f'Basis {i} residue:', '', '$$', sp.latex(r), '$$', '']
lines += [
    'After inserting the exact v0.43 values of all twelve basis integrals at z=0, the coefficient of the complete `1/z` term is', '',
    '$$', sp.latex(leading), '$$', '',
    'so the leading projector singularity cancels exactly.', '',
    '## What remains for the finite z->0 limit', '',
    'Because some basis coefficients have `C_i(z)=r_i/z+c_i+...`, the finite term also contains `r_i I_i\'(0)`. Therefore the exact z=0 basis values alone are not sufficient. The next stage is to derive and IBP-reduce the first z-derivatives of basis 0, 1, 3, 5, 6, 7, and 8 (zero weights can be skipped), then combine them with the regular coefficient parts and perform the epsilon expansion.', '',
]
OUT.write_text('\n'.join(lines), encoding='utf-8')
print('Phase-12 assembly audit: PASS')
print('72 raw monomials ->', len(assembly.canonical_target_coefficients), 'canonical targets -> 12 basis integrals')
print('nonzero derivative weights:', [i for i,r in enumerate(residues) if r != 0])
print('complete 1/z coefficient:', leading)
print('Output:', OUT)
