"""Finish the 64 diagnostic target certificates, not family closure.

Reproduce all analytic rules, audit new exact DAGs against original IBP
rows, and preserve all 46 prior certificates. Alternative field points
select paths only; acceptance requires rational identities.
"""
import argparse
import os
import time
from examples import three_loop_vp05_residual_covariance as cov
from examples import three_loop_vp05_common_exact as ce
from examples import three_loop_vp05_sec77_exact_retry as retry

m=cov.m;s=cov.s;c=cov.c;p=cov.p;f=cov.f;a=cov.a;old=cov.old;sp=cov.sp;gap=cov.gap;n=cov.n;v=cov.v
exact=ce.exact
ROOT=n.BASE/"output"/"vp05_final_diagnostic_exact20"
SOURCE=cov.ROOT/"audit.json"
SHA="0d79d364c408b050d8cad1a264dd6c4947601ae2d28143ff82b14badd1e3d404"

def rules_replay(identity,structure,moments,final,candidates,props,kernel,deadline):
    rules=ce.validate_rules(identity["records"],candidates,props,kernel,deadline)
    zeros=[x for x in structure["records"] if x["kind"]=="massless_factor_zero"]
    if len(zeros)!=4:raise RuntimeError("Zero scope")
    for rec in zeros:
        key=tuple(rec["integral"])
        if s.massless_factor(key,props)!=rec["certificate"] or rec["rule"]:raise RuntimeError("Zero replay")
        rules[key]={}
    bubble=m.bubble71(props,candidates,deadline)
    if bubble!=next(x for x in moments["records"] if tuple(x["integral"])==m.K71):raise RuntimeError("Bubble replay")
    rules[m.K71]=p.decode(bubble["rule"])
    keys=sorted(tuple(x["integral"]) for x in moments["records"] if x["sector"]==228)
    sym,proof=m.symmetry228(keys,candidates,props,deadline)
    if sym!=[x for x in moments["records"] if x["sector"]==228] or proof!=moments["symmetry_certificate"]:raise RuntimeError("Symmetry replay")
    for item in sym:
        if item["kind"]!="unresolved":rules[tuple(item["integral"])]=p.decode(item["rule"])
    records,cert=cov.solve([cov.R,cov.J],candidates,props,deadline,proof)
    if records!=final["records"] or cert!=final["certificate"] or any(x["kind"]=="unresolved" for x in records):raise RuntimeError("Covariance replay")
    for rec in records:rules[tuple(rec["integral"])]=p.decode(rec["rule"])
    expected={tuple(x["integral"]) for x in identity["records"]}|{cov.J}
    if len(rules)!=12 or set(rules)!=expected or any(not set(row)<=candidates for row in rules.values()):
        raise RuntimeError("Consolidated rule scope")
    # Separate algebraic check of the saved partial symmetry relation.
    partial=next(x for x in sym if tuple(x["integral"])==cov.R)
    check={}
    for key,coef in p.decode(partial["partial_remainder"]).items():
        for dest,value in rules.get(key,{key:sp.S.One}).items():check[dest]=check.get(dest,0)+coef*value
    if {k:sp.cancel(x) for k,x in check.items() if sp.cancel(x)!=0}!=rules[cov.R]:
        raise RuntimeError("Partial symmetry composition")
    return rules

def pin_prior(common,pins):
    previous=gap.read(retry.SOURCE);report=gap.read(s.RETRY);sec204=gap.read(c.AUDIT)
    if previous["verified"]!=17 or len(report["results"])!=13 or report["unresolved"] or len(sec204["results"])!=16:raise RuntimeError("Prior count")
    done={};inventory=[]
    def put(sec,target,path,digest):
        key=tuple(target)
        if (sec,key) in done or n.sha(path)!=digest:raise RuntimeError("Prior certificate SHA or duplicate")
        pins[path]=digest;done[sec,key]=digest
        inventory.append({"sector":sec,"target":target,"path":str(path),"sha256":digest})
    # Locate sec204 proofs by their actual audited hashes, not by a
    # positional index in a different stage summary.
    source=gap.read(c.audit.SOURCE)
    by_target={tuple(x["target"]):x["sha256"] for x in source["results"]}
    files={}
    for path in sorted(c.audit.PROOFS.glob("target[0-9][0-9].json")):
        digest=n.sha(path)
        if digest in files:raise RuntimeError("Duplicate sec204 certificate hash")
        files[digest]=path
    if len(by_target)!=16 or len(files)!=16:raise RuntimeError("Sec204 proof inventory")
    for item in sec204["results"]:
        digest=item["certificate_sha256"]
        if by_target.get(tuple(item["target"]))!=digest or digest not in files:
            raise RuntimeError("Sec204 proof summary mismatch")
        path=files[digest]
        if gap.read(path)["target"]!=item["target"]:raise RuntimeError("Sec204 target mismatch")
        put(204,item["target"],path,digest)
    for job in previous["jobs"]:
        sec=job["sector"]
        targets=next(x["diagnostic_targets"] for x in common["jobs"] if x["sector"]==sec)
        for item in job["results"]:
            idx=targets.index(item["target"])
            put(sec,item["target"],ce.ROOT/f"sec{sec}_target{idx:02d}.json",item["certificate_sha256"])
    targets=next(x["diagnostic_targets"] for x in common["jobs"] if x["sector"]==77)
    for item in report["results"]:
        idx=targets.index(item["target"])
        put(77,item["target"],retry.ROOT/f"target{idx:02d}.json",item["certificate_sha256"])
    if len(done)!=46 or any(sum(k[0]==sec for k in done)!=count for sec,count in ((204,16),(77,16),(71,10),(228,4))):raise RuntimeError("Prior inventory")
    return done,inventory

def job_run(job,final_job,done,rules,candidates,props,kernel,deadline,pins,extension_sha):
    sec=job["sector"];targets=[tuple(x) for x in job["diagnostic_targets"]]
    pending={k for k in targets if (sec,k) not in done}
    if len(pending)!={71:6,228:12}[sec] or set(targets)!=set(map(tuple,final_job["ready_targets"])):raise RuntimeError("Pending scope")
    originals,sources=ce.load_rows(job,pins,extension_sha)
    _,audit_reduce=ce.make_reducer(props,deadline);regenerated={}
    def source(ref):
        i=ref["index"]
        if type(i)!=int or not 0<=i<len(sources) or ref!=sources[i]:raise RuntimeError("Source provenance")
        if i not in regenerated:regenerated[i]=ce.replay_row(originals[i],kernel,audit_reduce)
        return regenerated[i]
    def expected(target):
        out=[]
        for pt,check in zip(old.POINTS,final_job["post_identity_checks"]):
            if list(pt)!=check["point"]:raise RuntimeError("Point scope")
            out.append((pt,next(x for x in check["targets"] if tuple(x["target"])==target)))
        if len(out)!=2:raise RuntimeError("Point count")
        return out
    rule_data=[[list(k),p.encode(row)] for k,row in sorted(rules.items())]
    def verify(cert,target):
        if cert["source_sha256"]!=SHA or cert["sector"]!=sec or tuple(cert["target"])!=target or cert["rules"]!=rule_data or tuple(cert["trace_point"]) not in (*old.POINTS,*retry.POINTS):raise RuntimeError("Certificate scope")
        verifier=ce.Verifier(candidates,deadline)
        ar={k:{j:verifier.coeff(x) for j,x in row.items()} for k,row in rules.items()}
        verifier.target_rule(cert,source,ar,expected(target))
    paths={k:ROOT/f"sec{sec}_target{targets.index(k):02d}.json" for k in pending}
    results=[];diagnostics=[]
    def register(target):
        path=paths[target];cert=gap.read(path);verify(cert,target)
        digest=n.sha(path);pins[path]=digest
        item={"sector":sec,"target":list(target),"trace_point":cert["trace_point"],"pivots":len(cert["pivots"]),
              "remainder":cert["remainder"],"certificate_sha256":digest,"exact_identity_verified":True}
        results.append(item);pending.remove(target);v.log("VP05_FINAL_DIAGNOSTIC_VERIFIED",**item)
    for target in sorted(pending):
        if paths[target].exists():register(target)
    if pending:
        _,reduce=ce.make_reducer(props,deadline)
        rows=[]
        for rec in originals:
            if time.monotonic()>=deadline:raise TimeoutError("Source replay budget")
            rows.append(ce.replay_row(rec,kernel,reduce))
        for point in (*old.POINTS,*retry.POINTS):
            if not pending:break
            if not sp.isprime(point[0]):raise RuntimeError("Nonprime point")
            try:
                eng=retry.make_trace(rows,candidates,point,deadline)
                mod_rules={k:p.field_row(row,point) for k,row in rules.items()}
            except (ValueError,ZeroDivisionError) as exc:
                v.log("VP05_FINAL_DIAGNOSTIC_POINT_SKIPPED",sector=sec,point=list(point),reason=str(exc));continue
            builder=retry.DiagnosticExact(rows,eng,point,deadline)
            fr={k:{j:builder.coeff(x) for j,x in row.items()} for k,row in rules.items()}
            traces=[]
            for target in sorted(pending):
                free,direct=eng.target_trace(target)
                if point in old.POINTS:
                    i=old.POINTS.index(point)
                    saved=next(x for x in job["final_checks"][i]["targets"] if tuple(x["target"])==target)
                    if [[list(k),x] for k,x in sorted(free.items())]!=saved["remainder"]:raise RuntimeError("Old trace mismatch")
                combined={}
                for k,x in free.items():
                    for j,y in mod_rules.get(k,{k:1}).items():combined[j]=(combined.get(j,0)+x*y)%point[0]
                if any(k not in candidates for k,x in combined.items() if x):continue
                deps=exact.dependency_order(eng.trace,direct);traces.append((target,direct,deps))
            v.log("VP05_FINAL_DIAGNOSTIC_POINT",sector=sec,point=list(point),pending=len(pending),candidate_only=len(traces),pivot_rank=len(eng.piv))
            for target,direct,deps in sorted(traces,key=lambda x:(len(x[2]),x[0])):
                builder.guard();builder.failure=None
                try:
                    cert,result=retry.make_certificate(builder,sources,target,direct,deps,fr,rule_data,point)
                    if not set(result)<=candidates or any([[list(k),x] for k,x in sorted(builder.evalrow(result,pt).items())]!=item["remainder"] for pt,item in expected(target)):
                        raise RuntimeError("Exact remainder mismatch")
                except RuntimeError as exc:
                    if str(exc) not in (*retry.PATH_ERRORS,"Exact remainder mismatch"):raise
                    item={"sector":sec,"target":list(target),"point":list(point),"reason":str(exc),"first_failure":builder.failure}
                    diagnostics.append(item);v.log("VP05_FINAL_DIAGNOSTIC_DEFERRED",**item);continue
                except (ValueError,ZeroDivisionError) as exc:
                    item={"sector":sec,"target":list(target),"point":list(point),"reason":"Singular evaluation: "+str(exc)}
                    diagnostics.append(item);v.log("VP05_FINAL_DIAGNOSTIC_DEFERRED",**item);continue
                cert["source_sha256"]=SHA;cert["sector"]=sec;cert.pop("retry_source_sha256")
                verify(cert,target);c.save(paths[target],cert);register(target)
            del builder,eng
    return {"sector":sec,"results":sorted(results,key=lambda x:x["target"]),"unresolved":[list(k) for k in sorted(pending)],
            "original_rows_replayed":len(regenerated),"diagnostics":diagnostics}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (cov.ROOT,m.ROOT,s.ROOT,s.m.ROOT,c.ROOT,retry.ROOT,ce.ROOT,c.audit.ROOT,c.audit.PROOFS,c.inv.ROOT,c.h.ROOT,p.ROOT,a.ROOT,f.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={SOURCE:SHA,cov.SOURCE:cov.SHA,m.SOURCE:m.SHA,s.SOURCE:s.SHA,s.m.SOURCE:s.m.SHA,
              s.RETRY:s.RETRY_SHA,retry.SOURCE:retry.SHA,c.AUDIT:c.SHA,c.audit.SOURCE:c.audit.SHA,
              c.inv.SOURCE:c.inv.SHA,a.PILOT:a.SHA,p.AUDIT:p.AUDIT_SHA,f.EVIDENCE:f.EVIDENCE_SHA}
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Evidence SHA")
        common=gap.read(s.m.SOURCE);identity=gap.read(s.SOURCE);structure=gap.read(m.SOURCE);moments=gap.read(cov.SOURCE);final=gap.read(SOURCE)
        if final["status"]!="VP05_RESIDUAL_COVARIANCE_NOT_CLOSURE" or any(j["candidate_only_after"]!=16 or j["unresolved"] for j in final["jobs"]):raise RuntimeError("Final scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[manifest]=n.sha(manifest)
        if common["inputs"].get(str(manifest))!=pins[manifest]:raise RuntimeError("Manifest SHA")
        candidates=set(gap.indices(x) for x in gap.read(manifest)["candidate_masters"])
        if len(candidates)!=63 or None in candidates or f.a.CAND not in candidates:raise RuntimeError("Candidate scope")
        props=old.build_family_spec("VP05_full").propagators;kernel=old.build_kernel(props)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        extension=c.ROOT/"extension.json";pins[extension]=common["extension_sha256"]
        if n.sha(extension)!=pins[extension]:raise RuntimeError("Extension SHA")
        reducers,reduce=ce.make_reducer(props,deadline)
        if any(reducers[sec].map not in gap.read(a.PILOT)["maps"] for sec in f.SECTORS):raise RuntimeError("Prior affine map")
        if c.validate_extension(reducers,props,kernel,reduce,deadline)!=gap.read(extension)["results"]:raise RuntimeError("Extension replay")
        done,inventory=pin_prior(common,pins)
        rules=rules_replay(identity,structure,moments,final,candidates,props,kernel,deadline)
        rule_records=[{"integral":list(k),"kind":"replayed","rule":p.encode(row)} for k,row in sorted(rules.items())]
        for job in common["jobs"]:
            fj=next(x for x in final["jobs"] if x["sector"]==job["sector"])
            if s.m.apply(job["final_checks"],rule_records,candidates)!=fj["post_identity_checks"]:raise RuntimeError("Consolidated rule application")
        v.log("VP05_FINAL_DIAGNOSTIC_RULES",rules=len(rules),original_residuals=11,prior_proofs=len(done),analytic_replay=True)
        jobs=[]
        for sec in (71,228):
            job=next(x for x in common["jobs"] if x["sector"]==sec)
            fj=next(x for x in final["jobs"] if x["sector"]==sec)
            jobs.append(job_run(job,fj,done,rules,candidates,props,kernel,deadline,pins,common["extension_sha256"]))
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        verified=sum(len(j["results"]) for j in jobs)
        payload={"status":"VP05_FINAL_DIAGNOSTIC_EXACT_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},
                 "prior_proofs":inventory,"rules":rule_records,"jobs":jobs,"prior_verified":46,"new_verified":verified,
                 "diagnostic_verified":46+verified,"analytic_rules_reproduced":True,"full_closure_proven":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=c.save(dest,payload)
        v.log("VP05_FINAL_DIAGNOSTIC_EXACT_NOT_CLOSURE",ready=18,verified=verified,diagnostic_verified=46+verified,
              deferred=18-verified,original_rows_replayed_job_sum=sum(j["original_rows_replayed"] for j in jobs),
              sha256=digest,report=dest.name,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
