"""Bounded parent IBP substitution and modular target feasibility pilot.

Regenerate manifest-direct rows, substitute only verified factorized sectors
and their proven scaleless proper subsets, retain all other terms. Compare
raw and substituted finite-field row spaces with candidate columns protected
from pivot selection. No claim of full parent closure or rational proof.
"""
import argparse
import collections
import functools
import time
import os
from examples import three_loop_vp05_factorized_ibp_audit as a

f=a.f;old=a.old;sp=a.sp;gap=a.gap;n=a.n;v=a.v
q=f.e.m.q
ROOT=n.BASE/"output"/"vp05_parent_substitution07"
AUDIT=a.ROOT/"audit.json"
AUDIT_SHA="c6b3fd9170faf61e5d706c256d73b2e5e5a4efaac922f6b8f3dac18b20025a32"
MAX_TERMS=500000
MAX_OPS=3000000
MAX_FILL=20000

def substitute(row,reduce):
    out={};used={};blocked={}
    for ex,c in sorted(row.items()):
        sec=gap.sector(ex)
        if sec in f.SECTORS:
            s,d=a.degrees(ex)
            if s<=f.MAX_DEGREE and d<=f.MAX_DOTS:
                value=reduce(ex);used[ex]=value
                key=f.a.CAND;c=c*value
            else:
                blocked[ex]=(s,d);key=ex
        elif any(sec!=s and sec&s==sec for s in f.SECTORS):
            used[ex]=sp.S.Zero;continue
        else:key=ex
        out[key]=out.get(key,0)+c
    out={k:sp.cancel(c) for k,c in out.items()}
    return {k:c for k,c in out.items() if c!=0},used,blocked

def encode(row):
    return [[list(k),str(c)] for k,c in sorted(row.items())]

def decode(row):
    return {tuple(k):sp.sympify(c,locals={"d":f.D,"z":f.Z}) for k,c in row}

def inventory(manifest):
    jobs={}
    for label in ("candidate_masters","closure_targets"):
        for item in manifest[label]:
            ex=gap.indices(item)
            if ex is None:raise RuntimeError("Invalid manifest integral")
            for seed,parents in q.t.MISSING.items():
                if gap.sector(ex) in parents and q.scope(ex,8,6 if seed=="r8s6d2" else 5,2 if seed=="r8s6d2" else 3):
                    jobs.setdefault((seed,gap.sector(ex)),{}).setdefault(ex,set()).add(label)
    return jobs

def field_row(row,point):
    out={}
    for k,c in row.items():
        val=f.evaluate(sp.sympify(c),point)
        if val:out[k]=val
    return out

class Echelon:
    def __init__(self,p,candidates,deadline):
        self.p=p;self.candidates=candidates;self.deadline=deadline
        self.piv={};self.ops=0;self.terms=0;self.candidate_relations=0
    def guard(self,row):
        if time.monotonic()>=self.deadline:raise TimeoutError("Parent modular budget")
        if self.ops>MAX_OPS or len(row)>MAX_FILL or self.terms>MAX_TERMS:raise RuntimeError("Parent modular cap")
        if self.ops%1024==0:f.e.b.a.memory()
    def subtract(self,row,pivot,c):
        for k,v in pivot.items():
            val=(row.get(k,0)-c*v)%self.p
            if val:row[k]=val
            else:row.pop(k,None)
        self.ops+=len(pivot);self.guard(row)
    def insert(self,row):
        row=dict(row)
        while row:
            self.guard(row)
            keys=[k for k in row if k not in self.candidates]
            if not keys:
                self.candidate_relations+=1;return
            lead=max(keys,key=f.e.b.c.key)
            if lead not in self.piv:
                inv=pow(row[lead],-1,self.p)
                self.piv[lead]={k:c*inv%self.p for k,c in row.items()}
                self.terms+=len(row);self.guard(row);return
            self.subtract(row,self.piv[lead],row[lead])
    def target(self,ex):
        row={ex:1};free={}
        while row:
            self.guard(row)
            lead=max(row,key=lambda k:(k not in self.candidates,f.e.b.c.key(k)))
            if lead in self.piv:self.subtract(row,self.piv[lead],row[lead])
            else:free[lead]=row.pop(lead)
        return {"target":list(ex),"candidate_only":all(k in self.candidates for k in free),
                "remainder":[[list(k),c] for k,c in sorted(free.items())]}

def modular(rows,targets,candidates,point,deadline):
    engine=Echelon(point[0],candidates,deadline)
    for row in rows:engine.insert(field_row(row,point))
    results=[engine.target(ex) for ex in sorted(targets)]
    return {"point":list(point),"pivot_rank":len(engine.piv),"pivot_terms":engine.terms,
            "candidate_only_relations":engine.candidate_relations,"operations":engine.ops,
            "targets":results,"candidate_only_targets":sum(x["candidate_only"] for x in results)}

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    deadline=time.monotonic()+args.hours*3600;started=time.monotonic()
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (a.ROOT,f.ROOT,f.a.ROOT,f.e.ROOT,q.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={AUDIT:AUDIT_SHA,a.PILOT:a.SHA,f.EVIDENCE:f.EVIDENCE_SHA}
        if any(n.sha(p)!=h for p,h in pins.items()):raise RuntimeError("Evidence SHA")
        audit=gap.read(AUDIT);pilot=gap.read(a.PILOT)
        if audit["status"]!="VP05_FACTORIZED_IBP_AUDIT_NOT_CLOSURE" or sum(x["counts"].get("PASS",0) for x in audit["summaries"])!=5059 or sum(x["counts"].get("UNSUPPORTED",0) for x in audit["summaries"])!=581:raise RuntimeError("Audit scope")
        for name,h in audit["seed_sha256"].items():
            if os.path.basename(name)!=name:raise RuntimeError("Seed path")
            p=a.ROOT/name
            if n.sha(p)!=h:raise RuntimeError("Seed SHA")
            pins[p]=h
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[path]=n.sha(path);manifest=gap.read(path)
        candidates=set(gap.indices(x) for x in manifest["candidate_masters"])
        if len(candidates)!=63 or f.a.CAND not in candidates:raise RuntimeError("Candidate scope")
        spec=old.build_family_spec("VP05_full");kernel=old.build_kernel(spec.propagators)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        reducers={sec:f.Reducer(spec.propagators,sec,deadline) for sec in f.SECTORS}
        if any(r.map not in pilot["maps"] for r in reducers.values()):raise RuntimeError("Affine map mismatch")
        @functools.lru_cache(maxsize=4096)
        def reduce(ex):
            r=reducers[gap.sector(ex)];a.begin_seed(r);return r.reduce(ex)
        jobs=inventory(manifest)
        if sum(len(x) for x in jobs.values())*15>2070:raise RuntimeError("Unexpected direct scope")
        summaries=[]
        for (seed,sec),targets in sorted(jobs.items()):
            dest=ROOT/f"{seed}_sec{sec}.json"
            meta={"seed":seed,"sector":sec,"audit_sha256":AUDIT_SHA,"manifest_sha256":pins[path],"kernel_sha256":f.e.b.c.PIN}
            raw=[];after=[];records=[];used_all={};blocked_all={}
            for ex in sorted(targets):
                if time.monotonic()>=deadline:raise TimeoutError("Parent budget")
                f.e.b.a.memory()
                for ij,entries in sorted(kernel.items()):
                    row=q.exact_row(ex,entries,*ij)
                    sub,used,blocked=substitute(row,reduce)
                    raw.append(row);after.append(sub);used_all.update(used);blocked_all.update(blocked)
                    records.append({"seed":list(ex),"derivative":list(ij),"raw":encode(row),"substituted":encode(sub)})
            # Keep target candidates separate: only noncandidate targets count as reductions.
            wanted={ex for ex,labels in targets.items() if "closure_targets" in labels and ex not in candidates}
            before_cols=set().union(*(set(x) for x in raw));after_cols=set().union(*(set(x) for x in after))
            stats={"rows":len(raw),"columns_before":len(before_cols),"columns_after":len(after_cols),
                   "terms_before":sum(map(len,raw)),"terms_after":sum(map(len,after)),
                   "factorized_or_zero_targets":len(used_all),"blocked_targets":len(blocked_all),
                   "noncandidate_closure_targets":len(wanted)}
            checks=[]
            for point in old.POINTS:
                checks.append({"raw":modular(raw,wanted,candidates,point,deadline),
                               "substituted":modular(after,wanted,candidates,point,deadline)})
            payload={"meta":meta,"stats":stats,"rows":records,"substitutions":encode(used_all),
                     "blocked":[[list(k),list(d)] for k,d in sorted(blocked_all.items())],"checks":checks,
                     "full_closure_proven":False}
            if dest.exists():
                if gap.read(dest)!=payload:raise RuntimeError("Existing job differs")
            else:old.atomic(dest,payload)
            if gap.read(dest)!=payload:raise RuntimeError("Saved job mismatch")
            result={"seed":seed,"sector":sec,**stats,"raw_candidate_only":[c["raw"]["candidate_only_targets"] for c in checks],
                    "substituted_candidate_only":[c["substituted"]["candidate_only_targets"] for c in checks],"sha256":n.sha(dest)}
            summaries.append(result);v.log("VP05_PARENT_SUBSTITUTION_JOB",**result)
        if any(n.sha(p)!=h for p,h in pins.items()):raise RuntimeError("Input changed")
        payload={"status":"VP05_PARENT_SUBSTITUTION_NOT_CLOSURE","inputs":{str(p):h for p,h in pins.items()},
                 "jobs":summaries,"full_closure_proven":False,"generic_rational_target_proof":False,
                 "recursive_parent_reduction_proven":False}
        dest=ROOT/"summary.json"
        if dest.exists():
            if gap.read(dest)!=payload:raise RuntimeError("Existing summary differs")
        else:old.atomic(dest,payload)
        v.log("VP05_PARENT_SUBSTITUTION_NOT_CLOSURE",jobs=len(summaries),rows=sum(x["rows"] for x in summaries),
              terms_before=sum(x["terms_before"] for x in summaries),terms_after=sum(x["terms_after"] for x in summaries),
              blocked_job_targets=sum(x["blocked_targets"] for x in summaries),sha256=n.sha(dest),
              elapsed_s=time.monotonic()-started,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
