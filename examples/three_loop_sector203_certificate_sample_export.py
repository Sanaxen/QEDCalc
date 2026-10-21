"""Save replay-checked compressed VP05 modular certificate samples.

Training and holdout roles are kept separate. Atomic export, source SHA256,
independent recomputation. No Fermat/Kira; no rational-function proof.
"""
from __future__ import annotations
import argparse,hashlib,json,os,tempfile
from pathlib import Path
from examples.three_loop_sector203_dual_certificate_preflight import dual_certificate
from examples.three_loop_sector203_target_scope_preflight import DEFAULT,TARGET
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_target_rowspace_audit import residue

TRAIN=((1000037,21,15),(1001003,19,53),(1001107,36,64),(1002101,47,83))
HOLD=((1003001,17,71),(1004003,43,29))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_compressed_certificate_samples.json"))
    a=ap.parse_args()
    data=a.equations.read_bytes()
    source=json.loads(data.decode("utf-8-sig"))
    if source.get("type")!="symbolic_exact_linear_combinations" or len(source.get("rows",[]))!=166:
        ap.error("Expected exactly 166 compressed equations")
    rows=source["rows"];samples=[]
    for role,points in (("training",TRAIN),("holdout",HOLD)):
        for p,z,d in points:
            target={k:residue(c,p,z,d) for k,c in TARGET.items()}
            r=dual_certificate(mod_rows(rows,p,z,d),target,p)
            if r["rank"]!=166 or r["remainder_size"] or not r["replay_verified"]:
                raise RuntimeError(f"Replay/rank failed for {(p,z,d)}")
            sample={"point":[p,z,d],"role":role,
                    "coefficients_by_compressed_row":[r["certificate"].get(i,0) for i in range(166)],
                    "rank":r["rank"],"replay_verified":True}
            samples.append(sample)
            print("VP05_CERT_SAMPLE "+json.dumps({"point":sample["point"],"role":role,
                "nonzero_coefficients":sum(x!=0 for x in sample["coefficients_by_compressed_row"]),
                "replay_verified":True,"proof":False}),flush=True)
    manifest={"type":"compressed_modular_certificate_samples",
        "source_sha256":hashlib.sha256(data).hexdigest(),
        "source":str(a.equations),"rows":166,
        "target":[{"key":list(k),"coefficient":v} for k,v in TARGET.items()],
        "samples":samples,"alias_mapping_verified":False,
        "symbolic_reconstruction":False,"proof":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=a.output.name+".",suffix=".tmp",dir=str(a.output.parent))
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(manifest,f,indent=2)
            f.write("\n")
        os.replace(tmp,a.output)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print("VP05_CERT_SAMPLES_SUMMARY "+json.dumps({
        "training":len(TRAIN),"holdout":len(HOLD),"rows":166,
        "output":str(a.output),"source_sha256":manifest["source_sha256"],
        "fermat_executed":False,"proof":False}),flush=True)

if __name__=="__main__":main()
