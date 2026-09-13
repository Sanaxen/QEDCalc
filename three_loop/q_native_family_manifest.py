"""Explicit native-family metadata for all quenched three-loop Q diagrams.

The representative-family plan proves how each Q01--Q50 denominator family is
related to one of 28 representatives.  This module turns that structural proof
into a stable per-diagram basis contract that later native-demand generators
can write beside their integral-index artifacts.

No projected traces or integral mappings are evaluated here.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Iterable

from three_loop.family_sharing_algebraic import verify_q_reflection_family_algebraically
from three_loop.family_sharing_propagator import verify_reflection_physical_propagators
from three_loop.q_family_representatives import QRepresentativeFamily
from three_loop.registry import ThreeLoopRegistry


def _pair_name(pair: tuple[str, str]) -> str:
    return f"{pair[0]}.{pair[1]}"


def _duplicate_rules_payload(member) -> list[dict[str, object]]:
    return [
        {
            "dependent_index": rule.dependent_index,
            "keep_index": rule.keep_index,
            "scale": str(rule.scale),
        }
        for rule in member.duplicate_rules
    ]


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class QNativeFamilyMemberManifest:
    diagram_id: str
    representative_id: str
    reflected: bool
    physical_rank: int
    independent_representative_physical_indices: tuple[int, ...]
    physical_to_representative: tuple[tuple[int, int], ...]
    duplicate_rules: tuple[dict[str, object], ...]
    auxiliary_basis_mode: str
    auxiliary_basis: tuple[str, ...]
    kira_slot_count: int
    basis_fingerprint: str

    def as_dict(self) -> dict[str, object]:
        return {
            "diagram_id": self.diagram_id,
            "representative_id": self.representative_id,
            "reflected": self.reflected,
            "physical_rank": self.physical_rank,
            "independent_representative_physical_indices": list(
                self.independent_representative_physical_indices
            ),
            "physical_to_representative": [list(pair) for pair in self.physical_to_representative],
            "duplicate_rules": list(self.duplicate_rules),
            "auxiliary_basis_mode": self.auxiliary_basis_mode,
            "auxiliary_basis": list(self.auxiliary_basis),
            "kira_slot_count": self.kira_slot_count,
            "basis_fingerprint": self.basis_fingerprint,
        }


def _member_payload_without_fingerprint(
    family: QRepresentativeFamily,
    member,
    auxiliary_basis_mode: str,
    auxiliary_basis: tuple[str, ...],
) -> dict[str, object]:
    return {
        "diagram_id": member.diagram_id,
        "representative_id": family.representative_id,
        "reflected": member.reflected,
        "physical_rank": family.physical_rank,
        "independent_representative_physical_indices": list(family.independent_physical_indices),
        "physical_to_representative": [list(pair) for pair in member.physical_to_representative],
        "duplicate_rules": _duplicate_rules_payload(member),
        "auxiliary_basis_mode": auxiliary_basis_mode,
        "auxiliary_basis": list(auxiliary_basis),
        "kira_slot_count": family.kira_slot_count,
    }


def build_q_native_family_manifest(
    registry: ThreeLoopRegistry,
    families: Iterable[QRepresentativeFamily],
) -> tuple[QNativeFamilyMemberManifest, ...]:
    """Build a deterministic basis contract for every Q diagram.

    Representative diagrams use their deterministic completion ISP pairs.
    Reflected partners use the algebraically induced auxiliary basis in the
    same slot order.  This is the convention future native-demand artifacts
    must declare in a sidecar before they are considered translation-ready.
    """
    manifests: list[QNativeFamilyMemberManifest] = []

    for family in families:
        representative = registry.get(family.representative_id)
        representative_basis = tuple(_pair_name(pair) for pair in family.completion_isp_pairs)

        for member in family.member_maps:
            if not member.reflected:
                mode = "representative_completion_basis"
                basis = representative_basis
            else:
                target = registry.get(member.diagram_id)
                physical_map = verify_reflection_physical_propagators(representative, target)
                algebraic = verify_q_reflection_family_algebraically(
                    representative, target, physical_map
                )
                if not algebraic.reflection_equivalent:
                    raise ValueError(
                        f"{family.representative_id}<->{member.diagram_id}: reflection proof failed"
                    )
                mode = "induced_from_representative"
                basis = tuple(algebraic.induced_target_isps)

            payload = _member_payload_without_fingerprint(family, member, mode, basis)
            fingerprint = _fingerprint(payload)
            manifests.append(
                QNativeFamilyMemberManifest(
                    diagram_id=member.diagram_id,
                    representative_id=family.representative_id,
                    reflected=member.reflected,
                    physical_rank=family.physical_rank,
                    independent_representative_physical_indices=family.independent_physical_indices,
                    physical_to_representative=member.physical_to_representative,
                    duplicate_rules=tuple(_duplicate_rules_payload(member)),
                    auxiliary_basis_mode=mode,
                    auxiliary_basis=basis,
                    kira_slot_count=family.kira_slot_count,
                    basis_fingerprint=fingerprint,
                )
            )

    manifests.sort(key=lambda item: item.diagram_id)
    ids = [item.diagram_id for item in manifests]
    if len(ids) != 50 or len(set(ids)) != 50:
        raise ValueError(f"expected exactly 50 unique Q member manifests, got {len(ids)}")
    if any(item.kira_slot_count != 12 for item in manifests):
        raise ValueError("every Q native-family manifest must define exactly 12 Kira slots")
    return tuple(manifests)


def manifest_index(
    manifests: Iterable[QNativeFamilyMemberManifest],
) -> dict[str, QNativeFamilyMemberManifest]:
    result = {item.diagram_id: item for item in manifests}
    if len(result) != 50:
        raise ValueError("native-family manifest index must contain all 50 Q diagrams")
    return result
