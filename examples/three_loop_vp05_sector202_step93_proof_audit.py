"""Independent exact audit of VP05 sector202 Target A proof JSON.

Read-only: checks proof/state/source hashes, reconstructs the exact A target
from QEDCalc's encoded Kira IDs, and replays all original IBP rows.
Does not mutate the protected 389-pivot checkpoint or saved target state.
"""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
import sympy as sp

from examples.three_loop_sector203_weight_audit import ROOT, load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P, TARGETS
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_target_exact_checkpoint import decoded, trace_decoded
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, FORMULAS, replay, target_row, sha,
)

STATE = BASE / "vp05_sector202_A_exact_target_state.json"
PROOF = BASE / "vp05_sector202_A_exact_target_state_proof.json"
EXPECTED_STEP93_SHA = "c685cd2627ad4d6f9bea6c7afc0b5e0f6611184b2382b303616283068a54c13c"


def audit(state_path=STATE, proof_path=PROOF, checkpoint=CHECKPOINT, source_path=SOURCE,
          certificate=CERT):
    if sha(state_path) != EXPECTED_STEP93_SHA:
        raise RuntimeError("Step93 saved state hash mismatch")
    state=json.loads(state_path.read_text(encoding="utf-8-sig"))
    proof=json.loads(proof_path.read_text(encoding="utf-8-sig"))
    cfg=state["config"]
    if (state.get("steps")!=93 or state.get("remaining")!=[]
        or len(state.get("pivot_path",[]))!=93
        or state.get("exact_target_proven") is not False
        or cfg.get("target")!="A"
        or cfg.get("source_checkpoint_sha256")!=sha(checkpoint)
        or cfg.get("source_sha256")!=sha(source_path)
        or cfg.get("certificate_sha256")!=sha(certificate)):
        raise RuntimeError("Saved exact zero-remainder checkpoint mismatch")
    if (proof.get("status")!="EXACT_SINGLE_TARGET_PROVEN"
        or proof.get("target")!="A" or proof.get("steps")!=93
        or proof.get("original_source_replay_verified") is not True
        or proof.get("source_checkpoint_sha256")!=sha(checkpoint)
        or proof.get("source_sha256")!=sha(source_path)
        or proof.get("certificate_sha256")!=sha(certificate)
        or proof.get("source_multipliers")!=state["source"]):
        raise RuntimeError("Exact proof header, source trace, or input hashes mismatch")
    z,d=sp.symbols("z d")
    provenance=trace_decoded(proof["source_multipliers"],z,d)
    with gzip.open(source_path,"rt",encoding="utf-8") as stream:
        src=json.load(stream)
    if src.get("status")!="ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED" or len(src.get("rows",[]))!=2241:
        raise RuntimeError("Unexpected source rows format")
    rows={r["global_zero_based"]:r for r in src["rows"]}
    if len(rows)!=2241 or not all(rid in rows for rid in provenance):
        raise RuntimeError("Invalid proof provenance IDs")
    codec_module=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
    bits,order=codec_module.from_kiradb(str(P/"results/kira.db"))
    if order!=5:
        raise RuntimeError("Unexpected Kira order")
    codec=codec_module.WeightCodec(np=12,bits=bits,iord=order,topsectors=[203])
    keys=[(codec.encode(v),139) for v in TARGETS]
    if any(tuple(codec.decode(k[0]))!=v for k,v in zip(keys,TARGETS)):
        raise RuntimeError("Kira target encoding mismatch")
    initial=target_row("A",keys,[expr(raw,z,d) for raw in FORMULAS])
    saved_target=decoded(proof["target_terms"],z,d)
    if set(initial)!=set(saved_target) or any(
        sp.cancel(initial[k]-saved_target[k])!=0 for k in initial):
        raise RuntimeError("Proof target does not match formula-defined A target")
    if not replay(provenance,rows,z,d,initial):
        raise AssertionError("Independent original IBP exact replay FAILED")
    return {"status":"TARGET_A_INDEPENDENT_EXACT_PROOF_AUDIT_PASS",
            "target":"A","steps":93,"remainder_terms":0,
            "original_source_support":len(provenance),
            "state_sha256":sha(state_path),"proof_sha256":sha(proof_path),
            "original_ibp_exact_replay":True,
            "protected_source_checkpoint_modified":False}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--state",type=Path,default=STATE)
    ap.add_argument("--proof",type=Path,default=PROOF)
    args=ap.parse_args()
    result=audit(args.state,args.proof)
    print("VP05_SECTOR202_TARGET_A_PROOF_AUDIT "+json.dumps(result),flush=True)


if __name__=="__main__":
    main()
