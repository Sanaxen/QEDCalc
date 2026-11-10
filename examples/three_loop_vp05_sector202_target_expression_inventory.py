"""Read-only size/structure inventory of a saved sector202 exact target state.

Does not evaluate another elimination step or modify any state.  Only shows
bounded previews of the longest coefficient strings.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "output/three_loop_integral_family_audit"
DEFAULT_STATE = BASE / "vp05_sector202_A_exact_target_state.json"
DEFAULT_SOURCE_CHECKPOINT = BASE / "vp05_sector202_exact_support_checkpoint_support400_col256.json"
DEFAULT_SOURCE = BASE / "vp05_sector202_exact_source_rows.json.gz"
DEFAULT_CERT = BASE / "vp05_sector202_modular_provenance_certificate.json"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rank_entries(state, count, preview):
    entries = []
    for kind, field in (("remainder", "remaining"), ("source_trace", "source")):
        for key, coefficient in state[field]:
            value = str(coefficient)
            entries.append({"kind":kind,"key":key,
                            "chars":len(value),"preview":value[:preview],
                            "has_additive_terms":(" + " in value or " - " in value),
                            "has_division":"/" in value})
    entries.sort(key=lambda e: (-e["chars"], e["kind"], str(e["key"])))
    return entries[:count]

def inspect(state, source_checkpoint, source, cert, count=5, preview=120):
    config = state.get("config", {})
    required = {
        "source_checkpoint_sha256": source_checkpoint,
        "source_sha256": source,
        "certificate_sha256": cert,
    }
    for field, path in required.items():
        if config.get(field) != digest(path):
            raise RuntimeError("Saved target state input digest mismatch: "+field)
    if (state.get("version") != 1 or
            state.get("status") not in
                ("EXACT_TARGET_PREFIX_NOT_PROOF", "EXACT_TARGET_CAP_REACHED_NOT_PROOF") or
            state.get("exact_target_proven") is not False or
            not isinstance(state.get("steps"), int) or state["steps"] < 0):
        raise RuntimeError("Unexpected target state status/version")
    if len(state.get("pivot_path", [])) != state["steps"]:
        raise RuntimeError("Target state pivot path length mismatch")
    reported = state["metrics"]
    actual_row = max((len(str(x[1])) for x in state["remaining"]), default=0)
    actual_source = max((len(str(x[1])) for x in state["source"]), default=0)
    if (reported["row_expression_chars"] != actual_row or
            reported["source_expression_chars"] != actual_source or
            reported["remainder_terms"] != len(state["remaining"]) or
            reported["original_support"] != len(state["source"])):
        raise RuntimeError("Stored target state metrics disagree with serialized data")
    return {
        "status":"READ_ONLY_TARGET_EXPRESSION_INVENTORY_NOT_PROOF",
        "target":config.get("target"),
        "steps":state["steps"],
        "remainder_terms":len(state["remaining"]),
        "original_support":len(state["source"]),
        "row_expression_chars":actual_row,
        "source_expression_chars":actual_source,
        "max_expression_chars_limit":config.get("max_expression_chars"),
        "largest_entries":rank_entries(state,count,preview),
        "checkpoint_modified":False,
        "next_step_executed":False,
        "exact_target_proven":False,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--state",type=Path,default=DEFAULT_STATE)
    ap.add_argument("--source-checkpoint",type=Path,default=DEFAULT_SOURCE_CHECKPOINT)
    ap.add_argument("--input",type=Path,default=DEFAULT_SOURCE)
    ap.add_argument("--certificate",type=Path,default=DEFAULT_CERT)
    ap.add_argument("--top",type=int,default=5)
    ap.add_argument("--preview-chars",type=int,default=120)
    ap.add_argument("--output",type=Path,default=BASE/"vp05_sector202_A_exact_step50_expression_inventory.json")
    args=ap.parse_args()
    if not 1<=args.top<=20 or not 0<=args.preview_chars<=240:
        ap.error("--top must be 1..20 and --preview-chars 0..240")
    protected={p.resolve() for p in
               (args.state,args.source_checkpoint,args.input,args.certificate)}
    if args.output.resolve() in protected:
        ap.error("Inventory output must not overwrite input artifacts")
    if args.output.exists():
        raise FileExistsError("Refusing to overwrite inventory: "+str(args.output))
    state=json.loads(args.state.read_text(encoding="utf-8-sig"))
    report=inspect(state,args.source_checkpoint,args.input,args.certificate,
                   args.top,args.preview_chars)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as handle:
        json.dump(report,handle,indent=2,ensure_ascii=True)
        handle.write("\n")
    print("VP05_SECTOR202_TARGET_EXPRESSION_INVENTORY "+
          json.dumps(report,ensure_ascii=True),flush=True)

if __name__=="__main__":
    main()
