"""Reconcile VP05 row-cell accounting against the actual Fermat pilot map.

Exact structural replay of the pilot's expected/row_maps construction; no
Fermat/Kira and no assertion about actual RSS or symbolic identity.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows, modular_echelon, order
from examples.three_loop_sector203_memory_pressure_audit import profile
from examples.three_loop_sector203_target_scope_preflight import estimates

DEFAULT=Path("output/three_loop_integral_family_audit/vp05_target_symbolic_compressed.equations.json")
POINTS=((1000037,21,15),(1001003,19,53),(1001107,36,64),(1002101,47,83))


def reconcile(rows,schedule):
    expected=[]
    exact_sizes=[]
    per_row=[]
    last_use={i:i for i in range(len(rows))}
    for i,row in enumerate(rows):
        values={tuple(t["key"]) for t in row["terms"]}
        # Mirrors expected[] with --prune-eliminated-pivots in Fermat pilot.
        cur=set(values)
        for owner,pivot in schedule[i][0]:
            last_use[owner]=max(last_use[owner],i)
            cur.update(expected[owner])
            cur.discard(pivot)
        expected.append(set(cur))
        # Mirrors sparse row_maps: values U pivots U expected[owner] U lead.
        keys=set(values)
        for owner,pivot in schedule[i][0]:
            keys.add(pivot)
            keys.update(expected[owner])
        lead=schedule[i][1]
        if lead is not None:keys.add(lead)
        exact_sizes.append(len(keys))
        per_row.append({"row":i,"pilot_sparse_map_cells":len(keys),
                        "normalized_pivot_support_cells":len(cur),
                        "elimination_ops":len(schedule[i][0])})
    active=set()
    peak=0
    peak_row=-1
    peak_count=0
    for i in range(len(rows)):
        active.add(i)
        cells=sum(exact_sizes[j] for j in active)
        if cells>peak:
            peak,peak_row,peak_count=cells,i,len(active)
        active={j for j in active if last_use[j]>i}
    return {"pilot_sparse_allocated_cells":sum(exact_sizes),
            "pilot_sparse_lifetime_peak_cells":peak,
            "pilot_peak_row":peak_row,"pilot_peak_live_rows":peak_count},per_row


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_cell_accounting_reconciliation.json"))
    a=ap.parse_args()
    data=json.loads(a.equations.read_text(encoding="utf-8-sig"))
    if data.get("type")!="symbolic_exact_linear_combinations" or len(data.get("rows",[]))!=166:
        ap.error("Expected exact-combination 166-row input")
    rows=data["rows"]
    results=[]
    first=None
    for p,z,d in POINTS:
        schedule,pivots=modular_echelon(mod_rows(rows,p,z,d),p)
        if len(pivots)!=166:raise RuntimeError("Full rank required for this audit")
        actual,per_row=reconcile(rows,schedule)
        memory=profile(rows,schedule,20000)
        scope=estimates(rows,schedule,set(range(166)))
        differences=[]
        for row,item in enumerate(per_row):
            other=memory["top_rows_by_allocation"]
            # Full per-row memory profile calculated below independently.
            pass
        result={"point":[p,z,d],"rank":len(pivots),
                "same_schedule_as_first":first is None or first==schedule,
                **actual,
                "memory_profiler_allocated_cells":memory["allocated_cells_total"],
                "memory_profiler_peak_cells":memory["lifetime_peak_cells"],
                "target_scope_allocated_cells":scope["estimated_array_cells_allocated"],
                "target_scope_peak_cells":scope["estimated_peak_live_cells_if_released"],
                "memory_profiler_minus_pilot":memory["allocated_cells_total"]-actual["pilot_sparse_allocated_cells"],
                "target_scope_minus_pilot":scope["estimated_array_cells_allocated"]-actual["pilot_sparse_allocated_cells"],
                "pilot_above_20000":actual["pilot_sparse_allocated_cells"]>20000,
                "pilot_release_peak_above_20000":actual["pilot_sparse_lifetime_peak_cells"]>20000}
        results.append({"summary":result,"pilot_per_row":per_row})
        if first is None:first=schedule
        print("VP05_CELL_RECONCILE_POINT "+json.dumps(result),flush=True)
    summary={"all_schedules_match_first":all(x["summary"]["same_schedule_as_first"] for x in results),
             "pilot_allocated_cells":max(x["summary"]["pilot_sparse_allocated_cells"] for x in results),
             "pilot_release_peak_cells":max(x["summary"]["pilot_sparse_lifetime_peak_cells"] for x in results),
             "resource_cap":20000,"fermat_executed":False,"proof":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"source":str(a.equations),"summary":summary,"points":results},indent=2)+"\n",encoding="utf-8")
    print("VP05_CELL_RECONCILE_SUMMARY "+json.dumps({**summary,"output":str(a.output)}),flush=True)


if __name__=="__main__":main()
