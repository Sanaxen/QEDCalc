"""Prepare isolated sector-203 Kira configuration A/B diagnostics (no heavy solve here)."""
from __future__ import annotations
import argparse
import json
import shutil
from pathlib import Path
from examples.three_loop_master_basis_candidate_firefly_numerator import _context, _project, PREFERRED_NAME
from examples.three_loop_master_basis_candidate_closure import _parse_seed

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--family", default="VP05_full")
    p.add_argument("--baseline-seed", default="r8s3d0")
    p.add_argument("--sector", type=int, default=203)
    p.add_argument("--max-s", type=int, default=6)
    p.add_argument("--max-d", type=int, default=2)
    a = p.parse_args()
    a.baseline_seed = _parse_seed(a.baseline_seed)
    spec, baseline, _, _, _, _, sector, targets, seed, _, _ = _context(a)
    if (spec.family_id, baseline.tag, seed.tag, sector) != ("VP05_full", "r8s3d0", "r7s6d2", 203):
        raise ValueError("diagnostic is deliberately restricted to VP05 sector 203 r7s6d2")
    if len(targets) != 4:
        raise ValueError("expected four exact-sector targets; refusing diagnostic")
    source = _project(spec.family_id, baseline, sector, seed, multi_target=True)
    required = ["jobs.yaml", "integralfamilies.yaml", "kinematics.yaml",
                "mandatory_firefly_numerator_target.txt", PREFERRED_NAME]
    for name in required:
        if not (source / name).is_file():
            raise FileNotFoundError(source / name)
    jobs = (source / "jobs.yaml").read_text(encoding="utf-8")
    if 'run_initiate: true' not in jobs or 'run_triangular: false' not in jobs or 'run_firefly: false' not in jobs:
        raise ValueError("unexpected source jobs.yaml; refusing to copy")
    for label in ("with_preferred", "without_preferred"):
        dest = source.parent / (source.name + "_diagnostic_" + label)
        if dest.exists():
            raise FileExistsError(f"diagnostic directory already exists: {dest}")
        dest.mkdir()
        for name in required:
            shutil.copy2(source / name, dest / name)
        if label == "without_preferred":
            text = (dest / "jobs.yaml").read_text(encoding="utf-8")
            lines = [line for line in text.splitlines()
                     if "preferred_masters:" not in line]
            if len(lines) != len(text.splitlines()) - 1:
                raise ValueError("expected exactly one preferred_masters key")
            (dest / "jobs.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
            (dest / PREFERRED_NAME).unlink()
        print(f"{label}: {dest}")
    print("Diagnostic projects prepared; original Kira database and sector-202 basis unchanged.")

if __name__ == "__main__":
    main()
