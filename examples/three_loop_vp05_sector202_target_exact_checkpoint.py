"""Resumable, bounded exact sector202 A/B target elimination.

This is a NEW checkpoint distinct from the immutable 389-pivot source
checkpoint. No target proof is claimed until zero remainder and an exact
original-IBP reconstruction both pass. Checkpoint resume revalidates source
hashes, algebraic modular invariants, and the recorded reduction path.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_weight_audit import ROOT, load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P, TARGETS
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_rank_extension_probe import load_data
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CERT, CHECKPOINT, SOURCE, FORMULAS, POINTS, modular, target_row,
    add, replay, sha,
)

def encoded(row):
    return [[list(k), str(v)] for k, v in sorted(row.items())]

def decoded(items, z, d):
    result={}
    for key, val in items:
        k=tuple(key)
        if k in result:
            raise RuntimeError("Duplicate saved residual key")
        v=expr(val,z,d)
        if v == 0:
            raise RuntimeError("Saved residual has exact zero coefficient")
        result[k]=v
    return result

def trace_encoded(row):
    return [[rid,str(v)] for rid,v in sorted(row.items())]

def trace_decoded(items,z,d):
    result={}
    for rid,val in items:
        rid=int(rid)
        if rid in result:
            raise RuntimeError("Duplicate original source ID in trace")
        v=expr(val,z,d)
        if v == 0:
            raise RuntimeError("Saved provenance has exact zero coefficient")
        result[rid]=v
    return result

def metrics(remaining, source):
    row_chars=max((len(str(v)) for v in remaining.values()),default=0)
    source_chars=max((len(str(v)) for v in source.values()),default=0)
    return {"remainder_terms":len(remaining),"original_support":len(source),
            "row_expression_chars":row_chars,
            "source_expression_chars":source_chars,
            "max_expression_chars":max(row_chars,source_chars),
            "lead":list(min(remaining)) if remaining else None}

def assert_modular_invariant(initial, remaining, trace, originals, z, d, point):
    p=point[0]
    actual={k:modular(v,z,d,point) for k,v in remaining.items()}
    actual={k:v for k,v in actual.items() if v}
    for rid,weight in trace.items():
        if rid not in originals:
            raise RuntimeError("Checkpoint provenance references unknown original source")
        factor=modular(weight,z,d,point)
        for term in originals[rid]["terms"]:
            k=tuple(term["key"])
            n=modular(expr(term["coefficient"],z,d),z,d,point)
            v=(actual.get(k,0)+factor*n)%p
            if v:actual[k]=v
            else:actual.pop(k,None)
    desired={k:modular(v,z,d,point) for k,v in initial.items()}
    desired={k:v for k,v in desired.items() if v}
    if actual != desired:
        different=sorted(k for k in set(actual)|set(desired)
                         if actual.get(k,0)!=desired.get(k,0))
        raise AssertionError("Target/trace/residual modular invariant failure: "+
                             str(different[:3]))

def atomic_create(path,payload):
    if path.exists():
        raise FileExistsError("Refusing to overwrite: "+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+".tmp")
    if tmp.exists():
        raise FileExistsError("Stale temp checkpoint exists: "+str(tmp))
    with tmp.open("x",encoding="utf-8") as handle:
        json.dump(payload,handle,ensure_ascii=True,separators=(",",":"))
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp,path)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-checkpoint",type=Path,default=CHECKPOINT)
    ap.add_argument("--input",type=Path,default=SOURCE)
    ap.add_argument("--certificate",type=Path,default=CERT)
    ap.add_argument("--target",choices=("A","B"),default="A")
    ap.add_argument("--state",type=Path,default=BASE/"vp05_sector202_A_exact_target_state.json")
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--new-steps",type=int,default=8)
    ap.add_argument("--max-columns",type=int,default=256)
    ap.add_argument("--max-support",type=int,default=400)
    ap.add_argument("--max-expression-chars",type=int,default=7500)
    ap.add_argument("--max-steps-total",type=int,default=128)
    ap.add_argument("--progress-every",type=int,default=1)
    args=ap.parse_args()
    if not 1<=args.new_steps<=16 or min(args.max_columns,args.max_support,
                                        args.max_expression_chars,args.max_steps_total,args.progress_every)<1:
        ap.error("Invalid safety limit")
    if args.state.resolve() in {p.resolve() for p in (args.source_checkpoint,args.input,args.certificate)}:
        ap.error("Target state must be distinct from all input artifacts")
    if args.target=="B" and args.state.name=="vp05_sector202_A_exact_target_state.json":
        ap.error("Provide a distinct --state path for Target B")
    if args.resume and not args.state.exists():
        raise FileNotFoundError("Missing state to resume")
    if not args.resume and args.state.exists():
        raise FileExistsError("State exists; use --resume or a new path")
    # load_data performs source/checkpoint/certificate hash, status and selector
    # checks. It also expects a fresh diagnostic output path, but this runner
    # only writes its separate --state. Supply a never-used validation path
    # so resumed states aren't rejected by load_data's output-exists guard.
    args.checkpoint=args.source_checkpoint
    args.output=args.state.with_name(args.state.name+".source_validation_unused")
    if args.output.exists():
        raise FileExistsError("Reserved validation path exists: "+str(args.output))
    saved, source_rows, selected=load_data(args)
    originals={r["global_zero_based"]:r for r in source_rows["rows"]}
    z,d=sp.symbols("z d")
    mod=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
    bits,order=mod.from_kiradb(str(P/"results/kira.db"))
    if order!=5:raise RuntimeError("Unexpected Kira ordering")
    codec=mod.WeightCodec(np=12,bits=bits,iord=order,topsectors=[203])
    keys=[(codec.encode(x),139) for x in TARGETS]
    if any(tuple(codec.decode(k[0]))!=v for k,v in zip(keys,TARGETS)):
        raise RuntimeError("Target codec roundtrip mismatch")
    initial=target_row(args.target,keys,[expr(raw,z,d) for raw in FORMULAS])
    pivots={}
    for item in saved["pivots"]:
        lead=tuple(item["lead"])
        row=decoded(item["row"],z,d)
        trace=trace_decoded(item["trace"],z,d)
        if lead in pivots or min(row)!=lead or sp.cancel(row[lead]-1)!=0:
            raise RuntimeError("Source checkpoint pivot invariant failure")
        pivots[lead]=(row,trace)
    config={"target":args.target,"source_checkpoint_sha256":sha(args.source_checkpoint),
            "source_sha256":sha(args.input),"certificate_sha256":sha(args.certificate),
            "initial_sha256":hashlib.sha256(json.dumps(encoded(initial)).encode()).hexdigest(),
            "max_columns":args.max_columns,"max_support":args.max_support,
            "max_expression_chars":args.max_expression_chars,
            "max_steps_total":args.max_steps_total}
    if args.resume:
        state=json.loads(args.state.read_text(encoding="utf-8-sig"))
        if (state.get("version")!=1 or state.get("config")!=config
                or state.get("status") not in ("EXACT_TARGET_PREFIX_NOT_PROOF",
                                               "EXACT_TARGET_CAP_REACHED_NOT_PROOF")
                or state.get("exact_target_proven") is not False):
            raise RuntimeError("Checkpoint config/status/hash mismatch")
        steps=state["steps"]
        if not isinstance(steps,int) or steps<0 or steps>args.max_steps_total:
            raise RuntimeError("Invalid target step index")
        remaining=decoded(state["remaining"],z,d)
        source=trace_decoded(state["source"],z,d)
        history=state.get("pivot_path",[])
        if len(history)!=steps or any(tuple(x) not in pivots for x in history):
            raise RuntimeError("Saved pivot path/step count invalid")
        m=metrics(remaining,source)
        if (m["remainder_terms"]>args.max_columns or
                m["original_support"]>args.max_support or
                m["max_expression_chars"]>args.max_expression_chars):
            raise RuntimeError("Saved checkpoint exceeds safety limits")
        for point in POINTS:
            assert_modular_invariant(initial,remaining,source,originals,z,d,point)
    else:
        steps=0
        remaining=dict(initial)
        source={}
        history=[]
    def save(status):
        data={"version":1,"status":status,"config":config,
              "steps":steps,"remaining":encoded(remaining),
              "source":trace_encoded(source),"pivot_path":history,
              "metrics":metrics(remaining,source),
              "exact_target_proven":False,
              "original_source_replay_proven":False,
              "protected_source_checkpoint_modified":False}
        # A valid state represents a single fully completed elimination.
        # Overwrite ONLY our separate target state after the first exclusive
        # create; the protected 389-pivot source checkpoint is never written.
        if args.state.exists():
            tmp=args.state.with_name(args.state.name+".tmp")
            if tmp.exists():raise FileExistsError(str(tmp))
            with tmp.open("x",encoding="utf-8") as handle:
                json.dump(data,handle,ensure_ascii=True,separators=(",",":"))
                handle.flush();os.fsync(handle.fileno())
            os.replace(tmp,args.state)
        else:
            atomic_create(args.state,data)
    if not args.resume:save("EXACT_TARGET_PREFIX_NOT_PROOF")
    completed_new=0
    status="EXACT_TARGET_PREFIX_NOT_PROOF"
    while remaining and completed_new<args.new_steps and steps<args.max_steps_total:
        lead=min(remaining)
        if lead not in pivots:
            status="EXACT_TARGET_UNRESOLVED_LEAD_NOT_PROOF"
            break
        p_row,p_trace=pivots[lead]
        fac=remaining[lead]
        next_remaining=dict(remaining)
        next_source=dict(source)
        add(next_remaining,p_row,-fac)
        add(next_source,p_trace,fac)
        next_metrics=metrics(next_remaining,next_source)
        if (next_metrics["remainder_terms"]>args.max_columns or
                next_metrics["original_support"]>args.max_support or
                next_metrics["max_expression_chars"]>args.max_expression_chars):
            status="EXACT_TARGET_CAP_REACHED_NOT_PROOF"
            print("VP05_SECTOR202_TARGET_EXACT_CAP "+json.dumps(
                {"attempted_step":steps+1,"last_saved_step":steps,
                 "candidate_metrics":next_metrics,"limits":{
                  "max_columns":args.max_columns,"max_support":args.max_support,
                  "max_expression_chars":args.max_expression_chars}},ensure_ascii=True),flush=True)
            break
        remaining=next_remaining
        source=next_source
        steps+=1
        completed_new+=1
        history.append(list(lead))
        if steps%args.progress_every==0:
            print("VP05_SECTOR202_TARGET_EXACT_PROGRESS "+json.dumps(
                {"target":args.target,"steps":steps,**next_metrics},ensure_ascii=True),flush=True)
        save("EXACT_TARGET_PREFIX_NOT_PROOF")
    if not remaining:
        # Final independent rational-function replay is mandatory, even
        # though all three modular point invariants may be satisfied.
        if not replay(source,originals,z,d,initial):
            raise AssertionError("Exact original-IBP target replay failed")
        certificate={"status":"EXACT_SINGLE_TARGET_PROVEN","target":args.target,
                     "steps":steps,"source_checkpoint_sha256":config["source_checkpoint_sha256"],
                     "source_sha256":config["source_sha256"],
                     "certificate_sha256":config["certificate_sha256"],
                     "original_source_replay_verified":True,
                     "source_multipliers":trace_encoded(source),
                     "target_terms":encoded(initial)}
        proof_path=args.state.with_name(args.state.stem+"_proof.json")
        if proof_path.exists():raise FileExistsError("Proof file already exists")
        atomic_create(proof_path,certificate)
        print("VP05_SECTOR202_TARGET_EXACT_RESULT "+json.dumps(
            {"status":"EXACT_SINGLE_TARGET_PROVEN","target":args.target,
             "steps":steps,"proof":str(proof_path),"protected_checkpoint_modified":False}),flush=True)
        return
    if status=="EXACT_TARGET_CAP_REACHED_NOT_PROOF":
        save(status)
    else:
        save("EXACT_TARGET_PREFIX_NOT_PROOF")
    print("VP05_SECTOR202_TARGET_EXACT_RESULT "+json.dumps(
        {"status":status,"target":args.target,"steps":steps,
         "steps_this_run":completed_new,**metrics(remaining,source),
         "state":str(args.state),"exact_target_proven":False,
         "protected_checkpoint_modified":False}),flush=True)

if __name__=="__main__":main()
