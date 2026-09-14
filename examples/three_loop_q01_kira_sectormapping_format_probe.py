"""Inspect saved Kira sectormapping files to determine their exact on-disk syntax.

This diagnostic performs no Kira/FireFly computation.  It reads a small set of
saved Q01 ``sectormappings`` artifacts and records representative non-empty
lines so later code can parse sector/symmetry mappings from facts rather than
from guessed file formats.
"""
from __future__ import annotations

import json
from pathlib import Path

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    ALT_ROOT,
    FAMILY,
    PROJECT,
)

BASE = ALT_ROOT / "sectormappings" / FAMILY
OUTPUT_JSON = PROJECT / "q01_kira_sectormapping_format_probe.json"

CANDIDATES = (
    "relations.frm",
    "symmetries.frm",
    "relations",
    "symmetries",
    "sectorRelations",
    "sectorSymmetries",
)

MAX_LINES_PER_FILE = 18
MAX_LINE_CHARS = 500


def _sample_lines(path: Path) -> list[dict[str, object]]:
    samples: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, raw in enumerate(handle, 1):
            text = raw.rstrip("\r\n")
            if not text.strip():
                continue
            samples.append(
                {
                    "line": line_no,
                    "text": text[:MAX_LINE_CHARS],
                    "truncated": len(text) > MAX_LINE_CHARS,
                }
            )
            if len(samples) >= MAX_LINES_PER_FILE:
                break
    return samples


def main() -> None:
    print("QEDCalc Q01 Kira sectormapping-format probe")
    print("mode: saved metadata only; no Kira/FireFly recomputation")
    print("base:", BASE)

    if not BASE.is_dir():
        raise SystemExit(f"ERROR: sectormappings directory not found: {BASE}")

    files: list[dict[str, object]] = []
    missing: list[str] = []
    for name in CANDIDATES:
        path = BASE / name
        if not path.is_file():
            missing.append(name)
            continue
        samples = _sample_lines(path)
        files.append(
            {
                "name": name,
                "path": str(path),
                "size": path.stat().st_size,
                "sample_nonempty_lines": samples,
            }
        )

        print()
        print(f"--- {name} ---")
        print("size:", path.stat().st_size)
        for item in samples:
            suffix = " ...[truncated]" if item["truncated"] else ""
            print(f"L{item['line']}: {item['text']}{suffix}")

    print()
    print("files found:", len(files))
    print("files missing:", len(missing))
    if missing:
        print("missing names:", missing)

    summary = {
        "mode": "saved Kira sectormapping syntax inspection; no recomputation",
        "base": str(BASE),
        "candidate_names": list(CANDIDATES),
        "files_found": len(files),
        "missing": missing,
        "files": files,
        "pass": len(files) >= 4 and all(item["sample_nonempty_lines"] for item in files),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("probe JSON:", OUTPUT_JSON)

    if not summary["pass"]:
        raise SystemExit("Q01 Kira sectormapping-format probe FAIL")
    print("Q01 Kira sectormapping-format probe PASS")


if __name__ == "__main__":
    main()
