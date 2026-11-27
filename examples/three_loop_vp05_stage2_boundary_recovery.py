"""Recover archived isolated local retention, not full boundary closure."""
import time
from pathlib import Path
from collections import Counter
from examples import three_loop_vp05_stage2_coverage_inventory as cov
from examples import three_loop_vp05_boundary_evidence_reconcile as rec
from examples import three_loop_vp05_remaining_safe_batch as safe

gap=cov.gap;n=cov.n;v=cov.v;c=cov.c
ROOT=n.BASE/"output"/"vp05_stage2_boundary_recovery22"
SOURCE=cov.ROOT/"report_1795766027485591700.json"
SHA="c93e9ea3ebb01f7ed86724ebaefeb31adc3578e3f973529499233413eee83ff4"

def merge(rows,isolated):
    result=[]
    for row in rows:
        item=dict(row)
        sec=row["sector"]
        recovered=isolated.get((row["seed"],sec))
        item["isolated_evidence"]=recovered
        item["local_evidence_present"]=bool(recovered and recovered["state"]=="completed_local_retained") or row["classification"] in (
            "saved_local_pass_inventory_match","local_inventory_only","restricted_equivalent_review")
        item["full_seed_closure_proven"]=False
        result.append(item)
    return result

def inspect():
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Coverage report SHA")
    prior=gap.read(SOURCE)
    if prior["status"]!="VP05_STAGE2_COVERAGE_INVENTORY_NOT_CLOSURE" or prior["target_count"]!=63 or prior["boundary_count"]!=78:raise RuntimeError("Coverage scope")
    pins={Path(k):d for k,d in prior["inputs"].items()}
    pins[SOURCE]=SHA
    if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Prior input SHA")
    # Reuse original read-only validators, including archived input hashes,
    # monitor exit status and actual master lists. No calculation entrypoint.
    baseline=rec.run()
    _,nextrows=rec.follow.verified_scope()
    first=rec.follow.base.first_pilot.audit("first01")
    medium=rec.follow.base.previous_batch.report_all("medium01")
    non=rec.non.audit("no202a")
    remaining=safe.run("audit",12)
    isolated={}
    def add(seed,sector,state,source,detail):
        key=(seed,sector)
        item={"state":state,"source":source,"detail":detail}
        if key in isolated:
            old=isolated[key]
            if old["state"]=="completed_local_retained" and state!="completed_local_retained":raise RuntimeError("Conflicting isolated evidence")
            if old["state"]==state:return
        isolated[key]=item
    if first["status"]!="VP05_PILOT_SECTOR73_MASTER_RETAINED_PENDING_CROSS_SECTOR_REVIEW":raise RuntimeError("First pilot")
    add("r8s5d3",73,"completed_local_retained","first01",first)
    for row in medium["sector_rows"]:
        if row["state"]!="completed_local_retained" or row.get("candidate_retained") is not True:raise RuntimeError("Medium pilot")
        add("r8s5d3",row["sector"],row["state"],"medium01",row)
    for row in nextrows:add("r8s5d3",row["sector"],row["state"],"next01",row)
    for row in non["sector_rows"]:
        add("r8s5d3",row["sector"],row["state"],"no202a",row)
    for row in remaining["rows"]:
        add(row["seed"],row["sector"],row["state"],"remaining_safe01",row)
    rows=merge(prior["boundaries"],isolated)
    counts={}
    for seed in gap.SEEDS:
        subset=[x for x in rows if x["seed"]==seed]
        if len(subset)!=26:raise RuntimeError("Boundary scope")
        counts[seed]={"local_evidence":sum(x["local_evidence_present"] for x in subset),
                      "recovered":[x["sector"] for x in subset if x["local_evidence_present"] and x["classification"]=="missing_or_failed_local_evidence"],
                      "missing":[x["sector"] for x in subset if not x["local_evidence_present"]]}
        v.log("VP05_BOUNDARY_RECOVERY_SEED",seed=seed,**counts[seed])
    if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
    return {"status":"VP05_BOUNDARY_RECOVERY_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},
            "counts":counts,"boundaries":rows,"earlier_reconciliation":baseline,
            "local_evidence_total":sum(x["local_evidence"] for x in counts.values()),
            "full_closure_proven":False,"kira_executed":False,"registry_changed":False}

def main():
    payload=inspect()
    ROOT.mkdir(exist_ok=True)
    dest=ROOT/f"report_{time.time_ns()}.json";digest=c.save(dest,payload)
    v.log("VP05_BOUNDARY_RECOVERY_NOT_CLOSURE",counts=payload["counts"],local_evidence_total=payload["local_evidence_total"],
          report=dest.name,sha256=digest,inputs_unchanged=True,full_closure_proven=False)

if __name__=="__main__":main()
