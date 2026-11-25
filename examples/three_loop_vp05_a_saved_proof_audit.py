"""Read-only audit of serialized VP05 A exact proof, pinned to Windows result."""
import gzip
import json
import time
import sympy as sp
from examples import three_loop_vp05_a_fieldpilot_target_proof as proof
from examples import three_loop_vp05_sector202_target_exact_reduction as exact
from examples import three_loop_vp05_sector202_a_exact_batch as batch

PROOF_SHA = "9393696362fb2e22c011e734fe92393d845ac0055d2f6a9a1114c8e21b308858"

def audit():
    batch.preflight()
    pins = {proof.OUTPUT:PROOF_SHA, proof.CHECKPOINT:proof.PIN,
            exact.SOURCE:batch.SOURCE_SHA, exact.CERT:batch.CERT_SHA}
    for path, digest in pins.items():
        if batch.sha(path)!=digest:
            raise RuntimeError("Pinned input mismatch: "+str(path))
    report=json.loads(proof.OUTPUT.read_text(encoding="utf-8"))
    expected={"status":"VP05_A_EXACT_TARGET_PROOF_CANDIDATE","target":"A",
        "checkpoint_sha256":proof.PIN,"source_sha256":batch.SOURCE_SHA,
        "certificate_sha256":batch.CERT_SHA,"source_rows":339,
        "steps":70,"remainder_terms":0,"original_support":339,
        "original_ibp_replay_verified":True,"exact_target_A_proven":True,
        "formal_promotion_completed":False,"whole_family_63_closure_proven":False}
    if any(report.get(k)!=v for k,v in expected.items()):
        raise RuntimeError("Unexpected proof metadata")
    cert=json.loads(exact.CERT.read_text(encoding="utf-8-sig"))
    ids=set(cert["target_results"][0]["support_original_ids"])
    z,d=sp.symbols("z d")
    mod=exact.load_codec((exact.ROOT/"output/tools/pyred_weight.py").resolve())
    bits,ordering=mod.from_kiradb(str(exact.P/"results/kira.db"))
    if ordering!=5:
        raise RuntimeError("Unexpected codec ordering")
    codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    keys=[(codec.encode(v),139) for v in exact.TARGETS]
    if any(tuple(codec.decode(k[0]))!=v for k,v in zip(keys,exact.TARGETS)):
        raise RuntimeError("Codec roundtrip mismatch")
    initial=exact.target_row("A",keys,[exact.expr(v,z,d) for v in exact.FORMULAS])
    if report["target_definitions"]!=[list(v) for v in exact.TARGETS] or report["candidate_formulas"]!=list(exact.FORMULAS):
        raise RuntimeError("Target definitions mismatch")
    terms=report["target_terms"]
    actual={tuple(k):exact.expr(v,z,d) for k,v in terms}
    if len(actual)!=len(terms) or set(actual)!=set(initial) or any(sp.cancel(actual[k]-initial[k])!=0 for k in initial):
        raise RuntimeError("Serialized target mismatch")
    multipliers=report["source_multipliers"]
    provenance={int(k):exact.expr(v,z,d) for k,v in multipliers}
    if len(multipliers)!=339 or len(provenance)!=339 or set(provenance)!=ids or any(sp.cancel(v)==0 for v in provenance.values()):
        raise RuntimeError("Serialized multiplier support mismatch")
    with gzip.open(exact.SOURCE,"rt",encoding="utf-8") as fh:
        source=json.load(fh)
    rows={r["global_zero_based"]:r for r in source["rows"]}
    start=time.monotonic()
    if not exact.replay(provenance,rows,z,d,initial):
        raise AssertionError("Serialized proof original IBP replay mismatch")
    for path,digest in pins.items():
        if batch.sha(path)!=digest:
            raise RuntimeError("Input changed during audit")
    return {"status":"VP05_A_SAVED_PROOF_READ_ONLY_AUDIT_PASS",
        "proof_sha256":PROOF_SHA,"checkpoint_sha256":proof.PIN,
        "original_support":339,"original_ibp_replay_verified":True,
        "replay_s":time.monotonic()-start,"formal_promotion_completed":False,
        "whole_family_63_closure_proven":False,"files_modified":False}

if __name__=="__main__":
    print("VP05_A_SAVED_PROOF_AUDIT "+json.dumps(audit()),flush=True)
