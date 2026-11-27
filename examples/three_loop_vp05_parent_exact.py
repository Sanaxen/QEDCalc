"""Trace modular dependencies and replay only the needed exact pivot DAG.

Each exact pivot is an explicit linear combination of an original substituted
IBP row and earlier normalized pivots. Each target is verified in QQ(z,d)
with exact coefficients, including the independently audited scalar maps.
No generic claim about the unselected rows or the whole parent sector.
"""
import argparse
import functools
import os
import time
from examples import three_loop_vp05_residual_identity as r

inv=r.inv;h=inv.h;p=r.p;f=r.f;a=r.a;old=r.old;sp=r.sp;gap=r.gap;n=r.n;v=r.v;q=inv.q
ROOT=n.BASE/"output"/"vp05_parent_exact11"
SOURCE=r.ROOT/"audit.json"
SHA="061cf6a32f8ce1a8525a5ab88fee0ebe3164f179e84cf6b4f711e4a9979ba366"
MAX_PIVOTS=1800
MAX_TERMS=200000
MAX_OPS=2000000
MAX_CHARS=200000

class Trace(p.Echelon):
    def __init__(self,prime,candidates,deadline):
        super().__init__(prime,candidates,deadline);self.trace={}
    def insert_source(self,row,index):
        row=dict(row);deps=[]
        while row:
            self.guard(row)
            keys=[k for k in row if k not in self.candidates]
            if not keys:
                self.candidate_relations+=1;return
            lead=max(keys,key=f.e.b.c.key)
            if lead not in self.piv:
                iv=pow(row[lead],-1,self.p)
                self.piv[lead]={k:c*iv%self.p for k,c in row.items()}
                self.trace[lead]=(index,tuple(deps))
                self.terms+=len(row);self.guard(row);return
            deps.append(lead);self.subtract(row,self.piv[lead],row[lead])
    def target_trace(self,ex):
        row={ex:1};free={};deps=[]
        while row:
            self.guard(row)
            lead=max(row,key=lambda k:(k not in self.candidates,f.e.b.c.key(k)))
            if lead in self.piv:
                deps.append(lead);self.subtract(row,self.piv[lead],row[lead])
            else:free[lead]=row.pop(lead)
        return free,deps

def dependency_order(trace,deps):
    seen=set();out=[]
    def visit(k):
        if k in seen:return
        seen.add(k)
        for j in trace[k][1]:visit(j)
        out.append(k)
    for k in deps:visit(k)
    return out

def collapse(row,rules):
    out={}
    for k,c in row.items():
        k=rules.get(k,k)
        out[k]=out.get(k,0)+c
    return {k:c for k,c in out.items() if c}

class Exact:
    def __init__(self,rows,engine,point,deadline):
        self.rows=rows;self.engine=engine;self.point=point;self.deadline=deadline
        self.field,self.z,self.d=sp.polys.fields.field("z,d",sp.QQ)
        self.piv={};self.ops=0;self.terms=0
    def guard(self):
        if time.monotonic()>=self.deadline:raise TimeoutError("Exact budget")
        if len(self.piv)>MAX_PIVOTS or self.terms>MAX_TERMS or self.ops>MAX_OPS:raise RuntimeError("Exact size cap")
        f.e.b.a.memory()
    def coeff(self,c):
        return self.field.from_expr(sp.sympify(c))
    def subtract(self,row,pivot,c):
        for k,vv in pivot.items():
            x=row.get(k,self.field.zero)-c*vv
            if x:row[k]=x
            else:row.pop(k,None)
        self.ops+=len(pivot)
        if len(row)>p.MAX_FILL or self.ops>MAX_OPS:raise RuntimeError("Exact operation/fill cap")
    def evalrow(self,row,pt):
        return p.field_row({k:c.as_expr() for k,c in row.items()},pt)
    def build(self,k):
        if k in self.piv:return
        self.guard()
        index,deps=self.engine.trace[k]
        row={j:self.coeff(c) for j,c in self.rows[index].items()}
        multipliers=[]
        for j in deps:
            if j not in self.piv:raise RuntimeError("Dependency order")
            c=row.get(j,self.field.zero)
            if not c:raise RuntimeError("Exact pivot path diverged")
            self.subtract(row,self.piv[j]["row"],c);multipliers.append((j,c))
        if not row.get(k) or max((j for j in row if j not in self.engine.candidates),key=f.e.b.c.key)!=k:
            raise RuntimeError("Exact leading key differs")
        divisor=row[k];row={j:c/divisor for j,c in row.items()}
        if self.evalrow(row,self.point)!=self.engine.piv[k]:raise RuntimeError("Modular pivot replay mismatch")
        self.terms+=len(row)
        record={"row":row,"source":index,"dependencies":multipliers,"divisor":divisor}
        self.piv[k]=record;self.guard()
    def target(self,ex,deps):
        cur={ex:self.field.one};multipliers=[]
        for k in deps:
            c=cur.get(k,self.field.zero)
            if not c:raise RuntimeError("Exact target path diverged")
            self.subtract(cur,self.piv[k]["row"],c);multipliers.append((k,c))
        return cur,multipliers

def expr(c):
    s=str(c.as_expr())
    if len(s)>MAX_CHARS:raise RuntimeError("Exact coefficient size cap")
    return s

def encoded(row):
    return [[list(k),expr(c)] for k,c in sorted(row.items())]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (r.ROOT,inv.ROOT,h.ROOT,p.ROOT,a.ROOT,f.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={SOURCE:SHA,r.SOURCE:r.SHA,inv.SOURCE:inv.SHA,a.PILOT:a.SHA,p.AUDIT:p.AUDIT_SHA,f.EVIDENCE:f.EVIDENCE_SHA}
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Evidence SHA")
        audit=gap.read(SOURCE);previous=gap.read(r.SOURCE);frontier=gap.read(inv.SOURCE)
        if audit["candidate_only_both"]!=16 or len(audit["records"])!=2:raise RuntimeError("Identity scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[path]=n.sha(path);candidates=set(gap.indices(x) for x in gap.read(path)["candidate_masters"])
        if len(candidates)!=63 or f.a.CAND not in candidates:raise RuntimeError("Candidate scope")
        spec=old.build_family_spec("VP05_full");kernel=old.build_kernel(spec.propagators)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        rules={}
        for rec in audit["records"]:
            k=tuple(rec["integral"]);proof=r.affine_match(k,f.a.CAND,spec.propagators,deadline)
            if not proof or proof not in rec["affine_matches"]:raise RuntimeError("Identity replay")
            rules[k]=f.a.CAND
        pilot=gap.read(a.PILOT)
        reducers={sec:f.Reducer(spec.propagators,sec,deadline) for sec in f.SECTORS}
        if any(x.map not in pilot["maps"] for x in reducers.values()):raise RuntimeError("Affine map")
        @functools.lru_cache(maxsize=4096)
        def reduce(ex):
            x=reducers[gap.sector(ex)];a.begin_seed(x);return x.reduce(ex)
        job=next(j for j in frontier["jobs"] if j["sector"]==204)
        paths=[(h.ROOT/f"r8s6d2_sec204_round{x['round']}.json",x["sha256"]) for x in job["rounds"]]
        paths.extend((inv.ROOT/f"sec204_round{x['round']}.json",x["sha256"]) for x in previous["rounds"])
        rows=[];sources=[]
        engines=[Trace(pt[0],candidates,deadline) for pt in old.POINTS]
        for path,digest in paths:
            pins[path]=digest
            if n.sha(path)!=digest:raise RuntimeError("Round SHA")
            for rec in gap.read(path)["rows"]:
                if time.monotonic()>=deadline:raise TimeoutError("Source replay budget")
                ex=tuple(rec["seed"]);ij=tuple(rec["derivative"])
                raw=q.exact_row(ex,kernel[ij],*ij);sub,used,blocked=p.substitute(raw,reduce)
                if p.encode(raw)!=rec["raw"] or p.encode(sub)!=rec["substituted"] or p.encode(used)!=rec["analytic_coefficients"] or [list(k) for k in sorted(blocked)]!=rec["blocked"]:raise RuntimeError("Original row replay")
                index=len(rows);rows.append(sub);sources.append({"index":index,"seed":list(ex),"derivative":list(ij),"source_file":path.name,"source_sha256":digest})
                for eng,pt in zip(engines,old.POINTS):eng.insert_source(p.field_row(sub,pt),index)
        if len(rows)!=1935:raise RuntimeError("Original row count")
        targets=[tuple(k) for k in previous["targets"]];traces=[]
        for target in targets:
            pairs=[eng.target_trace(target) for eng in engines]
            for i,(free,deps) in enumerate(pairs):
                expected=next(x for x in previous["final_checks"][i]["targets"] if tuple(x["target"])==target)
                if [[list(k),c] for k,c in sorted(free.items())]!=expected["remainder"]:raise RuntimeError("Target modular replay")
            deps=dependency_order(engines[0].trace,pairs[0][1])
            traces.append((target,pairs[0][1],deps))
            v.log("VP05_PARENT_EXACT_SLICE",target=list(target),pivots=len(deps),source_rows=len({engines[0].trace[k][0] for k in deps}),total_original_rows=len(rows))
        # Small slices first. Per-target independent immutable certificate;
        # no need to symbolically eliminate all 1935 rows.
        exact=Exact(rows,engines[0],old.POINTS[0],deadline)
        results=[]
        for target,direct,deps in sorted(traces,key=lambda x:(len(x[2]),x[0])):
            for k in deps:exact.build(k)
            rem,multipliers=exact.target(target,direct)
            collapsed=collapse(rem,rules)
            if any(k not in candidates for k in collapsed):raise RuntimeError("Exact residual outside candidates")
            for i,pt in enumerate(old.POINTS):
                expected=next(x for x in audit["post_identity_checks"][i]["targets"] if tuple(x["target"])==target)
                if [[list(k),c] for k,c in sorted(exact.evalrow(collapsed,pt).items())]!=expected["remainder"]:raise RuntimeError("Exact target point mismatch")
            # Store a DAG certificate: normalized pivot = (source - sum
            # multiplier * earlier pivot)/divisor. Target identity is
            # I_target - remainder = sum multiplier * normalized pivot.
            cert=[]
            for k in deps:
                item=exact.piv[k]
                cert.append({"lead":list(k),"source":sources[item["source"]],"divisor":expr(item["divisor"]),
                             "dependencies":[[list(j),expr(c)] for j,c in item["dependencies"]],"row":encoded(item["row"])})
            payload={"source_sha256":SHA,"target":list(target),"pivots":cert,
                     "target_dependencies":[[list(k),expr(c)] for k,c in multipliers],
                     "remainder_before_identity":encoded(rem),"remainder":encoded(collapsed),
                     "identities":[[list(k),list(j)] for k,j in sorted(rules.items())],
                     "exact_dag_replay":True,"two_point_match":True,"full_closure_proven":False}
            dest=ROOT/f"target{targets.index(target):02d}.json"
            if dest.exists():
                if gap.read(dest)!=payload:raise RuntimeError("Saved proof differs")
            else:old.atomic(dest,payload)
            if gap.read(dest)!=payload:raise RuntimeError("Proof save mismatch")
            result={"target":list(target),"pivots":len(deps),"remainder":encoded(collapsed),"sha256":n.sha(dest)}
            results.append(result);v.log("VP05_PARENT_EXACT_TARGET",**result)
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_PARENT_EXACT_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},"results":results,
                 "exact_target_count":len(results),"full_closure_proven":False}
        dest=ROOT/"summary.json"
        if dest.exists():
            if gap.read(dest)!=payload:raise RuntimeError("Summary mismatch")
        else:old.atomic(dest,payload)
        v.log("VP05_PARENT_EXACT_NOT_CLOSURE",targets=len(results),unique_exact_pivots=len(exact.piv),original_rows=len(rows),
              sha256=n.sha(dest),elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
