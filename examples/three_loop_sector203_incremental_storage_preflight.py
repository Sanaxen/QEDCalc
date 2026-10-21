"""Audit smaller row storage using per-operation pivot scratch cells.

No Fermat/Kira. This is a structural proposal, NOT an executable proof.
A row's intermediate pivot coefficients are needed only until that pivot is
eliminated. The original sparse pilot permanently reserves every such key.
This audit computes a safe per-row upper bound for incremental mutable storage:
initial support + normalized destination support + maximum simultaneous pivot
scratch (one factor). Does not assume modular zeros are symbolic zeros.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows,modular_echelon
from examples.three_loop_sector203_cell_accounting_reconciliation import reconcile,POINTS,DEFAULT

def estimate(rows,schedule):
    normalized=[]
    fixed_sizes=[]
    scratch_sizes=[]
    pilot_sizes=[]
    last={i:i for i in range(len(rows))}
    for i,row in enumerate(rows):
        originals={tuple(t["key"]) for t in row["terms"]}
        cur=set(originals)
        transient=set()
        reserved=set(originals)
        for owner,pivot in schedule[i][0]:
            last[owner]=max(last[owner],i)
            reserved.add(pivot)
            reserved.update(normalized[owner])
            # Only one pivot factor is needed at once, but normalized rows
            # may still contain other, not-yet-removed pivots.
            transient.add(pivot)
            cur.update(normalized[owner])
            cur.discard(pivot)
        lead=schedule[i][1]
        if lead is not None:reserved.add(lead)
        normalized.append(cur.copy())
        fixed_sizes.append(len(cur|originals))
        scratch_sizes.append(len(transient-(cur|originals)))
        pilot_sizes.append(len(reserved))
    def peak(sizes):
        live=set();mx=0;at=-1
        for i in range(len(rows)):
            live.add(i)
            val=sum(sizes[j] for j in live)
            if val>mx:mx,at=val,i
            live={j for j in live if last[j]>i}
        return mx,at
    # Candidate persistent keys = union of input and post-elimination support.
    # Scratch is a separate scalar factor and is not a persistent row cell.
    fixed_peak,fixed_at=peak(fixed_sizes)
    pilot_peak,pilot_at=peak(pilot_sizes)
    if sum(pilot_sizes)!=reconcile(rows,schedule)[0]["pilot_sparse_allocated_cells"]:
        raise RuntimeError("Pilot count mismatch")
    return {"pilot_total":sum(pilot_sizes),"pilot_peak":pilot_peak,
            "persistent_candidate_total":sum(fixed_sizes),
            "persistent_candidate_peak":fixed_peak,
            "potential_allocated_cell_reduction":sum(pilot_sizes)-sum(fixed_sizes),
            "potential_peak_cell_reduction":pilot_peak-fixed_peak,
            "candidate_within_20000":fixed_peak<=20000,
            "candidate_peak_at_row":fixed_at,
            "pilot_peak_at_row":pilot_at,
            "transient_pivot_key_count_total":sum(scratch_sizes),
            "note":"Candidate uses a scalar scratch per pivot but is NOT yet implemented or proven safe. Static support only."}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_incremental_storage_preflight.json"))
    a=ap.parse_args()
    data=json.loads(a.equations.read_text(encoding="utf-8-sig"))
    if data.get("type")!="symbolic_exact_linear_combinations" or len(data.get("rows",[]))!=166:
        ap.error("Expected compressed 166-row symbolic equations")
    rows=data["rows"];first=None;reports=[]
    for p,z,d in POINTS:
        schedule,pivots=modular_echelon(mod_rows(rows,p,z,d),p)
        if len(pivots)!=166:raise RuntimeError("Full rank expected")
        metrics=estimate(rows,schedule)
        report={"point":[p,z,d],"same_schedule_as_first":first is None or schedule==first,**metrics}
        if first is None:first=schedule
        reports.append(report)
        print("VP05_INCREMENTAL_STORAGE_POINT "+json.dumps(report),flush=True)
    summary={"same_schedule":all(x["same_schedule_as_first"] for x in reports),
             "pilot_peak":max(x["pilot_peak"] for x in reports),
             "candidate_peak":max(x["persistent_candidate_peak"] for x in reports),
             "candidate_within_20000":all(x["candidate_within_20000"] for x in reports),
             "fermat_executed":False,"proof":False,"implementation_ready":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"summary":summary,"points":reports},indent=2)+"\n",encoding="utf-8")
    print("VP05_INCREMENTAL_STORAGE_SUMMARY "+json.dumps(summary),flush=True)

if __name__=="__main__":main()
