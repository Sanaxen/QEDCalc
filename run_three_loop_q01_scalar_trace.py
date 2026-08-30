from __future__ import annotations

from pathlib import Path
import json
import time
import sympy as sp

from three_loop import (
    ThreeLoopRegistry,
    build_topology_projected_trace,
    reduce_projected_trace_to_scalar_products,
)


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "three_loop_topologies.json"
OUTDIR = ROOT / "output"


def main() -> int:
    OUTDIR.mkdir(exist_ok=True)
    reg = ThreeLoopRegistry.from_json(DATA)
    q01 = reg.get("Q01")
    D, z = sp.symbols("D z")

    print("QEDCalc Q01 finite-q D-dimensional scalar trace reduction")
    t0 = time.perf_counter()
    projected = build_topology_projected_trace(q01, D=D, z=z)
    t1 = time.perf_counter()
    print(f"projector trace build: {t1-t0:.3f} s")

    reduced = reduce_projected_trace_to_scalar_products(projected, D_name="D")
    t2 = time.perf_counter()
    print(f"scalar trace reduction: {t2-t1:.3f} s")

    expression_path = OUTDIR / "3loop_q01_projected_scalar.txt"
    expression_path.write_text(str(reduced.expression), encoding="utf-8")

    summary = {
        "diagram_id": reduced.diagram_id,
        "elapsed_build_seconds": t1 - t0,
        "elapsed_reduce_seconds": t2 - t1,
        "operation_count": int(sp.count_ops(reduced.expression)),
        "scalar_product_atom_count": len(reduced.scalar_product_atoms),
        "scalar_product_atoms": list(reduced.scalar_product_atoms),
        "has_D": bool(reduced.expression.has(D)),
        "has_z": bool(reduced.expression.has(z)),
        "output": str(expression_path.relative_to(ROOT)),
    }
    summary_path = OUTDIR / "3loop_q01_projected_scalar_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"operation count: {summary['operation_count']}")
    print(f"scalar-product atoms: {summary['scalar_product_atom_count']}")
    print(f"generated: {expression_path}")
    print(f"generated: {summary_path}")
    print("Q01 scalar trace reduction PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
