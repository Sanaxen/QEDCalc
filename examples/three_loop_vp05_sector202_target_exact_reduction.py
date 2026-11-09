"""Read-only A/B rational-function reduction against VP05 sector202 exact pivots.

Modular evaluations are diagnostics, never a symbolic proof.
A proof needs exact zero remainder and an original-IBP source replay.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_weight_audit import ROOT, load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P, TARGETS
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr

BASE = ROOT / "output/three_loop_integral_family_audit"
CHECKPOINT = BASE / "vp05_sector202_exact_support_checkpoint_support400_col256.json"
SOURCE = BASE / "vp05_sector202_exact_source_rows.json.gz"
CERT = BASE / "vp05_sector202_modular_provenance_certificate.json"
FORMULAS = (
    "4*(d*z+4*d-8)/(3*(3*d-4))",
    "(d*z+10*d-z-14)/(3*d-4)",
    "(d*d*z*z+8*d*d*z+16*d*d-5*d*z*z-8*d*z-16*d+12*z*z-32*z)/(3*(d-1)*(3*d-4))",
    "(d*d*z*z+2*d*d*z+10*d*d-4*d*z*z+2*d*z-22*d+4*z*z-8*z+12)/((d-1)*(3*d-4))",
)
POINTS = ((1000003, 17, 7), (1000033, 19, 11), (1000037, 21, 15))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def add(dest, source, factor, prime=None):
    for k, v in source.items():
        x = dest.get(k, 0) + factor*v
        x = x % prime if prime else sp.cancel(x)
        if x == 0: dest.pop(k, None)
        else: dest[k] = x

def modular(value, z, d, point):
    p, zv, dv = point
    n, den = sp.fraction(sp.cancel(sp.together(value)))
    a = int(n.subs({z:zv,d:dv})) % p
    b = int(den.subs({z:zv,d:dv})) % p
    if b == 0: raise ZeroDivisionError("Singular modular specialization")
    return a*pow(b,-1,p)%p

def target_row(label, keys, values):
    idx = 0 if label == "A" else 1
    row = {}
    add(row, {keys[idx]:sp.S.One}, 1)
    add(row, {keys[2]:values[idx*2]}, -1)
    add(row, {(4,73):values[idx*2+1]}, -1)
    return row

def reduce(row, pivots, max_steps, max_columns, max_support, max_chars, prime=None):
    remaining = dict(row)
    source = {}
    steps = 0
    while remaining:
        lead = min(remaining)
        if lead not in pivots:
            return remaining, source, steps, "UNRESOLVED_LEAD"
        if steps >= max_steps:
            return remaining, source, steps, "STEP_CAP"
        prow, ptrace = pivots[lead]
        factor = remaining[lead]
        add(remaining, prow, -factor, prime)
        add(source, ptrace, factor, prime)
        steps += 1
        if len(remaining)>max_columns or len(source)>max_support:
            return remaining, source, steps, "FILL_OR_SUPPORT_CAP"
        if prime is None and max((len(str(v)) for v in
             list(remaining.values())+list(source.values())),default=0)>max_chars:
            return remaining, source, steps, "EXPRESSION_CAP"
    return remaining, source, steps, "ZERO_REMAINDER"

def replay(source, rows, z, d, expected):
    actual = {}
    for rid, factor in sorted(source.items()):
        if rid not in rows: raise AssertionError("Unknown original source row")
        for term in rows[rid]["terms"]:
            add(actual,{tuple(term["key"]):expr(term["coefficient"],z,d)},factor)
    return set(actual)==set(expected) and all(
        sp.cancel(actual[k]-expected[k])==0 for k in expected)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint",type=Path,default=CHECKPOINT)
    ap.add_argument("--input",type=Path,default=SOURCE)
    ap.add_argument("--certificate",type=Path,default=CERT)
    ap.add_argument("--target",choices=("A","B","both"),default="both")
    ap.add_argument("--mode",choices=("modular","exact"),default="modular")
    ap.add_argument("--max-steps",type=int,default=16)
    ap.add_argument("--max-columns",type=int,default=256)
    ap.add_argument("--max-support",type=int,default=400)
    ap.add_argument("--max-expression-chars",type=int,default=7500)
    ap.add_argument("--output",type=Path)
    args = ap.parse_args()
    if min(args.max_steps,args.max_columns,args.max_support,args.max_expression_chars)<1:
        ap.error("Safety caps must be positive")
    if args.output is None:
        args.output=BASE/("vp05_sector202_target_%s_%s.json"%(args.target.lower(),args.mode))
    if args.output.resolve() in {v.resolve() for v in (args.checkpoint,args.input,args.certificate)}:
        ap.error("Output may not overwrite an input")
    if args.output.exists(): raise FileExistsError("Result exists: "+str(args.output))
    saved=json.loads(args.checkpoint.read_text(encoding="utf-8-sig"))
    with gzip.open(args.input,"rt",encoding="utf-8") as f: source=json.load(f)
    cert=json.loads(args.certificate.read_text(encoding="utf-8-sig"))
    cfg=saved.get("config",{})
    if not (saved.get("status")=="EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF"
         and saved.get("processed")==saved.get("total")==389
         and saved.get("dependent")==0 and len(saved.get("pivots",[]))==389
         and saved.get("source_pivots_exact_replay_verified") is True
         and cfg.get("target")=="union"
         and cfg.get("source_sha256")==sha(args.input)
         and cfg.get("certificate_sha256")==sha(args.certificate)):
        raise RuntimeError("Checkpoint status or input hashes mismatch")
    if source.get("status")!="ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED" or len(source["rows"])!=2241:
        raise RuntimeError("Unexpected exact source format")
    if cert.get("status")!="MODULAR_ORIGINAL_ROW_CERTIFICATE_VERIFIED_NOT_EXACT_PROOF":
        raise RuntimeError("Unexpected modular certificate")
    t=cert["target_results"]
    if len(t)!=2: raise RuntimeError("Missing A/B modular supports")
    ids=sorted(set(t[0]["support_original_ids"])|set(t[1]["support_original_ids"]))
    if len(ids)!=389 or cfg.get("ids_sha256")!=hashlib.sha256(json.dumps(ids).encode()).hexdigest():
        raise RuntimeError("Source selection mismatch")
    rows={r["global_zero_based"]:r for r in source["rows"]}
    z,d=sp.symbols("z d")
    mod=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
    bits,ordering=mod.from_kiradb(str(P/"results/kira.db"))
    if ordering!=5: raise RuntimeError("Unexpected Kira ordering")
    codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    keys=[(codec.encode(v),139) for v in TARGETS]
    if any(tuple(codec.decode(key[0]))!=v for key,v in zip(keys,TARGETS)):
        raise RuntimeError("Target weight codec mismatch")
    coeffs=[expr(raw,z,d) for raw in FORMULAS]
    pivots={}
    for item in saved["pivots"]:
        lead=tuple(item["lead"])
        if lead in pivots: raise RuntimeError("Duplicate pivot")
        row={tuple(k):expr(v,z,d) for k,v in item["row"]}
        trace={int(k):expr(v,z,d) for k,v in item["trace"]}
        if min(row)!=lead or sp.cancel(row[lead]-1)!=0:
            raise RuntimeError("Invalid normalized pivot")
        pivots[lead]=(row,trace)
    results=[]
    for label in (("A","B") if args.target=="both" else (args.target,)):
        initial=target_row(label,keys,coeffs)
        if args.mode=="modular":
            trials=[]
            for point in POINTS:
                try:
                    prime=point[0]
                    pb={}
                    for lead,(row,trace) in pivots.items():
                        r={k:q for k,v in row.items() if (q:=modular(v,z,d,point))}
                        tr={k:q for k,v in trace.items() if (q:=modular(v,z,d,point))}
                        if r.get(lead)!=1: raise RuntimeError("Modular pivot not normalized")
                        pb[lead]=(r,tr)
                    ini={k:q for k,v in initial.items() if (q:=modular(v,z,d,point))}
                    rem,provenance,steps,status=reduce(ini,pb,args.max_steps,args.max_columns,
                        args.max_support,args.max_expression_chars,prime)
                    trials.append({"point":point,"status":status,"steps":steps,
                                   "remainder_terms":len(rem),"support":len(provenance)})
                except (ZeroDivisionError,ValueError) as e:
                    trials.append({"point":point,"status":"SINGULAR_POINT","error":str(e)})
            item={"target":label,"modular_diagnostics":trials,"exact_proven":False}
        else:
            rem,provenance,steps,status=reduce(initial,pivots,args.max_steps,
                args.max_columns,args.max_support,args.max_expression_chars)
            valid=None
            if status=="ZERO_REMAINDER":
                valid=replay(provenance,rows,z,d,initial)
                if not valid: raise AssertionError("Exact source replay mismatch")
            item={"target":label,"status":status,"steps":steps,
                "remainder_terms":len(rem),"original_support":len(provenance),
                "original_replay_verified":valid,
                "exact_proven":status=="ZERO_REMAINDER" and valid is True}
            if item["exact_proven"]:
                item["source_multipliers"]=[[k,str(v)] for k,v in sorted(provenance.items())]
                item["target_terms"]=[[list(k),str(v)] for k,v in sorted(initial.items())]
            else:
                item["unresolved_lead"]=list(min(rem)) if rem else None
        results.append(item)
        print("VP05_SECTOR202_TARGET_REDUCTION "+json.dumps(item,ensure_ascii=True),flush=True)
    complete=(args.mode=="exact" and args.target=="both"
             and all(x["exact_proven"] for x in results))
    single=(args.mode=="exact" and args.target!="both" and results[0]["exact_proven"])
    status=("EXACT_TARGET_PROVEN" if complete else
            "EXACT_SINGLE_TARGET_PROVEN" if single else "TARGET_DIAGNOSTIC_OR_INCOMPLETE_NOT_PROOF")
    report={"status":status,"mode":args.mode,"checkpoint_sha256":sha(args.checkpoint),
        "source_sha256":sha(args.input),"certificate_sha256":sha(args.certificate),
        "target_definitions":[list(v) for v in TARGETS],"candidate_formulas":FORMULAS,
        "results":results,"exact_target_reduction_proven":complete,
        "checkpoint_modified":False,"kira_executed":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as out:
        json.dump(report,out,indent=2,ensure_ascii=True)
        out.write("\n")
    print("VP05_SECTOR202_TARGET_REPORT "+json.dumps(
        {"status":status,"output":str(args.output),"exact_target_reduction_proven":complete,
         "checkpoint_modified":False}),flush=True)

if __name__=="__main__":
    main()
