from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

ENV_PROCESSES = "QEDCALC_PROCESSES"
DEFAULT_PROCESSES = 1
DEFAULT_CONFIG_NAME = "qedcalc_runtime.json"


@dataclass(frozen=True)
class RuntimeConfig:
    requested_processes: int
    effective_processes: int
    source: str
    config_path: str | None


def _positive_int(value, *, name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive integer, got {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{name} must be >= 1, got {parsed}")
    return parsed


def load_runtime_config(
    *,
    root: Path | None = None,
    max_useful_processes: int | None = None,
) -> RuntimeConfig:
    """Resolve the QEDCalc process count.

    Priority:
      1. QEDCALC_PROCESSES environment variable
      2. qedcalc_runtime.json in ``root``
      3. safe default of one process

    ``max_useful_processes`` caps the effective process count for a phase that
    exposes only a limited number of independent jobs (for example, two finite
    field primes).  The requested value is preserved for diagnostics.
    """

    root = Path.cwd() if root is None else Path(root)
    config_path = root / DEFAULT_CONFIG_NAME

    env_value = os.environ.get(ENV_PROCESSES)
    if env_value is not None and env_value.strip() != "":
        requested = _positive_int(env_value.strip(), name=ENV_PROCESSES)
        source = "environment"
        used_config_path = None
    elif config_path.is_file():
        data = json.loads(config_path.read_text(encoding="utf-8"))
        requested = _positive_int(data.get("processes", DEFAULT_PROCESSES), name="processes")
        source = "config"
        used_config_path = str(config_path)
    else:
        requested = DEFAULT_PROCESSES
        source = "default"
        used_config_path = None

    cpu_count = os.cpu_count() or 1
    effective = min(requested, cpu_count)
    if max_useful_processes is not None:
        max_useful = _positive_int(max_useful_processes, name="max_useful_processes")
        effective = min(effective, max_useful)

    return RuntimeConfig(
        requested_processes=requested,
        effective_processes=max(1, effective),
        source=source,
        config_path=used_config_path,
    )


def format_runtime_config(config: RuntimeConfig) -> str:
    location = f", config={config.config_path}" if config.config_path else ""
    return (
        f"requested processes: {config.requested_processes}\n"
        f"effective processes: {config.effective_processes}\n"
        f"process setting source: {config.source}{location}"
    )
