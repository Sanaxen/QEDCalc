"""Inspect Kira SQLite database schema and selected table contents read-only."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from three_loop.integral_family_classification import ROOT


def _find_project(family: str, name_filter: str) -> Path:
    out = ROOT / "output"
    family_key = family.lower()
    hits = sorted(
        p for p in out.iterdir()
        if p.is_dir()
        and family_key in p.name.lower()
        and name_filter.lower() in p.name.lower()
    )
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one project for filter {name_filter!r}, found {len(hits)}: {hits}")
    return hits[0]


def _db(project: Path) -> Path:
    hits = sorted(project.rglob("kira.db"))
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one kira.db under {project}, found {len(hits)}")
    return hits[0]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--project-filter", required=True)
    p.add_argument("--table", default="EQUATION")
    p.add_argument("--sample-rows", type=int, default=5)
    args = p.parse_args()

    project = _find_project(args.family, args.project_filter)
    db = _db(project)
    uri = "file:" + db.resolve().as_posix() + "?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        table = args.table
        qtable = '"' + table.replace('"', '""') + '"'
        exists = con.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        ).fetchone()[0]
        if not exists:
            raise SystemExit(f"table {table!r} not found in {db}")

        columns = []
        for row in con.execute(f"PRAGMA table_info({qtable})"):
            columns.append({
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": row[3],
                "default": row[4],
                "pk": row[5],
            })
        count = int(con.execute(f"SELECT COUNT(*) FROM {qtable}").fetchone()[0])

        aggregates = {}
        if table.upper() == "EQUATION":
            aggregates["auxiliary_counts"] = [
                {"auxiliary": row[0], "count": int(row[1])}
                for row in con.execute(
                    f"SELECT AUXILIARY, COUNT(*) FROM {qtable} "
                    "GROUP BY AUXILIARY ORDER BY AUXILIARY"
                )
            ]
            aggregates["length_counts"] = [
                {"length": row[0], "count": int(row[1])}
                for row in con.execute(
                    f"SELECT LENGTH, COUNT(*) FROM {qtable} "
                    "GROUP BY LENGTH ORDER BY LENGTH"
                )
            ]
            aggregates["sector_counts_top"] = [
                {"sector": row[0], "count": int(row[1])}
                for row in con.execute(
                    f"SELECT SECTOR, COUNT(*) AS C FROM {qtable} "
                    "GROUP BY SECTOR ORDER BY C DESC, SECTOR LIMIT 30"
                )
            ]
            aggregates["nontrivial_count"] = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {qtable} "
                    "WHERE LENGTH > 1 OR AUXILIARY = 0"
                ).fetchone()[0]
            )
            aggregates["length_gt1_count"] = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {qtable} WHERE LENGTH > 1"
                ).fetchone()[0]
            )
            aggregates["auxiliary_zero_count"] = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {qtable} WHERE AUXILIARY = 0"
                ).fetchone()[0]
            )
            aggregates["sector_199_count"] = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {qtable} WHERE SECTOR = 199"
                ).fetchone()[0]
            )
            aggregates["sector_199_length_gt1_count"] = int(
                con.execute(
                    f"SELECT COUNT(*) FROM {qtable} "
                    "WHERE SECTOR = 199 AND LENGTH > 1"
                ).fetchone()[0]
            )

        samples = []
        cur = con.execute(f"SELECT * FROM {qtable} LIMIT ?", (max(0, args.sample_rows),))
        names = [d[0] for d in cur.description]
        for row in cur:
            rec = {}
            for name, value in zip(names, row):
                if isinstance(value, bytes):
                    rec[name] = {
                        "kind": "bytes",
                        "length": len(value),
                        "hex_prefix": value[:64].hex(),
                    }
                else:
                    text = repr(value)
                    rec[name] = text if len(text) <= 500 else text[:500] + "...<truncated>"
            samples.append(rec)

        meaningful_samples = []
        if table.upper() == "EQUATION":
            cur2 = con.execute(
                f"SELECT * FROM {qtable} "
                "WHERE LENGTH > 1 OR AUXILIARY = 0 "
                "ORDER BY CASE WHEN SECTOR = 199 THEN 0 ELSE 1 END, "
                "LENGTH DESC, SECTOR LIMIT ?",
                (max(0, args.sample_rows),),
            )
            names2 = [d[0] for d in cur2.description]
            for row in cur2:
                rec = {}
                for name, value in zip(names2, row):
                    if isinstance(value, bytes):
                        rec[name] = {
                            "kind": "bytes",
                            "length": len(value),
                            "hex_prefix": value[:64].hex(),
                        }
                    else:
                        text = repr(value)
                        rec[name] = text if len(text) <= 500 else text[:500] + "...<truncated>"
                meaningful_samples.append(rec)

        indexes = []
        for row in con.execute(f"PRAGMA index_list({qtable})"):
            indexes.append({
                "seq": row[0],
                "name": row[1],
                "unique": row[2],
                "origin": row[3],
                "partial": row[4],
            })

        payload = {
            "project": str(project),
            "database": str(db),
            "database_size_bytes": db.stat().st_size,
            "table": table,
            "row_count": count,
            "columns": columns,
            "indexes": indexes,
            "aggregates": aggregates,
            "sample_rows": samples,
            "meaningful_sample_rows": meaningful_samples,
        }
    finally:
        con.close()

    audit_dir = ROOT / "output" / "three_loop_integral_family_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    stem = f"kira_db_{project.name.lower()}_{args.table.lower()}_inspect"
    out_json = audit_dir / f"{stem}.json"
    out_txt = audit_dir / f"{stem}.txt"
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    lines = [
        "QEDCalc Kira DB table inspect",
        f"project: {project.name}",
        f"database: {db}",
        f"database size: {db.stat().st_size}",
        f"table: {table}",
        f"row count: {count}",
        "columns:",
    ]
    for col in columns:
        lines.append(
            f"  {col['cid']}: {col['name']} type={col['type']} "
            f"notnull={col['notnull']} pk={col['pk']}"
        )
    lines.append("indexes:")
    for idx in indexes:
        lines.append(f"  {idx['name']} unique={idx['unique']} origin={idx['origin']}")
    if payload.get("aggregates"):
        a = payload["aggregates"]
        lines.append("aggregates:")
        lines.append(f"  auxiliary counts: {a.get('auxiliary_counts')}")
        lines.append(f"  length counts: {a.get('length_counts')}")
        lines.append(f"  nontrivial count: {a.get('nontrivial_count')}")
        lines.append(f"  length>1 count: {a.get('length_gt1_count')}")
        lines.append(f"  auxiliary=0 count: {a.get('auxiliary_zero_count')}")
        lines.append(f"  sector 199 count: {a.get('sector_199_count')}")
        lines.append(f"  sector 199 length>1 count: {a.get('sector_199_length_gt1_count')}")
        lines.append(f"  top sectors: {a.get('sector_counts_top')}")
    lines.append("sample rows:")
    for i, rec in enumerate(samples, 1):
        lines.append(f"  row {i}:")
        for name, value in rec.items():
            lines.append(f"    {name}: {value}")
    if payload.get("meaningful_sample_rows"):
        lines.append("meaningful sample rows:")
        for i, rec in enumerate(payload["meaningful_sample_rows"], 1):
            lines.append(f"  row {i}:")
            for name, value in rec.items():
                lines.append(f"    {name}: {value}")
    lines.extend([f"audit JSON: {out_json}", f"audit TXT: {out_txt}"])
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
