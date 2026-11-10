"""Diagnose termwise-vs-combined modular replay for a small VP05 pivot.

Read-only original-row audit. Records each original contribution and both
evaluation paths to identify first algebra-homomorphism discrepancy.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE,CHECKPOINT,SOURCE,CERT,POINTS,modular)
from examples.three_loop_vp05_sector202_rank_extension_probe import load_data,sha
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_sector203_ffrank_audit import coefficient

def mod_safe(value,z,d,point):
    try:
        return {"value":modular(value,z,d,point),"error":None}
    except (ZeroDivisionError,ValueError,TypeError) as exc:
        return {"value":None,"error":type(exc).__name__+": "+str(exc)[:100]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--checkpoint",type=Path,default=CHECKPOINT)
    ap.add_argument("--input",type=Path,default=SOURCE)
    ap.add_argument("--certificate",type=Path,default=CERT)
    ap.add_argument("--pivot-index",type=int,default=93)
    ap.add_argument("--max-columns",type=int,default=4)
    ap.add_argument("--max-contributions",type=int,default=30)
    ap.add_argument("--output",type=Path,default=BASE/"vp05_sector202_pivot93_termwise_diagnostic.json")
    args=ap.parse_args()
    if args.pivot_index<0 or not 1<=args.max_columns<=8 or not 1<=args.max_contributions<=80:
        ap.error("Invalid diagnostic bounds")
    if args.output.resolve() in {x.resolve() for x in (args.checkpoint,args.input,args.certificate)}:
        ap.error("Output overlaps input")
    if args.output.exists():raise FileExistsError("Output exists: "+str(args.output))
    saved,source,selected=load_data(args)
    if args.pivot_index>=len(saved["pivots"]):ap.error("Pivot index beyond checkpoint")
    rows={r["global_zero_based"]:r for r in source["rows"]}
    entry=saved["pivots"][args.pivot_index]
    z,d=sp.symbols("z d")
    point=POINTS[0]
    prime,zv,dv=point
    pivot={tuple(k):expr(raw,z,d) for k,raw in entry["row"]}
    trace={int(rid):expr(raw,z,d) for rid,raw in entry["trace"]}
    per_column={}
    for rid,factor in trace.items():
        for term in rows[rid]["terms"]:
            key=tuple(term["key"])
            if key not in per_column:per_column[key]=[]
            per_column[key].append((rid,factor,term["coefficient"]))
    discrepancies=[]
    for key,contributions in sorted(per_column.items()):
        exact_total=sp.S.Zero
        by_term=0
        examples=[]
        for rid,factor,raw in contributions:
            v=expr(raw,z,d)
            exact_total=sp.cancel(exact_total+factor*v)
            fv=mod_safe(factor,z,d,point)
            vv=mod_safe(v,z,d,point)
            product=mod_safe(sp.cancel(factor*v),z,d,point)
            finite_product=(fv["value"]*vv["value"])%prime if fv["value"] is not None and vv["value"] is not None else None
            if finite_product is not None:by_term=(by_term+finite_product)%prime
            if len(examples)<args.max_contributions:
                num,den=sp.fraction(sp.cancel(sp.together(factor*v)))
                examples.append({"original_id":rid,"raw_coefficient":raw[:140],
                                 "trace_expression":str(factor)[:140],
                                 "term_expression":str(v)[:140],
                                 "trace_mod":fv,"raw_mod_sympy":vv,
                                 "raw_mod_ast":coefficient(raw,zv,dv,prime),
                                 "separate_product_mod":finite_product,
                                 "product_mod":product,
                                 "numerator_mod":int(num.subs({z:zv,d:dv}))%prime,
                                 "denominator_mod":int(den.subs({z:zv,d:dv}))%prime})
        combined=mod_safe(exact_total,z,d,point)
        saved=mod_safe(pivot.get(key,sp.S.Zero),z,d,point)
        if combined["value"]!=by_term or saved["value"]!=by_term:
            discrepancies.append({"key":list(key),"count":len(contributions),
                                  "combined_mod":combined,"termwise_mod":by_term,
                                  "saved_mod":saved,
                                  "exact_equal_to_saved":sp.cancel(exact_total-pivot.get(key,sp.S.Zero))==0,
                                  "contributions":examples})
    report={"status":"PIVOT_TERMWISE_EVALUATION_DIAGNOSTIC_NOT_PROOF",
            "point":list(point),"pivot_index":args.pivot_index,
            "pivot_lead":entry["lead"],"trace_support":len(trace),
            "discrepant_column_count":len(discrepancies),
            "first_discrepancies":discrepancies[:args.max_columns],
            "checkpoint_sha256":sha(args.checkpoint),"source_sha256":sha(args.input),
            "certificate_sha256":sha(args.certificate),
            "checkpoint_modified":False,"kira_executed":False,"exact_target_proven":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as f:
        json.dump(report,f,indent=2,ensure_ascii=True);f.write("\n")
    summary={k:report[k] for k in ("status","pivot_index","trace_support","discrepant_column_count")}
    summary["columns"]=[{"key":c["key"],"combined_mod":c["combined_mod"],
                         "termwise_mod":c["termwise_mod"],
                         "saved_mod":c["saved_mod"],"first_contribution":c["contributions"][:2]}
                        for c in report["first_discrepancies"]]
    summary["output"]=str(args.output)
    print("VP05_SECTOR202_PIVOT_TERMWISE "+json.dumps(summary,ensure_ascii=True),flush=True)

if __name__=="__main__":main()
