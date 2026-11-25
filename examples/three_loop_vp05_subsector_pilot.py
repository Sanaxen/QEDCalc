"""Isolated three-subsector generation pilot with guarded WSL execution.

Use the previously saved truncate_sp syntax only if it is actually present
and unambiguous in the old VP05 job. No scope equivalence is asserted.
"""
import argparse,json,os,re,shutil,subprocess,time
from examples import three_loop_vp05_remaining_safe_batch as old
from examples import three_loop_vp05_sector202_quotient_sensitivity as q
from three_loop.master_basis_api import Seed,build_family_spec,export_kira_project

SECTORS=(69,196,200)
BASE=old.base
FILES=("jobs.yaml","config/integralfamilies.yaml","config/kinematics.yaml","qedcalc_master_basis_manifest.json",BASE.MONITOR)
MANIFEST="subsector_pilot_manifest.json"

def truncate_setting(raw):
    hits=re.findall(r"(?m)^([ \t]*)truncate_sp\s*:\s*([^\r\n#]+)",raw)
    if len(hits)!=1 or not re.fullmatch(r"\s*2\s*",hits[0][1]):
        raise RuntimeError("Old truncate_sp setting not uniquely confirmed as scalar 2")
    return hits[0][0]+"truncate_sp: 2"

def source_setting():
    # The original experiment is read-only; never assume its YAML schema.
    return truncate_setting((q.P/"jobs.yaml").read_text(encoding="utf-8"))

def folder(sec,variant):
    if sec not in SECTORS or variant not in ("plain","trunc2"):
        raise ValueError("Invalid pilot")
    return old.OUTPUT/f"vp05_subsector_pilot01_sec{sec}_{variant}"

def prepare(sec,variant,setting):
    dest=folder(sec,variant)
    dest.mkdir(exist_ok=False)
    spec=build_family_spec(BASE.FAMILY)
    export_kira_project(spec,dest,seed=Seed(5,6,2),solver="masters",
        reduce_sectors=[sec],top_level_sectors=[sec],clean=False)
    job=dest/"jobs.yaml"
    raw=job.read_text(encoding="utf-8")
    # Select the full recursive seed for this top sector, not the family top.
    raw,n=re.subn(r"(select_mandatory_recursively:\s*\n\s*-\s*\{topologies: \[VP05_full\], sectors: )\[\d+\]",lambda m:m[1]+f"[{sec}]",raw)
    if n!=1:
        raise RuntimeError("Unexpected recursive selection YAML")
    if variant=="trunc2":
        if setting is None or len(setting)-len(setting.lstrip())!=6:
            raise RuntimeError("Unverified truncate_sp nesting; refuse")
        raw=raw.replace("      run_symmetries: true",setting+"\n      run_symmetries: true",1)
    job.write_text(raw,encoding="utf-8",newline="\n")
    shutil.copyfile(old.ROOT/"scripts/vp05_stage2_monitored_kira.py",dest/BASE.MONITOR)
    with (dest/MANIFEST).open("x",encoding="utf-8") as f:
        json.dump({"sector":sec,"variant":variant,"seed":"r5s6d2",
                   "hashes":{p:old.old.sha256(dest/p) for p in FILES}},f,indent=2)

def inspect(sec,variant):
    dest=folder(sec,variant)
    if dest.is_symlink():raise RuntimeError("Linked project")
    if not dest.exists():return {"state":"new"}
    m=old.old.read_json(dest/MANIFEST)
    if (m.get("sector"),m.get("variant"),m.get("seed"))!=(sec,variant,"r5s6d2") or set(m.get("hashes",{}))!=set(FILES):
        raise RuntimeError("Manifest mismatch")
    for p,h in m["hashes"].items():
        if (dest/p).is_symlink() or old.old.sha256(dest/p)!=h:raise RuntimeError("Input changed")
    end=dest/"monitored_exit.json"
    if end.exists():
        result=old.old.read_json(end)
        state="completed" if result.get("success") is True and result.get("reason")=="kira_exit" and result.get("kira_returncode")==0 else "guard_stopped" if result.get("reason") in ("ram_stop","swap_stop","time_stop") and result.get("success") is False else "failed"
        systems=sorted((dest/"tmp"/BASE.FAMILY).glob("SYSTEM_*.gz"))
        return {"state":state,"monitor":result,"resources":BASE.read_resource_peaks(dest),
                "SYSTEM_files":[{"name":p.name,"bytes":p.stat().st_size} for p in systems],
                "masters_file_exists":(dest/"results"/BASE.FAMILY/"masters").is_file()}
    if any((dest/p).exists() for p in ("console_output.log","results","tmp","sectormappings","monitored_kira.log","monitored_metrics.jsonl")):
        return {"state":"interrupted"}
    return {"state":"prepared"}

def run(mode,hours):
    # Validate the ten original jobs once; no original run is restarted.
    for item in old.scope():
        state,detail=old.status(item)
        if item["seed"]=="r8s5d3":
            if state!="completed_local_retained":raise RuntimeError("Prior success changed")
        elif state!="guard_stopped" or detail.get("reason")!="ram_stop":
            raise RuntimeError("Prior RAM stop changed")
    try:
        setting=source_setting()
        if len(setting)-len(setting.lstrip())!=6:raise RuntimeError("Old setting nesting differs")
        setting_error=None
    except (OSError,RuntimeError) as exc:
        setting=None
        setting_error=str(exc)
    start=time.monotonic()
    rows=[]
    for sec in SECTORS:
        for variant in ("plain","trunc2"):
            before=inspect(sec,variant)
            if mode=="run" and before["state"] in ("new","prepared"):
                # Only try truncated generation after plain guard stop.
                if variant=="trunc2" and (setting is None or inspect(sec,"plain")["state"]!="guard_stopped"):
                    rows.append({"sector":sec,"variant":variant,"state":"skipped"});continue
                remaining=int(hours*3600-(time.monotonic()-start))
                if remaining<30:break
                BASE._no_other_kira()
                old.old.wsl_resource_preflight()
                if shutil.disk_usage(old.OUTPUT).free<10*1024**3:raise RuntimeError("Disk free below 10 GiB")
                if before["state"]=="new":prepare(sec,variant,setting)
                dest=folder(sec,variant)
                remaining=int(hours*3600-(time.monotonic()-start))
                if remaining<30:break
                cmd=["wsl.exe","--cd",str(dest),"python3",BASE.MONITOR,
                     "--max-seconds",str(min(5400,remaining)),"--interval","5","--warn-gib","4","--stop-gib","8","--ram-warn-gib","18","--ram-stop-gib","22"]
                print("VP05_SUBSECTOR_BEGIN "+json.dumps({"sector":sec,"variant":variant}),flush=True)
                with (dest/"console_output.log").open("x",encoding="utf-8") as log:
                    code=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode
                before=inspect(sec,variant)
                if not ((code==0 and before["state"]=="completed") or (code in (124,125) and before["state"]=="guard_stopped")):
                    raise RuntimeError("Unexpected pilot exit; preserve job")
            row={"sector":sec,"variant":variant,**before}
            rows.append(row)
            print("VP05_SUBSECTOR_JOB "+json.dumps(row),flush=True)
            if mode=="run" and before["state"] in ("failed","interrupted"):raise RuntimeError("Review existing job before continuing")
    return {"status":"VP05_SUBSECTOR_PILOT_NOT_CLOSURE","rows":rows,"truncate_setting":setting,
            "truncate_setting_blocker":setting_error,"parent_scope_equivalence_proven":False,"family_closure_proven":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("run","audit"))
    p.add_argument("--hours",type=float,default=12)
    a=p.parse_args()
    if a.mode=="run" and (os.name!="nt" or not 0<a.hours<=12):p.error("Windows and 0<hours<=12 required")
    print("VP05_SUBSECTOR_PILOT "+json.dumps(run(a.mode,a.hours)),flush=True)
