"""Exact unscaled original-IBP pivot replay for difficult B Step64 keys.

The previous 259 coefficient updates have been independently checked with
exact rational-function identities; given a nonzero pivot multiplier, the
full Step63-to-Step64 replay difference is exactly the pivot multiplier
times (pivot_row - sum(pivot_trace*original_IBP)). This module checks that
unscaled *exact symbolic* identity, without numerical or modular shortcuts.
Formal B state and saved replay checkpoints are never modified here.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import sympy as sp

from examples.three_loop_vp05_sector202_target_b_step64_original_ibp_replay import (
    load, REPORT, OUT, STATE, AUDIT, EXPECTED_STEP63_SHA, EXPECTED_CANDIDATE_SHA,
    SOURCE, CHECKPOINT, CERT, sha,
)
from examples.three_loop_vp05_sector202_target_b_step64_exact_candidate import (
    load_context,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr


def verify_index(index):
    before,assembled,assembled_sha,old_rem,new_rem,old_src,new_src,jobs,by_key=load()
    if not 0<=index<len(jobs):
        raise ValueError("Out-of-range exact replay key index")
    args=argparse.Namespace(state=STATE, source_checkpoint=CHECKPOINT,
                            input=SOURCE,certificate=CERT)
    state,pivot,coefficient_jobs,binding=load_context(args)
    candidate=json.loads(OUT.read_text(encoding="utf-8-sig"))
    audit=json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    checks=audit.get("checked",[])
    done=candidate.get("done",[])
    if (len(coefficient_jobs)!=259 or len(checks)!=259 or len(done)!=259
        or candidate.get("config")!=binding
        or audit.get("config",{}).get("candidate_sha256")!=EXPECTED_CANDIDATE_SHA
        or audit.get("config",{}).get("state_step63_sha256")!=EXPECTED_STEP63_SHA
        or any(row.get("index")!=i or row.get("id")!=done[i]["id"]
               or row.get("coefficient_sha256")!=hashlib.sha256(done[i]["value"].encode()).hexdigest()
               for i,row in enumerate(checks))):
        raise RuntimeError("Independent exact local coefficient certificate incomplete")
    lead=min(tuple(k) for k,_ in state["remaining"])
    if lead!=(166596413882370,139) or tuple(pivot["lead"])!=lead:
        raise RuntimeError("Unexpected checkpoint source pivot lead")
    z,d=sp.symbols("z d")
    factor=expr(dict((tuple(k),v) for k,v in state["remaining"])[lead],z,d)
    if factor==0:
        raise RuntimeError("A zero pivot multiplier invalidates normalization")
    key=jobs[index]
    pivot_row={tuple(k):v for k,v in pivot["row"]}
    pivot_trace={int(rid):v for rid,v in pivot["trace"]}
    with gzip.open(SOURCE,"rt",encoding="utf-8") as fh:
        source=json.load(fh)
    terms=[]
    source_ids=set(pivot_trace)
    for row in source["rows"]:
        rid=int(row["global_zero_based"])
        if rid not in source_ids:
            continue
        for term in row["terms"]:
            if tuple(term["key"])==key:
                terms.append(expr(pivot_trace[rid],z,d)*expr(term["coefficient"],z,d))
    # Exact identity: pivot_row == sum(trace*original IBP rows).
    # Independently checked Step64 coefficient updates imply the full replay
    # equality after multiplication by the nonzero Step63 pivot coefficient.
    result=sp.cancel(expr(pivot_row.get(key,"0"),z,d)-sp.Add(*terms))
    if result!=0:
        raise AssertionError("Unscaled original IBP pivot identity failed "+str(key))
    if (sha(STATE)!=EXPECTED_STEP63_SHA or sha(OUT)!=EXPECTED_CANDIDATE_SHA
        or sha(REPORT)!=assembled_sha):
        raise RuntimeError("Inputs changed during normalized exact replay")
    return {
        "event":"EXACT_ORIGINAL_IBP_KEY_PASS",
        "index":index,"key":list(key),
        "assembled_sha256":assembled_sha,
        "method":"unscaled_source_pivot_exact_with_259_certificates",
        "source_terms_in_key":len(terms),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--index",type=int,required=True)
    args=ap.parse_args()
    print("VP05_B_STEP64_ORIGINAL_IBP_REPLAY "+json.dumps(verify_index(args.index)),flush=True)


if __name__=="__main__":
    main()
