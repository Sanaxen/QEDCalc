"""Native08: direct packed transactions; Python holds no pivot matrix."""
import argparse,ctypes,hashlib,itertools,json,os,shutil,subprocess,tempfile,time
from pathlib import Path
from examples import three_loop_vp05_native_boundary_shell as prev
n=prev.n;b=prev.b;v=prev.v
ROOT=n.BASE/"output"/"vp05_independent_ibp_native08"
OBS={69:(135000,89345,59376749),196:(65000,52538,57204542),200:(105000,78380,53615833)}
CAP=120000000
GB=10**9

def header(path,checked=True):
    if path.is_symlink() or not path.is_file():raise RuntimeError("Checkpoint path")
    size=path.stat().st_size
    h=hashlib.sha256()
    with path.open("rb") as f:
        if f.readline()!=b"VP05PACK4\n":raise RuntimeError("Magic")
        line=f.readline(1048576)
        obj=json.loads(line)
        cursor,rank,terms,keys=(obj[k] for k in ("cursor","rank","terms","keys"))
        if not 0<=rank<=cursor or not 0<=keys<=terms<=CAP:raise RuntimeError("Header counts")
        end=f.tell()+10*keys+12*rank+8*terms
        if size!=end+(32 if checked else 0):raise RuntimeError("Checkpoint size")
        f.seek(0);remaining=end
        while remaining:
            raw=f.read(min(4*1024**2,remaining))
            if not raw:raise RuntimeError("Truncated checkpoint")
            h.update(raw);remaining-=len(raw)
        if checked and f.read(32)!=h.digest():raise RuntimeError("Checkpoint checksum")
    return obj,h.digest()

def host_guard(paths,reserve=0):
    for path in paths:
        free=shutil.disk_usage(path).free
        if free<50*GB+reserve:raise RuntimeError("Disk reserve guard: "+str(path))
        if free<100*GB+reserve:print("VP05_NATIVE08_DISK_WARNING "+str(path),flush=True)
    if os.name=="nt":
        class M(ctypes.Structure):
            _fields_=[("length",ctypes.c_ulong),("load",ctypes.c_ulong)]+[(x,ctypes.c_ulonglong) for x in ("total","available","total_page","available_page","total_virtual","available_virtual","extended")]
        m=M();m.length=ctypes.sizeof(m)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):raise RuntimeError("Host memory query")
        if m.available<8*1024**3:print("VP05_NATIVE08_HOST_RAM_WARNING available="+str(m.available),flush=True)
        if m.available_page<512*1024**2:raise RuntimeError("Host critical commit reserve")
        return m.available
    return None

def run_native(cmd,paths,deadline,reserve):
    with subprocess.Popen(cmd) as proc:
        try:
            while proc.poll() is None:
                host_guard(paths,reserve)
                if time.monotonic()>=deadline:raise TimeoutError("Time budget")
                time.sleep(5)
            if proc.returncode:raise RuntimeError("Native exit "+str(proc.returncode))
        except BaseException:
            if proc.poll() is None:
                import re
                subprocess.run(["wsl","--exec","pkill","-f","^"+re.escape(cmd[2])+" "],check=False,timeout=15)
                if proc.poll() is None:proc.kill()
            raise

def job(sec,kernel,exe,work,deadline,batch,paths,cap):
    source=prev.ROOT/f"sec{sec}_s5_p0.bin"
    original,_=header(source)
    if original["meta"]!=prev.meta(sec,5,0,"empty") or tuple(original[k] for k in ("cursor","rank","terms"))!=OBS[sec]:raise RuntimeError("Native07 source scope")
    digest=n.sha(source)
    meta={**b.meta(sec,5,0),"native_batch":8,"source_sha256":digest}
    path=ROOT/source.name
    if path.exists():
        state,_=header(path)
        if state["meta"]!=meta or not OBS[sec][0]<=state["cursor"]<=b.c.expected(5):raise RuntimeError("Resume scope")
    else:state=original
    p,z,d=b.c.old.POINTS[0];end=b.c.expected(5)
    ev={ij:[(b.c.old.evaluate(x,p,z),tuple(b.c.old.evaluate(y,p,z) for y in cs)) for x,cs in entries] for ij,entries in kernel.items()}
    cursor=state["cursor"];iterator=itertools.islice(b.c.rows(sec,5),cursor,None)
    v.log("VP05_NATIVE08_RESUME",sector=sec,rows=cursor,rank=state["rank"],terms=state["terms"],source_sha256=digest)
    reason=None
    while cursor<end and time.monotonic()<deadline:
        stop=min(cursor+batch,end)
        inp=work/"raw.in";out=work/"packed.payload";mf=work/"meta.json"
        try:
            host_guard(paths,8*cap+GB)
            mf.write_text(json.dumps(meta,separators=(",",":")),encoding="ascii")
            with inp.open("xb") as f:
                count=0
                for ex,j,k in itertools.islice(iterator,stop-cursor):
                    raw=b.c.old.row(ex,ev[j,k],j,k,d)
                    n.write_row(f,((b.c.key(key),val%p) for key,val in raw.items() if val%p));count+=1
                if count!=stop-cursor:raise RuntimeError("Row cursor")
            current=path if path.exists() else source
            before,_=header(current)
            if before!=state:raise RuntimeError("Current checkpoint changed")
            v.log("VP05_NATIVE08_BATCH",sector=sec,start=cursor,stop=stop)
            cmd=["wsl","--exec",n.wslpath(exe),n.wslpath(current),n.wslpath(inp),n.wslpath(out),n.wslpath(mf),str(p),str(cursor),str(state["rank"]),str(state["keys"]),str(state["terms"]),str(stop),str(cap)]
            run_native(cmd,paths,min(deadline,time.monotonic()+1560),8*cap+GB)
            new,checksum=header(out,False)
            if new["meta"]!=meta or new["cursor"]!=stop or not state["rank"]<=new["rank"]<=state["rank"]+stop-cursor or not state["terms"]<=new["terms"]<=cap:raise RuntimeError("Output scope")
            with out.open("ab") as f:f.write(checksum);f.flush();os.fsync(f.fileno())
            if header(out)[0]!=new or n.sha(source)!=digest:raise RuntimeError("Checkpoint/source verification")
            os.replace(out,path);state=new;cursor=stop
            v.log("VP05_NATIVE08_SAVED",sector=sec,rows=cursor,rank=state["rank"],terms=state["terms"])
        except (RuntimeError,TimeoutError) as exc:
            if str(exc).startswith(("Native exit ","Disk reserve guard","Host critical commit reserve","Time budget")):reason=str(exc);break
            raise
        finally:
            inp.unlink(missing_ok=True);out.unlink(missing_ok=True);mf.unlink(missing_ok=True)
    if n.sha(source)!=digest:raise RuntimeError("Source changed")
    result={"sector":sec,"rows":cursor,"expected":end,"rank":state["rank"],"terms":state["terms"],"complete":cursor==end,"reason":reason}
    v.log("VP05_NATIVE08_JOB",**result)
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);ap.add_argument("--batch-rows",type=int,default=5000);ap.add_argument("--term-cap",type=int,default=CAP);ap.add_argument("--swap-volume",type=Path,default=None)
    args=ap.parse_args()
    if not 0<args.hours<=12 or not 64<=args.batch_rows<=5000 or not 60000000<=args.term_cap<=CAP:ap.error("Invalid scope")
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    deadline=time.monotonic()+args.hours*3600
    results=[]
    try:
        for root in (prev.ROOT,b.ROOT,b.a.ROOT,b.c.ROOT,n.ROOT,v.ROOT,prev.prev.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        paths=[ROOT, args.swap_volume or Path(os.environ.get("SystemDrive","C:")+"/")]
        host_guard(paths)
        kernel=b.c.old.build_kernel(b.c.old.build_family_spec("VP05_full").propagators)
        if b.c.old.digest(kernel)!=b.c.PIN:raise RuntimeError("Kernel differs")
        with tempfile.TemporaryDirectory(prefix="native08_",dir=ROOT) as folder:
            work=Path(folder);exe=work/"native"
            subprocess.run(["wsl","--exec","g++","-std=c++17","-O3","-Wall","-Wextra",n.wslpath(n.BASE/"examples"/"vp05_native_packed.cpp"),"-o",n.wslpath(exe)],check=True,timeout=120)
            for sec in (69,196,200):
                if time.monotonic()>=deadline:break
                results.append(job(sec,kernel,exe,work,deadline,args.batch_rows,paths,args.term_cap))
        v.log("VP05_NATIVE08_NOT_CLOSURE",results=results,full_closure_proven=False)
    finally:lock.unlink()
if __name__=="__main__":main()
