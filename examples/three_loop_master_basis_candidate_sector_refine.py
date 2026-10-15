"""Apply a restricted exact-sector Kira master-list basis replacement.

Requires a locally saved passing restricted audit and explicitly recovered Kira
master evidence. This changes representatives, not a proven global IBP rank.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from examples.three_loop_master_basis_candidate_closure import _resolve, _read_integrals, _parse_seed, AUDIT_DIR
from examples.three_loop_master_basis_candidate_sector_closure import _sector
from examples.three_loop_master_basis_candidate_firefly_numerator import RECOVERED_MASTER_EVIDENCE


def run(family: str, baseline_text: str, sector: int, seed_text: str, apply: bool) -> None:
    baseline = _parse_seed(baseline_text)
    seed = _parse_seed(seed_text)
    (_, _, _, _, _, _, candidate_path, candidates, _, mode) = _resolve(
        argparse.Namespace(family=family, baseline_seed=baseline_text, solver="masters")
    )
    if mode != "refined-candidate-only":
        raise ValueError(f"expected refined-candidate-only, got {mode}")
    key = (family, baseline.tag, seed.tag, sector)
    evidence = RECOVERED_MASTER_EVIDENCE.get(key)
    if evidence is None:
        raise ValueError(f"no recorded Kira master-identification evidence for {key}")
    audits = AUDIT_DIR / (
        f"three_loop_{family.lower()}_firefly_numerator_"
        f"{baseline.tag}_{seed.tag}_sec{sector}_audit.json"
    )
    audit = json.loads(audits.read_text(encoding="utf-8"))
    old = [x for x in candidates if _sector(x) == sector]
    masters = [x for x in evidence["reported_masters"] if _sector(x) == sector]
    if (
        audit.get("audit_pass") is not True
        or audit.get("sector") != sector
        or audit.get("family") != family
        or audit.get("firefly_seed") != seed.tag
        or audit.get("baseline_seed") != baseline.tag
        or set(audit.get("targets", [])) != set(old)
        or set(old) != set(evidence["mandatory_targets"])
        or len(old) != len(evidence["mandatory_targets"])
        or len(masters) != len(old)
        or len(set(masters)) != len(masters)
        or not set(masters).issubset(set(evidence["reported_masters"]))
        or any(_sector(x) != sector for x in masters)
    ):
        raise ValueError("audit, candidate or recovered Kira evidence mismatch; refusing modification")
    if set(masters) & (set(candidates) - set(old)):
        raise ValueError("replacement collides with existing candidates in another sector")
    updated = []
    inserted = False
    for x in candidates:
        if _sector(x) == sector:
            if not inserted:
                updated.extend(masters)
                inserted = True
        else:
            updated.append(x)
    if len(updated) != len(candidates) or len(set(updated)) != len(updated):
        raise ValueError("basis cardinality or uniqueness changed unexpectedly")
    new_sectors = {_sector(x) for x in updated}
    if new_sectors != {_sector(x) for x in candidates}:
        raise ValueError("sector composition changed unexpectedly")
    report = {
        "schema_version": 1,
        "stage": "restricted_exact_sector_basis_replacement",
        "family": family, "baseline_seed": baseline.tag,
        "restricted_seed": seed.tag, "sector": sector,
        "audit_source": str(audits),
        "evidence_source": evidence["source"],
        "original_candidate_file": str(candidate_path),
        "old_sector_candidates": old,
        "new_sector_masters": masters,
        "old_count": len(candidates), "new_count": len(updated),
        "representative_replacement": True,
        "global_basis_closure_proven": False,
        "note": "Initiate-stage classification is not an exported coefficient identity; revalidate global closure.",
    }
    destination = candidate_path.with_name(candidate_path.stem + f"_sector{sector}_refined.txt")
    destination.write_text("\n".join(updated) + "\n", encoding="utf-8")
    report_path = AUDIT_DIR / f"three_loop_{family.lower()}_{baseline.tag}_sector{sector}_basis_replacement.json"
    report["proposed_candidate_file"] = str(destination)
    report["applied"] = bool(apply)
    if apply:
        backup = candidate_path.with_name(candidate_path.name + f".before_sector{sector}")
        if backup.exists():
            raise FileExistsError(f"backup already exists; refusing overwrite: {backup}")
        backup.write_bytes(candidate_path.read_bytes())
        candidate_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
        report["backup_file"] = str(backup)
        if _read_integrals(candidate_path, family) != updated:
            raise RuntimeError("post-write verification failed; restore from backup")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", default="VP05_full")
    p.add_argument("--baseline-seed", default="r8s3d0")
    p.add_argument("--sector", type=int, default=202)
    p.add_argument("--restricted-seed", default="r6s6d2")
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    run(a.family, a.baseline_seed, a.sector, a.restricted_seed, a.apply)


if __name__ == "__main__":
    main()
