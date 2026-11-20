"""Read-only single *real original-IBP pivot* exact field-vs-SymPy pilot.

Not a source-row completion or Target A proof. Verifies both results by
replaying the original exported IBP equations, never writes checkpoint.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from examples import three_loop_vp05_exact_arithmetic_probe as ar
from examples import three_loop_vp05_sector202_exact_support_checkpoint as engine

EXPECTED_A_CHECKPOINT_SHA256 = "90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297"
EXPECTED_SOURCE_SHA256 = "f0dd7f338ead97e455306bc49c4ce475fe8a8bee3e5a866f6fa17de1e9ad0163"
EXPECTED_CERT_SHA256 = "512114a669d3fb8761d89bfe11a51cc8ec146d46739a36b61e869edcddb583eb"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validated_inputs(checkpoint: Path, source: Path, certificate: Path):
    # Fingerprint all three immutable source artifacts before parsing.
    for path in (checkpoint, source, certificate):
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("Missing or symbolic-link protected input: " + str(path))
    checkpoint_bytes = checkpoint.read_bytes()
    source_bytes = source.read_bytes()
    cert_bytes = certificate.read_bytes()
    if sha(checkpoint_bytes) != EXPECTED_A_CHECKPOINT_SHA256:
        raise RuntimeError("Protected 296-row checkpoint SHA256 mismatch")
    if sha(source_bytes) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("Original exact source rows SHA256 mismatch")
    if sha(cert_bytes) != EXPECTED_CERT_SHA256:
        raise RuntimeError("Original provenance certificate SHA256 mismatch")
    saved = json.loads(checkpoint_bytes.decode("utf-8-sig"))
    cert = json.loads(cert_bytes.decode("utf-8-sig"))
    source_data = json.loads(gzip.decompress(source_bytes))
    if (saved.get("version") != 1 or
        saved.get("status") != "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF" or
        saved.get("config", {}).get("target") != "A" or
        saved["config"].get("source_sha256") != EXPECTED_SOURCE_SHA256 or
        saved["config"].get("certificate_sha256") != EXPECTED_CERT_SHA256 or
        saved.get("processed") != 296 or saved.get("total") != 339 or
        saved.get("dependent") != 0 or
        len(saved.get("pivots", [])) != 296 or
        saved.get("source_pivots_exact_replay_verified") is not True or
        saved.get("exact_target_reduction_proven") is not False):
        raise RuntimeError("Unexpected saved Target A checkpoint state")
    if (cert.get("status") !=
            "MODULAR_ORIGINAL_ROW_CERTIFICATE_VERIFIED_NOT_EXACT_PROOF" or
        cert.get("point") != [1000003, 17, 7] or
        source_data.get("status") != "ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED" or
        len(source_data.get("rows", [])) != 2241):
        raise RuntimeError("Unexpected original source/certificate structure")
    targets = cert.get("target_results", [])
    if len(targets) != 2 or targets[0].get("target_index") != 0:
        raise RuntimeError("Unexpected original Target A certificate")
    ids = sorted(targets[0]["support_original_ids"])
    if len(ids) != 339:
        raise RuntimeError("Unexpected 339-source selection")
    if sha(json.dumps(ids).encode()) != saved["config"].get("ids_sha256"):
        raise RuntimeError("Original source ID selection differs from saved state")
    return saved, {r["global_zero_based"]: r for r in source_data["rows"]}, ids



def compare_pivot_step(cur, trace, brow, btrace, factor, rows, z, d):
    """Compare one genuine pivot step and independently replay original IBP."""
    before = time.monotonic()
    old_row = ar.sympy_sparse_subtract(cur, brow, factor)
    old_trace = ar.sympy_sparse_subtract(trace, btrace, factor)
    baseline_s = time.monotonic() - before
    conversion_start = time.monotonic()
    field_cur = {k: ar.FIELD.from_expr(v) for k, v in cur.items()}
    field_brow = {k: ar.FIELD.from_expr(v) for k, v in brow.items()}
    field_trace = {k: ar.FIELD.from_expr(v) for k, v in trace.items()}
    field_btrace = {k: ar.FIELD.from_expr(v) for k, v in btrace.items()}
    field_factor = ar.FIELD.from_expr(factor)
    conversion_s = time.monotonic() - conversion_start
    field_start = time.monotonic()
    for dest, src in ((field_cur, field_brow), (field_trace, field_btrace)):
        for key, value in src.items():
            updated = dest.get(key, ar.FIELD.zero) - field_factor * value
            if updated == ar.FIELD.zero:
                dest.pop(key, None)
            else:
                dest[key] = updated
    field_update_s = time.monotonic() - field_start
    back_start = time.monotonic()
    new_row = {k: v.as_expr() for k, v in field_cur.items()}
    new_trace = {k: v.as_expr() for k, v in field_trace.items()}
    back_conversion_s = time.monotonic() - back_start
    equality_start = time.monotonic()
    row_equal = ar.exact_same(old_row, new_row)
    trace_equal = ar.exact_same(old_trace, new_trace)
    if not (row_equal and trace_equal):
        raise AssertionError("Field/old exact pivot-step mismatch")
    engine.verify(new_row, new_trace, rows, z, d)
    verification_s = time.monotonic() - equality_start
    return {
        "output_columns": len(new_row),
        "output_provenance_support": len(new_trace),
        "baseline_row_plus_trace_s": round(baseline_s, 6),
        "field_conversion_s": round(conversion_s, 6),
        "field_row_plus_trace_update_s": round(field_update_s, 6),
        "field_back_conversion_s": round(back_conversion_s, 6),
        "strict_exact_row_equal": row_equal,
        "strict_exact_trace_equal": trace_equal,
        "original_ibp_source_replay_verified": True,
        "verification_s": round(verification_s, 6),
    }


def real_first_pivot(checkpoint: Path, source: Path, certificate: Path):
    saved, rows, ids = validated_inputs(checkpoint, source, certificate)
    rid = ids[saved["processed"]]
    z, d = ar.Z, ar.D
    cur = {}
    for term in rows[rid]["terms"]:
        key = tuple(term["key"])
        val = sp.cancel(cur.get(key, sp.S.Zero) +
                        engine.expr(term["coefficient"], z, d))
        if val:
            cur[key] = val
        else:
            cur.pop(key, None)
    if not cur:
        raise RuntimeError("Next source equation is identically zero before a pivot")
    lead = min(cur)
    matching = [entry for entry in saved["pivots"]
                if tuple(entry["lead"]) == lead]
    if len(matching) != 1:
        raise RuntimeError("Next original source leading key is not a unique saved pivot")
    entry = matching[0]
    brow = engine.decode_terms(entry["row"], z, d)
    btrace = {int(k): engine.expr(v, z, d) for k, v in entry["trace"]}
    if min(brow) != lead or sp.cancel(brow[lead] - 1) != 0:
        raise RuntimeError("Saved pivot not normalized")
    if not set(btrace).issubset(set(ids[:296])):
        raise RuntimeError("Saved pivot trace references an unprocessed source row")
    # Verify exactly the selected saved pivot, not all 296, before use.
    engine.verify(brow, btrace, rows, z, d)
    trace = {rid: sp.S.One}
    factor = cur[lead]
    measurements = compare_pivot_step(cur, trace, brow, btrace, factor, rows, z, d)
    if sha(checkpoint.read_bytes()) != EXPECTED_A_CHECKPOINT_SHA256:
        raise RuntimeError("Checkpoint SHA changed during read-only pilot")
    return {
        "status": "REAL_ORIGINAL_IBP_FIRST_PIVOT_EXACT_PASS_NOT_TARGET_PROOF",
        "original_source_id": rid, "pivot": list(lead),
        "source_row_columns": len(cur),
        "saved_pivot_columns": len(brow),
        "saved_pivot_provenance_support": len(btrace),
        "checkpoint_sha256": EXPECTED_A_CHECKPOINT_SHA256,
        "checkpoint_processed": 296,
        "checkpoint_modified": False,
        "production_engine_modified": False,
        "target_A_proven": False,
        "real_original_ibp_path_replayed": True,
        "real_original_ibp_path_steps": 1,
        "kira_executed": False,
        **measurements,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--source", type=Path, default=engine.SOURCE)
    ap.add_argument("--certificate", type=Path, default=engine.CERT)
    args = ap.parse_args()
    result = real_first_pivot(args.checkpoint, args.source, args.certificate)
    print("VP05_REAL_FIRST_PIVOT_FIELD_PROBE " + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
