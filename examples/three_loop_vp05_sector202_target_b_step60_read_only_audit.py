"""Read-only independent verification of promoted VP05 sector202 Target B Step60.

No mutation, no promotion invocation, and no Target B proof claim.
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
)
from examples.three_loop_vp05_sector202_target_b_step53_formal_promotion import (
    BACKUP as STEP52_BACKUP, B_STEP52_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step59_formal_promotion import (
    BACKUP as STEP58_BACKUP, B_STEP58_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step60_formal_promotion import (
    BACKUP as STEP59_BACKUP, B_STEP59_SHA,
    CHECKPOINT, SOURCE, CERT, SOURCE_CHECKPOINT_SHA, ORIGINAL_SOURCE_SHA,
    CERTIFICATE_SHA,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import sha

PROMOTED_STEP60_SHA = "4eebc9694e460654e1224fa72e6d6385ae1689dedf3004bbf5934be27f3075c8"


def inspect():
    expected = [
        (B_STATE, PROMOTED_STEP60_SHA),
        (STEP50_BACKUP, B_STEP50_SHA),
        (STEP51_BACKUP, B_STEP51_SHA),
        (STEP52_BACKUP, B_STEP52_SHA),
        (STEP58_BACKUP, B_STEP58_SHA),
        (STEP59_BACKUP, B_STEP59_SHA),
        (A_STATE, A_STATE_SHA), (A_PROOF, A_PROOF_SHA),
        (CHECKPOINT, SOURCE_CHECKPOINT_SHA),
        (SOURCE, ORIGINAL_SOURCE_SHA), (CERT, CERTIFICATE_SHA),
    ]
    if len({path.resolve() for path, _ in expected}) != len(expected):
        raise RuntimeError("Protected paths overlap")
    for path, digest in expected:
        if sha(path) != digest:
            raise RuntimeError("Missing or mismatched protected file: " + str(path))
    state = json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    cfg = state.get("config", {})
    rem = state.get("remaining", [])
    src = state.get("source", [])
    if not rem:
        raise RuntimeError("Unexpected zero residual; separate proof needed")
    lead = list(min(tuple(k) for k, _ in rem))
    lengths = [len(v) for _, v in rem + src]
    metrics = state.get("metrics", {})
    pivot_path = state.get("pivot_path", [])
    if (
        state.get("steps") != 60
        or state.get("status") != "EXACT_TARGET_PREFIX_NOT_PROOF"
        or state.get("exact_target_proven") is not False
        or state.get("original_source_replay_proven") is not False
        or cfg.get("target") != "B"
        or len(pivot_path) != 60
        or len({tuple(k) for k in pivot_path}) != 60
        or len(rem) != 85 or len(src) != 164
        or len({tuple(k) for k, _ in rem}) != 85
        or len({int(k) for k, _ in src}) != 164
        or any(not isinstance(v, str) or v == "0" or len(v) > 7500
               for _, v in rem + src)
        or max(lengths, default=0) != 7356
        or metrics.get("lead") != lead
        or metrics.get("remainder_terms") != 85
        or metrics.get("original_support") != 164
        or metrics.get("max_expression_chars") != 7356
        or cfg.get("max_expression_chars") != 7500
        or cfg.get("max_columns") != 256
        or cfg.get("max_support") != 400
        or cfg.get("source_checkpoint_sha256") != SOURCE_CHECKPOINT_SHA
        or cfg.get("source_sha256") != ORIGINAL_SOURCE_SHA
        or cfg.get("certificate_sha256") != CERTIFICATE_SHA
    ):
        raise RuntimeError("Promoted formal B Step60 state invalid")
    for path, digest in expected:
        if sha(path) != digest:
            raise RuntimeError("Protected input modified during read-only audit: " + str(path))
    return {
        "status": "B_STEP60_FORMAL_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF",
        "steps": 60, "remainder_terms": 85, "original_support": 164,
        "max_expression_chars": 7356, "next_lead": lead,
        "state_sha256": sha(B_STATE),
        "step50_backup_sha256": sha(STEP50_BACKUP),
        "step51_backup_sha256": sha(STEP51_BACKUP),
        "step52_backup_sha256": sha(STEP52_BACKUP),
        "step58_backup_sha256": sha(STEP58_BACKUP),
        "step59_backup_sha256": sha(STEP59_BACKUP),
        "a_protected_unchanged": True, "exact_target_proven": False,
    }


if __name__ == "__main__":
    print("VP05_B_STEP60_READ_ONLY_AUDIT " + json.dumps(inspect()), flush=True)
