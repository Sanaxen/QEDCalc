"""Audit Q02 FireFly master-set changes across baseline and one-axis seed extensions.

This does not declare a final basis.  It computes the exact set relations needed
for the next mandatory-union reduction stage.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from three_loop.integral_family_classification import ROOT

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
OUT_JSON = AUDIT_DIR / "three_loop_q02_firefly_master_union_audit.json"
OUT_TXT = AUDIT_DIR / "three_loop_q02_firefly_master_union_audit.txt"
OUT_TARGETS = AUDIT_DIR / "q02_firefly_master_union_targets.txt"

SOURCES = {
    "r8s3d0": AUDIT_DIR / "three_loop_q02_kira_firefly_r8s3d0_audit.json",
    "r9s3d0": AUDIT_DIR / "three_loop_q02_kira_firefly_r9s3d0_boundary_audit.json",
    "r8s4d0": AUDIT_DIR / "three_loop_q02_kira_firefly_r8s4d0_boundary_audit.json",
    "r8s3d1": AUDIT_DIR / "three_loop_q02_kira_firefly_r8s3d1_boundary_audit.json",
}

PATTERN = re.compile(r"Q02_full\s*\[[^\]]+\]")


def _norm(item: str) -> str:
    return re.sub(r"\s+", "", item)


def _load(path: Path) -> tuple[dict[str, object], list[str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    masters = data.get("masters")
    if isinstance(masters, list):
        parsed = [_norm(str(x)) for x in masters if PATTERN.fullmatch(_norm(str(x)))]
    else:
        masters_path = data.get("masters_final")
        if not masters_path:
            raise ValueError(f"no masters or masters_final in {path}")
        mp = Path(str(masters_path))
        if not mp.is_file():
            raise FileNotFoundError(mp)
        parsed = [_norm(x) for x in PATTERN.findall(mp.read_text(encoding="utf-8", errors="replace"))]
    out: list[str] = []
    seen: set[str] = set()
    for item in parsed:
        if item not in seen:
            seen.add(item)
            out.append(item)
    if not out:
        raise ValueError(f"no Q02_full masters parsed from {path}")
    return data, out


def main() -> None:
    errors: list[str] = []
    sets: dict[str, set[str]] = {}
    ordered: dict[str, list[str]] = {}
    source_status: dict[str, object] = {}

    for seed, path in SOURCES.items():
        try:
            data, masters = _load(path)
            ordered[seed] = masters
            sets[seed] = set(masters)
            source_status[seed] = {
                "path": str(path),
                "master_count": len(masters),
                "source_audit_pass": bool(data.get("audit_pass")),
            }
        except Exception as exc:
            errors.append(f"{seed}: {exc}")

    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q02 FireFly master-union audit FAIL")

    names = list(SOURCES)
    union = set().union(*(sets[name] for name in names))
    intersection = set.intersection(*(sets[name] for name in names))

    # Stable deterministic order: baseline first, then newly encountered masters
    # in r+1, s+1, d+1 order.
    union_ordered: list[str] = []
    seen: set[str] = set()
    for name in names:
        for item in ordered[name]:
            if item not in seen:
                seen.add(item)
                union_ordered.append(item)

    pairwise: dict[str, object] = {}
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            a, b = sets[left], sets[right]
            pairwise[f"{left}__{right}"] = {
                "intersection": len(a & b),
                "left_only": len(a - b),
                "right_only": len(b - a),
            }

    per_seed = {
        name: {
            "master_count": len(sets[name]),
            "in_all_four": len(sets[name] & intersection),
            "unique_to_seed": len(sets[name] - set().union(*(sets[n] for n in names if n != name))),
            "missing_from_union": len(union - sets[name]),
        }
        for name in names
    }

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_TARGETS.write_text("\n".join(union_ordered) + "\n", encoding="utf-8")

    result = {
        "canonical_family": "Q02_full",
        "source_status": source_status,
        "master_counts": {name: len(sets[name]) for name in names},
        "intersection_count": len(intersection),
        "union_count": len(union),
        "intersection_masters": sorted(intersection),
        "union_targets": union_ordered,
        "pairwise": pairwise,
        "per_seed": per_seed,
        "next_stage": "mandatory_union_reduction",
        "union_target_file": str(OUT_TARGETS),
        "errors": [],
        "audit_pass": True,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q02 FireFly master-union audit",
        "master counts: " + ", ".join(f"{k}={len(sets[k])}" for k in names),
        f"intersection across all four seeds: {len(intersection)}",
        f"union across all four seeds: {len(union)}",
    ]
    for key, value in pairwise.items():
        lines.append(
            f"{key}: intersection={value['intersection']} left_only={value['left_only']} right_only={value['right_only']}"
        )
    lines += [
        f"union target file: {OUT_TARGETS}",
        "next stage: mandatory union reduction",
        f"audit JSON: {OUT_JSON}",
        f"audit TXT: {OUT_TXT}",
        "QEDCalc Q02 FireFly master-union audit PASS",
    ]
    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
