"""Conservative global integral-family classification helpers for three-loop diagrams.

This module intentionally distinguishes two different notions of "family":

* physical/topological family from ``data/three_loop_topologies.json``;
* canonical IBP/Kira integral family, which requires an explicit denominator
  basis and a proven loop-momentum transformation.

Topology alone is not enough to prove the latter.  The helpers below therefore
build *structural candidate classes* that are useful for scheduling the 72
three-loop diagrams, while refusing to promote a candidate to a confirmed
IBP/Kira family unless explicit evidence is registered.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_FILE = ROOT / "data" / "three_loop_topologies.json"


@dataclass(frozen=True)
class ConfirmedFamilyEvidence:
    diagram_id: str
    canonical_family_id: str
    kira_family: str | None
    canonical_propagator_basis: list[str] | None
    loop_momentum_transform: dict[str, str] | None
    sign_normalization_transform: str | None
    representative: str
    kira_reusable: bool | None
    requires_new_auxiliary_basis: bool | None
    master_basis_id: str | None
    evidence: str


# Only claim what has actually been established.  Q01 has a validated Kira
# family and 60-master coefficient pipeline, but its explicit denominator-basis
# / routing transformation has not yet been committed as canonical registry
# data.  Consequently Q01 is marked pipeline_validated below rather than
# "confirmed" by canonical_mapping_status().
KNOWN_EVIDENCE: dict[str, ConfirmedFamilyEvidence] = {
    "Q01": ConfirmedFamilyEvidence(
        diagram_id="Q01",
        canonical_family_id="Q01_full",
        kira_family="Q01_full",
        canonical_propagator_basis=None,
        loop_momentum_transform=None,
        sign_normalization_transform="identity in the validated Q01 routing",
        representative="Q01",
        kira_reusable=True,
        requires_new_auxiliary_basis=False,
        master_basis_id="Q01_final60",
        evidence=(
            "Validated exact944/d+1 Kira-FireFly reduction and reusable Fermat "
            "master-coefficient API; 60/60 coefficients reproduce the PASS reference."
        ),
    )
}


def load_topologies(path: Path = TOPOLOGY_FILE) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("diagrams")
    if not isinstance(rows, list):
        raise ValueError(f"missing diagrams list in {path}")
    ids = [row.get("id") for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate diagram IDs in topology inventory")
    return rows


def _norm_edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a <= b else (b, a)


def _open_line_signature(row: dict[str, Any], *, reflected: bool) -> tuple[Any, ...]:
    n = int(row["open_vertices"])

    def vertex(v: int) -> int:
        return n + 1 - v if reflected else v

    ext_raw = row.get("external_vertex")
    ext = vertex(int(ext_raw)) if isinstance(ext_raw, int) else ext_raw
    insert_on = row.get("insert_on")

    edges: list[tuple[Any, ...]] = []
    for edge in row.get("photon_edges", []):
        if "a" not in edge or "b" not in edge:
            continue
        a, b = _norm_edge(vertex(int(edge["a"])), vertex(int(edge["b"])))
        # For one-loop VP insertion diagrams the inserted photon line is
        # distinguished structurally; ordinary photon labels are otherwise
        # dummy loop-momentum names and deliberately ignored.
        distinguished = bool(insert_on is not None and edge.get("label") == insert_on)
        edges.append((1 if distinguished else 0, a, b))
    edges.sort()

    extra: tuple[Any, ...] = ()
    if row.get("family") == "vp2_insert":
        # A/B/C are different kernels/numerators on the same open-line
        # denominator topology.  Keep the kernel out of the candidate key but
        # report it separately in the audit.
        extra = ("vp2-kernel-denominator-class",)
    elif row.get("family") == "vp1_double":
        extra = ("double-vp",)

    return (row.get("family"), n, ext, tuple(edges), extra)


def structural_candidate_key(row: dict[str, Any]) -> tuple[Any, ...]:
    """Return a conservative topology-derived candidate-family key.

    The key quotients open-line diagrams by left/right reflection and dummy
    photon-label permutations.  It is *not* a proof of IBP-family equivalence.
    """
    family = row.get("family")
    if family == "external_lbl":
        # All six entries have the same denominator-level external-LBL skeleton;
        # closed-loop ordering is retained in each record as a diagnostic but is
        # not used to assert a canonical Kira family.
        return (
            "external_lbl",
            int(row.get("open_vertices", 0)),
            len(row.get("photon_edges", [])),
            int(row.get("closed_fermion_loops", 0)),
        )

    direct = _open_line_signature(row, reflected=False)
    mirror = _open_line_signature(row, reflected=True)
    return min(direct, mirror, key=repr)


def candidate_classes(rows: Iterable[dict[str, Any]]) -> dict[str, list[str]]:
    grouped: dict[tuple[Any, ...], list[str]] = defaultdict(list)
    for row in rows:
        grouped[structural_candidate_key(row)].append(str(row["id"]))

    # Stable IDs make diffs/audits reproducible without pretending these are
    # already proven canonical Kira-family IDs.
    ordered = sorted(grouped.items(), key=lambda item: (str(item[0][0]), repr(item[0])))
    return {
        f"CAND_{i:02d}": sorted(ids)
        for i, (_key, ids) in enumerate(ordered, start=1)
    }


def canonical_mapping_status(evidence: ConfirmedFamilyEvidence | None) -> str:
    if evidence is None:
        return "candidate_only"
    if evidence.canonical_propagator_basis and evidence.loop_momentum_transform:
        return "confirmed"
    return "pipeline_validated_mapping_incomplete"


def build_global_classification(rows: list[dict[str, Any]]) -> dict[str, Any]:
    classes = candidate_classes(rows)
    candidate_of = {diagram_id: cid for cid, ids in classes.items() for diagram_id in ids}

    records: list[dict[str, Any]] = []
    for row in rows:
        diagram_id = str(row["id"])
        evidence = KNOWN_EVIDENCE.get(diagram_id)
        status = canonical_mapping_status(evidence)
        rec: dict[str, Any] = {
            "diagram_id": diagram_id,
            "physical_topology_family": row.get("family"),
            "structural_candidate_class": candidate_of[diagram_id],
            "classification_status": status,
            "canonical_integral_family_id": evidence.canonical_family_id if evidence else None,
            "canonical_propagator_basis": evidence.canonical_propagator_basis if evidence else None,
            "loop_momentum_transform": evidence.loop_momentum_transform if evidence else None,
            "sign_normalization_transform": evidence.sign_normalization_transform if evidence else None,
            "symmetry_representative": evidence.representative if evidence else classes[candidate_of[diagram_id]][0],
            "existing_kira_family_reusable": evidence.kira_reusable if evidence else None,
            "requires_new_auxiliary_basis": evidence.requires_new_auxiliary_basis if evidence else None,
            "projected_amplitude_target_stats": (
                {"native": 910, "exact_kira_targets": 944}
                if diagram_id == "Q01"
                else None
            ),
            "master_basis_id": evidence.master_basis_id if evidence else None,
            "closed_fermion_loops": row.get("closed_fermion_loops"),
            "topology_specific": {
                key: row[key]
                for key in ("external_vertex", "open_vertices", "photon_edges", "insert_on", "vp2_kernel", "closed_loop_order")
                if key in row
            },
            "evidence": evidence.evidence if evidence else (
                "Topology-derived structural candidate only; explicit denominator basis and "
                "loop-momentum map have not yet been proven."
            ),
        }
        records.append(rec)

    counts: dict[str, int] = defaultdict(int)
    for rec in records:
        counts[rec["classification_status"]] += 1

    physical_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        physical_counts[str(row.get("family"))] += 1

    confirmed = counts.get("confirmed", 0)
    complete = confirmed == len(records)
    return {
        "schema_version": 1,
        "diagram_count": len(records),
        "physical_family_counts": dict(sorted(physical_counts.items())),
        "structural_candidate_class_count": len(classes),
        "structural_candidate_classes": classes,
        "classification_status_counts": dict(sorted(counts.items())),
        "confirmed_canonical_mapping_count": confirmed,
        "classification_complete": complete,
        "records": records,
        "interpretation": (
            "Structural candidate classes quotient obvious topology reflection/dummy-label symmetries. "
            "They are scheduling hints, not canonical IBP/Kira-family proofs. A diagram reaches "
            "classification_status=confirmed only after an explicit canonical propagator basis and "
            "loop-momentum transformation are registered."
        ),
    }


def validate_global_audit(audit: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    records = audit.get("records", [])
    ids = [rec.get("diagram_id") for rec in records]
    if len(records) != 72:
        errors.append(f"expected 72 diagrams, got {len(records)}")
    if len(ids) != len(set(ids)):
        errors.append("duplicate diagram IDs in classification records")

    expected_counts = {
        "quenched": 50,
        "vp1_insert": 12,
        "vp2_insert": 3,
        "vp1_double": 1,
        "external_lbl": 6,
    }
    if audit.get("physical_family_counts") != dict(sorted(expected_counts.items())):
        errors.append(
            f"physical-family counts differ from 72-diagram inventory: {audit.get('physical_family_counts')}"
        )

    classes = audit.get("structural_candidate_classes", {})
    flattened = [diagram_id for members in classes.values() for diagram_id in members]
    if sorted(flattened) != sorted(ids):
        errors.append("candidate classes do not partition the 72 diagrams exactly once")

    for rec in records:
        if rec.get("classification_status") == "confirmed":
            if not rec.get("canonical_integral_family_id"):
                errors.append(f"{rec.get('diagram_id')}: confirmed mapping lacks canonical family ID")
            if not rec.get("canonical_propagator_basis"):
                errors.append(f"{rec.get('diagram_id')}: confirmed mapping lacks propagator basis")
            if not rec.get("loop_momentum_transform"):
                errors.append(f"{rec.get('diagram_id')}: confirmed mapping lacks momentum transform")
    return errors
