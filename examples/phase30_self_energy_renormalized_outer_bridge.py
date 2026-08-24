import sympy as sp
from qedcalc.operations.self_energy import self_energy_renormalized_outer_to_GA
r=self_energy_renormalized_outer_to_GA()
print('Phase-30 self-energy renormalized outer bridge')
print('Projector term counts:',r.projector_term_counts)
print('D-denominator q stream:',r.denominator_D_stream)
print('Q-denominator q stream:',r.denominator_Q_stream)
print('Convention normalization:',r.normalization_factor)
print('Generated G_A residual:',r.checkpoint_residual)
print('Phase-30 self-energy renormalized outer bridge: PASS' if r.checkpoint_residual==0 else 'FAIL')
