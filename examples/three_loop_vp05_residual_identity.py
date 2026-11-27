"""Read-only identity audit for the final sec204 inverse-IBP residuals.

Exact affine propagator matching with fixed external momenta; no guessed
zero or symmetry relations. Rank deficient positive-line sets are zero in
DR because a free loop variable has only polynomial numerator dependence.
"""
import argparse
import collections
import itertools
import os
import time
from examples import three_loop_vp05_parent_inverse as inv
from examples import three_loop_vp05_stage2_sector_inventory as inventory

p=inv.p;f=inv.f;a=inv.a;old=inv.old;sp=inv.sp;gap=inv.gap;n=inv.n;v=inv.v
ROOT=n.BASE/"output"/"vp05_parent_residual10"
SOURCE=inv.ROOT/"summary.json"
SHA="c76de71ea7de40fba1813b06ea64ec884dc770d9229fd1d57fc511b94fb93239"

def positive(ex):
    return [i for i,x in enumerate(ex) if x>0]

def signature(ex,props):
    return sorted((str(props[i].mass),ex[i]) for i in positive(ex))

def rank_certificate(ex,props):
    lines=positive(ex)
    mat=sp.Matrix([f.a.momentum(props[i]) for i in lines]).jacobian(old.MOM[:3]) if lines else sp.zeros(0,3)
    rank=mat.rank()
    return {"positive_lines":[i+1 for i in lines],"loop_rank":rank,
            "null_vectors":[[str(x) for x in u] for u in mat.nullspace()],
            "scaleless_free_loop":rank<3}

def polynomial(momentum,mass):
    c=[momentum.coeff(m) for m in old.MOM]
    if sp.expand(momentum-sum(x*m for x,m in zip(c,old.MOM)))!=0:raise RuntimeError("Nonlinear momentum")
    return sp.expand(sum(c[i]*c[j]*old.dot(i,j) for i in range(5) for j in range(5))-(1 if mass=="m2" else 0))

def affine_match(src,dst,props,deadline):
    # Only equal denominator exponents/masses, equal total numerator
    # degree, fixed external momenta, and unit absolute determinant.
    if signature(src,props)!=signature(dst,props) or a.degrees(src)[0]!=a.degrees(dst)[0]:return None
    sl=positive(src);dl=positive(dst)
    if len(sl)<3:return None
    if any(x.mass not in ("0","m2") for x in props):raise RuntimeError("Mass scope")
    mom=[f.a.momentum(x) for x in props]
    A=sp.Matrix([mom[i] for i in sl]).jacobian(old.MOM[:3])
    if A.rank()!=3:return None
    rows=next(r for r in itertools.combinations(range(len(sl)),3) if A[list(r),:].det()!=0)
    B=A[list(rows),:];Bi=B.inv()
    shifts=[sp.expand(mom[i]-sum(A[j,k]*old.MOM[k] for k in range(3))) for j,i in enumerate(sl)]
    dst_num=sp.prod(polynomial(mom[i],props[i].mass)**(-x) for i,x in enumerate(dst) if x<0)
    for perm in itertools.permutations(dl):
        if any((props[i].mass,src[i])!=(props[j].mass,dst[j]) for i,j in zip(sl,perm)):continue
        for signs in itertools.product((-1,1),repeat=len(sl)):
            if time.monotonic()>=deadline:raise TimeoutError("Affine audit budget")
            rhs=sp.Matrix([signs[r]*mom[perm[r]]-shifts[r] for r in rows])
            mapping=(Bi*rhs).applyfunc(sp.expand)
            T=mapping.jacobian(old.MOM[:3]);det=T.det()
            if abs(det)!=1:continue
            sub=dict(zip(old.MOM[:3],mapping))
            if any(sp.expand(mom[i].subs(sub,simultaneous=True)-sign*mom[j])!=0 for i,j,sign in zip(sl,perm,signs)):continue
            transformed=sp.prod(polynomial(sp.expand(mom[i].subs(sub,simultaneous=True)),props[i].mass)**(-x) for i,x in enumerate(src) if x<0)
            if sp.expand(transformed-dst_num)!=0:continue
            return {"source":list(src),"destination":list(dst),"source_lines":[i+1 for i in sl],
                    "destination_lines":[i+1 for i in perm],"signs":list(signs),
                    "source_loop_in_destination":[str(x) for x in mapping],
                    "matrix":[[str(x) for x in row] for row in T.tolist()],"determinant":str(det),
                    "denominators_and_powers_verified":True,"numerator_polynomial_verified":True,
                    "external_momenta_fixed":True}
    return None

def occurrences(checks,key):
    return [{"point":check["point"],"target":r["target"],"coefficient":c}
            for check in checks for r in check["targets"] for ex,c in r["remainder"] if tuple(ex)==key]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    deadline=time.monotonic()+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (inv.ROOT,inv.h.ROOT,p.ROOT,a.ROOT,f.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        if n.sha(SOURCE)!=SHA:raise RuntimeError("Inverse summary SHA")
        source=gap.read(SOURCE);pins={SOURCE:SHA}
        if source["status"]!="VP05_PARENT_INVERSE_NOT_CLOSURE" or source["sector"]!=204 or len(source["targets"])!=16 or len(source["rounds"])!=5:raise RuntimeError("Inverse scope")
        for r in source["rounds"]:
            path=inv.ROOT/f"sec204_round{r['round']}.json";pins[path]=r["sha256"]
            if n.sha(path)!=pins[path]:raise RuntimeError("Round SHA")
        if gap.read(path)["checks"]!=source["final_checks"]:raise RuntimeError("Final checks differ")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[manifest]=n.sha(manifest);candidates=set(gap.indices(x) for x in gap.read(manifest)["candidate_masters"])
        if len(candidates)!=63 or None in candidates:raise RuntimeError("Candidate scope")
        checks=source["final_checks"];count=inv.residuals(checks,candidates)
        if len(count)!=2:raise RuntimeError("Expected two residual keys")
        spec=old.build_family_spec("VP05_full");props=spec.propagators
        if old.digest(old.build_kernel(props))!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        evidence=inventory.inspect()
        records=[]
        for key in sorted(count):
            f.e.b.a.memory()
            sec=gap.sector(key);rank=rank_certificate(key,props)
            matches=[]
            for cand in sorted(candidates):
                if rank["scaleless_free_loop"]:break
                proof=affine_match(key,cand,props,deadline)
                if proof:matches.append(proof)
            local=[]
            for seed,info in evidence["boundary_inventory"].items():
                for row in info["sector_rows"]:
                    if row["sector"]==sec:
                        local.append({"seed":seed,"classification":row["classification"],"project":row["project"],
                                      "local_masters_path":row["local_masters_path"],"restricted_audit_note":row["restricted_audit_note"]})
            record={"integral":list(key),"sector":sec,"degrees":list(a.degrees(key)),"occurrences":occurrences(checks,key),
                    "rank_certificate":rank,"same_sector_candidates":[list(k) for k in sorted(candidates) if gap.sector(k)==sec],
                    "affine_matches":matches,"local_inventory":local}
            records.append(record);v.log("VP05_RESIDUAL_IDENTITY",**record)
        # Apply only independently established exact identities to saved
        # modular remainder vectors, not to original rational IBP proofs.
        rules={}
        for r in records:
            k=tuple(r["integral"])
            if r["rank_certificate"]["scaleless_free_loop"]:rules[k]=None
            elif r["affine_matches"]:rules[k]=tuple(r["affine_matches"][0]["destination"])
        final=[]
        for check in checks:
            pt=check["point"];results=[]
            for r in check["targets"]:
                row={}
                for ex,c in r["remainder"]:
                    k=tuple(ex);dest=rules.get(k,k)
                    if dest is not None:row[dest]=(row.get(dest,0)+c)%pt[0]
                row={k:c for k,c in row.items() if c}
                results.append({"target":r["target"],"remainder":[[list(k),c] for k,c in sorted(row.items())],
                                "candidate_only":all(k in candidates for k in row)})
            final.append({"point":pt,"targets":results})
        both=sum(x["candidate_only"] and y["candidate_only"] for x,y in zip(final[0]["targets"],final[1]["targets"]))
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_RESIDUAL_IDENTITY_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},
                 "records":records,"post_identity_checks":final,"candidate_only_both":both,
                 "full_closure_proven":False,"generic_rational_target_proof":False}
        dest=ROOT/"audit.json"
        if dest.exists():
            if gap.read(dest)!=payload:raise RuntimeError("Existing audit mismatch")
        else:old.atomic(dest,payload)
        v.log("VP05_RESIDUAL_IDENTITY_NOT_CLOSURE",residuals=len(records),identities=len(rules),candidate_only_both=both,
              sha256=n.sha(dest),inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
