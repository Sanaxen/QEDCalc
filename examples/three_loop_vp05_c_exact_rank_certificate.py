"""Certified full-row-rank minor for saved restricted VP05 SYSTEM.

Nonzero minor modulo a prime at a regular specialization implies nonzero
minor over QQ(z,d). Row count supplies the exact upper bound. This is NOT
a claim about a larger seed, full master quotient, or the physical identity
of opaque column M. Read source files without changing them.
"""
import gzip
import hashlib
import json
import os
from functools import lru_cache
import sympy as sp
from sympy.polys.fields import field
from examples import three_loop_vp05_c_retention_probe as probe
from examples import three_loop_sector203_ffrank_audit as ff
from examples import three_loop_vp05_sector202_a_exact_batch as batch

PINS={
131:"77a928e5a67d3fdefeebedc3466061d39037f87b2ccb320fa6f3c9c2ec135baa",
137:"e83dce3282712fe0e3240ed701dcaf170182d5b8ef92fa612229d4ad944026b1",
138:"0bbbd439a004c2ce4349aca75064a4498472203d72c448de49e6c59cb98903ef",
139:"0da71c1e429a949a4f2f71258525e6741d8bba487c4af10bf75c6d4a032ccf0c",
194:"ee7dea07e150a1829911012d49a157bdc1f0ba6108fc00dc8baa513938fd333b",
195:"397a386d7608b490078cac6de3a3f2b8e1d21caa5458020139528d71cffcab5c",
200:"570cd6060b692565f9a6e6caa80a5d930528ca83fb86c70f83ce6a06790b46a5",
201:"11a7434336d97460d40b7105a9e8219becebfefd1df2ea8d67b694782e79c07c",
202:"73e8c529115e93e1ada0af3be246f6510079fb55ad075e4246164be270b3ff13",
203:"25226827c4cbd309c2b23be122fa0cfd1f7b231fbc9a28812041bb9196ec38a7",
67:"39853075e190324114bdfd60ea2b0c5c8c6f77127f182ca17f825ac0c347458d",
73:"770c3380a35c4ba8ffe102be244811c6f51e8ca725684a9ec63380fb50033bc4",
74:"b30ff66e48d16552cbfd8957f4cfc13dd90bab02043ba5976453f733e4877c78",
75:"7cd70249ebe83226d0935a34c52993108888e223f2d9eb8183aa1faba3664acc"}
POINT=(1000003,17,7)
C=(166576011608064,139)
M=(4,73)
OUTPUT=batch.DIR/"vp05_sector202_c_restricted_exact_rank_certificate.json"

def evaluator(point):
    p,zv,dv=point
    if not sp.isprime(p):
        raise ValueError("Not a prime")
    z,d=sp.symbols("z d")
    f,_,_=field("z,d",sp.QQ)
    @lru_cache(maxsize=16384)
    def evaluate(raw):
        # Require a genuine rational function and rational coefficients
        # integral at p, even before specializing z,d.
        val=sp.sympify(raw.replace("^","**"),locals={"z":z,"d":d})
        v=f.from_expr(val)
        for poly in (v.numer,v.denom):
            for coeff in poly.values():
                if int(coeff.denominator)%p==0:
                    raise ZeroDivisionError("Coefficient denominator divisible by prime")
        def peval(poly):
            out=0
            for powers,coeff in poly.items():
                residue=int(coeff.numerator)*pow(int(coeff.denominator)%p,-1,p)%p
                out=(out+residue*pow(zv,powers[0],p)*pow(dv,powers[1],p))%p
            return out
        den=peval(v.denom)
        if not den:
            raise ZeroDivisionError("Nonregular specialization")
        result=peval(v.numer)*pow(den,-1,p)%p
        if result!=ff.coefficient(raw,zv,dv,p):
            raise AssertionError("Independent coefficient mismatch")
        return result
    return evaluate

def read_rows(files,evaluate,p):
    rows=[]
    terms=0
    for path in files:
        with gzip.open(path,"rt",encoding="utf-8") as stream:
            while marker:=stream.readline():
                if marker.strip()!="Eq":
                    raise ValueError("Bad equation marker")
                int(stream.readline().strip())
                n=int(stream.readline().strip())
                if n<1:
                    raise ValueError("Empty original equation")
                row={}
                for _ in range(n):
                    fields=stream.readline().split()
                    if len(fields)<4:
                        raise ValueError("Malformed original term")
                    k=(int(fields[2]),int(fields[3]))
                    row[k]=(row.get(k,0)+evaluate(fields[1]))%p
                    terms+=1
                rows.append({k:v for k,v in row.items() if v})
    return rows,terms

def minor_certificate(rows,p,cap=20000):
    """Use pivot discovery order as column order; determinant is pivot product."""
    basis={}
    columns=[]
    divisors=[]
    for row in rows:
        cur=dict(row)
        # Eliminate in discovery order, NOT sorted key order. This gives a
        # triangular minor on precisely the ordered discovered columns.
        for lead in columns:
            alpha=cur.get(lead,0)
            if alpha:
                for k,v in basis[lead].items():
                    x=(cur.get(k,0)-alpha*v)%p
                    if x:cur[k]=x
                    else:cur.pop(k,None)
                if len(cur)>cap:
                    raise RuntimeError("Sparse fill cap")
        if not cur:
            raise RuntimeError("Full row rank not certified")
        lead=min(cur)
        divisor=cur[lead]
        columns.append(lead)
        divisors.append(divisor)
        inv=pow(divisor,-1,p)
        basis[lead]={k:v*inv%p for k,v in cur.items()}
    determinant=1
    for v in divisors:
        determinant=determinant*v%p
    return {"ordered_columns":[list(k) for k in columns],
            "pivot_residues":divisors,"determinant_mod_p":determinant}

def run():
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise FileExistsError("Certificate exists; preserve for audit")
    folder=probe.q.P/"tmp/VP05_full"
    files=sorted(folder.glob("SYSTEM_VP05_full_*.gz"))
    expected={f"SYSTEM_VP05_full_{k}.gz":v for k,v in PINS.items()}
    if {f.name:batch.sha(f) for f in files}!=expected:
        raise RuntimeError("Pinned SYSTEM inventory mismatch")
    mod=probe.q.load_codec((probe.q.ROOT/"output/tools/pyred_weight.py").resolve())
    bits,ordering=mod.from_kiradb(str(probe.q.P/"results/kira.db"))
    if ordering!=5:
        raise RuntimeError("Codec ordering mismatch")
    codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    if (codec.encode(probe.q.TARGETS[2]),139)!=C or tuple(codec.decode(C[0]))!=probe.q.TARGETS[2]:
        raise RuntimeError("C codec mismatch")
    p,z,d=POINT
    rows,terms=read_rows(files,evaluator(POINT),p)
    if len(rows)!=2678:
        raise RuntimeError("Unexpected equation count")
    print("VP05_C_COEFFICIENT_CHECK "+json.dumps({"rows":len(rows),"terms":terms,"all_regular_and_independently_equal":True}),flush=True)
    result=minor_certificate(rows+[{M:1},{C:1}],p)
    if len(result["ordered_columns"])!=2680 or not result["determinant_mod_p"]:
        raise RuntimeError("Full augmented row rank not certified")
    if {f.name:batch.sha(f) for f in files}!=expected:
        raise RuntimeError("Input mutated")
    report={"status":"VP05_C_RESTRICTED_EXACT_INDEPENDENCE_CERTIFICATE",
        "point":list(POINT),"system_sha256":expected,"rows":2678,
        "term_count":terms,"C_key":list(C),"opaque_M_key":list(M),
        "C_exponents":list(probe.q.TARGETS[2]),"minor":result,
        "exact_rank_E":2678,"exact_rank_E_M":2679,"exact_rank_E_M_C":2680,
        "C_independent_modulo_M_in_pinned_SYSTEM":True,
        "regular_specialization_verified":True,"new_boundary_equivalence_proven":False,
        "whole_family_63_closure_proven":False}
    raw=(json.dumps(report,indent=2)+"\n").encode()
    with OUTPUT.open("xb") as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())
    print("VP05_C_EXACT_RANK "+json.dumps({"status":report["status"],
        "determinant_mod_p":result["determinant_mod_p"],"rows":2678,
        "augmented_rank":2680,"term_count":terms,"output":str(OUTPUT),
        "certificate_sha256":hashlib.sha256(raw).hexdigest(),
        "new_boundary_equivalence_proven":False}),flush=True)

if __name__=="__main__":
    run()
