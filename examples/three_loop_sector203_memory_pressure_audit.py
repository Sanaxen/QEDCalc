"""Inspect why the VP05 Fermat symbolic-row allocation exceeds its safety cap.

Static structural accounting only; no Fermat/Kira, no symbolic pruning.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows, modular_echelon, order

DEFAULT = Path("output/three_loop_integral_family_audit/vp05_target_symbolic_compressed.equations.json")
POINTS=((1000037,21,15),(1001003,19,53),(1001107,36,64),(1002101,47,83))


def profile(rows, schedule, cap):
    expected=[]
    row_sizes=[]
    last_use={i:i for i in range(len(rows))}
    for i,row in enumerate(rows):
        original={tuple(t["key"]) for t in row["terms"]}
        supported=set(original)
        allocated=set(original)
        for owner,pivot in schedule[i][0]:
            if owner>=i:raise ValueError("Forward reference in row schedule")
            last_use[owner]=max(last_use[owner],i)
            allocated.add(pivot)
            allocated.update(expected[owner])
            supported.update(expected[owner])
            supported.discard(pivot)
        lead=schedule[i][1]
        if lead is not None:allocated.add(lead)
        expected.append(supported)
        row_sizes.append({"row":i,"original_terms":len(original),
                          "allocated_cells":len(allocated),
                          "normalized_structural_support":len(supported),
                          "elimination_ops":len(schedule[i][0])})
    active=set()
    peak={"row":-1,"live_cells":0,"live_rows":0,"contributors":[]}
    for i in range(len(rows)):
        active.add(i)
        cells=sum(row_sizes[j]["allocated_cells"] for j in active)
        if cells>peak["live_cells"]:
            contributors=sorted(active,key=lambda j:row_sizes[j]["allocated_cells"],reverse=True)
            peak={"row":i,"live_cells":cells,"live_rows":len(active),
                  "contributors":[{"row":j,"cells":row_sizes[j]["allocated_cells"],
                                   "last_use":last_use[j]} for j in contributors]}
        active={j for j in active if last_use[j]>i}
    total=sum(x["allocated_cells"] for x in row_sizes)
    top=sorted(row_sizes,key=lambda x:x["allocated_cells"],reverse=True)[:12]
    return {"allocated_cells_total":total,"lifetime_peak_cells":peak["live_cells"],
            "peak_row":peak["row"],"peak_live_rows":peak["live_rows"],
            "above_cap_allocated":max(0,total-cap),
            "above_cap_even_if_released":max(0,peak["live_cells"]-cap),
            "top_rows_by_allocation":top,
            "peak_contributors_top_12":peak["contributors"][:12],
            "peak_contributors_total":len(peak["contributors"]),
            "notes":"Structural cells are not bytes/RSS. Peak assumes actual row release works; not verified."}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--max-array-cells",type=int,default=20000)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_memory_pressure_profile.json"))
    a=ap.parse_args()
    if a.max_array_cells<1:ap.error("Positive cell cap required")
    raw=json.loads(a.equations.read_text(encoding="utf-8-sig"))
    if raw.get("type")!="symbolic_exact_linear_combinations" or len(raw.get("rows",[]))!=166:
        ap.error("Expected exactly 166 compressed symbolic combination rows")
    rows=raw["rows"]
    profiles=[]
    reference=None
    for p,z,d in POINTS:
        schedule,pivots=modular_echelon(mod_rows(rows,p,z,d),p)
        if len(pivots)!=166:raise RuntimeError(f"Unexpected rank at {(p,z,d)}")
        info=profile(rows,schedule,a.max_array_cells)
        entry={"point":[p,z,d],"rank":len(pivots),"schedule_matches_first":reference is None or schedule==reference,**info}
        profiles.append(entry)
        if reference is None:reference=schedule
        print("VP05_MEMORY_PROFILE_POINT "+json.dumps({k:v for k,v in entry.items() if k not in ("top_rows_by_allocation","peak_contributors_top_12")}),flush=True)
    result={"input":str(a.equations),"cap_cells":a.max_array_cells,
            "all_schedules_match_first":all(x["schedule_matches_first"] for x in profiles),
            "profiles":profiles,"fermat_executed":False,"symbolic_proof":False,
            "release_dead_rows_tested":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("VP05_MEMORY_PROFILE_SUMMARY "+json.dumps({
        "points":len(profiles),"all_schedules_match_first":result["all_schedules_match_first"],
        "peak_cells":max(x["lifetime_peak_cells"] for x in profiles),
        "cap_cells":a.max_array_cells,"output":str(a.output),
        "fermat_executed":False,"proof":False}),flush=True)


if __name__=="__main__":
    main()
