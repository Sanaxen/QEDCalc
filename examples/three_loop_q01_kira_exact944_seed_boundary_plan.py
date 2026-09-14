"""Plan the smallest saved-artifact-driven Q01 exact944 seed-boundary extension tests.

No Kira/FireFly/Fermat/projected-trace recomputation is performed.
The script scans saved exact944 job YAMLs, extracts r/s/d and top-sector settings,
records mandatory target coverage, and proposes one-axis-at-a-time extensions.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import PROJECT

SCOPE_JSON = PROJECT / "q01_kira_exact944_ibp_scope_audit.json"
OUTPUT_JSON = PROJECT / "q01_kira_exact944_seed_boundary_plan.json"
OUTPUT_TXT = PROJECT / "q01_kira_exact944_seed_boundary_plan.txt"

_ALT_RE = re.compile(r"\balt_dir\s*:\s*exact944(?:\s|$)")
_R_RE = re.compile(r"^\s*r\s*:\s*(\d+)\s*(?:#.*)?$", re.MULTILINE)
_S_RE = re.compile(r"^\s*s\s*:\s*(\d+)\s*(?:#.*)?$", re.MULTILINE)
_D_RE = re.compile(r"^\s*d\s*:\s*(\d+)\s*(?:#.*)?$", re.MULTILINE)
_TOP_RE = re.compile(r"^\s*top_level_sectors?\s*:\s*(.+?)\s*(?:#.*)?$", re.MULTILINE)


def _last_int(regex: re.Pattern[str], text: str) -> int | None:
    vals = regex.findall(text)
    return int(vals[-1]) if vals else None


def main() -> None:
    print("QEDCalc Q01 exact944 seed-boundary planning audit")
    print("mode: saved YAML/artifacts only; no recomputation")

    if not SCOPE_JSON.exists():
        raise SystemExit(f"ERROR: prerequisite scope JSON not found: {SCOPE_JSON}")
    scope = json.loads(SCOPE_JSON.read_text(encoding="utf-8"))
    if not scope.get("pass"):
        raise SystemExit("ERROR: exact944 IBP scope audit is not marked PASS")

    rows = []
    tuples = set()
    for path in sorted(PROJECT.rglob("*.yaml")):
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError):
            continue
        if not _ALT_RE.search(text):
            continue
        r = _last_int(_R_RE, text)
        s = _last_int(_S_RE, text)
        d = _last_int(_D_RE, text)
        tops = _TOP_RE.findall(text)
        top = tops[-1].strip() if tops else None
        rows.append({
            "path": str(path.relative_to(PROJECT)),
            "r": r,
            "s": s,
            "d": d,
            "top_level_sectors": top,
        })
        if r is not None and s is not None and d is not None:
            tuples.add((r, s, d))

    complete_rows = [row for row in rows if all(row[k] is not None for k in ("r", "s", "d"))]
    if not complete_rows:
        raise SystemExit("ERROR: no exact944 YAML with complete r/s/d settings was found")

    # Use the component-wise maxima as the strongest saved exact944 seed scope.
    base_r = max(int(row["r"]) for row in complete_rows)
    base_s = max(int(row["s"]) for row in complete_rows)
    base_d = max(int(row["d"]) for row in complete_rows)
    base = (base_r, base_s, base_d)

    proposals = [
        {"name": "r_plus_1", "r": base_r + 1, "s": base_s, "d": base_d,
         "purpose": "test sensitivity to one extra denominator power"},
        {"name": "s_plus_1", "r": base_r, "s": base_s + 1, "d": base_d,
         "purpose": "test sensitivity to one extra numerator/ISP complexity unit"},
        {"name": "d_plus_1", "r": base_r, "s": base_s, "d": base_d + 1,
         "purpose": "test sensitivity to one extra dot-count allowance"},
    ]

    summary = {
        "mode": "saved-artifact exact944 seed-boundary planning audit",
        "prerequisite_scope_pass": bool(scope.get("pass")),
        "exact944_yaml_files_scanned": len(rows),
        "yaml_rows": rows,
        "unique_complete_rsd_settings": [list(v) for v in sorted(tuples)],
        "strongest_saved_componentwise_scope": {"r": base_r, "s": base_s, "d": base_d},
        "proposed_one_axis_extensions": proposals,
        "recommended_order": ["r_plus_1", "s_plus_1", "d_plus_1"],
        "interpretation": (
            "Run one-axis-at-a-time extensions first. If all three retain the same final-60 subset "
            "inside the new masters.final and the 944 mandatory targets remain fully reduced, the "
            "claim that the 60-form basis is stable against modest seed-boundary enlargement becomes "
            "substantially stronger. This still does not constitute a proof for arbitrarily large seeds."
        ),
        "pass": len(rows) > 0 and len(complete_rows) > 0,
    }

    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "QEDCalc Q01 exact944 seed-boundary planning audit",
        "",
        f"exact944 YAML files scanned: {len(rows)}",
        f"unique complete r/s/d settings: {len(tuples)}",
        f"strongest saved component-wise scope: r={base_r}, s={base_s}, d={base_d}",
        "",
        "Saved exact944 YAML scopes:",
    ]
    for row in rows:
        lines.append(
            f"  {row['path']}: r={row['r']} s={row['s']} d={row['d']} top={row['top_level_sectors']}"
        )
    lines.extend(["", "Proposed minimal boundary extensions:"])
    for p in proposals:
        lines.append(f"  {p['name']}: r={p['r']} s={p['s']} d={p['d']} -- {p['purpose']}")
    lines.extend(["", summary["interpretation"]])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("exact944 YAML files scanned:", len(rows))
    print("unique complete r/s/d settings:", sorted(tuples))
    print("strongest saved component-wise scope:", f"r={base_r} s={base_s} d={base_d}")
    for p in proposals:
        print("proposal:", p["name"], f"r={p['r']} s={p['s']} d={p['d']}")
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)

    if not summary["pass"]:
        raise SystemExit("Q01 exact944 seed-boundary planning audit FAIL")
    print("Q01 exact944 seed-boundary planning audit PASS")


if __name__ == "__main__":
    main()
