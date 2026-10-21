"""Bounded, read-only diagnostic of the saved VP05 Kira EQUATION table.

Outputs a few original records and aggregate statistics. Does not change the
database or presume a mapping between small SYSTEM IDs and physical integrals.
"""
from __future__ import annotations
import argparse
import json
import sqlite3
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, default=DEFAULT)
    ap.add_argument("--output", type=Path, default=Path("output/three_loop_integral_family_audit/vp05_kiradb_equation_sample.json"))
    args = ap.parse_args()
    db = (args.project / "results/kira.db").resolve()
    if not db.is_file():
        ap.error("Missing kira.db")
    conn = sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)
    conn.execute("PRAGMA query_only=ON")
    try:
        count = conn.execute("SELECT count(*) FROM EQUATION").fetchone()[0]
        rows = conn.execute("SELECT ID, ARRAYID, AUXILIARY, SECTOR, LENGTH, substr(COEFFICIENT,1,120) FROM EQUATION LIMIT 12").fetchall()
        sectors = conn.execute("SELECT SECTOR,count(*) FROM EQUATION GROUP BY SECTOR ORDER BY SECTOR LIMIT 32").fetchall()
        auxiliary = conn.execute("SELECT AUXILIARY,count(*) FROM EQUATION GROUP BY AUXILIARY ORDER BY AUXILIARY LIMIT 32").fetchall()
        samples = [dict(zip(("ID","ARRAYID","AUXILIARY","SECTOR","LENGTH","coefficient_prefix"), r)) for r in rows]
        result = {"equation_count": count, "samples": samples,
                  "sector_counts": sectors, "auxiliary_counts": auxiliary,
                  "mapping_verified": False,
                  "note": "Limited database inspection; raw IDs are not yet mapped to exponent vectors."}
    finally:
        conn.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("VP05_KIRADB_EQUATION_SAMPLE " + json.dumps({**result,"output":str(args.output)}), flush=True)

if __name__ == "__main__":
    main()
