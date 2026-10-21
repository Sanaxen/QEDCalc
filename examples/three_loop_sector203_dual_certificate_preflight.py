"""VP05 dual (certificate-first) finite-field feasibility audit.

Computes target = sum_i c_i * compressed_row_i via pivot provenance.
Checks replay independently and reports certificate support and coefficient
density. It is NOT rational-function reconstruction or a symbolic proof.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows,order
from examples.three_loop_sector203_target_scope_preflight import POINTS,DEFAULT,TARGET
from examples.three_loop_sector203_target_rowspace_audit import residue


def dual_certificate(rows,target,p):
    basis={}
    provenance={}
    for i,source in enumerate(rows):
        v=source.copy()
        coeff={i:1}
        while v:
            pivot=min(v,key=order)
            if pivot not in basis:
                inv=pow(v[pivot],-1,p)
                basis[pivot]={k:x*inv%p for k,x in v.items()}
                provenance[pivot]={j:x*inv%p for j,x in coeff.items() if x%p}
                break
            factor=v[pivot]
            for k,x in basis[pivot].items():
                new=(v.get(k,0)-factor*x)%p
                if new:v[k]=new
                else:v.pop(k,None)
            for j,x in provenance[pivot].items():
                new=(coeff.get(j,0)-factor*x)%p
                if new:coeff[j]=new
                else:coeff.pop(j,None)
    remain=target.copy();cert={}
    while remain:
        pivot=min(remain,key=order)
        if pivot not in basis:break
        factor=remain[pivot]
        for k,x in basis[pivot].items():
            new=(remain.get(k,0)-factor*x)%p
            if new:remain[k]=new
            else:remain.pop(k,None)
        for j,x in provenance[pivot].items():
            new=(cert.get(j,0)+factor*x)%p
            if new:cert[j]=new
            else:cert.pop(j,None)
    reconstructed={}
    for i,c in cert.items():
        for k,x in rows[i].items():
            v=(reconstructed.get(k,0)+c*x)%p
            if v:reconstructed[k]=v
            else:reconstructed.pop(k,None)
    return {"rank":len(basis),"certificate":cert,
            "remainder_size":len(remain),
            "replay_verified":not remain and reconstructed==target}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_dual_certificate_preflight.json"))
    a=ap.parse_args()
    source=json.loads(a.equations.read_text(encoding="utf-8-sig"))
    if source.get("type")!="symbolic_exact_linear_combinations" or len(source.get("rows",[]))!=166:
        ap.error("Expected 166 exact-combination compressed rows")
    rows=source["rows"];results=[]
    for p,z,d in POINTS:
        matrix=mod_rows(rows,p,z,d)
        target={k:residue(s,p,z,d) for k,s in TARGET.items()}
        result=dual_certificate(matrix,target,p)
        if not result["replay_verified"] or result["rank"]!=166:
            raise RuntimeError("Modular certificate replay or rank failed at "+str((p,z,d)))
        support=sorted(result["certificate"])
        record={"point":[p,z,d],"rank":result["rank"],
                "certificate_support":len(support),
                "certificate_zero_rows":166-len(support),
                "support_rows":support,
                "remainder_size":result["remainder_size"],
                "replay_verified":result["replay_verified"],
                "proof":False}
        results.append(record)
        print("VP05_DUAL_CERT_POINT "+json.dumps({k:v for k,v in record.items() if k!="support_rows"}),flush=True)
    stable=all(x["support_rows"]==results[0]["support_rows"] for x in results)
    report={"input":str(a.equations),"samples":results,
            "all_replay_verified":all(x["replay_verified"] for x in results),
            "support_stable_across_points":stable,
            "certificate_support_max":max(x["certificate_support"] for x in results),
            "symbolic_certificate_found":False,
            "alias_mapping_verified":False,
            "fermat_executed":False,
            "proof":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_DUAL_CERT_SUMMARY "+json.dumps({k:v for k,v in report.items() if k not in ("samples",)} | {"output":str(a.output)}),flush=True)


if __name__=="__main__":main()
