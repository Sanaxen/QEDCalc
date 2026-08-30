from pathlib import Path

from qedcalc import __version__
from qedcalc.config import load_conventions
from qedcalc.history.markdown_session import MarkdownSession


def main():
    root = Path(__file__).resolve().parents[1]
    cfg = load_conventions(root / "conventions.txt")
    print(f"QEDCalc v{__version__} conventions")
    print(f"Source: {cfg.source_path}")
    print(f"Metric signature: {cfg.metric_signature}")
    print(f"Gauge: {cfg.gauge}")
    print(f"Renormalization scheme: {cfg.renormalization_scheme}")
    print(f"Dim-reg subtraction: {cfg.dimreg_subtraction}")
    print(f"Compact outer one-loop prefactor: {cfg.compact_outer_one_loop_prefactor_latex()}")

    out = root / "output" / "conventions.md"
    s = MarkdownSession(out, "QEDCalc conventions")
    s.text("Version", f"QEDCalc v{__version__}")
    s.text("Source", str(cfg.source_path))
    s.text("Loaded conventions", cfg.to_markdown())
    s.equation("Standard one-loop normalization", cfg.standard_loop_prefactor_latex(1))
    s.equation("Standard two-loop normalization", cfg.standard_loop_prefactor_latex(2))
    s.equation("One-loop subdiagram-owned normalization", cfg.subdiagram_prefactor_latex(1))
    s.equation("Outer prefactor after contracting one loop from a two-loop graph", cfg.compact_outer_one_loop_prefactor_latex())
    s.save()
    print(f"Markdown: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
