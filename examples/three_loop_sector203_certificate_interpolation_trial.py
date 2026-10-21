"""Bounded bivariate rational interpolation of VP05 certificate samples.

Finite-field hypothesis test only, never an exact symbolic proof.
Requires a 1-dimensional homogeneous nullspace and all holdouts to pass.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

DEFAULT=Path("output/three_loop_integral_family_audit/vp05_same_prime_certificate_samples.json")
OUT=Path("output/three_loop_integral_family_audit/vp05_certificate_interpolation_trial.json")


def powers(degree):
    return [(i,j) for s in range(degree+1) for i in range(s+1) for j in [s-i]]


def value(monomials,z,d,p):
    return [pow(z,i,p)*pow(d,j,p)%p for i,j in monomials]


def null_vector(matrix,p):
    """One null vector only if kernel dimension is exactly one."""
    a=[list(row) for row in matrix]
    n=len(a[0])
    pivots=[]
    r=0
    for c in range(n):
        pivot=next((j for j in range(r,len(a)) if a[j][c]%p),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r]
        inv=pow(a[r][c]%p,-1,p)
        a[r]=[v*inv%p for v in a[r]]
        for j in range(len(a)):
            if j==r:continue
            factor=a[j][c]%p
            if factor:a[j]=[(x-factor*y)%p for x,y in zip(a[j],a[r])]
        pivots.append(c);r+=1
        if r==len(a):break
    free=[c for c in range(n) if c not in pivots]
    if len(free)!=1:return None,r,len(free)
    v=[0]*n
    v[free[0]]=1
    for k,col in enumerate(pivots):
        v[col]=(-a[k][free[0]])%p
    return v,r,1


def solve(samples,prime,degree,index):
    mons=powers(degree);m=len(mons)
    matrix=[]
    for s in samples:
        _,z,d=s["point"];y=s["coefficients_by_compressed_row"][index]%prime
        v=value(mons,z,d,prime)
        matrix.append(v+[(-y*x)%prime for x in v])
    vec,rank,nullity=null_vector(matrix,prime)
    if vec is None:return {"status":"nonunique","rank":rank,"nullity":nullity}
    a,b=vec[:m],vec[m:]
    # Denominator must be nonzero at every training point.
    for s in samples:
        _,z,d=s["point"];v=value(mons,z,d,prime)
        den=sum(x*y for x,y in zip(b,v))%prime
        num=sum(x*y for x,y in zip(a,v))%prime
        y=s["coefficients_by_compressed_row"][index]%prime
        if den==0 or num!=y*den%prime:
            return {"status":"singular_training","rank":rank,"nullity":nullity}
    return {"status":"candidate","numerator":a,"denominator":b,"rank":rank,"nullity":nullity}


def trial(data,degree):
    p=data["prime"];train=[x for x in data["samples"] if x["role"]=="training"]
    hold=[x for x in data["samples"] if x["role"]=="holdout"]
    if not hold:raise ValueError("Holdouts required")
    models=[];passed=0;failed=0;nonunique=0;singular=0
    mons=powers(degree)
    for col in range(166):
        model=solve(train,p,degree,col)
        if model["status"]!="candidate":
            if model["status"]=="nonunique":nonunique+=1
            else:singular+=1
            models.append({"row":col,**model})
            continue
        checks=0
        for s in hold:
            _,z,d=s["point"];v=value(mons,z,d,p)
            num=sum(a*x for a,x in zip(model["numerator"],v))%p
            den=sum(b*x for b,x in zip(model["denominator"],v))%p
            if den==0 or num!=s["coefficients_by_compressed_row"][col]*den%p:break
            checks+=1
        if checks==len(hold):passed+=1;status="holdout_pass"
        else:failed+=1;status="holdout_fail"
        models.append({"row":col,**model,"status":status,"holdouts_passed":checks})
    return {"degree":degree,"monomials":mons,"training_count":len(train),
            "holdout_count":len(hold),"holdout_pass":passed,
            "holdout_fail":failed,"nonunique":nonunique,
            "singular_training":singular,"models":models}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=OUT)
    ap.add_argument("--degree",type=int,default=3)
    a=ap.parse_args()
    if a.degree<0 or a.degree>6:ap.error("Degree must be 0..6")
    raw=a.samples.read_bytes();data=json.loads(raw.decode("utf-8-sig"))
    if data.get("type")!="same_prime_modular_certificate_samples" or data.get("rows")!=166:
        ap.error("Invalid sample format")
    p=data.get("prime")
    if not isinstance(p,int) or p<=2:ap.error("Invalid prime")
    seen=set()
    for s in data.get("samples",[]):
        pt=tuple(s["point"])
        if pt in seen or pt[0]!=p or not s.get("replay_verified") or len(s["coefficients_by_compressed_row"])!=166:
            ap.error("Invalid, duplicate, or non-replayed sample")
        seen.add(pt)
    result=trial(data,a.degree)
    summary={k:v for k,v in result.items() if k!="models"}
    summary.update({"source_sha256":hashlib.sha256(raw).hexdigest(),
                    "equations_sha256":data.get("source_sha256"),
                    "prime":p,"proof":False,"fermat_executed":False,
                    "symbolic_reconstruction":False,
                    "all_holdouts_pass":result["holdout_pass"]==166})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"summary":summary,"models":result["models"]},indent=2)+"\n",encoding="utf-8")
    print("VP05_INTERPOLATION_TRIAL "+json.dumps({**summary,"output":str(a.output)}),flush=True)


if __name__=="__main__":main()
