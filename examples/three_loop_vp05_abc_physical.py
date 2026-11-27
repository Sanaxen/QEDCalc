"""Bounded physical IBP row-space proof of the opaque-free ABC relation.

Only independently generated IBP rows; no Kira column decoding in reduction.
No analytic substitution, zero-sector assumption or candidate protection.
Modular membership selects a DAG, never constitutes the proof.
"""
import argparse
import os
import time
from collections import Counter
from pathlib import Path
from examples import three_loop_vp05_abc_boundary_scope as scope
from examples import three_loop_vp05_parent_exact as exact
from examples import three_loop_vp05_parent_exact_audit as audit
from examples import three_loop_vp05_sec77_exact_retry as retry

gap=exact.gap;n=exact.n;v=exact.v;p=exact.p;f=exact.f;old=exact.old;sp=exact.sp;q=exact.q;inv=exact.inv
ROOT=n.BASE/"output"/"vp05_abc_physical24"
SOURCE=scope.ROOT/"report_1795767387663077800.json"
SHA="a84768d8a61b83f798678bd2841899675387eddc1434fda2aa0ef0759779829f"
POINTS=(*old.POINTS,*retry.POINTS)
MAX_SEEDS=240
BATCH=24
MAX_ROUNDS=10

def trace_row(engine,row):
    cur=dict(row);free={};deps=[]
    while cur:
        engine.guard(cur)
        k=max(cur,key=f.e.b.c.key)
        if k in engine.piv:
            deps.append(k);engine.subtract(cur,engine.piv[k],cur[k])
        else:free[k]=cur.pop(k)
    return free,deps

def seed_ok(ex):
    mask=gap.sector(ex)
    return mask!=0 and mask&202==mask and q.scope(ex,8,5,3)

def select_seeds(residual,seen,kernel):
    counts=Counter()
    for k in residual:
        for ex,derivs in inv.inverse_seeds(k,kernel).items():
            if ex not in seen and seed_ok(ex):counts[ex]+=len(derivs)
    def order(k):
        return (-counts[k],sum(abs(x) for x in k),sum(-x for x in k if x<0),k)
    return sorted(counts,key=order)[:min(BATCH,MAX_SEEDS-len(seen))]

def make_proof(rows,sources,target,engine,point,direct,deadline):
    builder=retry.DiagnosticExact(rows,engine,point,deadline)
    deps=exact.dependency_order(engine.trace,direct)
    for k in deps:builder.build(k)
    rem={k:builder.coeff(x) for k,x in target.items()};mult=[]
    for k in direct:
        x=rem.get(k,builder.field.zero)
        if not x:raise RuntimeError("Exact target path diverged")
        builder.subtract(rem,builder.piv[k]["row"],x);mult.append([list(k),exact.expr(x)])
    if rem:raise RuntimeError("Exact relation remainder nonzero")
    cert=[]
    for k in deps:
        item=builder.piv[k]
        cert.append({"lead":list(k),"source":sources[item["source"]],
                     "divisor":exact.expr(item["divisor"]),
                     "dependencies":[[list(j),exact.expr(x)] for j,x in item["dependencies"]],
                     "row":exact.encoded(item["row"])})
    return {"status":"VP05_ABC_PHYSICAL_EXACT_RELATION",
            "source_sha256":SHA,"kernel_sha256":f.e.b.c.PIN,
            "target":p.encode(target),"trace_point":list(point),
            "pivots":cert,"target_dependencies":mult,"remainder":[],
            "full_closure_proven":False}

def verify(cert,target,kernel,deadline):
    if cert.get("status")!="VP05_ABC_PHYSICAL_EXACT_RELATION" or cert.get("source_sha256")!=SHA or cert.get("kernel_sha256")!=f.e.b.c.PIN or cert.get("target")!=p.encode(target) or cert.get("remainder")!=[] or tuple(cert["trace_point"]) not in POINTS:
        raise RuntimeError("Certificate scope")
    verifier=audit.Verifier(set(),deadline);available=set();regenerated={}
    def source(ref):
        ex=tuple(ref["seed"]);ij=tuple(ref["derivative"])
        if len(ex)!=12 or not seed_ok(ex) or ij not in kernel:raise RuntimeError("Physical source scope")
        key=(ex,ij)
        if key not in regenerated:
            raw=q.exact_row(ex,kernel[ij],*ij)
            if p.encode(raw)!=ref["row"]:raise RuntimeError("Physical source mismatch")
            regenerated[key]=raw
        return regenerated[key]
    for rec in cert["pivots"]:verifier.pivot(rec,source,available)
    rem={k:verifier.coeff(x) for k,x in target.items()}
    verifier.dependencies(rem,cert["target_dependencies"],available)
    if rem:raise RuntimeError("Independent exact relation replay failed")
    return len(regenerated)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        if n.sha(SOURCE)!=SHA:raise RuntimeError("ABC scope report SHA")
        prior=gap.read(SOURCE);relation=prior["combined_relation"]
        if prior["status"]!="VP05_ABC_BOUNDARY_SCOPE_NOT_CLOSURE" or relation["opaque_M_eliminated"] is not True or relation["exact_original_source_replay"] is not True:
            raise RuntimeError("Prior relation scope")
        pins={Path(k):d for k,d in prior["inputs"].items()};pins[SOURCE]=SHA
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input SHA")
        if relation["target_exponents"]!=[list(k) for k in gap.TARGETS]:raise RuntimeError("ABC exponents")
        raw=relation["coefficient_row"]
        if [k for k,x in raw]!=relation["target_keys"] or len(raw)!=3:raise RuntimeError("ABC key order")
        target={k:sp.cancel(sp.sympify(x,locals={"z":old.Z,"d":old.D})) for k,(_,x) in zip(gap.TARGETS,raw)}
        if any(not x or x.free_symbols-{old.Z,old.D} for x in target.values()):raise RuntimeError("ABC coefficient scope")
        manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        if manifest not in pins or not set(target)<=set(gap.indices(x) for x in gap.read(manifest)["candidate_masters"]):raise RuntimeError("Manifest")
        kernel=old.build_kernel(old.build_family_spec("VP05_full").propagators)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Physical kernel SHA")
        certpath=ROOT/"physical_relation.json"
        if certpath.exists():
            cert=gap.read(certpath);verified=verify(cert,target,kernel,deadline)
            if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
            v.log("VP05_ABC_PHYSICAL_EXACT_PROVEN_NOT_CLOSURE",original_rows_replayed=verified,sha256=n.sha(certpath),reused=True,full_closure_proven=False)
            return
        rows=[];sources=[];seen=set();checks=[]
        # Deterministic persisted seed schedules. Regenerate raw rows and
        # compare immutable checkpoints on restart; do not rerun Kira.
        schedule=list(gap.TARGETS)
        proven=False;verified=0;diagnostics=[]
        for rid in range(MAX_ROUNDS):
            if not schedule:break
            records=[]
            for ex in schedule:
                if ex in seen or not seed_ok(ex):raise RuntimeError("Seed scope")
                seen.add(ex);old.memory_guard()
                for ij,entries in sorted(kernel.items()):
                    if time.monotonic()>=deadline:raise TimeoutError("Physical row budget")
                    row=q.exact_row(ex,entries,*ij)
                    ref={"seed":list(ex),"derivative":list(ij),"row":p.encode(row)}
                    sources.append(ref);rows.append(row);records.append(ref)
            dest=ROOT/f"round{rid:02d}.json"
            c=scope.c
            c.save(dest,{"source_sha256":SHA,"kernel_sha256":f.e.b.c.PIN,"schedule":[list(k) for k in schedule],"rows":records})
            pins[dest]=n.sha(dest)
            residual=set();check=[]
            for point in POINTS:
                engine=retry.make_trace(rows,set(),point,deadline)
                free,direct=trace_row(engine,p.field_row(target,point))
                result={"point":list(point),"rank":len(engine.piv),"residual":[[list(k),x] for k,x in sorted(free.items())]}
                check.append(result)
                residual.update(free)
                if not free:
                    try:cert=make_proof(rows,sources,target,engine,point,direct,deadline)
                    except RuntimeError as exc:
                        if str(exc) not in (*retry.PATH_ERRORS,"Exact relation remainder nonzero"):raise
                        diagnostics.append({"point":list(point),"reason":str(exc)})
                        continue
                    verified=verify(cert,target,kernel,deadline)
                    c.save(certpath,cert);verified=verify(gap.read(certpath),target,kernel,deadline)
                    pins[certpath]=n.sha(certpath);proven=True
                    break
                del engine
            checks.append({"round":rid,"seeds":len(seen),"rows":len(rows),"points":check})
            v.log("VP05_ABC_PHYSICAL_ROUND",round=rid,seeds=len(seen),rows=len(rows),residual_counts=[len(x["residual"]) for x in check],exact_proven=proven)
            if proven or len(seen)>=MAX_SEEDS:break
            schedule=select_seeds(residual,seen,kernel)
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        status="VP05_ABC_PHYSICAL_EXACT_PROVEN_NOT_CLOSURE" if proven else "VP05_ABC_PHYSICAL_SEARCH_INCOMPLETE_NOT_PROOF"
        payload={"status":status,"inputs":{str(k):d for k,d in pins.items()},"checks":checks,
                 "target":p.encode(target),"exact_proven":proven,"original_rows_replayed":verified,
                 "diagnostics":diagnostics,"full_closure_proven":False,"registry_changed":False}
        report=ROOT/f"report_{time.time_ns()}.json";digest=scope.c.save(report,payload)
        v.log(status,seeds=len(seen),rows=len(rows),original_rows_replayed=verified,sha256=digest,report=report.name,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
