"""Read-only exact-vs-modular spot audit for sector202 pivot provenance mismatches.

For a bounded set of pivots, replay just the finite-field discrepant columns
symbolically from the literal exported original equations, and compare both
symbolic exact differences and specialized values. Never write inputs.
"""
from __future__ import annotations
import argparse,gzip,json
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_exact_reduction import BASE,CHECKPOINT,SOURCE,CERT,POINTS,modular
from examples.three_loop_vp05_sector202_rank_extension_probe import load_data,specialized,sha
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_sector203_ffrank_audit import coefficient

def accumulate(dest,key,value,p):
    v=(dest.get(key,0)+value)%p
    if v:dest[key]=v
    else:dest.pop(key,None)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--checkpoint",type=Path,default=CHECKPOINT)
    ap.add_argument("--input",type=Path,default=SOURCE)
    ap.add_argument("--certificate",type=Path,default=CERT)
    ap.add_argument("--pivot-indices",type=str,default="34,58,93")
    ap.add_argument("--max-columns",type=int,default=8)
    ap.add_argument("--output",type=Path,default=BASE/"vp05_sector202_pivot_mismatch_exact_spot_audit.json")
    args=ap.parse_args()
    indices=[int(x.strip()) for x in args.pivot_indices.split(",")]
    if not indices or len(indices)>5 or len(set(indices))!=len(indices) or min(indices)<0 or args.max_columns<1 or args.max_columns>16:
        ap.error("Choose 1..5 distinct nonnegative pivot indices and 1..16 columns")
    if args.output.resolve() in {x.resolve() for x in (args.checkpoint,args.input,args.certificate)}:
        ap.error("Cannot overwrite an input")
    if args.output.exists():raise FileExistsError("Output exists: "+str(args.output))
    saved,source,selected=load_data(args)
    if max(indices)>=len(saved["pivots"]):ap.error("Pivot index out of bounds")
    rows={r["global_zero_based"]:r for r in source["rows"]}
    p,zv,dv=POINTS[0]
    z,d=sp.symbols("z d")
    findings=[]
    for idx in indices:
        pivot=saved["pivots"][idx]
        pivot_expr={tuple(k):expr(raw,z,d) for k,raw in pivot["row"]}
        trace_expr={int(rid):expr(raw,z,d) for rid,raw in pivot["trace"]}
        pivot_mod={k:v for k,value in pivot_expr.items()
                   if (v:=modular(value,z,d,POINTS[0]))}
        trace_mod={rid:v for rid,value in trace_expr.items()
                   if (v:=modular(value,z,d,POINTS[0]))}
        replay_mod={}
        for rid,factor in trace_mod.items():
            if rid not in rows:raise RuntimeError("Unknown original row in trace")
            terms=specialized(rows[rid]["terms"],z,d,POINTS[0])
            for key,value in terms.items():accumulate(replay_mod,key,factor*value,p)
        diff=[key for key in sorted(set(replay_mod)|set(pivot_mod))
              if replay_mod.get(key,0)!=pivot_mod.get(key,0)]
        entries=[]
        for key in diff[:args.max_columns]:
            exact_sum=sp.S.Zero
            evaluated_separately=0
            for rid,trace_factor in trace_expr.items():
                raw_sum=sp.S.Zero
                for term in rows[rid]["terms"]:
                    if tuple(term["key"])==key:
                        raw_sum+=expr(term["coefficient"],z,d)
                if raw_sum!=0:
                    exact_sum=sp.cancel(exact_sum+trace_factor*raw_sum)
                    evaluated_separately=(evaluated_separately+
                        modular(trace_factor,z,d,POINTS[0])*modular(raw_sum,z,d,POINTS[0]))%p
            expected=pivot_expr.get(key,sp.S.Zero)
            exact_delta=sp.cancel(exact_sum-expected)
            report={"column":list(key),"saved_mod":pivot_mod.get(key,0),
                    "replay_mod":replay_mod.get(key,0),
                    "modular_exact_sum":modular(exact_sum,z,d,POINTS[0]),
                    "modular_saved_expr":modular(expected,z,d,POINTS[0]),
                    "modular_separate_sum":evaluated_separately,
                    "exact_delta_is_zero":exact_delta==0,
                    "delta_expression_chars":len(str(exact_delta)),
                    "delta_preview":str(exact_delta)[:240]}
            entries.append(report)
        findings.append({"pivot_index":idx,"lead":pivot["lead"],
                         "trace_support":len(trace_expr),"difference_count":len(diff),
                         "first_columns":entries})
    result={"status":"EXACT_SPOT_PIVOT_MISMATCH_DIAGNOSTIC_NOT_PROOF",
            "point":list(POINTS[0]),"checkpoint_sha256":sha(args.checkpoint),
            "source_sha256":sha(args.input),"certificate_sha256":sha(args.certificate),
            "findings":findings,"checkpoint_modified":False,
            "kira_executed":False,"exact_target_proven":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2,ensure_ascii=True);f.write("\n")
    print("VP05_SECTOR202_PIVOT_MISMATCH_SPOT "+json.dumps(result,ensure_ascii=True),flush=True)

if __name__=="__main__":main()
