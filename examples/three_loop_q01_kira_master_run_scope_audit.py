"""Explain Q01 masters.final as run-scoped artifacts.

Saved-artifact only: consumes q01_kira_master_provenance_audit.json and reports
how each masters.final differs across Kira alt_dirs.  No Kira, FireFly, Fermat,
or projected-trace recomputation is performed.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import PROJECT

SOURCE_JSON = PROJECT / "q01_kira_master_provenance_audit.json"
OUTPUT_JSON = PROJECT / "q01_kira_master_run_scope_audit.json"
OUTPUT_TXT = PROJECT / "q01_kira_master_run_scope_audit.txt"


def main() -> None:
    print("QEDCalc Q01 masters.final run-scope audit")
    print("mode: saved provenance artifact only; no recomputation")

    if not SOURCE_JSON.exists():
        raise SystemExit(f"ERROR: provenance JSON not found: {SOURCE_JSON}")
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    if not data.get("pass"):
        raise SystemExit("ERROR: provenance audit is not marked PASS")

    artifacts = [
        row for row in data.get("master_artifacts", [])
        if isinstance(row, dict) and row.get("is_masters_final")
    ]
    if not artifacts:
        raise SystemExit("ERROR: no masters.final artifacts in provenance JSON")

    rows = []
    for row in artifacts:
        path = str(row.get("path", ""))
        p = Path(path)
        # The alt_dir is the path prefix before results/Q01_full/masters.final.
        parts = p.parts
        try:
            i = parts.index("results")
            alt_dir = str(Path(*parts[:i])) if i > 0 else "."
        except ValueError:
            alt_dir = str(p.parent)
        rows.append({
            "path": path,
            "alt_dir": alt_dir,
            "master_forms": int(row.get("integral_forms", 0)),
            "final_60_overlap": int(row.get("basis_overlap", 0)),
            "final_60_missing": int(row.get("basis_missing_from_file", 0)),
            "forms_not_in_final_60": int(row.get("forms_not_in_final_basis", 0)),
        })

    rows.sort(key=lambda r: (r["master_forms"], r["path"]))
    count_hist = Counter(r["master_forms"] for r in rows)
    four_rows = [r for r in rows if r["master_forms"] == 4]
    max_overlap = max(r["final_60_overlap"] for r in rows)
    max_overlap_rows = [r for r in rows if r["final_60_overlap"] == max_overlap]

    provenance = data.get("basis_provenance", [])
    membership_hist = Counter()
    membership_rows = []
    for row in provenance:
        if not isinstance(row, dict):
            continue
        files = row.get("masters_final_files", [])
        n = len(files) if isinstance(files, list) else 0
        membership_hist[n] += 1
        membership_rows.append({
            "integral": row.get("integral"),
            "sector": row.get("sector"),
            "masters_final_membership_count": n,
            "masters_final_files": files if isinstance(files, list) else [],
        })

    summary = {
        "mode": "saved-provenance masters.final run-scope audit",
        "masters_final_files": len(rows),
        "masters_final_size_histogram": {str(k): v for k, v in sorted(count_hist.items())},
        "runs": rows,
        "four_master_runs": four_rows,
        "four_master_run_count": len(four_rows),
        "maximum_final_60_overlap_in_one_run": max_overlap,
        "runs_with_maximum_final_60_overlap": max_overlap_rows,
        "final_60_membership_histogram": {str(k): v for k, v in sorted(membership_hist.items())},
        "final_60_membership": membership_rows,
        "interpretation": {
            "four_is_run_scoped": len(four_rows) > 0 and data.get("final_basis_forms_in_any_masters_final") == 60,
            "four_is_not_global_master_count": len(four_rows) > 0 and int(data.get("union_forms_in_all_masters_final", 0)) > 4,
            "report_tag_is_sector_number": bool(data.get("report_tag_is_sector_for_all_reports")),
        },
        "pass": (
            len(rows) == int(data.get("masters_final_files", len(rows)))
            and int(data.get("final_basis_forms_in_any_masters_final", 0)) == 60
            and bool(data.get("report_tag_is_sector_for_all_reports"))
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 masters.final run-scope audit",
        "",
        f"masters.final files: {len(rows)}",
        f"four-master runs: {len(four_rows)}",
        f"maximum overlap with final 60 in one run: {max_overlap}",
        "",
        "Per-run masters.final:",
    ]
    for r in rows:
        lines.append(
            f"  masters={r['master_forms']:3d} overlap60={r['final_60_overlap']:2d} "
            f"extra={r['forms_not_in_final_60']:3d}  {r['alt_dir']}"
        )
    lines.extend(["", "Final-60 membership count histogram:"])
    for n, count in sorted(membership_hist.items()):
        lines.append(f"  present in {n} masters.final file(s): {count} form(s)")
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("masters.final files:", len(rows))
    print("masters.final size histogram:", dict(sorted(count_hist.items())))
    print("four-master runs:", len(four_rows))
    for r in four_rows:
        print("  four-master run:", r["alt_dir"], "overlap60=", r["final_60_overlap"])
    print("maximum final-60 overlap in one masters.final:", max_overlap)
    for r in max_overlap_rows:
        print("  max-overlap run:", r["alt_dir"], "masters=", r["master_forms"])
    print("final-60 masters.final membership histogram:", dict(sorted(membership_hist.items())))
    print("four is run-scoped:", summary["interpretation"]["four_is_run_scoped"])
    print("four is not global master count:", summary["interpretation"]["four_is_not_global_master_count"])
    print("report tag is sector number:", summary["interpretation"]["report_tag_is_sector_number"])
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)

    if not summary["pass"]:
        raise SystemExit("Q01 masters.final run-scope audit FAIL")
    print("Q01 masters.final run-scope audit PASS")


if __name__ == "__main__":
    main()
