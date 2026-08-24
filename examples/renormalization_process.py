from pathlib import Path
import sys
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qedcalc.operations.subdiagram import Subdiagram, relation, enumerate_forests
from qedcalc.operations.r_operation import CountertermAssignment, assemble_renormalized_amplitude, renormalization_plan


def md_math(expr):
    return "\n$$\n" + sp.latex(sp.sympify(expr)) + "\n$$\n"


def main():
    eps = sp.Symbol("epsilon")
    A, B = sp.symbols("A B")

    # A schematic two-loop bare amplitude with a one-loop UV subdivergence.
    bare = A / eps + B

    vertex_sub = Subdiagram(
        "vertex_subgraph_1",
        "vertex",
        1,
        {"v2", "v3", "fermion_e2", "fermion_e3", "photon_k"},
        divergence="UV",
        superficial_degree=0,
    )

    assignment = CountertermAssignment(
        vertex_sub,
        -A / eps,
        "one-loop vertex counterterm amplitude",
    )

    result = assemble_renormalized_amplitude(bare, (assignment,), eps)
    plan = renormalization_plan((vertex_sub,), (assignment,))

    lines = []
    lines += ["# Renormalization Process Demo", ""]
    lines += ["## Bare amplitude", "", md_math(bare).strip("\n"), ""]
    lines += ["## Declared UV subdiagram", ""]
    lines += [f"- Name: `{vertex_sub.name}`", f"- Kind: `{vertex_sub.kind}`", f"- Loop order: `{vertex_sub.loop_order}`", ""]
    lines += ["Topology members:", "", "```text", ", ".join(sorted(vertex_sub.members)), "```", ""]
    lines += ["## Counterterm amplitude", "", md_math(assignment.contribution).strip("\n"), ""]
    lines += ["## Renormalized sum", "", md_math(result.total).strip("\n"), ""]
    lines += ["## Remaining pole part", "", md_math(result.pole_part).strip("\n"), ""]
    lines += ["## Finite / regular part", "", md_math(result.finite_or_regular).strip("\n"), ""]
    lines += ["## Forest bookkeeping", ""]
    lines += [f"Compatible forests: `{len(plan['forests'])}`", ""]
    for i, forest in enumerate(plan["forests"], 1):
        names = ", ".join(s.name for s in forest) if forest else "empty forest"
        lines.append(f"- Forest {i}: {names}")
    lines += ["", "## Design rule", ""]
    lines += [
        "QEDCalc does not infer UV subgraphs from a bare algebraic formula alone.",
        "Subdiagram topology is declared explicitly, while algebraic counterterm amplitudes may be generated or supplied separately.",
        "This keeps the physical renormalization decision inspectable and avoids ambiguous automatic guesses.",
        "",
    ]

    out = Path(__file__).resolve().parents[1] / "output" / "renormalization_process.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("Renormalization process demo completed.")
    print(f"Output: {out}")
    print(f"Remaining pole part: {sp.simplify(result.pole_part)}")


if __name__ == "__main__":
    main()
