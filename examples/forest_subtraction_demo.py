from pathlib import Path
import sys
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qedcalc.operations.subdiagram import Subdiagram, enumerate_forests, relation
from qedcalc.operations.forest import (
    TaylorSubtractionSpec, taylor_operator, bphz_local_counterterm,
    bphz_subtract, contract_graph, forest_formula,
)


def md_math(expr):
    return "\n$$\n" + sp.latex(sp.sympify(expr)) + "\n$$\n"


def main():
    p, q = sp.symbols("p q")

    # Schematic subdiagram amplitudes used only to demonstrate the local
    # Taylor projectors.  Topology and algebra stay explicitly separate.
    vertex = Subdiagram(
        "gamma_V", "vertex", 1, {"v1", "e1", "e2"},
        divergence="UV", superficial_degree=0,
    )
    self_energy = Subdiagram(
        "gamma_SE", "self_energy", 1, {"e4", "v4"},
        divergence="UV", superficial_degree=1,
    )
    overlap = Subdiagram(
        "gamma_O", "vertex", 1, {"e2", "e3", "v3"},
        divergence="UV", superficial_degree=0,
    )

    v_amp = 3 + 5*p + 7*p**2
    se_amp = 11 + 13*q + 17*q**2
    v_spec = TaylorSubtractionSpec(vertex, (p,))
    se_spec = TaylorSubtractionSpec(self_energy, (q,))

    graph_members = {"v1", "e1", "e2", "e3", "e4", "v4", "tail"}

    # A disjoint two-subgraph example so all four forests exist.
    forests = enumerate_forests((vertex, self_energy))
    amplitudes = {
        frozenset(): sp.Symbol("I_G"),
        frozenset({"gamma_V"}): sp.Symbol("I_G_over_V"),
        frozenset({"gamma_SE"}): sp.Symbol("I_G_over_SE"),
        frozenset({"gamma_V", "gamma_SE"}): sp.Symbol("I_G_over_V_SE"),
    }

    def provider(cg):
        return amplitudes[frozenset(s.name for s in cg.forest)]

    forest_result = forest_formula("G", graph_members, (vertex, self_energy), provider)

    lines = ["# Zimmermann / BPHZ Forest Demo", ""]
    lines += ["## Local Taylor subtraction", ""]
    lines += ["### Vertex subdiagram amplitude", "", md_math(v_amp).strip("\n"), ""]
    lines += [f"Taylor degree: `{v_spec.degree}`", ""]
    lines += ["Taylor projector result", "", md_math(taylor_operator(v_amp, (p,), v_spec.degree)).strip("\n"), ""]
    lines += ["Local BPHZ counterterm", "", md_math(bphz_local_counterterm(v_amp, v_spec)).strip("\n"), ""]
    lines += ["Subtracted subdiagram amplitude", "", md_math(bphz_subtract(v_amp, v_spec)).strip("\n"), ""]

    lines += ["### Electron self-energy subdiagram amplitude", "", md_math(se_amp).strip("\n"), ""]
    lines += [f"Taylor degree: `{se_spec.degree}`", ""]
    lines += ["Taylor projector result", "", md_math(taylor_operator(se_amp, (q,), se_spec.degree)).strip("\n"), ""]
    lines += ["Local BPHZ counterterm", "", md_math(bphz_local_counterterm(se_amp, se_spec)).strip("\n"), ""]
    lines += ["Subtracted subdiagram amplitude", "", md_math(bphz_subtract(se_amp, se_spec)).strip("\n"), ""]

    lines += ["## Contracted graph metadata", ""]
    for forest in forests:
        cg = contract_graph("G", graph_members, forest)
        names = ", ".join(s.name for s in forest) if forest else "empty forest"
        lines += [f"### Forest: {names}", ""]
        lines += ["```text", "Members: " + ", ".join(sorted(cg.members)), "```", ""]

    lines += ["## Forest-formula sign structure", ""]
    lines += ["The amplitude provider is explicit; QEDCalc does not infer contracted amplitudes from the bare formula alone.", ""]
    for c in forest_result.contributions:
        names = ", ".join(s.name for s in c.forest) if c.forest else "empty forest"
        lines += [f"- `{names}`: sign = `{c.sign}`"]
    lines += ["", "Forest sum", "", md_math(forest_result.total).strip("\n"), ""]

    lines += ["## Overlapping-subdiagram check", ""]
    lines += [f"Relation between `{vertex.name}` and `{overlap.name}`: `{relation(vertex, overlap)}`", ""]
    lines += ["They cannot appear together in one Zimmermann forest.", ""]

    lines += ["## Important design boundary", ""]
    lines += [
        "Topology contraction is automatic after subdiagrams are declared.",
        "Taylor subtraction is automatic after the external variables and subtraction degree are declared.",
        "The algebraic amplitude associated with each contracted graph remains explicit and is supplied by the caller/evaluator.",
        "This avoids reconstructing graph topology from a bare algebraic expression where that information is no longer unique.",
        "",
    ]

    out = ROOT / "output" / "forest_subtraction_demo.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("Zimmermann/BPHZ forest demo completed.")
    print(f"Output: {out}")
    print(f"Compatible forests: {len(forests)}")


if __name__ == "__main__":
    main()
