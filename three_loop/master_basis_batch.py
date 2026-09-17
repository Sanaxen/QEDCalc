"""Resumable batch planning/checkpoint utilities for stage-2 master-basis work.

The module is intentionally conservative: it discovers already completed seed
audits, builds an execution queue from the canonical master-basis schedule,
records per-step runtimes, and estimates remaining wall-clock time. Actual Kira
execution remains in the thin Windows BAT layer.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
from pathlib import Path
import statistics
from typing import Any, Iterable

from three_loop.integral_family_classification import ROOT, load_topologies
from three_loop.master_basis_api import Seed, build_family_spec
from three_loop.master_basis_schedule import build_master_basis_schedule

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
CHECKPOINT = AUDIT_DIR / "three_loop_master_basis_batch_checkpoint.json"
RUNTIME_DB = AUDIT_DIR / "three_loop_master_basis_runtime_history.json"


@dataclass(frozen=True)
class BatchStep:
    family: str
    phase: str
    seed: Seed
    solver: str

    @property
    def key(self) -> str:
        return f"{self.family}:{self.phase}:{self.seed.tag}:{self.solver}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "phase": self.phase,
            "seed": asdict(self.seed),
            "seed_tag": self.seed.tag,
            "solver": self.solver,
            "key": self.key,
        }


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def _seed_from_obj(obj: Any) -> Seed | None:
    if not isinstance(obj, dict):
        return None
    try:
        return Seed(int(obj["r"]), int(obj.get("s", 0)), int(obj.get("d", 0)))
    except Exception:
        return None


def discover_seed_results() -> dict[tuple[str, str], dict[str, Any]]:
    """Index successful existing seed audits, including older dedicated audits."""
    out: dict[tuple[str, str], dict[str, Any]] = {}
    if not AUDIT_DIR.exists():
        return out
    for path in AUDIT_DIR.glob("*.json"):
        payload = _read_json(path)
        if not payload or payload.get("audit_pass") is False:
            continue
        family = payload.get("family") or payload.get("canonical_family")
        seed = _seed_from_obj(payload.get("seed"))
        masters = payload.get("masters")
        count = payload.get("master_count")
        if not family or seed is None:
            continue
        if not isinstance(masters, list) and not isinstance(count, int):
            continue
        out[(str(family), seed.tag)] = {
            "path": str(path),
            "family": str(family),
            "seed": seed.tag,
            "master_count": int(count if isinstance(count, int) else len(masters)),
            "solver": str(payload.get("solver") or payload.get("solver_backend") or "legacy"),
        }
    return out


def load_runtime_history() -> list[dict[str, Any]]:
    payload = _read_json(RUNTIME_DB)
    rows = payload.get("records", []) if payload else []
    return [row for row in rows if isinstance(row, dict)]


def append_runtime(record: dict[str, Any]) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_runtime_history()
    rows.append(record)
    RUNTIME_DB.write_text(
        json.dumps({"schema_version": 1, "records": rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_checkpoint() -> dict[str, Any]:
    return _read_json(CHECKPOINT) or {"schema_version": 1, "steps": {}}


def save_checkpoint(payload: dict[str, Any]) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def update_checkpoint(step: BatchStep, *, status: str, elapsed_s: float | None = None,
                      detail: str | None = None) -> None:
    payload = load_checkpoint()
    steps = payload.setdefault("steps", {})
    item = step.to_dict()
    item["status"] = status
    if elapsed_s is not None:
        item["elapsed_s"] = float(elapsed_s)
    if detail:
        item["detail"] = detail
    steps[step.key] = item
    save_checkpoint(payload)


@lru_cache(maxsize=1)
def execution_families() -> tuple[str, ...]:
    schedule = build_master_basis_schedule(load_topologies())
    return tuple(str(item["canonical_family_id"]) for item in schedule.get("schedule", []))


@lru_cache(maxsize=None)
def cached_family_spec(family_id: str):
    return build_family_spec(family_id)


def family_steps(family_id: str, *, baseline_solver: str = "ordinary",
                 boundary_solver: str = "firefly") -> list[BatchStep]:
    spec = cached_family_spec(family_id)
    base = spec.baseline_seed
    r1, s1, d1 = base.one_axis_extensions()
    return [
        BatchStep(family_id, "baseline", base, baseline_solver),
        BatchStep(family_id, "boundary-r", r1, boundary_solver),
        BatchStep(family_id, "boundary-s", s1, boundary_solver),
        BatchStep(family_id, "boundary-d", d1, boundary_solver),
    ]


def build_queue(*, start_family: str | None = None) -> list[BatchStep]:
    families = list(execution_families())
    if start_family:
        if start_family not in families:
            raise ValueError(f"start family is not pending: {start_family}")
        families = families[families.index(start_family):]
    existing = discover_seed_results()
    checkpoint = load_checkpoint().get("steps", {})
    queue: list[BatchStep] = []
    for family in families:
        for step in family_steps(family):
            prior = checkpoint.get(step.key, {})
            if prior.get("status") == "pass":
                continue
            if (step.family, step.seed.tag) in existing:
                continue
            queue.append(step)
    return queue


def _runtime_samples(step: BatchStep, history: Iterable[dict[str, Any]]) -> list[float]:
    spec = cached_family_spec(step.family)
    exact: list[float] = []
    structural: list[float] = []
    phase_class = "baseline" if step.phase == "baseline" else "boundary"
    for row in history:
        try:
            elapsed = float(row["elapsed_s"])
        except Exception:
            continue
        if elapsed <= 0:
            continue
        if row.get("phase_class") != phase_class:
            continue
        if row.get("solver") == step.solver and row.get("unique_physical") == spec.unique_physical_count:
            structural.append(elapsed)
            if row.get("topology") == spec.topology_family:
                exact.append(elapsed)
    return exact or structural


def estimate_step(step: BatchStep) -> dict[str, Any]:
    """Return a deliberately broad runtime estimate from local empirical history."""
    samples = _runtime_samples(step, load_runtime_history())
    if not samples:
        if step.phase == "baseline":
            samples = [1246.3, 2244.1]
        else:
            samples = [896.5, 2045.2, 3298.4, 18358.8]
    median = statistics.median(samples)
    low = max(60.0, min(samples) * 0.7)
    high = max(median * 2.0, max(samples) * 1.25)
    return {
        "median_s": float(median),
        "low_s": float(low),
        "high_s": float(high),
        "sample_count": len(samples),
    }


def estimate_queue(queue: Iterable[BatchStep]) -> dict[str, Any]:
    rows = []
    total_low = total_mid = total_high = 0.0
    for step in queue:
        est = estimate_step(step)
        rows.append({**step.to_dict(), "estimate": est})
        total_low += est["low_s"]
        total_mid += est["median_s"]
        total_high += est["high_s"]
    return {
        "steps": rows,
        "step_count": len(rows),
        "total_low_s": total_low,
        "total_median_s": total_mid,
        "total_high_s": total_high,
    }
