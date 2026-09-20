"""Formal 3-loop input -> graph -> canonical-family bridge."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from three_loop.canonical_family_registry import apply_confirmed_family_registry
from three_loop.integral_family_classification import (
    ROOT,
    build_global_classification,
    load_topologies,
    validate_global_audit,
)

INPUT_DIR = ROOT / "input" / "three_loop"
MANIFEST_FILE = INPUT_DIR / "manifest.json"
OUTPUT_DIR = ROOT / "output" / "three_loop_input_pipeline"
META_PREFIX = "% qedcalc_meta: "


@dataclass(frozen=True)
class ThreeLoopInputRecord:
    diagram_id: str
    physical_family: str
    path: Path
    amplitude_tex: str
    graph: dict[str, Any]
    source_document: str
    sha256: str


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _meta(text: str, path: Path) -> dict[str, Any]:
    for line in text.splitlines():
        if line.startswith(META_PREFIX):
            value = json.loads(line[len(META_PREFIX):])
            if not isinstance(value, dict):
                raise ValueError(f"{path}: qedcalc_meta must be an object")
            return value
    raise ValueError(f"{path}: missing qedcalc_meta header")


def _amplitude(text: str) -> str:
    lines = text.splitlines()
    i = 0
    while i < len(lines) and (not lines[i].strip() or lines[i].lstrip().startswith("%")):
        i += 1
    return "\n".join(lines[i:]).strip()


def expected_ids() -> list[str]:
    return (
        [f"Q{i:02d}" for i in range(1, 51)]
        + [f"VP{i:02d}" for i in range(1, 13)]
        + ["VP4A", "VP4B", "VP4C", "VP22"]
        + [f"LBL{i:02d}" for i in range(1, 7)]
    )


def load_three_loop_inputs() -> list[ThreeLoopInputRecord]:
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    rows = manifest.get("files")
    if not isinstance(rows, list):
        raise ValueError("manifest.json: missing files list")

    records: list[ThreeLoopInputRecord] = []
    for row in rows:
        rel = Path(str(row["path"]))
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        digest = _sha256(text)
        if digest != row.get("sha256"):
            raise ValueError(f"{rel}: sha256 mismatch")
        meta = _meta(text, path)
        graph = meta.get("graph")
        if not isinstance(graph, dict):
            raise ValueError(f"{rel}: graph metadata is missing")
        diagram_id = str(meta.get("diagram_id", ""))
        family = str(meta.get("physical_family", ""))
        amp = _amplitude(text)
        if graph.get("id") != diagram_id or graph.get("family") != family:
            raise ValueError(f"{rel}: metadata identity mismatch")
        if diagram_id not in amp or r"\Lambda" not in amp or r"\int d^4k" not in amp:
            raise ValueError(f"{rel}: amplitude provenance sanity check failed")
        records.append(
            ThreeLoopInputRecord(
                diagram_id=diagram_id,
                physical_family=family,
                path=path,
                amplitude_tex=amp,
                graph=graph,
                source_document=str(meta.get("source_document", "")),
                sha256=digest,
            )
        )
    return records


def build_input_to_family_audit() -> dict[str, Any]:
    records = load_three_loop_inputs()
    errors: list[str] = []
    ids = [r.diagram_id for r in records]
    if ids != expected_ids():
        errors.append("formal input inventory is not the exact canonical 72-diagram order")
    if len(ids) != 72 or len(set(ids)) != 72:
        errors.append(f"formal input count/uniqueness failure: count={len(ids)} unique={len(set(ids))}")

    counts = Counter(r.physical_family for r in records)
    expected_counts = {
        "quenched": 50,
        "vp1_insert": 12,
        "vp2_insert": 3,
        "vp1_double": 1,
        "external_lbl": 6,
    }
    if dict(counts) != expected_counts:
        errors.append(f"physical-family counts differ: {dict(counts)}")

    topology_rows = load_topologies()
    topology_by_id = {str(row["id"]): row for row in topology_rows}
    graph_rows = []
    for rec in records:
        expected = topology_by_id.get(rec.diagram_id)
        exact = rec.graph == expected
        graph_rows.append(
            {
                "diagram_id": rec.diagram_id,
                "input_path": str(rec.path.relative_to(ROOT)),
                "source_document": rec.source_document,
                "input_graph": rec.graph,
                "registry_graph": expected,
                "exact_match": exact,
            }
        )
        if not exact:
            errors.append(f"{rec.diagram_id}: formal-input graph != data/three_loop_topologies.json")

    classification = build_global_classification(topology_rows)
    registry_errors = apply_confirmed_family_registry(topology_rows, classification)
    class_errors = validate_global_audit(classification) + registry_errors
    classification["audit_errors"] = class_errors
    classification["audit_pass"] = not class_errors
    errors.extend(class_errors)

    family_by_diagram = {
        str(row["diagram_id"]): row for row in classification.get("records", [])
    }
    provenance = []
    for rec in records:
        cls = family_by_diagram.get(rec.diagram_id, {})
        provenance.append(
            {
                "diagram_id": rec.diagram_id,
                "input_path": str(rec.path.relative_to(ROOT)),
                "source_document": rec.source_document,
                "input_sha256": rec.sha256,
                "physical_family": rec.physical_family,
                "canonical_integral_family_id": cls.get("canonical_integral_family_id"),
                "master_basis_id": cls.get("master_basis_id"),
                "classification_status": cls.get("classification_status"),
                "symmetry_representative": cls.get("symmetry_representative"),
            }
        )

    return {
        "schema_version": 1,
        "stage": "three-loop-input-to-canonical-family",
        "diagram_count": len(records),
        "input_validation_pass": not any("formal input" in x or "physical-family" in x for x in errors),
        "graph_registry_exact_match_count": sum(1 for row in graph_rows if row["exact_match"]),
        "graph_registry_pass": all(row["exact_match"] for row in graph_rows),
        "canonical_classification_pass": bool(classification.get("audit_pass")),
        "classification_complete": bool(classification.get("classification_complete")),
        "canonical_family_count": len(classification.get("canonical_registry", {})),
        "provenance": provenance,
        "graph_comparisons": graph_rows,
        "classification": classification,
        "errors": errors,
        "audit_pass": not errors,
    }


def _markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# QEDCalc 3-loop input -> canonical-family audit",
        "",
        "This is the reproducible front half of the three-loop pipeline.",
        "It does not launch Kira/FireFly or change the running master-basis job.",
        "",
        "## Summary",
        "",
        f"- formal input diagrams: **{audit['diagram_count']}**",
        f"- graph/registry exact matches: **{audit['graph_registry_exact_match_count']}/72**",
        f"- canonical families: **{audit['canonical_family_count']}**",
        f"- classification complete: **{audit['classification_complete']}**",
        f"- overall: **{'PASS' if audit['audit_pass'] else 'FAIL'}**",
        "",
        "## Provenance",
        "",
        "| Diagram | Formal input | Physical family | Canonical family | Master basis | Status |",
        "|---|---|---|---|---|---|",
    ]
    for row in audit["provenance"]:
        lines.append(
            f"| {row['diagram_id']} | `{row['input_path']}` | {row['physical_family']} | "
            f"{row.get('canonical_integral_family_id') or '-'} | "
            f"{row.get('master_basis_id') or '-'} | "
            f"{row.get('classification_status') or '-'} |"
        )
    lines += ["", "## Errors", ""]
    lines += [f"- {x}" for x in audit["errors"]] if audit["errors"] else ["- none"]
    lines += [
        "",
        "## Pipeline boundary",
        "",
        "The next stage is the existing canonical-family/master-basis machinery. "
        "This audit intentionally stops before Kira/FireFly execution.",
        "",
    ]
    return "\n".join(lines)


def write_input_to_family_audit() -> tuple[Path, Path, dict[str, Any]]:
    audit = build_input_to_family_audit()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "three_loop_input_to_family_audit.json"
    md_path = OUTPUT_DIR / "three_loop_input_to_family_audit.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(audit), encoding="utf-8")
    return json_path, md_path, audit
