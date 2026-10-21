"""VP05 certificate rational-function sampling design, without claiming proof.

Read six saved modular certificates; count degrees of freedom for bivariate
numerator/denominator ansatz. Never interpolate unrelated prime fields as if
they were the same field. Use dimensional lower bounds to reject inadequate
sample sets and propose prime-fixed sampling grids.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

DEFAULT=Path("output/three_loop_integral_family_audit/vp05_compressed_certificate_samples.json")
OUTPUT=Path("output/three_loop_integral_family_audit/vp05_certificate_reconstruction_design.json")

def monomials(total_degree):
    return (total_degree+1)*(total_degree+2)//2

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=OUTPUT)
    ap.add_argument("--max-total-degree",type=int,default=6)
    ap.add_argument("--verification-points",type=int,default=8)
    a=ap.parse_args()
    if not 0<=a.max_total_degree<=20 or a.verification_points<1:
        ap.error("Invalid degree or verification count")
    data=json.loads(a.samples.read_text(encoding="utf-8-sig"))
    if data.get("type")!="compressed_modular_certificate_samples" or data.get("rows")!=166:
        ap.error("Expected 166-component compressed modular certificate samples")
    points=data.get("samples",[])
    seen=set()
    for item in points:
        point=tuple(item["point"])
        if point in seen or len(item["coefficients_by_compressed_row"])!=166 or not item.get("replay_verified"):
            ap.error("Duplicate point or invalid/unverified certificate")
        seen.add(point)
    by_prime={}
    for item in points:
        by_prime.setdefault(item["point"][0],[]).append(item)
    training=[x for x in points if x["role"]=="training"]
    holdout=[x for x in points if x["role"]=="holdout"]
    models=[]
    for n in range(a.max_total_degree+1):
        for d in range(a.max_total_degree+1):
            # Scalar normalization leaves one projective degree of freedom.
            unknowns=monomials(n)+monomials(d)-1
            # Numerator and denominator may be simultaneously zero at a
            # singular evaluation; regularity must be verified per sample.
            min_training=unknowns
            desired=min_training+a.verification_points
            models.append({"numerator_total_degree":n,"denominator_total_degree":d,
                           "unknown_projective_coefficients":unknowns,
                           "minimum_generic_same_prime_training_points":min_training,
                           "suggested_same_prime_points_including_holdouts":desired,
                           "current_distinct_prime_training_usable_together":max(
                               (sum(x["role"]=="training" for x in group) for group in by_prime.values()),default=0),
                           "ready_for_identification":False})
    summary={"type":"vp05_certificate_reconstruction_design","source_sha256":data.get("source_sha256"),
             "saved_points":len(points),"training_points":len(training),"holdout_points":len(holdout),
             "distinct_primes":len(by_prime),
             "max_training_points_at_one_prime":max((sum(x["role"]=="training" for x in group) for group in by_prime.values()),default=0),
             "all_166_coefficients_present":True,
             "cross_prime_direct_interpolation_allowed":False,
             "reason":"Finite-field residues at distinct primes cannot be treated as values over one common field; reconstruct using same-prime z,d grids followed by CRT/rational lifting, with new holdouts.",
             "models":models,"symbolic_proof":False,"fermat_executed":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print("VP05_RECON_DESIGN_SUMMARY "+json.dumps({k:v for k,v in summary.items() if k!="models"} | {"models_count":len(models),"output":str(a.output)}),flush=True)
    for n,d in ((0,0),(1,1),(2,2),(3,3),(4,4),(6,6)):
        if n<=a.max_total_degree:
            match=next(m for m in models if m["numerator_total_degree"]==n and m["denominator_total_degree"]==d)
            print("VP05_RECON_DEGREE "+json.dumps(match),flush=True)

if __name__=="__main__":main()
