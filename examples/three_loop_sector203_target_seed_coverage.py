"""Fail-closed VP05 seed coverage audit using original project artifacts.

Checks whether mandatory physical targets are present in the original SYSTEM
and whether the Kira result metadata explicitly reports them. Absence does
not establish a missing seed without inspecting generation commands.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_weight_audit import load_codec,parse_file_integrals

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--presence",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_full_system_physical_target_presence.json"))
 p.add_argument("--codec-file",type=Path,default=Path("output/tools/pyred_weight.py"))
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_target_seed_coverage_preflight.json"))
 a=p.parse_args()
 observed=json.loads(a.presence.read_text(encoding="utf-8-sig"))
 if observed.get("status")!="FULL_SYSTEM_TARGET_PRESENCE_AUDIT" or observed.get("source_equations")!=2678:
  p.error("Expected full 2678-equation source audit")
 m=load_codec(a.codec_file);bits,ordering=m.from_kiradb(str(a.project/"results/kira.db"))
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 mandatory=parse_file_integrals(a.project/"mandatory_provisional64_sector203.txt")
 if len(mandatory)!=5:p.error("Expected five mandatory target vectors")
 references=[]
 for rel in ("jobs.yaml","config/jobs.yaml","config/integralfamilies.yaml",
             "preferred_provisional64_sector203.txt","mandatory_provisional64_sector203.txt",
             "results/preferredMasters","results/VP05_full/masters",
             "provisional64_sector203_preflight.json","qedcalc_master_basis_manifest.json"):
  file=a.project/rel
  item={"path":rel,"exists":file.is_file()}
  if file.is_file() and file.stat().st_size<100000:
   item["head"]=file.read_text(encoding="utf-8-sig",errors="replace").splitlines()[:18]
  references.append(item)
 records=[]
 for v in mandatory:
  w=int(codec.encode(v));row=next((r for r in observed["targets"] if r["weight"]==w),None)
  if row is None:raise ValueError("Mandatory target absent from full-system audit input")
  records.append({"integral":row["integral"],"weight":w,"recorded_occurrences":row["recorded_occurrences"],
      "roundtrip_verified":tuple(codec.decode(w))==v,
      "in_mandatory_file":True})
 report={"status":"TARGET_SEED_COVERAGE_UNRESOLVED",
   "original_equations":observed["source_equations"],"records":records,
   "all_mandatory_absent_from_original_SYSTEM":all(r["recorded_occurrences"]==0 for r in records),
   "generation_artifacts":references,
   "recommendation":"Audit exact Kira generate_input/reduce commands and job seed ranges and verify that target integrals were passed to the solver. If missing, regenerate constrained sector-203 seed and then rerun presence audit.",
   "seed_incompleteness_proven":False,"physical_ibp_reduction_proven":False}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_TARGET_SEED_COVERAGE "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
