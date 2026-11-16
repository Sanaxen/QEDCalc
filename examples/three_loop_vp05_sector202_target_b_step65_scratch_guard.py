"""Read-only structural audit of Step65 zero-step scratch cap stop.

The scratch engine may reserialize exact coefficients without eliminating a
pivot. This audit deliberately does NOT certify exact symbolic equivalence
of differing strings. Step65 coefficient workers instead read the immutable,
already independently audited *formal Step64* state as their only input.
"""
from __future__ import annotations
import json
from examples.three_loop_vp05_sector202_target_b_scratch_from64 import (
    SCRATCH, B_STATE, validate, validate_scratch,
)
from examples.three_loop_vp05_sector202_target_b_step64_read_only_audit import SAVED_STEP64_SHA
from examples.three_loop_vp05_sector202_target_exact_reduction import sha

SCRATCH_SHA="e7ef7c12cb68cb8492723a864ba80febda9a8a5415581ec4bd1cd2ad15989fcc"


def verify_scratch():
    formal=validate()
    if sha(B_STATE)!=SAVED_STEP64_SHA or sha(SCRATCH)!=SCRATCH_SHA:
        raise RuntimeError("Formal Step64 or preserved scratch hash changed")
    scratch=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    validate_scratch(formal,scratch)
    if (scratch.get("steps")!=64 or scratch.get("status")!="EXACT_TARGET_CAP_REACHED_NOT_PROOF"
        or scratch.get("exact_target_proven") is not False
        or scratch.get("original_source_replay_proven") is not False
        or len(scratch.get("remaining",[]))!=86
        or len(scratch.get("source",[]))!=172
        or scratch.get("metrics",{}).get("lead")!=[166596413882371,139]
        or scratch.get("metrics",{}).get("max_expression_chars")!=7310
        or max((len(v) for _,v in scratch["remaining"]+scratch["source"]),default=0)!=7310):
        raise RuntimeError("Scratch cap-stop metadata differs from logged zero-step result")
    f_rem={tuple(k):v for k,v in formal["remaining"]}
    s_rem={tuple(k):v for k,v in scratch["remaining"]}
    f_src={int(k):v for k,v in formal["source"]}
    s_src={int(k):v for k,v in scratch["source"]}
    if len(f_rem)!=86 or len(s_rem)!=86 or set(f_rem)!=set(s_rem) or (
        len(f_src)!=172 or len(s_src)!=172 or set(f_src)!=set(s_src)):
        raise RuntimeError("Zero-step scratch changed residual or source keys")
    return {
        "status":"B_STEP65_SCRATCH_STRUCTURAL_AUDIT_PASS_REENCODING_NOT_EXACT_PROOF",
        "formal_step64_sha256":SAVED_STEP64_SHA,
        "scratch_sha256":SCRATCH_SHA,
        "steps_saved_after_cap_stop":0,
        "residual_reencoded_string_count":sum(f_rem[k]!=s_rem[k] for k in f_rem),
        "source_reencoded_string_count":sum(f_src[k]!=s_src[k] for k in f_src),
        "scratch_symbolic_equivalence_verified":False,
        "step65_candidate_uses_immutable_formal_state":True,
        "formal_state_unchanged":True,
        "target_b_proven":False,
    }


if __name__=="__main__":
    print("VP05_B_STEP65_SCRATCH_AUDIT "+json.dumps(verify_scratch()),flush=True)
