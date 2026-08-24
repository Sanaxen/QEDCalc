from pathlib import Path
import sympy as sp
from qedcalc.operations.self_energy import self_energy_phase80_end_to_end_checkpoint
rho=sp.Symbol('rho', positive=True)
c=self_energy_phase80_end_to_end_checkpoint(rho)
checks=[
    all(x==0 for x in c.raw_sample_residuals),
    c.raw_uv_residual==0,
    c.renormalized_GA_residual==0,
    c.total_residual==0,
    c.ir_cancellation_residual==0,
]
text=f'''# Phase 80: self-energy insertion end-to-end checkpoint\n\nRaw sample residuals: `{c.raw_sample_residuals}`\n\nRaw UV residual: `{c.raw_uv_residual}`\n\nRenormalized G_A residual: `{c.renormalized_GA_residual}`\n\nFinite part:\n\n$$\n{sp.latex(c.finite_part)}\n$$\n\nIR part:\n\n$$\n{sp.latex(c.ir_part)}\n$$\n\nTotal asymptotic:\n\n$$\n{sp.latex(c.total_asymptotic)}\n$$\n\nSelf-energy coefficient of $\\log(1/\\rho)$: `{c.self_energy_log_coefficient}`\n\nCorner coefficient of $\\log(1/\\rho)$: `{c.corner_log_coefficient}`\n\nIR cancellation residual: `{c.ir_cancellation_residual}`\n'''
out=Path(__file__).resolve().parents[1]/'output'/'phase80_self_energy_end_to_end_checkpoint.md'
out.parent.mkdir(exist_ok=True)
out.write_text(text, encoding='utf-8')
if not all(checks):
    raise SystemExit('Phase-80 self-energy end-to-end closure FAIL')
print('Phase-80 self-energy end-to-end closure PASS')
print('Output:', out)
