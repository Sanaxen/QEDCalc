"""Prepare one isolated sector-203 target-specific seed diagnostic, without changing existing jobs."""
import argparse
import json
import re
import shutil
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.master_basis_api import parse_integral

SOURCE = ROOT / "output" / "kira_vp05_full_preferred_masters_r8s3d0_r7s6d2_sec203"
MANDATORY = "mandatory_firefly_numerator_target.txt"
SEEDS = {"r5s6d0": (5, 6, 0), "r6s6d1": (6, 6, 1), "r7s6d2": (7, 6, 2)}


def prepare(target_number: int, seed_tag: str) -> Path:
    if seed_tag not in SEEDS or target_number not in range(1, 5):
        raise ValueError("expected target index 1..4 and seed r5s6d0/r6s6d1/r7s6d2")
    required = ["jobs.yaml", "config/integralfamilies.yaml", "config/kinematics.yaml", MANDATORY]
    for name in required:
        if not (SOURCE / name).is_file():
            raise FileNotFoundError(SOURCE / name)
    targets = [s.strip() for s in (SOURCE / MANDATORY).read_text(encoding="utf-8").splitlines() if s.strip()]
    if len(targets) != 4:
        raise ValueError(f"expected 4 mandatory integrals; found {len(targets)}")
    if len(set(targets)) != 4:
        raise ValueError("duplicate mandatory integrals")
    for target in targets:
        family, powers = parse_integral(target)
        sector = sum(1 << i for i, p in enumerate(powers) if p > 0)
        if family != "VP05_full" or sector != 203:
            raise ValueError(f"unexpected target: {target}")
    target = targets[target_number - 1]
    _, powers = parse_integral(target)
    r, s, d = SEEDS[seed_tag]
    positive_sum = sum(p for p in powers if p > 0)
    negative_sum = -sum(p for p in powers if p < 0)
    if positive_sum > r or negative_sum > s or positive_sum - 5 > d:
        raise ValueError(f"target {target_number} outside {seed_tag} envelope")
    destination = SOURCE.parent / (SOURCE.name + f"_single_t{target_number}_{seed_tag}")
    if destination.exists():
        raise FileExistsError(f"refusing reuse/overwrite of isolated project: {destination}")
    jobs = (SOURCE / "jobs.yaml").read_text(encoding="utf-8")
    if "run_initiate: true" not in jobs or "run_triangular: false" not in jobs:
        raise ValueError("source job is not an initiate-only reduction")
    pattern = r"(sectors:\s*\[203\],\s*r:\s*)7(,\s*s:\s*)6(,\s*d:\s*)2"
    jobs, hits = re.subn(pattern, lambda m: m.group(1)+str(r)+m.group(2)+str(s)+m.group(3)+str(d), jobs)
    if hits != 1:
        raise ValueError(f"expected one sector-203 seed configuration; found {hits}")
    jobs = "\n".join(line for line in jobs.splitlines() if "preferred_masters:" not in line) + "\n"
    destination.mkdir(parents=True)
    for name in required:
        out = destination / name
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / name, out)
    (destination / "jobs.yaml").write_text(jobs, encoding="utf-8", newline="\n")
    (destination / MANDATORY).write_text(target+"\n", encoding="utf-8", newline="\n")
    (destination / "target_diagnostic_manifest.json").write_text(
        json.dumps({"family":"VP05_full","sector":203,"target_index":target_number,
          "target":target,"seed":seed_tag,"original_target_count":4,
          "mode":"single-mandatory-initiate-only-no-preferred",
          "scope":"diagnostic; not proof of four-target closure"}, indent=2)+"\n", encoding="utf-8")
    print(f"TARGET={target}\nSEED={seed_tag}\nPROJECT={destination}")
    return destination


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("target", type=int)
    p.add_argument("seed", choices=SEEDS)
    a = p.parse_args()
    prepare(a.target, a.seed)
