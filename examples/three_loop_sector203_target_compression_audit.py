"""Audit compression H_g = sum_i r_i E_i under sampled coefficient ratios.

H_g combines exact original equation expressions using exact rational constants,
but target membership and class proportionality are verified ONLY at finite-field
samples. This does not establish the claimed Q(z,d) identity.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from examples.three_loop_sector203_fermat_probe import FOLDER
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_target_rowspace_audit import residue

DEFAULT_CERT = Path("output/three_loop_integral_family_audit/vp05_target_certificate_samples.json")
DEFAULT_GROUPS = Path("output/three_loop_integral_family_audit/vp05_target_coefficient_structure.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certificate", type=Path, default=DEFAULT_CERT)
    ap.add_argument("--groups", type=Path, default=DEFAULT_GROUPS)
    ap.add_argument("--equations", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    cert = json.loads(args.certificate.read_text(encoding="utf-8-sig"))
    grouping = json.loads(args.groups.read_text(encoding="utf-8-sig"))
    files = [args.equations.resolve()] if args.equations else sorted(FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
    if not files:
        ap.error("Source equations unavailable")
    path = files[-1]
    original = json.loads(path.read_text(encoding="utf-8-sig"))["rows"][:cert["rows"]]
    classes = grouping["proportional_classes"]
    if not classes or cert["rows"] != grouping["rows"] or len(original) != cert["rows"]:
        ap.error("Mismatched group or equation lengths")
    seen = set()
    for group in classes:
        if group["representative"] not in group["rows"]:
            ap.error("Invalid representative")
        ratios = {x["row"]: Fraction(x["ratio"]) for x in group["ratios_to_representative"]}
        if set(group["rows"]) != set(ratios) or ratios[group["representative"]] != 1:
            ap.error("Invalid group ratios")
        if seen.intersection(ratios):
            ap.error("Overlapping groups")
        seen.update(ratios)
    if seen != set(range(cert["rows"])):
        ap.error("Incomplete partition")
    target_terms = cert["target"]
    compressed_sizes = []
    outcomes = []
    for sample in cert["samples"]:
        p, z, d = sample["point"]
        raw = mod_rows(original, p, z, d)
        vector = sample["coefficients_by_original_row"]
        target = {(int(t["key"][0]),int(t["key"][1])): residue(t["coefficient"],p,z,d)
                  for t in target_terms}
        target = {k:v for k,v in target.items() if v}
        combined = defaultdict(int)
        row_sizes = []
        ratios_valid = True
        for gi, group in enumerate(classes):
            rep = group["representative"]
            rep_coeff = vector[rep] % p
            compressed = defaultdict(int)
            for entry in group["ratios_to_representative"]:
                i = entry["row"]
                q = Fraction(entry["ratio"])
                if q.denominator % p == 0:
                    ap.error("Ratio denominator divisible by sample prime")
                scalar = q.numerator * pow(q.denominator,-1,p) % p
                if vector[i] % p != rep_coeff * scalar % p:
                    ratios_valid = False
                for key, value in raw[i].items():
                    compressed[key] = (compressed[key] + scalar * value) % p
            compressed = {k:v for k,v in compressed.items() if v}
            row_sizes.append(len(compressed))
            for key,value in compressed.items():
                combined[key] = (combined[key] + rep_coeff * value) % p
        combined = {k:v for k,v in combined.items() if v}
        outcomes.append({"point":sample["point"],"role":sample.get("role","training"),
                         "ratios_valid":ratios_valid,
                         "reconstructed":combined == target,
                         "compressed_nonzero_terms":sum(row_sizes),
                         "compressed_nonempty_rows":sum(bool(x) for x in row_sizes),
                         "max_compressed_row_terms":max(row_sizes)})
    print("TARGET_COMPRESSED_AUDIT " + json.dumps({
        "original_rows":len(original),"compressed_rows":len(classes),
        "original_terms":sum(len(r["terms"]) for r in original),
        "points":len(outcomes),"all_ratios_valid":all(x["ratios_valid"] for x in outcomes),
        "all_reconstructed":all(x["reconstructed"] for x in outcomes),
        "samples":outcomes, "proof":False}),flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps({"type":"sampled_compression_audit",
            "source":str(path),"groups":str(args.groups),"results":outcomes,
            "compressed_rows":len(classes),"proof":False},indent=2)+"\n",encoding="utf-8")
        print("TARGET_COMPRESSED_AUDIT_EXPORTED " + json.dumps({"file":str(args.output)}),flush=True)


if __name__ == "__main__":
    main()
