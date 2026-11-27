"""Diagnose and retry sector77 exact paths at alternative field points.

Preserve all earlier certificates. Fresh point traces are only hints; every
accepted identity is independently verified over QQ(z,d) and both old points.
"""
import argparse
import os
import time
from examples import three_loop_vp05_common_exact as m

c=m.c;p=m.p;f=m.f;a=m.a;old=m.old;sp=m.sp;gap=m.gap;n=m.n;v=m.v
exact=m.exact;residual=m.residual
ROOT=n.BASE/"output"/"vp05_sec77_exact_retry16"
SOURCE=m.ROOT/"partial_summary.json"
SHA="8eafc950bcd57ebfd97e868f7446bdecdbcebb8fc860287598b70fbbdc836560"
POINTS=((1000037,31,13),(1000039,53,29),(1000081,79,43))
PATH_ERRORS=("Exact pivot path diverged","Exact leading key differs","Exact target path diverged","Modular pivot replay mismatch")

class DiagnosticExact(exact.Exact):
    def __init__(self,*args):
        super().__init__(*args);self.failure=None
    def build(self,k):
        if k in self.piv:return
        self.failure=None
        try:super().build(k)
        except RuntimeError as exc:
            if str(exc) not in PATH_ERRORS:raise
            index,deps=self.engine.trace[k]
            row={j:self.coeff(x) for j,x in self.rows[index].items()}
            for j in deps:
                if j not in self.piv:break
                coeff=row.get(j,self.field.zero)
                if coeff:self.subtract(row,self.piv[j]["row"],coeff)
            lead=max((j for j in row if j not in self.engine.candidates),key=f.e.b.c.key,default=None)
            vals=[]
            if lead is not None:
                for pt in (self.point,*old.POINTS):
                    try:value=f.evaluate(row[lead].as_expr(),pt)
                    except (ValueError,ZeroDivisionError,TypeError):value=None
                    vals.append({"point":list(pt),"value":value})
            self.failure={"reason":str(exc),"trace_point":list(self.point),"source_index":index,
                          "modular_lead":list(k),"exact_lead":list(lead) if lead is not None else None,
                          "exact_lead_coefficient":exact.expr(row[lead]) if lead is not None else None,
                          "evaluations":vals,"dependencies":[list(j) for j in deps]}
            raise

def make_trace(rows,candidates,point,deadline):
    eng=exact.Trace(point[0],candidates,deadline)
    for i,row in enumerate(rows):
        if time.monotonic()>=deadline:raise TimeoutError("Trace budget")
        eng.insert_source(p.field_row(row,point),i)
    return eng

def make_certificate(builder,sources,target,direct,deps,rules,rule_data,point):
    for k in deps:builder.build(k)
    rem,multipliers=builder.target(target,direct)
    result=m.collapse(rem,rules,builder.field)
    cert=[]
    for k in deps:
        item=builder.piv[k]
        cert.append({"lead":list(k),"source":sources[item["source"]],"divisor":exact.expr(item["divisor"]),
                     "dependencies":[[list(j),exact.expr(x)] for j,x in item["dependencies"]],"row":exact.encoded(item["row"])})
    return {"source_sha256":m.SHA,"retry_source_sha256":SHA,"sector":77,"target":list(target),"trace_point":list(point),
            "pivots":cert,"target_dependencies":[[list(k),exact.expr(x)] for k,x in multipliers],
            "remainder_before_identity":exact.encoded(rem),"remainder":exact.encoded(result),
            "rules":rule_data,"full_closure_proven":False},result

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (m.ROOT,residual.ROOT,c.ROOT,c.audit.ROOT,c.audit.PROOFS,c.inv.ROOT,c.h.ROOT,p.ROOT,a.ROOT,f.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={SOURCE:SHA,m.SOURCE:m.SHA,residual.SOURCE:residual.SHA,c.AUDIT:c.SHA,
              a.PILOT:a.SHA,p.AUDIT:p.AUDIT_SHA,f.EVIDENCE:f.EVIDENCE_SHA}
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Evidence SHA")
        prior=gap.read(SOURCE);common=gap.read(residual.SOURCE);identity=gap.read(m.SOURCE)
        if prior["status"]!="VP05_COMMON_EXACT_NOT_CLOSURE" or prior["ready"]!=30 or prior["verified"]!=17:raise RuntimeError("Prior scope")
        prior77=next(x for x in prior["jobs"] if x["sector"]==77)
        pending={tuple(x["target"]) for x in prior77["deferred"]}
        if len(pending)!=13 or prior77["verified"]!=3 or any(x["reason"]!="Exact leading key differs" for x in prior77["deferred"]):raise RuntimeError("Deferred scope")
        extension=c.ROOT/"extension.json";pins[extension]=common["extension_sha256"]
        if n.sha(extension)!=pins[extension]:raise RuntimeError("Extension SHA")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[manifest]=n.sha(manifest)
        if common["inputs"].get(str(manifest))!=pins[manifest]:raise RuntimeError("Manifest SHA")
        candidates=set(gap.indices(x) for x in gap.read(manifest)["candidate_masters"])
        if len(candidates)!=63 or None in candidates or f.a.CAND not in candidates:raise RuntimeError("Candidate scope")
        spec=old.build_family_spec("VP05_full");props=spec.propagators;kernel=old.build_kernel(props)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        reducers,reduce=m.make_reducer(props,deadline)
        if any(reducers[sec].map not in gap.read(a.PILOT)["maps"] for sec in f.SECTORS):raise RuntimeError("Prior affine map")
        if c.validate_extension(reducers,props,kernel,reduce,deadline)!=gap.read(extension)["results"]:raise RuntimeError("Extension replay")
        rules=m.validate_rules(identity["records"],candidates,props,kernel,deadline)
        rule_data=[[list(k),p.encode(row)] for k,row in sorted(rules.items())]
        # Protect all 17 earlier certificates using the pinned partial summary.
        for item in prior["jobs"]:
            j=next(x for x in common["jobs"] if x["sector"]==item["sector"])
            for proof in item["results"]:
                index=j["diagnostic_targets"].index(proof["target"])
                path=m.ROOT/f"sec{item['sector']}_target{index:02d}.json"
                pins[path]=proof["certificate_sha256"]
                if n.sha(path)!=pins[path]:raise RuntimeError("Prior certificate SHA")
        job=next(x for x in common["jobs"] if x["sector"]==77)
        ready=next(x for x in identity["jobs"] if x["sector"]==77)
        targets=[tuple(k) for k in job["diagnostic_targets"]]
        if set(targets)!=set(map(tuple,ready["ready_targets"])) or not pending<=set(targets):raise RuntimeError("Target scope")
        if residual.apply(job["final_checks"],identity["records"],candidates)!=ready["post_identity_checks"]:raise RuntimeError("Identity replay")
        originals,sources=m.load_rows(job,pins,common["extension_sha256"])
        if len(originals)!=1770:raise RuntimeError("Original row scope")
        _,audit_reduce=m.make_reducer(props,deadline)
        regenerated={}
        def source(ref):
            i=ref["index"]
            if type(i)!=int or not 0<=i<len(sources) or ref!=sources[i]:raise RuntimeError("Source provenance")
            if i not in regenerated:regenerated[i]=m.replay_row(originals[i],kernel,audit_reduce)
            return regenerated[i]
        def expected(target):
            return [(pt,next(x for x in check["targets"] if tuple(x["target"])==target))
                    for pt,check in zip(old.POINTS,ready["post_identity_checks"])]
        def verify(cert,target):
            if cert["source_sha256"]!=m.SHA or cert["retry_source_sha256"]!=SHA or cert["sector"]!=77 or tuple(cert["target"])!=target or cert["rules"]!=rule_data or tuple(cert["trace_point"]) not in (*old.POINTS,*POINTS):
                raise RuntimeError("Retry certificate scope")
            # Different point paths may give different normalized pivots.
            # Use separate verifier for each certificate (no cross-path cache).
            verifier=m.Verifier(candidates,deadline)
            audit_rules={k:{j:verifier.coeff(x) for j,x in row.items()} for k,row in rules.items()}
            verifier.target_rule(cert,source,audit_rules,expected(target))
        paths={k:ROOT/f"target{targets.index(k):02d}.json" for k in pending}
        results=[]
        def register(target):
            path=paths[target];cert=gap.read(path);verify(cert,target)
            digest=n.sha(path);pins[path]=digest
            item={"target":list(target),"trace_point":cert["trace_point"],"pivots":len(cert["pivots"]),
                  "remainder":cert["remainder"],"certificate_sha256":digest,"exact_identity_verified":True}
            results.append(item);pending.remove(target);v.log("VP05_SEC77_RETRY_VERIFIED",**item)
        for target in sorted(pending):
            if paths[target].exists():register(target)
        diagnostics=[]
        if pending:
            rows=[]
            for rec in originals:
                if time.monotonic()>=deadline:raise TimeoutError("Source replay budget")
                rows.append(m.replay_row(rec,kernel,reduce))
            for point in (*old.POINTS,*POINTS):
                if not pending:break
                if not sp.isprime(point[0]):raise RuntimeError("Nonprime retry point")
                try:eng=make_trace(rows,candidates,point,deadline)
                except (ValueError,ZeroDivisionError) as exc:
                    v.log("VP05_SEC77_RETRY_POINT_SKIPPED",point=list(point),reason=str(exc));continue
                builder=DiagnosticExact(rows,eng,point,deadline)
                field_rules={k:{j:builder.coeff(x) for j,x in row.items()} for k,row in rules.items()}
                traces=[]
                for target in sorted(pending):
                    free,direct=eng.target_trace(target)
                    if point in old.POINTS:
                        i=old.POINTS.index(point)
                        saved=next(x for x in job["final_checks"][i]["targets"] if tuple(x["target"])==target)
                        if [[list(k),x] for k,x in sorted(free.items())]!=saved["remainder"]:raise RuntimeError("Old point trace mismatch")
                    mod_rules={k:p.field_row(row,point) for k,row in rules.items()}
                    combined={}
                    for k,x in free.items():
                        for j,y in mod_rules.get(k,{k:1}).items():combined[j]=(combined.get(j,0)+x*y)%point[0]
                    if any(k not in candidates for k,x in combined.items() if x):continue
                    deps=exact.dependency_order(eng.trace,direct)
                    traces.append((target,direct,deps))
                v.log("VP05_SEC77_RETRY_POINT",point=list(point),pending=len(pending),candidate_only=len(traces),pivot_rank=len(eng.piv))
                for target,direct,deps in sorted(traces,key=lambda x:(len(x[2]),x[0])):
                    builder.guard();builder.failure=None
                    try:cert,result=make_certificate(builder,sources,target,direct,deps,field_rules,rule_data,point)
                    except RuntimeError as exc:
                        if str(exc) not in PATH_ERRORS:raise
                        item={"target":list(target),"point":list(point),"reason":str(exc),"first_failure":builder.failure}
                        diagnostics.append(item);v.log("VP05_SEC77_RETRY_DIVERGENCE",**item);continue
                    except (ValueError,ZeroDivisionError) as exc:
                        item={"target":list(target),"point":list(point),"reason":"Singular exact evaluation: "+str(exc)}
                        diagnostics.append(item);v.log("VP05_SEC77_RETRY_DIVERGENCE",**item);continue
                    if not set(result)<=candidates or any([[list(k),x] for k,x in sorted(builder.evalrow(result,pt).items())]!=item["remainder"] for pt,item in expected(target)):
                        item={"target":list(target),"point":list(point),"reason":"Exact remainder mismatch"}
                        diagnostics.append(item);v.log("VP05_SEC77_RETRY_DIVERGENCE",**item);continue
                    verify(cert,target);c.save(paths[target],cert);register(target)
                del builder,eng
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        # Stable per-target output, append-only run reports preserve prior diagnostics.
        payload={"status":"VP05_SEC77_EXACT_RETRY_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},
                 "results":sorted(results,key=lambda x:x["target"]),"unresolved":[list(k) for k in sorted(pending)],
                 "diagnostics":diagnostics,"full_closure_proven":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=c.save(dest,payload)
        v.log("VP05_SEC77_EXACT_RETRY_NOT_CLOSURE",ready=13,verified=len(results),deferred=len(pending),
              original_rows_replayed=len(regenerated),diagnostics=len(diagnostics),sha256=digest,
              report=dest.name,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
