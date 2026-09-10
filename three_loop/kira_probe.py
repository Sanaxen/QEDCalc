"""Safe initiate-only scaling probes for the Q01 Kira backend."""
from __future__ import annotations

from pathlib import Path

from three_loop.kira_backend import (
    KiraSeedLimits,
    export_q01_kira_project,
    q01_kira_manifest,
)


def render_initiate_only_jobs(limits: KiraSeedLimits) -> str:
    """Render a Kira job that stops after equation selection/master discovery.

    This follows Kira's recommended large-reduction workflow: inspect the
    master basis after run_initiate before committing memory/time to the
    triangular and back-substitution phases.
    """
    return f"""jobs:
  - reduce_sectors:
      reduce:
        - {{topologies: [Q01_4line], sectors: [15], r: {limits.r}, s: {limits.s}, d: {limits.d}}}
      select_integrals:
        select_mandatory_recursively:
          - {{topologies: [Q01_4line], sectors: [15], r: {limits.r}, s: {limits.s}, d: {limits.d}}}
      run_symmetries: true
      run_initiate: true
      run_triangular: false
      run_back_substitution: false
"""


def export_q01_kira_initiate_probe(
    root: str | Path,
    *,
    limits: KiraSeedLimits,
) -> Path:
    root = export_q01_kira_project(root, limits=limits, back_substitution=False)
    (root / "jobs.yaml").write_text(
        render_initiate_only_jobs(limits), encoding="utf-8", newline="\n"
    )
    # Keep the regular manifest and add one explicit mode marker without
    # changing the stable exporter schema.
    manifest = q01_kira_manifest(limits)
    manifest["run_mode"] = "initiate_only_scaling_probe"
    import json

    (root / "qedcalc_kira_probe_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8", newline="\n"
    )
    return root
