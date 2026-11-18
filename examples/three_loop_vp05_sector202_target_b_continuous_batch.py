"""Resumable bounded multi-step VP05 sector202 Target B exact-audited batch.

Independent work copy; formal Step77 and every previous audit stay untouched.
Each completed pivot is verified in exact QQ(z,d) twice (coefficient update
and original unscaled IBP replay) and checkpointed before advancing.
No claim of whole Target B proof or formal promotion is made.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import contextlib
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from examples.three_loop_vp05_sector202_target_b_step77_read_only_audit import inspect as inspect77
from examples.three_loop_vp05_sector202_target_b_step77_formal_promotion import (
    B_STATE, EXPECTED_STEP77_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step78_exact_audit import (
    SCRATCH as STEP78_SCRATCH, EXPECTED_STEP78_SHA, context as context78,
    validate_progress as validate_progress78, COEFF as STEP78_COEFF,
    IBP as STEP78_IBP, field_equal, coefficient_identity, rows_dict,
)
from examples.three_loop_vp05_sector202_target_b_step78_scratch import protected_inputs
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_target_b_multistep_from60 import classify

RUN_DIR=BASE/"vp05_sector202_B_continuous_batch_from77"
WORK=RUN_DIR/"working_state.json"
JOURNAL=RUN_DIR/"batch_journal.json"
LOCK=RUN_DIR/"batch.lock"
START=77
TAG="VP05_B_BATCH_EXACT "
END_STATUS="AUDITED_PREFIX_NOT_TARGET_PROOF"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def atomic(path,obj,exclusive=False):
    path.parent.mkdir(parents=True,exist_ok=True)
    if exclusive and path.exists():
        raise FileExistsError(str(path))
    tmp=path.with_name(path.name+"."+str(os.getpid())+".tmp")
    with tmp.open("x",encoding="utf-8") as out:
        json.dump(obj,out,ensure_ascii=True,separators=(",",":"))
        out.flush()
        os.fsync(out.fileno())
    try:
        if exclusive and path.exists(): raise FileExistsError(str(path))
        os.replace(tmp,path)
    finally:
        if tmp.exists():tmp.unlink()

def exclusive_bytes(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("xb") as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())
    if digest(raw)!=sha(path):raise RuntimeError("Snapshot hash mismatch")

@contextlib.contextmanager
def locked():
    RUN_DIR.mkdir(parents=True,exist_ok=True)
    with LOCK.open("a+b") as f:
        f.seek(0)
        if f.tell()==0:
            f.write(b"0")
            f.flush()
        f.seek(0)
        if os.name=="nt":
            import msvcrt
            msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:yield
        finally:
            f.seek(0)
            if os.name=="nt":msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(f,fcntl.LOCK_UN)

def ensure_sources(journal=None):
    if inspect77().get("status")!="B_STEP77_SAVED_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF":
        raise RuntimeError("Formal Step77 independent saved audit not PASS")
    protected=protected_inputs()
    if sha(B_STATE)!=EXPECTED_STEP77_SHA or sha(STEP78_SCRATCH)!=EXPECTED_STEP78_SHA:
        raise RuntimeError("Baseline formal77 or immutable Step78 scratch SHA mismatch")
    source_hashes={"checkpoint":sha(CHECKPOINT),"source":sha(SOURCE),"certificate":sha(CERT)}
    if journal is not None and journal["source_hashes"]!=source_hashes:
        raise RuntimeError("Original source hash changed")
    return source_hashes,protected

def initialize(steps):
    if JOURNAL.exists() or WORK.exists():
        raise FileExistsError("Existing continuous batch; use --resume")
    source_hashes,protected=ensure_sources()
    c=context78()
    state, jobs=validate_progress78("coeff",c)
    other, ibp_jobs=validate_progress78("ibp",c)
    if len(state["checked"])!=len(jobs) or len(other["checked"])!=len(ibp_jobs):
        raise RuntimeError("Step78 source exact certificates incomplete")
    if other["config"].get("coefficient_checkpoint_sha256")!=sha(STEP78_COEFF):
        raise RuntimeError("Step78 coefficient-to-IBP certificate bridge broken")
    if len(ibp_jobs)!=232 or sha(STEP78_SCRATCH)!=EXPECTED_STEP78_SHA:
        raise RuntimeError("Step78 independent evidence mismatch")
    working=STEP78_SCRATCH.read_bytes()
    exclusive_bytes(WORK,working)
    journal={"version":1,"status":END_STATUS,"start_step":START,
        "max_step":min(START+steps,128),"audited_step":START,
        "audited_sha256":EXPECTED_STEP77_SHA,
        "source_hashes":source_hashes,"initial_scratch_sha256":EXPECTED_STEP78_SHA,
        "formal_unchanged":True,"target_b_proven":False}
    atomic(JOURNAL,journal,exclusive=True)
    print(TAG+json.dumps({"event":"INITIALIZED","audited_step":START,
        "working_step":78,"max_step":journal["max_step"]}),flush=True)
    return journal

def before_path(step):return RUN_DIR/("before_step"+str(step)+".json")
def phase_path(step,phase):return RUN_DIR/("step"+str(step)+"_"+phase+".json")
def certificate_path(step):return RUN_DIR/("step"+str(step)+"_certificate.json")

def phase_context(step,before,after):
    if before["steps"]!=step-1 or after["steps"]!=step:
        raise RuntimeError("Unmatched before/after step")
    if before["config"]!=after["config"]:
        raise RuntimeError("Step changed configuration")
    if after["pivot_path"]!=before["pivot_path"]+[before["metrics"]["lead"]]:
        raise RuntimeError("Wrong pivot path")
    if not after["remaining"] or after.get("exact_target_proven") is not False:
        raise RuntimeError("Unverified or empty Target B state")
    orem=rows_dict(before["remaining"],True)
    nrem=rows_dict(after["remaining"],True)
    osrc=rows_dict(before["source"],False)
    nsrc=rows_dict(after["source"],False)
    lead=tuple(before["metrics"]["lead"])
    if lead!=min(orem) or lead in nrem or min(nrem)<=lead:
        raise RuntimeError("Invalid eliminated pivot/ordering")
    pivots=load(CHECKPOINT)["pivots"]
    matched=[p for p in pivots if tuple(p["lead"])==lead]
    if len(matched)!=1:raise RuntimeError("Original source pivot missing/nonunique")
    prow=rows_dict(matched[0]["row"],True)
    ptrace=rows_dict(matched[0]["trace"],False)
    cjobs=[("remainder",k) for k in sorted(set(orem)|set(nrem)|set(prow))]
    cjobs += [("source",k) for k in sorted(set(osrc)|set(nsrc)|set(ptrace))]
    with gzip.open(SOURCE,"rt",encoding="utf-8") as f:
        original=json.load(f)
    originals={int(r["global_zero_based"]):r for r in original["rows"]}
    if len(originals)!=len(original["rows"]) or not set(ptrace).issubset(originals):
        raise RuntimeError("Missing source IBP row")
    keyed={}
    for rid,w in ptrace.items():
        for term in originals[rid]["terms"]:
            keyed.setdefault(tuple(term["key"]),[]).append((w,term["coefficient"]))
    ijobs=sorted(set(prow)|set(keyed))
    return (orem,nrem,osrc,nsrc,prow,ptrace,cjobs,keyed,ijobs)

def manifest(step,phase,c,before_sha,after_sha):
    jobs=c[6] if phase=="coeff" else c[8]
    serial=[[k,list(v) if k=="remainder" else v] for k,v in jobs] if phase=="coeff" else [list(v) for v in jobs]
    return {"phase":phase,"step":step,"before_sha256":before_sha,
            "after_sha256":after_sha,"source_checkpoint_sha256":sha(CHECKPOINT),
            "source_sha256":sha(SOURCE),"source_certificate_sha256":sha(CERT),
            "job_count":len(jobs),
            "job_sha256":digest(json.dumps(serial,separators=(",",":")).encode())}

def checked_phase(path,m):
    if not path.exists():
        value={"status":"EXACT_PREFIX_NOT_TARGET_PROOF","manifest":m,"verified":0}
        atomic(path,value,exclusive=True)
        return value
    value=load(path)
    if (value.get("status")!="EXACT_PREFIX_NOT_TARGET_PROOF" or
        value.get("manifest")!=m or
        type(value.get("verified")) is not int or
        not 0<=value["verified"]<=m["job_count"]):
        raise RuntimeError("Incomplete phase checkpoint incompatible: "+str(path))
    return value

def verify_worker(step,phase,index):
    j=load(JOURNAL)
    if j["audited_step"]!=step-1:
        raise RuntimeError("Worker journal step mismatch")
    bp=before_path(step)
    before,after=load(bp),load(WORK)
    if (sha(bp)!=j["audited_sha256"] or
        after["steps"]!=step or before["steps"]!=step-1 or
        j["source_hashes"]!={"checkpoint":sha(CHECKPOINT),"source":sha(SOURCE),"certificate":sha(CERT)}):
        raise RuntimeError("Worker state/source changed")
    c=phase_context(step,before,after)
    jobs=c[6] if phase=="coeff" else c[8]
    if not 0<=index<len(jobs):raise RuntimeError("Worker index invalid")
    if phase=="coeff":
        kind,key=jobs[index]
        old,new,piv=(c[0],c[1],c[4]) if kind=="remainder" else (c[2],c[3],c[5])
        ok=coefficient_identity(kind,old.get(key,"0"),new.get(key,"0"),
                                piv.get(key,"0"),c[0][tuple(before["metrics"]["lead"])])
    else:
        key=jobs[index]
        ok=field_equal(c[4].get(key,"0"),c[7].get(key,[]))
    if not ok:raise AssertionError("Exact QQ(z,d) identity failed: "+str((step,phase,index)))
    print(TAG+json.dumps({"event":"EXACT_KEY_PASS","step":step,
        "phase":phase,"index":index,"working_sha256":sha(WORK)}),flush=True)

def worker_subprocess(step,phase,index,expected_sha,worker_timeout,deadline):
    left=deadline-time.monotonic()
    if left<1:raise TimeoutError("Global batch deadline reached")
    proc=subprocess.run([sys.executable,"-m",
         "examples.three_loop_vp05_sector202_target_b_continuous_batch",
         "--worker-step",str(step),"--worker-phase",phase,
         "--worker-index",str(index)],
        capture_output=True,text=True,timeout=min(worker_timeout,max(1,left)))
    if proc.returncode:
        raise RuntimeError("Exact worker failed "+str(step)+" "+phase+" "+str(index)+": "+proc.stderr[-1600:])
    reports=[line[len(TAG):] for line in proc.stdout.splitlines() if line.startswith(TAG)]
    if len(reports)!=1:raise RuntimeError("Missing or duplicate exact worker PASS")
    result=json.loads(reports[0])
    if result!={"event":"EXACT_KEY_PASS","step":step,"phase":phase,
                "index":index,"working_sha256":expected_sha}:
        raise RuntimeError("Exact worker PASS not bound to saved candidate")
    return True

def run_phase(step,phase,before_sha,after_sha,deadline,worker_timeout,workers):
    before,after=load(before_path(step)),load(WORK)
    c=phase_context(step,before,after)
    m=manifest(step,phase,c,before_sha,after_sha)
    if phase=="ibp":
        pc=phase_path(step,"coeff")
        cc=load(pc)
        if cc["verified"]!=cc["manifest"]["job_count"] or cc["manifest"]["before_sha256"]!=before_sha or cc["manifest"]["after_sha256"]!=after_sha:
            raise RuntimeError("Coefficient phase not complete")
        m["coeff_checkpoint_sha256"]=sha(pc)
    path=phase_path(step,phase)
    state=checked_phase(path,m)
    while state["verified"]<m["job_count"]:
        if deadline-time.monotonic()<5:
            return False,m["job_count"],state["verified"],"time_limit"
        indices=list(range(state["verified"],min(m["job_count"],state["verified"]+workers)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            tasks={i:pool.submit(worker_subprocess,step,phase,i,after_sha,
                                 worker_timeout,deadline) for i in indices}
            for index in indices:
                tasks[index].result()
                if sha(WORK)!=after_sha or sha(before_path(step))!=before_sha:
                    raise RuntimeError("State modified during exact worker")
                state["verified"]+=1
                atomic(path,state)
                if state["verified"]%25==0 or state["verified"]==m["job_count"]:
                    print(TAG+json.dumps({"event":"EXACT_PROGRESS","step":step,
                        "phase":phase,"verified":state["verified"],
                        "total":m["job_count"],"workers":workers}),flush=True)
    return True,m["job_count"],state["verified"],"complete"

def audit_candidate(j,deadline,worker_timeout,workers):
    step=j["audited_step"]+1
    before_file=before_path(step)
    if not before_file.exists():
        if j["audited_step"]==START:
            exclusive_bytes(before_file,B_STATE.read_bytes())
        else:
            raise RuntimeError("Previous audited snapshot missing")
    if sha(before_file)!=j["audited_sha256"]:
        raise RuntimeError("Before snapshot does not match audited chain")
    before,after=load(before_file),load(WORK)
    if after["steps"]!=step:
        raise RuntimeError("Working state not at next candidate")
    candidate_hash=sha(WORK)
    c=phase_context(step,before,after)
    for phase in ("coeff","ibp"):
        try:
            ok,total,verified,reason=run_phase(step,phase,j["audited_sha256"],
                                              candidate_hash,deadline,worker_timeout,workers)
        except subprocess.TimeoutExpired:
            return False,"worker_timeout"
        if not ok:return False,reason
    ensure_sources(j)
    if sha(WORK)!=candidate_hash:
        raise RuntimeError("Candidate changed before certificate commit")
    certificate={"status":"EXACT_AUDITED_PREFIX_NOT_TARGET_PROOF",
        "step":step,"before_sha256":j["audited_sha256"],
        "after_sha256":candidate_hash,"coefficient_keys_verified":len(c[6]),
        "original_ibp_keys_verified":len(c[8]),
        "coefficient_checkpoint_sha256":sha(phase_path(step,"coeff")),
        "original_ibp_checkpoint_sha256":sha(phase_path(step,"ibp")),
        "metrics":after["metrics"],"target_b_proven":False}
    cp=certificate_path(step)
    if cp.exists():
        if load(cp)!=certificate:raise RuntimeError("Existing exact certificate differs")
    else:atomic(cp,certificate,exclusive=True)
    j["audited_step"]=step
    j["audited_sha256"]=candidate_hash
    atomic(JOURNAL,j)
    print(TAG+json.dumps({"event":"STEP_AUDITED","step":step,
        "remainder_terms":len(after["remaining"]),
        "original_support":len(after["source"]),
        "max_expression_chars":after["metrics"]["max_expression_chars"],
        "original_ibp_keys_verified":len(c[8]),"target_b_proven":False}),flush=True)
    return True,"complete"

def validate_journal(j):
    if (j.get("version")!=1 or j.get("start_step")!=START or
        j.get("status")!=END_STATUS or
        j.get("initial_scratch_sha256")!=EXPECTED_STEP78_SHA or
        j.get("formal_unchanged") is not True or j.get("target_b_proven") is not False or
        not START<=j.get("audited_step",-1)<=j.get("max_step",-1)<=128):
        raise RuntimeError("Unexpected batch journal")
    if j["audited_step"]==START and j["audited_sha256"]!=EXPECTED_STEP77_SHA:
        raise RuntimeError("Initial chain SHA mismatch")
    if j["audited_step"]>START:
        cp=certificate_path(j["audited_step"])
        if not cp.exists() or load(cp).get("after_sha256")!=j["audited_sha256"]:
            raise RuntimeError("Latest audited certificate missing/mismatch")
    current=load(WORK)
    if (current["steps"] not in (j["audited_step"],j["audited_step"]+1) or
        current["config"].get("target")!="B" or
        current["config"].get("max_columns")!=256 or
        current["config"].get("max_support")!=400 or
        current["config"].get("max_expression_chars")!=7500):
        raise RuntimeError("Unexpected working state step/config")
    if current["steps"]==j["audited_step"] and sha(WORK)!=j["audited_sha256"]:
        raise RuntimeError("Committed working state SHA mismatch")
    if (current["steps"]==START+1 and j["audited_step"]==START
        and sha(WORK)!=EXPECTED_STEP78_SHA):
        raise RuntimeError("Initial saved Step78 scratch copy mismatch")
    return current

def recover_interrupted_engine_tmp():
    """Quarantine stale engine staging only under the exclusive process lock.

    A killed engine can leave `working_state.json.tmp`. The authoritative
    working state is never replaced by an unaudited temporary file.
    """
    tmp=WORK.with_name(WORK.name+".tmp")
    if not tmp.exists():return
    if not WORK.exists():raise RuntimeError("Orphan engine staging without working state")
    quarantine=RUN_DIR/"quarantine"
    quarantine.mkdir(parents=True,exist_ok=True)
    key=sha(tmp)
    dest=quarantine/("interrupted_engine_"+key+".tmp")
    if dest.exists():
        raise RuntimeError("Quarantine hash collision; inspect stale engine staging")
    os.replace(tmp,dest)
    print(TAG+json.dumps({"event":"INTERRUPTED_ENGINE_STAGING_QUARANTINED",
        "sha256":key,"path":str(dest)}),flush=True)

def control(args):
    if args.check_only and not RUN_DIR.exists():
        if WORK.exists() or JOURNAL.exists():
            raise RuntimeError("Unexpected orphan batch artifacts")
        ensure_sources()
        print(TAG+json.dumps({"status":"BATCH_PREFLIGHT_PASS_NOT_TARGET_PROOF",
            "audited_step":START,"working_step":78,
            "max_step":min(START+args.steps,128),"formal_unchanged":True}),flush=True)
        return
    with locked():
        if args.check_only:
            sources,_=ensure_sources(load(JOURNAL) if JOURNAL.exists() else None)
            if JOURNAL.exists():
                j=load(JOURNAL)
                state=validate_journal(j)
                print(TAG+json.dumps({"status":"BATCH_PREFLIGHT_PASS_NOT_TARGET_PROOF",
                    "audited_step":j["audited_step"],"working_step":state["steps"],
                    "max_step":j["max_step"],"formal_unchanged":True}),flush=True)
            else:
                if WORK.exists():raise RuntimeError("Orphan working file")
                if sha(STEP78_SCRATCH)!=EXPECTED_STEP78_SHA:raise RuntimeError("Step78 scratch mismatch")
                print(TAG+json.dumps({"status":"BATCH_PREFLIGHT_PASS_NOT_TARGET_PROOF",
                    "audited_step":START,"working_step":78,
                    "max_step":min(START+args.steps,128),"formal_unchanged":True}),flush=True)
            return
        if args.resume:
            if not JOURNAL.exists():raise FileNotFoundError("Missing batch journal; run without --resume")
            j=load(JOURNAL)
            ensure_sources(j)
        else:
            j=initialize(args.steps)
        recover_interrupted_engine_tmp()
        deadline=time.monotonic()+args.hours*3600
        reason="max_steps"
        while j["audited_step"]<j["max_step"]:
            state=validate_journal(j)
            if state["steps"]==j["audited_step"]+1:
                ok,reason=audit_candidate(j,deadline,args.worker_timeout,args.workers)
                if not ok:break
                continue
            if not state.get("remaining") and (RUN_DIR/"working_state_proof.json").exists():
                reason="exact_source_replay_proof_requires_independent_review"
                break
            if deadline-time.monotonic()<30:
                reason="time_limit"
                break
            if not state.get("remaining"):
                reason="empty_remainder_requires_full_proof"
                break
            before_file=before_path(state["steps"]+1)
            if before_file.exists():
                if sha(before_file)!=sha(WORK):
                    raise RuntimeError("Prepared before snapshot differs from working state")
            else:exclusive_bytes(before_file,WORK.read_bytes())
            with (RUN_DIR/"engine.log").open("a",encoding="utf-8") as log:
                try:
                    result=subprocess.run([sys.executable,"-m",
                        "examples.three_loop_vp05_sector202_target_exact_checkpoint",
                        "--resume","--state",str(WORK),"--target","B",
                        "--new-steps","1","--max-columns","256",
                        "--max-support","400","--max-expression-chars","7500",
                        "--max-steps-total",str(state["config"]["max_steps_total"])],
                        stdout=log,stderr=subprocess.STDOUT,
                        timeout=max(1,deadline-time.monotonic()))
                    rc=result.returncode
                except subprocess.TimeoutExpired:
                    reason="engine_timeout"
                    break
            after=load(WORK)
            if not after.get("remaining") and (RUN_DIR/"working_state_proof.json").exists():
                reason="exact_source_replay_proof_requires_independent_review"
                break
            if after["steps"]==state["steps"]:
                reason="engine_no_progress_or_cap"
                break
            if rc!=0 or after["steps"]!=state["steps"]+1:
                raise RuntimeError("Engine failure or unexpected step count; inspect engine.log")
            classify(state,after,1,rc,False,(RUN_DIR/"working_state_proof.json").exists())
            print(TAG+json.dumps({"event":"STEP_SAVED_PENDING_EXACT_AUDIT",
                "step":after["steps"],"metrics":after["metrics"]}),flush=True)
        ensure_sources(j)
        validated=validate_journal(j)
        print(TAG+json.dumps({"status":"BATCH_STOPPED_RESUMABLE_NOT_TARGET_PROOF",
            "reason":reason,"audited_step":j["audited_step"],
            "working_step":validated["steps"],"max_step":j["max_step"],
            "formal_state_modified":False,"target_b_proven":False}),flush=True)

def main():
    ap=argparse.ArgumentParser()
    op=ap.add_mutually_exclusive_group()
    op.add_argument("--check-only",action="store_true")
    op.add_argument("--resume",action="store_true")
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--steps",type=int,default=51)
    ap.add_argument("--worker-timeout",type=int,default=1200)
    ap.add_argument("--workers",type=int,default=4)
    ap.add_argument("--worker-step",type=int)
    ap.add_argument("--worker-phase",choices=["coeff","ibp"])
    ap.add_argument("--worker-index",type=int)
    args=ap.parse_args()
    if args.worker_step is not None:
        if args.worker_phase is None or args.worker_index is None:ap.error("Worker args incomplete")
        verify_worker(args.worker_step,args.worker_phase,args.worker_index)
        return
    if not 0<args.hours<=12 or not 1<=args.steps<=51 or not 30<=args.worker_timeout<=3600 or not 1<=args.workers<=8:
        ap.error("Invalid bounded batch limits")
    control(args)

if __name__=="__main__":main()
