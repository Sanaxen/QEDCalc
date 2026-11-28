"""Native07: continue exact numerator shells s5/s6 at two finite-field points.
Each shell is independent (not a cumulative boundary retention certificate).
Reuse matching packed04 state if present; never seed s5 with s4 pivots.
"""
import argparse,gc,itertools,os,shutil,subprocess,tempfile,time
from pathlib import Path
from examples import three_loop_vp05_native_batch as prev
v=prev.v;n=prev.n;b=prev.b
ROOT=n.BASE/"output"/"vp05_independent_ibp_native07"
SECTORS=(69,196,200)

def meta(sec,s,point,digest):
    return {**b.meta(sec,s,point),"native_batch":7,"source_sha256":digest}

def job(sec,s,point,kernel,exe,work,deadline,batch,reference_rank):
    p,z,d=b.c.old.POINTS[point]
    end=b.c.expected(s)
    source=b.ROOT/f"sec{sec}_s{s}_p{point}.bin"
    digest=n.sha(source) if source.exists() else "empty"
    m=meta(sec,s,point,digest)
    path=ROOT/f"sec{sec}_s{s}_p{point}.bin"
    if path.with_suffix(".tmp").exists():raise RuntimeError("Stale temporary checkpoint")
    if path.exists():
        cursor,store,peak,elapsed=b.load(path,m,p)
    elif source.exists():
        cursor,store,peak,elapsed=b.load(source,b.meta(sec,s,point),p)
        if n.sha(source)!=digest:raise RuntimeError("Source changed")
    else:
        cursor=0;store=b.Packed();peak=elapsed=0
    v.log("VP05_NATIVE07_RESUME",sector=sec,shell=s,point=point,rows=cursor,expected=end,rank=len(store.piv),terms=store.terms,source_sha256=digest)
    ev={ij:[(b.c.old.evaluate(x,p,z),tuple(b.c.old.evaluate(y,p,z) for y in cs)) for x,cs in entries] for ij,entries in kernel.items()}
    iterator=itertools.islice(b.c.rows(sec,s),cursor,None)
    reason=None
    while cursor<end and time.monotonic()<deadline:
        t=time.monotonic()
        b.a.memory()
        if shutil.disk_usage(ROOT).free<4*b.a.GIB:raise RuntimeError("Disk reserve")
        stop=min(cursor+batch,end)
        rows=[(i,b.c.old.row(ex,ev[j,k],j,k,d)) for i,(ex,j,k) in enumerate(itertools.islice(iterator,stop-cursor),cursor)]
        if len(rows)!=stop-cursor:raise RuntimeError("Source cursor")
        inp=work/"batch.in";out=work/"batch.out"
        try:
            prev.export(inp,store,rows,p,deadline)
            v.log("VP05_NATIVE07_BATCH",sector=sec,shell=s,point=point,start=cursor,stop=stop)
            peak=max(peak,v.run_native(exe,inp,out,min(deadline,time.monotonic()+1560)))
            pending,native_s,ram,swap=prev.read_result(out,store,rows,p)
            if cursor==0:
                shadow=b.Packed()
                native={i:row for i,_,row in pending if i<64}
                for i,raw in rows[:64]:
                    lead,row=b.reduce(raw,shadow,p,b.CAP,deadline)
                    if (row or {})!=native.get(i,{}):raise RuntimeError("Fresh point Python comparison")
                    if lead is not None:shadow.add(i,lead,row.items())
            if source.exists() and n.sha(source)!=digest:raise RuntimeError("Source changed")
            for i,lead,row in pending:store.add(i,lead,row.items())
            if stop==end and reference_rank is not None and len(store.piv)!=reference_rank:raise RuntimeError("Completed rank disagreement")
            elapsed+=time.monotonic()-t
            b.save(path,m,stop,store,peak,elapsed)
            cursor=stop
            v.log("VP05_NATIVE07_SAVED",sector=sec,shell=s,point=point,rows=cursor,expected=end,rank=len(store.piv),terms=store.terms,native_s=native_s,peak_wsl_ram_gib=ram,peak_wsl_swap_gib=swap,peak_windows_ram_gib=peak,elapsed_before_save_s=elapsed)
            if native_s>900:batch=max(64,batch//2)
        except TimeoutError as exc:
            reason=str(exc);break
        except RuntimeError as exc:
            # Preserve last completed transaction; do not conceal validation failures.
            if str(exc).startswith("Native exit "):reason=str(exc);break
            raise
        finally:
            inp.unlink(missing_ok=True);out.unlink(missing_ok=True)
    expected=(cursor,len(store.piv),store.terms)
    del store;gc.collect()
    if path.exists():
        check,loaded,_,_=b.load(path,m,p)
        if (check,len(loaded.piv),loaded.terms)!=expected:raise RuntimeError("Saved checkpoint mismatch")
        del loaded;gc.collect()
    if source.exists() and n.sha(source)!=digest:raise RuntimeError("Source changed")
    if cursor==end and reference_rank is not None and expected[1]!=reference_rank:raise RuntimeError("Rank disagreement")
    result={"sector":sec,"shell":s,"point":point,"rows":cursor,"expected":end,"rank":expected[1],"terms":expected[2],"complete":cursor==end,"reason":reason}
    v.log("VP05_NATIVE07_JOB",**result)
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--batch-rows",type=int,default=5000)
    ap.add_argument("--smax",type=int,default=6)
    args=ap.parse_args()
    if not 0<args.hours<=12 or not 64<=args.batch_rows<=5000 or not 5<=args.smax<=6:ap.error("Invalid scope")
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    deadline=time.monotonic()+args.hours*3600
    results=[];blocked=set()
    try:
        for root in (b.ROOT,b.a.ROOT,b.c.ROOT,n.ROOT,v.ROOT,prev.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        b.a.memory()
        kernel=b.c.old.build_kernel(b.c.old.build_family_spec("VP05_full").propagators)
        if b.c.old.digest(kernel)!=b.c.PIN:raise RuntimeError("Kernel differs")
        with tempfile.TemporaryDirectory(prefix="native07_",dir=ROOT) as folder:
            work=Path(folder);exe=work/"native"
            subprocess.run(["wsl","--exec","g++","-std=c++17","-O3","-Wall","-Wextra",n.wslpath(n.BASE/"examples"/"vp05_native_batch.cpp"),"-o",n.wslpath(exe)],check=True,timeout=120)
            n.synthetic(exe,work)
            for s in range(5,args.smax+1):
                for sec in SECTORS:
                    if sec in blocked or time.monotonic()>=deadline:continue
                    reference=None
                    for point in range(2):
                        if time.monotonic()>=deadline:break
                        result=job(sec,s,point,kernel,exe,work,deadline,args.batch_rows,reference)
                        results.append(result)
                        if not result["complete"]:blocked.add(sec);break
                        reference=result["rank"]
        v.log("VP05_NATIVE07_NOT_CLOSURE",results=results,blocked_sectors=sorted(blocked),all_requested_complete=len(results)==len(SECTORS)*(args.smax-4)*2 and all(r["complete"] for r in results),full_closure_proven=False)
    except (KeyboardInterrupt,TimeoutError) as exc:
        v.log("VP05_NATIVE07_PAUSED_NOT_CLOSURE",reason=str(exc) or "User interrupt",full_closure_proven=False)
    finally:lock.unlink()
if __name__=="__main__":main()
