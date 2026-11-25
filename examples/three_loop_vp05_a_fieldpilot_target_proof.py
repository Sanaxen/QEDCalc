"""Exact A-only target identity from the audited 339-row fieldpilot checkpoint.

No modular proof, no Kira, no checkpoint mutation. The field reduction
must have zero remainder and independent SymPy original-source replay.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import os
import time
from pathlib import Path

import sympy as sp
from sympy.polys.fields import field
from examples import three_loop_vp05_sector202_target_exact_reduction as exact
from examples import three_loop_vp05_sector202_a_exact_batch as batch

PIN = "945547ba7e166d41932041d2ca34917c7dacf883b20765e7551d013a863ff755"
CHECKPOINT = batch.project("fieldpilot")[0]
OUTPUT = exact.BASE / "vp05_sector202_target_a_fieldpilot_exact_proof.json"
MAX_STEPS = 339
MAX_COLUMNS = 256
MAX_SUPPORT = 339

def reduce_field(initial, pivots, *, max_steps=MAX_STEPS,
                 max_columns=MAX_COLUMNS, max_support=MAX_SUPPORT,
                 progress=False):
    f, _, _ = field("z,d", sp.QQ)
    remaining = {k:f.from_expr(v) for k,v in initial.items() if v != 0}
    provenance = {}
    steps = 0
    def add(dest, src, factor):
        for k,v in src.items():
            x = dest.get(k, f.zero) + factor*f.from_expr(v)
            if x == f.zero:
                dest.pop(k, None)
            else:
                dest[k] = x
    while remaining:
        lead = min(remaining)
        if lead not in pivots:
            raise RuntimeError("UNRESOLVED_LEAD: " + repr(lead))
        if steps >= max_steps:
            raise RuntimeError("STEP_CAP")
        prow, ptrace = pivots[lead]
        factor = remaining[lead]
        if progress:
            print("VP05_A_TARGET_PIVOT_BEGIN "+json.dumps(
                {"step":steps+1,"lead":list(lead)}),flush=True)
        add(remaining, prow, -factor)
        add(provenance, ptrace, factor)
        if lead in remaining or (remaining and min(remaining) <= lead):
            raise AssertionError("Pivot order failed to advance")
        steps += 1
        if len(remaining)>max_columns or len(provenance)>max_support:
            raise RuntimeError("FILL_OR_SUPPORT_CAP")
        if progress:
            print("VP05_A_TARGET_PIVOT_COMPLETE "+json.dumps(
                {"step":steps,"remainder_terms":len(remaining),
                 "original_support":len(provenance)}),flush=True)
    return {k:v.as_expr() for k,v in provenance.items()},steps

def run():
    batch.preflight()
    protected = {CHECKPOINT:PIN, exact.SOURCE:batch.SOURCE_SHA,
                 exact.CERT:batch.CERT_SHA}
    for path, digest in protected.items():
        if batch.sha(path) != digest:
            raise RuntimeError("Protected input SHA256 mismatch: "+str(path))
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise FileExistsError("Proof output already exists; preserve for audit")
    state = batch.checkpoint_state(CHECKPOINT)
    if state["processed"] != 339 or state["rank"] != 339 or state["dependent"] != 0:
        raise RuntimeError("Expected completed A-only 339-row checkpoint")
    saved = json.loads(CHECKPOINT.read_text(encoding="utf-8-sig"))
    cert = json.loads(exact.CERT.read_text(encoding="utf-8-sig"))
    with gzip.open(exact.SOURCE,"rt",encoding="utf-8") as fh:
        source = json.load(fh)
    if source.get("status")!="ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED" or len(source["rows"])!=2241:
        raise RuntimeError("Unexpected original IBP export")
    ids = sorted(cert["target_results"][0]["support_original_ids"])
    if len(ids)!=339 or len(set(ids))!=339 or hashlib.sha256(json.dumps(ids).encode()).hexdigest()!=saved["config"]["ids_sha256"]:
        raise RuntimeError("Unexpected A source selection")
    rows = {r["global_zero_based"]:r for r in source["rows"]}
    if not set(ids).issubset(rows):
        raise RuntimeError("Missing original source ID")
    z,d=sp.symbols("z d")
    mod=exact.load_codec((exact.ROOT/"output/tools/pyred_weight.py").resolve())
    bits,ordering=mod.from_kiradb(str(exact.P/"results/kira.db"))
    if ordering!=5:
        raise RuntimeError("Unexpected Kira ordering")
    codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    keys=[(codec.encode(v),139) for v in exact.TARGETS]
    if any(tuple(codec.decode(k[0]))!=v for k,v in zip(keys,exact.TARGETS)):
        raise RuntimeError("Target weight codec mismatch")
    initial=exact.target_row("A",keys,[exact.expr(v,z,d) for v in exact.FORMULAS])
    pivots={}
    for item in saved["pivots"]:
        lead=tuple(item["lead"])
        row={tuple(k):exact.expr(v,z,d) for k,v in item["row"]}
        trace={int(k):exact.expr(v,z,d) for k,v in item["trace"]}
        if lead in pivots or not row or min(row)!=lead or sp.cancel(row[lead]-1)!=0:
            raise RuntimeError("Invalid normalized pivot")
        if not set(trace).issubset(ids):
            raise RuntimeError("Pivot provenance outside A support")
        pivots[lead]=(row,trace)
    start=time.monotonic()
    provenance,steps=reduce_field(initial,pivots,progress=True)
    reduction_s=time.monotonic()-start
    print("VP05_A_TARGET_ZERO_REMAINDER "+json.dumps(
        {"steps":steps,"original_support":len(provenance),
         "reduction_s":reduction_s,"proof":False}),flush=True)
    if not provenance or not set(provenance).issubset(ids):
        raise AssertionError("Invalid A target provenance")
    # Separate algebraic implementation: literal exported source replay with
    # SymPy cancel, not the field arithmetic used for target elimination.
    start=time.monotonic()
    if not exact.replay(provenance,rows,z,d,initial):
        raise AssertionError("Independent original IBP replay mismatch")
    replay_s=time.monotonic()-start
    for path,digest in protected.items():
        if batch.sha(path)!=digest:
            raise RuntimeError("Protected input changed during proof")
    report={"status":"VP05_A_EXACT_TARGET_PROOF_CANDIDATE",
        "target":"A","checkpoint_sha256":PIN,"source_sha256":batch.SOURCE_SHA,
        "certificate_sha256":batch.CERT_SHA,"source_rows":339,
        "target_definitions":[list(v) for v in exact.TARGETS],
        "candidate_formulas":list(exact.FORMULAS),
        "target_terms":[[list(k),str(v)] for k,v in sorted(initial.items())],
        "source_multipliers":[[k,str(v)] for k,v in sorted(provenance.items())],
        "steps":steps,"remainder_terms":0,"original_support":len(provenance),
        "original_ibp_replay_verified":True,"exact_target_A_proven":True,
        "formal_promotion_completed":False,"whole_family_63_closure_proven":False,
        "reduction_s":reduction_s,"independent_replay_s":replay_s,
        "checkpoint_modified":False,"kira_executed":False}
    raw=(json.dumps(report,indent=2,ensure_ascii=True)+"\n").encode()
    with OUTPUT.open("xb") as fh:
        fh.write(raw)
        fh.flush()
        os.fsync(fh.fileno())
    print("VP05_A_TARGET_EXACT_PROOF "+json.dumps(
        {"status":report["status"],"steps":steps,"original_support":len(provenance),
         "remainder_terms":0,"original_ibp_replay_verified":True,
         "reduction_s":reduction_s,"independent_replay_s":replay_s,
         "output":str(OUTPUT),"proof_sha256":hashlib.sha256(raw).hexdigest(),
         "formal_promotion_completed":False}),flush=True)

if __name__=="__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    run()
