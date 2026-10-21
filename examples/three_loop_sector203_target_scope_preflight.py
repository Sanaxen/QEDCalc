"""VP05 target-only dependency/resource audit; finite-field planning, NOT proof.

Uses compressed exact-combination equations. Does not launch Fermat or Kira.
Keeps the original 166-row matrix order and pivot scheme. A modularly-zero
factor can conceal a nonzero rational function, so the dependency plan is
only a sampled scheduling hypothesis, never an exact symbolic pruning license.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows, modular_echelon, order
from examples.three_loop_sector203_target_rowspace_audit import eliminate, residue

DEFAULT = Path("output/three_loop_integral_family_audit/vp05_target_symbolic_compressed.equations.json")
POINTS = ((1000037,21,15),(1001003,19,53),(1001107,36,64),(1002101,47,83))
TARGET = {(10,203):"z",(6,203):"-2",(5,201):"2"}


def target_trace(rows, pivots, p, z, d):
    vec = {key:residue(expr,p,z,d) for key,expr in TARGET.items()}
    used = []
    while vec:
        key = min(vec,key=order)
        if key not in pivots:
            return used,vec
        owner,basis = pivots[key]
        factor = vec[key]
        used.append((owner,key))
        for col,value in basis.items():
            new = (vec.get(col,0)-factor*value)%p
            if new: vec[col]=new
            else: vec.pop(col,None)
    return used,vec


def dependency_closure(schedule, initial):
    needed=set(initial)
    pending=list(needed)
    while pending:
        row=pending.pop()
        for owner,_ in schedule[row][0]:
            if owner not in needed:
                needed.add(owner)
                pending.append(owner)
    return needed


def estimates(rows,schedule,needed):
    """Structural support growth estimate, not polynomial/memory upper bound."""
    supports={}
    cells=0
    operations=0
    for i in sorted(needed):
        support={tuple(t["key"]) for t in rows[i]["terms"]}
        for owner,pivot in schedule[i][0]:
            if owner not in needed:
                raise RuntimeError("Owner outside dependency closure")
            operations+=1
            support.update(supports[owner])
            support.discard(pivot)
        lead=schedule[i][1]
        if lead is not None:
            support.add(lead)
        supports[i]=support
        cells+=len(support)
    last_use={i:i for i in needed}
    for i in needed:
        for owner,_ in schedule[i][0]:
            last_use[owner]=max(last_use[owner],i)
    active=set()
    peak=0
    peak_row=None
    for i in range(len(rows)):
        if i in needed: active.add(i)
        size=sum(len(supports[j]) for j in active)
        if size>peak:
            peak=size
            peak_row=i
        active={j for j in active if last_use[j]>i}
    return {"dependency_rows":len(needed),
            "dependency_operations":operations,
            "estimated_array_cells_allocated":cells,
            "estimated_peak_live_cells_if_released":peak,
            "peak_row_zero_based":peak_row,
            "estimated_target_output_columns":len(set().union(*(supports[i] for i in needed))) if needed else 0,
            "actual_fermat_memory_measured":False}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--max-array-cells",type=int,default=20000)
    ap.add_argument("--output",type=Path,help="Optional JSON audit report")
    args=ap.parse_args()
    data=json.loads(args.equations.read_text(encoding="utf-8-sig"))
    if data.get("type")!="symbolic_exact_linear_combinations":
        ap.error("Expected symbolic exact-combination JSON")
    rows=data["rows"]
    if len(rows)!=166: ap.error("Expected 166 compressed rows")
    columns={tuple(t["key"]) for row in rows for t in row["terms"]}
    if set(TARGET)-columns: ap.error("Missing target column keys")
    results=[]
    reference_schedule=None
    reference_pivots=None
    for p,z,d in POINTS:
        sampled=mod_rows(rows,p,z,d)
        schedule,pivots=modular_echelon(sampled,p)
        trace,remainder=target_trace(sampled,pivots,p,z,d)
        check=eliminate(sampled,{k:residue(v,p,z,d) for k,v in TARGET.items()},p)
        if not check["certificate_original_equation_replay_verified"] or remainder:
            raise RuntimeError("Target modular replay failed")
        needed=dependency_closure(schedule,(owner for owner,_ in trace))
        scope=estimates(rows,schedule,needed)
        result={"point":[p,z,d],"rank":len(pivots),
                "target_steps":len(trace),"target_owners":len({i for i,_ in trace}),
                "target_in_rowspace":not remainder,
                "replay_verified":check["certificate_original_equation_replay_verified"],
                **scope,"within_allocated_cell_cap":scope["estimated_array_cells_allocated"]<=args.max_array_cells,
                "within_lifetime_cell_cap":scope["estimated_peak_live_cells_if_released"]<=args.max_array_cells}
        results.append(result)
        print("VP05_TARGET_SCOPE_POINT "+json.dumps(result),flush=True)
        if reference_schedule is None:
            reference_schedule= schedule
            reference_pivots=[key for _,key in trace]
        else:
            result["same_schedule_as_first"]=(schedule==reference_schedule)
            result["same_target_pivots_as_first"]=([key for _,key in trace]==reference_pivots)
    report={"source":str(args.equations),"rows":166,"columns":len(columns),
            "points":results,
            "all_replayed":all(v["replay_verified"] for v in results),
            "max_dependency_rows":max(v["dependency_rows"] for v in results),
            "max_allocated_cells_estimate":max(v["estimated_array_cells_allocated"] for v in results),
            "all_schedules_match_first":all(v.get("same_schedule_as_first",True) for v in results),
            "symbolic_pruning_authorized":False,
            "fermat_executed":False,"proof":False,
            "warning":"Only modular planning; symbolic zeros, resource use, and alias identities remain unverified."}
    print("VP05_TARGET_SCOPE_SUMMARY "+json.dumps({k:v for k,v in report.items() if k!="points"}),flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
