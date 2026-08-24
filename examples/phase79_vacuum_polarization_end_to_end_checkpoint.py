from pathlib import Path
from qedcalc.operations.vacuum_polarization import vp_phase79_end_to_end_checkpoint

c = vp_phase79_end_to_end_checkpoint()
assert c["transverse_residual"] == 0
assert c["on_shell_subtraction_residual"] == 0
assert c["four_dimensional_kernel_residual"] == 0
assert c["outer_insertion_kernel_residual"] == 0
assert c["z_kernel_residual"] == 0
assert c["primitive_derivative_residual"] == 0
assert c["final_closed_form_residual"] == 0

out = Path(__file__).resolve().parents[1] / "output" / "phase79_vacuum_polarization_end_to_end_checkpoint.md"
out.parent.mkdir(exist_ok=True)
lines = [
    "# Phase 79: vacuum-polarization end-to-end closure checkpoint", "",
    f"Transversality residual: `{c['transverse_residual']}`", "",
    f"On-shell subtraction residual: `{c['on_shell_subtraction_residual']}`", "",
    f"Finite D->4 kernel residual: `{c['four_dimensional_kernel_residual']}`", "",
    f"Outer magnetic insertion residual: `{c['outer_insertion_kernel_residual']}`", "",
    f"z-kernel residual: `{c['z_kernel_residual']}`", "",
    f"Primitive derivative residual: `{c['primitive_derivative_residual']}`", "",
    "Final coefficient:", "", "$$", str(c['final']), "$$", "",
    "Closed form:", "", "$$", str(c['closed_form']), "$$", "",
    f"Final residual: `{c['final_closed_form_residual']}`", "",
]
out.write_text("\n".join(lines), encoding="utf-8")
print("Phase-79 vacuum-polarization end-to-end closure PASS")
print("Output:", out)
