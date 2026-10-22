"""Trace saved VP05 L2 preferred-master input and its generator, read-only.

Unlike the previous config/jobs-only audit, scan the project root, associated
logs, text manifests and QEDCalc source scripts. Report explicit file candidates
and positions 5/6/10; do not interpret result masters as input preferences.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_weight_audit import ROOT,parse_file_integrals
NEEDLE=re.compile(r"preferred[_ -]?masters|preferred[_ -]?basis|select_masters_reduction|mandatory_provisional64|provisional64_sector203",re.I)
SUFFIX={".yaml",".yml",".json",".txt",".log",".bat",".py",".ps1",".md"}
SKIP={".git","__pycache__","node_modules",".venv","venv"}
def scan(root,base,max_files):
 items=[];visited=0
 if not root.exists():return items,visited
 for f in root.rglob("*"):
  if any(s in SKIP for s in f.relative_to(root).parts):continue
  if not f.is_file() or f.suffix.lower() not in SUFFIX or f.stat().st_size>2_000_000:continue
  visited+=1
  if visited>max_files:raise RuntimeError("Source scan cap reached")
  lines=f.read_text(encoding="utf-8-sig",errors="replace").splitlines()
  hits=[{"line":i,"context":lines[max(0,i-3):min(len(lines),i+4)]} for i,line in enumerate(lines) if NEEDLE.search(line)]
  if hits:items.append({"file":str(f.relative_to(base)) if f.is_relative_to(base) else str(f),"matches":hits[:8]})
 return items,visited
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--project",type=Path,default=DEFAULT)
 ap.add_argument("--max-source-files",type=int,default=6000)
 a=ap.parse_args()
 project=a.project.resolve()
 repo=ROOT.resolve()
 # Avoid scanning output recursively, which contains huge experiment datasets.
 project_hits,project_n=scan(project,project,1000)
 source_hits=[];source_n=0
 for relative in ("examples","three_loop"):
  h,n=scan(repo/relative,repo,a.max_source_files)
  source_hits+=h;source_n+=n
 candidates=[]
 for f in sorted(project.rglob("*")):
  if not f.is_file() or f.stat().st_size>1_000_000:continue
  if "master" not in f.name.lower() and "basis" not in f.name.lower() and "mandatory" not in f.name.lower():continue
  if f.suffix.lower() not in ("",".txt",".yaml",".yml"):continue
  powers=parse_file_integrals(f)
  if powers:
   candidates.append({"file":str(f.relative_to(project)),"integrals":len(powers),
     "position_5":list(powers[4]) if len(powers)>=5 else None,
     "position_6":list(powers[5]) if len(powers)>=6 else None,
     "position_10":list(powers[9]) if len(powers)>=10 else None})
 output={"status":"PREFERRED_MASTER_INPUT_TRACE","project_config_matches":project_hits[:60],
 "qedcalc_generator_matches":source_hits[:75],"candidate_lists":candidates[:75],
 "files_scanned":{"project":project_n,"code":source_n},
 "preferred_master_input_sequence_verified":False,
 "small_weight_to_exponents_verified":False,"kira_executed":False,
 "source_files_modified":False,
 "note":"An input sequence must be verified against the actual Kira configuration, not inferred from output masters or filenames."}
 print("VP05_PREFERRED_INPUT_TRACE "+json.dumps(output,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
