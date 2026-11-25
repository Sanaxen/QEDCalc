"""Archive audited A proof without modifying original files or registry."""
import json
import os
from pathlib import Path
from examples import three_loop_vp05_a_saved_proof_audit as audit
from examples import three_loop_vp05_a_fieldpilot_target_proof as proof
from examples import three_loop_vp05_sector202_a_exact_batch as batch

DEST=proof.OUTPUT.parent/"vp05_sector202_target_a_confirmed_v1"

def run():
    result=audit.audit()
    if result["status"]!="VP05_A_SAVED_PROOF_READ_ONLY_AUDIT_PASS":
        raise RuntimeError("Saved proof audit failed")
    if DEST.is_symlink() or DEST.exists():
        raise FileExistsError("Archive exists; preserve for review")
    DEST.mkdir()
    target=DEST/proof.OUTPUT.name
    raw=proof.OUTPUT.read_bytes()
    with target.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    if batch.sha(target)!=audit.PROOF_SHA or batch.sha(proof.OUTPUT)!=audit.PROOF_SHA:
        raise RuntimeError("Archive copy hash mismatch")
    manifest={"status":"VP05_A_CONFIRMED_PROOF_ARCHIVE",
        "target":"A","original_support":339,"proof_file":target.name,
        "proof_sha256":audit.PROOF_SHA,"checkpoint_sha256":proof.PIN,
        "source_sha256":batch.SOURCE_SHA,"certificate_sha256":batch.CERT_SHA,
        "saved_proof_audit":result,"archive_copy_verified":True,
        "registry_promotion_completed":False,"whole_family_63_closure_proven":False}
    path=DEST/"manifest.json"
    with path.open("x",encoding="utf-8") as stream:
        json.dump(manifest,stream,indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    if json.loads(path.read_text(encoding="utf-8"))!=manifest or batch.sha(target)!=audit.PROOF_SHA:
        raise RuntimeError("Saved archive verification failed")
    print("VP05_A_CONFIRMED_ARCHIVE "+json.dumps({"status":manifest["status"],
        "archive":str(DEST),"proof_sha256":audit.PROOF_SHA,
        "manifest_sha256":batch.sha(path),"original_support":339,
        "registry_promotion_completed":False}),flush=True)

if __name__=="__main__":
    run()
