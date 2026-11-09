"""Read-only bounded finite-field rank extension for VP05 sector202 A.

Only candidate screening: NEVER a symbolic target proof. Original checkpoint
and exported equations are not modified.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json
from collections import Counter
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_weight_audit import ROOT, load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P, TARGETS
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CERT, CHECKPOINT, SOURCE, FORMULAS, POINTS, modular, target_row,
)

MISSING = (166595341189123, 139)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def add(dest, row, factor, prime):
    for key, coefficient in row.items():
        value = (dest.get(key, 0) + factor * coefficient) % prime
        if value: dest[key] = value
        else: dest.pop(key, None)

def forward(row, basis, prime, max_steps, max_columns):
    current = dict(row)
    steps = 0
    if len(current) > max_columns:
        return current, steps, "COLUMN_CAP"
    while current:
        lead = min(current)
        if lead not in basis:
            return current, steps, "UNRESOLVED_LEAD"
        if steps >= max_steps:
            return current, steps, "STEP_CAP"
        add(current, basis[lead], -current[lead], prime)
        steps += 1
        if len(current) > max_columns:
            return current, steps, "COLUMN_CAP"
    return current, steps, "ZERO_REMAINDER"

def specialized(terms, z, d, point):
    result = {}
    for term in terms:
        key = tuple(term["key"])
        value = modular(expr(term["coefficient"], z, d), z, d, point)
        add(result, {key:value}, 1, point[0])
    return result

def load_data(args):
    inputs = (args.checkpoint, args.input, args.certificate)
    if args.output.resolve() in {path.resolve() for path in inputs}:
        raise ValueError("Output overlaps an input")
    if args.output.exists():
        raise FileExistsError("Output exists: " + str(args.output))
    checkpoint = json.loads(args.checkpoint.read_text(encoding="utf-8-sig"))
    with gzip.open(args.input, "rt", encoding="utf-8") as stream:
        source = json.load(stream)
    cert = json.loads(args.certificate.read_text(encoding="utf-8-sig"))
    cfg = checkpoint.get("config", {})
    if not (checkpoint.get("status") == "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF"
        and checkpoint.get("processed") == checkpoint.get("total") == 389
        and checkpoint.get("dependent") == 0
        and len(checkpoint.get("pivots", [])) == 389
        and checkpoint.get("source_pivots_exact_replay_verified") is True
        and cfg.get("target") == "union"
        and cfg.get("source_sha256") == sha(args.input)
        and cfg.get("certificate_sha256") == sha(args.certificate)):
        raise RuntimeError("Checkpoint/hash mismatch")
    if source.get("status") != "ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED" or len(source.get("rows", [])) != 2241:
        raise RuntimeError("Unexpected source export")
    if cert.get("status") != "MODULAR_ORIGINAL_ROW_CERTIFICATE_VERIFIED_NOT_EXACT_PROOF":
        raise RuntimeError("Unexpected certificate")
    results = cert.get("target_results", [])
    if len(results) != 2:
        raise RuntimeError("Missing A/B support")
    selected = sorted(set(results[0]["support_original_ids"]) | set(results[1]["support_original_ids"]))
    if len(selected) != 389 or cfg.get("ids_sha256") != hashlib.sha256(json.dumps(selected).encode()).hexdigest():
        raise RuntimeError("Source selection mismatch")
    ids = [row["global_zero_based"] for row in source["rows"]]
    if len(set(ids)) != 2241 or not set(selected).issubset(ids):
        raise RuntimeError("Source IDs mismatch")
    return checkpoint, source, set(selected)

def run(args):
    checkpoint, source, selected = load_data(args)
    point = POINTS[args.point_index]
    prime = point[0]
    z, d = sp.symbols("z d")
    basis = {}
    for item in checkpoint["pivots"]:
        lead = tuple(item["lead"])
        if lead in basis: raise RuntimeError("Duplicate pivot")
        terms = [{"key":key, "coefficient":v} for key,v in item["row"]]
        row = specialized(terms, z, d, point)
        if not row or min(row) != lead or row[lead] != 1:
            raise RuntimeError("Pivot specialization mismatch")
        basis[lead] = row
    mod = load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
    bits, order = mod.from_kiradb(str(P/"results/kira.db"))
    if order != 5: raise RuntimeError("Unexpected Kira order")
    codec = mod.WeightCodec(np=12, bits=bits, iord=order, topsectors=[203])
    keys = [(codec.encode(v),139) for v in TARGETS]
    if any(tuple(codec.decode(k[0])) != v for k,v in zip(keys,TARGETS)):
        raise RuntimeError("Target encoding mismatch")
    target_sym = target_row("A",keys,[expr(f,z,d) for f in FORMULAS])
    target = {k:value for k,v in target_sym.items()
              if (value:=modular(v,z,d,point)) != 0}
    base_rem, base_steps, base_status = forward(target,basis,prime,args.max_steps,args.max_columns)
    if base_status != "UNRESOLVED_LEAD" or min(base_rem) != MISSING:
        raise RuntimeError("Baseline missing lead not reproduced; increase caps or inspect inputs")
    candidates = [r for r in source["rows"] if r["global_zero_based"] not in selected]
    if len(candidates) != 1852: raise RuntimeError("Expected 1852 outside rows")
    candidates = candidates[:args.max_candidates]
    counts = Counter()
    additions, changes, capped = [], [], []
    last = {"status":base_status,"steps":base_steps,"lead":list(min(base_rem)),
            "remainder_terms":len(base_rem)}
    stopped_zero = stopped_rank_cap = False
    for idx,item in enumerate(candidates,1):
        rid = item["global_zero_based"]
        try:
            row = specialized(item["terms"], z, d, point)
        except (ZeroDivisionError,ValueError) as exc:
            counts["SINGULAR_SOURCE_ROW"] += 1
            capped.append({"id":rid,"status":"SINGULAR_SOURCE_ROW","detail":str(exc)[:120]})
            continue
        rem,steps,status = forward(row,basis,prime,args.max_steps,args.max_columns)
        counts[status] += 1
        if status in ("STEP_CAP","COLUMN_CAP"):
            capped.append({"id":rid,"status":status,"steps":steps,"columns":len(rem)})
            continue
        if status == "ZERO_REMAINDER":
            continue
        if status != "UNRESOLVED_LEAD" or not rem:
            raise RuntimeError("Unexpected candidate status")
        if len(additions) >= args.max_new_pivots:
            stopped_rank_cap = True
            break
        lead = min(rem)
        inverse = pow(rem[lead],-1,prime)
        normalized = {k:v*inverse%prime for k,v in rem.items()}
        if lead in basis or normalized[lead] != 1:
            raise RuntimeError("Invalid independent pivot")
        basis[lead] = normalized
        additions.append({"original_id":rid,"new_pivot":list(lead),
                          "columns":len(normalized),"steps":steps})
        tr,ts,tstatus = forward(target,basis,prime,args.max_steps,args.max_columns)
        now = {"status":tstatus,"steps":ts,
               "lead":list(min(tr)) if tr else None,"remainder_terms":len(tr)}
        if now != last:
            changes.append({"after_original_id":rid,
                            "added_count":len(additions),**now})
        last = now
        if tstatus == "ZERO_REMAINDER" and args.stop_at_zero:
            stopped_zero = True
            break
        if idx % args.progress_every == 0:
            print("VP05_SECTOR202_RANK_EXTENSION_PROGRESS "+json.dumps(
                {"scanned":idx,"independent":len(additions),
                 "capped":len(capped),"target":last}),flush=True)
    scanned = sum(counts.values())
    report = {
        "status":"MODULAR_RANK_EXTENSION_DIAGNOSTIC_NOT_PROOF",
        "point":list(point),"missing_lead":list(MISSING),
        "checkpoint_sha256":sha(args.checkpoint),"source_sha256":sha(args.input),
        "certificate_sha256":sha(args.certificate),
        "original_basis_rank":389,"outside_rows_total":1852,
        "outside_rows_requested":len(candidates),"outside_rows_scanned":scanned,
        "outside_rows_skipped":len(candidates)-scanned,
        "status_counts":dict(counts),"new_pivots":len(additions),
        "first_added_rows":additions[:args.max_records],
        "target_change_count":len(changes),
        "first_target_changes":changes[:args.max_records],
        "capped_count":len(capped),"first_capped_rows":capped[:args.max_records],
        "stopped_at_zero":stopped_zero,"stopped_at_new_pivot_cap":stopped_rank_cap,
        "exhaustive":scanned == 1852 and not capped and not stopped_rank_cap,
        "target_after_scan":last,
        "exact_target_proven":False,"checkpoint_modified":False,"kira_executed":False,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as stream:
        json.dump(report,stream,indent=2,ensure_ascii=True)
        stream.write("\n")
    print("VP05_SECTOR202_RANK_EXTENSION_RESULT "+json.dumps({
        "status":report["status"],"scanned":scanned,"new_pivots":len(additions),
        "capped":len(capped),"target":last,"output":str(args.output),
        "checkpoint_modified":False}),flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint",type=Path,default=CHECKPOINT)
    ap.add_argument("--input",type=Path,default=SOURCE)
    ap.add_argument("--certificate",type=Path,default=CERT)
    ap.add_argument("--output",type=Path,default=BASE/"vp05_sector202_A_rank_extension_p0.json")
    ap.add_argument("--point-index",type=int,choices=(0,1,2),default=0)
    ap.add_argument("--max-candidates",type=int,default=1852)
    ap.add_argument("--max-steps",type=int,default=512)
    ap.add_argument("--max-columns",type=int,default=512)
    ap.add_argument("--max-new-pivots",type=int,default=256)
    ap.add_argument("--max-records",type=int,default=40)
    ap.add_argument("--progress-every",type=int,default=50)
    ap.add_argument("--stop-at-zero",action="store_true")
    args = ap.parse_args()
    if not 1 <= args.max_candidates <= 1852:
        ap.error("--max-candidates must be 1..1852")
    if min(args.max_steps,args.max_columns,args.max_new_pivots,args.max_records,args.progress_every) < 1:
        ap.error("Safety caps must be positive")
    run(args)

if __name__ == "__main__":
    main()
