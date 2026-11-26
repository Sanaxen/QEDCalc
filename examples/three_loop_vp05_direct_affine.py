"""Complete direct demand evidence via explicit affine maps and tensor moments.
Preserve the original 11 IBP certificates. The final identity uses a separate
analytic proof, not an original-source IBP multiplier certificate.
"""
import json
import os
import time
from examples import three_loop_vp05_direct_exact as e
m=e.m
n=e.n
v=e.v
gap=e.gap
old=e.old
sp=e.sp
ROOT=n.BASE/"output"/"vp05_direct_affine04"
CAND=(1,0,0,1,0,0,1,0,0,0,0,0)
BLOCK=(0,0,2,0,-1,0,1,1,0,0,0,0)

def momentum(prop):
    return sp.expand(sp.sympify(prop.momentum,locals=dict(zip(map(str,old.MOM),old.MOM))))

def basis(props,ex):
    lines=[i for i,a in enumerate(ex) if a>0]
    if len(lines)!=3 or any(props[i].mass!="m2" for i in lines):
        raise RuntimeError("Expected three massive denominators")
    expressions=sp.Matrix([momentum(props[i]) for i in lines])
    A=expressions.jacobian(old.MOM[:3])
    shift=expressions-A*sp.Matrix(old.MOM[:3])
    shift=shift.applyfunc(sp.expand)
    if abs(A.det())!=1 or any(x.free_symbols-set(old.MOM[3:]) for x in shift):
        raise RuntimeError("Not an affine unit determinant basis")
    return lines,expressions,A,shift

def affine(props,src,dst):
    sl,S,A,a=basis(props,src);dl,D,B,c=basis(props,dst)
    # Old source loop variables expressed in destination loop variables.
    mapping=(A.inv()*(D-a)).applyfunc(sp.expand)
    transform=mapping.jacobian(old.MOM[:3])
    if abs(transform.det())!=1:raise RuntimeError("Jacobian mismatch")
    sub=dict(zip(old.MOM[:3],mapping))
    for x,y in zip(S,D):
        if sp.expand(x.subs(sub,simultaneous=True)-y)!=0:raise RuntimeError("Momentum map mismatch")
    return {"source":list(src),"destination":list(dst),"source_lines_1based":[i+1 for i in sl],
            "destination_lines_1based":[i+1 for i in dl],"source_loop_in_destination":[str(x) for x in mapping],
            "matrix":[[str(x) for x in row] for row in transform.tolist()],"determinant":str(transform.det()),
            "propagators_verified":3,"mass_match":True,"jacobian_absolute":1}

def moment_proof(props):
    lines,S,A,a=basis(props,BLOCK)
    if [BLOCK[i] for i in lines]!=[2,1,1] or [i for i,x in enumerate(BLOCK) if x<0]!=[4] or BLOCK[4]!=-1:
        raise RuntimeError("Unexpected numerator/dots")
    U=sp.Matrix(sp.symbols("u0:3"))
    mapping=(A.inv()*(U-a)).applyfunc(sp.expand)
    q=sp.expand(momentum(props[4]).subs(dict(zip(old.MOM[:3],mapping)),simultaneous=True))
    if props[4].mass not in ("0","m2"):raise RuntimeError("Numerator mass")
    alpha=[q.coeff(u) for u in U]
    ext=sp.expand(q-sum(x*u for x,u in zip(alpha,U)))
    pvec,qvec=old.MOM[3:]
    beta=ext.coeff(pvec);gamma=ext.coeff(qvec)
    if sp.expand(ext-beta*pvec-gamma*qvec)!=0:raise RuntimeError("Numerator not affine")
    ext2=sp.expand(beta**2-beta*gamma*old.Z+gamma**2*old.Z)
    # Odd vector moments vanish for independently centered tadpoles.
    # For P=u^2-1, J2/J1=(d-2)/2 from 0=d J1-2(J1+J2).
    # u^2/P^a = 1/P^(a-1)+1/P^a; J0=0 in dimensional regularization.
    d=old.D;ratio=d/2-1
    coeff=sp.expand(alpha[0]**2*(1+ratio)+(alpha[1]**2+alpha[2]**2+ext2-(1 if props[4].mass=="m2" else 0))*ratio)
    # Note each undotted u^2 term leaves J0+J1, hence ratio overall.
    if sp.expand(coeff-(d-2))!=0:raise RuntimeError("Analytic coefficient differs from candidate: "+str(coeff))
    return {"target":list(BLOCK),"scalar":list(int(bool(196&(1<<i))) for i in range(12)),
            "new_loop_momenta":[str(x) for x in S],"old_loop_in_new":[str(x) for x in mapping],
            "determinant":str(A.det()),"numerator_momentum":str(q),"numerator_mass":props[4].mass,
            "loop_coefficients":[str(x) for x in alpha],"external_square":str(ext2),
            "coefficient":str(coeff),"tadpole_ratio":str(ratio),
            "assumptions":["dimensional regularization","translation invariant loop measure","odd centered tadpole moments vanish","scaleless J0=0","m2=1"],
            "original_symbolic_IBP_certificate":False,"analytic_factorization_proof":True}

def main():
    ROOT.mkdir(exist_ok=True)
    lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    try:
        if (e.ROOT/"running.lock").exists():raise RuntimeError("Exact engine running")
        if n.sha(e.SOURCE)!=e.SHA:raise RuntimeError("Reduction input SHA")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        manifest=gap.read(path);pins={path:n.sha(path),e.SOURCE:e.SHA}
        if CAND not in [gap.indices(x) for x in manifest["candidate_masters"]]:raise RuntimeError("Candidate missing")
        spec=old.build_family_spec("VP05_full");kernel=old.build_kernel(spec.propagators)
        if old.digest(kernel)!=e.b.c.PIN:raise RuntimeError("Kernel")
        maps=[affine(spec.propagators,tuple(int(bool(sec&(1<<i))) for i in range(12)),CAND) for sec in (196,200)]
        for item in maps:v.log("VP05_DIRECT_AFFINE_MAP",**item)
        proof=moment_proof(spec.propagators)
        data=gap.read(e.SOURCE)
        observed=[r for r in data["results"] if tuple(r["target"])==BLOCK]
        if len(observed)!=2:raise RuntimeError("Blocked target scope")
        for r in observed:
            p,z,d=r["field"];num,den=sp.fraction(sp.sympify(proof["coefficient"]).subs(old.D,d))
            val=int(num)%p*pow(int(den)%p,-1,p)%p
            if r["remainder"]!=[[proof["scalar"],val]]:raise RuntimeError("Analytic point mismatch")
        v.log("VP05_DIRECT_ANALYTIC_PROOF",**proof)
        # Independently replay all existing certificates without loading pivots.
        proofs=[]
        for sec in (196,200):
            engine=e.Exact(sec,0,kernel,[e.b.Packed() for _ in range(2 if sec==196 else 3)],time.monotonic()+3600)
            left=[r for r in data["results"] if r["sector"]==sec and r["point"]==0]
            right={tuple(r["target"]):r for r in data["results"] if r["sector"]==sec and r["point"]==1}
            for i,r in enumerate(left):
                if tuple(r["target"])==BLOCK:continue
                src=e.ROOT/f"sec{sec}_{i}.json";pins[src]=n.sha(src)
                saved=gap.read(src);engine.verify_saved(saved,r,right[tuple(r["target"])])
                proofs.append({"target":r["target"],"sha256":pins[src],"file":str(src)})
                v.log("VP05_DIRECT_AFFINE_IBP_AUDIT",sector=sec,target=r["target"],original_symbolic_replay=True)
        if len(proofs)!=11 or any(n.sha(p)!=h for p,h in pins.items()):raise RuntimeError("Evidence count/input changed")
        payload={"status":"VP05_DIRECT_AFFINE_COMPLETE_NOT_CLOSURE","kernel_sha256":e.b.c.PIN,"inputs":{str(p):h for p,h in pins.items()},"maps":maps,"analytic_proof":proof,"ibp_certificates":proofs,"direct_targets_proven":12,"original_ibp_certificates":11,"full_closure_proven":False}
        dest=ROOT/"direct_evidence.json"
        if dest.exists():
            if gap.read(dest)!=payload:raise RuntimeError("Existing evidence differs")
        else:old.atomic(dest,payload)
        if gap.read(dest)!=payload:raise RuntimeError("Saved evidence mismatch")
        v.log("VP05_DIRECT_AFFINE_COMPLETE_NOT_CLOSURE",direct_targets_proven=12,original_ibp_certificates=11,analytic_certificates=1,scalar_maps=2,sha256=n.sha(dest),inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
