"""Adaptive continuation of compact02. Original checkpoints read-only.

Same field, row order, integral ordering and pivot algorithm. New checkpoint
format stores one pivot per line, checksummed, avoiding giant JSON buffers.
Adaptive budget is conservative, sampled, not an OS hard memory limit.
"""
import argparse,hashlib,json,os,time,shutil
from pathlib import Path
from examples import three_loop_vp05_compact_ibp as c

ROOT=c.old.ROOT/"output"/"vp05_independent_ibp_adaptive03"
BASE_CAP=5000000
MAX_CAP=12000000
STEP=1000000
VERSION=2
MAX_FILE=1024**3
GIB=1024**3
OBSERVED={69:(21334,13752,1499224),196:(11093,8646,1499479),200:(17952,13222,1499810)}
RANKS={69:4363,196:4553,200:4553}

def memory():
    c.old.memory_guard()
    if os.name=="nt":
        import ctypes
        class M(ctypes.Structure):
            _fields_=[("length",ctypes.c_ulong),("load",ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ("total","available","total_page","available_page","total_virtual","available_virtual","extended")]
        m=M();m.length=ctypes.sizeof(m)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            raise RuntimeError("Host memory measurement failed")
        return m.total,m.available
    m=dict((x.split(":")[0],int(x.split()[1])*1024) for x in Path("/proc/meminfo").read_text().splitlines() if x.startswith(("MemTotal:","MemAvailable:")))
    return m["MemTotal"],m["MemAvailable"]

def next_cap(cap,available,stored):
    # Allow growth only while at least 10 GiB remain and estimated extra
    # dict storage (256 bytes/term) fits above the 8 GiB reserve.
    if cap>=MAX_CAP or available<10*GIB:return cap
    extra=min(STEP,MAX_CAP-cap)
    if (cap+extra-stored)*256>available-8*GIB:return cap
    return cap+extra

def meta(sec,s,point):
    return {"version":VERSION,"sector":sec,"shell":s,"point":list(c.old.POINTS[point]),
            "kernel_sha256":c.PIN,"ordering":"t-r-s-packed-desc","fill":c.FILL}

def old_meta(m):
    return {**m,"version":c.VERSION,"cap":c.CAP}

def state_path(sec,s,point):
    return ROOT/f"sec{sec}_s{s}_p{point}.stream"

def save(path,m,cursor,piv,selected,stored,peak,elapsed,cap):
    tmp=path.with_suffix(".tmp")
    if shutil.disk_usage(path.parent).free<2*GIB:raise RuntimeError("Checkpoint disk reserve")
    h=hashlib.sha256()
    with tmp.open("xb") as f:
        def line(obj):
            b=json.dumps(obj,separators=(",",":")).encode()+b"\n"
            h.update(b);f.write(b)
        line({"meta":m,"cursor":cursor,"rank":len(piv),"stored":stored,
              "peak":peak,"elapsed":elapsed,"cap":cap})
        for index,(lead,v) in zip(selected,piv.items()):
            line([index,lead,list(v.items())])
        f.write(h.hexdigest().encode()+b"\n")
        f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def load(path,m,p):
    if path.is_symlink() or path.stat().st_size>MAX_FILE:raise RuntimeError("Checkpoint size/link")
    h=hashlib.sha256()
    piv={};selected=[];stored=0
    with path.open("rb") as f:
        raw=f.readline(1024*1024)
        h.update(raw);head=json.loads(raw)
        if head["meta"]!=m or not 0<=head["rank"]<=head["cursor"]<=c.expected(m["shell"]) or not BASE_CAP<=head["cap"]<=MAX_CAP or not 0<=head["stored"]<=head["cap"]:
            raise RuntimeError("Checkpoint scope")
        for i in range(head["rank"]):
            if i%1000==0:memory()
            raw=f.readline(4*1024*1024)
            h.update(raw);index,lead,items=json.loads(raw)
            v=dict(items)
            if (not v or len(v)!=len(items) or lead in piv or max(v)!=lead or v.get(lead)!=1
                or any(not 0<x<p or c.key(c.decode(k))!=k for k,x in v.items())
                or not 0<=index<head["cursor"] or (selected and index<=selected[-1])):
                raise RuntimeError("Invalid pivot")
            piv[lead]=v;selected.append(index);stored+=len(v)
            if stored>head["cap"]:raise RuntimeError("Stored term cap")
        if f.readline().strip()!=h.hexdigest().encode() or f.read(1) or stored!=head["stored"]:
            raise RuntimeError("Checkpoint checksum/count")
    return head["cursor"],piv,selected,stored,head["peak"],head["elapsed"],head["cap"]

def migrate(m,p,point):
    path=c.ROOT/f"sec{m['sector']}_s{m['shell']}_p{point}.checkpoint"
    if not path.exists():return 0,{},[],0,0,0,BASE_CAP
    state=c.load(path,old_meta(m),p)
    cursor,piv,selected,stored,peak,elapsed=state
    if m["shell"]==2:
        if cursor!=6750 or len(piv)!=RANKS[m["sector"]]:raise RuntimeError("Prior s2 rank/cursor mismatch")
    elif m["shell"]==3 and point==0:
        if (cursor,len(piv),stored)!=OBSERVED[m["sector"]]:raise RuntimeError("Prior s3 log mismatch")
    else:raise RuntimeError("Unexpected prior checkpoint")
    return (*state,BASE_CAP)

def job(sec,s,point,kernel,deadline):
    m=meta(sec,s,point)
    p,z,d=c.old.POINTS[point]
    path=state_path(sec,s,point)
    if path.with_suffix(".tmp").exists():raise RuntimeError("Interrupted temporary checkpoint; preserve for review")
    memory()
    if path.exists():
        state=load(path,m,p)
    else:
        state=migrate(m,p,point)
        if state[0]:
            save(path,m,*state)
            print("VP05_ADAPTIVE_MIGRATED "+json.dumps({"sector":sec,"shell":s,"point":point,"rows":state[0],"rank":len(state[1]),"terms":state[3]}),flush=True)
    cursor,piv,selected,stored,peak,elapsed,cap=state
    start=time.monotonic();last_save=cursor;reason=None
    ev={ij:[(c.old.evaluate(x,p,z),tuple(c.old.evaluate(y,p,z) for y in cs)) for x,cs in entries] for ij,entries in kernel.items()}
    original_cap=c.CAP
    try:
        for index,(a,i,j) in enumerate(c.rows(sec,s)):
            if index<cursor:continue
            if index%15==0:
                total,available=memory()
                peak=max(peak,(total-available)/GIB)
            if time.monotonic()>=deadline:raise TimeoutError("Time budget")
            raw=c.old.row(a,ev[i,j],i,j,d)
            while True:
                c.CAP=cap
                try:
                    lead,v=c.reduce_row(raw,piv,p,stored)
                    break
                except RuntimeError as exc:
                    if str(exc)!="Stored term cap":raise
                    total,available=memory()
                    new=next_cap(cap,available,stored)
                    if new==cap:raise
                    cap=new
                    print("VP05_ADAPTIVE_CAP "+json.dumps({"sector":sec,"shell":s,"point":point,"rows":cursor,"cap":cap,"available_gib":available/GIB}),flush=True)
            if lead is not None:
                piv[lead]=v;stored+=len(v);selected.append(index)
            cursor=index+1
            if cursor-last_save>=5000:
                save(path,m,cursor,piv,selected,stored,peak,elapsed+time.monotonic()-start,cap)
                last_save=cursor
    except (TimeoutError,RuntimeError,KeyboardInterrupt) as exc:
        reason=str(exc) or "User interrupt"
    finally:
        c.CAP=original_cap
    complete=cursor==c.expected(s)
    if cursor!=last_save or not path.exists():
        save(path,m,cursor,piv,selected,stored,peak,elapsed+time.monotonic()-start,cap)
    if complete and s==2 and len(piv)!=RANKS[sec]:raise RuntimeError("Rank regression")
    result={"sector":sec,"shell":s,"point":point,"rows":cursor,"expected":c.expected(s),"rank":len(piv),"terms":stored,"cap":cap,"complete":complete,"reason":reason,"peak_host_ram_gib":peak,"elapsed_s":elapsed+time.monotonic()-start}
    print("VP05_ADAPTIVE_JOB "+json.dumps(result),flush=True)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--smax",type=int,default=6)
    p.add_argument("--hours",type=float,default=12)
    a=p.parse_args()
    if not 3<=a.smax<=6 or not 0<a.hours<=12:p.error("Invalid scope")
    memory()
    if (c.ROOT/"running.lock").exists():raise RuntimeError("Previous engine lock present")
    kernel=c.old.build_kernel(c.old.build_family_spec("VP05_full").propagators)
    if c.old.digest(kernel)!=c.PIN:raise RuntimeError("Kernel differs")
    ROOT.mkdir(exist_ok=True)
    lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    deadline=time.monotonic()+a.hours*3600
    blocked=set();results=[]
    try:
        for s in range(2,a.smax+1):
            for sec in c.old.SECTORS:
                if sec in blocked or time.monotonic()>=deadline:continue
                pair=[]
                for point in range(2):
                    r=job(sec,s,point,kernel,deadline);results.append(r);pair.append(r)
                    if not r["complete"]:blocked.add(sec);break
                if len(pair)==2 and all(x["complete"] for x in pair) and pair[0]["rank"]!=pair[1]["rank"]:
                    raise RuntimeError("Finite-field rank disagreement")
        print("VP05_ADAPTIVE_IBP_NOT_CLOSURE "+json.dumps({"results":results,"blocked_sectors":sorted(blocked),"full_closure_proven":False}),flush=True)
    finally:
        lock.unlink()

if __name__=="__main__":main()
