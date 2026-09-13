"""Demand-artifact readiness audit for the 28 representative Q families.

This module is deliberately lightweight.  It never regenerates projected
scalar traces or native integral mappings.  Instead it inspects already-created
per-diagram integral-index artifacts and reports which representative families
are ready for demand unioning.

A native artifact is considered fully translatable only when its auxiliary
basis convention is known to agree with the representative/induced basis.
Currently Q01 is the established canonical native 12-slot convention.  Other
Q diagrams are reported conservatively until their native family generators
record the corresponding auxiliary-basis metadata.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

from three_loop.q_family_representatives import QRepresentativeFamily


_INTEGRAL_RE = re.compile(r"I\(\s*((?:[-+]?\d+\s*,\s*){11}[-+]?\d+)\s*\)")


@dataclass(frozen=True)
class QDemandArtifactStatus:
    diagram_id: str
    path: str
    exists: bool
    integral_count: int | None
    twelve_slot_parse_ok: bool
    auxiliary_basis_status: str
    full_translation_ready: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "diagram_id": self.diagram_id,
            "path": self.path,
            "exists": self.exists,
            "integral_count": self.integral_count,
            "twelve_slot_parse_ok": self.twelve_slot_parse_ok,
            "auxiliary_basis_status": self.auxiliary_basis_status,
            "full_translation_ready": self.full_translation_ready,
        }


@dataclass(frozen=True)
class QFamilyDemandReadiness:
    representative_id: str
    members: tuple[str, ...]
    member_status: tuple[QDemandArtifactStatus, ...]

    @property
    def union_ready(self) -> bool:
        return all(item.full_translation_ready for item in self.member_status)

    @property
    def available_member_count(self) -> int:
        return sum(item.exists for item in self.member_status)

    def as_dict(self) -> dict[str, object]:
        return {
            "representative_id": self.representative_id,
            "members": list(self.members),
            "available_member_count": self.available_member_count,
            "union_ready": self.union_ready,
            "member_status": [item.as_dict() for item in self.member_status],
        }


def expected_native_demand_path(output_dir: Path, diagram_id: str) -> Path:
    return output_dir / f"3loop_{diagram_id.lower()}_integral_indices.txt"


def parse_native_integral_indices(path: Path) -> tuple[tuple[int, ...], ...]:
    """Parse unique 12-slot I(...) tuples without recomputing any mapping."""
    text = path.read_text(encoding="utf-8", errors="replace")
    found: set[tuple[int, ...]] = set()
    for match in _INTEGRAL_RE.finditer(text):
        values = tuple(int(piece.strip()) for piece in match.group(1).split(","))
        if len(values) == 12:
            found.add(values)
    return tuple(sorted(found))


def _basis_status(diagram_id: str) -> tuple[str, bool]:
    # Q01 is the established native convention used by the current 910-demand
    # and Kira bridge.  Do not infer partner ISP conventions merely from
    # reflection equivalence; each native generator must declare/verify them.
    if diagram_id == "Q01":
        return "canonical_q01_verified", True
    return "native_auxiliary_basis_not_yet_declared", False


def audit_q_family_demand_readiness(
    families: Iterable[QRepresentativeFamily],
    output_dir: Path,
) -> tuple[QFamilyDemandReadiness, ...]:
    reports: list[QFamilyDemandReadiness] = []
    for family in families:
        statuses: list[QDemandArtifactStatus] = []
        for diagram_id in family.members:
            path = expected_native_demand_path(output_dir, diagram_id)
            exists = path.exists()
            parsed_ok = False
            count: int | None = None
            if exists:
                integrals = parse_native_integral_indices(path)
                count = len(integrals)
                parsed_ok = count > 0
            basis_status, basis_ready = _basis_status(diagram_id)
            statuses.append(
                QDemandArtifactStatus(
                    diagram_id=diagram_id,
                    path=str(path),
                    exists=exists,
                    integral_count=count,
                    twelve_slot_parse_ok=parsed_ok,
                    auxiliary_basis_status=basis_status,
                    full_translation_ready=exists and parsed_ok and basis_ready,
                )
            )
        reports.append(
            QFamilyDemandReadiness(
                representative_id=family.representative_id,
                members=family.members,
                member_status=tuple(statuses),
            )
        )
    return tuple(reports)
