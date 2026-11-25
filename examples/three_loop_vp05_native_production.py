"""Native production pilot: sector196 s4 p0 only, atomic completed-batch checkpoints.

Uses the measured native executable unchanged. Each batch is transactional:
an interrupted batch is discarded and recomputed, not partially promoted.
No writes to packed04, no closure claim.
"""
import argparse
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
import time
from pathlib import Path
from examples import three_loop_vp05_native_benchmark as n

b=n.b
ROOT=n.BASE/"output"/"vp05_independent_ibp_native05"
SOURCE=b.ROOT/"sec196_s4_p0.bin"
START=73949
END=74250
OBS=(START,46175,37179224)
META={**b.meta(196,4,0),"native_pilot":1}
# packed loader requires exactly this meta and validates shell/coefficients.
def log(tag,**kw):
    print(tag+" "+json.dumps(kw),flush=True)

def run_native(exe,inp,out,deadline):
    cmd=["wsl","--exec",n.wslpath(exe),n.wslpath(inp),n.wslpath(out)]
    peak=0
    with subprocess.Popen(cmd) as proc:
        try:
            while proc.poll() is None:
                total,avail=b.a.memory()
                peak=max(peak,(total-avail)/b.a.GIB)
                if time.monotonic()>=deadline:raise TimeoutError("Native batch budget")
                time.sleep(1)
            if proc.returncode:raise RuntimeError("Native exit "+str(proc.returncode))
        except BaseException:
            try:
                subprocess.run(["wsl","--exec","pkill","-f","^"+re.escape(cmd[2])+" "],timeout=15,check=False)
            finally:
                if proc.poll() is None:proc.kill()
            raise
    return peak

def import_result(out,store,rows):
    """Check output structure/counts before changing the on-disk state."""
    rank=len(store.piv);terms=store.terms
    seen=set();pending=[];trace=[]
    with out.open("rb") as f:
        if struct.unpack("<II",n.exact(f,8))!=(n.MAGIC,len(rows)):raise RuntimeError("Native output header")
        for index,_ in rows:
            v=n.read_row(f)
            if v:
                lead=max(v)
                if v[lead]!=1 or lead in store.piv or lead in seen:raise RuntimeError("Native pivot invariant")
                if any(b.c.key(b.c.decode(k))!=k for k in v):raise RuntimeError("Native key invariant")
                seen.add(lead);pending.append((index,lead,v));rank+=1;terms+=len(v)
            if terms>b.CAP or struct.unpack("<IQ",n.exact(f,12))!=(rank,terms):
                raise RuntimeError("Native rank/term mismatch")
            trace.append((rank,terms))
        ns,ram,swap=struct.unpack("<QQQ",n.exact(f,24))
        if f.read(1):raise RuntimeError("Trailing native output")
        if ram>=22*1048576 or swap>=8*1048576:raise RuntimeError("Native resource limit")
    return pending,trace,ns/1e9,ram/1048576,swap/1048576

def save_batch(path,store,cursor,peak,elapsed,pending):
    # No live state mutation before all native output has been checked.
    for index,lead,v in pending:store.add(index,lead,v.items())
    b.save(path,META,cursor,store,peak,elapsed)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--batch-rows",type=int,default=301)
    ap.add_argument("--max-batches",type=int,default=0)
    args=ap.parse_args()
    if not 0<args.hours<=12 or not 1<=args.batch_rows<=301 or args.max_batches<0:ap.error("Invalid scope")
    ROOT.mkdir(exist_ok=True)
    lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    deadline=time.monotonic()+args.hours*3600
    path=ROOT/"sec196_s4_p0.bin"
    try:
        for root in (b.ROOT,b.a.ROOT,b.c.ROOT,n.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        if path.with_suffix(".tmp").exists():raise RuntimeError("Stale temporary checkpoint; review before restart")
        b.a.memory()
        digest=n.sha(SOURCE)
        pin=ROOT/"source.sha256"
        if pin.exists():
            if pin.read_text().strip()!=digest:raise RuntimeError("Source digest changed")
        else:
            if path.exists():raise RuntimeError("Missing source pin")
            with pin.open("x") as f:f.write(digest+"\n");f.flush();os.fsync(f.fileno())
        if path.exists():
            cursor,store,peak,elapsed=b.load(path,META,n.P)
            if not START<cursor<=END or len(store.piv)<OBS[1] or store.terms<OBS[2]:raise RuntimeError("Native resume scope")
        else:
            cursor,store,peak,elapsed=b.load(SOURCE,b.meta(196,4,0),n.P)
            if (cursor,len(store.piv),store.terms)!=OBS:raise RuntimeError("Original observed state mismatch")
            peak=0;elapsed=0
        log("VP05_NATIVE_PRODUCTION_RESUME",cursor=cursor,rank=len(store.piv),terms=store.terms,source_sha256=digest)
        if cursor==END:
            log("VP05_NATIVE_PRODUCTION_COMPLETE_NOT_CLOSURE",rows=cursor,rank=len(store.piv),terms=store.terms)
            return
        kernel=b.c.old.build_kernel(b.c.old.build_family_spec("VP05_full").propagators)
        if b.c.old.digest(kernel)!=b.c.PIN:raise RuntimeError("Kernel differs")
        p,z,d=b.c.old.POINTS[0]
        if p!=n.P:raise RuntimeError("Prime differs")
        ev={ij:[(b.c.old.evaluate(x,p,z),tuple(b.c.old.evaluate(y,p,z) for y in cs)) for x,cs in entries] for ij,entries in kernel.items()}
        with tempfile.TemporaryDirectory(prefix="native_",dir=ROOT) as folder:
            work=Path(folder);exe=work/"native"
            subprocess.run(["wsl","--exec","g++","-std=c++17","-O3","-Wall","-Wextra",n.wslpath(n.BASE/"examples"/"vp05_native_benchmark.cpp"),"-o",n.wslpath(exe)],check=True,timeout=120)
            n.synthetic(exe,work)
            batches=0
            while cursor<END and time.monotonic()<deadline:
                if args.max_batches and batches>=args.max_batches:break
                t=time.monotonic()
                if shutil.disk_usage(ROOT).free<4*b.a.GIB:raise RuntimeError("Disk reserve")
                stop=min(cursor+args.batch_rows,END)
                rows=[]
                for i,(ex,j,k) in enumerate(b.c.rows(196,4)):
                    if i<cursor:continue
                    if i>=stop:break
                    rows.append((i,b.c.old.row(ex,ev[j,k],j,k,d)))
                if [i for i,_ in rows]!=list(range(cursor,stop)):raise RuntimeError("Row cursor mismatch")
                inp=work/"batch.in";out=work/"batch.out"
                with inp.open("xb") as f:
                    f.write(struct.pack("<IIII",n.MAGIC,p,len(store.piv),len(rows)))
                    for j,lead in enumerate(store.piv):
                        if j%256==0:
                            b.a.memory()
                            if time.monotonic()>=deadline:raise TimeoutError("Export budget")
                        n.write_row(f,store.items(lead))
                    for _,raw in rows:n.write_row(f,((b.c.key(k),v%p) for k,v in raw.items() if v%p))
                log("VP05_NATIVE_PRODUCTION_BATCH",start=cursor,stop=stop)
                peak=max(peak,run_native(exe,inp,out,min(deadline,time.monotonic()+1560)))
                pending,trace,reduce_s,ram,swap=import_result(out,store,rows)
                # Known real benchmark endpoint checked whenever included.
                if cursor<74013<=stop and trace[74013-cursor-1]!=(46194,37221447):
                    raise RuntimeError("Measured benchmark endpoint mismatch")
                if n.sha(SOURCE)!=digest:raise RuntimeError("Source changed")
                elapsed+=time.monotonic()-t
                save_batch(path,store,stop,peak,elapsed,pending)
                cursor=stop;batches+=1
                log("VP05_NATIVE_PRODUCTION_SAVED",rows=cursor,rank=len(store.piv),terms=store.terms,native_reduce_s=reduce_s,peak_wsl_ram_gib=ram,peak_wsl_swap_gib=swap,peak_windows_ram_gib=peak,elapsed_s=elapsed)
                inp.unlink();out.unlink()
        # Independent structural/checksum reload after final save.
        if path.exists():
            expected=(cursor,len(store.piv),store.terms)
            del store
            check,loaded,_,_=b.load(path,META,p)
            if (check,len(loaded.piv),loaded.terms)!=expected:raise RuntimeError("Saved-state mismatch")
        if n.sha(SOURCE)!=digest:raise RuntimeError("Source changed")
        log("VP05_NATIVE_PRODUCTION_COMPLETE_NOT_CLOSURE" if cursor==END else "VP05_NATIVE_PRODUCTION_PAUSED_NOT_CLOSURE",rows=cursor,expected=END,source_unchanged=True)
    finally:lock.unlink()

if __name__=="__main__":main()
