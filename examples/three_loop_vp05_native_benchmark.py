"""Read-only packed04 benchmark; never promotes or updates a checkpoint."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import time
from examples import three_loop_vp05_packed_ibp as b

MAGIC=0x31425056
P=1000003
BASE=b.c.old.ROOT
ROOT=BASE/"output"/"vp05_native_benchmark01"

def wslpath(path):
    return subprocess.check_output(["wsl","--exec","wslpath","-a",path.resolve().as_posix()],text=True,timeout=30).strip()

def write_row(f,items):
    items=list(items)
    f.write(struct.pack("<I",len(items)))
    for k,v in items:
        f.write(k.to_bytes(10,"little")+struct.pack("<I",v))

def exact(f,n):
    v=f.read(n)
    if len(v)!=n:raise RuntimeError("Truncated native result")
    return v

def read_row(f):
    n,=struct.unpack("<I",exact(f,4))
    if n>b.FILL:raise RuntimeError("Native output fill")
    r={}
    for _ in range(n):
        k=int.from_bytes(exact(f,10),"little")
        v,=struct.unpack("<I",exact(f,4))
        if k in r or not 0<v<P:raise RuntimeError("Native output term")
        r[k]=v
    return r

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def compare(exe,work,store,rows,label):
    inp=work/(label+".in");out=work/(label+".out")
    t=time.monotonic()
    with inp.open("xb") as f:
        f.write(struct.pack("<IIII",MAGIC,P,len(store.piv),len(rows)))
        for j,lead in enumerate(store.piv):
            if j%256==0:b.a.memory()
            write_row(f,store.items(lead))
        for index,raw in rows:
            write_row(f,((b.c.key(k),v%P) for k,v in raw.items() if v%P))
    export_s=time.monotonic()-t
    expected=[];t=time.monotonic()
    deadline=t+1500
    for index,raw in rows:
        b.a.memory()
        if time.monotonic()>=deadline:raise TimeoutError("Python benchmark budget")
        lead,v=b.reduce(raw,store,P,b.CAP,deadline)
        if lead is not None:store.add(index,lead,v.items())
        expected.append((v or {},len(store.piv),store.terms))
    py_s=time.monotonic()-t
    t=time.monotonic()
    cmd=["wsl","--exec",wslpath(exe),wslpath(inp),wslpath(out)]
    peak_host=0
    with subprocess.Popen(cmd) as proc:
        try:
            while proc.poll() is None:
                total,available=b.a.memory()
                peak_host=max(peak_host,(total-available)/b.a.GIB)
                if time.monotonic()-t>1560:raise TimeoutError("Native process budget")
                time.sleep(1)
            if proc.returncode:raise RuntimeError("Native exit "+str(proc.returncode))
        except BaseException:
            # Terminate the specific Linux executable, never the whole WSL VM.
            try:
                subprocess.run(["wsl","--exec","pkill","-f","^"+re.escape(cmd[2])+" "],timeout=15,check=False)
            finally:
                if proc.poll() is None:proc.kill()
            raise
    native_total=time.monotonic()-t
    with out.open("rb") as f:
        if struct.unpack("<II",exact(f,8))!=(MAGIC,len(rows)):raise RuntimeError("Native output header")
        for (index,_),e in zip(rows,expected):
            v=read_row(f);rank,terms=struct.unpack("<IQ",exact(f,12))
            if (v,rank,terms)!=e:raise RuntimeError("Native mismatch at source index "+str(index))
        ns,ram,swap=struct.unpack("<QQQ",exact(f,24))
        if f.read(1):raise RuntimeError("Trailing native result")
    print("VP05_NATIVE_COMPARE "+json.dumps({"label":label,"rows":len(rows),"all_rows_equal":True,"rank":len(store.piv),"terms":store.terms,"python_reduce_s":py_s,"native_reduce_and_output_s":ns/1e9,"native_process_s":native_total,"export_s":export_s,"peak_wsl_ram_gib":ram/1048576,"peak_wsl_swap_gib":swap/1048576,"peak_windows_ram_gib":peak_host}),flush=True)

def synthetic(exe,work):
    # Raw exponents exercise the actual packed key codec, including >64-bit keys.
    ex=[(1,1,1,0,0,0,0,0,0,0,0,0),(2,1,1,0,0,0,0,0,0,0,0,0),(1,1,1,-1,0,0,0,0,0,0,0,0)]
    if max(map(b.c.key,ex))<=2**64:raise RuntimeError("Synthetic key scope")
    x,y,z=ex
    rows=[(0,{x:2,y:3}),(1,{x:4,y:6}),(2,{x:-1,z:7}),(3,{y:1,z:2}),(4,{})]
    compare(exe,work,b.Packed(),rows,"synthetic")
    bad=work/"bad.in";bad.write_bytes(b"bad")
    proc=subprocess.run(["wsl","--exec",wslpath(exe),wslpath(bad),wslpath(work/"bad.out")],timeout=30,capture_output=True,text=True)
    if proc.returncode!=1 or proc.stderr.strip()!="truncated input":raise RuntimeError("Unexpected malformed-input result: "+proc.stderr)
    print("VP05_NATIVE_NEGATIVE_TEST_PASS",flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--rows",type=int,default=64)
    parser.add_argument("--synthetic-only",action="store_true")
    args=parser.parse_args()
    if not 1<=args.rows<=301:parser.error("rows must be 1..301")
    ROOT.mkdir(exist_ok=True)
    lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    try:
        for root in (b.ROOT,b.a.ROOT,b.c.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Existing engine lock")
        b.a.memory()
        if shutil.disk_usage(ROOT).free<4*b.a.GIB:raise RuntimeError("Benchmark disk reserve")
        with tempfile.TemporaryDirectory(prefix="compare_",dir=ROOT) as folder:
            work=Path(folder);exe=work/"native"
            t=time.monotonic()
            subprocess.run(["wsl","--exec","g++","-std=c++17","-O3","-Wall","-Wextra",wslpath(BASE/"examples"/"vp05_native_benchmark.cpp"),"-o",wslpath(exe)],check=True,timeout=120)
            print("VP05_NATIVE_BUILD "+json.dumps({"elapsed_s":time.monotonic()-t}),flush=True)
            synthetic(exe,work)
            if not args.synthetic_only:
                path=b.ROOT/"sec196_s4_p0.bin"
                digest=sha(path)
                try:
                    cursor,store,peak,elapsed=b.load(path,b.meta(196,4,0),P)
                    if (cursor,len(store.piv),store.terms)!=(73949,46175,37179224):raise RuntimeError("Packed04 observed state mismatch")
                    kernel=b.c.old.build_kernel(b.c.old.build_family_spec("VP05_full").propagators)
                    if b.c.old.digest(kernel)!=b.c.PIN:raise RuntimeError("Kernel differs")
                    p,z,d=b.c.old.POINTS[0]
                    if p!=P:raise RuntimeError("Prime differs")
                    ev={ij:[(b.c.old.evaluate(x,p,z),tuple(b.c.old.evaluate(y,p,z) for y in cs)) for x,cs in entries] for ij,entries in kernel.items()}
                    rows=[]
                    for i,(ex,j,k) in enumerate(b.c.rows(196,4)):
                        if i<cursor:continue
                        rows.append((i,b.c.old.row(ex,ev[j,k],j,k,d)))
                        if len(rows)==args.rows:break
                    if len(rows)!=args.rows:raise RuntimeError("Insufficient source rows")
                    compare(exe,work,store,rows,"sector196_s4_p0")
                finally:
                    if sha(path)!=digest:raise RuntimeError("Source checkpoint changed")
            print("VP05_NATIVE_BENCHMARK_PASS_NOT_CLOSURE "+json.dumps({"synthetic_only":args.synthetic_only,"production_modified":False}),flush=True)
    finally:lock.unlink()

if __name__=="__main__":main()
