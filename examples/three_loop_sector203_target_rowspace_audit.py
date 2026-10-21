"""Finite-field target row-space membership for saved VP05 witness equations.

No Kira or Fermat execution, no symbolic proof. Integral aliases must be
verified against the actual witness column encoding before conclusions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

from examples.three_loop_sector203_fermat_probe import FOLDER
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows, order

POINTS = ((1000037, 21, 15), (1000081, 25, 23), (1000117, 29, 31))
DEFAULT_TERMS = ((10, 203, "z"), (6, 203, "-2"), (5, 201, "2"))


def residue(expr, p, z, d):
    if expr == "z":
        return z % p
    if expr == "-2":
        return (-2) % p
    if expr == "2":
        return 2 % p
    raise ValueError("Only audited target coefficients z,-2,2 are supported")


def eliminate(rows, target, p):
    """Finite-field row-space test with original-IBP provenance certificate.

    Provenance tracks a linear combination of original equation indices.
    Every sampled certificate is independently checked against raw rows.
    """
    basis = {}
    combinations = {}
    owner_ids = {}
    target_appearing_rows = set()
    target_keys = set(target)
    for i, original in enumerate(rows):
        if target_keys.intersection(original):
            target_appearing_rows.add(i)
        vec = original.copy()
        combo = {i: 1}
        while vec:
            lead = min(vec, key=order)
            if lead not in basis:
                inv = pow(vec[lead], -1, p)
                basis[lead] = {k: v * inv % p for k, v in vec.items()}
                combinations[lead] = {j: val * inv % p for j, val in combo.items() if val % p}
                owner_ids[lead] = i
                break
            fac = vec[lead]
            for k, value in basis[lead].items():
                val = (vec.get(k, 0) - fac * value) % p
                if val: vec[k] = val
                else: vec.pop(k, None)
            for j, value in combinations[lead].items():
                val = (combo.get(j, 0) - fac * value) % p
                if val: combo[j] = val
                else: combo.pop(j, None)
    original_target = target.copy()
    target_ops = []
    certificate = {}
    while target:
        lead = min(target, key=order)
        if lead not in basis:
            break
        fac = target[lead]
        target_ops.append({"owner": owner_ids[lead], "pivot": list(lead)})
        for k, value in basis[lead].items():
            val = (target.get(k, 0) - fac * value) % p
            if val: target[k] = val
            else: target.pop(k, None)
        for j, value in combinations[lead].items():
            val = (certificate.get(j, 0) + fac * value) % p
            if val: certificate[j] = val
            else: certificate.pop(j, None)
    reconstruction = {}
    for j, factor in certificate.items():
        for k, value in rows[j].items():
            val = (reconstruction.get(k, 0) + factor * value) % p
            if val: reconstruction[k] = val
            else: reconstruction.pop(k, None)
    verified = not target and reconstruction == original_target
    return {"rank": len(basis), "target_in_rowspace": not target,
            "target_remainder_size": len(target),
            "target_remainder_sample": [
                {"key": list(k), "coefficient": target[k]}
                for k in sorted(target, key=order)[:8]],
            "target_elimination_steps": len(target_ops),
            "target_elimination_first_owners": target_ops[:12],
            "direct_target_support_rows": len(target_appearing_rows),
            "direct_target_support_row_ids": sorted(target_appearing_rows)[:40],
            "certificate_support_count": len(certificate),
            "certificate_coefficients": certificate,
            "certificate_row_ids": sorted(certificate),
            "certificate_original_equation_replay_verified": verified,
            "certificate_nonzero_coefficients_sample": [
                {"row": j, "coefficient": certificate[j]}
                for j in sorted(certificate)[:12]],
            "full_target": [{"key": list(k), "coefficient": v}
                            for k, v in original_target.items()]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--equations", type=Path)
    ap.add_argument("--rows", type=int, default=528)
    ap.add_argument("--export-certificate", type=Path,
                    help="Write all sampled modular coefficient vectors and replay status to JSON")
    ap.add_argument("--append-certificate", action="store_true",
                    help="Append verified new samples to existing export, never overwrite incompatible source")
    ap.add_argument("--extra-points", type=int, default=0,
                    help="Number of additional deterministic modular points beyond original three (max 24)")
    ap.add_argument("--holdout-points", type=int, default=0,
                    help="Number of extra points reserved for independent validation (max 12)")
    ap.add_argument("--target-term", action="append", nargs=3,
                    metavar=("KEY", "SECTOR", "COEFFICIENT"),
                    help="Override default keys for I10,I6,I5; repeated triple")
    a = ap.parse_args()
    if not 0 <= a.extra_points <= 24 or not 0 <= a.holdout_points <= 12:
        ap.error("extra-points must be 0..24 and holdout-points 0..12")
    if a.append_certificate and not a.export_certificate:
        ap.error("--append-certificate requires --export-certificate")
    if not 1 <= a.rows <= 528:
        ap.error("rows must be 1..528")
    files = [a.equations.resolve()] if a.equations else sorted(
        FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
    if not files:
        ap.error("Witness equations JSON not found")
    path = files[-1]
    rows = json.loads(path.read_text(encoding="utf-8-sig"))["rows"][:a.rows]
    columns = {tuple(t["key"]) for row in rows for t in row["terms"]}
    terms = [(int(k), int(sec), value) for k, sec, value in a.target_term] if a.target_term else DEFAULT_TERMS
    keys = {(k, sector) for k, sector, _ in terms}
    if len(keys) != len(terms):
        ap.error("Target keys must be distinct")
    absent = sorted(keys - columns)
    print("TARGET_ROWSPACE_INPUT " + json.dumps({
        "rows": len(rows), "columns": len(columns),
        "keys": [{"key": [k, sec], "coefficient": v,
                  "present_in_witness_columns": (k, sec) in columns}
                 for k, sec, v in terms],
        "source": str(path),
        "alias_mapping_verified": False,
        "proof": False}), flush=True)
    if absent:
        print("TARGET_ROWSPACE_BLOCKED " + json.dumps({
            "reason": "target aliases absent from this equation encoding",
            "missing_keys": [list(k) for k in absent],
            "next": "Resolve key mapping against witness metadata; do not interpret missing keys as independent integrals",
            "proof": False}), flush=True)
        return
    # Prime selections are deterministic; reserve later points as holdouts.
    # Each point has a distinct modulus and avoids zero z,d.
    extra_primes = (1000039, 1000087, 1000099, 1000117, 1000121, 1000133,
        1000151, 1000159, 1000171, 1000183, 1000193, 1000199,
        1000211, 1000213, 1000231, 1000249, 1000253, 1000273,
        1000289, 1000291, 1000303, 1000313, 1000333, 1000357,
        1000367, 1000381, 1000393, 1000397, 1000403, 1000423,
        1000427, 1000429, 1000453, 1000457, 1000507, 1000537)
    import sympy as sp
    selected_primes = [p for p in extra_primes if sp.isprime(p) and p not in {x[0] for x in POINTS}]
    required = a.extra_points + a.holdout_points
    if required > len(selected_primes):
        ap.error("Not enough distinct confirmed primes in configured grid")
    grid = [(p, 31 + 2*i, 37 + 4*i) for i, p in enumerate(selected_primes[:required])]
    point_roles = [(pt, "training") for pt in POINTS]
    point_roles += [(pt, "training") for pt in grid[:a.extra_points]]
    point_roles += [(pt, "holdout") for pt in grid[a.extra_points:]]
    exported = []
    for (p, z, d), role in point_roles:
        try:
            matrix = mod_rows(rows, p, z, d)
            target = {(k, sec): residue(v, p, z, d) for k, sec, v in terms}
            target = {k: v for k, v in target.items() if v}
            result = eliminate(matrix, target, p)
        except (ZeroDivisionError, ValueError) as exc:
            print("TARGET_ROWSPACE_POINT_ERROR " + json.dumps({
                "point": [p, z, d], "error": str(exc)}), flush=True)
            continue
        coeffs = result.pop("certificate_coefficients")
        exported.append({"point": [p, z, d], "role": role,
                         "coefficients_by_original_row": [coeffs.get(j, 0) for j in range(len(rows))],
                         "replay_verified": result["certificate_original_equation_replay_verified"]})
        result.update({"point": [p, z, d], "proof": False})
        print("TARGET_ROWSPACE_POINT " + json.dumps(result), flush=True)
    if a.export_certificate:
        if len(exported) != len(point_roles) or not all(x["replay_verified"] for x in exported):
            raise SystemExit("Certificate export blocked: not all points replay-verified")
        out = a.export_certificate.resolve()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest = {"type": "modular_target_certificate_samples",
            "source": str(path), "source_sha256": digest, "rows": len(rows),
            "target": [{"key": [k, sec], "coefficient": v} for k, sec, v in terms],
            "alias_mapping_verified": False, "proof": False, "samples": []}
        existing_count = 0
        if a.append_certificate and out.exists():
            old = json.loads(out.read_text(encoding="utf-8-sig"))
            # Earlier exports lacked an equation digest: refuse mixing without
            # first verifying source and original three saved point vectors.
            for field in ("type", "rows", "target"):
                if old.get(field) != manifest[field]:
                    raise SystemExit("Append blocked: mismatched "+field)
            if old.get("source_sha256") not in (None, digest):
                raise SystemExit("Append blocked: source SHA256 mismatch")
            if old.get("source_sha256") is None:
                if Path(old.get("source", "")).resolve() != path:
                    raise SystemExit("Append blocked: legacy source path differs")
            old_samples = old.get("samples", [])
            if not isinstance(old_samples, list):
                raise SystemExit("Append blocked: invalid prior samples")
            fresh = {tuple(x["point"]): x for x in exported}
            seen = set()
            for old_sample in old_samples:
                key = tuple(old_sample["point"])
                if key in seen or not old_sample.get("replay_verified"):
                    raise SystemExit("Append blocked: repeated or unverified prior point")
                seen.add(key)
                if key in fresh:
                    if old_sample["coefficients_by_original_row"] != fresh[key]["coefficients_by_original_row"]:
                        raise SystemExit("Append blocked: saved coefficient vector differs from recomputation")
                    if old_sample.get("role", "training") != fresh[key]["role"]:
                        raise SystemExit("Append blocked: saved role differs")
                if len(old_sample["coefficients_by_original_row"]) != len(rows):
                    raise SystemExit("Append blocked: incorrect saved vector length")
            manifest["samples"] = old_samples[:]
            existing_count = len(old_samples)
        occupied = {tuple(x["point"]) for x in manifest["samples"]}
        manifest["samples"].extend(x for x in exported if tuple(x["point"]) not in occupied)
        if len({tuple(x["point"]) for x in manifest["samples"]}) != len(manifest["samples"]):
            raise SystemExit("Append blocked: duplicate points")
        out.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replacement prevents a failed write corrupting prior samples.
        fd, temporary = tempfile.mkstemp(prefix=out.name+".", suffix=".tmp", dir=str(out.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(manifest, handle, indent=2)
                handle.write("\n")
            os.replace(temporary, out)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        print("TARGET_ROWSPACE_CERTIFICATE_EXPORTED " + json.dumps({
            "file": str(out), "samples": len(manifest["samples"]),
            "prior_samples": existing_count, "new_samples": len(manifest["samples"])-existing_count,
            "training_samples": sum(x.get("role", "training") == "training" for x in manifest["samples"]),
            "holdout_samples": sum(x.get("role") == "holdout" for x in manifest["samples"]),
            "coefficients_per_sample": len(rows), "proof": False}), flush=True)


if __name__ == "__main__":
    main()
