"""Prepare (never execute) isolated VP05 single non-master Kira reduction.

Copies only small text configs, not original Kira database/SYSTEM, and
refuses overwriting a destination. Explicit dry run is the default.
"""
from __future__ import annotations
import argparse,json,shutil
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_weight_audit import parse_file_integrals

TARGET=(1,1,0,1,0,0,1,1,0,0,0,0)
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source-project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--destination",type=Path,default=Path("output/vp05_single_nonmaster_reduction_prepared"))
 p.add_argument("--create",action="store_true",help="Only prepare new files; NEVER start Kira")
 a=p.parse_args()
 src=a.source_project.resolve();dest=a.destination.resolve()
 if dest==src or src in dest.parents: p.error("Destination may not be original project or inside it")
 required=["config/integralfamilies.yaml","config/kinematics.yaml"]
 for x in required:
  if not (src/x).is_file():p.error(f"Missing source {x}")
 oldjobs=(src/"jobs.yaml").read_text(encoding="utf-8-sig")
 mandatory=parse_file_integrals(src/"mandatory_provisional64_sector203.txt")
 masters=parse_file_integrals(src/"results/VP05_full/masters")
 if TARGET not in mandatory or TARGET in masters:p.error("Expected target to be sole mandatory non-master")
 if not all(x in masters for x in mandatory if x!=TARGET):p.error("Other mandatory targets unresolved")
 if dest.exists():p.error(f"Destination already exists; refusing overwrite: {dest}")
 job="""jobs:
  - reduce_sectors:
      reduce:
        - {topologies: [VP05_full], sectors: [203], r: 6, s: 6, d: 1}
      truncate_sp:
        - {topologies: [VP05_full], l: 2}
      select_integrals:
        select_mandatory_list:
          - [VP05_full,mandatory_single_nonmaster.txt]
      preferred_masters: "preferred_provisional64_sector203.txt"
      run_symmetries: true
      run_initiate: true
      run_triangular: false
      run_back_substitution: false
      run_firefly: false
"""
 report={"status":"PREVIEW_ONLY" if not a.create else "PREPARED_NOT_EXECUTED",
   "original_project":str(src),"destination":str(dest),
   "target":"VP05_full["+",".join(map(str,TARGET))+"]",
   "source_seed":[6,6,1],"truncate_sp_l":2,
   "run_initiate":True,"run_triangular":False,"run_back_substitution":False,
   "kira_executed":False,"source_project_modified":False,
   "warning":"Kira dry-run/schema validation and reduction stage configuration remain future steps; this prepare step does not prove reduction."}
 if a.create:
  (dest/"config").mkdir(parents=True,exist_ok=False)
  for x in required:shutil.copy2(src/x,dest/x)
  (dest/"jobs.yaml").write_text(job,encoding="utf-8")
  (dest/"mandatory_single_nonmaster.txt").write_text(
    "VP05_full["+",".join(map(str,TARGET))+"]\n",encoding="utf-8")
  shutil.copy2(src/"preferred_provisional64_sector203.txt",dest/"preferred_provisional64_sector203.txt")
  (dest/"qedcalc_preparation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print("VP05_SINGLE_NONMASTER_PREPARE "+json.dumps(report),flush=True)
if __name__=="__main__":main()
