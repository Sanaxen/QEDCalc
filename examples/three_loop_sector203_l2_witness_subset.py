"""Read-only finite-field row-provenance extraction for VP05 candidate4.

Identify a *necessary candidate subset* of serialized SYSTEM equations whose
finite-field combination yields z*I10-2*I6+2*I5. This is NOT an exact symbolic
certificate. Do not run Kira. Hard caps stop runaway symbolic/provenance fill.
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

from examples.three_loop_sector203_weight_audit import ROOT

DEFAULT = ROOT / "output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734"
P = 1000003
TARGET = (10, 203)
I5 = (5, 201)
I6 = (6, 203)
MASTERS = {I5, I6, (7,203), (8,203), (9,203)}


def read_rows(project):
    from examples.three_loop_sector203_ffrank_audit import coefficient
    rows=[]
    for path in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        with gzip.open(path,"rt",encoding="utf8") as stream:
            while marker:=stream.readline():
                if marker.strip()!="Eq":
                    raise ValueError(f"Bad marker {marker!r} in {path}")
                eqid=stream.readline().strip()
                n=int(stream.readline().strip())
                row={}
                for _ in range(n):
                    fields=stream.readline().split()
                    key=(int(fields[2]),int(fields[3]))
                    value=coefficient(fields[1],17,7,P)
                    value=(row.get(key,0)+value)%P
                    if value:row[key]=value
                    else:row.pop(key,None)
                rows.append((path.name,eqid,row))
    if len(rows)!=2678:
        raise ValueError(f"Expected 2678 equations; got {len(rows)}")
    return rows


def eliminate(vector,pivots,trace,max_terms,max_support):
    order=lambda k:(k in MASTERS,k[0],k[1])
    while vector:
        lead=min(vector,key=order)
        pivot=pivots.get(lead)
        if pivot is None:
            return lead
        prow,ptrace=pivot
        factor=vector[lead]
        for k,v in prow.items():
            new=(vector.get(k,0)-factor*v)%P
            if new:vector[k]=new
            else:vector.pop(k,None)
        for idx,v in ptrace.items():
            new=(trace.get(idx,0)-factor*v)%P
            if new:trace[idx]=new
            else:trace.pop(idx,None)
        if len(vector)>max_terms or len(trace)>max_support:
            raise RuntimeError(f"Provenance cap exceeded: terms={len(vector)}, equations={len(trace)}")
    return None


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",type=Path,default=DEFAULT)
    ap.add_argument("--max-support",type=int,default=2678)
    ap.add_argument("--max-terms",type=int,default=25000)
    ap.add_argument("--report-top",type=int,default=30)
    args=ap.parse_args()
    rows=read_rows(args.project.resolve())
    pivots={}
    for idx,(_,_,source) in enumerate(rows):
        vec=dict(source)
        trace={idx:1}
        lead=eliminate(vec,pivots,trace,args.max_terms,args.max_support)
        if lead is not None:
            inv=pow(vec[lead],-1,P)
            pivots[lead]=({k:v*inv%P for k,v in vec.items()},
                          {k:v*inv%P for k,v in trace.items()})
        if (idx+1)%500==0:print(f"PROVENANCE_PROGRESS {idx+1}/2678 rank={len(pivots)}",flush=True)
    if len(pivots)!=2678:raise RuntimeError("Unexpected rank; no conclusion")
    # Desired polynomial relation rather than division by z.
    vector={TARGET:17,I6:P-2,I5:2}
    trace={}
    residue=eliminate(vector,pivots,trace,args.max_terms,args.max_support)
    if vector or residue is not None:
        print("PROPOSED_RELATION_RESIDUAL " + json.dumps({"remaining_terms":[{"key":list(k),"coefficient_mod_p":v} for k,v in sorted(vector.items())], "missing_pivot":list(residue) if residue is not None else None, "trace_size":len(trace)}),flush=True)
        raise RuntimeError(f"Proposed relation did not reduce to zero: remaining {len(vector)} terms; see PROPOSED_RELATION_RESIDUAL")
    # Trace is such that desired = sum(trace[i]*equation[i]) mod P at z=17,d=7.
    # Verify directly against ORIGINAL saved rows, not against echelon form.
    reconstructed={}
    for idx,c in trace.items():
        for k,v in rows[idx][2].items():
            val=(reconstructed.get(k,0)+c*v)%P
            if val:reconstructed[k]=val
            else:reconstructed.pop(k,None)
    expected={TARGET:17,I6:P-2,I5:2}
    if reconstructed!=expected:
        raise AssertionError("Provenance check against original equations failed")
    print("WITNESS_SUBSET "+json.dumps({
        "finite_field":"GF(1000003)","z":17,"d":7,
        "rows_total":len(rows),"rank":len(pivots),
        "support_count":len(trace),"verified_against_original_rows":True,
        "selected_row_provenance":[{"file":rows[i][0],"equation_id":rows[i][1],"weight_mod_p":trace[i]}
            for i in sorted(trace)[:args.report_top]],
        "printed_count":min(args.report_top,len(trace)),
        "next":"Use these row IDs as a candidate subset for exact symbolic verification; GF(p) coefficients are not symbolic multipliers."
        },ensure_ascii=False),flush=True)


if __name__=="__main__":
    main()
