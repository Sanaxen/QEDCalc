"""Parse compact structural results from Kira 3.x text logs.

The parser intentionally depends only on stable, human-readable milestones in
Kira's stdout.  It is used as an independent bridge layer: QEDCalc can record
master integrals, equation counts and timings without depending on Kira's
internal database format.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


_MASTER_RE = re.compile(
    r"^(?P<family>[A-Za-z0-9_]+)\[(?P<indices>-?\d+(?:,-?\d+)*)\]\s*#\s*(?P<sector>\d+)\s*$"
)
_EQ_RE = re.compile(
    r"^(?P<total>\d+) equations:\s*(?P<zero>\d+) zero \+ (?P<independent>\d+) independent\s*$"
)
_MASTER_COUNT_RE = re.compile(r"^Number of master integrals:\s*(?P<count>\d+)\s*$")
_IBP_RE = re.compile(r"^There are (?P<count>\d+) IBP identities\s*$")
_LI_RE = re.compile(r"^There are (?P<count>\d+) LI identities\s*$")
_NONTRIVIAL_RE = re.compile(r"^Non trivial sectors in total:\s*(?P<count>\d+)\s*$")
_TRIVIAL_RE = re.compile(r"^Trivial sectors in total:\s*(?P<count>\d+)\s*$")
_SECTOR_REL_RE = re.compile(r"^Sector relations:\s*(?P<count>\d+)\s*$")
_SECTOR_SYM_RE = re.compile(r"^Sector symmetries:\s*(?P<count>\d+)\s*$")
_TRIANGULAR_RE = re.compile(r"^Triangular form completed after \(\s*(?P<seconds>[0-9.]+) s \)\s*$")
_TIME_ONLY_RE = re.compile(r"^\(\s*(?P<seconds>[0-9.]+) s \)\s*$")


@dataclass(frozen=True)
class KiraMasterIntegral:
    family: str
    indices: tuple[int, ...]
    sector: int

    def as_dict(self) -> dict[str, object]:
        return {
            "family": self.family,
            "indices": list(self.indices),
            "sector": self.sector,
        }


def _first_int(lines: Iterable[str], pattern: re.Pattern[str]) -> int | None:
    for raw in lines:
        match = pattern.match(raw.strip())
        if match:
            return int(match.group("count"))
    return None


def parse_kira_log_text(text: str) -> dict[str, object]:
    lines = text.splitlines()
    masters: list[KiraMasterIntegral] = []
    equation_summaries: list[dict[str, int]] = []
    declared_master_count: int | None = None
    triangular_seconds: float | None = None
    total_seconds: float | None = None

    for pos, raw in enumerate(lines):
        line = raw.strip()
        match = _MASTER_RE.match(line)
        if match:
            masters.append(
                KiraMasterIntegral(
                    family=match.group("family"),
                    indices=tuple(int(v) for v in match.group("indices").split(",")),
                    sector=int(match.group("sector")),
                )
            )
            continue

        match = _EQ_RE.match(line)
        if match:
            equation_summaries.append(
                {
                    "total": int(match.group("total")),
                    "zero": int(match.group("zero")),
                    "independent": int(match.group("independent")),
                }
            )
            continue

        match = _MASTER_COUNT_RE.match(line)
        if match:
            declared_master_count = int(match.group("count"))
            continue

        match = _TRIANGULAR_RE.match(line)
        if match:
            triangular_seconds = float(match.group("seconds"))
            continue

        if line == "Total time:" and pos + 1 < len(lines):
            next_match = _TIME_ONLY_RE.match(lines[pos + 1].strip())
            if next_match:
                total_seconds = float(next_match.group("seconds"))

    # Kira can print masters more than once in some job layouts.  Preserve
    # first-seen order while removing exact duplicates.
    unique_masters: list[KiraMasterIntegral] = []
    seen: set[tuple[str, tuple[int, ...], int]] = set()
    for master in masters:
        key = (master.family, master.indices, master.sector)
        if key not in seen:
            seen.add(key)
            unique_masters.append(master)

    parsed_count = len(unique_masters)
    consistent_master_count = (
        declared_master_count is None or declared_master_count == parsed_count
    )

    return {
        "ibp_identity_count": _first_int(lines, _IBP_RE),
        "li_identity_count": _first_int(lines, _LI_RE),
        "nontrivial_sector_count": _first_int(lines, _NONTRIVIAL_RE),
        "trivial_sector_count": _first_int(lines, _TRIVIAL_RE),
        "sector_relation_count": _first_int(lines, _SECTOR_REL_RE),
        "sector_symmetry_count": _first_int(lines, _SECTOR_SYM_RE),
        "declared_master_count": declared_master_count,
        "parsed_master_count": parsed_count,
        "master_count_consistent": consistent_master_count,
        "masters": [master.as_dict() for master in unique_masters],
        "equation_summaries": equation_summaries,
        "triangular_seconds": triangular_seconds,
        "total_seconds": total_seconds,
    }


def parse_kira_log(path: str | Path) -> dict[str, object]:
    return parse_kira_log_text(Path(path).read_text(encoding="utf-8", errors="replace"))
