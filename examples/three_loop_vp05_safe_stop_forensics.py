"""Read-only triage of remaining_safe01: preserve completed and stopped jobs.

Inspect saved logs, resource peaks, partial SYSTEM inventory, and whether
the logged bottleneck is a bitwise subsector. No equivalence or closure claim.
"""
import json
from collections import defaultdict
from examples import three_loop_vp05_remaining_safe_batch as batch
from examples import three_loop_vp05_stage2_residual_forensics as forensic

EXPECTED={204:200,205:200,228:196,229:69,230:196,231:69,237:200}

def group_stops(rows):
    groups=defaultdict(list)
    for row in rows:
        if row["state"]=="guard_stopped":
            last=row["detail"].get("last_sector")
            if not last:
                raise RuntimeError("Missing stopped sector progress")
            sec=int(last[0])
            groups[sec].append(row["sector"])
    return {str(k):sorted(v) for k,v in sorted(groups.items())}

def run():
    items=batch.scope()
    rows=[]
    for item in items:
        state,detail=batch.status(item)
        project=batch.path_for(item)
        if item["seed"]=="r8s5d3":
            if state!="completed_local_retained":
                raise RuntimeError("Saved completed job changed")
        else:
            if state!="guard_stopped" or detail.get("reason")!="ram_stop" or detail.get("kira_returncode")!=-15:
                raise RuntimeError("Saved RAM stop changed")
            if int(detail["last_sector"][0])!=EXPECTED[item["sector"]]:
                raise RuntimeError("Unexpected logged progress")
        profile=forensic.project_profile(project,expected_targets=item["targets"],
            mandatory_name=batch.base.MANDATORY,preferred_name=batch.base.PREFERRED)
        if not profile["mandatory_input_set_matches_expected"] or not profile["preferred_input_set_matches_expected"]:
            raise RuntimeError("Input list mismatch")
        row={**item,"state":state,"detail":detail,
             "resources":batch.base.read_resource_peaks(project),
             "profile":profile}
        if state=="guard_stopped":
            last=int(detail["last_sector"][0])
            row["logged_sector_is_bitwise_subsector"]=(last&item["sector"])==last
            row["logged_sector_is_not_proven_cause"]=True
            row["possible_exact_sector_seed"]=f"r{min(8,last.bit_count()+2)}s6d2"
        rows.append(row)
        print("VP05_SAFE_JOB_FORENSICS "+json.dumps(row),flush=True)
    groups=group_stops(rows)
    return {"status":"VP05_SAFE_STOP_FORENSICS_READ_ONLY",
            "completed_local":3,"guard_stopped":7,"logged_sector_groups":groups,
            "any_saved_partial_SYSTEM":any(r["profile"]["metadata"]["system_equations"]["count"] for r in rows if r["state"]=="guard_stopped"),
            "subsector_reuse_proven":False,"whole_family_closure_proven":False,
            "kira_executed":False,"files_modified":False}
if __name__=="__main__":
    print("VP05_SAFE_STOP_FORENSICS "+json.dumps(run()),flush=True)
