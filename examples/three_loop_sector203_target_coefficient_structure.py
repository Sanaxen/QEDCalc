"""Analyze modular target certificate coefficient equivalence / signed / rational ratios.

Finite-field hypothesis discovery only. A holdout point is a consistency test,
not an exact identity proof. No Kira or Fermat execution.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

DEFAULT = Path("output/three_loop_integral_family_audit/vp05_target_certificate_samples.json")


def ratio_signature(a, b, samples):
    residues = []
    for s in samples:
        p = s["point"][0]
        va, vb = s["coefficients_by_original_row"][a] % p, s["coefficients_by_original_row"][b] % p
        if vb == 0:
            return None
        residues.append(va * pow(vb, -1, p) % p)
    return residues


def scalar_candidates(samples, bound):
    # Test small signed integer ratios a/b, with gcd=1.
    result = {}
    for den in range(1, bound + 1):
        for num in range(-bound, bound + 1):
            if num == 0:
                continue
            frac = Fraction(num, den)
            if frac in result:
                continue
            vals = []
            valid = True
            for s in samples:
                p = s["point"][0]
                if frac.denominator % p == 0:
                    valid = False
                    break
                vals.append(frac.numerator * pow(frac.denominator, -1, p) % p)
            if valid:
                result[frac] = tuple(vals)
    return result


def classify(data, bound):
    samples = data["samples"]
    training = [s for s in samples if s.get("role", "training") == "training"]
    holdout = [s for s in samples if s.get("role", "training") == "holdout"]
    if len(training) < 2:
        raise ValueError("At least two training samples required")
    n = data["rows"]
    if any(len(s["coefficients_by_original_row"]) != n or not s.get("replay_verified") for s in samples):
        raise ValueError("Invalid or unverified samples")
    if len({tuple(s["point"]) for s in samples}) != len(samples):
        raise ValueError("Duplicate sample points")
    # Normalize each coordinate as tuple of residues across distinct fields.
    signatures = [tuple(s["coefficients_by_original_row"][i] % s["point"][0] for s in training)
                  for i in range(n)]
    groups = defaultdict(list)
    for i, sig in enumerate(signatures):
        groups[sig].append(i)
    equals = [v for v in groups.values() if len(v) > 1]
    scalar = scalar_candidates(training, bound)
    signature_ratios = {v: k for k, v in scalar.items()}
    by_signature = defaultdict(list)
    for i, sig in enumerate(signatures):
        by_signature[sig].append(i)
    relations = []
    candidates_checked = 0
    for a in range(n):
        for b in range(a + 1, n):
            if signatures[a] == signatures[b]:
                continue
            rs = ratio_signature(a, b, training)
            if rs is None:
                continue
            ratio = signature_ratios.get(tuple(rs))
            if ratio is None:
                continue
            candidates_checked += 1
            ok = all(
                (s["coefficients_by_original_row"][a] * ratio.denominator
                 - s["coefficients_by_original_row"][b] * ratio.numerator) % s["point"][0] == 0
                for s in holdout
            )
            relations.append({"a": a, "b": b, "ratio": str(ratio),
                              "holdout_pass": ok})
    equals_info = []
    for ids in sorted(equals, key=lambda v: (-len(v), v[0])):
        rep = ids[0]
        ok = all(all(
            s["coefficients_by_original_row"][i] % s["point"][0] ==
            s["coefficients_by_original_row"][rep] % s["point"][0]
            for i in ids[1:]) for s in holdout)
        equals_info.append({"rows": ids, "size": len(ids), "holdout_pass": ok})
    # Build ratio-consistent connected components using only relationships
    # confirmed by all holdouts; weighted disjoint set enforces consistency.
    parent = list(range(n))
    weight = [Fraction(1) for _ in range(n)]  # value(node)/value(parent)
    def find(x):
        if parent[x] != x:
            root, factor = find(parent[x])
            weight[x] *= factor
            parent[x] = root
        return parent[x], weight[x]
    def union(a, b, ratio):
        ra, wa = find(a)
        rb, wb = find(b)
        if ra == rb:
            return wa == ratio * wb
        parent[ra] = rb
        weight[ra] = ratio * wb / wa
        return True
    inconsistencies = 0
    for group in equals_info:
        if not group["holdout_pass"]:
            continue
        for idx in group["rows"][1:]:
            if not union(idx, group["rows"][0], Fraction(1)):
                inconsistencies += 1
    for relation in relations:
        if relation["holdout_pass"]:
            if not union(relation["a"], relation["b"], Fraction(relation["ratio"])):
                inconsistencies += 1
    components = defaultdict(list)
    for i in range(n):
        root, _ = find(i)
        components[root].append(i)
    classes = []
    for members in components.values():
        representative = min(members)
        _, repr_weight = find(representative)
        classes.append({"representative": representative, "size": len(members),
            "rows": members,
            "ratios_to_representative": [
                {"row": i, "ratio": str(find(i)[1] / repr_weight)}
                for i in members]})
    classes.sort(key=lambda x: (-x["size"], x["representative"]))
    return {"type": "modular_coefficient_structure_audit",
            "rows": n, "training_points": len(training),
            "holdout_points": len(holdout),
            "equal_group_count": len(equals_info),
            "equal_rows_total": sum(x["size"] for x in equals_info),
            "distinct_training_signatures": len(groups),
            "equal_groups": equals_info,
            "small_rational_ratio_pair_count": len(relations),
            "small_rational_ratio_pairs": relations,
            "ratio_bound": bound,
            "proportional_class_count": len(classes),
            "proportional_class_largest": max(len(c["rows"]) for c in classes),
            "proportional_class_inconsistencies": inconsistencies,
            "proportional_classes": classes,
            "proof": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certificate", type=Path, default=DEFAULT)
    ap.add_argument("--ratio-bound", type=int, default=4)
    ap.add_argument("--output", type=Path)
    a = ap.parse_args()
    if not 1 <= a.ratio_bound <= 12:
        ap.error("ratio-bound must be 1..12")
    data = json.loads(a.certificate.read_text(encoding="utf-8-sig"))
    if data.get("type") != "modular_target_certificate_samples":
        ap.error("Not a target certificate file")
    result = classify(data, a.ratio_bound)
    print("TARGET_COEFF_STRUCTURE " + json.dumps({k:v for k,v in result.items()
          if k not in ("equal_groups","small_rational_ratio_pairs","proportional_classes")}), flush=True)
    print("TARGET_COEFF_EQUAL_GROUPS_TOP " + json.dumps(result["equal_groups"][:12]), flush=True)
    print("TARGET_COEFF_RATIO_PAIRS_TOP " + json.dumps(result["small_rational_ratio_pairs"][:12]), flush=True)
    print("TARGET_COEFF_PROPORTIONAL_CLASSES_TOP " + json.dumps(result["proportional_classes"][:8]), flush=True)
    print("TARGET_COEFF_HOLDOUT " + json.dumps({
        "equal_failed": sum(not x["holdout_pass"] for x in result["equal_groups"]),
        "ratio_failed": sum(not x["holdout_pass"] for x in result["small_rational_ratio_pairs"]),
        "proof": False}), flush=True)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
        print("TARGET_COEFF_STRUCTURE_EXPORTED " + json.dumps({"file":str(a.output)}), flush=True)


if __name__ == "__main__":
    main()
