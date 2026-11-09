"""Read-only audit of the first unresolved lead in VP05 sector202 A modular reduction.

No SymPy elimination, Kira execution, checkpoint mutation, or proof claim.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from examples.three_loop_sector203_weight_audit import ROOT, load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P

BASE = ROOT / "output/three_loop_integral_family_audit"
CHECKPOINT = BASE / "vp05_sector202_exact_support_checkpoint_support400_col256.json"
SOURCE = BASE / "vp05_sector202_exact_source_rows.json.gz"
CERT = BASE / "vp05_sector202_modular_provenance_certificate.json"
LEAD = (166595341189123, 139)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(args):
    lead = (args.weight, args.order)
    output = args.output.resolve()
    if output in {p.resolve() for p in (args.checkpoint, args.input, args.certificate)}:
        raise ValueError("Output must differ from all inputs")
    if args.output.exists():
        raise FileExistsError("Refusing to overwrite: " + str(args.output))
    checkpoint = json.loads(args.checkpoint.read_text(encoding="utf-8-sig"))
    with gzip.open(args.input, "rt", encoding="utf-8") as stream:
        exported = json.load(stream)
    certificate = json.loads(args.certificate.read_text(encoding="utf-8-sig"))
    cfg = checkpoint.get("config", {})
    if not (
        checkpoint.get("status") == "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF"
        and checkpoint.get("processed") == checkpoint.get("total") == 389
        and checkpoint.get("dependent") == 0
        and len(checkpoint.get("pivots", [])) == 389
        and checkpoint.get("source_pivots_exact_replay_verified") is True
        and cfg.get("target") == "union"
        and cfg.get("source_sha256") == digest(args.input)
        and cfg.get("certificate_sha256") == digest(args.certificate)
    ):
        raise RuntimeError("Checkpoint or source hash validation failed")
    if exported.get("status") != "ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED" or len(exported.get("rows", [])) != 2241:
        raise RuntimeError("Unexpected source export")
    if certificate.get("status") != "MODULAR_ORIGINAL_ROW_CERTIFICATE_VERIFIED_NOT_EXACT_PROOF":
        raise RuntimeError("Unexpected certificate status")
    targets = certificate.get("target_results", [])
    if len(targets) != 2:
        raise RuntimeError("Expected two target results")
    selected = sorted(set(targets[0]["support_original_ids"]) | set(targets[1]["support_original_ids"]))
    if len(selected) != 389 or cfg.get("ids_sha256") != hashlib.sha256(json.dumps(selected).encode()).hexdigest():
        raise RuntimeError("Selected original-source IDs mismatch")
    selected_set = set(selected)
    mod = load_codec((ROOT / "output/tools/pyred_weight.py").resolve())
    bits, ordering = mod.from_kiradb(str(P / "results/kira.db"))
    if ordering != lead[1]:
        # Integral row keys have a distinct ordering ID (139); codec's Kira order is 5.
        if ordering != 5 or lead[1] != 139:
            raise RuntimeError("Unexpected key/codec ordering")
    codec = mod.WeightCodec(np=12, bits=bits, iord=ordering, topsectors=[203])
    powers = list(codec.decode(lead[0]))
    if codec.encode(powers) != lead[0]:
        raise RuntimeError("Weight encode/decode roundtrip failed")
    sector = sum(1 << i for i, power in enumerate(powers) if power > 0)
    matches = []
    for r in exported["rows"]:
        keys = {tuple(term["key"]) for term in r["terms"]}
        if lead in keys:
            rid = r["global_zero_based"]
            matches.append({"source_id": rid, "selected_in_389": rid in selected_set,
                            "row_terms": len(r["terms"])})
    pivot_leads = {tuple(p["lead"]) for p in checkpoint["pivots"]}
    other_pivots = []
    for item in checkpoint["pivots"]:
        if lead in {tuple(key) for key, _ in item["row"]}:
            other_pivots.append(list(item["lead"]))
    report = {
        "status": "UNRESOLVED_LEAD_STRUCTURAL_AUDIT_NOT_PROOF",
        "lead": list(lead), "powers": powers, "sector": sector,
        "checkpoint_sha256": digest(args.checkpoint),
        "source_sha256": digest(args.input),
        "certificate_sha256": digest(args.certificate),
        "lead_is_saved_pivot": lead in pivot_leads,
        "lead_in_saved_pivot_rows_count": len(other_pivots),
        "lead_in_saved_pivot_rows_sample": other_pivots[:20],
        "lead_in_original_source_count": len(matches),
        "lead_in_selected_original_source_count": sum(x["selected_in_389"] for x in matches),
        "original_source_matches": matches[:50],
        "matches_truncated": len(matches) > 50,
        "selected_original_rows": len(selected),
        "source_rows_total": len(exported["rows"]),
        "exact_target_proven": False, "checkpoint_modified": False,
        "kira_executed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=True)
        stream.write("\n")
    print("VP05_SECTOR202_UNRESOLVED_LEAD_AUDIT " + json.dumps(report, ensure_ascii=True), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weight", type=int, default=LEAD[0])
    ap.add_argument("--order", type=int, default=LEAD[1])
    ap.add_argument("--input", type=Path, default=SOURCE)
    ap.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    ap.add_argument("--certificate", type=Path, default=CERT)
    ap.add_argument("--output", type=Path, default=BASE / "vp05_sector202_A_unresolved_lead_audit.json")
    args = ap.parse_args()
    if args.weight < 1 or args.order < 1:
        ap.error("Key components must be positive integers")
    inspect(args)


if __name__ == "__main__":
    main()
