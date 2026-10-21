"""Fail-closed VP05 physical target readiness gate for saved initiate-only Kira run.

This diagnostic never launches Kira. A Kira SYSTEM regeneration count does
NOT certify any reduction, including an omitted mandatory non-master.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_weight_audit import parse_file_integrals,load_codec

def last_match(text,pattern):
 matches=re.findall(pattern,text,re.I)
 return int(matches[-1]) if matches else None

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 ap.add_argument("--codec-file",type=Path,default=Path("output/tools/pyred_weight.py"))
 ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_physical_reduction_readiness_gate.json"))
 args=ap.parse_args()
 job=(args.project/"jobs.yaml").read_text(encoding="utf-8-sig")
 monitored=(args.project/"monitored_kira.log").read_text(encoding="utf-8-sig",errors="replace")
 mandatory=parse_file_integrals(args.project/"mandatory_provisional64_sector203.txt")
 masters=parse_file_integrals(args.project/"results/VP05_full/masters")
 if len(mandatory)!=5 or len(masters)!=5:ap.error("Expected 5 mandatory and 5 saved master entries")
 m=load_codec(args.codec_file)
 bits,ordering=m.from_kiradb(str(args.project/"results/kira.db"))
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 values=[]
 for x in mandatory:
  w=int(codec.encode(x))
  if tuple(int(v) for v in codec.decode(w))!=x:raise RuntimeError("Kira codec roundtrip failure")
  values.append({"integral":"VP05_full["+",".join(map(str,x))+"]",
      "weight":w,"sector":int(m.sec_of(x)),
      "saved_master":x in masters,
      "classification":"SAVED_MASTER" if x in masters else "NONMASTER_REDUCTION_NOT_VERIFIED"})
 selected=last_match(monitored,r"Number of selected equations to reduce:\s*(\d+)\s+equations")
 all_selected=re.findall(r"Number of selected equations to reduce:\s*(\d+)\s+equations",monitored,re.I)
 regenerate="Regenerate:" in monitored
 forward=last_match(monitored,r"solve forward:\s*([\d]+)\.?\d*")
 no_triangular=bool(re.search(r"run_triangular:\s*false",job,re.I))
 no_back=bool(re.search(r"run_back_substitution:\s*false",job,re.I))
 report={"status":"PHYSICAL_REDUCTION_NOT_CERTIFIED",
   "original_job_initiate_only":bool(re.search(r"run_initiate:\s*true",job,re.I)) and no_triangular and no_back,
   "selection_counts":[int(x) for x in all_selected],
   "regenerate_marker_present":regenerate,
   "saved_masters":len(masters),"mandatory_targets":values,
   "mandatory_masters":sum(x["saved_master"] for x in values),
   "unresolved_physical_targets":[x for x in values if not x["saved_master"]],
   "physical_target_reduction_certificate_verified":False,
   "safe_next_action":"Use a separate guarded Kira target-reduction dry-run/preflight for the one non-master; do not change or overwrite this initiate-only project or rerun 528-row proof.",
   "warning":"SYSTEM generation and algebraic 528-row replay are NOT physical target reduction certificates."}
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_PHYSICAL_READINESS_GATE "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
