"""Read-only forensic inspection after the B Step59 -> Step60 wrapper exception.

The exact checkpoint engine can rewrite strings/metrics even with zero completed
steps. This script never retries, rewrites, promotes or alters any file.
"""
from __future__ import annotations
import json
from examples.three_loop_vp05_sector202_target_b_start import (
    B_STATE, A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step59_formal_promotion import (
    BACKUP as STEP58_BACKUP, B_STEP58_SHA, REPORT,
    STEP50_BACKUP, B_STEP50_SHA, STEP51_BACKUP, B_STEP51_SHA,
    STEP52_BACKUP, B_STEP52_SHA,
    CHECKPOINT, SOURCE, CERT,
    SOURCE_CHECKPOINT_SHA, ORIGINAL_SOURCE_SHA, CERTIFICATE_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step59_read_only_audit import PROMOTED_STEP59_SHA
from examples.three_loop_vp05_sector202_target_exact_reduction import sha


def compare_state(state, audit):
    rem = state.get("remaining", [])
    src = state.get("source", [])
    expected_rem = audit.get("remaining", [])
    expected_src = audit.get("source", [])
    current_r = {tuple(k): v for k, v in rem}
    expected_r = {tuple(k): v for k, v in expected_rem}
    current_s = {int(k): v for k, v in src}
    expected_s = {int(k): v for k, v in expected_src}
    if (len(current_r) != len(rem) or len(expected_r) != len(expected_rem)
            or len(current_s) != len(src) or len(expected_s) != len(expected_src)):
        raise RuntimeError("Duplicate key in current or audited checkpoint")
    return {
        "steps": state.get("steps"),
        "status": state.get("status"),
        "pivot_path_equal_to_audited_step59": state.get("pivot_path") == audit.get("pivot_path"),
        "remaining_keys_equal": set(current_r) == set(expected_r),
        "source_ids_equal": set(current_s) == set(expected_s),
        "remaining_string_changes": sum(current_r.get(k) != expected_r.get(k) for k in set(current_r)|set(expected_r)),
        "source_string_changes": sum(current_s.get(k) != expected_s.get(k) for k in set(current_s)|set(expected_s)),
        "config_equal": state.get("config") == audit.get("config"),
        "metrics": state.get("metrics"),
        "max_saved_chars": max((len(v) for v in list(current_r.values())+list(current_s.values())), default=0),
        "proof_flag": state.get("exact_target_proven"),
    }


def diagnose():
    expected = [(STEP58_BACKUP, B_STEP58_SHA),
                (STEP50_BACKUP, B_STEP50_SHA), (STEP51_BACKUP, B_STEP51_SHA),
                (STEP52_BACKUP, B_STEP52_SHA),
                (A_STATE, A_STATE_SHA), (A_PROOF, A_PROOF_SHA),
                (CHECKPOINT, SOURCE_CHECKPOINT_SHA), (SOURCE, ORIGINAL_SOURCE_SHA),
                (CERT, CERTIFICATE_SHA)]
    if any(sha(path) != digest for path, digest in expected):
        raise RuntimeError("Protected file hash mismatch; abort forensic inspection")
    current = json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    audited = json.loads(REPORT.read_text(encoding="utf-8-sig"))
    # Report has the exact Step59 coefficient payload, but not the full formal
    # state. The other metadata can be reconstructed without touching disk.
    base = json.loads(STEP58_BACKUP.read_text(encoding="utf-8-sig"))
    original_lead = min(tuple(k) for k, _ in base["remaining"])
    reconstructed = dict(base)
    reconstructed.update(
        steps=59,
        status="EXACT_TARGET_PREFIX_NOT_PROOF",
        remaining=audited["remaining"],
        source=audited["source"],
        pivot_path=base["pivot_path"]+[list(original_lead)],
        exact_target_proven=False,
    )
    result = compare_state(current, reconstructed)
    result.update({
        "status_label": "B_STEP60_READ_ONLY_FORENSICS_NOT_PROOF",
        "formal_step59_original_sha256": PROMOTED_STEP59_SHA,
        "current_state_sha256": sha(B_STATE),
        "original_sha_matches": sha(B_STATE) == PROMOTED_STEP59_SHA,
        "step58_backup_verified": True,
        "target_a_protected_verified": True,
        "audit_report_source_verified": audited.get("original_ibp_exact_replay_verified") is True,
    })
    for path, digest in expected:
        if sha(path) != digest:
            raise RuntimeError("Protected file changed during inspection: " + str(path))
    return result


if __name__ == "__main__":
    print("VP05_B_STEP60_FORENSICS " + json.dumps(diagnose()), flush=True)
