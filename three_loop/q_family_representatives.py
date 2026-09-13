"""Canonical representative families and index translation for Q01--Q50.

The quenched three-loop vertex registry contains 50 Q diagrams.  Reflection
analysis proves 22 diagram pairs are algebraically equivalent.  This module
turns those proofs into a deterministic set of representative IBP families and
provides a physical-index translator from every member diagram to its
representative.

Rank-deficient families are normalized first by merging exactly duplicate
physical propagators.  Their representative Kira layout is then

    independent physical denominators + completion ISPs = 12 slots.

For reflected partners the ISP basis is *induced* from the representative
basis.  Therefore auxiliary exponents keep their order under translation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from qedcalc.operations.denominator_normalization import (
    DuplicateDenominatorRule,
    normalize_duplicate_denominator_powers,
)
from three_loop.duplicate_propagator_preprocess import build_duplicate_propagator_plan
from three_loop.family_sharing import analyze_three_loop_family_sharing
from three_loop.family_sharing_algebraic import (
    q_completion_isp_pairs,
    q_physical_rank,
    verify_q_reflection_family_algebraically,
)
from three_loop.family_sharing_propagator import verify_reflection_physical_propagators
from three_loop.registry import ThreeLoopRegistry, ThreeLoopTopology


@dataclass(frozen=True)
class QFamilyMemberMap:
    diagram_id: str
    representative_id: str
    physical_to_representative: tuple[tuple[int, int], ...]
    duplicate_rules: tuple[DuplicateDenominatorRule, ...]
    auxiliary_count: int
    reflected: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "diagram_id": self.diagram_id,
            "representative_id": self.representative_id,
            "physical_to_representative": [list(pair) for pair in self.physical_to_representative],
            "duplicate_rules": [
                {
                    "dependent_index": rule.dependent_index,
                    "keep_index": rule.keep_index,
                    "scale": str(rule.scale),
                }
                for rule in self.duplicate_rules
            ],
            "auxiliary_count": self.auxiliary_count,
            "reflected": self.reflected,
        }


@dataclass(frozen=True)
class QRepresentativeFamily:
    representative_id: str
    members: tuple[str, ...]
    physical_rank: int
    independent_physical_indices: tuple[int, ...]
    completion_isp_pairs: tuple[tuple[str, str], ...]
    member_maps: tuple[QFamilyMemberMap, ...]

    @property
    def physical_slot_count(self) -> int:
        return len(self.independent_physical_indices)

    @property
    def auxiliary_slot_count(self) -> int:
        return len(self.completion_isp_pairs)

    @property
    def kira_slot_count(self) -> int:
        return self.physical_slot_count + self.auxiliary_slot_count

    @property
    def requires_duplicate_preprocessing(self) -> bool:
        return self.physical_rank < 9

    def as_dict(self) -> dict[str, object]:
        return {
            "representative_id": self.representative_id,
            "members": list(self.members),
            "physical_rank": self.physical_rank,
            "independent_physical_indices": list(self.independent_physical_indices),
            "completion_isp_pairs": [list(pair) for pair in self.completion_isp_pairs],
            "physical_slot_count": self.physical_slot_count,
            "auxiliary_slot_count": self.auxiliary_slot_count,
            "kira_slot_count": self.kira_slot_count,
            "requires_duplicate_preprocessing": self.requires_duplicate_preprocessing,
            "member_maps": [member.as_dict() for member in self.member_maps],
        }


def _duplicate_rules_for(topology: ThreeLoopTopology) -> tuple[DuplicateDenominatorRule, ...]:
    rank = q_physical_rank(topology)
    if rank == 9:
        return ()
    return build_duplicate_propagator_plan(topology).duplicate_rules


def _independent_indices_for(topology: ThreeLoopTopology) -> tuple[int, ...]:
    rank = q_physical_rank(topology)
    if rank == 9:
        return tuple(range(1, 10))
    return build_duplicate_propagator_plan(topology).independent_indices


def _identity_physical_map() -> tuple[tuple[int, int], ...]:
    return tuple((i, i) for i in range(1, 10))


def build_q_representative_families(
    registry: ThreeLoopRegistry,
) -> tuple[QRepresentativeFamily, ...]:
    """Build the verified 28-family representative plan for all Q diagrams.

    The count is derived, not hard coded.  Any future registry change that
    alters reflection equivalence or rank structure will therefore show up in
    the generated report instead of silently reusing an obsolete plan.
    """
    sharing = analyze_three_loop_family_sharing(registry)
    reflection_groups = sharing["reflection_candidates"]["multi_member_groups"]
    q_pairs = [
        tuple(group)
        for group in reflection_groups
        if len(group) == 2 and group[0].startswith("Q") and group[1].startswith("Q")
    ]

    paired_ids = {diagram_id for pair in q_pairs for diagram_id in pair}
    q_ids = sorted(
        topology.diagram_id
        for topology in registry
        if topology.diagram_id.startswith("Q")
    )
    groups: list[tuple[str, ...]] = list(q_pairs)
    groups.extend((diagram_id,) for diagram_id in q_ids if diagram_id not in paired_ids)
    groups.sort(key=lambda group: group[0])

    families: list[QRepresentativeFamily] = []
    for members in groups:
        representative_id = members[0]
        representative = registry.get(representative_id)
        rep_rank = q_physical_rank(representative)
        independent = _independent_indices_for(representative)
        isp_pairs = q_completion_isp_pairs(representative)
        if len(independent) != rep_rank:
            raise ValueError(
                f"{representative_id}: independent physical count {len(independent)} != rank {rep_rank}"
            )
        if len(independent) + len(isp_pairs) != 12:
            raise ValueError(
                f"{representative_id}: representative layout is not 12 slots: "
                f"{len(independent)} physical + {len(isp_pairs)} ISP"
            )

        member_maps: list[QFamilyMemberMap] = []
        rep_rules = _duplicate_rules_for(representative)
        member_maps.append(
            QFamilyMemberMap(
                diagram_id=representative_id,
                representative_id=representative_id,
                physical_to_representative=_identity_physical_map(),
                duplicate_rules=rep_rules,
                auxiliary_count=len(isp_pairs),
                reflected=False,
            )
        )

        if len(members) == 2:
            partner_id = members[1]
            partner = registry.get(partner_id)
            physical_map = verify_reflection_physical_propagators(representative, partner)
            algebraic_map = verify_q_reflection_family_algebraically(
                representative, partner, physical_map
            )
            if not algebraic_map.reflection_equivalent:
                raise ValueError(f"{representative_id}<->{partner_id}: reflection proof failed")
            if algebraic_map.source_physical_rank != rep_rank:
                raise ValueError(f"{representative_id}: inconsistent source rank")
            if algebraic_map.target_physical_rank != rep_rank:
                raise ValueError(f"{partner_id}: reflected rank differs from representative")
            partner_rules = _duplicate_rules_for(partner)
            # algebraic_map stores source -> target.  Record target -> source for
            # member-to-representative translation.
            target_to_source = tuple(
                sorted((target_index, source_index) for source_index, target_index in algebraic_map.physical_index_map)
            )
            member_maps.append(
                QFamilyMemberMap(
                    diagram_id=partner_id,
                    representative_id=representative_id,
                    physical_to_representative=target_to_source,
                    duplicate_rules=partner_rules,
                    auxiliary_count=len(isp_pairs),
                    reflected=True,
                )
            )

        families.append(
            QRepresentativeFamily(
                representative_id=representative_id,
                members=members,
                physical_rank=rep_rank,
                independent_physical_indices=independent,
                completion_isp_pairs=isp_pairs,
                member_maps=tuple(member_maps),
            )
        )

    covered = sorted(member.diagram_id for family in families for member in family.member_maps)
    if covered != q_ids:
        raise ValueError("representative-family plan does not cover every Q diagram exactly once")
    return tuple(families)


def family_for_diagram(
    families: Sequence[QRepresentativeFamily], diagram_id: str
) -> tuple[QRepresentativeFamily, QFamilyMemberMap]:
    for family in families:
        for member in family.member_maps:
            if member.diagram_id == diagram_id:
                return family, member
    raise KeyError(diagram_id)


def translate_q_physical_powers_to_representative(
    family: QRepresentativeFamily,
    member: QFamilyMemberMap,
    physical_powers: Sequence[int],
    auxiliary_powers: Sequence[int] | None = None,
) -> tuple[int, ...]:
    """Translate one member integral into the representative 12-slot layout.

    ``physical_powers`` always refers to the diagram's nine raw physical
    propagators before duplicate elimination.  ``auxiliary_powers`` refers to
    the member's induced auxiliary basis in the same order as the
    representative completion basis.  If omitted, all auxiliary powers are 0.

    Exact duplicate denominators are merged both before and after reflection;
    this makes rank-7/8 partner translations canonical even when the kept raw
    denominator slot differs on the two sides of the reflection.
    """
    if len(physical_powers) != 9:
        raise ValueError("Q physical power vector must contain exactly 9 entries")
    if auxiliary_powers is None:
        auxiliary_powers = (0,) * family.auxiliary_slot_count
    if len(auxiliary_powers) != family.auxiliary_slot_count:
        raise ValueError(
            f"expected {family.auxiliary_slot_count} auxiliary powers, got {len(auxiliary_powers)}"
        )

    normalized_member = normalize_duplicate_denominator_powers(
        physical_powers, member.duplicate_rules
    )
    if normalized_member.prefactor != 1:
        raise ValueError(
            f"{member.diagram_id}: non-unit duplicate scale requires coefficient handling"
        )

    representative_raw = [0] * 9
    for member_index, representative_index in member.physical_to_representative:
        representative_raw[representative_index - 1] += normalized_member.powers[member_index - 1]

    representative_member = next(
        item for item in family.member_maps if item.diagram_id == family.representative_id
    )
    normalized_rep = normalize_duplicate_denominator_powers(
        representative_raw, representative_member.duplicate_rules
    )
    if normalized_rep.prefactor != 1:
        raise ValueError(
            f"{family.representative_id}: non-unit duplicate scale requires coefficient handling"
        )

    packed_physical = tuple(
        normalized_rep.powers[index - 1]
        for index in family.independent_physical_indices
    )
    result = packed_physical + tuple(int(value) for value in auxiliary_powers)
    if len(result) != 12:
        raise ValueError(f"translated representative integral has {len(result)} slots, expected 12")
    return result
