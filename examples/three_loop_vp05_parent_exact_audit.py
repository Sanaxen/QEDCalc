"""Independent verification of saved sec204 exact DAG certificates.

No call to the proof constructor, pivot selection or modular elimination.
Check the saved linear identities directly in QQ(z,d) against regenerated
original IBP rows and independently recomputed analytic substitutions.
"""
import argparse
import functools
import os
import time
from examples import three_loop_vp05_residual_identity as r

inv=r.inv;h=inv.h;p=r.p;f=r.f;a=r.a;old=r.old;sp=r.sp;gap=r.gap;n=r.n;v=r.v;q=inv.q
PROOFS=n.BASE/"output"/"vp05_parent_exact11"
ROOT=n.BASE/"output"/"vp05_parent_exact_audit12"
SOURCE=PROOFS/"summary.json"
SHA="9e92b236b4940876fb66e74980c43897a6d64dda388b7721b14651254636584b"
IDENTITY_SHA="061cf6a32f8ce1a8525a5ab88fee0ebe3164f179e84cf6b4f711e4a9979ba366"
MAX_OPS=3000000
MAX_TERMS=200000
MAX_CHARS=200000

class Verifier:
    def __init__(self,candidates,deadline):
        self.field,self.z,self.d=sp.polys.fields.field("z,d",sp.QQ)
        self.candidates=candidates;self.deadline=deadline
        self.pivots={};self.records={};self.ops=0;self.terms=0
    def guard(self):
        if time.monotonic()>=self.deadline:raise TimeoutError("Audit budget")
        if self.ops>MAX_OPS or self.terms>MAX_TERMS:raise RuntimeError("Audit size cap")
        f.e.b.a.memory()
    def coeff(self,c):
        if len(str(c))>MAX_CHARS:raise RuntimeError("Coefficient cap")
        return self.field.from_expr(sp.sympify(c,locals={"z":f.Z,"d":f.D}))
    def decode(self,items):
        out={}
        for ex,c in items:
            k=tuple(ex)
            if len(k)!=12 or any(type(x)!=int for x in k) or k in out:raise RuntimeError("Invalid integral or duplicate")
            value=self.coeff(c)
            if not value:raise RuntimeError("Explicit zero in certificate")
            out[k]=value
        return out
    def add(self,row,other,scale):
        for k,c in other.items():
            val=row.get(k,self.field.zero)+scale*c
            if val:row[k]=val
            else:row.pop(k,None)
        self.ops+=len(other)
        if len(row)>20000 or self.ops>MAX_OPS:raise RuntimeError("Audit fill/operation cap")
    def dependencies(self,row,items,available):
        seen=set()
        for ex,c in items:
            k=tuple(ex)
            if k not in available or k in seen:raise RuntimeError("Invalid dependency order or duplicate")
            seen.add(k);value=self.coeff(c)
            if not value:raise RuntimeError("Zero multiplier")
            self.add(row,self.pivots[k],-value)
    def pivot(self,rec,source,available):
        self.guard()
        lead=tuple(rec["lead"])
        if lead in available or lead in self.candidates:raise RuntimeError("Invalid pivot lead")
        if lead in self.records:
            if self.records[lead]!=rec:raise RuntimeError("Conflicting shared pivot")
            if any(tuple(k) not in available for k,c in rec["dependencies"]):raise RuntimeError("Missing shared dependency")
            available.add(lead);return
        row=self.decode(rec["row"]);divisor=self.coeff(rec["divisor"])
        if not divisor or row.get(lead)!=self.field.one:raise RuntimeError("Invalid normalized pivot")
        if max((k for k in row if k not in self.candidates),key=f.e.b.c.key)!=lead:raise RuntimeError("Pivot ordering")
        # Direct equality: original substituted row - dependencies
        # - divisor * saved normalized pivot must be exactly zero.
        residual={k:self.coeff(c) for k,c in source(rec["source"]).items()}
        self.dependencies(residual,rec["dependencies"],available)
        self.add(residual,row,-divisor)
        if residual:raise RuntimeError("Nonzero exact pivot identity")
        self.pivots[lead]=row;self.records[lead]=rec;available.add(lead)
        self.terms+=len(row);self.guard()
    def target(self,cert,source,rules,expected):
        available=set();before=len(self.pivots)
        for rec in cert["pivots"]:self.pivot(rec,source,available)
        target=tuple(cert["target"])
        residual={target:self.field.one}
        self.dependencies(residual,cert["target_dependencies"],available)
        rem=self.decode(cert["remainder_before_identity"])
        self.add(residual,rem,-self.field.one)
        if residual:raise RuntimeError("Nonzero exact target identity")
        if cert["identities"]!=[[list(k),list(j)] for k,j in sorted(rules.items())]:raise RuntimeError("Identity rules differ")
        collapsed={}
        for k,c in rem.items():self.add(collapsed,{rules.get(k,k):c},self.field.one)
        if collapsed!=self.decode(cert["remainder"]) or any(k not in self.candidates for k in collapsed):raise RuntimeError("Candidate remainder mismatch")
        for point,result in expected:
            evaluated=p.field_row({k:c.as_expr() for k,c in collapsed.items()},point)
            if [[list(k),c] for k,c in sorted(evaluated.items())]!=result["remainder"] or not result["candidate_only"]:raise RuntimeError("Point mismatch")
        return len(self.pivots)-before

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (PROOFS,r.ROOT,inv.ROOT,h.ROOT,p.ROOT,a.ROOT,f.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        identity=r.ROOT/"audit.json"
        pins={SOURCE:SHA,identity:IDENTITY_SHA,r.SOURCE:r.SHA,inv.SOURCE:inv.SHA,a.PILOT:a.SHA,p.AUDIT:p.AUDIT_SHA,f.EVIDENCE:f.EVIDENCE_SHA}
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Evidence SHA")
        summary=gap.read(SOURCE);audit=gap.read(identity);previous=gap.read(r.SOURCE);frontier=gap.read(inv.SOURCE)
        if summary["status"]!="VP05_PARENT_EXACT_NOT_CLOSURE" or summary["exact_target_count"]!=16 or len(summary["results"])!=16 or audit["candidate_only_both"]!=16:raise RuntimeError("Proof scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[manifest]=n.sha(manifest);candidates=set(gap.indices(x) for x in gap.read(manifest)["candidate_masters"])
        if len(candidates)!=63 or f.a.CAND not in candidates or None in candidates:raise RuntimeError("Candidate scope")
        spec=old.build_family_spec("VP05_full");kernel=old.build_kernel(spec.propagators)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        rules={}
        for rec in audit["records"]:
            k=tuple(rec["integral"]);proof=r.affine_match(k,f.a.CAND,spec.propagators,deadline)
            if not proof or proof not in rec["affine_matches"]:raise RuntimeError("Affine replay")
            rules[k]=f.a.CAND
        if len(rules)!=2:raise RuntimeError("Identity count")
        pilot=gap.read(a.PILOT)
        reducers={sec:f.Reducer(spec.propagators,sec,deadline) for sec in f.SECTORS}
        if any(x.map not in pilot["maps"] for x in reducers.values()):raise RuntimeError("Factorized affine map")
        @functools.lru_cache(maxsize=4096)
        def reduce(ex):
            x=reducers[gap.sector(ex)];a.begin_seed(x);return x.reduce(ex)
        job=next(j for j in frontier["jobs"] if j["sector"]==204)
        paths=[(h.ROOT/f"r8s6d2_sec204_round{x['round']}.json",x["sha256"]) for x in job["rounds"]]
        paths.extend((inv.ROOT/f"sec204_round{x['round']}.json",x["sha256"]) for x in previous["rounds"])
        originals=[]
        for path,digest in paths:
            pins[path]=digest
            if n.sha(path)!=digest:raise RuntimeError("Round SHA")
            for rec in gap.read(path)["rows"]:
                originals.append((path.name,digest,rec))
        if len(originals)!=1935:raise RuntimeError("Original row count")
        regenerated={}
        def source(ref):
            i=ref["index"]
            if type(i)!=int or not 0<=i<len(originals):raise RuntimeError("Invalid source index")
            name,digest,rec=originals[i]
            if ref!={"index":i,"source_file":name,"source_sha256":digest,"seed":rec["seed"],"derivative":rec["derivative"]}:raise RuntimeError("Source provenance")
            if i not in regenerated:
                ex=tuple(rec["seed"]);ij=tuple(rec["derivative"])
                raw=q.exact_row(ex,kernel[ij],*ij)
                sub,used,blocked=p.substitute(raw,reduce)
                if p.encode(raw)!=rec["raw"] or p.encode(sub)!=rec["substituted"] or p.encode(used)!=rec["analytic_coefficients"] or [list(k) for k in sorted(blocked)]!=rec["blocked"]:raise RuntimeError("Original row or analytic replay")
                regenerated[i]=sub
            return regenerated[i]
        targets=[tuple(k) for k in previous["targets"]]
        by_target={tuple(x["target"]):x for x in summary["results"]}
        if len(targets)!=16 or len(set(targets))!=16 or set(targets)!=set(by_target) or any(k in candidates for k in targets):raise RuntimeError("Target inventory")
        verifier=Verifier(candidates,deadline);results=[]
        for target in targets:
            item=by_target[target];path=PROOFS/f"target{targets.index(target):02d}.json"
            pins[path]=item["sha256"]
            if n.sha(path)!=pins[path]:raise RuntimeError("Target certificate SHA")
            cert=gap.read(path)
            if cert["source_sha256"]!=IDENTITY_SHA or tuple(cert["target"])!=target or len(cert["pivots"])!=item["pivots"] or cert["remainder"]!=item["remainder"]:raise RuntimeError("Certificate summary mismatch")
            expected=[]
            for point,check in zip(old.POINTS,audit["post_identity_checks"]):
                if list(point)!=check["point"]:raise RuntimeError("Point scope")
                expected.append((point,next(x for x in check["targets"] if tuple(x["target"])==target)))
            if len(expected)!=2:raise RuntimeError("Expected two points")
            added=verifier.target(cert,source,rules,expected)
            result={"target":list(target),"pivots":len(cert["pivots"]),"new_verified_pivots":added,"certificate_sha256":pins[path],"exact_identity_verified":True}
            results.append(result);v.log("VP05_PARENT_EXACT_AUDIT_TARGET",**result)
        if len(verifier.pivots)!=268 or len(regenerated)!=268:raise RuntimeError("Expected 268 distinct pivot/source rows")
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_PARENT_EXACT_AUDIT_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},"results":results,
                 "unique_verified_pivots":len(verifier.pivots),"unique_original_rows_replayed":len(regenerated),
                 "affine_identities_verified":len(rules),"full_closure_proven":False}
        dest=ROOT/"audit.json"
        if dest.exists():
            if gap.read(dest)!=payload:raise RuntimeError("Existing audit mismatch")
        else:old.atomic(dest,payload)
        if gap.read(dest)!=payload:raise RuntimeError("Audit save mismatch")
        v.log("VP05_PARENT_EXACT_AUDIT_NOT_CLOSURE",targets=len(results),unique_verified_pivots=len(verifier.pivots),
              original_rows_replayed=len(regenerated),affine_identities_verified=len(rules),
              sha256=n.sha(dest),elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
