"""Native06: bounded resumable s4 continuation, not family closure."""
import argparse
import gc
import itertools
import os
import shutil
import struct
import subprocess
import tempfile
import time
from examples import three_loop_vp05_native_production as v

n=v.n
b=v.b
ROOT=n.BASE/"output"/"vp05_independent_ibp_native06"
JOBS=((196,1),(200,0),(200,1))
END=74250

def meta(sec,point,source):
    return {**b.meta(sec,4,point),"native_batch":6,"source_sha256":source}

def source_for(sec,point):
    if point==0 and sec==200:return b.a.state_path(sec,4,point)
    return None

def read_result(path,store,rows,p):
    # Generalize the tested native05 import to either actual field.
    pending=[];seen=set();rank=len(store.piv);terms=store.terms
    with path.open("rb") as f:
        if struct.unpack("<II",n.exact(f,8))!=(n.MAGIC,len(rows)):raise RuntimeError("Native header")
        for index,_ in rows:
            size,=struct.unpack("<I",n.exact(f,4))
            if size>b.FILL:raise RuntimeError("Native fill")
            row={}
            for _ in range(size):
                key=int.from_bytes(n.exact(f,10),"little")
                val,=struct.unpack("<I",n.exact(f,4))
                if key in row or not 0<val<p or b.c.key(b.c.decode(key))!=key:raise RuntimeError("Native term")
                row[key]=val
            if row:
                lead=max(row)
                if row[lead]!=1 or lead in store.piv or lead in seen:raise RuntimeError("Native lead")
                seen.add(lead);rank+=1;terms+=size
                pending.append((index,lead,row))
            if terms>b.CAP or struct.unpack("<IQ",n.exact(f,12))!=(rank,terms):raise RuntimeError("Native totals")
        ns,ram,swap=struct.unpack("<QQQ",n.exact(f,24))
        if f.read(1) or ram>=22*1048576 or swap>=8*1048576:raise RuntimeError("Native trailer")
    return pending,ns/1e9,ram/1048576,swap/1048576

def raw_rows(sec,cursor,stop,ev,d):
    return [(i,b.c.old.row(ex,ev[j,k],j,k,d)) for i,(ex,j,k) in
            enumerate(itertools.islice(b.c.rows(sec,4),cursor,stop),cursor)]

def export(path,store,rows,p,deadline):
    with path.open("xb") as f:
        f.write(struct.pack("<IIII",n.MAGIC,p,len(store.piv),len(rows)))
        for j,lead in enumerate(store.piv):
            if j%256==0:
                b.a.memory()
                if time.monotonic()>=deadline:raise TimeoutError("Export budget")
            n.write_row(f,store.items(lead))
        for _,raw in rows:n.write_row(f,((b.c.key(k),val%p) for k,val in raw.items() if val%p))

def verify_prior():
    results={}
    for sec,point,path,m,rank,terms in [
        (69,0,b.ROOT/"sec69_s4_p0.bin",b.meta(69,4,0),43732,15365823),
        (69,1,b.ROOT/"sec69_s4_p1.bin",b.meta(69,4,1),43732,15368744),
        (196,0,v.ROOT/"sec196_s4_p0.bin",v.META,46280,37355607)]:
        digest=n.sha(path)
        cursor,store,_,_=b.load(path,m,b.c.old.POINTS[point][0])
        if (cursor,len(store.piv),store.terms)!=(END,rank,terms) or n.sha(path)!=digest:raise RuntimeError("Prior completed state mismatch")
        results[path]=digest
        del store
        gc.collect()
    if n.sha(v.SOURCE)!="81b6cdc7cdc770bcd49150925378bc09b25aa65c0cd04061968d32b0939655bd":raise RuntimeError("Native05 original source changed")
    results[v.SOURCE]=n.sha(v.SOURCE)
    return results

def job(sec,point,kernel,exe,work,deadline,batch,reference_rank):
    p,z,d=b.c.old.POINTS[point]
    source=source_for(sec,point)
    digest=n.sha(source) if source else "empty"
    m=meta(sec,point,digest)
    path=ROOT/f"sec{sec}_s4_p{point}.bin"
    if path.with_suffix(".tmp").exists():raise RuntimeError("Stale temporary checkpoint: "+str(path))
    if path.exists():
        cursor,store,peak,elapsed=b.load(path,m,p)
        if not (51110 if source else 0)<=cursor<=END:raise RuntimeError("Resume cursor")
    elif source:
        cursor,store,_,_=b.read_legacy(sec,4,point,p)
        if (cursor,len(store.piv),store.terms)!=(51110,37145,11999831) or n.sha(source)!=digest:raise RuntimeError("Legacy source mismatch")
        peak=elapsed=0
    else:
        cursor=0;store=b.Packed();peak=elapsed=0
    v.log("VP05_NATIVE06_RESUME",sector=sec,point=point,rows=cursor,rank=len(store.piv),terms=store.terms)
    ev={ij:[(b.c.old.evaluate(x,p,z),tuple(b.c.old.evaluate(y,p,z) for y in cs)) for x,cs in entries] for ij,entries in kernel.items()}
    # Reuse the same row iterator, avoiding rescanning the entire prefix for each batch.
    iterator=itertools.islice(b.c.rows(sec,4),cursor,None)
    while cursor<END and time.monotonic()<deadline:
        t=time.monotonic()
        b.a.memory()
        if shutil.disk_usage(ROOT).free<4*b.a.GIB:raise RuntimeError("Disk reserve")
        stop=min(cursor+batch,END)
        rows=[(i,b.c.old.row(ex,ev[j,k],j,k,d)) for i,(ex,j,k) in enumerate(itertools.islice(iterator,stop-cursor),cursor)]
        if len(rows)!=stop-cursor:raise RuntimeError("Source cursor")
        inp=work/"batch.in";out=work/"batch.out"
        export(inp,store,rows,p,deadline)
        v.log("VP05_NATIVE06_BATCH",sector=sec,point=point,start=cursor,stop=stop)
        peak=max(peak,v.run_native(exe,inp,out,min(deadline,time.monotonic()+1560)))
        pending,native_s,ram,swap=read_result(out,store,rows,p)
        # At first batch of a fresh point, independently compare the first 64 source rows.
        if cursor==0:
            shadow=b.Packed()
            native={i:row for i,_,row in pending if i<64}
            for i,raw in rows[:64]:
                lead,row=b.reduce(raw,shadow,p,b.CAP,deadline)
                if (row or {})!=native.get(i,{}):raise RuntimeError("Fresh point Python comparison")
                if lead is not None:shadow.add(i,lead,row.items())
            v.log("VP05_NATIVE06_FRESH_POINT_COMPARE",sector=sec,point=point,rows=min(64,len(rows)),equal=True)
        if source and n.sha(source)!=digest:raise RuntimeError("Legacy source changed")
        for i,lead,row in pending:store.add(i,lead,row.items())
        if stop==END and reference_rank is not None and len(store.piv)!=reference_rank:
            raise RuntimeError("Completed rank disagreement; final batch not saved")
        elapsed+=time.monotonic()-t
        b.save(path,m,stop,store,peak,elapsed)
        cursor=stop
        v.log("VP05_NATIVE06_SAVED",sector=sec,point=point,rows=cursor,expected=END,rank=len(store.piv),terms=store.terms,native_s=native_s,elapsed_before_save_s=elapsed,peak_wsl_ram_gib=ram,peak_wsl_swap_gib=swap,peak_windows_ram_gib=peak)
        inp.unlink();out.unlink()
        # adapt downward when native time approaches per-batch budget
        if native_s>900:batch=max(64,batch//2)
    expected=(cursor,len(store.piv),store.terms)
    del store
    gc.collect()
    if path.exists():
        check,loaded,_,_=b.load(path,m,p)
        if (check,len(loaded.piv),loaded.terms)!=expected:raise RuntimeError("Saved state mismatch")
        del loaded
        gc.collect()
    if source and n.sha(source)!=digest:raise RuntimeError("Legacy source changed")
    if cursor==END and reference_rank is not None and expected[1]!=reference_rank:raise RuntimeError("Rank disagreement")
    v.log("VP05_NATIVE06_JOB",sector=sec,point=point,rows=cursor,rank=expected[1],terms=expected[2],complete=cursor==END)
    return cursor,expected[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--batch-rows",type=int,default=2000)
    args=ap.parse_args()
    if not 0<args.hours<=12 or not 64<=args.batch_rows<=5000:ap.error("Invalid scope")
    ROOT.mkdir(exist_ok=True)
    lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    deadline=time.monotonic()+args.hours*3600
    prior={}
    try:
        for root in (b.ROOT,b.a.ROOT,b.c.ROOT,n.ROOT,v.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        prior=verify_prior()
        kernel=b.c.old.build_kernel(b.c.old.build_family_spec("VP05_full").propagators)
        if b.c.old.digest(kernel)!=b.c.PIN:raise RuntimeError("Kernel differs")
        rank200=None;complete=True
        with tempfile.TemporaryDirectory(prefix="native06_",dir=ROOT) as folder:
            from pathlib import Path
            work=Path(folder);exe=work/"native"
            subprocess.run(["wsl","--exec","g++","-std=c++17","-O3","-Wall","-Wextra",n.wslpath(n.BASE/"examples"/"vp05_native_batch.cpp"),"-o",n.wslpath(exe)],check=True,timeout=120)
            n.synthetic(exe,work)
            for sec,point in JOBS:
                if time.monotonic()>=deadline:complete=False;break
                cursor,rank=job(sec,point,kernel,exe,work,deadline,args.batch_rows,46280 if sec==196 else rank200)
                if cursor!=END:complete=False;break
                if sec==200 and point==0:rank200=rank
        if any(n.sha(path)!=digest for path,digest in prior.items()):raise RuntimeError("Prior checkpoint changed")
        v.log("VP05_NATIVE06_S4_COMPLETE_NOT_CLOSURE" if complete else "VP05_NATIVE06_PAUSED_NOT_CLOSURE",s4_complete=complete,prior_unchanged=True,full_closure_proven=False)
    except (TimeoutError,KeyboardInterrupt) as exc:
        v.log("VP05_NATIVE06_PAUSED_NOT_CLOSURE",reason=str(exc) or "User interrupt",full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
