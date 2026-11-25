"""Kira3 documented truncate_sp pilot, explicit scalar/dot targets.

Not a full s6 closure test. Keep all prior plain projects immutable.
"""
import argparse,json,os,shutil,subprocess,time
from examples import three_loop_vp05_subsector_pilot as prior
from three_loop.master_basis_api import Seed,build_family_spec,export_kira_project,parse_masters_final
from examples.three_loop_master_basis_candidate_closure import _read_integrals

BASE=prior.BASE
OLD=prior.old
SECTORS=prior.SECTORS
LEVELS=(2,0,-2)
MANIFEST="truncate_pilot_manifest.json"
FILES=prior.FILES+(BASE.MANDATORY,)

def targets(sec):
    if sec not in SECTORS:raise ValueError("Invalid sector")
    pos=[i for i in range(12) if sec&(1<<i)]
    a=[int(i in pos) for i in range(12)]
    # Scalar and all one/two dots on positive lines; no claim of numerator coverage.
    rows=[a]
    for i in pos:
        b=a.copy();b[i]+=1;rows.append(b)
    for i in pos:
        for j in pos:
            if j<i:continue
            b=a.copy();b[i]+=1;b[j]+=1;rows.append(b)
    return ["VP05_full["+",".join(map(str,b))+"]" for b in rows]

def setting(raw,level):
    if level not in LEVELS or "truncate_sp:" in raw or raw.count("      select_integrals:")!=1:
        raise ValueError("Unexpected job schema")
    return raw.replace("      select_integrals:",
        "      truncate_sp:\n        - {topologies: [VP05_full], l: "+str(level)+"}\n      select_integrals:",1)

def folder(sec,level):
    if sec not in SECTORS or level not in LEVELS:raise ValueError("Invalid pilot")
    return OLD.OUTPUT/f"vp05_subsector_truncate02_sec{sec}_l{level}"

def prepare(sec,level):
    dest=folder(sec,level)
    dest.mkdir(exist_ok=False)
    export_kira_project(build_family_spec(BASE.FAMILY),dest,seed=Seed(5,6,2),solver="masters",
        mandatory_file=BASE.MANDATORY,reduce_sectors=[sec],top_level_sectors=[sec],clean=False)
    job=dest/"jobs.yaml"
    job.write_text(setting(job.read_text(encoding="utf-8"),level),encoding="utf-8",newline="\n")
    (dest/BASE.MANDATORY).write_text("\n".join(targets(sec))+"\n",encoding="utf-8",newline="\n")
    shutil.copyfile(OLD.ROOT/"scripts/vp05_stage2_monitored_kira.py",dest/BASE.MONITOR)
    with (dest/MANIFEST).open("x",encoding="utf-8") as f:
        json.dump({"sector":sec,"level":level,"seed":"r5s6d2","targets":targets(sec),
                   "hashes":{p:OLD.old.sha256(dest/p) for p in FILES}},f,indent=2)

def inspect(sec,level):
    dest=folder(sec,level)
    if dest.is_symlink():raise RuntimeError("Linked project")
    if not dest.exists():return {"state":"new"}
    m=OLD.old.read_json(dest/MANIFEST)
    if (m.get("sector"),m.get("level"),m.get("seed"),m.get("targets"))!=(sec,level,"r5s6d2",targets(sec)) or set(m.get("hashes",{}))!=set(FILES):
        raise RuntimeError("Manifest mismatch")
    for p,h in m["hashes"].items():
        if (dest/p).is_symlink() or OLD.old.sha256(dest/p)!=h:raise RuntimeError("Input changed")
    if _read_integrals(dest/BASE.MANDATORY,BASE.FAMILY)!=targets(sec):raise RuntimeError("Target mismatch")
    end=dest/"monitored_exit.json"
    if end.exists():
        result=OLD.old.read_json(end)
        state="completed" if result.get("success") is True and result.get("reason")=="kira_exit" and result.get("kira_returncode")==0 else "guard_stopped" if result.get("reason") in ("ram_stop","swap_stop","time_stop") and result.get("success") is False and result.get("kira_returncode") in (-15,-9) else "failed"
        files=sorted((dest/"tmp"/BASE.FAMILY).glob("SYSTEM_*.gz"))
        master=dest/"results"/BASE.FAMILY/"masters"
        masters=parse_masters_final(master,BASE.FAMILY) if master.is_file() else []
        return {"state":state,"monitor":result,"resources":BASE.read_resource_peaks(dest),
                "SYSTEM_files":[{"name":p.name,"bytes":p.stat().st_size} for p in files],
                "masters":masters,"masters_file_exists":master.is_file()}
    if any((dest/p).exists() for p in ("console_output.log","results","tmp","sectormappings","monitored_kira.log","monitored_metrics.jsonl")):
        return {"state":"interrupted"}
    return {"state":"prepared"}

def run(mode,hours):
    for sec in SECTORS:
        old=prior.inspect(sec,"plain")
        if old["state"]!="guard_stopped" or old["monitor"]["reason"]!="ram_stop":
            raise RuntimeError("Original plain run changed")
    start=time.monotonic()
    rows=[]
    # Start with stronger truncation. If it succeeds, loosen it in steps;
    # if it hits the guard, do not spend resources on weaker truncations.
    for sec in SECTORS:
        for level in LEVELS:
            before=inspect(sec,level)
            if mode=="run" and before["state"] in ("new","prepared"):
                if level!=LEVELS[0] and inspect(sec,LEVELS[LEVELS.index(level)-1])["state"]!="completed":
                    break
                remaining=int(hours*3600-(time.monotonic()-start))
                if remaining<30:break
                BASE._no_other_kira()
                OLD.old.wsl_resource_preflight()
                if shutil.disk_usage(OLD.OUTPUT).free<10*1024**3:raise RuntimeError("Disk free below 10 GiB")
                if before["state"]=="new":prepare(sec,level)
                dest=folder(sec,level)
                remaining=int(hours*3600-(time.monotonic()-start))
                if remaining<30:break
                cmd=["wsl.exe","--cd",str(dest),"python3",BASE.MONITOR,
                     "--max-seconds",str(min(5400,remaining)),"--interval","5","--warn-gib","4","--stop-gib","8","--ram-warn-gib","18","--ram-stop-gib","22"]
                print("VP05_TRUNCATE_BEGIN "+json.dumps({"sector":sec,"level":level}),flush=True)
                with (dest/"console_output.log").open("x",encoding="utf-8") as log:
                    code=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode
                before=inspect(sec,level)
                if not ((code==0 and before["state"]=="completed") or (code in (124,125) and before["state"]=="guard_stopped")):
                    print("VP05_TRUNCATE_UNEXPECTED "+json.dumps({"sector":sec,"level":level,"exit":code,"detail":before}),flush=True)
                    raise RuntimeError("Unexpected pilot exit; preserve job")
            row={"sector":sec,"level":level,"target_count":len(targets(sec)),**before}
            rows.append(row)
            print("VP05_TRUNCATE_JOB "+json.dumps(row),flush=True)
            if mode=="run" and before["state"] in ("failed","interrupted"):raise RuntimeError("Review existing job")
            if mode=="run" and before["state"]=="guard_stopped":break
    return {"status":"VP05_SUBSECTOR_TRUNCATE_DIAGNOSTIC_NOT_CLOSURE","rows":rows,
            "explicit_scalar_dot_targets_only":True,"full_numerator_coverage_proven":False,
            "parent_scope_equivalence_proven":False,"family_closure_proven":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("run","audit"))
    p.add_argument("--hours",type=float,default=12)
    a=p.parse_args()
    if a.mode=="run" and (os.name!="nt" or not 0<a.hours<=12):p.error("Windows and 0<hours<=12 required")
    print("VP05_SUBSECTOR_TRUNCATE "+json.dumps(run(a.mode,a.hours)),flush=True)
