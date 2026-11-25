"""Read-only integration inventory, not a boundary closure or promotion."""
import json
from examples import three_loop_vp05_stage2_step93_gap_audit as gap
from examples import three_loop_vp05_a_confirmed_archive as archive
from examples import three_loop_vp05_a_saved_proof_audit as a
from examples import three_loop_vp05_c_saved_rank_audit as c
from examples import three_loop_vp05_sector202_a_exact_batch as batch

def run():
    if batch.sha(archive.DEST/"manifest.json")!="c4b285f0066160f0bf443ad2278b6e9dfe183fd033aa78bcbde078ddaf43529e":
        raise RuntimeError("A archive manifest mismatch")
    if batch.sha(archive.DEST/a.proof.OUTPUT.name)!=a.PROOF_SHA:
        raise RuntimeError("Archived A proof mismatch")
    if batch.sha(c.cert.OUTPUT)!=c.SHA:
        raise RuntimeError("C certificate mismatch")
    report=gap.inspect()
    if report["step93_target_b"]["formal_archive_verified"] is not True:
        raise RuntimeError("B archive not verified")
    manifest=gap.read(gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json")
    return {"status":"VP05_ABC_STAGE2_SCOPE_INVENTORY_NOT_CLOSURE",
            "A_archive_sha256":a.PROOF_SHA,"C_certificate_sha256":c.SHA,
            "candidate_target_coverage":gap.target_coverage(manifest.get("candidate_masters",[])),
            "closure_target_coverage":gap.target_coverage(manifest.get("closure_targets",[])),
            "stage2":report,"restricted_ABC_evidence_only":True,
            "extended_seed_equivalence_proven":False,"family_registry_changed":False}
if __name__=="__main__":
    print("VP05_ABC_STAGE2 "+json.dumps(run()),flush=True)
