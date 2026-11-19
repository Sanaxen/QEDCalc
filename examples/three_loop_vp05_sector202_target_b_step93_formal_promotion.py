"""Versioned, backup-first formal archive of the independently proven VP05 Target B Step93.

Unlike historic pivot promotion this never overwrites formal Step77 or the
Step93 work/proof/checkpoints. The new versioned formal_state_step93.json plus
manifest is the authoritative proven *Target B identity* artifact.
Default --check-only is strictly read-only. --resume repairs partial copies
only when every existing byte matches the original evidence SHA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import uuid
from pathlib import Path

from examples.three_loop_vp05_sector202_target_b_step77_read_only_audit import inspect as inspect77
from examples.three_loop_vp05_sector202_target_b_step93_independent_proof import (
    B_STATE, BEFORE, CHECKPOINT, CERT, JOURNAL, OUTPUT, PROOF, SOURCE, WORK,
)
from examples import three_loop_vp05_sector202_target_b_step93_independent_proof as independent
from examples.three_loop_vp05_sector202_target_exact_reduction import BASE

PACKAGE = BASE / "vp05_sector202_B_step93_formal_artifact"
MANIFEST = PACKAGE / "formal_manifest.json"
FORMAL = PACKAGE / "formal_state_step93.json"
TAG = "VP05_B_STEP93_FORMAL_PROMOTION "
EXPECTED_STEP77 = "9df3d205bdee62f00533df12da0ee6918861f4d11ae31d91a474f3614d44622f"
EXPECTED_STEP93 = "b3a7793b145e937e8a6f008b7f70f6ed2c3398e52a856797b9e96f54a31b896a"
EXPECTED_PROOF = "de84f75d921d9dc4425864195eebf8fd437336216ab91caa3b5e34856bf9fd89"
PHASE_COUNTS = {"pivot": 393, "source": 537}
STATUS = "FORMAL_STEP93_SECTOR202_TARGET_B_INDEPENDENT_EXACT_PROOF"


def digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def encode(obj):
    return (json.dumps(obj, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")


def inputs():
    """Portable relative evidence names and their immutable original locations."""
    return {
        "formal_state_step93.json": WORK,
        "proof_step93.json": PROOF,
        "before_step93.json": BEFORE,
        "batch_journal.json": JOURNAL,
        "independent_pivot_verified.json": OUTPUT / "pivot_verified.json",
        "independent_source_verified.json": OUTPUT / "source_verified.json",
        "step77_baseline_backup.json": B_STATE,
        "original_exact_support_checkpoint.json": CHECKPOINT,
        "original_source_rows.json.gz": SOURCE,
        "original_source_provenance_certificate.json": CERT,
    }


def preflight():
    """All exact audits must already have passed; no recomputation or writes."""
    if inspect77().get("status") != "B_STEP77_SAVED_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF":
        raise RuntimeError("Step77 independently saved-state audit failed")
    if digest_file(B_STATE) != EXPECTED_STEP77:
        raise RuntimeError("Formal Step77 SHA mismatch")
    if digest_file(WORK) != EXPECTED_STEP93 or digest_file(PROOF) != EXPECTED_PROOF:
        raise RuntimeError("Step93 candidate/proof not the independently inspected exact bytes")
    c = independent.context()
    state, proof = read(WORK), read(PROOF)
    if (state.get("steps") != 93 or state.get("remaining") != []
        or len(state.get("source", [])) != 389
        or proof.get("source_multipliers") != state["source"]
        or proof.get("status") != "EXACT_SINGLE_TARGET_PROVEN"
        or proof.get("original_source_replay_verified") is not True
        or len(c[11]) != 393 or len(c[12]) != 537):
        raise RuntimeError("Incomplete Step93 original-source proof")
    verified = {}
    for phase, required in PHASE_COUNTS.items():
        record, checkpoint_path = independent.verify_progress(phase, c)
        job_count = independent.manifest(phase, c)["job_count"]
        if (not checkpoint_path.is_file() or job_count != required
            or record["verified"] != required):
            raise RuntimeError("Incomplete independent Step93 exact " + phase + " audit")
        verified[phase] = {"verified": required, "sha256": digest_file(checkpoint_path)}
    src = inputs()
    if len({p.resolve() for p in src.values()}) != len(src):
        raise RuntimeError("Evidence inputs overlap")
    hashes = {name: digest_file(p) for name, p in src.items()}
    if (hashes["formal_state_step93.json"] != EXPECTED_STEP93
        or hashes["proof_step93.json"] != EXPECTED_PROOF
        or hashes["step77_baseline_backup.json"] != EXPECTED_STEP77):
        raise RuntimeError("Pinned primary evidence changed during preflight")
    coefficients = encode(state["source"])
    return {"status": "B_STEP93_FORMAL_PROMOTION_PREFLIGHT_PASS",
            "step": 93, "original_ibp_multipliers": 389,
            "pivot_coefficient_keys_verified": 393,
            "original_source_keys_verified": 537,
            "source_and_evidence_sha256": hashes,
            "coefficients_389_sha256": digest_bytes(coefficients),
            "independent_verification": verified,
            "original_formal_state_modified": False,
            "scope": "VP05_full sector202 Target B identity for pinned original IBP data only"}


def write_bytes_once(dest: Path, raw: bytes, expected: str, resume: bool):
    """Publish a complete snapshot by atomic rename, never a partial final file.

    A crash can leave a uniquely named staging file, but --resume will safely
    start another copy. Existing published snapshots are never overwritten.
    """
    if dest.exists():
        if not resume or digest_file(dest) != expected:
            raise FileExistsError("Existing evidence differs: " + str(dest))
        return
    if digest_bytes(raw) != expected:
        raise RuntimeError("Generated evidence SHA mismatch")
    dest.parent.mkdir(parents=True, exist_ok=True)
    stage = dest.with_name(dest.name + "." + uuid.uuid4().hex + ".staging")
    try:
        with stage.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if digest_file(stage) != expected:
            raise RuntimeError("Staged snapshot SHA mismatch: " + str(stage))
        if dest.exists():
            raise FileExistsError("Another promotion already published: " + str(dest))
        os.replace(stage, dest)
        if digest_file(dest) != expected:
            raise RuntimeError("Published snapshot SHA mismatch: " + str(dest))
    finally:
        if stage.exists():
            stage.unlink()


def copy_exact(source: Path, dest: Path, expected: str, resume: bool):
    if dest.exists():
        if not resume or digest_file(dest) != expected:
            raise FileExistsError("Existing snapshot not authorized for overwrite: " + str(dest))
        return
    raw = source.read_bytes()
    if digest_bytes(raw) != expected:
        raise RuntimeError("Evidence changed while copying: " + str(source))
    write_bytes_once(dest, raw, expected, resume)


def promote(resume=False):
    """Versioned promotion; never replace the historic formal-state pathname."""
    report = preflight()
    if MANIFEST.exists():
        raise FileExistsError("Formal manifest already exists; run --post-audit")
    if resume:
        if not PACKAGE.is_dir():
            raise FileNotFoundError("No partial archive to resume")
    else:
        PACKAGE.mkdir(parents=True, exist_ok=False)
    if any(p.resolve() == PACKAGE.resolve() or PACKAGE.resolve() in p.resolve().parents
           for p in inputs().values()):
        raise RuntimeError("Archive overlaps protected inputs")
    evidence = PACKAGE / "evidence"
    evidence.mkdir(exist_ok=True)
    for name, source in inputs().items():
        target = FORMAL if name == "formal_state_step93.json" else evidence / name
        copy_exact(source, target, report["source_and_evidence_sha256"][name], resume)
    multipliers = encode(read(WORK)["source"])
    write_bytes_once(evidence / "source_multipliers_389.json",
                     multipliers, report["coefficients_389_sha256"], resume)
    # Check originals and every byte in the new archive before committing.
    after = preflight()
    if after != report:
        raise RuntimeError("Protected evidence changed while archiving")
    data = {"version": 1, "status": STATUS,
            "formal_state": "formal_state_step93.json",
            "original_formal_step77_preserved": True,
            "backup": "evidence/step77_baseline_backup.json",
            "proof": "evidence/proof_step93.json",
            "coefficients": "evidence/source_multipliers_389.json",
            "source_and_evidence_sha256": report["source_and_evidence_sha256"],
            "coefficients_389_sha256": report["coefficients_389_sha256"],
            "independent_verification": report["independent_verification"],
            "pivot_keys": 393, "original_source_keys": 537,
            "original_ibp_multipliers": 389, "steps": 93,
            "target_b_proven_within_pinned_source": True,
            "formal_step77_sha256": EXPECTED_STEP77,
            "formal_step93_sha256": EXPECTED_STEP93,
            "scope": report["scope"],
            "entire_vp05_family_proven": False,
            "all_three_loop_diagrams_proven": False}
    # Completion marker is LAST, exclusively created; interruption before
    # this point can be restarted with --resume without overwriting evidence.
    write_bytes_once(MANIFEST, encode(data), digest_bytes(encode(data)), False)
    return post_audit()


def post_audit():
    """Read-only audit of *saved bytes* against original independent evidence."""
    if not MANIFEST.exists():
        raise FileNotFoundError("Formal manifest missing (partial archive: use --resume)")
    manifest = read(MANIFEST)
    if (manifest.get("version") != 1 or manifest.get("status") != STATUS
        or manifest.get("formal_state") != "formal_state_step93.json"
        or manifest.get("steps") != 93 or manifest.get("pivot_keys") != 393
        or manifest.get("original_source_keys") != 537
        or manifest.get("original_ibp_multipliers") != 389
        or manifest.get("target_b_proven_within_pinned_source") is not True
        or manifest.get("entire_vp05_family_proven") is not False
        or manifest.get("all_three_loop_diagrams_proven") is not False
        or manifest.get("formal_step77_sha256") != EXPECTED_STEP77
        or manifest.get("formal_step93_sha256") != EXPECTED_STEP93):
        raise RuntimeError("Invalid formal archive manifest")
    report = preflight()
    if (manifest.get("source_and_evidence_sha256") != report["source_and_evidence_sha256"]
        or manifest.get("coefficients_389_sha256") != report["coefficients_389_sha256"]
        or manifest.get("independent_verification") != report["independent_verification"]):
        raise RuntimeError("Independent exact proof manifest/evidence mismatch")
    expected = manifest["source_and_evidence_sha256"]
    for name, path in inputs().items():
        dest = FORMAL if name == "formal_state_step93.json" else PACKAGE / "evidence" / name
        if digest_file(path) != expected[name] or digest_file(dest) != expected[name]:
            raise RuntimeError("Source or saved evidence diverged: " + name)
    coefficients = PACKAGE / "evidence/source_multipliers_389.json"
    if (digest_file(coefficients) != manifest["coefficients_389_sha256"]
        or read(coefficients) != read(FORMAL)["source"]
        or read(coefficients) != read(PACKAGE / "evidence/proof_step93.json")["source_multipliers"]
        or read(FORMAL)["remaining"] != []
        or digest_file(B_STATE) != EXPECTED_STEP77):
        raise RuntimeError("Saved 389 coefficients, proof or baseline do not match")
    return {"status": "B_STEP93_FORMAL_ARTIFACT_POST_AUDIT_PASS",
            "steps": 93, "original_ibp_multipliers": 389,
            "pivot_coefficient_keys_verified": 393,
            "original_source_keys_verified": 537,
            "formal_state_path": str(FORMAL),
            "formal_state_sha256": digest_file(FORMAL),
            "formal_manifest_sha256": digest_file(MANIFEST),
            "original_step77_preserved": True,
            "original_step93_evidence_preserved": True,
            "target_b_proven_within_pinned_source": True,
            "entire_vp05_family_proven": False}


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check-only", action="store_true")
    mode.add_argument("--promote", action="store_true")
    mode.add_argument("--resume", action="store_true")
    mode.add_argument("--post-audit", action="store_true")
    args = parser.parse_args()
    if args.promote:
        result = promote(False)
    elif args.resume:
        result = promote(True)
    elif args.post_audit:
        result = post_audit()
    else:
        result = preflight()
    print(TAG + json.dumps(result, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
