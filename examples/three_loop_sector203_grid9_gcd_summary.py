"""Summarize the five grid9 kernel basis GCDs without inventing canonicality.

Reads the existing 80-point audit JSON; no modular sample recomputation.
An individual basis vector's gcd does not determine the rational function.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from collections import Counter

ROOT=Path("output/three_loop_integral_family_audit")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=ROOT/"vp05_grid9_kernel_factor_audit.json")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_grid9_gcd_summary.json")
    a=ap.parse_args()
    raw=a.input.read_bytes()
    data=json.loads(raw.decode("utf-8-sig"))
    expected={21,32,44,110,113}
    rows=data["rows"]
    if len(rows)!=5 or {r["row"] for r in rows}!=expected:
        ap.error("Unexpected five-row factor audit")
    if data["summary"]["outcomes"].get("all_holdouts_function_fixed")!=5:
        ap.error("Holdout functional test not complete")
    output=[]
    total=Counter()
    for row in sorted(rows,key=lambda x:x["row"]):
        basis=row["basis_polynomial_gcd_diagnostics"]
        if len(basis)!=row["kernel_nullity"]:ap.error("Basis count mismatch")
        hist=Counter(str(x.get("common_factor_total_degree")) for x in basis)
        for k,v in hist.items():total[k]+=v
        output.append({"row":row["row"],"kernel_nullity":row["kernel_nullity"],
          "basis_gcd_degree_histogram":dict(hist),
          "reduced_degree_pairs":[[v.get("reduced_numerator_degree"),v.get("reduced_denominator_degree")]
             for v in basis if not v.get("zero_denominator")],
          "holdouts_function_fixed":row["function_fixed_at_all_holdouts"]})
    report={"summary":{"rows":5,"basis_vectors":sum(x["kernel_nullity"] for x in output),
       "basis_gcd_degree_histogram":dict(total),
       "source_sha256":hashlib.sha256(raw).hexdigest(),
       "canonical_rational_function_reconstructed":False,
       "rational_lift":False,"symbolic_proof":False},
       "rows":output}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_GRID9_GCD_SUMMARY "+json.dumps({**report["summary"],"per_row":[{"row":r["row"],"gcd_degrees":r["basis_gcd_degree_histogram"],"reduced_pairs":r["reduced_degree_pairs"]} for r in output],"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
