"""Shrink five ambiguous VP05 degree-six kernels with fresh off-grid points.

Replay original 70 second-prime training samples; keep the ten original
holdouts completely out of the fitting matrix. Add bounded off-grid training
points, replay modular IBP certificates, track nullities after each addition,
then validate any projectively unique recovered model on ten holdouts.
No Fermat/Kira, no characteristic-zero proof.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
from collections import Counter
from examples.three_loop_sector203_second_prime_ambiguity_audit import rref
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value
from examples.three_loop_sector203_certificate_adaptive_degree import fit
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_dual_certificate_preflight import dual_certificate
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT
from examples.three_loop_sector203_target_rowspace_audit import residue

ROOT=Path("output/three_loop_integral_family_audit")
ROWS=(21,32,44,110,113)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--trial",type=Path,default=ROOT/"vp05_independent_prime_certificate_grid9.json")
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_grid9_offgrid_kernel_shrink.json")
    ap.add_argument("--extra-training",type=int,default=12)
    ap.add_argument("--max-attempts",type=int,default=60)
    a=ap.parse_args()
    if not 1<=a.extra_training<=32 or not a.extra_training<=a.max_attempts<=200:
        ap.error("Invalid sampling bounds")
    raw=a.equations.read_bytes(); eq=json.loads(raw.decode("utf-8-sig"))
    trial=json.loads(a.trial.read_text(encoding="utf-8-sig"))
    s=trial["summary"]; p=s["prime"]
    if (s.get("columns"),s["training"],s["holdouts"],s["rejected"])!=(9,70,10,0):
        ap.error("Require original grid9 70 training / 10 holdout trial")
    if hashlib.sha256(raw).hexdigest()!=s["equations_sha256"] or len(eq["rows"])!=166:
        ap.error("Compressed equations mismatch")
    failed={x["row"]:x for x in trial["fits"] if x["result"]["status"]!="holdout_pass"}
    if set(failed)!=set(ROWS):ap.error("Unexpected residual rows")
    original_coords=[((47+53*(i%9))%p,(83+79*(i//9))%p) for i in range(80)]
    hold_coords=set(original_coords[70:])
    occupied=set(original_coords)
    mons=powers(6);m=len(mons)
    def sample(z,d):
        evaluated=mod_rows(eq["rows"],p,z,d)
        target={k:residue(v,p,z,d) for k,v in TARGET.items()}
        cert=dual_certificate(evaluated,target,p)
        if cert["rank"]!=166 or not cert["replay_verified"]:
            raise ValueError("Rank or replay failure")
        return {"point":[p,z,d],"role":"training",
                "coefficients_by_compressed_row":[cert["certificate"].get(j,0) for j in range(166)]}
    train=[];hold=[];rejected=0
    for i,(z,d) in enumerate(original_coords):
        item=sample(z,d)
        item["role"]="training" if i<70 else "holdout"
        (train if i<70 else hold).append(item)
        if (i+1)%20==0:
            print("VP05_OFFGRID_REPLAY "+json.dumps({"replayed":i+1}),flush=True)
    def nullity(row):
        mat=[]
        for item in train:
            z,d=item["point"][1:]
            v=value(mons,z,d,p)
            y=item["coefficients_by_compressed_row"][row]
            mat.append(v+[(-y*t)%p for t in v])
        rank,basis=rref(mat,p)
        return rank,len(basis)
    before={str(row):nullity(row)[1] for row in ROWS}
    if any(before[str(row)]!=failed[row]["result"]["nullity"] for row in ROWS):
        ap.error("Failed to reproduce original kernel nullities")
    steps=[]; added=0
    for i in range(a.max_attempts):
        if added>=a.extra_training:break
        # Break both old z and d lattice coordinate sets, without touching holdouts.
        z=(101+127*i+17*i*i)%p
        d=(211+131*i+19*i*i*i)%p
        if not z or not d or (z,d) in occupied or (z,d) in hold_coords:continue
        try:item=sample(z,d)
        except (ZeroDivisionError,ValueError):
            rejected+=1;continue
        train.append(item);occupied.add((z,d));added+=1
        dims={str(row):nullity(row)[1] for row in ROWS}
        steps.append({"point":[p,z,d],"after_added":added,"kernel_nullities":dims})
        if added%3==0 or added==a.extra_training:
            print("VP05_OFFGRID_PROGRESS "+json.dumps({"added":added,"requested":a.extra_training,"nullities":dims}),flush=True)
    if added!=a.extra_training:
        raise RuntimeError("Not enough valid off-grid points; no output written")
    results=[];tally=Counter()
    for row in ROWS:
        rank,n=nullity(row)
        outcome=fit(train,hold,p,row,6,6) if n==1 else None
        status=outcome["status"] if outcome else ("no_nonzero_fit" if n==0 else "still_nonunique")
        tally[status]+=1
        results.append({"row":row,"rank":rank,"nullity":n,"status":status,"model":outcome})
    report={"summary":{"prime":p,"original_training":70,"added_training":added,
        "holdouts_untouched":10,"initial_nullities":before,
        "final_nullities":{str(r["row"]):r["nullity"] for r in results},
        "outcome_counts":dict(tally),"rejected_new_points":rejected,
        "equations_sha256":hashlib.sha256(raw).hexdigest(),
        "trial_sha256":hashlib.sha256(a.trial.read_bytes()).hexdigest(),
        "proof":False,"fermat_executed":False},
        "steps":steps,"rows":results}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=a.output.name+".",suffix=".tmp",dir=str(a.output.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:json.dump(report,f,indent=2);f.write("\n")
        os.replace(tmp,a.output)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print("VP05_OFFGRID_KERNEL_SHRINK "+json.dumps({**report["summary"],"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
