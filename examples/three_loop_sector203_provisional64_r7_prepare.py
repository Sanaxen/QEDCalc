"""Prepare ONLY a unique restricted VP05 sector203 r7s6d2 Kira project.

No Kira execution. No modifications to existing 63/64 candidate files or
previous Kira results. Uses the 64-entry provisional file explicitly.
"""
import argparse
import json
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,CANDIDATE,parse_file_integrals
from three_loop.master_basis_api import Seed,export_kira_project
from examples.three_loop_master_basis_candidate_firefly_numerator import _context

EXTRA=(1,1,-1,1,0,0,1,1,0,0,0,0)
PROVISIONAL=ROOT/"output/three_loop_integral_family_audit/vp05_full_masters_r8s3d0_union_r8s5d2_provisional64_masters.txt"

def fmt(x):return "VP05_full["+",".join(map(str,x))+"]"
def sector(x):return sum(1<<i for i,a in enumerate(x) if a>0)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--run-id",default="provisional64_dryprep")
    args=p.parse_args()
    import re
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,48}",args.run_id):p.error("unsafe run ID")
    original=parse_file_integrals(CANDIDATE)
    expanded=parse_file_integrals(PROVISIONAL)
    if len(original)!=63 or len(set(original))!=63 or len(expanded)!=64 or len(set(expanded))!=64:
        p.error("63/64 candidate integrity check failed")
    if expanded[:63]!=original or expanded[-1]!=EXTRA:p.error("64 file does not exactly append expected fifth candidate")
    targets=[fmt(x) for x in expanded if sector(x)==203]
    if len(targets)!=5:p.error("expected five sector203 targets")
    # Fetch the topology spec through the existing validated QEDCalc context.
    ns=argparse.Namespace(family="VP05_full",baseline_seed=Seed(8,3,0),sector=203,max_s=6,max_d=2)
    spec,baseline,*_= _context(ns)
    if spec.family_id!="VP05_full" or baseline.tag!="r8s3d0":p.error("wrong family context")
    base=ROOT/"output"
    project=base/("kira_vp05_full_provisional64_sec203_r7s6d2_"+args.run_id)
    if project.exists():p.error(f"refusing to alter existing project {project}")
    # Preferred: exact-sector five plus proper-subsector provisional candidates.
    preferred=sorted({fmt(x) for x in expanded if (sector(x)&203)==sector(x)})
    if not set(targets).issubset(set(preferred)):p.error("targets not preferred")
    export_kira_project(spec,project,seed=Seed(7,6,2),solver="masters",
        mandatory_file="mandatory_provisional64_sector203.txt",
        reduce_sectors=[203],top_level_sectors=[203],
        preferred_masters_file="preferred_provisional64_sector203.txt",clean=False)
    (project/"mandatory_provisional64_sector203.txt").write_text("\n".join(targets)+"\n",encoding="utf-8")
    (project/"preferred_provisional64_sector203.txt").write_text("\n".join(preferred)+"\n",encoding="utf-8")
    manifest={"status":"PREPARED_ONLY_DO_NOT_AUTO_RUN","project":str(project),
        "family":"VP05_full","seed":"r7s6d2","sector":203,
        "candidate_file":str(PROVISIONAL),"target_count":len(targets),
        "targets":targets,"preferred_count":len(preferred),
        "required_next_step":"Review jobs.yaml/estimated workload before any Kira execution",
        "warning":"r7s6d2 multi-target may be extremely expensive; no Kira launch performed"}
    (project/"provisional64_sector203_preflight.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
