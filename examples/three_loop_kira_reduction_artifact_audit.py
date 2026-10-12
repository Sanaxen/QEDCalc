"""Audit existing Kira project artifacts for reusable reduction data.

The goal is to determine whether a previously completed VP05_full s<=5 run
contains enough reduction output (kira.db / results tables / id2int) to seed an
incremental s=6 analysis without rebuilding the whole lower-shell row space in
QEDCalc's Python finite-field engine.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from three_loop.integral_family_classification import ROOT


def _find_projects(family: str) -> list[Path]:
    out = ROOT / "output"
    if not out.exists():
        return []
    needle = family.lower()
    return sorted(
        p for p in out.iterdir()
        if p.is_dir() and needle in p.name.lower() and p.name.lower().startswith("kira_")
    )


def _text_has(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def _sqlite_summary(path: Path) -> dict:
    """Inspect a Kira SQLite database without assuming a particular schema."""
    out = {
        "path": str(path),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "sqlite_readable": False,
        "tables": [],
        "errors": [],
    }
    try:
        uri = "file:" + path.resolve().as_posix() + "?mode=ro"
        con = sqlite3.connect(uri, uri=True)
        try:
            tables = [
                str(row[0])
                for row in con.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
            ]
            out["sqlite_readable"] = True
            for name in tables:
                rec = {"name": name, "row_count": None}
                try:
                    quoted = '"' + name.replace('"', '""') + '"'
                    rec["row_count"] = int(
                        con.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0]
                    )
                except Exception as exc:
                    rec["error"] = str(exc)
                out["tables"].append(rec)
        finally:
            con.close()
    except Exception as exc:
        out["errors"].append(str(exc))
    return out


def _looks_like_completed_reduction(
    *,
    run_triangular: bool,
    run_back: bool,
    id2int_hits: list[Path],
    kira_table_hits: list[Path],
    db_summaries: list[dict],
) -> tuple[bool, str]:
    """Conservative evidence test for reusable reduction rules.

    A bare kira.db is not sufficient: masters-only initiate runs also create it.
    Prefer explicit exported reduction artifacts.  Otherwise report a completed
    triangular/back-substitution database only as needing schema-level review.
    """
    if id2int_hits and kira_table_hits:
        return True, "explicit id2int + result reduction table"
    if run_triangular and run_back and db_summaries:
        return False, "triangular/back-substitution requested but no exported reduction table; inspect database contents"
    if db_summaries:
        return False, "bare kira.db only; insufficient evidence of reusable reduction rules"
    return False, "no reduction database/output"


def _project_record(project: Path, family: str) -> dict:
    results_family = project / "results" / family
    jobs = project / "jobs.yaml"

    db_hits = sorted(project.rglob("kira.db"))
    id2int_hits = sorted(project.rglob("id2int"))
    kira_table_hits = sorted(
        p for p in project.rglob("kira")
        if p.is_file() and "results" in {part.lower() for part in p.parts}
    )
    masters_final_hits = sorted(project.rglob("masters.final"))
    masters_hits = sorted(
        p for p in project.rglob("masters")
        if p.is_file()
    )
    master_hits = sorted(
        p for p in project.rglob("master")
        if p.is_file()
    )

    run_triangular = _text_has(jobs, "run_triangular: sectorwise")
    run_back = _text_has(jobs, "run_back_substitution: true")
    run_firefly = _text_has(jobs, "run_firefly: true")

    db_summaries = [_sqlite_summary(p) for p in db_hits]
    reusable_reduction, reusable_reason = _looks_like_completed_reduction(
        run_triangular=run_triangular,
        run_back=run_back,
        id2int_hits=id2int_hits,
        kira_table_hits=kira_table_hits,
        db_summaries=db_summaries,
    )
    return {
        "project": str(project),
        "name": project.name,
        "jobs_yaml": str(jobs) if jobs.exists() else None,
        "run_triangular_sectorwise": run_triangular,
        "run_back_substitution": run_back,
        "run_firefly": run_firefly,
        "kira_db": [str(p) for p in db_hits],
        "kira_db_details": db_summaries,
        "id2int": [str(p) for p in id2int_hits],
        "kira_result_tables": [str(p) for p in kira_table_hits],
        "masters_final": [str(p) for p in masters_final_hits],
        "masters": [str(p) for p in masters_hits],
        "master": [str(p) for p in master_hits],
        "results_family_dir_exists": results_family.exists(),
        "reusable_reduction_artifacts": reusable_reduction,
        "reusable_reduction_reason": reusable_reason,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--contains", default="")
    args = p.parse_args()

    projects = _find_projects(args.family)
    if args.contains:
        projects = [p for p in projects if args.contains.lower() in p.name.lower()]

    rows = [_project_record(project, args.family) for project in projects]
    reusable = [row for row in rows if row["reusable_reduction_artifacts"]]

    audit_dir = ROOT / "output" / "three_loop_integral_family_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    stem = f"three_loop_{args.family.lower()}_kira_reduction_artifact_audit"
    if args.contains:
        stem += "_" + args.contains.lower().replace(" ", "_")
    out_json = audit_dir / f"{stem}.json"
    out_txt = audit_dir / f"{stem}.txt"

    payload = {
        "schema_version": 1,
        "stage": "kira_reduction_artifact_audit",
        "family": args.family,
        "filter_contains": args.contains,
        "project_count": len(rows),
        "reusable_reduction_project_count": len(reusable),
        "projects": rows,
    }
    out_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )

    lines = [
        "QEDCalc Kira reduction artifact audit",
        f"family: {args.family}",
        f"project filter: {args.contains or '(none)'}",
        f"projects found: {len(rows)}",
        f"projects with reusable reduction artifacts: {len(reusable)}",
    ]
    for row in rows:
        lines.extend([
            "",
            f"project: {row['name']}",
            f"  triangular: {row['run_triangular_sectorwise']}",
            f"  back substitution: {row['run_back_substitution']}",
            f"  firefly: {row['run_firefly']}",
            f"  kira.db: {len(row['kira_db'])}",
            f"  id2int: {len(row['id2int'])}",
            f"  result kira tables: {len(row['kira_result_tables'])}",
            f"  masters.final: {len(row['masters_final'])}",
            f"  masters/master: {len(row['masters']) + len(row['master'])}",
            f"  reusable reduction artifacts: {row['reusable_reduction_artifacts']}",
            f"  reason: {row['reusable_reduction_reason']}",
        ])
        for db in row.get("kira_db_details", []):
            lines.append(
                f"  db: size={db['size_bytes']} sqlite={db['sqlite_readable']} "
                f"tables={len(db['tables'])}"
            )
            for table in db.get("tables", []):
                lines.append(
                    f"    table {table['name']}: rows={table.get('row_count')}"
                )
    lines.extend([
        "",
        f"audit JSON: {out_json}",
        f"audit TXT: {out_txt}",
    ])
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
