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
    ap.add_argument("--save-subset",action="store_true",help="Write exact original equation subset and modular witness to new audit files")
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
    # Target trace starts empty and pivot subtraction gives NEGATIVE source coefficients.
    # Hence desired = -sum(trace[i]*original_equation[i]) modulo P.
    # Verify directly against ORIGINAL saved rows, not against echelon form.
    reconstructed={}
    for idx,c in trace.items():
        for k,v in rows[idx][2].items():
            val=(reconstructed.get(k,0)-c*v)%P
            if val:reconstructed[k]=val
            else:reconstructed.pop(k,None)
    expected={TARGET:17,I6:P-2,I5:2}
    if reconstructed!=expected:
        raise AssertionError("Provenance reconstruction failed: " + json.dumps({"expected_terms":len(expected),"actual_terms":len(reconstructed),"difference_count":len(set(expected.items()) ^ set(reconstructed.items()))}))
    if args.save_subset:
        from datetime import datetime
        stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir=ROOT/"output"/"three_loop_integral_family_audit"
        outdir.mkdir(parents=True,exist_ok=True)
        base=outdir/f"vp05_candidate4_witness_{stamp}"
        exact_rows=[]
        wanted=set(trace)
        idx=0
        for file in sorted((args.project.resolve()/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
            with gzip.open(file,"rt",encoding="utf8") as inp:
                while (marker:=inp.readline()):
                    if marker.strip()!="Eq": raise ValueError("Malformed SYSTEM equation")
                    eqid=inp.readline().strip()
                    n=int(inp.readline().strip())
                    terms=[]
                    for _ in range(n):
                        fields=inp.readline().split()
                        if idx in wanted:
                            terms.append({"key":[int(fields[2]),int(fields[3])],"coefficient":fields[1]})
                    if idx in wanted:
                        assert rows[idx][0]==file.name and rows[idx][1]==eqid
                        exact_rows.append({"row_index":idx,"file":file.name,"equation_id":eqid,"terms":terms})
                    idx+=1
        assert len(exact_rows)==len(wanted) and idx==len(rows)
        with (base.with_suffix(".equations.json")).open("w",encoding="utf8") as stream:
            json.dump({"scope":"Original exact coefficient text for selected SYSTEM equations; symbolic identity NOT yet proven","rows":exact_rows},stream,indent=2)
        with (base.with_suffix(".modular_witness.json")).open("w",encoding="utf8") as stream:
            json.dump({"prime":P,"z":17,"d":7,"target":"17*I10-2*I6+2*I5","verified":True,"rows":[{"row_index":i,"file":rows[i][0],"equation_id":rows[i][1],"multiplier_mod_p":(-trace[i])%P} for i in sorted(trace)]},stream,indent=2)
        print("SAVED_SUBSET "+str(base)+".equations.json",flush=True)
        print("SAVED_MODULAR_WITNESS "+str(base)+".modular_witness.json",flush=True)
    print("WITNESS_SUBSET "+json.dumps({
        "finite_field":"GF(1000003)","z":17,"d":7,
        "rows_total":len(rows),"rank":len(pivots),
        "support_count":len(trace),"verified_against_original_rows":True,
        "selected_row_provenance":[{"file":rows[i][0],"equation_id":rows[i][1],"weight_mod_p":(-trace[i])%P}
            for i in sorted(trace)[:args.report_top]],
        "printed_count":min(args.report_top,len(trace)),
        "next":"Use these row IDs as a candidate subset for exact symbolic verification; GF(p) coefficients are not symbolic multipliers."
        },ensure_ascii=False),flush=True)


if __name__=="__main__":
    main()
