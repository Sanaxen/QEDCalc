"""Common exact DAG construction and independent verification of ready targets.
Use immutable per-target certificates; existing certificates are audited on
restart without rebuilding their exact pivots. No full closure assertion.
"""
import argparse
import functools
import os
import time
from examples import three_loop_vp05_common_residual as residual
from examples import three_loop_vp05_parent_exact as exact
from examples import three_loop_vp05_parent_exact_audit as audit

c=residual.c;p=c.p;f=c.f;a=c.a;old=c.old;sp=c.sp;gap=c.gap;n=c.n;v=c.v
ROOT=n.BASE/"output"/"vp05_parent_common_exact15"
SOURCE=residual.ROOT/"audit.json"
SHA="4c61d580deb6474e929f639b41266e88afe26802831c630fe9c8006712635ecb"

def collapse(row,rules,field):
    result={}
    for k,val in row.items():
        for j,coeff in rules.get(k,{k:field.one}).items():
            result[j]=result.get(j,field.zero)+val*coeff
    return {k:val for k,val in result.items() if val}

class Verifier(audit.Verifier):
    def target_rule(self,cert,source,rules,expected):
        self.guard()
        available=set();before=len(self.pivots)
        for rec in cert["pivots"]:self.pivot(rec,source,available)
        target=tuple(cert["target"])
        row={target:self.field.one}
        self.dependencies(row,cert["target_dependencies"],available)
        rem=self.decode(cert["remainder_before_identity"])
        self.add(row,rem,-self.field.one)
        if row:raise RuntimeError("Nonzero exact target identity")
        # Deliberately separate implementation from constructor collapse.
        result={}
        for k,coeff in rem.items():
            self.add(result,rules.get(k,{k:self.field.one}),coeff)
        if result!=self.decode(cert["remainder"]) or any(k not in self.candidates for k in result):
            raise RuntimeError("Candidate remainder mismatch")
        for pt,item in expected:
            actual=p.field_row({k:x.as_expr() for k,x in result.items()},pt)
            if [[list(k),x] for k,x in sorted(actual.items())]!=item["remainder"] or not item["candidate_only"]:
                raise RuntimeError("Independent point mismatch")
        return len(self.pivots)-before

def load_rows(job,pins,extension_sha):
    sec=job["sector"]
    paths=[(c.ROOT/f"sec{sec}_initial.json",job["initial_sha256"])]
    paths.extend((c.ROOT/f"sec{sec}_round{x['round']}.json",x["sha256"]) for x in job["rounds"])
    originals=[];sources=[]
    for path,digest in paths:
        pins[path]=digest
        if n.sha(path)!=digest:raise RuntimeError("Round SHA")
        data=gap.read(path)
        if data["meta"]["sector"]!=sec or data["meta"]["extension_sha256"]!=extension_sha or data["meta"]["kernel_sha256"]!=f.e.b.c.PIN:
            raise RuntimeError("Round scope")
        for rec in data["rows"]:
            sources.append({"index":len(originals),"source_file":path.name,"source_sha256":digest,
                            "seed":rec["seed"],"derivative":rec["derivative"]})
            originals.append(rec)
    if data["checks"]!=job["final_checks"] or len(originals)!=job["final"]["rows"]:raise RuntimeError("Final scope")
    return originals,sources

def replay_row(rec,kernel,reduce):
    ex=tuple(rec["seed"]);ij=tuple(rec["derivative"])
    raw=c.q.exact_row(ex,kernel[ij],*ij)
    sub,used,blocked=c.substitute(raw,reduce)
    if p.encode(raw)!=rec["raw"] or p.encode(sub)!=rec["substituted"] or p.encode(used)!=rec["analytic_coefficients"] or [list(k) for k in sorted(blocked)]!=rec["blocked"]:
        raise RuntimeError("Original IBP or substitution mismatch")
    return sub

def make_reducer(props,deadline):
    reducers={sec:f.Reducer(props,sec,deadline) for sec in c.SECTORS}
    @functools.lru_cache(maxsize=4096)
    def reduce(ex):
        r=reducers[gap.sector(ex)];a.begin_seed(r);return r.reduce(ex)
    return reducers,reduce

def validate_rules(records,candidates,props,kernel,deadline):
    result={}
    for rec in records:
        if rec["kind"]=="unresolved":continue
        k=tuple(rec["integral"])
        again=residual.identify(k,candidates,props,kernel,deadline)
        if again!={key:val for key,val in rec.items() if key!="occurrences"}:
            raise RuntimeError("Residual rule replay mismatch")
        result[k]=p.decode(rec["rule"])
        if not set(result[k])<=candidates:raise RuntimeError("Rule outside candidates")
    if len(result)!=4:raise RuntimeError("Expected four rules")
    return result

def job_run(job,ready_job,candidates,props,kernel,deadline,pins,extension_sha,rules):
    sec=job["sector"];originals,sources=load_rows(job,pins,extension_sha)
    targets=[tuple(k) for k in job["diagnostic_targets"]]
    ready={tuple(k) for k in ready_job["ready_targets"]}
    if len(targets)!=16 or len(set(targets))!=16 or not ready<=set(targets) or len(ready)!={228:4,71:10,77:16}[sec]:
        raise RuntimeError("Ready target scope")
    # Verify existing certificates first, and keep audit caches separate
    # from construction. Recreate only requested original rows for audit.
    verifier=Verifier(candidates,deadline)
    _,audit_reduce=make_reducer(props,deadline)
    regenerated={}
    def source(ref):
        i=ref["index"]
        if type(i)!=int or not 0<=i<len(sources) or ref!=sources[i]:raise RuntimeError("Source provenance")
        if i not in regenerated:regenerated[i]=replay_row(originals[i],kernel,audit_reduce)
        return regenerated[i]
    audit_rules={k:{j:verifier.coeff(x) for j,x in row.items()} for k,row in rules.items()}
    rule_data=[[list(k),p.encode(row)] for k,row in sorted(rules.items())]
    def expected(target):
        out=[]
        for pt,check in zip(old.POINTS,ready_job["post_identity_checks"]):
            if list(pt)!=check["point"]:raise RuntimeError("Point scope")
            out.append((pt,next(x for x in check["targets"] if tuple(x["target"])==target)))
        if len(out)!=2:raise RuntimeError("Point count")
        return out
    def verify(path,target):
        cert=gap.read(path)
        if cert["source_sha256"]!=SHA or cert["sector"]!=sec or tuple(cert["target"])!=target or cert["rules"]!=rule_data:
            raise RuntimeError("Certificate scope")
        added=verifier.target_rule(cert,source,audit_rules,expected(target))
        digest=n.sha(path);pins[path]=digest
        result={"sector":sec,"target":list(target),"pivots":len(cert["pivots"]),"new_verified_pivots":added,
                "remainder":cert["remainder"],"certificate_sha256":digest,"exact_identity_verified":True}
        v.log("VP05_COMMON_EXACT_VERIFIED",**result)
        return result
    paths={k:ROOT/f"sec{sec}_target{targets.index(k):02d}.json" for k in ready}
    results=[];pending=[]
    for target in targets:
        if target not in ready:continue
        if paths[target].exists():results.append(verify(paths[target],target))
        else:pending.append(target)
    failures=[]
    if pending:
        _,reduce=make_reducer(props,deadline)
        rows=[];engines=[exact.Trace(pt[0],candidates,deadline) for pt in old.POINTS]
        for i,rec in enumerate(originals):
            if time.monotonic()>=deadline:raise TimeoutError("Source replay budget")
            sub=replay_row(rec,kernel,reduce);rows.append(sub)
            for eng,pt in zip(engines,old.POINTS):eng.insert_source(p.field_row(sub,pt),i)
        traces=[]
        for target in pending:
            pairs=[eng.target_trace(target) for eng in engines]
            for i,(free,_) in enumerate(pairs):
                item=next(x for x in job["final_checks"][i]["targets"] if tuple(x["target"])==target)
                if [[list(k),val] for k,val in sorted(free.items())]!=item["remainder"]:raise RuntimeError("Modular replay mismatch")
            deps=exact.dependency_order(engines[0].trace,pairs[0][1])
            traces.append((target,pairs[0][1],deps))
            v.log("VP05_COMMON_EXACT_SLICE",sector=sec,target=list(target),pivots=len(deps),original_rows=len(rows))
        builder=exact.Exact(rows,engines[0],old.POINTS[0],deadline)
        field_rules={k:{j:builder.coeff(x) for j,x in row.items()} for k,row in rules.items()}
        for target,direct,deps in sorted(traces,key=lambda x:(len(x[2]),x[0])):
            builder.guard()
            # Path divergence is diagnostic, not a proof of irreducibility.
            # Fail closed on provenance errors, resource errors or audit errors.
            try:
                for k in deps:builder.build(k)
                rem,multipliers=builder.target(target,direct)
            except RuntimeError as exc:
                if str(exc) not in ("Exact pivot path diverged","Exact leading key differs","Exact target path diverged","Modular pivot replay mismatch"):raise
                item={"sector":sec,"target":list(target),"reason":str(exc)}
                failures.append(item);v.log("VP05_COMMON_EXACT_DEFERRED",**item);continue
            collapsed=collapse(rem,field_rules,builder.field)
            if not set(collapsed)<=candidates or any([[list(k),val] for k,val in sorted(builder.evalrow(collapsed,pt).items())]!=item["remainder"] for pt,item in expected(target)):
                item={"sector":sec,"target":list(target),"reason":"Exact candidate remainder or point mismatch"}
                failures.append(item);v.log("VP05_COMMON_EXACT_DEFERRED",**item);continue
            cert=[]
            for k in deps:
                item=builder.piv[k]
                cert.append({"lead":list(k),"source":sources[item["source"]],"divisor":exact.expr(item["divisor"]),
                             "dependencies":[[list(j),exact.expr(x)] for j,x in item["dependencies"]],"row":exact.encoded(item["row"])})
            payload={"source_sha256":SHA,"sector":sec,"target":list(target),"pivots":cert,
                     "target_dependencies":[[list(k),exact.expr(x)] for k,x in multipliers],
                     "remainder_before_identity":exact.encoded(rem),"remainder":exact.encoded(collapsed),
                     "rules":rule_data,"full_closure_proven":False}
            # Verify before persistence; reread and verify again after save.
            verifier.target_rule(payload,source,audit_rules,expected(target))
            c.save(paths[target],payload)
            results.append(verify(paths[target],target))
    # Drop cache-dependent audit statistics from persistent summary.
    for item in results:item.pop("new_verified_pivots")
    results.sort(key=lambda x:x["target"]);failures.sort(key=lambda x:x["target"])
    result={"sector":sec,"ready":len(ready),"verified":len(results),"original_rows":len(originals),
            "unique_verified_pivots":len(verifier.pivots),"original_rows_replayed":len(regenerated),
            "results":results,"deferred":failures,"not_ready":[list(k) for k in targets if k not in ready]}
    v.log("VP05_COMMON_EXACT_JOB",**{k:x for k,x in result.items() if k not in ("results","not_ready")})
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (residual.ROOT,c.ROOT,c.audit.ROOT,c.audit.PROOFS,c.inv.ROOT,c.h.ROOT,p.ROOT,a.ROOT,f.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={SOURCE:SHA,residual.SOURCE:residual.SHA,c.AUDIT:c.SHA,a.PILOT:a.SHA,p.AUDIT:p.AUDIT_SHA,f.EVIDENCE:f.EVIDENCE_SHA}
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Evidence SHA")
        common=gap.read(residual.SOURCE);identity=gap.read(SOURCE)
        if common["status"]!="VP05_PARENT_COMMON_NOT_CLOSURE" or identity["status"]!="VP05_COMMON_RESIDUAL_NOT_CLOSURE" or len(identity["records"])!=11:
            raise RuntimeError("Input scope")
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
        reducers,reduce=make_reducer(props,deadline)
        pilot=gap.read(a.PILOT)
        if any(reducers[sec].map not in pilot["maps"] for sec in f.SECTORS):raise RuntimeError("Prior affine map")
        ext=c.validate_extension(reducers,props,kernel,reduce,deadline)
        if ext!=gap.read(extension)["results"]:raise RuntimeError("Extension replay")
        rules=validate_rules(identity["records"],candidates,props,kernel,deadline)
        results=[]
        for sec in (77,71,228):
            job=next(x for x in common["jobs"] if x["sector"]==sec)
            ready=next(x for x in identity["jobs"] if x["sector"]==sec)
            if residual.apply(job["final_checks"],identity["records"],candidates)!=ready["post_identity_checks"]:raise RuntimeError("Identity application replay")
            results.append(job_run(job,ready,candidates,props,kernel,deadline,pins,common["extension_sha256"],rules))
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_COMMON_EXACT_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},"jobs":results,
                 "ready":sum(x["ready"] for x in results),"verified":sum(x["verified"] for x in results),"full_closure_proven":False}
        # Keep incomplete summaries separate; successful target files can
        # always be independently reused on restart.
        dest=ROOT/("summary.json" if payload["verified"]==30 else "partial_summary.json")
        if dest.exists() and gap.read(dest)!=payload:
            if payload["verified"]==30:raise RuntimeError("Final summary mismatch")
            raise RuntimeError("Partial summary changed; retain target proofs and review")
        digest=c.save(dest,payload)
        v.log("VP05_COMMON_EXACT_NOT_CLOSURE",ready=payload["ready"],verified=payload["verified"],
              unique_verified_pivots_job_sum=sum(x["unique_verified_pivots"] for x in results),
              original_rows_replayed_job_sum=sum(x["original_rows_replayed"] for x in results),
              sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
