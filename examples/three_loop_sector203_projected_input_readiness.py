"""Read-only inventory of actual VP05 projected-amplitude readiness.

Contrast Q01's 910-term projected input, native ISP bridge, FORM table,
and stable basis with the saved VP05 single-target exact certificate.
Do not interpret a topology input .tex or Kira mandatory list as a
projected-amplitude artifact.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_weight_audit import ROOT,parse_file_integrals
from three_loop.vp05_verified_reduction import TARGET,MASTER_6,MASTER_5
def main():
 p=argparse.ArgumentParser();p.add_argument("--project",type=Path,default=DEFAULT)
 a=p.parse_args();root=ROOT.resolve();project=a.project.resolve()
 q01=root/"output/3loop_q01_integral_indices.txt"
 vp_input=root/"input/three_loop/VP05.tex"
 candidate_names=("3loop_vp05_integral_indices.txt","3loop_VP05_integral_indices.txt",
     "vp05_projected_amplitude.txt","vp05_projected_integral_indices.txt")
 candidate_files=[root/"output"/n for n in candidate_names]
 existing_candidates=[str(x.relative_to(root)) for x in candidate_files if x.is_file()]
 # Metadata-only scan of names; avoid opening heavy projected-trace data.
 output_names=[str(f.relative_to(root)) for f in (root/"output").iterdir()
    if f.is_file() and re.search(r"vp05.*(projected|amplitude|integral_indices)|(?:projected|amplitude).*vp05",f.name,re.I)]
 files={
  "q01_projected_amplitude":q01.is_file(),
  "vp05_topology_input":vp_input.is_file(),
  "vp05_projected_candidate_files":existing_candidates,
  "vp05_output_top_level_name_matches":output_names[:40],
  "vp05_verified_rule":(root/"output/three_loop_integral_family_audit/vp05_verified_reduction_artifact_v1.json").is_file(),
  "vp05_preferred_list":(project/"results/preferredMasters").is_file(),
  "vp05_initiate_masters":(project/"results/VP05_full/masters").is_file(),
  "vp05_form_export_files":[str(f.relative_to(project)) for f in (project/"results/VP05_full").glob("*.inc")] if (project/"results/VP05_full").is_dir() else [],
 }
 masters=parse_file_integrals(project/"results/VP05_full/masters") if files["vp05_initiate_masters"] else []
 checks={"saved_five_masters":len(masters)==5,
  "verified_rhs_masters_present":MASTER_6 in masters and MASTER_5 in masters,
  "verified_target_not_selected_master":TARGET not in masters,
  "q01_reference_projected_present":files["q01_projected_amplitude"],
  "vp05_projected_identified":bool(existing_candidates or output_names),
  "vp05_form_export_present":bool(files["vp05_form_export_files"])}
 report={"status":"VP05_PROJECTED_INPUT_READINESS_INVENTORY",
  "checks":checks,"files":files,"actual_projected_amplitude_verified":False,
  "native_vp05_to_kira_bridge_verified":False,
  "all_vp05_targets_reduced":False,"full_vp05_master_basis_verified":False,
  "q01_reference":{"native_terms":910,"kira_target_count":944,"final_masters":60,
    "source":"output/3loop_q01_integral_indices.txt",
    "api":"three_loop/master_coefficient_api.py"},
  "vp05_scope":{"exact_target":list(TARGET),"rhs_masters":[list(MASTER_6),list(MASTER_5)],
    "single_target_reduction_verified":checks["verified_rhs_masters_present"]},
  "next_actions":["Verify whether VP05 actual projected amplitude exists (do not infer from a filename)",
    "Confirm diagram-specific native index to Kira denominator routing",
    "Enumerate actual VP05 projected native and Kira target demand",
    "Establish reduction coverage for all demand targets and stable final basis",
    "Only then run full exact coefficient synthesis"],
  "project":str(project),"kira_executed":False,"project_modified":False}
 print("VP05_PROJECTED_INPUT_READINESS "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
