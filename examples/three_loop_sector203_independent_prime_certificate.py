"""Independent-prime VP05 modular coefficient reconstruction.

Use original p=1000037 assembled model *degree bounds only*, NOT residues.
Collect modular IBP certificates at a different prime, refit all 166 models,
validate fresh holdouts, and compare degree requirements.
No Fermat/Kira, no characteristic-zero proof.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
import sympy as sp
from collections import Counter
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_dual_certificate_preflight import dual_certificate
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT
from examples.three_loop_sector203_target_rowspace_audit import residue
from examples.three_loop_sector203_certificate_adaptive_degree import fit

ROOT=Path("output/three_loop_integral_family_audit")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--models",type=Path,default=ROOT/"vp05_modular_certificate_assembled.json")
    ap.add_argument("--prime",type=int,default=1001003)
    ap.add_argument("--training",type=int,default=70)
    ap.add_argument("--holdouts",type=int,default=10)
    ap.add_argument("--max-attempts",type=int,default=130)
    ap.add_argument("--columns",type=int,default=13,help="Grid width; >=7 distinct d-levels required for degree six")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_independent_prime_certificate.json")
    a=ap.parse_args()
    if not sp.isprime(a.prime) or a.prime<=1000 or a.prime==1000037:ap.error("Choose an independent prime >1000")
    if not 65<=a.training<=90 or not 8<=a.holdouts<=20 or a.max_attempts<a.training+a.holdouts or not 7<=a.columns<=20:
        ap.error("Invalid bounded sampling counts")
    raw=a.equations.read_bytes()
    eq=json.loads(raw.decode("utf-8-sig"))
    master=json.loads(a.models.read_text(encoding="utf-8-sig"))
    if eq.get("type")!="symbolic_exact_linear_combinations" or len(eq.get("rows",[]))!=166:
        ap.error("Unexpected compressed IBP equation file")
    summary=master["summary"]
    if summary["equations_sha256"]!=hashlib.sha256(raw).hexdigest() or summary["rows"]!=166 or not summary["complete_sample_replay_passed"]:
        ap.error("Assembled-model provenance mismatch")
    model_rows=master["coefficients"]
    if len(model_rows)!=166 or {e["row"] for e in model_rows}!=set(range(166)):
        ap.error("Incomplete or duplicate coefficient models")
    if (a.training-1)//a.columns+1<7:
        ap.error("Training grid requires at least 7 distinct d levels for degree-6 fits")
    p=a.prime;samples=[];rejected=[]
    # 13-column shifted lattice distinct from all training grids at p0.
    for i in range(a.max_attempts):
        if len(samples)==a.training+a.holdouts:break
        z=(47+53*(i%a.columns))%p
        d=(83+79*(i//a.columns))%p
        if not z or not d:continue
        try:
            evaluated=mod_rows(eq["rows"],p,z,d)
            target={k:residue(v,p,z,d) for k,v in TARGET.items()}
            cert=dual_certificate(evaluated,target,p)
        except (ZeroDivisionError,ValueError) as e:
            rejected.append({"point":[p,z,d],"error":str(e)[:120]});continue
        if cert["rank"]!=166 or not cert["replay_verified"]:
            rejected.append({"point":[p,z,d],"reason":"rank_or_replay_failure"});continue
        role="training" if len(samples)<a.training else "holdout"
        samples.append({"point":[p,z,d],"role":role,
            "coefficients_by_compressed_row":[cert["certificate"].get(j,0) for j in range(166)],
            "rank":166,"replay_verified":True})
        if len(samples)%10==0 or len(samples)==a.training+a.holdouts:
            print("VP05_INDEPENDENT_PRIME_PROGRESS "+json.dumps({"valid":len(samples),
                "requested":a.training+a.holdouts,"rejected":len(rejected)}),flush=True)
    if len(samples)!=a.training+a.holdouts:
        raise RuntimeError("Insufficient valid independent-prime samples; no result written")
    train=[s for s in samples if s["role"]=="training"]
    hold=[s for s in samples if s["role"]=="holdout"]
    hist=Counter();fits=[]
    for e in sorted(model_rows,key=lambda x:x["row"]):
        model=e["model"];row=e["row"]
        result=fit(train,hold,p,row,model["numerator_degree"],model["denominator_degree"])
        hist[result["status"]]+=1
        fits.append({"row":row,"original_degree":[model["numerator_degree"],model["denominator_degree"]],
            "origin":e["origin"],"result":result})
    report={"summary":{"prime":p,"training":len(train),"holdouts":len(hold),
            "rejected":len(rejected),"rows":166,"columns":a.columns,"outcome_counts":dict(hist),
            "independent_prime_pass":hist["holdout_pass"],"original_prime":summary["prime"],
            "equations_sha256":hashlib.sha256(raw).hexdigest(),
            "original_models_sha256":hashlib.sha256(a.models.read_bytes()).hexdigest(),
            "proof":False,"fermat_executed":False,"rational_lift":False},
            "fits":fits,"rejected_points":rejected}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=a.output.name+".",suffix=".tmp",dir=str(a.output.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(report,f,indent=2);f.write("\n")
        os.replace(tmp,a.output)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print("VP05_INDEPENDENT_PRIME_SUMMARY "+json.dumps({**report["summary"],"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
