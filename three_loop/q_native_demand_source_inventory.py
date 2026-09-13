"""Lightweight inventory of native Q demand inputs and artifacts.

This module never parses projected scalar expressions and never regenerates
integral mappings.  It only inspects file existence/size plus optional basis
sidecars so that expensive mapping work can be scheduled deliberately.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from three_loop.q_native_family_manifest import QNativeFamilyMemberManifest


@dataclass(frozen=True)
class QNativeDemandSourceStatus:
    diagram_id: str
    representative_id: str
    projected_scalar_path: str
    projected_scalar_exists: bool
    projected_scalar_size_bytes: int | None
    integral_indices_path: str
    integral_indices_exists: bool
    sidecar_path: str
    sidecar_exists: bool
    sidecar_fingerprint_matches: bool
    basis_proven: bool
    basis_proof: str
    new_mapping_candidate: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "diagram_id": self.diagram_id,
            "representative_id": self.representative_id,
            "projected_scalar_path": self.projected_scalar_path,
            "projected_scalar_exists": self.projected_scalar_exists,
            "projected_scalar_size_bytes": self.projected_scalar_size_bytes,
            "integral_indices_path": self.integral_indices_path,
            "integral_indices_exists": self.integral_indices_exists,
            "sidecar_path": self.sidecar_path,
            "sidecar_exists": self.sidecar_exists,
            "sidecar_fingerprint_matches": self.sidecar_fingerprint_matches,
            "basis_proven": self.basis_proven,
            "basis_proof": self.basis_proof,
            "new_mapping_candidate": self.new_mapping_candidate,
        }


def _read_sidecar_fingerprint(path: Path) -> str | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    value = payload.get("basis_fingerprint")
    return value if isinstance(value, str) else None


def inventory_q_native_demand_sources(
    manifests: Iterable[QNativeFamilyMemberManifest],
    output_dir: Path,
) -> tuple[QNativeDemandSourceStatus, ...]:
    statuses: list[QNativeDemandSourceStatus] = []
    for manifest in manifests:
        stem = f"3loop_{manifest.diagram_id.lower()}"
        projected = output_dir / f"{stem}_projected_scalar_pq.txt"
        indices = output_dir / f"{stem}_integral_indices.txt"
        sidecar = output_dir / f"{stem}_integral_indices.meta.json"

        projected_exists = projected.is_file()
        indices_exists = indices.is_file()
        sidecar_exists = sidecar.is_file()
        sidecar_fingerprint = _read_sidecar_fingerprint(sidecar) if sidecar_exists else None
        sidecar_matches = sidecar_fingerprint == manifest.basis_fingerprint

        # Q01 predates the sidecar contract.  Its 910-integral artifact and
        # canonical basis are already independently established, so preserve it
        # as the single legacy exception without rewriting/recomputing it.
        if manifest.diagram_id == "Q01" and indices_exists:
            basis_proven = True
            basis_proof = "legacy_q01_canonical_verified"
        elif sidecar_matches:
            basis_proven = True
            basis_proof = "manifest_fingerprint_sidecar"
        else:
            basis_proven = False
            basis_proof = "missing_or_mismatched_basis_sidecar"

        statuses.append(
            QNativeDemandSourceStatus(
                diagram_id=manifest.diagram_id,
                representative_id=manifest.representative_id,
                projected_scalar_path=str(projected),
                projected_scalar_exists=projected_exists,
                projected_scalar_size_bytes=projected.stat().st_size if projected_exists else None,
                integral_indices_path=str(indices),
                integral_indices_exists=indices_exists,
                sidecar_path=str(sidecar),
                sidecar_exists=sidecar_exists,
                sidecar_fingerprint_matches=sidecar_matches,
                basis_proven=basis_proven,
                basis_proof=basis_proof,
                new_mapping_candidate=projected_exists and not indices_exists,
            )
        )

    statuses.sort(key=lambda item: item.diagram_id)
    return tuple(statuses)
