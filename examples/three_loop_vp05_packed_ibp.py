"""Compressed immutable pivot rows, preserving adaptive03 mathematical order.

Intern full (up to 76-bit) integral keys into uint32 IDs. Coefficients are
uint32. Working row remains a dict of original keys so max() is unchanged.
Binary records are little endian, checksummed; old JSON read one pivot at a time.
"""
import argparse, hashlib, json, os, struct, sys, time, shutil
from array import array
from examples import three_loop_vp05_adaptive_ibp as a
c=a.c
ROOT=c.old.ROOT/"output"/"vp05_independent_ibp_packed04"
CAP=60000000
FILL=c.FILL
OBS={69:(64998,40049,11996933),196:(32813,25011,11998825),200:(51110,37145,11999831)}
RANK3={69:15115,196:15908,200:15908}
MAGIC=b"VP05PACK4\n"

class Packed:
    def __init__(self):
        if array("I").itemsize!=4:raise RuntimeError("uint32 unavailable")
        self.ids={};self.keys=[];self.piv={};self.selected=[];self.terms=0
    def add(self,index,lead,items):
        ids=array("I");values=array("I")
        for k,v in items:
            n=self.ids.get(k)
            if n is None:
                n=len(self.keys);self.ids[k]=n;self.keys.append(k)
            ids.append(n);values.append(v)
        self.piv[lead]=(ids,values);self.selected.append(index);self.terms+=len(ids)
    def items(self,lead):
        ids,values=self.piv[lead]
        return zip((self.keys[n] for n in ids),values)

def reduce(raw,store,p,cap,deadline=float("inf")):
    cur={c.key(k):v%p for k,v in raw.items() if v%p}
    steps=0
    while cur:
        if len(cur)>FILL:raise RuntimeError("Fill cap")
        lead=max(cur)
        if lead not in store.piv:
            if store.terms+len(cur)>cap:raise RuntimeError("Stored term cap")
            inv=pow(cur[lead],-1,p)
            return lead,{k:v*inv%p for k,v in cur.items()}
        f=cur[lead]
        for k,v in store.items(lead):
            x=(cur.get(k,0)-f*v)%p
            if x:cur[k]=x
            else:cur.pop(k,None)
        steps+=1
        if steps%256==0:
            if time.monotonic()>=deadline:raise TimeoutError("Time budget")
            a.memory()
    return None,None

def meta(sec,s,point):
    return {**a.meta(sec,s,point),"version":4,"representation":"interned-u32-pairs"}

def validate_row(index,lead,items,p,store,cursor):
    v=dict(items)
    if (not v or len(v)!=len(items) or len(v)>FILL or lead in store.piv or max(v)!=lead or v.get(lead)!=1
        or any(not 0<x<p or c.key(c.decode(k))!=k for k,x in v.items())
        or not 0<=index<cursor or (store.selected and index<=store.selected[-1])):
        raise RuntimeError("Invalid pivot")
    store.add(index,lead,items)

def read_legacy(sec,s,point,p):
    path=a.state_path(sec,s,point)
    if not path.exists():
        if s<=3 or (s==4 and point==0):raise RuntimeError("Required prior checkpoint missing")
        return 0,Packed(),0,0
    if path.is_symlink() or path.stat().st_size>a.MAX_FILE:raise RuntimeError("Legacy size/link")
    h=hashlib.sha256();store=Packed()
    with path.open("rb") as f:
        raw=f.readline(1024*1024);h.update(raw);head=json.loads(raw)
        if head["meta"]!=a.meta(sec,s,point) or not 0<=head["rank"]<=head["cursor"]<=c.expected(s) or not 0<=head["stored"]<=head["cap"]<=a.MAX_CAP:
            raise RuntimeError("Legacy metadata")
        for i in range(head["rank"]):
            if i%1000==0:a.memory()
            raw=f.readline(4*1024*1024);h.update(raw)
            index,lead,items=json.loads(raw)
            validate_row(index,lead,items,p,store,head["cursor"])
            if store.terms>head["stored"]:raise RuntimeError("Legacy term count")
        if f.readline().strip()!=h.hexdigest().encode() or f.read(1) or store.terms!=head["stored"]:
            raise RuntimeError("Legacy checksum")
    if s==4 and point==0:
        if (head["cursor"],len(store.piv),store.terms)!=OBS[sec]:raise RuntimeError("Prior s4 log mismatch")
    elif s<=3:
        rank=a.RANKS[sec] if s==2 else RANK3[sec]
        if head["cursor"]!=c.expected(s) or len(store.piv)!=rank:raise RuntimeError("Prior completed rank mismatch")
    else:raise RuntimeError("Unexpected legacy checkpoint")
    return head["cursor"],store,head["peak"],head["elapsed"]

def bytes32(v):
    if sys.byteorder=="little":return v.tobytes()
    b=array("I",v);b.byteswap();return b.tobytes()

def save(path,m,cursor,store,peak,elapsed):
    tmp=path.with_suffix(".tmp")
    if shutil.disk_usage(path.parent).free<2*a.GIB+8*store.terms:raise RuntimeError("Checkpoint disk reserve")
    h=hashlib.sha256()
    with tmp.open("xb") as f:
        def put(b):h.update(b);f.write(b)
        put(MAGIC)
        put(json.dumps({"meta":m,"cursor":cursor,"rank":len(store.piv),"terms":store.terms,"keys":len(store.keys),"peak":peak,"elapsed":elapsed},separators=(",",":")).encode()+b"\n")
        for k in store.keys:put(k.to_bytes(10,"little"))
        for index,(lead,(ids,values)) in zip(store.selected,store.piv.items()):
            put(struct.pack("<III",index,store.ids[lead],len(ids)))
            put(bytes32(ids));put(bytes32(values))
        f.write(h.digest());f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def load(path,m,p):
    if path.is_symlink() or path.stat().st_size>2*a.GIB:raise RuntimeError("Packed size/link")
    h=hashlib.sha256();store=Packed()
    with path.open("rb") as f:
        def get(n):
            b=f.read(n)
            if len(b)!=n:raise RuntimeError("Truncated checkpoint")
            h.update(b);return b
        if get(len(MAGIC))!=MAGIC:raise RuntimeError("Magic")
        raw=f.readline(1024*1024);h.update(raw);head=json.loads(raw)
        if head["meta"]!=m or not 0<=head["rank"]<=head["cursor"]<=c.expected(m["shell"]) or not 0<=head["keys"]<=head["terms"]<=CAP:raise RuntimeError("Packed metadata")
        for n in range(head["keys"]):
            if n%10000==0:a.memory()
            k=int.from_bytes(get(10),"little")
            if k in store.ids or c.key(c.decode(k))!=k:raise RuntimeError("Integral key")
            store.ids[k]=n;store.keys.append(k)
        for i in range(head["rank"]):
            if i%1000==0:a.memory()
            index,leadid,n=struct.unpack("<III",get(12))
            if not 0<n<=FILL or leadid>=len(store.keys) or store.terms+n>head["terms"]:raise RuntimeError("Packed row header")
            ids=array("I");values=array("I");ids.frombytes(get(4*n));values.frombytes(get(4*n))
            if sys.byteorder!="little":ids.byteswap();values.byteswap()
            if any(k>=len(store.keys) for k in ids) or len(set(ids))!=n or any(not 0<v<p for v in values):raise RuntimeError("Packed row content")
            lead=store.keys[leadid]
            if (lead in store.piv or max(store.keys[k] for k in ids)!=lead or leadid not in ids or values[ids.index(leadid)]!=1
                or not 0<=index<head["cursor"] or (store.selected and index<=store.selected[-1])):raise RuntimeError("Packed pivot")
            store.piv[lead]=(ids,values);store.selected.append(index);store.terms+=n
        if f.read(32)!=h.digest() or f.read(1) or store.terms!=head["terms"]:raise RuntimeError("Packed checksum")
    return head["cursor"],store,head["peak"],head["elapsed"]

def job(sec,s,point,kernel,deadline):
    p,z,d=c.old.POINTS[point];m=meta(sec,s,point)
    path=ROOT/f"sec{sec}_s{s}_p{point}.bin"
    if path.with_suffix(".tmp").exists():raise RuntimeError("Stale temporary checkpoint")
    if path.exists():cursor,store,peak,elapsed=load(path,m,p)
    else:
        cursor,store,peak,elapsed=read_legacy(sec,s,point,p)
        if cursor:
            save(path,m,cursor,store,peak,elapsed)
            print("VP05_PACKED_MIGRATED "+json.dumps({"sector":sec,"shell":s,"point":point,"rows":cursor,"rank":len(store.piv),"terms":store.terms}),flush=True)
    start=time.monotonic();last_save=cursor;last_time=start;reason=None
    ev={ij:[(c.old.evaluate(x,p,z),tuple(c.old.evaluate(y,p,z) for y in cs)) for x,cs in entries] for ij,entries in kernel.items()}
    try:
        for index,(ex,i,j) in enumerate(c.rows(sec,s)):
            if index<cursor:continue
            if index%15==0:
                total,available=a.memory();peak=max(peak,(total-available)/a.GIB)
            if time.monotonic()>=deadline:raise TimeoutError("Time budget")
            lead,v=reduce(c.old.row(ex,ev[i,j],i,j,d),store,p,CAP,deadline)
            if lead is not None:store.add(index,lead,v.items())
            cursor=index+1
            if cursor-last_save>=5000 or time.monotonic()-last_time>=300:
                save(path,m,cursor,store,peak,elapsed+time.monotonic()-start)
                last_save=cursor;last_time=time.monotonic()
                print("VP05_PACKED_PROGRESS "+json.dumps({"sector":sec,"shell":s,"point":point,"rows":cursor,"terms":store.terms,"peak_host_ram_gib":peak}),flush=True)
    except (RuntimeError,TimeoutError,KeyboardInterrupt) as exc:
        reason=str(exc) or "User interrupt"
    if cursor!=last_save or not path.exists():save(path,m,cursor,store,peak,elapsed+time.monotonic()-start)
    result={"sector":sec,"shell":s,"point":point,"rows":cursor,"expected":c.expected(s),"rank":len(store.piv),"terms":store.terms,"packed_payload_bytes":8*store.terms,"complete":cursor==c.expected(s),"reason":reason,"peak_host_ram_gib":peak,"elapsed_s":elapsed+time.monotonic()-start}
    print("VP05_PACKED_JOB "+json.dumps(result),flush=True)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--smax",type=int,default=6)
    parser.add_argument("--hours",type=float,default=12)
    args=parser.parse_args()
    if not 4<=args.smax<=6 or not 0<args.hours<=12:parser.error("Invalid scope")
    a.memory()
    if any((p/"running.lock").exists() for p in (a.ROOT,c.ROOT)):raise RuntimeError("Previous engine lock")
    kernel=c.old.build_kernel(c.old.build_family_spec("VP05_full").propagators)
    if c.old.digest(kernel)!=c.PIN:raise RuntimeError("Kernel differs")
    ROOT.mkdir(exist_ok=True)
    lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    deadline=time.monotonic()+args.hours*3600;results=[];blocked=set()
    try:
        # Earlier completed s2/s3 are preserved and not duplicated.
        for s in range(4,args.smax+1):
            for sec in c.old.SECTORS:
                if sec in blocked or time.monotonic()>=deadline:continue
                pair=[]
                for point in range(2):
                    r=job(sec,s,point,kernel,deadline);pair.append(r);results.append(r)
                    if not r["complete"]:blocked.add(sec);break
                if len(pair)==2 and all(r["complete"] for r in pair) and pair[0]["rank"]!=pair[1]["rank"]:raise RuntimeError("Rank disagreement")
                if any(r["reason"]=="User interrupt" for r in pair):return
        print("VP05_PACKED_IBP_NOT_CLOSURE "+json.dumps({"results":results,"blocked_sectors":sorted(blocked),"full_closure_proven":False}),flush=True)
    finally:lock.unlink()

if __name__=="__main__":main()
