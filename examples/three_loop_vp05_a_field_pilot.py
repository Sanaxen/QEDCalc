"""Bounded isolated VP05 A field continuation from immutable 296-row state."""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path
from examples import three_loop_vp05_sector202_a_exact_batch as batch
from examples import three_loop_vp05_exact_real_first_pivot_probe as pin

def run(rows, timeout):
    batch.preflight()
    original,_=batch.project("a339a")
    scratch,logs=batch.project("fieldpilot")
    if batch.sha(original)!=pin.EXPECTED_A_CHECKPOINT_SHA256:
        raise RuntimeError("Immutable A seed changed")
    if scratch.is_symlink() or logs.is_symlink():
        raise RuntimeError("Linked pilot output refused")
    if not scratch.exists():
        with scratch.open("xb") as stream:
            stream.write(original.read_bytes())
        if batch.sha(scratch)!=pin.EXPECTED_A_CHECKPOINT_SHA256:
            raise RuntimeError("Pilot copy hash mismatch")
    before=batch.checkpoint_state(scratch)
    if before["processed"]<296:
        raise RuntimeError("Pilot position precedes pinned seed")
    if before["processed"]==339:
        return {"status":"PILOT_SOURCE_ROWS_COMPLETE_NOT_TARGET_PROOF","checkpoint":before}
    logs.mkdir(exist_ok=True)
    index=1
    while (logs/f"from_{before['processed']}_attempt_{index}.log").exists():
        index+=1
    logfile=logs/f"from_{before['processed']}_attempt_{index}.log"
    cmd=batch.command(scratch,resume=True,rows=rows)+["--experimental-field"]
    with logfile.open("x",encoding="utf-8") as stream:
        try:
            code=subprocess.run(cmd,cwd=batch.ROOT,stdout=stream,
                                stderr=subprocess.STDOUT,timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            code=None
    after=batch.checkpoint_state(scratch)
    if not before["processed"]<=after["processed"]<=min(339,before["processed"]+rows):
        raise RuntimeError("Unexpected pilot checkpoint progress")
    if after["processed"]==before["processed"] and after["checkpoint_sha256"]!=before["checkpoint_sha256"]:
        raise RuntimeError("Pilot checkpoint changed without progress")
    if batch.sha(original)!=pin.EXPECTED_A_CHECKPOINT_SHA256:
        raise RuntimeError("Immutable A seed changed during pilot")
    batch.preflight()
    return {"status":"PILOT_SOURCE_PROGRESS_NOT_TARGET_PROOF",
            "before":before,"after":after,"exit_code":code,"timed_out":code is None,
            "log":str(logfile),"original_checkpoint_unchanged":True,
            "target_A_proven":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--rows",type=int,default=10)
    ap.add_argument("--timeout-seconds",type=int,default=43200)
    args=ap.parse_args()
    if not 1<=args.rows<=43 or not 1<=args.timeout_seconds<=43200:
        ap.error("rows 1..43; timeout 1..43200")
    print("VP05_A_FIELD_PILOT "+json.dumps(run(args.rows,args.timeout_seconds)),flush=True)

if __name__=="__main__":
    main()
