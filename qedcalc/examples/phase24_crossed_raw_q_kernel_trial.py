from pathlib import Path
from qedcalc.operations.crossed_ladder import (
    crossed_raw_one_variable_kernel_checks,
    crossed_raw_to_canonical_difference,
)

ROOT = Path(__file__).resolve().parents[1]
checks = crossed_raw_one_variable_kernel_checks()
difference = crossed_raw_to_canonical_difference()
assert checks["cutoff_log_coefficient"] == 0
assert checks["unexpected_polylogs"] == ()
assert difference == 0

lines = [
    "# Phase 24: crossed-ladder raw one-variable kernel regeneration", "",
    "The t integral is generated directly from the Phase-23 triangular kernel.", "",
    "A lower cutoff epsilon is retained until the rational and logarithmic sectors are combined. Its logarithmic coefficient cancels exactly:", "",
    "$$", r"C_{\ln\varepsilon}=0.", "$$", "",
    "The resulting one-variable kernel closes on", "",
    "$$", r"1,\quad L,\quad M,\quad L^2,\quad LM,\quad D(q),", "$$", "",
    r"with $L=\ln q$, $M=\ln(1-q)$ and $D(q)=\operatorname{Li}_2(q)-\operatorname{Li}_2(2-1/q)$.", "",
    "Using the audited total-derivative primitive G(q), the exact symbolic check gives", "",
    "$$", r"\mathcal F_{\rm raw}(q)-\frac{d\mathcal G}{dq}-\mathcal F_{\rm can}(q)=0.", "$$", "",
    f"Raw-kernel operation count: **{checks['operation_count']}**.", "",
]
(ROOT / "output" / "phase24_crossed_raw_q_kernel_trial.md").write_text("\n".join(lines), encoding="utf-8")
print("Phase-24 crossed raw q kernel: PASS")
