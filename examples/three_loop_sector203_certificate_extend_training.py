"""Extend VP05 same-prime TRAINING set without consuming reserved holdouts.

Immutable input archive, source digest verified against compressed equations.
Independent shifted 2D grid, bounded attempts, independent modular replay.
No Fermat/Kira or symbolic proof.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_dual_certificate_preflight import dual_certificate
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT
from examples.three_loop_sector203_target_rowspace_audit import residue

BASE=Path("output/three_loop_integral_family_audit/vp05_same_prime_certificate_samples_grid_v2.json")
OUT=Path("output/three_loop_integral_family_audit/vp05_same_prime_certificate_samples_grid_v3.json")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",type=Path,default=BASE)
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=OUT)
    ap.add_argument("--extra-training",type=int,default=20)
    ap.add_argument("--max-attempts",type=int,default=100)
    a=ap.parse_args()
    if not 1<=a.extra_training<=60 or a.max_attempts<a.extra_training or a.max_attempts>500:
        ap.error("Invalid bounded extra-training / max-attempts")
    if a.output.resolve() in (a.base.resolve(),a.equations.resolve()):
        ap.error("Output must be separate from source inputs")
    base=json.loads(a.base.read_text(encoding="utf-8-sig"))
    eqbytes=a.equations.read_bytes()
    data=json.loads(eqbytes.decode("utf-8-sig"))
    if base.get("type")!="same_prime_modular_certificate_samples" or base.get("rows")!=166:
        ap.error("Invalid base certificate archive")
    if base.get("source_sha256")!=hashlib.sha256(eqbytes).hexdigest():
        ap.error("Source equation SHA256 mismatch")
    if data.get("type")!="symbolic_exact_linear_combinations" or len(data.get("rows",[]))!=166:
        ap.error("Unexpected compressed equations")
    p=base["prime"]
    old=base["samples"]
    seen=set()
    for s in old:
        point=tuple(s["point"])
        if point in seen or point[0]!=p or len(s["coefficients_by_compressed_row"])!=166 or not s.get("replay_verified") or s.get("role") not in ("training","holdout"):
            ap.error("Invalid or repeated prior sample")
        seen.add(point)
    original_holdouts=[s for s in old if s["role"]=="holdout"]
    additional=[];rejected=0
    for i in range(a.max_attempts):
        if len(additional)==a.extra_training:break
        # New lattice shifted from old grid (z=17+37*k, d=29+61*l).
        z=(23+41*(i%7))%p
        d=(47+67*(i//7))%p
        key=(p,z,d)
        if key in seen or not z or not d:continue
        try:
            evaluated=mod_rows(data["rows"],p,z,d)
            target={k:residue(v,p,z,d) for k,v in TARGET.items()}
            r=dual_certificate(evaluated,target,p)
        except (ZeroDivisionError,ValueError):
            rejected+=1;continue
        if r["rank"]!=166 or not r["replay_verified"]:
            rejected+=1;continue
        seen.add(key)
        additional.append({"point":[p,z,d],"role":"training",
                           "coefficients_by_compressed_row":[r["certificate"].get(j,0) for j in range(166)],
                           "rank":166,"replay_verified":True})
        if len(additional)%5==0 or len(additional)==a.extra_training:
            print("VP05_TRAIN_EXTEND_PROGRESS "+json.dumps({"added":len(additional),
                "requested":a.extra_training,"rejected":rejected}),flush=True)
    if len(additional)!=a.extra_training:
        raise RuntimeError("Insufficient valid new training points; output not written")
    combined=[s for s in old if s["role"]=="training"]+additional+original_holdouts
    report={**{k:v for k,v in base.items() if k not in ("samples","training","holdouts")},
            "sampling_strategy":"grid_v3_shifted_independent_lattice",
            "training":len(combined)-len(original_holdouts),
            "holdouts":len(original_holdouts),
            "samples":combined,
            "parent_archive_sha256":hashlib.sha256(a.base.read_bytes()).hexdigest(),
            "additional_training":len(additional),"rejected_new":rejected,
            "symbolic_reconstruction":False,"proof":False,"fermat_executed":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=a.output.name+".",suffix=".tmp",dir=str(a.output.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            json.dump(report,handle,indent=2);handle.write("\n")
        os.replace(tmp,a.output)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print("VP05_TRAIN_EXTEND_SUMMARY "+json.dumps({"prime":p,
        "training":report["training"],"untouched_holdouts":len(original_holdouts),
        "added":len(additional),"output":str(a.output),"proof":False}),flush=True)

if __name__=="__main__":main()
