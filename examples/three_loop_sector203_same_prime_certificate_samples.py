"""Collect same-prime VP05 certificate samples with a separate holdout set.

No Fermat/Kira; this does not reconstruct or prove rational functions.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_dual_certificate_preflight import dual_certificate
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT
from examples.three_loop_sector203_target_rowspace_audit import residue

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--prime",type=int,default=1000037)
    ap.add_argument("--training",type=int,default=19)
    ap.add_argument("--holdouts",type=int,default=8)
    ap.add_argument("--max-attempts",type=int,default=120)
    ap.add_argument("--grid-v2",action="store_true",help="Use independent 5-column x 2D grid; choose a new output path")
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_same_prime_certificate_samples.json"))
    a=ap.parse_args()
    if a.training<1 or a.holdouts<1 or a.training+a.holdouts>120 or a.max_attempts<a.training+a.holdouts:
        ap.error("Invalid bounded sampling parameters")
    if not sp.isprime(a.prime) or a.prime<=1000:
        ap.error("prime must be a prime greater than 1000")
    raw=a.equations.read_bytes()
    data=json.loads(raw.decode("utf-8-sig"))
    if data.get("type")!="symbolic_exact_linear_combinations" or len(data.get("rows",[]))!=166:
        ap.error("Expected exactly 166 compressed symbolic equations")
    if a.grid_v2 and a.output.name=="vp05_same_prime_certificate_samples.json":
        ap.error("--grid-v2 requires a separate --output to preserve old sample archive")
    rows=data["rows"]
    samples=[]
    rejected=[]
    for i in range(a.max_attempts):
        if len(samples)>=a.training+a.holdouts:break
        # Distinct, non-collinear grid points for generic two-variable interpolation.
        if a.grid_v2:
            z=(17+37*(i%5))%a.prime
            d=(29+61*(i//5))%a.prime
        else:
            z=(17+37*i+11*i*i)%a.prime
            d=(29+61*i+7*i*i*i)%a.prime
        if not z or not d:continue
        try:
            evaluated=mod_rows(rows,a.prime,z,d)
            target={k:residue(v,a.prime,z,d) for k,v in TARGET.items()}
            result=dual_certificate(evaluated,target,a.prime)
        except (ValueError,ZeroDivisionError) as e:
            rejected.append({"point":[a.prime,z,d],"error":str(e)[:160]})
            continue
        if result["rank"]!=166 or not result["replay_verified"]:
            rejected.append({"point":[a.prime,z,d],"reason":"singular_or_replay_failure"})
            continue
        role="training" if len(samples)<a.training else "holdout"
        s={"point":[a.prime,z,d],"role":role,
           "coefficients_by_compressed_row":[result["certificate"].get(j,0) for j in range(166)],
           "rank":166,"replay_verified":True}
        samples.append(s)
        if len(samples)%5==0 or len(samples)==a.training+a.holdouts:
            print("VP05_SAME_PRIME_PROGRESS "+json.dumps({"valid":len(samples),
                "requested":a.training+a.holdouts,"rejected":len(rejected),"last_role":role}),flush=True)
    if len(samples)!=a.training+a.holdouts:
        raise RuntimeError("Insufficient nonsingular points; no partial archive written")
    report={"type":"same_prime_modular_certificate_samples","source":str(a.equations),
        "source_sha256":hashlib.sha256(raw).hexdigest(),"prime":a.prime,
        "rows":166,"training":a.training,"holdouts":a.holdouts,
        "sampling_strategy":"grid_v2_5_columns" if a.grid_v2 else "legacy_curve",
        "samples":samples,"rejected_points":rejected,
        "symbolic_reconstruction":False,"proof":False,"fermat_executed":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=a.output.name+".",suffix=".tmp",dir=str(a.output.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(report,f,indent=2)
            f.write("\n")
        os.replace(tmp,a.output)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print("VP05_SAME_PRIME_SUMMARY "+json.dumps({"prime":a.prime,
        "training":a.training,"holdouts":a.holdouts,"rejected":len(rejected),
        "output":str(a.output),"source_sha256":report["source_sha256"],
        "proof":False,"fermat_executed":False}),flush=True)
if __name__=="__main__":main()
