"""Tentative CRT and bounded rational reconstruction for aligned VP05 coefficients.

A two-prime modular lift is a *candidate*, not a characteristic-zero proof.
Never substitutes guessed rational coefficients into the IBP equations.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter
from pathlib import Path

ROOT=Path("output/three_loop_integral_family_audit")
P=1000037;Q=1001003

def crt(a,b,p,q):
    x=(a%p + p*(((b%q-a%p)*pow(p,-1,q))%q))%(p*q)
    if x%p!=a%p or x%q!=b%q:
        raise ArithmeticError("CRT replay failed")
    return x

def rational_candidate(residue,modulus,limit):
    # Euclidean rational reconstruction, with positive denominator and
    # |numerator|,denominator <= limit. Uniqueness guaranteed when
    # 2*limit*limit < modulus for coprime numerator/denominator.
    r0,r1=modulus,residue
    t0,t1=0,1
    while abs(r1)>limit:
        if r1==0:return None
        k=r0//r1
        r0,r1=r1,r0-k*r1
        t0,t1=t1,t0-k*t1
    num,den=r1,t1
    if den<0:num,den=-num,-den
    if not den or den>limit or abs(num)>limit or math.gcd(num,den)!=1:
        return None
    if math.gcd(den,modulus)!=1 or (num-residue*den)%modulus:
        return None
    return [num,den]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--alignment",type=Path,default=ROOT/"vp05_two_prime_model_alignment.json")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_two_prime_crt_candidate_audit.json")
    args=ap.parse_args()
    raw=args.alignment.read_bytes()
    data=json.loads(raw.decode("utf-8-sig"))
    summary=data["summary"]
    if (summary["first_prime"],summary["second_prime"])!=(P,Q):
        ap.error("Unexpected primes")
    coeffs=data["coefficients"]
    if len(coeffs)!=166 or {x["row"] for x in coeffs}!=set(range(166)):
        ap.error("Expected 166 unique row IDs")
    M=P*Q
    bound=math.isqrt((M-1)//2)
    allrows=[];stats=Counter()
    for entry in sorted(coeffs,key=lambda x:x["row"]):
        if not entry["coefficient_alignment_possible"]:
            ap.error("Incompatible projective pivot on row "+str(entry["row"]))
        first,second=entry["first"],entry["second"]
        if first["degree_pair"]!=second["degree_pair"] or first["pivot"]!=second["pivot"]:
            ap.error("Degree or pivot mismatch on row "+str(entry["row"]))
        pairs={}
        for name in ("numerator","denominator"):
            if len(first[name])!=len(second[name]):
                ap.error("Unequal coefficient vector lengths")
            values=[]
            for aa,bb in zip(first[name],second[name]):
                residue=crt(int(aa),int(bb),P,Q)
                rational=rational_candidate(residue,M,bound)
                stats["coefficient_total"]+=1
                stats["rational_candidate" if rational is not None else "unresolved"]+=1
                values.append({"crt_residue":residue,"rational_candidate":rational})
            pairs[name]=values
        complete=all(v["rational_candidate"] is not None for v in pairs["numerator"]+pairs["denominator"])
        stats["complete_rows" if complete else "incomplete_rows"]+=1
        allrows.append({"row":entry["row"],"degree_pair":first["degree_pair"],
            "pivot":first["pivot"],"all_coefficients_reconstructed":complete,
            "coefficients":pairs})
    out={"summary":{"first_prime":P,"second_prime":Q,"combined_modulus":M,
        "unique_reconstruction_bound":bound,"rows":166,"counts":dict(stats),
        "alignment_sha256":hashlib.sha256(raw).hexdigest(),
        "interpretation":"Candidates satisfy both modular residues and the explicit bounded uniqueness condition only; two primes do not establish true coefficient heights.",
        "characteristic_zero_proof":False,"original_ibp_replay":False,"fermat_executed":False},
        "rows":allrows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("VP05_TWO_PRIME_CRT_AUDIT "+json.dumps({**out["summary"],"output":str(args.output)}),flush=True)

if __name__=="__main__":main()
