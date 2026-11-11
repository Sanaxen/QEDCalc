"""Read-only modular audit of completed VP05 sector202 Step51 scratch.

Three-point finite-field checks are diagnostics, never exact target proof.
No protected checkpoint or formal target state is written.
"""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_step51_scratch import (
    STATE, SCRATCH, SEAL, source_context, scratch_config, seal_matches,
    summarize,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, POINTS, modular, sha,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr


def materialize(target, scratch, jobs):
    if len(scratch["done"]) != len(jobs):
        raise RuntimeError("Scratch incomplete")
    rem = {tuple(k): v for k, v in target["remaining"]}
    trace = {int(k): v for k, v in target["source"]}
    for record, (kind, key, _) in zip(scratch["done"], jobs):
        mapping = rem if kind == "remainder" else trace
        k = tuple(key) if kind == "remainder" else int(key)
        if record["value"] == "0":
            mapping.pop(k, None)
        else:
            mapping[k] = record["value"]
    return rem, trace


def modular_invariant(previous_rem, previous_trace, rem, trace, originals,
                      points=POINTS):
    """R51 + source51*IBP equals R50 + source50*IBP, at each field point."""
    z, d = sp.symbols("z d")
    checked = []
    for point in points:
        p = point[0]
        residual = {}

        def add_term(k, v):
            value = (residual.get(k, 0) + v) % p
            if value:
                residual[k] = value
            else:
                residual.pop(k, None)

        for k, v in rem.items():
            add_term(k, modular(expr(v, z, d), z, d, point))
        for k, v in previous_rem.items():
            add_term(k, -modular(expr(v, z, d), z, d, point))
        for rid in set(trace) | set(previous_trace):
            if rid not in originals:
                raise RuntimeError("Missing original IBP row: %s" % rid)
            current = modular(expr(trace[rid], z, d), z, d, point) if rid in trace else 0
            old = modular(expr(previous_trace[rid], z, d), z, d, point) if rid in previous_trace else 0
            factor = (current - old) % p
            if not factor:
                continue
            for term in originals[rid]["terms"]:
                coefficient = modular(expr(term["coefficient"], z, d), z, d, point)
                add_term(tuple(term["key"]), factor * coefficient)
        if residual:
            raise AssertionError(
                "Step51 original-IBP modular invariant failed at %s: %s" %
                (point, sorted(residual)[:5]))
        checked.append(list(point))
    return checked


def audit(target, scratch, pivot, jobs, originals, points=POINTS):
    stats = summarize(scratch, target, pivot, jobs)
    if not stats["complete"]:
        raise RuntimeError("Scratch incomplete")
    rem, trace = materialize(target, scratch, jobs)
    lead = min(tuple(k) for k, _ in target["remaining"])
    if lead in rem or (rem and min(rem) <= lead):
        raise AssertionError("Step51 pivot not eliminated")
    old_rem = {tuple(k): v for k, v in target["remaining"]}
    old_trace = {int(k): v for k, v in target["source"]}
    checked = modular_invariant(old_rem, old_trace, rem, trace, originals, points)
    return {
        "status": "STEP51_COMPLETE_CANDIDATE_MODULAR_AUDIT_NOT_PROOF",
        "coefficients": len(scratch["done"]),
        "verified_points": checked,
        "candidate_metrics": stats,
        "eliminated_pivot": list(lead),
        "formal_target_state_modified": False,
        "protected_source_checkpoint_modified": False,
        "exact_target_proven": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--source-checkpoint", type=Path, default=CHECKPOINT)
    ap.add_argument("--input", type=Path, default=SOURCE)
    ap.add_argument("--certificate", type=Path, default=CERT)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--verified-seal", type=Path, default=SEAL)
    ap.add_argument("--output", type=Path,
                    default=BASE / "vp05_sector202_A_step51_candidate_modular_audit.json")
    args = ap.parse_args()
    inputs = (args.state, args.source_checkpoint, args.input,
              args.certificate, args.scratch, args.verified_seal)
    if args.output.resolve() in {path.resolve() for path in inputs}:
        ap.error("Output must not overwrite a source or protected state")
    if args.output.exists():
        raise FileExistsError("Refusing to overwrite audit report")
    target = json.loads(args.state.read_text(encoding="utf-8-sig"))
    lead, pivot, jobs = source_context(target, args.source_checkpoint)
    config = scratch_config(args.state, args.source_checkpoint, args.input,
                            args.certificate, target, lead, jobs, 9000)
    scratch = json.loads(args.scratch.read_text(encoding="utf-8-sig"))
    if not seal_matches(args.verified_seal, args.scratch, config, scratch):
        raise RuntimeError("Missing/mismatched verified scratch seal")
    records = scratch.get("done")
    if (scratch.get("version") != 1 or scratch.get("config") != config
        or scratch.get("status") != "INTRA_STEP51_SCRATCH_NOT_PROOF"
        or scratch.get("exact_target_proven") is not False
        or not isinstance(records, list) or len(records) != len(jobs)
        or [r.get("id") for r in records] != config["operation_ids"]):
        raise RuntimeError("Scratch metadata, operation order or hashes mismatch")
    if any(not isinstance(r.get("value"), str)
           or r.get("chars") != len(r["value"])
           or len(r["value"]) > config["scratch_max_expression_chars"]
           for r in records):
        raise RuntimeError("Invalid scratch coefficient record")
    if target.get("config", {}).get("max_expression_chars") != 7500:
        raise RuntimeError("Unexpected formal expression safety cap")
    with gzip.open(args.input, "rt", encoding="utf-8") as handle:
        source = json.load(handle)
    if (source.get("status") != "ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED"
        or len(source["rows"]) != 2241):
        raise RuntimeError("Unexpected original IBP source format")
    originals = {r["global_zero_based"]: r for r in source["rows"]}
    report = audit(target, scratch, pivot, jobs, originals)
    report["input_hashes"] = {p.name: sha(p) for p in inputs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print("VP05_SECTOR202_STEP51_CANDIDATE_AUDIT " + json.dumps(report))


if __name__ == "__main__":
    main()
