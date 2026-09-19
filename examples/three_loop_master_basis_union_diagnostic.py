"""Diagnose a failed mandatory-union Kira project without rerunning it."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.master_basis_api import build_family_spec, parse_integral, integral_complexity
from examples.three_loop_master_basis_union_reduction import (
    _default_target_path,
    _parse_seed,
    _read_targets,
    _target_sectors,
    _maximal_sectors,
    project_path,
)

def _extract_int_list(text: str, key: str) -> list[int]:
    m = re.search(rf"{re.escape(key)}:\s*\[([^\]]*)\]", text)
    if not m:
        return []
    out=[]
    for x in m.group(1).split(","):
        x=x.strip()
        if x:
            try: out.append(int(x))
            except ValueError: pass
    return out

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--baseline-seed", type=_parse_seed)
    p.add_argument("--solver", default="firefly")
    args=p.parse_args()

    spec=build_family_spec(args.family)
    base=args.baseline_seed or spec.baseline_seed
    targets_path=_default_target_path(spec.family_id,args.solver,base)
    targets=_read_targets(targets_path,spec.family_id)
    sectors=_target_sectors(targets)
    maximal=_maximal_sectors([spec.top_sector,*sectors])
    project=project_path(spec.family_id,args.solver,base)
    jobs=project/"jobs.yaml"
    fam=project/"config"/"integralfamilies.yaml"
    mandatory=project/"mandatory_union_targets.txt"

    print("QEDCalc mandatory-union diagnostic")
    print("family:", spec.family_id)
    print("baseline:", base.tag)
    print("physical top sector:", spec.top_sector)
    print("target count:", len(targets))
    print("unique target sectors:", sectors)
    print("expected maximal top-level sectors:", maximal)
    print("project:", project)
    print("jobs exists:", jobs.exists())
    print("family yaml exists:", fam.exists())
    print("mandatory copy exists:", mandatory.exists())

    if jobs.exists():
        jt=jobs.read_text(encoding="utf-8",errors="replace")
        print("jobs reduce sectors:", _extract_int_list(jt,"sectors"))
        print("--- jobs.yaml ---")
        print(jt)
    if fam.exists():
        ft=fam.read_text(encoding="utf-8",errors="replace")
        print("family top_level_sectors:", _extract_int_list(ft,"top_level_sectors"))
        print("--- integralfamilies.yaml ---")
        print(ft)
    if mandatory.exists():
        mt=_read_targets(mandatory,spec.family_id)
        print("prepared target count:", len(mt))
        print("source/prepared identical:", mt==targets)

    bad_top=[]
    for t in targets:
        _,idx=parse_integral(t)
        sec=sum(1<<i for i,a in enumerate(idx) if int(a)>0)
        comp=integral_complexity(idx)
        covered=any((sec & top)==sec for top in maximal)
        if not covered:
            bad_top.append((t,sec,comp.tag))
    print("targets not covered by expected top-level sectors:", len(bad_top))
    for row in bad_top[:20]:
        print("  ",row)

    print("first target samples:")
    for t in targets[:20]:
        _,idx=parse_integral(t)
        sec=sum(1<<i for i,a in enumerate(idx) if int(a)>0)
        comp=integral_complexity(idx)
        print(f"  sector={sec:4d} complexity={comp.tag:8s} {t}")

    logs=sorted(project.glob("*.log"))
    print("logs:", [str(x) for x in logs])
    for log in logs[-3:]:
        lines=log.read_text(encoding="utf-8",errors="replace").splitlines()
        print(f"--- tail {log.name} ---")
        for line in lines[-120:]:
            print(line)

if __name__=="__main__":
    main()
