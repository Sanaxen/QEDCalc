"""Clone an existing single-target sector-203 Kira configuration for a monitored run."""
import argparse
import re
import shutil
from pathlib import Path
from three_loop.integral_family_classification import ROOT
def main():
    p=argparse.ArgumentParser()
    p.add_argument("target",type=int)
    p.add_argument("seed",choices=("r5s6d0","r6s6d1","r7s6d2"))
    p.add_argument("--run-id", default="original")
    args=p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", args.run_id):
        p.error("run-id must contain only letters, numbers, underscore, dash")
    if args.target not in range(1,5):
        p.error("target must be 1..4")
    base=ROOT/"output"/"kira_vp05_full_preferred_masters_r8s3d0_r7s6d2_sec203"
    source=base.with_name(base.name+f"_single_t{args.target}_{args.seed}")
    dest=base.with_name(base.name+f"_monitored_t{args.target}_{args.seed}" + ("" if args.run_id=="original" else f"_{args.run_id}"))
    if dest.exists():
        raise FileExistsError(f"refusing to overwrite existing monitored project: {dest}")
    required=["jobs.yaml","config/integralfamilies.yaml","config/kinematics.yaml","mandatory_firefly_numerator_target.txt"]
    for name in required:
        if not (source/name).is_file():
            raise FileNotFoundError(f"{source/name}; run original single-target preparation first")
    dest.mkdir()
    for name in required:
        target=dest/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source/name,target)
    shutil.copy2(ROOT/"scripts"/"sector203_monitored_kira.py",dest/"sector203_monitored_kira.py")
    print(f"MONITORED_PROJECT={dest}")
if __name__=="__main__":
    main()
