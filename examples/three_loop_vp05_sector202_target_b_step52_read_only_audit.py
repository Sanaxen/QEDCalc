"""Read-only independent verification of formally promoted B Step52.

Does not import or invoke promotion() and does not mutate any file.
Checks the user-observed promoted hash and the original backup byte hashes.
"""
from __future__ import annotations
import json
from examples.three_loop_vp05_sector202_target_b_start import (
    B_STATE, A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step51_formal_promotion import (
    BACKUP as STEP50_BACKUP, B_STEP50_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step52_formal_promotion import (
    BACKUP as STEP51_BACKUP, B_STEP51_SHA,
    CHECKPOINT, SOURCE, CERT, SOURCE_CHECKPOINT_SHA, ORIGINAL_SOURCE_SHA,
    CERTIFICATE_SHA,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import sha

PROMOTED_STEP52_SHA="731147f8d8113e12684afbc21d9756991d0378361326d391693d2c671a0565f2"

def inspect():
    expected=[(B_STATE,PROMOTED_STEP52_SHA),(STEP50_BACKUP,B_STEP50_SHA),
              (STEP51_BACKUP,B_STEP51_SHA),
              (A_STATE,A_STATE_SHA),(A_PROOF,A_PROOF_SHA),
              (CHECKPOINT,SOURCE_CHECKPOINT_SHA),
              (SOURCE,ORIGINAL_SOURCE_SHA),(CERT,CERTIFICATE_SHA)]
    for path,digest in expected:
        if sha(path)!=digest:
            raise RuntimeError("Mismatch/missing protected file: "+str(path))
    state=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    cfg=state["config"]
    rem=state["remaining"]; src=state["source"]
    lengths=[len(v) for _,v in rem+src]
    lead=list(min(tuple(k) for k,v in rem))
    if (state.get("steps")!=52 or state.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or state.get("exact_target_proven") is not False
        or cfg.get("target")!="B"
        or len(state.get("pivot_path",[]))!=52
        or len(rem)!=103 or len(src)!=187
        or max(lengths,default=0)!=7447
        or state.get("metrics",{}).get("lead")!=lead
        or state.get("metrics",{}).get("max_expression_chars")!=7447
        or cfg.get("max_expression_chars")!=7500
        or cfg.get("max_columns")!=256 or cfg.get("max_support")!=400
        or cfg.get("source_checkpoint_sha256")!=SOURCE_CHECKPOINT_SHA
        or cfg.get("source_sha256")!=ORIGINAL_SOURCE_SHA
        or cfg.get("certificate_sha256")!=CERTIFICATE_SHA):
        raise RuntimeError("Promoted formal B Step52 checkpoint structure invalid")
    return {
        "status":"B_STEP52_FORMAL_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF",
        "steps":52,"remainder_terms":103,"original_support":187,
        "max_expression_chars":7447,"next_lead":lead,
        "state_sha256":sha(B_STATE),
        "step50_backup_sha256":sha(STEP50_BACKUP),
        "step51_backup_sha256":sha(STEP51_BACKUP),
        "a_protected_unchanged":True,"exact_target_proven":False
    }

if __name__=="__main__":
    print("VP05_B_STEP52_READ_ONLY_AUDIT "+json.dumps(inspect()),flush=True)
