"""Audit whether certified VP05 sector202 source rows lie in the saved pivot span.

Read-only, single finite-field point, no Kira or symbolic elimination.
The output locates the first discrepancy between certified original IBP rows
and the checkpoint basis. All conclusions are diagnostic, not exact proofs.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_ffrank_audit import coefficient
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_target_exact_reduction import BASE, CHECKPOINT, SOURCE, CERT, POINTS, modular
from examples.three_loop_vp05_sector202_rank_extension_probe import forward, load_data, specialized, sha

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--checkpoint",type=Path,default=CHECKPOINT)
    parser.add_argument("--input",type=Path,default=SOURCE)
    parser.add_argument("--certificate",type=Path,default=CERT)
    parser.add_argument("--output",type=Path,default=BASE/"vp05_sector202_A_source_basis_membership.json")
    parser.add_argument("--max-source-rows",type=int,default=389)
    parser.add_argument("--max-steps",type=int,default=1024)
    parser.add_argument("--max-columns",type=int,default=1024)
    parser.add_argument("--max-records",type=int,default=20)
    args=parser.parse_args()
    if min(args.max_source_rows,args.max_steps,args.max_columns,args.max_records)<1:
        parser.error("All diagnostic caps must be positive")
    if args.output.resolve() in {x.resolve() for x in (args.input,args.checkpoint,args.certificate)}:
        parser.error("Output collides with a protected input")
    if args.output.exists():
        raise FileExistsError("Result exists: "+str(args.output))
    saved,source,selected=load_data(args)
    cert=json.loads(args.certificate.read_text(encoding="utf-8-sig"))
    if cert.get("point")!=list(POINTS[0]):
        raise RuntimeError("Unexpected finite-field point")
    targets=cert["target_results"]
    if targets[0].get("modular_original_replay_verified") is not True:
        raise RuntimeError("A original replay not verified in certificate")
    verified_ids=sorted(set(targets[0]["support_original_ids"]))
    if len(verified_ids)!=339 or not set(verified_ids).issubset(selected):
        raise RuntimeError("A certificate support and 389-row selection disagree")
    rows={r["global_zero_based"]:r for r in source["rows"]}
    point=POINTS[0]
    z,d=sp.symbols("z d")
    basis={}
    for item in saved["pivots"]:
        lead=tuple(item["lead"])
        row=specialized([{"key":k,"coefficient":v} for k,v in item["row"]],z,d,point)
        if lead in basis or min(row)!=lead or row[lead]!=1:
            raise RuntimeError("Saved pivot specialization invalid")
        basis[lead]=row
    checked=0
    failed=[]
    successes=0
    count_by_status={}
    for rid in verified_ids[:args.max_source_rows]:
        original=specialized(rows[rid]["terms"],z,d,point)
        remaining,steps,status=forward(original,basis,point[0],args.max_steps,args.max_columns)
        checked+=1
        count_by_status[status]=count_by_status.get(status,0)+1
        if status=="ZERO_REMAINDER":
            successes+=1
        else:
            failed.append({"original_id":rid,"status":status,"steps":steps,
                           "initial_terms":len(original),"remaining_terms":len(remaining),
                           "first_lead":list(min(remaining)) if remaining else None})
    report={"status":"CERTIFIED_SOURCE_BASIS_MEMBERSHIP_DIAGNOSTIC_NOT_PROOF",
        "point":list(point),"checkpoint_sha256":sha(args.checkpoint),
        "source_sha256":sha(args.input),"certificate_sha256":sha(args.certificate),
        "certified_A_support":len(verified_ids),"requested_source_limit":args.max_source_rows,
        "checked":checked,"reduced_to_zero":successes,
        "failed_count":len(failed),"counts":count_by_status,
        "first_failures":failed[:args.max_records],
        "all_checked_reduced_to_zero":checked==len(verified_ids) and not failed,
        "exact_target_proven":False,"checkpoint_modified":False,"kira_executed":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as stream:
        json.dump(report,stream,indent=2,ensure_ascii=True)
        stream.write("\n")
    print("VP05_SECTOR202_A_SOURCE_BASIS_MEMBERSHIP "+json.dumps(report,ensure_ascii=True),flush=True)

if __name__=="__main__":
    main()
