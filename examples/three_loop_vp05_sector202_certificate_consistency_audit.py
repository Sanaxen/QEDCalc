"""Read-only finite-field consistency audit of VP05 sector202 target A provenance.

Checks a previously verified original-IBP source multiplier certificate against
literal exported rows and the current target constructor. No elimination.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_ffrank_audit import coefficient
from examples.three_loop_sector203_weight_audit import ROOT, load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P, TARGETS
from examples.three_loop_vp05_sector202_bivariate_candidate_verify import functions
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CERT, CHECKPOINT, SOURCE, FORMULAS, POINTS, modular, target_row,
)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def add(dest, key, value, p):
    result = (dest.get(key, 0) + value) % p
    if result:
        dest[key] = result
    else:
        dest.pop(key, None)

def compare(actual, expected):
    keys = sorted(set(actual) | set(expected))
    differing = [key for key in keys if actual.get(key,0) != expected.get(key,0)]
    return {"matches": not differing, "actual_terms":len(actual),
            "expected_terms":len(expected), "difference_count":len(differing),
            "first_differences":[{"key":list(k),"actual":actual.get(k,0),
                                  "expected":expected.get(k,0)}
                                 for k in differing[:8]]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=SOURCE)
    ap.add_argument("--certificate",type=Path,default=CERT)
    ap.add_argument("--checkpoint",type=Path,default=CHECKPOINT)
    ap.add_argument("--output",type=Path,default=BASE/"vp05_sector202_A_certificate_consistency_audit.json")
    args=ap.parse_args()
    inputs=(args.input,args.certificate,args.checkpoint)
    if args.output.resolve() in {p.resolve() for p in inputs}:
        ap.error("Output must differ from input")
    if args.output.exists():
        raise FileExistsError("Refusing to replace existing result: "+str(args.output))
    saved=json.loads(args.checkpoint.read_text(encoding="utf-8-sig"))
    cert=json.loads(args.certificate.read_text(encoding="utf-8-sig"))
    with gzip.open(args.input,"rt",encoding="utf-8") as stream:
        source=json.load(stream)
    cfg=saved.get("config",{})
    if not (saved.get("status")=="EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF"
            and saved.get("processed")==saved.get("total")==389
            and saved.get("dependent")==0
            and len(saved.get("pivots",[]))==389
            and saved.get("source_pivots_exact_replay_verified") is True
            and cfg.get("target")=="union"
            and cfg.get("source_sha256")==sha(args.input)
            and cfg.get("certificate_sha256")==sha(args.certificate)):
        raise RuntimeError("Checkpoint/hash guard failed")
    if (cert.get("status")!="MODULAR_ORIGINAL_ROW_CERTIFICATE_VERIFIED_NOT_EXACT_PROOF"
            or cert.get("point")!=list(POINTS[0])):
        raise RuntimeError("Certificate or evaluation point mismatch")
    if source.get("status")!="ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED" or len(source.get("rows",[]))!=2241:
        raise RuntimeError("Unexpected source")
    entries=cert.get("target_results",[])
    if len(entries)!=2 or any(e.get("modular_original_replay_verified") is not True for e in entries):
        raise RuntimeError("Unverified certificate targets")
    ids=sorted(set(entries[0]["support_original_ids"])|set(entries[1]["support_original_ids"]))
    if len(ids)!=389 or cfg.get("ids_sha256")!=hashlib.sha256(json.dumps(ids).encode()).hexdigest():
        raise RuntimeError("Certificate selection mismatch")
    rows={r["global_zero_based"]:r for r in source["rows"]}
    if not set(ids).issubset(rows):
        raise RuntimeError("Source missing certified support")
    p,zval,dval=POINTS[0]
    z,d=sp.symbols("z d")
    mod=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
    bits,order=mod.from_kiradb(str(P/"results/kira.db"))
    if order!=5:raise RuntimeError("Unexpected codec ordering")
    codec=mod.WeightCodec(np=12,bits=bits,iord=order,topsectors=[203])
    keys=[(codec.encode(v),139) for v in TARGETS]
    if any(tuple(codec.decode(k[0]))!=v for k,v in zip(keys,TARGETS)):
        raise RuntimeError("Codec roundtrip mismatch")
    expected_fractions=functions(zval,dval)[:2]
    formula_eval=[modular(expr(f,z,d),z,d,POINTS[0]) for f in FORMULAS[:2]]
    fraction_eval=[f.numerator%p*pow(f.denominator%p,-1,p)%p for f in expected_fractions]
    cert_eval=[entries[0]["modular_coeff_C"],entries[0]["modular_coeff_small4"]]
    constructed=target_row("A",keys,[expr(f,z,d) for f in FORMULAS])
    constructed_mod={key:v for key,val in constructed.items()
                     if (v:=modular(val,z,d,POINTS[0]))}
    original_target={}
    add(original_target,keys[0],1,p)
    add(original_target,keys[2],-cert_eval[0],p)
    add(original_target,(4,73),-cert_eval[1],p)
    direct_replay_ast={}
    direct_replay_sympy={}
    discrepancy=[]
    for rid,factor in entries[0]["source_multipliers"]:
        rid=int(rid); factor=int(factor)%p
        if rid not in rows:raise RuntimeError("Certificate references missing row")
        for term in rows[rid]["terms"]:
            key=tuple(term["key"])
            raw=term["coefficient"]
            va=coefficient(raw,zval,dval,p)
            vs=modular(expr(raw,z,d),z,d,POINTS[0])
            if va!=vs and len(discrepancy)<12:
                discrepancy.append({"original_id":rid,"key":list(key),
                                    "ast":va,"sympy":vs,"coefficient":raw[:150]})
            add(direct_replay_ast,key,factor*va,p)
            add(direct_replay_sympy,key,factor*vs,p)
    checks={
        "formula_vs_fraction":formula_eval==fraction_eval,
        "formula_vs_certificate":formula_eval==cert_eval,
        "constructed_vs_certificate_target":compare(constructed_mod,original_target),
        "source_replay_ast_vs_cert_target":compare(direct_replay_ast,original_target),
        "source_replay_sympy_vs_cert_target":compare(direct_replay_sympy,original_target),
        "source_replay_ast_vs_sympy":compare(direct_replay_ast,direct_replay_sympy),
        "first_input_coefficient_discrepancies":discrepancy,
    }
    passed=(checks["formula_vs_fraction"] and checks["formula_vs_certificate"]
            and all(checks[k]["matches"] for k in
                ("constructed_vs_certificate_target",
                 "source_replay_ast_vs_cert_target",
                 "source_replay_sympy_vs_cert_target",
                 "source_replay_ast_vs_sympy")))
    report={"status":"CERTIFICATE_CONSISTENCY_PASS_NOT_EXACT_PROOF" if passed
            else "CERTIFICATE_CONSISTENCY_MISMATCH_INVESTIGATE",
            "point":list(POINTS[0]),"checkpoint_sha256":sha(args.checkpoint),
            "source_sha256":sha(args.input),"certificate_sha256":sha(args.certificate),
            "support_count":len(entries[0]["source_multipliers"]),
            "candidate_coefficients_mod_p":formula_eval,
            "certificate_coefficients_mod_p":cert_eval,
            "checks":checks,"exact_target_proven":False,
            "checkpoint_modified":False,"original_sources_modified":False,"kira_executed":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as stream:
        json.dump(report,stream,indent=2,ensure_ascii=True)
        stream.write("\n")
    print("VP05_SECTOR202_CERTIFICATE_CONSISTENCY "+
          json.dumps({"status":report["status"],"checks":checks,
                      "output":str(args.output),"checkpoint_modified":False}),
          flush=True)

if __name__=="__main__":
    main()
