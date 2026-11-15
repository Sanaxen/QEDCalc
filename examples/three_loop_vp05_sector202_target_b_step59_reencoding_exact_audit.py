"""Independent read-only exact comparison: reserialized B Step59 vs audited Step59.

Run after Step60 cap-stop changed three residual coefficient spellings.
No writes, no modification to the formally saved state or protected artifacts.
A successful modular check alone is NOT accepted as an exact proof.
"""
from __future__ import annotations
import json
import subprocess
import sys
import argparse
from pathlib import Path

from examples.three_loop_vp05_sector202_target_b_start import (
    B_STATE, A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step59_formal_promotion import (
    REPORT, STEP50_BACKUP, B_STEP50_SHA, STEP51_BACKUP, B_STEP51_SHA,
    STEP52_BACKUP, B_STEP52_SHA, BACKUP as STEP58_BACKUP, B_STEP58_SHA,
    CHECKPOINT, SOURCE, CERT,
    SOURCE_CHECKPOINT_SHA, ORIGINAL_SOURCE_SHA, CERTIFICATE_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step59_read_only_audit import PROMOTED_STEP59_SHA
from examples.three_loop_vp05_sector202_target_exact_reduction import sha

CURRENT_CAP_STOP_SHA = "a5a341737487cc4a1f2e20323b1adc927ead02e043af44db4442857a7cfdc38a"


def load_context():
    protected = [
        (A_STATE,A_STATE_SHA), (A_PROOF,A_PROOF_SHA),
        (STEP50_BACKUP,B_STEP50_SHA), (STEP51_BACKUP,B_STEP51_SHA),
        (STEP52_BACKUP,B_STEP52_SHA), (STEP58_BACKUP,B_STEP58_SHA),
        (CHECKPOINT,SOURCE_CHECKPOINT_SHA), (SOURCE,ORIGINAL_SOURCE_SHA),
        (CERT,CERTIFICATE_SHA),
    ]
    if sha(B_STATE) != CURRENT_CAP_STOP_SHA:
        raise RuntimeError("Current Step59 cap-stop state hash differs; refuse verification")
    for path, known in protected:
        if sha(path) != known:
            raise RuntimeError("Protected artifact mismatch: " + str(path))
    state = json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    audited = json.loads(REPORT.read_text(encoding="utf-8-sig"))
    backup = json.loads(STEP58_BACKUP.read_text(encoding="utf-8-sig"))
    original_lead = min(tuple(k) for k,v in backup["remaining"])
    if (audited.get("state_step58_sha256") != B_STEP58_SHA
        or audited.get("candidate_step") != 59
        or audited.get("original_ibp_exact_replay_verified") is not True
        or state.get("steps") != 59
        or state.get("status") != "EXACT_TARGET_CAP_REACHED_NOT_PROOF"
        or state.get("exact_target_proven") is not False
        or state.get("pivot_path") != backup["pivot_path"] + [list(original_lead)]
        or state.get("config") != backup["config"]
        or len(state.get("remaining",[])) != 86
        or len(state.get("source",[])) != 163):
        raise RuntimeError("Current checkpoint or audited predecessor metadata mismatch")
    rem = {tuple(k):v for k,v in state["remaining"]}
    audited_rem = {tuple(k):v for k,v in audited["remaining"]}
    src = {int(k):v for k,v in state["source"]}
    audited_src = {int(k):v for k,v in audited["source"]}
    if (len(rem)!=86 or len(audited_rem)!=86 or set(rem)!=set(audited_rem)
        or len(src)!=163 or len(audited_src)!=163 or src != audited_src):
        raise RuntimeError("Original IBP support or residual keys do not match audited Step59")
    changed=[(k, audited_rem[k], rem[k]) for k in sorted(rem)
             if audited_rem[k]!=rem[k]]
    if len(changed)!=3:
        raise RuntimeError("Expected exactly 3 changed residual coefficient strings")
    return changed, protected


def exact_check(before, after):
    import sympy as sp
    from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
    z,d=sp.symbols("z d")
    return sp.cancel(expr(before,z,d)-expr(after,z,d)) == 0


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worker",type=int,default=-1,help=argparse.SUPPRESS)
    ap.add_argument("--timeout-seconds",type=int,default=1800)
    args=ap.parse_args()
    changed, protected = load_context()
    if args.worker >= 0:
        if args.worker >= len(changed):
            raise ValueError("Invalid worker index")
        key,before,after=changed[args.worker]
        good=exact_check(before,after)
        if not good:
            raise AssertionError("Changed coefficient is not symbolically identical: "+str(key))
        print("VP05_B_STEP59_REENCODING_EXACT "+json.dumps({
            "status":"EXACT_COEFFICIENT_EQUIVALENCE_PASS",
            "index":args.worker,"key":list(key),
            "before_chars":len(before),"after_chars":len(after)
        }),flush=True)
        return
    if not 30 <= args.timeout_seconds <= 3600:
        ap.error("timeout-seconds must be 30..3600")
    for index,(key,before,after) in enumerate(changed):
        command=[sys.executable,"-m",
                 "examples.three_loop_vp05_sector202_target_b_step59_reencoding_exact_audit",
                 "--worker",str(index)]
        run=subprocess.run(command,text=True,capture_output=True,
                           timeout=args.timeout_seconds,check=False)
        if run.returncode != 0:
            raise RuntimeError("Exact equivalence failed at "+str(key)+": "+run.stderr[-1800:])
        result=json.loads(run.stdout.split("VP05_B_STEP59_REENCODING_EXACT ",1)[1])
        if result.get("status")!="EXACT_COEFFICIENT_EQUIVALENCE_PASS":
            raise RuntimeError("Worker did not pass exact symbolic check")
        print("VP05_B_STEP59_REENCODING_EXACT "+json.dumps(result),flush=True)
    if sha(B_STATE)!=CURRENT_CAP_STOP_SHA or any(sha(p)!=h for p,h in protected):
        raise RuntimeError("Checkpoint/protected input changed during exact verification")
    print("VP05_B_STEP59_REENCODING_EXACT "+json.dumps({
        "status":"B_STEP59_REENCODING_ALL_3_EXACT_EQUIVALENCE_PASS_NOT_TARGET_PROOF",
        "current_state_sha256":CURRENT_CAP_STOP_SHA,
        "audited_formal_step59_sha256":PROMOTED_STEP59_SHA,
        "changed_residual_strings_verified":len(changed),
        "residual_keys":86,"original_ibp_support":163,
        "target_b_proven":False,"formal_state_modified":False,
    }),flush=True)


if __name__=="__main__":
    main()
