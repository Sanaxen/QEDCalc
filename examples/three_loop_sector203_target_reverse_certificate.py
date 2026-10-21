"""VP05 target-only certificate trace and exact-solver scheduling contract.

Read-only, no Fermat invocation. Reconstructs the target by *reverse*
substitution through original 166 compressed rows, and replays over distinct
finite fields. Produces a provenance schedule without assuming sampled
coefficients are symbolic identities.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows,modular_echelon,order
from examples.three_loop_sector203_target_scope_preflight import POINTS,TARGET
from examples.three_loop_sector203_target_rowspace_audit import residue

DEFAULT=Path("output/three_loop_integral_family_audit/vp05_target_symbolic_compressed.equations.json")
OUTPUT=Path("output/three_loop_integral_family_audit/vp05_target_reverse_certificate_plan.json")

def reverse_certificate(rows,prime,z,d):
    """Derive C such that sum C[i]*R[i] equals the target, without basis provenance blowup.

    Each normalized pivot E_i=(R_i - sum f_ij E_j)/n_i.
    First write T=sum g_i E_i. Back substitute in descending i:
    C_i=g_i/n_i and g_j -= C_i*f_ij.
    """
    schedule,pivots=modular_echelon(rows,prime)
    if len(pivots)!=len(rows):
        raise ValueError("Rank deficiency in compressed subsystem")
    normalized={}
    factors_by_row={}
    divisors={}
    for i,raw in enumerate(rows):
        vec=dict(raw);factors=[]
        for owner,pivot in schedule[i][0]:
            if pivot not in vec:raise AssertionError(("missing elimination pivot",i,owner,pivot))
            fac=vec[pivot]
            if not fac:raise AssertionError(("zero scheduled coefficient",i,owner,pivot))
            factors.append((owner,fac))
            for k,v in normalized[owner].items():
                t=(vec.get(k,0)-fac*v)%prime
                if t:vec[k]=t
                else:vec.pop(k,None)
        lead=schedule[i][1]
        if lead is None:raise AssertionError(("unexpected dependent row",i))
        if min(vec,key=order)!=lead:raise AssertionError(("different lead",i,lead))
        div=vec[lead]
        if not div:raise AssertionError(("zero divisor",i))
        normalized[i]={k:v*pow(div,-1,prime)%prime for k,v in vec.items()}
        divisors[i]=div;factors_by_row[i]=factors
    if set(pivots)!={schedule[i][1] for i in range(len(rows))}:
        raise AssertionError("pivot set mismatch")
    target={k:residue(expr,prime,z,d) for k,expr in TARGET.items()}
    original=dict(target);g={};target_trace=[]
    while target:
        lead=min(target,key=order)
        if lead not in pivots:break
        owner=pivots[lead][0]
        factor=target[lead]
        g[owner]=(g.get(owner,0)+factor)%prime
        target_trace.append((owner,lead))
        for k,v in normalized[owner].items():
            t=(target.get(k,0)-factor*v)%prime
            if t:target[k]=t
            else:target.pop(k,None)
    if target:raise AssertionError(("target not in sampled rowspace",len(target)))
    cert={}
    for i in reversed(range(len(rows))):
        gi=g.get(i,0)
        if not gi:continue
        ci=gi*pow(divisors[i],-1,prime)%prime
        cert[i]=ci
        for owner,factor in factors_by_row[i]:
            t=(g.get(owner,0)-ci*factor)%prime
            if t:g[owner]=t
            else:g.pop(owner,None)
    rebuilt={}
    for i,ci in cert.items():
        for k,v in rows[i].items():
            t=(rebuilt.get(k,0)+ci*v)%prime
            if t:rebuilt[k]=t
            else:rebuilt.pop(k,None)
    if rebuilt!=original:raise AssertionError("Reverse certificate replay failed")
    return {"point":[prime,z,d],"rank":len(pivots),"target_ops":len(target_trace),
        "target_owners":[i for i,_ in target_trace],
        "certificate_support":len(cert),
        "certificate_mod_prime":[cert.get(i,0) for i in range(len(rows))],
        "original_row_replay_verified":True,
        "schedule":[{"lead":list(lead) if lead is not None else None,
                     "operations":[{"owner":owner,"pivot":list(k)} for owner,k in ops]}
                    for ops,lead in schedule]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=OUTPUT)
    args=ap.parse_args()
    data=json.loads(args.equations.read_text(encoding="utf-8-sig"))
    if data.get("type")!="symbolic_exact_linear_combinations" or len(data.get("rows",[]))!=166:
        ap.error("Expected exact-combination compressed 166-row JSON")
    rows=data["rows"]
    results=[]
    for point in POINTS:
        result=reverse_certificate(mod_rows(rows,*point),*point)
        results.append(result)
        print("VP05_TARGET_REVERSE_POINT "+json.dumps({
            k:v for k,v in result.items() if k not in ("certificate_mod_prime","schedule","target_owners")
        }),flush=True)
    shared=all(v["schedule"]==results[0]["schedule"] for v in results[1:])
    owners=all(v["target_owners"]==results[0]["target_owners"] for v in results[1:])
    report={"type":"vp05_target_reverse_certificate_plan","source":str(args.equations),
        "source_sha256":hashlib.sha256(args.equations.read_bytes()).hexdigest(),
        "rows":len(rows),"points":results,"shared_pivot_schedule":shared,
        "shared_target_owner_order":owners,"finite_field_replay_all":True,
        "symbolic_certificate_verified":False,"original_528_row_exact_replay_verified":False,
        "warning":"This is only a modular reverse-substitution trace; modular zero factors must not be assumed symbolically zero. Before a symbolic certificate can be claimed, exact rational-function factor/divisor validation, target residual zero, and 528-row exact provenance replay are required."}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_TARGET_REVERSE_SUMMARY "+json.dumps({
        "shared_pivot_schedule":shared,"shared_target_owner_order":owners,
        "modular_replay_all":True,"samples":len(results),"output":str(args.output),
        "symbolic_certificate_verified":False}),flush=True)
    if not shared or not owners:raise SystemExit("Different modular schedules; exact scripted replay not yet safe")
if __name__=="__main__":main()
