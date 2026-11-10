"""Read-only finite-field audit of sector202 checkpoint trace matrix and source replay.

Tests whether 389 saved pivot provenance rows span the 389 selected original
IBP rows at the certificate point. Does not modify Kira or checkpoints.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_exact_reduction import BASE,POINTS,CHECKPOINT,SOURCE,CERT,modular
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_rank_extension_probe import load_data,specialized,forward,sha

def xor_add(row,source,factor,p):
    for k,v in source.items():
        n=(row.get(k,0)+factor*v)%p
        if n:row[k]=n
        else:row.pop(k,None)

def rank_sparse(rows,p):
    pivots={}
    dependent=[]
    for i,row in enumerate(rows):
        cur=row.copy()
        while cur and min(cur) in pivots:
            lead=min(cur)
            xor_add(cur,pivots[lead],-cur[lead],p)
        if cur:
            lead=min(cur)
            inverse=pow(cur[lead],-1,p)
            pivots[lead]={k:v*inverse%p for k,v in cur.items()}
        else:
            dependent.append(i)
    return len(pivots),dependent

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--checkpoint",type=Path,default=CHECKPOINT)
    ap.add_argument("--input",type=Path,default=SOURCE)
    ap.add_argument("--certificate",type=Path,default=CERT)
    ap.add_argument("--output",type=Path,default=BASE/"vp05_sector202_pivot_trace_rank_audit.json")
    ap.add_argument("--max-records",type=int,default=15)
    args=ap.parse_args()
    if args.max_records<1:ap.error("max-records must be positive")
    if args.output.resolve() in {x.resolve() for x in (args.checkpoint,args.input,args.certificate)}:
        ap.error("Output overlaps an input")
    if args.output.exists():raise FileExistsError("Output already exists: "+str(args.output))
    saved,source,selected=load_data(args)
    cert=json.loads(args.certificate.read_text(encoding="utf-8-sig"))
    if cert.get("point")!=list(POINTS[0]):raise RuntimeError("Unexpected certificate point")
    ids=sorted(selected)
    id_pos={k:i for i,k in enumerate(ids)}
    source_rows={x["global_zero_based"]:x for x in source["rows"]}
    p=POINTS[0][0]
    z,d=sp.symbols("z d")
    original_mod={rid:specialized(source_rows[rid]["terms"],z,d,POINTS[0]) for rid in ids}
    trace_mod=[]
    row_mod=[]
    mismatches=[]
    for index,item in enumerate(saved["pivots"]):
        row=specialized([{"key":k,"coefficient":v} for k,v in item["row"]],z,d,POINTS[0])
        lead=tuple(item["lead"])
        if not row or min(row)!=lead or row[lead]!=1:
            raise RuntimeError("Pivot specialization invalid")
        trace={}
        for rid,raw in item["trace"]:
            rid=int(rid)
            if rid not in id_pos:raise RuntimeError("Pivot trace uses nonselected ID "+str(rid))
            v=modular(expr(raw,z,d),z,d,POINTS[0])
            if v:trace[id_pos[rid]]=v
        replay={}
        for k,v in trace.items():
            xor_add(replay,original_mod[ids[k]],v,p)
        if replay!=row:
            differences=sorted(k for k in set(replay)|set(row) if replay.get(k,0)!=row.get(k,0))
            mismatches.append({"pivot_index":index,"lead":list(lead),
                               "difference_count":len(differences),
                               "first_difference":list(differences[0]) if differences else None})
        trace_mod.append(trace)
        row_mod.append(row)
    trace_rank,trace_dep=rank_sparse(trace_mod,p)
    original_rank,orig_dep=rank_sparse([original_mod[rid] for rid in ids],p)
    pivot_rank,pivot_dep=rank_sparse(row_mod,p)
    report={"status":"SECTOR202_PIVOT_TRACE_RANK_AUDIT_NOT_EXACT_PROOF",
            "point":list(POINTS[0]),"selected_source_rows":len(ids),
            "checkpoint_pivots":len(saved["pivots"]),
            "trace_matrix_rank":trace_rank,
            "original_source_rank":original_rank,
            "pivot_row_rank":pivot_rank,
            "trace_dependent_count":len(trace_dep),
            "original_dependent_count":len(orig_dep),
            "pivot_dependent_count":len(pivot_dep),
            "first_trace_dependent_indices":trace_dep[:args.max_records],
            "first_original_dependent_indices":orig_dep[:args.max_records],
            "first_pivot_dependent_indices":pivot_dep[:args.max_records],
            "modular_pivot_provenance_mismatch_count":len(mismatches),
            "first_modular_provenance_mismatches":mismatches[:args.max_records],
            "checkpoint_sha256":sha(args.checkpoint),
            "source_sha256":sha(args.input),"certificate_sha256":sha(args.certificate),
            "checkpoint_modified":False,"kira_executed":False,
            "exact_target_proven":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as f:
        json.dump(report,f,indent=2,ensure_ascii=True);f.write("\n")
    print("VP05_SECTOR202_PIVOT_TRACE_RANK "+json.dumps(report,ensure_ascii=True),flush=True)

if __name__=="__main__":main()
