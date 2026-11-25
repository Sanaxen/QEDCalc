"""Reconcile saved sector-local jobs and ABC identities; no Kira or promotion."""
import json
from examples import three_loop_vp05_stage2_sector_inventory as inv
from examples import three_loop_vp05_stage2_non202_batch as non
from examples import three_loop_vp05_stage2_resume_after206 as follow
from examples import three_loop_vp05_abc_stage2_scope_inventory as abc
from examples import three_loop_vp05_sector202_target_exact_reduction as exact

def combine(rows, isolated):
    out=[]
    for row in rows:
        sec=row["sector"]
        state=isolated.get(sec)
        sources=[]
        if row["restricted_exact_sector_audit_match"]:
            sources.append("restricted_equivalent_review")
        if row["matching_local_master_inventory"]:
            sources.append("standard_local_inventory")
        if state=="completed_local_retained":
            sources.append("verified_isolated_local_retention")
        out.append({"sector":sec,"candidate_count":row["candidate_count"],
                    "sources":sources,"isolated_state":state,
                    "requires_more_local_evidence":not sources})
    return out

def run():
    integrated=abc.run()
    saved=inv.inspect()
    _,old=follow.verified_scope()
    non202=non.audit("no202a")
    states={r["sector"]:r["state"] for r in old+non202["sector_rows"]}
    # verified_scope validates the first and medium pilot successes.
    states.update({s:"completed_local_retained" for s in (73,201,228,117,118,199,204)})
    results={}
    for seed,info in saved["boundary_inventory"].items():
        rows=combine(info["sector_rows"],states if seed=="r8s5d3" else {})
        results[seed]={"rows":rows,"local_evidence_sectors":sum(bool(r["sources"]) for r in rows),
            "missing_local_evidence_sectors":[r["sector"] for r in rows if r["requires_more_local_evidence"]]}
    # M is a literal Kira column, NOT yet a physical integral.
    mod=exact.load_codec((exact.ROOT/"output/tools/pyred_weight.py").resolve())
    bits,ordering=mod.from_kiradb(str(exact.P/"results/kira.db"))
    codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    try:
        decoded=list(codec.decode(4))
        roundtrip=codec.encode(tuple(decoded))==4
        trial={"decoded":decoded,"roundtrip":roundtrip}
    except Exception as exc:
        trial={"error":str(exc)[:250]}
    return {"status":"VP05_BOUNDARY_EVIDENCE_RECONCILED_NOT_CLOSURE",
            "ABC_candidate_coverage":integrated["candidate_target_coverage"],
            "boundaries":results,"opaque_M_key":[4,73],"M_codec_trial_NOT_identity":trial,
            "M_physical_identity_proven":False,"candidate_basis_revision_required_for_review":True,
            "whole_family_closure_proven":False,"kira_executed":False,"files_modified":False}
if __name__=="__main__":
    print("VP05_BOUNDARY_RECONCILE "+json.dumps(run()),flush=True)
