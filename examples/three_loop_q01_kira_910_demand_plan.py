"""Build the exact Kira demand plan for the saved Q01 910-integral set.

This script does not run Kira and does not recompute the expensive projected
trace.  It reads output/3loop_q01_integral_indices.txt, expands the native
D10-D12 numerator ISPs into the Kira quadratic basis, then reports the exact
set of demanded Kira integrals, physical sectors, maximal sectors, and the
minimum observed r/s/d bounds needed by that demand.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

from three_loop.kira_isp_bridge import expand_qedcalc_integral_to_kira


ROOT = Path(__file__).resolve().parents[1]
NATIVE_TXT = ROOT / "output" / "3loop_q01_integral_indices.txt"
OUTPUT_JSON = ROOT / "output" / "kira_q01_910_demand_plan.json"
EXPECTED_NATIVE = 910
_INTEGRAL_RE = re.compile(r"\bI\(\s*([-+]?\d+(?:\s*,\s*[-+]?\d+){11})\s*\)")


def load_native_integrals(path: Path) -> tuple[tuple[int, ...], ...]:
    if not path.exists():
        raise SystemExit(f"ERROR: native integral file not found: {path}")

    parsed: list[tuple[int, ...]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _INTEGRAL_RE.search(line)
        if match is None:
            continue
        parsed.append(tuple(int(v.strip()) for v in match.group(1).split(",")))

    unique = tuple(dict.fromkeys(parsed))
    if len(parsed) != EXPECTED_NATIVE or len(unique) != EXPECTED_NATIVE:
        raise SystemExit(
            "ERROR: expected exactly "
            f"{EXPECTED_NATIVE} unique native integrals, got "
            f"parsed={len(parsed)}, unique={len(unique)}"
        )
    return unique


def sector(indices: tuple[int, ...]) -> int:
    return sum(1 << i for i, power in enumerate(indices[:9]) if power > 0)


def sector_lines(value: int) -> list[int]:
    return [i + 1 for i in range(9) if value & (1 << i)]


def maximal_sectors(sectors: set[int]) -> list[int]:
    """Return demanded sectors not contained in any other demanded sector."""
    result = []
    for item in sorted(sectors):
        if not any(item != other and (item & other) == item for other in sectors):
            result.append(item)
    return result


def main() -> None:
    print("QEDCalc Q01 Kira 910-integral demand planner")
    print("mode: saved native TXT only; Kira is NOT run")
    print("native source:", NATIVE_TXT)

    native = load_native_integrals(NATIVE_TXT)
    print("native integrals total:", len(native))

    demanded: set[tuple[int, ...]] = set()
    expansion_terms_total = 0
    max_expansion_size = 0
    for integral in native:
        expansion = expand_qedcalc_integral_to_kira(integral)
        expansion_terms_total += len(expansion.terms)
        max_expansion_size = max(max_expansion_size, len(expansion.terms))
        demanded.update(term.kira_indices for term in expansion.terms)

    ordered = sorted(demanded)
    sector_counts = Counter(sector(v) for v in ordered)
    sectors = set(sector_counts)
    maxima = maximal_sectors(sectors)

    uncovered = [s for s in sectors if not any((s & top) == s for top in maxima)]
    if uncovered:
        raise SystemExit(f"ERROR: maximal-sector coverage invariant failed: {uncovered[:10]}")

    r_max = max((sum(max(v, 0) for v in integral) for integral in ordered), default=0)
    s_max = max((sum(max(-v, 0) for v in integral) for integral in ordered), default=0)
    d_max = max(
        (sum(max(v - 1, 0) for v in integral if v > 0) for integral in ordered),
        default=0,
    )

    plan = {
        "diagram_id": "Q01",
        "native_source": str(NATIVE_TXT),
        "native_integral_count": len(native),
        "expanded_term_count": expansion_terms_total,
        "unique_demanded_kira_integral_count": len(ordered),
        "max_expansion_size": max_expansion_size,
        "distinct_demanded_sector_count": len(sectors),
        "maximal_sector_count": len(maxima),
        "maximal_sectors": maxima,
        "maximal_sector_lines": {str(s): sector_lines(s) for s in maxima},
        "required_seed_bounds_from_exact_demand": {
            "r_max": r_max,
            "s_max": s_max,
            "d_max": d_max,
        },
        "sector_distribution": {str(k): v for k, v in sorted(sector_counts.items())},
        "all_demanded_kira_integrals": [list(v) for v in ordered],
        "notes": [
            "maximal_sectors are inclusion-maximal among the sectors actually demanded by the 910-integral expansion.",
            "r/s/d values are maxima observed in the exact demanded integrals; Kira may require larger recursive seed limits for a successful reduction.",
            "No Kira job is launched by this planner.",
        ],
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

    print("expanded Kira terms total:", expansion_terms_total)
    print("unique demanded Kira integrals:", len(ordered))
    print("distinct demanded sectors:", len(sectors))
    print("maximal demanded sectors:", len(maxima))
    print("maximal sector list:", maxima)
    print("required demand maxima: r=%d s=%d d=%d" % (r_max, s_max, d_max))
    print("top 20 sectors by demanded integral count:")
    for sec, count in sorted(sector_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
        print(f"  sector {sec}: {count}")
    print("generated:", OUTPUT_JSON)
    print("Q01 Kira 910-integral demand plan PASS")


if __name__ == "__main__":
    main()
