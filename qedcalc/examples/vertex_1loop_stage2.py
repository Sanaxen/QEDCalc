from pathlib import Path
import sys

from qedcalc import parse_latex, render_latex
from qedcalc.config import load_symbol_table
from qedcalc.operations.propagator import (
    recognize_propagators,
    scalarize_fermion_propagators,
    separate_numerator_denominator,
)
from qedcalc.validation.validator import validate_indices
from qedcalc.history import MarkdownSession


def main():
    root = Path(__file__).resolve().parents[1]
    input_path = root / "input" / "vertex_1loop_integrand.tex"
    symbols_path = root / "symbols.txt"

    try:
        symbols = load_symbol_table(symbols_path)
        source = input_path.read_text(encoding="utf-8")
        expr = parse_latex(source, symbol_table=symbols)
        recognized = recognize_propagators(expr)
        scalarized = scalarize_fermion_propagators(recognized)
        separated = separate_numerator_denominator(scalarized)
        messages = validate_indices(expr)
    except (ValueError, FileNotFoundError) as exc:
        print("\n[QEDCalc ERROR]")
        print(exc)
        print("\nCheck the input expression and symbols.txt.")
        return 1

    print("=== Symbol definitions ===")
    print(symbols_path)
    print("\n=== Input file ===")
    print(input_path)
    print("\n=== Parsed -> LaTeX ===")
    print(render_latex(expr))
    print("\n=== Scalarized fermion propagators ===")
    print(render_latex(scalarized))
    print("\n=== Separated numerator / denominator ===")
    print(render_latex(separated))
    print("\n=== Validation ===")
    for msg in messages:
        print(f"[{msg.level}] {msg.message}")

    out = root / "output" / "vertex_1loop_session.md"
    s = MarkdownSession(out, "QED 1-loop vertex correction - calculation session")
    s.text("Symbol definitions", f"`{symbols_path.relative_to(root)}`\n\n{symbols.to_markdown()}")
    s.text("Input file", f"`{input_path.relative_to(root)}`")
    s.equation("Original input", source.strip())
    s.equation("Parser interpretation", expr)
    s.step(1, "Propagator recognition", expr, recognized,
           "Recognize LaTeX fraction structures as propagator candidates.")
    s.step(2, "Fermion propagator scalarization", recognized, scalarized,
           "Convert fermion propagators into Dirac numerators and scalar denominators.")
    s.step(3, "Numerator / denominator separation", scalarized, separated,
           "Collect numerators from product fractions while preserving factor order, and collect scalar denominators separately.")
    s.text("Index validation", "\n".join(f"- [{m.level}] {m.message}" for m in messages))
    s.save()
    print(f"\nMarkdown session written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
