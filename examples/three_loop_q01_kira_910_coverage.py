"""Audit coverage of the saved Q01 910-integral set against the Kira r6s2d2 table.

This runner deliberately does NOT regenerate the expensive Q01 projected trace.
It first tries the saved native-integral text artifact produced by QEDCalc
(`output/3loop_q01_integral_indices.txt`).  The text artifact is accepted only
when it contains exactly 910 unique 12-index native QEDCalc integrals.

For backward compatibility, JSON discovery remains available.  Set
QEDCALC_Q01_INTEGRALS_JSON to an explicit JSON path to force a particular JSON
artifact instead of the native text artifact.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Iterable

from three_loop.kira_isp_bridge import expand_qedcalc_integral_to_kira
from three_loop.kira_reducer import KiraReductionTable


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_4line_full_r6s2d2"
FORM_FILE = PROJECT / "results" / "Q01_4line" / "kira_Q01_4line.inc"
MASTERS_FILE = PROJECT / "results" / "Q01_4line" / "masters.final"
OUTPUT_JSON = PROJECT / "qedcalc_kira_q01_910_coverage.json"
NATIVE_TXT = ROOT / "output" / "3loop_q01_integral_indices.txt"
EXPECTED_NATIVE = 910

_INT_TOKEN_RE = re.compile(r"[-+]?\d+")


def _indices12(value: Any) -> tuple[int, ...] | None:
    if isinstance(value, (list, tuple)) and len(value) == 12:
        try:
            return tuple(int(v) for v in value)
        except (TypeError, ValueError):
            return None
    if isinstance(value, str):
        text = value.strip()
        # Accept forms such as I(1,...), Q01(...), [1,...], or comma lists.
        if "(" in text and ")" in text:
            text = text[text.find("(") + 1 : text.rfind(")")]
        elif "[" in text and "]" in text:
            text = text[text.find("[") + 1 : text.rfind("]")]
        nums = _INT_TOKEN_RE.findall(text)
        if len(nums) == 12:
            try:
                return tuple(int(v) for v in nums)
            except ValueError:
                return None
    if isinstance(value, dict):
        for key in ("powers", "indices", "integral", "index", "exponents"):
            if key in value:
                parsed = _indices12(value[key])
                if parsed is not None:
                    return parsed
    return None


def _load_native_txt(path: Path) -> tuple[tuple[int, ...], ...] | None:
    """Load the canonical Q01 integral-index text artifact if it is complete."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return None

    parsed: list[tuple[int, ...]] = []
    malformed: list[tuple[int, str]] = []
    for line_no, line in enumerate(lines, 1):
        text = line.strip()
        if not text:
            continue
        value = _indices12(text)
        if value is None:
            malformed.append((line_no, text))
            continue
        parsed.append(value)

    unique = tuple(dict.fromkeys(parsed))
    if malformed:
        print(f"WARNING: native TXT contains {len(malformed)} non-integral line(s); not using it.")
        for line_no, text in malformed[:5]:
            print(f"  line {line_no}: {text[:160]}")
        return None
    if len(parsed) != EXPECTED_NATIVE or len(unique) != EXPECTED_NATIVE:
        print(
            "WARNING: native TXT does not contain exactly "
            f"{EXPECTED_NATIVE} unique 12-index integrals "
            f"(parsed={len(parsed)}, unique={len(unique)}); not using it."
        )
        return None
    return unique


def _extract_integral_sets(obj: Any, trail: str = "$") -> list[tuple[str, tuple[tuple[int, ...], ...]]]:
    """Find list/dict containers that encode exactly 910 unique 12-index tuples."""
    found: list[tuple[str, tuple[tuple[int, ...], ...]]] = []

    if isinstance(obj, list):
        parsed = [_indices12(v) for v in obj]
        if parsed and all(v is not None for v in parsed):
            unique = tuple(dict.fromkeys(v for v in parsed if v is not None))
            if len(unique) == EXPECTED_NATIVE:
                found.append((trail, unique))
        for i, value in enumerate(obj):
            if isinstance(value, (dict, list)):
                found.extend(_extract_integral_sets(value, f"{trail}[{i}]"))
        return found

    if isinstance(obj, dict):
        # Some manifests store integral strings as dictionary keys.
        key_parsed = [_indices12(k) for k in obj.keys()]
        valid_keys = [v for v in key_parsed if v is not None]
        if len(valid_keys) == len(obj) and len(set(valid_keys)) == EXPECTED_NATIVE:
            found.append((trail + "{keys}", tuple(dict.fromkeys(valid_keys))))

        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                found.extend(_extract_integral_sets(value, f"{trail}.{key}"))
    return found


def _candidate_score(path: Path, trail: str) -> int:
    text = (str(path) + " " + trail).lower()
    score = 0
    for token, weight in (
        ("q01", 8),
        ("integral", 6),
        ("mapping", 5),
        ("mapped", 4),
        ("project", 1),
        ("kira", -2),
        ("coverage", -10),
    ):
        if token in text:
            score += weight
    return score


def _discover_saved_integrals() -> tuple[Path, str, tuple[tuple[int, ...], ...]]:
    explicit = os.environ.get("QEDCALC_Q01_INTEGRALS_JSON", "").strip()
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise FileNotFoundError(f"QEDCALC_Q01_INTEGRALS_JSON does not exist: {path}")
        paths = [path]
    else:
        native_txt = _load_native_txt(NATIVE_TXT) if NATIVE_TXT.exists() else None
        if native_txt is not None:
            return NATIVE_TXT, "$txt", native_txt

        output_root = ROOT / "output"
        paths = sorted(output_root.rglob("*.json")) if output_root.exists() else []

    candidates: list[tuple[int, Path, str, tuple[tuple[int, ...], ...]]] = []
    searched: list[str] = []
    for path in paths:
        if path.resolve() == OUTPUT_JSON.resolve():
            continue
        searched.append(str(path))
        try:
            # Avoid accidentally loading giant unrelated JSON artifacts.
            if path.stat().st_size > 128 * 1024 * 1024:
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        for trail, integrals in _extract_integral_sets(data):
            candidates.append((_candidate_score(path, trail), path, trail, integrals))

    # Deduplicate identical datasets, retaining the highest-scoring location.
    best_by_dataset: dict[tuple[tuple[int, ...], ...], tuple[int, Path, str]] = {}
    for score, path, trail, integrals in candidates:
        canonical = tuple(sorted(integrals))
        previous = best_by_dataset.get(canonical)
        if previous is None or score > previous[0]:
            best_by_dataset[canonical] = (score, path, trail)

    ranked = sorted(
        ((score, path, trail, dataset) for dataset, (score, path, trail) in best_by_dataset.items()),
        key=lambda item: (-item[0], str(item[1]), item[2]),
    )
    if not ranked:
        print("ERROR: no saved artifact containing exactly 910 unique 12-index Q01 integrals was found.")
        print("The expensive projected trace was NOT recomputed.")
        if not explicit:
            print("Expected native TXT:", NATIVE_TXT)
        print("Set QEDCALC_Q01_INTEGRALS_JSON to a saved mapping JSON if needed.")
        print(f"JSON files searched: {len(searched)}")
        for item in searched[:30]:
            print(f"  searched: {item}")
        if len(searched) > 30:
            print(f"  ... {len(searched)-30} more")
        raise SystemExit(2)

    if len(ranked) > 1 and ranked[0][0] == ranked[1][0]:
        print("ERROR: multiple different 910-integral datasets have the same discovery score; refusing to guess.")
        print("Set QEDCALC_Q01_INTEGRALS_JSON to select the intended artifact.")
        for score, path, trail, _ in ranked[:10]:
            print(f"  candidate score={score}: {path} :: {trail}")
        raise SystemExit(2)

    score, path, trail, dataset = ranked[0]
    return path, trail, dataset


def _sector(indices: tuple[int, ...]) -> int:
    return sum((1 << i) for i, power in enumerate(indices[:9]) if power > 0)


def _demand_stats(indices: tuple[int, ...]) -> dict[str, int]:
    return {
        "sector": _sector(indices),
        "positive_power_sum": sum(max(v, 0) for v in indices),
        "negative_power_sum": sum(max(-v, 0) for v in indices),
        "dot_count": sum(max(v - 1, 0) for v in indices[:9]),
    }


def main() -> None:
    print("QEDCalc Q01 Kira 910-integral coverage audit")
    print("project:", PROJECT)
    print("mode: saved native-integral artifact only; projected trace is not recomputed")

    if not FORM_FILE.exists() or not MASTERS_FILE.exists():
        print("ERROR: existing Kira r6s2d2 FORM export/master list is missing.")
        print("  FORM   :", FORM_FILE)
        print("  masters:", MASTERS_FILE)
        raise SystemExit(2)

    source_path, source_trail, native_integrals = _discover_saved_integrals()
    print("native source:", source_path)
    print("native artifact path:", source_trail)
    print("native integrals total:", len(native_integrals))

    table = KiraReductionTable.from_form_export(FORM_FILE, MASTERS_FILE)
    print("Kira rules loaded:", len(table.rules))
    print("Kira masters loaded:", len(table.masters))

    status_counts: Counter[str] = Counter()
    isp_degree_counts: Counter[int] = Counter()
    missing_sector_counts: Counter[int] = Counter()
    missing_kira: set[tuple[int, ...]] = set()
    unique_expanded: set[tuple[int, ...]] = set()
    total_expanded_terms = 0
    max_expansion_size = 0
    missing_examples: list[dict[str, Any]] = []
    rejected_examples: list[dict[str, Any]] = []

    for native in native_integrals:
        isp_degree = sum(max(-power, 0) for power in native[9:12])
        isp_degree_counts[isp_degree] += 1
        try:
            expansion = expand_qedcalc_integral_to_kira(native)
        except Exception as exc:
            status_counts["rejected"] += 1
            if len(rejected_examples) < 10:
                rejected_examples.append({"native": list(native), "error": str(exc)})
            continue

        total_expanded_terms += len(expansion.terms)
        max_expansion_size = max(max_expansion_size, len(expansion.terms))
        resolved = 0
        unresolved = 0
        local_missing: list[tuple[int, ...]] = []
        for term in expansion.terms:
            kira = term.kira_indices
            unique_expanded.add(kira)
            result = table.reduce_kira(kira)
            if result.status == "not_in_table":
                unresolved += 1
                missing_kira.add(kira)
                missing_sector_counts[_sector(kira)] += 1
                local_missing.append(kira)
            else:
                resolved += 1

        if unresolved == 0:
            status_counts["fully_reduced"] += 1
        elif resolved:
            status_counts["partially_reduced"] += 1
        else:
            status_counts["missing"] += 1

        if local_missing and len(missing_examples) < 10:
            missing_examples.append(
                {
                    "native": list(native),
                    "expansion_terms": len(expansion.terms),
                    "missing": [list(v) for v in local_missing[:10]],
                }
            )

    missing_demand = [_demand_stats(v) for v in sorted(missing_kira)]
    summary = {
        "native_source": str(source_path),
        "native_artifact_path": source_trail,
        "native_json_path": source_trail,
        "native_integrals_total": len(native_integrals),
        "status_counts": dict(sorted(status_counts.items())),
        "expanded_kira_terms_total": total_expanded_terms,
        "unique_expanded_kira_integrals": len(unique_expanded),
        "unique_missing_kira_integrals": len(missing_kira),
        "max_isp_expansion_size": max_expansion_size,
        "native_isp_degree_distribution": {str(k): v for k, v in sorted(isp_degree_counts.items())},
        "missing_sector_distribution": {str(k): v for k, v in sorted(missing_sector_counts.items())},
        "missing_demand_maxima": {
            "positive_power_sum": max((v["positive_power_sum"] for v in missing_demand), default=0),
            "negative_power_sum": max((v["negative_power_sum"] for v in missing_demand), default=0),
            "dot_count": max((v["dot_count"] for v in missing_demand), default=0),
        },
        "missing_examples": missing_examples,
        "rejected_examples": rejected_examples,
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("fully reduced:", status_counts["fully_reduced"])
    print("partially reduced:", status_counts["partially_reduced"])
    print("missing:", status_counts["missing"])
    print("rejected:", status_counts["rejected"])
    print("expanded Kira terms:", total_expanded_terms)
    print("unique expanded Kira integrals:", len(unique_expanded))
    print("unique missing Kira integrals:", len(missing_kira))
    print("max ISP expansion size:", max_expansion_size)
    print("native ISP degree distribution:")
    for degree, count in sorted(isp_degree_counts.items()):
        print(f"  degree {degree}: {count}")
    print("missing sector distribution (top 20 by count):")
    for sector, count in sorted(missing_sector_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
        print(f"  sector {sector}: {count}")
    print("missing demand maxima:", summary["missing_demand_maxima"])
    if missing_examples:
        print("missing examples:")
        for item in missing_examples[:5]:
            print("  native", tuple(item["native"]), "->", len(item["missing"]), "missing shown")
    if rejected_examples:
        print("rejected examples:")
        for item in rejected_examples[:5]:
            print("  native", tuple(item["native"]), "->", item["error"])
    print("generated:", OUTPUT_JSON)

    if len(native_integrals) != EXPECTED_NATIVE:
        raise SystemExit(f"expected {EXPECTED_NATIVE} native integrals")
    print("Q01 Kira 910-integral coverage PASS")


if __name__ == "__main__":
    main()
