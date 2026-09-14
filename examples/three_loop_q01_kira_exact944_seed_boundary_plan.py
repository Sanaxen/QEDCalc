"""Plan minimal Q01 exact944 seed-boundary extension tests from saved artifacts.

No Kira/FireFly/Fermat/projected-trace recomputation is performed.

Older Q01 job YAMLs do not necessarily store r/s/d together in one file.  This
audit therefore reconstructs the saved scope from multiple sources, in order:

1. exact944-related YAML values for each axis independently;
2. the project directory name (for example ``kira_q01_full_demand_r9s3d0``),
   which records the seed scope used to build the saved project;
3. saved scope-setting lines from the preceding IBP-scope audit.

The purpose is planning only: propose one-axis-at-a-time enlargement tests from
the strongest recoverable saved scope.
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
_PROJECT_SCOPE_RE = re.compile(r"(?:^|_)r(?P<r>\d+)s(?P<s>\d+)d(?P<d>\d+)(?:_|$)")
_INLINE_R_RE = re.compile(r"\br\s*[:=]\s*(\d+)")
_INLINE_S_RE = re.compile(r"\bs\s*[:=]\s*(\d+)")
_INLINE_D_RE = re.compile(r"\bd\s*[:=]\s*(\d+)")


def _last_int(regex: re.Pattern[str], text: str) -> int | None:
    vals = regex.findall(text)
    return int(vals[-1]) if vals else None


def _project_scope() -> tuple[int, int, int] | None:
    match = _PROJECT_SCOPE_RE.search(PROJECT.name)
    if not match:
        return None
    return (int(match.group("r")), int(match.group("s")), int(match.group("d")))


def _scope_line_values(scope: dict) -> dict[str, list[int]]:
    result = {"r": [], "s": [], "d": []}
    lines = scope.get("scope_setting_lines", [])
    if not isinstance(lines, list):
        return result
    for raw in lines:
        text = str(raw)
        for key, regex in (("r", _INLINE_R_RE), ("s", _INLINE_S_RE), ("d", _INLINE_D_RE)):
            for value in regex.findall(text):
                result[key].append(int(value))
    return result


def main() -> None:
    print("QEDCalc Q01 exact944 seed-boundary planning audit")
    print("mode: saved YAML/artifacts only; no recomputation")

    if not SCOPE_JSON.exists():
        raise SystemExit(f"ERROR: prerequisite scope JSON not found: {SCOPE_JSON}")
    scope = json.loads(SCOPE_JSON.read_text(encoding="utf-8"))
    if not scope.get("pass"):
        raise SystemExit("ERROR: exact944 IBP scope audit is not marked PASS")

    rows = []
    yaml_axis_values = {"r": [], "s": [], "d": []}
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
        if r is not None:
            yaml_axis_values["r"].append(r)
        if s is not None:
            yaml_axis_values["s"].append(s)
        if d is not None:
            yaml_axis_values["d"].append(d)
        if r is not None and s is not None and d is not None:
            tuples.add((r, s, d))

    project_scope = _project_scope()
    line_values = _scope_line_values(scope)

    recovered: dict[str, int | None] = {"r": None, "s": None, "d": None}
    sources: dict[str, list[str]] = {"r": [], "s": [], "d": []}

    for key in ("r", "s", "d"):
        candidates: list[int] = []
        if yaml_axis_values[key]:
            candidates.extend(yaml_axis_values[key])
            sources[key].append("exact944 YAML")
        if line_values[key]:
            candidates.extend(line_values[key])
            sources[key].append("IBP-scope audit setting lines")
        if project_scope is not None:
            project_value = {"r": project_scope[0], "s": project_scope[1], "d": project_scope[2]}[key]
            candidates.append(project_value)
            sources[key].append("project directory name")
        recovered[key] = max(candidates) if candidates else None

    if any(recovered[k] is None for k in ("r", "s", "d")):
        missing = [k for k in ("r", "s", "d") if recovered[k] is None]
        raise SystemExit(
            "ERROR: could not reconstruct complete exact944 seed scope; missing axes: "
            + ", ".join(missing)
        )

    base_r = int(recovered["r"])
    base_s = int(recovered["s"])
    base_d = int(recovered["d"])

    proposals = [
        {"name": "r_plus_1", "r": base_r + 1, "s": base_s, "d": base_d,
         "purpose": "test sensitivity to one extra denominator-power allowance"},
        {"name": "s_plus_1", "r": base_r, "s": base_s + 1, "d": base_d,
         "purpose": "test sensitivity to one extra numerator/ISP-complexity allowance"},
        {"name": "d_plus_1", "r": base_r, "s": base_s, "d": base_d + 1,
         "purpose": "test sensitivity to one extra dot-count allowance"},
    ]

    summary = {
        "mode": "saved-artifact exact944 seed-boundary planning audit",
        "prerequisite_scope_pass": bool(scope.get("pass")),
        "project_directory": str(PROJECT),
        "project_directory_scope": (
            {"r": project_scope[0], "s": project_scope[1], "d": project_scope[2]}
            if project_scope is not None else None
        ),
        "exact944_yaml_files_scanned": len(rows),
        "yaml_rows": rows,
        "yaml_axis_values": {k: sorted(set(v)) for k, v in yaml_axis_values.items()},
        "unique_complete_rsd_settings": [list(v) for v in sorted(tuples)],
        "ibp_scope_line_axis_values": {k: sorted(set(v)) for k, v in line_values.items()},
        "reconstructed_saved_scope": {"r": base_r, "s": base_s, "d": base_d},
        "scope_sources": sources,
        "proposed_one_axis_extensions": proposals,
        "recommended_order": ["r_plus_1", "s_plus_1", "d_plus_1"],
        "interpretation": (
            "The exact944 YAMLs do not need to contain r/s/d in one file. The saved project-name "
            "scope and any axis values found in YAML/audit metadata are combined conservatively by "
            "taking the maximum recovered value per axis. One-axis-at-a-time extensions are then "
            "used to test stability of the 60-form basis without immediately paying for a full "
            "three-axis enlargement."
        ),
        "pass": len(rows) > 0 and all(recovered[k] is not None for k in ("r", "s", "d")),
    }

    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "QEDCalc Q01 exact944 seed-boundary planning audit",
        "",
        f"exact944 YAML files scanned: {len(rows)}",
        f"unique complete r/s/d settings in one YAML: {len(tuples)}",
        f"project-directory encoded scope: {project_scope}",
        f"reconstructed saved scope: r={base_r}, s={base_s}, d={base_d}",
        f"scope sources: r={sources['r']}; s={sources['s']}; d={sources['d']}",
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
    print("unique complete r/s/d settings in one YAML:", sorted(tuples))
    print("project-directory encoded scope:", project_scope)
    print("reconstructed saved scope:", f"r={base_r} s={base_s} d={base_d}")
    print("scope sources:", sources)
    for p in proposals:
        print("proposal:", p["name"], f"r={p['r']} s={p['s']} d={p['d']}")
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)

    if not summary["pass"]:
        raise SystemExit("Q01 exact944 seed-boundary planning audit FAIL")
    print("Q01 exact944 seed-boundary planning audit PASS")


if __name__ == "__main__":
    main()
