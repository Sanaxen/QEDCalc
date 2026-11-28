"""Read-only forensics for seven outstanding r8s6d2 isolated jobs.
Validate serialized SYSTEM framing and gzip EOF/CRC; never assume completion.
"""
import argparse,gzip,time,os,re
from pathlib import Path
from examples import three_loop_vp05_remaining_safe_batch as safe
from examples import three_loop_vp05_recovery_gate as gate
from examples import three_loop_vp05_stage2_sector202_stop_forensics as forensic
a=gate.a;n=a.n;gap=a.gap
ROOT=n.BASE/"output"/"vp05_priority7_forensics48"
SOURCE=gate.ROOT/"report_1795820871336224500.json"
SHA="a6d66cfb273f39ca7643bf4f1f1010c632f84b2c2c986480872bb5ac070c69c0"
SECTORS=(204,205,228,229,230,231,237)
MAX_BYTES=4*1024**3
MAX_ROWS=5000000
MAX_LINE=1024*1024

def scan(path,deadline):
    rows=terms=bytes_read=0
    try:
        with gzip.open(path,"rb") as f:
            def line():
                nonlocal bytes_read
                if time.monotonic()>=deadline:raise TimeoutError("Scan deadline")
                b=f.readline(MAX_LINE+1);bytes_read+=len(b)
                if len(b)>MAX_LINE or bytes_read>MAX_BYTES:raise RuntimeError("Scan size cap")
                return b
            while True:
                marker=line()
                if not marker:break
                if marker.strip()!=b"Eq":raise ValueError("Invalid Eq marker")
                int(line().strip());count=int(line().strip())
                if not 0<=count<=100000:raise ValueError("Invalid term count")
                for _ in range(count):
                    fields=line().split()
                    if len(fields)<4:raise ValueError("Invalid term framing")
                    int(fields[2]);int(fields[3])
                rows+=1;terms+=count
                if rows>MAX_ROWS:raise RuntimeError("Row cap")
        return {"complete_stream":True,"rows":rows,"terms":terms,"uncompressed_bytes":bytes_read}
    except (OSError,EOFError,ValueError,RuntimeError,TimeoutError) as exc:
        return {"complete_stream":False,"rows":rows,"terms":terms,"uncompressed_bytes":bytes_read,"error":str(exc)}

def tail(path,limit=65536):
    with path.open("rb") as f:
        f.seek(max(0,f.seek(0,2)-limit))
        return f.read().decode("utf-8","replace")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=2:ap.error("Time cap")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Recovery SHA")
    data=gap.read(SOURCE)
    if data["local_evidence_total"]!=57 or data["review_issues"]:raise RuntimeError("Recovery scope")
    if not {("r8s6d2",s) for s in SECTORS}<=set(map(tuple,data["remaining_boundaries"])):raise RuntimeError("Missing scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    safe.base._no_other_kira()
    items=[i for i in safe.scope() if i["seed"]=="r8s6d2" and i["sector"] in SECTORS]
    if {i["sector"] for i in items}!=set(SECTORS):raise RuntimeError("Job scope")
    results=[]
    for item in items:
        path=safe.path_for(item);state,detail=safe.status(item)
        rec={**item,"state":state,"monitor":detail,"project":str(path),"systems":[],"metadata":{}}
        def pin(f):
            if f.is_symlink() or not f.is_file():raise RuntimeError("Nonregular file "+str(f))
            digest=n.sha(f)
            if f in pins and pins[f]!=digest:raise RuntimeError("Prior SHA changed")
            pins[f]=digest
        if path.exists():
            for name in (safe.MANIFEST,*safe.base.FILES,"monitored_exit.json","monitored_metrics.jsonl","monitored_kira.log","results/kira.db","results/preferredMasters","sectormappings/auxiliary.yaml","results/VP05_full/masters","tmp/VP05_full/masters"):
                f=path/name
                if f.exists():
                    pin(f);rec["metadata"][name]={"bytes":f.stat().st_size,"sha256":pins[f]}
            log=path/"monitored_kira.log"
            if log.exists():
                t=tail(log);rec["log_tail"]=t[-4096:]
                hits=re.findall(r"Generate equations for topology .*? sector (\d+) \((\d+) of (\d+)\)",t)
                rec["last_sector_progress"]=list(hits[-1]) if hits else None
            metrics=path/"monitored_metrics.jsonl"
            if metrics.exists():
                try:rec["resources"]=forensic.metrics(metrics)
                except (RuntimeError,ValueError,OSError) as exc:rec["metrics_issue"]=str(exc)
            for f in sorted((path/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
                if time.monotonic()>=deadline:raise TimeoutError("Job scan budget")
                pin(f)
                rec["systems"].append({"file":f.name,"sha256":pins[f],"compressed_bytes":f.stat().st_size,**scan(f,deadline)})
        rec["complete_streams"]=sum(x["complete_stream"] for x in rec["systems"])
        rec["readable_rows"]=sum(x["rows"] for x in rec["systems"] if x["complete_stream"])
        rec["codec_metadata_present"]=all(k in rec["metadata"] for k in ("results/kira.db","results/preferredMasters","sectormappings/auxiliary.yaml"))
        rec["reuse_class"]=("already_retained" if state=="completed_local_retained" else "requires_physical_codec_audit" if rec["complete_streams"] and rec["codec_metadata_present"] else "no_verified_reusable_system")
        results.append(rec)
        resources=rec.get("resources",{})
        a.v.log("VP05_PRIORITY7_FORENSIC_JOB",sector=item["sector"],state=state,reason=(detail or {}).get("reason"),effective_seed=item["effective_seed"],system_files=len(rec["systems"]),complete_streams=rec["complete_streams"],readable_rows=rec["readable_rows"],codec_metadata_present=rec["codec_metadata_present"],max_ram_gib=resources.get("max_ram_gib"),max_swap_gib=resources.get("max_swap_gib"),last_sector_progress=rec.get("last_sector_progress"),reuse_class=rec["reuse_class"])
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    payload={"status":"VP05_PRIORITY7_FORENSICS_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},"jobs":results,"full_closure_proven":False,"kira_executed":False}
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],jobs=len(results),complete_streams=sum(r["complete_streams"] for r in results),readable_rows=sum(r["readable_rows"] for r in results),report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
if __name__=="__main__":main()
