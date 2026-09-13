"""Plan projected-scalar artifacts for the 28 representative Q families.

This is deliberately metadata-only.  It does not parse projected expressions,
run traces, invoke FORM/Kira, or regenerate native integral mappings.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from three_loop.q_family_representatives import build_q_representative_families
from three_loop.q_native_family_manifest import build_q_native_family_manifest, manifest_index
from three_loop.registry import ThreeLoopRegistry


REGISTRY_PATH = ROOT / "data" / "three_loop_topologies.json"
OUTPUT_DIR = ROOT / "output"
REPORT_PATH = OUTPUT_DIR / "3loop_q_representative_projected_scalar_plan.json"


def _artifact_paths(diagram_id: str) -> dict[str, Path]:
    stem = f"3loop_{diagram_id.lower()}"
    return {
        "projected_scalar": OUTPUT_DIR / f"{stem}_projected_scalar_pq.txt",
        "projected_scalar_meta": OUTPUT_DIR / f"{stem}_projected_scalar_pq.meta.json",
        "integral_indices": OUTPUT_DIR / f"{stem}_integral_indices.txt",
        "integral_indices_meta": OUTPUT_DIR / f"{stem}_integral_indices.meta.json",
    }


def main() -> int:
    registry = ThreeLoopRegistry.from_json(REGISTRY_PATH)
    families = build_q_representative_families(registry)
    manifests = build_q_native_family_manifest(registry, families)
    manifest_by_id = manifest_index(manifests)

    rows: list[dict[str, object]] = []
    for family in families:
        rep = family.representative_id
        manifest = manifest_by_id[rep]
        paths = _artifact_paths(rep)
        projected_exists = paths["projected_scalar"].is_file()
        indices_exists = paths["integral_indices"].is_file()

        if rep == "Q01" and projected_exists and indices_exists:
            state = "legacy_ready"
            proof = "legacy_q01_canonical_verified"
        elif projected_exists:
            state = "projected_scalar_exists"
            proof = "basis_sidecar_required_before_new_native_mapping"
        else:
            state = "projected_scalar_missing"
            proof = "representative_generation_required"

        rows.append(
            {
                "representative_id": rep,
                "members": list(family.members),
                "member_count": len(family.members),
                "physical_rank": manifest.physical_rank,
                "auxiliary_basis": list(manifest.auxiliary_basis),
                "basis_fingerprint": manifest.basis_fingerprint,
                "state": state,
                "basis_proof": proof,
                "projected_scalar_path": str(paths["projected_scalar"]),
                "projected_scalar_exists": projected_exists,
                "projected_scalar_size_bytes": (
                    paths["projected_scalar"].stat().st_size if projected_exists else None
                ),
                "projected_scalar_meta_path": str(paths["projected_scalar_meta"]),
                "integral_indices_path": str(paths["integral_indices"]),
                "integral_indices_exists": indices_exists,
                "integral_indices_meta_path": str(paths["integral_indices_meta"]),
            }
        )

    rows.sort(key=lambda item: str(item["representative_id"]))
    missing = [row for row in rows if not row["projected_scalar_exists"]]
    existing = [row for row in rows if row["projected_scalar_exists"]]

    report = {
        "schema_version": 1,
        "representative_family_count": len(rows),
        "representatives_with_projected_scalar": len(existing),
        "representatives_missing_projected_scalar": len(missing),
        "representatives": rows,
        "generation_contract": {
            "scope": "representative families only; reflected members are not separately projected at this stage",
            "projected_scalar_naming": "output/3loop_<representative>_projected_scalar_pq.txt",
            "metadata_naming": "output/3loop_<representative>_projected_scalar_pq.meta.json",
            "metadata_required_fields": [
                "diagram_id",
                "representative_id",
                "basis_fingerprint",
                "physical_rank",
                "auxiliary_basis",
            ],
            "q01_policy": "preserve existing Q01 projected scalar and 910-integral mapping; never regenerate as part of this plan",
        },
        "next_stage": (
            "Refactor/reuse the existing Q01 projected-scalar pipeline into a representative-aware generator, "
            "then validate one missing representative before scheduling the remaining representatives."
        ),
        "scope_note": (
            "Planning only. No projected scalar is parsed or generated; no native mapping, FORM, Kira, Fermat, or FireFly job is run."
        ),
    }

    if len(rows) != 28:
        raise ValueError(f"expected 28 representative Q families, got {len(rows)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"representative Q families: {len(rows)}")
    print(f"representatives with projected scalar: {len(existing)}")
    print(f"representatives missing projected scalar: {len(missing)}")

    print("\nExisting representative projected scalars:")
    if existing:
        for row in existing:
            size = int(row["projected_scalar_size_bytes"] or 0)
            print(
                f"  {row['representative_id']}: {size:,} bytes, "
                f"state={row['state']}, members={','.join(row['members'])}"
            )
    else:
        print("  none")

    print("\nMissing representative projected scalars:")
    if missing:
        for row in missing:
            basis = ", ".join(row["auxiliary_basis"])
            print(
                f"  {row['representative_id']}: rank={row['physical_rank']}, "
                f"members={','.join(row['members'])}, basis=[{basis}], "
                f"fingerprint={str(row['basis_fingerprint'])[:16]}..."
            )
    else:
        print("  none")

    print(f"\nreport: {REPORT_PATH}")
    print("Three-loop Q representative projected-scalar plan PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
