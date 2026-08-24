"""Optional scientific-package Phase-83 regression.

Executed by run_v090_validation.bat only when SymPy is importable.  It reruns
fast exact scientific checkpoints for corner, crossed ladder and vacuum
polarization.  The self-energy raw-to-final checkpoint is also rerun.  The
ordinary-ladder heavy master reconstruction remains represented by its exact
72->40->12 reduction table and Phase-81 stored checkpoint unless mpmath is
available and the user explicitly runs the dedicated Phase-81 example.
"""
from __future__ import annotations
import sympy as sp

from qedcalc.operations.corner import corner_phase77_end_to_end_checkpoint
from qedcalc.operations.crossed_ladder import crossed_phase78_end_to_end_checkpoint
from qedcalc.operations.vacuum_polarization import vp_phase79_end_to_end_checkpoint
from qedcalc.operations.self_energy import self_energy_finite_audit


def assert_zero(x, name):
    if sp.simplify(x) != 0:
        raise AssertionError(f"{name} != 0: {x}")

c = corner_phase77_end_to_end_checkpoint()
for key in (
    "sector_route_residual",
    "matching_route_residual",
    "route_to_route_residual",
    "closed_form_residual",
    "combined_ir_log_coefficient",
    "combined_finite_checkpoint_residual",
):
    assert_zero(c[key], f"corner.{key}")

x = crossed_phase78_end_to_end_checkpoint(include_heavy_raw=False)
for key in (
    "projector_residual_F1",
    "projector_residual_F2",
    "endpoint_divergent_residual",
    "final_closed_form_residual",
):
    assert_zero(x[key], f"crossed.{key}")
if x["historical_gap_origin_resolved"] is not False:
    raise AssertionError("historical 1/32 provenance status changed unexpectedly")

v = vp_phase79_end_to_end_checkpoint()
for key in (
    "transverse_residual",
    "on_shell_subtraction_residual",
    "four_dimensional_kernel_residual",
    "outer_insertion_kernel_residual",
    "z_kernel_residual",
    "primitive_derivative_residual",
    "final_closed_form_residual",
):
    assert_zero(v[key], f"vp.{key}")

rho = sp.Symbol("rho", positive=True)
s = self_energy_finite_audit(rho)
assert_zero(s.one_variable_residual, "self_energy.one_variable_residual")
expected_self = sp.log(rho) + sp.Rational(11, 24) - sp.pi**2/18
assert_zero(s.total_asymptotic - expected_self, "self_energy.total_analytic_residual")
# The heavy raw-to-final Phase-80 regeneration remains represented by the
# standard-library release checkpoint; it is intentionally not repeated here.

print("Phase-83 optional scientific regression PASS")
print("corner Phase-77 PASS")
print("crossed Phase-78 PASS")
print("vacuum-polarization Phase-79 PASS")
print("self-energy Phase-80 PASS")
