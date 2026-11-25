"""Compact, resumable finite-field IBP shell experiment (not closure).

Static complexity ordering eliminates harder integrals first. Packed integer
keys are collision-free for the supported seed envelope. Process one point
at a time; save pivots and row cursor atomically, including on guarded stop.
"""
import argparse, hashlib, json, math, os, time
from pathlib import Path
from examples import three_loop_vp05_independent_ibp as old

VERSION=1
CAP=1500000
FILL=20000
PIN="09244783a9ce300ffbdd6b3e4c0f9eb216295eda9f7237b5c8e6ed513c85624b"
KNOWN={69:(127,959,4363),196:(127,987,None),200:(127,987,4553)}
ROOT=old.ROOT/"output"/"vp05_independent_ibp_compact02"
MASK=(1<<60)-1

def key(a):
    if len(a)!=12 or any(x<-16 or x>15 for x in a):raise ValueError("Exponent out of range")
    code=0
    for x in a:code=(code<<5)|(x+16)
    # High-complexity first via max(); stable static order independent of row.
    r=sum(max(0,x) for x in a)
    s=sum(max(0,-x) for x in a)
    t=sum(x>0 for x in a)
    return (((t*64+r)*64+s)<<60)|code

def decode(k):
    a=[]
    for i in range(12):
        a.append((k&31)-16);k>>=5
    return tuple(reversed(a))

def reduce_row(row,piv,p,stored):
    cur={key(a):c%p for a,c in row.items() if c%p}
    if len(cur)>FILL:raise RuntimeError("Fill cap")
    while cur:
        lead=max(cur)
        if lead not in piv:
            if stored+len(cur)>CAP:raise RuntimeError("Stored term cap")
            inv=pow(cur[lead],-1,p)
            return lead,{k:c*inv%p for k,c in cur.items()}
        c=cur[lead]
        for k,v in piv[lead].items():
            x=(cur.get(k,0)-c*v)%p
            if x:cur[k]=x
            else:cur.pop(k,None)
        if len(cur)>FILL:raise RuntimeError("Fill cap")
    return None,None

def rows(sec,s):
    for a in old.seeds(sec,s):
        if sum(-x for x in a if x<0)==s:
            for i in range(3):
                for j in range(5):yield a,i,j

def expected(s):
    return 150*math.comb(s+8,8)

def ram():
    old.memory_guard()
    if os.name=="nt":
        import ctypes
        class M(ctypes.Structure):
            _fields_=[("length",ctypes.c_ulong),("load",ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ("total","available","total_page","available_page","total_virtual","available_virtual","extended")]
        m=M();m.length=ctypes.sizeof(m)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):raise RuntimeError("RAM measurement")
        return (m.total-m.available)/1024**3
    m=dict((x.split(":")[0],int(x.split()[1])) for x in Path("/proc/meminfo").read_text().splitlines() if x.startswith(("MemTotal:","MemAvailable:")))
    return (m["MemTotal"]-m["MemAvailable"])/1024**2

def save(path,meta,cursor,piv,selected,stored,peak,elapsed):
    payload={"meta":meta,"cursor":cursor,"pivots":[[k,list(v.items())] for k,v in piv.items()],
             "selected":selected,"stored":stored,"peak_host_ram_gib":peak,"elapsed_s":elapsed}
    raw=json.dumps(payload,separators=(",",":")).encode()
    tmp=path.with_suffix(".tmp")
    with tmp.open("xb") as f:
        f.write(hashlib.sha256(raw).hexdigest().encode()+b"\n");f.write(raw);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def load(path,meta,p):
    if path.is_symlink() or path.stat().st_size>160*1024**2:raise RuntimeError("Checkpoint size/link")
    with path.open("rb") as f:
        h=f.readline().strip();raw=f.read()
    if hashlib.sha256(raw).hexdigest().encode()!=h:raise RuntimeError("Checkpoint checksum")
    obj=json.loads(raw)
    if obj["meta"]!=meta:raise RuntimeError("Checkpoint scope")
    piv={}
    for lead,items in obj["pivots"]:
        v=dict(items)
        if lead in piv or len(v)!=len(items) or not v or max(v)!=lead or v.get(lead)!=1 or any(not 0<c<p or key(decode(k))!=k for k,c in v.items()):
            raise RuntimeError("Invalid pivot")
        piv[lead]=v
    selected=obj["selected"];cursor=obj["cursor"];stored=sum(map(len,piv.values()))
    if not 0<=cursor<=expected(meta["shell"]) or len(selected)!=len(piv) or selected!=sorted(set(selected)) or any(not 0<=i<cursor for i in selected) or stored!=obj["stored"] or stored>CAP:
        raise RuntimeError("Checkpoint invariant")
    return cursor,piv,selected,stored,obj["peak_host_ram_gib"],obj["elapsed_s"]

def job(sec,s,point,kernel,deadline):
    p,z,d=old.POINTS[point]
    meta={"version":VERSION,"sector":sec,"shell":s,"point":list(old.POINTS[point]),"kernel_sha256":PIN,"ordering":"t-r-s-packed-desc","cap":CAP,"fill":FILL}
    path=ROOT/f"sec{sec}_s{s}_p{point}.checkpoint"
    if path.with_suffix(".tmp").exists():raise RuntimeError("Interrupted checkpoint write; preserve temporary file")
    cursor,piv,selected,stored,peak,elapsed=load(path,meta,p) if path.exists() else (0,{},[],0,0,0)
    start=time.monotonic()
    ev={ij:[(old.evaluate(c,p,z),tuple(old.evaluate(x,p,z) for x in cs)) for c,cs in entries] for ij,entries in kernel.items()}
    reason=None
    last_save=cursor
    try:
        for index,(a,i,j) in enumerate(rows(sec,s)):
            if index<cursor:continue
            if index%15==0:
                peak=max(peak,ram())
            if time.monotonic()>=deadline:raise TimeoutError("Time budget")
            lead,v=reduce_row(old.row(a,ev[i,j],i,j,d),piv,p,stored)
            if lead is not None:
                piv[lead]=v;stored+=len(v);selected.append(index)
            cursor=index+1
            if cursor-last_save>=1000:
                save(path,meta,cursor,piv,selected,stored,peak,elapsed+time.monotonic()-start);last_save=cursor
    except (RuntimeError,TimeoutError,KeyboardInterrupt) as exc:
        reason=str(exc) or "User interrupt"
    if cursor!=last_save or not path.exists():
        save(path,meta,cursor,piv,selected,stored,peak,elapsed+time.monotonic()-start)
    complete=cursor==expected(s)
    rank=len(piv)
    known=KNOWN[sec][s] if s<3 else None
    if complete and known is not None and rank!=known:raise RuntimeError("Rank regression")
    result={"sector":sec,"shell":s,"point":point,"rows":cursor,"expected":expected(s),"rank":rank,"terms":stored,"complete":complete,"reason":reason,"peak_host_ram_gib":peak,"elapsed_s":elapsed+time.monotonic()-start,"known_rank":known}
    print("VP05_COMPACT_JOB "+json.dumps(result),flush=True)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--smax",type=int,default=6)
    parser.add_argument("--hours",type=float,default=12)
    a=parser.parse_args()
    if not 2<=a.smax<=6 or not 0<a.hours<=12:parser.error("Invalid scope")
    kernel=old.build_kernel(old.build_family_spec("VP05_full").propagators)
    if old.digest(kernel)!=PIN:raise RuntimeError("Kernel differs")
    ROOT.mkdir(exist_ok=True)
    # Exclusive lock: interruption leaves lock requiring review, not overwrite.
    lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    deadline=time.monotonic()+a.hours*3600
    results=[]
    blocked=set()
    try:
        # First benchmark s2 on all three sectors; s0/s1 results remain intact.
        for s in range(2,a.smax+1):
            for sec in old.SECTORS:
                if sec in blocked or time.monotonic()>=deadline:continue
                pair=[]
                for point in range(2):
                    r=job(sec,s,point,kernel,deadline);results.append(r);pair.append(r)
                    if not r["complete"]:blocked.add(sec);break
                if len(pair)==2 and all(r["complete"] for r in pair) and pair[0]["rank"]!=pair[1]["rank"]:
                    raise RuntimeError("Finite-field rank disagreement")
        print("VP05_COMPACT_IBP_NOT_CLOSURE "+json.dumps({"results":results,"blocked_sectors":sorted(blocked),"full_closure_proven":False}),flush=True)
    finally:
        lock.unlink()

if __name__=="__main__":main()
