"""Generic one-axis boundary comparison for stage-2 master-basis identification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.master_basis_api import Seed, build_family_spec, compare_master_sets, parse_masters_final

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"


def _parse_seed(text: str) -> Seed:
    import re
    m = re.fullmatch(r"r(\d+)s(\d+)d(\d+)", text.strip())
    if not m:
        raise argparse.ArgumentTypeError("seed must look like r8s3d0")
    return Seed(*(int(x) for x in m.groups()))


def _generic_master_copy(family_id: str, solver: str, seed: Seed) -> Path:
    return AUDIT_DIR / f"{family_id.lower()}_{solver}_{seed.tag}_masters.txt"


def _legacy_master_candidates(family_id: str, seed: Seed) -> list[Path]:
    base = family_id.removesuffix("_full").lower()
    return [
        AUDIT_DIR / f"{base}_{seed.tag}_masters.txt",
        AUDIT_DIR / f"{base}_firefly_{seed.tag}_masters.txt",
        AUDIT_DIR / f"{family_id.lower()}_{seed.tag}_masters.txt",
    ]


def _read_master_file(path: Path, family_id: str) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    import re
    pattern = re.compile(rf"{re.escape(family_id)}\s*\[[^\]]+\]")
    out: list[str] = []
    seen: set[str] = set()
    for item in pattern.findall(text):
        item = re.sub(r"\s+", "", item)
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _resolve_baseline(family_id: str, seed: Seed) -> tuple[Path, list[str]]:
    candidates = [
        _generic_master_copy(family_id, "ordinary", seed),
        _generic_master_copy(family_id, "firefly", seed),
        *_legacy_master_candidates(family_id, seed),
    ]
    for path in candidates:
        masters = _read_master_file(path, family_id)
        if masters:
            return path, masters

    # Last-resort discovery from an existing completed baseline project.
    tag = seed.tag
    hits: list[Path] = []
    for path in (ROOT / "output").glob(f"kira_*{tag}*/results/{family_id}/masters.final"):
        masters = parse_masters_final(path, family_id)
        if masters:
            hits.append(path)
    if len(hits) == 1:
        return hits[0], parse_masters_final(hits[0], family_id)
    raise FileNotFoundError(
        f"no unique baseline master artifact found for {family_id} {seed.tag}; hits={hits}"
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--baseline-seed", type=_parse_seed)
    p.add_argument("--solver", choices=("ordinary", "firefly"), default="firefly")
    args = p.parse_args()

    spec = build_family_spec(args.family)
    baseline_seed = args.baseline_seed or spec.baseline_seed
    boundaries = baseline_seed.one_axis_extensions()
    baseline_path, baseline = _resolve_baseline(spec.family_id, baseline_seed)

    named: dict[str, list[str]] = {baseline_seed.tag: baseline}
    rows: list[dict[str, object]] = []
    errors: list[str] = []

    for seed in boundaries:
        path = _generic_master_copy(spec.family_id, args.solver, seed)
        masters = _read_master_file(path, spec.family_id)
        if not masters:
            errors.append(f"missing boundary master copy: {path}")
            rows.append({"seed": seed.tag, "master_count": 0, "stable": False, "error": str(path)})
            continue
        named[seed.tag] = masters
        base = set(baseline)
        current = set(masters)
        stable = base <= current
        rows.append({
            "seed": seed.tag,
            "master_count": len(masters),
            "retained_baseline": len(base & current),
            "baseline_count": len(base),
            "missing_baseline": sorted(base - current),
            "new_masters": sorted(current - base),
            "stable": stable,
        })

    comparison = compare_master_sets(named) if len(named) > 1 else None
    stable_all = not errors and all(bool(row.get("stable")) for row in rows)
    union_needed = not stable_all and not errors

    stem = f"three_loop_{spec.family_id.lower()}_{args.solver}_{baseline_seed.tag}_boundary_aggregate_audit"
    audit_json = AUDIT_DIR / f"{stem}.json"
    audit_txt = AUDIT_DIR / f"{stem}.txt"
    union_file = AUDIT_DIR / f"{spec.family_id.lower()}_{args.solver}_{baseline_seed.tag}_master_union_targets.txt"
    if comparison is not None:
        union_file.write_text("\n".join(comparison["union"]) + "\n", encoding="utf-8")

    audit = {
        "schema_version": 1,
        "family": spec.family_id,
        "diagrams": list(spec.diagrams),
        "baseline_seed": baseline_seed.tag,
        "baseline_master_source": str(baseline_path),
        "baseline_master_count": len(baseline),
        "boundary_solver": args.solver,
        "boundary_rows": rows,
        "comparison": comparison,
        "stable_under_one_axis_extensions": stable_all,
        "union_reduction_needed": union_needed,
        "union_target_file": str(union_file) if comparison is not None else None,
        "errors": errors,
        "audit_pass": not errors,
    }
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit_json.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc generic master-basis boundary aggregate audit",
        f"family: {spec.family_id}",
        f"diagrams: {list(spec.diagrams)}",
        f"baseline seed: {baseline_seed.tag}",
        f"baseline masters: {len(baseline)}",
        f"baseline source: {baseline_path}",
        f"boundary solver: {args.solver}",
    ]
    for row in rows:
        lines.append(
            f"{row['seed']}: masters={row.get('master_count')} "
            f"retained={row.get('retained_baseline','?')}/{len(baseline)} "
            f"stable={row.get('stable')}"
        )
    if comparison is not None:
        lines.append(f"intersection across available sets: {comparison['intersection_count']}")
        lines.append(f"union across available sets: {comparison['union_count']}")
        lines.append(f"union target file: {union_file}")
    lines.extend([
        f"stable under tested one-axis extensions: {stable_all}",
        f"union reduction needed: {union_needed}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {audit_json}",
        f"audit TXT: {audit_txt}",
        "QEDCalc generic master-basis boundary aggregate audit " + ("PASS" if not errors else "FAIL"),
    ])
    audit_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if errors:
        for item in errors:
            print("ERROR:", item)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
