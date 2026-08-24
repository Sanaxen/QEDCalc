from pathlib import Path
from qedcalc.operations.crossed_ladder import crossed_automatic_hermite_checks

ROOT = Path(__file__).resolve().parents[1]
c = crossed_automatic_hermite_checks()
assert c["G_difference"] == 0
assert c["canonical_difference"] == 0
assert c["raw_reconstruction_difference"] == 0

lines = [
    "# Phase 25: automatic crossed-ladder Hermite reduction", "",
    "The raw one-variable kernel is reduced without using a stored R,T,U,V,P,Q,Z table.", "",
    "The generated total-derivative coefficients are:", "",
]
for name in ("R", "T", "U", "V", "P", "Q", "Z"):
    lines += [f"## {name}(q)", "", "$$", str(c[name]), "$$", ""]
lines += [
    "The automatically generated primitive agrees with the audited primitive exactly,", "",
    "$$", r"\mathcal G_{\rm auto}(q)-\mathcal G_{\rm audited}(q)=0.", "$$", "",
    "The square-free remainder agrees with the audited canonical kernel exactly,", "",
    "$$", r"\mathcal F_{\rm can,auto}(q)-\mathcal F_{\rm can,audited}(q)=0.", "$$", "",
    "Finally,", "",
    "$$", r"\mathcal F_{\rm raw}(q)-\frac{d\mathcal G_{\rm auto}}{dq}-\mathcal F_{\rm can,auto}(q)=0.", "$$", "",
]
(ROOT / "output" / "phase25_crossed_automatic_hermite_trial.md").write_text("\n".join(lines), encoding="utf-8")
print("Phase-25 crossed automatic Hermite reduction: PASS")
