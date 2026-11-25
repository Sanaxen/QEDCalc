"""Guarded serial isolated boundary jobs outside the sector202 recursion.

Preserve all earlier jobs. New directories are exclusive; completed and
guard-stopped jobs are not rerun. Interrupted jobs require review.
This produces local candidate evidence, not global closure.
"""
import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from examples import three_loop_vp05_boundary_evidence_reconcile as reconcile
from examples import three_loop_vp05_stage2_sector_inventory as inv
from examples import three_loop_vp05_stage2_non202_batch as old
from examples import three_loop_vp05_stage2_continuation_batch as base
from examples.three_loop_master_basis_candidate_closure import _read_integrals
from three_loop.master_basis_api import Seed, build_family_spec, export_kira_project, find_or_infer_masters

ROOT=base.ROOT
OUTPUT=base.OUTPUT
RUN_ID="remaining_safe01"
MANIFEST="remaining_safe_manifest.json"
EXPECTED={"r8s5d3":(78,101,116),"r8s6d2":(204,205,228,229,230,231,237)}
BLOCKED={206,234}
MAX_TOTAL=43200
MAX_JOB=5400

def eligible(seed, sector):
    return seed in EXPECTED and sector in EXPECTED[seed] and sector not in BLOCKED and (sector & 202)!=202

def scope():
    evidence=reconcile.run()
    standard=inv.inspect()
    items=[]
    for seed,sectors in EXPECTED.items():
        missing=set(evidence["boundaries"][seed]["missing_local_evidence_sectors"])
        selected={s for s in missing if (s&202)!=202 and s not in BLOCKED}
        if selected!=set(sectors) or not all(eligible(seed,s) for s in selected):
            raise RuntimeError("Remaining safe sector scope changed: "+seed+" "+repr(sorted(selected)))
        s,d=(5,3) if seed=="r8s5d3" else (6,2)
        lookup={r["sector"]:r for r in standard["boundary_inventory"][seed]["sector_rows"]}
        for sec in sectors:
            targets=lookup[sec]["targets"]
            if not targets or len(set(targets))!=len(targets):
                raise RuntimeError("Invalid target inventory")
            items.append({"seed":seed,"sector":sec,"targets":targets,
                          "effective_seed":f"r{min(8,sec.bit_count()+d)}s{s}d{d}"})
    return items

def path_for(item):
    if not eligible(item["seed"],item["sector"]):
        raise ValueError("Blocked sector")
    return OUTPUT/f"vp05_{RUN_ID}_{item['seed']}_sec{item['sector']}"

def status(item):
    path=path_for(item)
    if path.is_symlink():
        raise RuntimeError("Linked job")
    if not path.exists():
        return "not_prepared",None
    saved=old.read_json(path/MANIFEST)
    if saved.get("item")!=item or set(saved.get("input_sha256",{}))!=set(base.FILES):
        raise RuntimeError("Saved manifest mismatch")
    for rel,digest in saved["input_sha256"].items():
        f=path/rel
        if f.is_symlink() or not f.is_file() or old.sha256(f)!=digest:
            raise RuntimeError("Input changed: "+str(f))
    if any(_read_integrals(path/name,base.FAMILY)!=item["targets"] for name in (base.MANDATORY,base.PREFERRED)):
        raise RuntimeError("Target list changed")
    end=path/"monitored_exit.json"
    if end.exists():
        result=old.read_json(end)
        if result.get("success") is True and result.get("reason")=="kira_exit" and result.get("kira_returncode")==0:
            source,masters,mode=find_or_infer_masters(path,base.FAMILY,mandatory_targets=item["targets"])
            return ("completed_local_retained" if set(masters)==set(item["targets"]) else "master_set_changed"),{"monitor":result,"masters":masters,"master_source":str(source),"source_mode":mode}
        if result.get("success") is False and result.get("reason") in ("ram_stop","swap_stop","time_stop") and result.get("kira_returncode") in (-15,-9):
            return "guard_stopped",result
        return "failed",result
    if any((path/f).exists() for f in ("console_output.log","monitored_kira.log","monitored_metrics.jsonl","results","tmp","sectormappings")):
        return "interrupted",None
    return "prepared",None

def prepare(item):
    path=path_for(item)
    path.mkdir(exist_ok=False)
    s,d=(5,3) if item["seed"]=="r8s5d3" else (6,2)
    r=min(8,item["sector"].bit_count()+d)
    export_kira_project(build_family_spec(base.FAMILY),path,seed=Seed(r,s,d),solver="masters",
        mandatory_file=base.MANDATORY,preferred_masters_file=base.PREFERRED,
        reduce_sectors=[item["sector"]],top_level_sectors=[item["sector"]],clean=False)
    for name in (base.MANDATORY,base.PREFERRED):
        (path/name).write_text("\n".join(item["targets"])+"\n",encoding="utf-8",newline="\n")
    shutil.copyfile(ROOT/"scripts/vp05_stage2_monitored_kira.py",path/base.MONITOR)
    with (path/MANIFEST).open("x",encoding="utf-8") as out:
        json.dump({"item":item,"input_sha256":{f:old.sha256(path/f) for f in base.FILES}},out,indent=2)
    if status(item)[0]!="prepared":
        raise RuntimeError("Preparation audit failed")

def run(mode,hours):
    items=scope()
    initial=[status(item)[0] for item in items]
    if mode=="audit":
        return {"status":"VP05_REMAINING_SAFE_AUDIT_NOT_CLOSURE","rows":[{**item,"state":status(item)[0],"detail":status(item)[1]} for item in items]}
    if os.name!="nt":
        raise RuntimeError("Windows WSL execution required")
    if not 0<hours<=12:
        raise ValueError("Hours must be positive and <=12")
    if any(s not in ("not_prepared","prepared","completed_local_retained","guard_stopped") for s in initial):
        raise RuntimeError("Unexpected existing state: "+repr(initial))
    start=time.monotonic()
    records=[]
    for item,state in zip(items,initial):
        if state in ("completed_local_retained","guard_stopped"):
            records.append({**item,"state":state,"action":"reuse_or_preserve"})
            continue
        remaining=int(hours*3600-(time.monotonic()-start))
        if remaining<30:
            break
        base._no_other_kira()
        old.wsl_resource_preflight()
        if shutil.disk_usage(OUTPUT).free<10*1024**3:
            raise RuntimeError("Disk free below 10 GiB")
        if state=="not_prepared":
            prepare(item)
        path=path_for(item)
        remaining=int(hours*3600-(time.monotonic()-start))
        if remaining<30:
            break
        print("VP05_REMAINING_JOB_BEGIN "+json.dumps(item),flush=True)
        args=["wsl.exe","--cd",str(path),"python3",base.MONITOR,
              "--max-seconds",str(min(MAX_JOB,remaining)),"--interval","5",
              "--warn-gib","4","--stop-gib","8","--ram-warn-gib","18","--ram-stop-gib","22"]
        with (path/"console_output.log").open("x",encoding="utf-8") as log:
            code=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT).returncode
        state,detail=status(item)
        row={**item,"state":state,"exit":code,"detail":detail}
        records.append(row)
        print("VP05_REMAINING_JOB_END "+json.dumps(row),flush=True)
        if not ((state=="completed_local_retained" and code==0) or (state=="guard_stopped" and code in (124,125))):
            break
    return {"status":"VP05_REMAINING_SAFE_BATCH_NOT_CLOSURE","records":records,
            "planned_jobs":len(items),"completed_local":sum(status(i)[0]=="completed_local_retained" for i in items),
            "guard_stopped":sum(status(i)[0]=="guard_stopped" for i in items),
            "family_closure_proven":False}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("run","audit"))
    parser.add_argument("--hours",type=float,default=12)
    args=parser.parse_args()
    print("VP05_REMAINING_SAFE "+json.dumps(run(args.mode,args.hours)),flush=True)
