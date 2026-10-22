"""Inspect Kira preferred-master weight remapping evidence in original L2 project.

Kira's Integral::set_preferred_masters assigns 1-based compact weights to the
ordered imported preferred-basis integral list; those are NOT output masters.
Scan only project YAML/config and explicitly referenced text candidates.
No automatic physical alias unless exact input list and version are confirmed.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_weight_audit import parse_file_integrals
def main():
 p=argparse.ArgumentParser();p.add_argument("--project",type=Path,default=DEFAULT);a=p.parse_args()
 root=a.project.resolve()
 files=sorted(x for d in ("config","jobs") for x in (root/d).rglob("*") if x.is_file() and x.suffix.lower() in (".yaml",".yml",".txt"))
 if len(files)>160:raise SystemExit("Configuration file cap exceeded")
 matches=[]
 for f in files:
  if f.stat().st_size>2_000_000:continue
  ls=f.read_text(encoding="utf-8-sig",errors="replace").splitlines()
  for idx,line in enumerate(ls):
   if re.search(r"preferred[_ -]?masters|preferred[_ -]?basis|basisfile|select_masters_reduction",line,re.I):
    matches.append({"file":str(f.relative_to(root)),"line":idx+1,"excerpt":ls[max(0,idx-2):min(len(ls),idx+5)]})
 candidates=[]
 for f in sorted((root/"config").rglob("*")):
  if not f.is_file() or f.stat().st_size>2_000_000:continue
  if f.suffix.lower() not in ("",".txt",".yaml",".yml"):continue
  try: igls=parse_file_integrals(f)
  except (UnicodeError,OSError):continue
  if igls and ("master" in f.name.lower() or "basis" in f.name.lower()):
   candidates.append({"file":str(f.relative_to(root)),"count":len(igls),
    "one_based_candidate_6":list(igls[5]) if len(igls)>=6 else None,
    "one_based_candidate_10":list(igls[9]) if len(igls)>=10 else None,
    "one_based_candidate_5":list(igls[4]) if len(igls)>=5 else None})
 report={"status":"PREFERRED_MASTER_REMAP_SOURCE_INVESTIGATION",
  "source_reference":"https://github.com/BootLoops-ai/kira/blob/main/src/pyred/integrals.cpp",
  "source_lines":"Integral::set_preferred_masters near lines 1492-1525 and Integral::properties near lines 980-996",
  "matching_config_lines":matches[:45],"candidate_config_basis_lists":candidates[:25],
  "total_matches":len(matches),"original_project":str(root),
  "small_id_values":[5,6,10],"output_masters_are_not_preferred_basis_input":True,
  "full_input_mapping_verified":False,"kira_version_compatibility_verified":False,
  "physical_propagator_mapping_verified":False,"kira_executed":False,"source_files_modified":False}
 print("VP05_PREFERRED_WEIGHT_SOURCE_AUDIT "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
