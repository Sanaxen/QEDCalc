"""Safely prepare isolated provisional64 sector203 r6s6d1 or r7s6d2 Kira project.
No Kira launch. Existing projects and candidate files are never overwritten.
"""
from __future__ import annotations
import argparse,json,re,shutil
from datetime import datetime
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,CANDIDATE,parse_file_integrals
from examples.three_loop_sector203_provisional64_r7_prepare import EXTRA,PROVISIONAL,fmt,sector
from three_loop.master_basis_api import Seed,export_kira_project
from examples.three_loop_master_basis_candidate_firefly_numerator import _context

def main():
    p=argparse.ArgumentParser()
    p.add_argument("seed",choices=["r6s6d1","r7s6d2"])
    p.add_argument("--run-id",default=None)
    a=p.parse_args()
    run_id=a.run_id or datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,48}",run_id):p.error("unsafe run ID")
    original=parse_file_integrals(CANDIDATE)
    proposed=parse_file_integrals(PROVISIONAL)
    if len(original)!=63 or len(set(original))!=63 or len(proposed)!=64 or len(set(proposed))!=64:
        p.error("63/64 candidate file count or uniqueness differs from verified audit")
    if proposed[:63]!=original or proposed[-1]!=EXTRA:p.error("provisional64 differs from expected appended candidate")
    targets=[fmt(x) for x in proposed if sector(x)==203]
    preferred=sorted({fmt(x) for x in proposed if (sector(x)&203)==sector(x)})
    if len(targets)!=5 or len(preferred)!=10:p.error("expected five targets and ten preferred masters")
    spec,baseline,*_= _context(argparse.Namespace(family="VP05_full",baseline_seed=Seed(8,3,0),sector=203,max_s=6,max_d=2))
    if spec.family_id!="VP05_full" or baseline.tag!="r8s3d0":p.error("unexpected topology baseline")
    seed=Seed(6,6,1) if a.seed=="r6s6d1" else Seed(7,6,2)
    project=ROOT/"output"/f"kira_vp05_full_provisional64_sec203_{seed.tag}_{run_id}"
    if project.exists():p.error(f"refusing to overwrite project: {project}")
    export_kira_project(spec,project,seed=seed,solver="masters",
        mandatory_file="mandatory_provisional64_sector203.txt",
        reduce_sectors=[203],top_level_sectors=[203],
        preferred_masters_file="preferred_provisional64_sector203.txt",clean=False)
    (project/"mandatory_provisional64_sector203.txt").write_text("\n".join(targets)+"\n",encoding="utf-8")
    (project/"preferred_provisional64_sector203.txt").write_text("\n".join(preferred)+"\n",encoding="utf-8")
    shutil.copy2(ROOT/"scripts"/"sector203_monitored_kira.py",project/"sector203_monitored_kira.py")
    job=(project/"jobs.yaml").read_text(encoding="utf-8")
    if any(f"r: {seed.r}, s: {seed.s}, d: {seed.d}" not in job for _ in [0]):
        p.error("generated jobs.yaml seed mismatch")
    required=["run_initiate: true","run_triangular: false","run_back_substitution: false","run_firefly: false",
              "sectors: [203]","select_mandatory_list:"]
    if not all(token in job for token in required):p.error("unsafe/unexpected jobs.yaml")
    manifest={"status":"PREPARED_ONLY_DO_NOT_AUTO_RUN","project":str(project),
       "seed":seed.tag,"sector":203,"target_count":len(targets),"preferred_count":len(preferred),
       "targets":targets,"source_candidate_file":str(PROVISIONAL),
       "execution":"manual via separate monitored BAT; no Kira launched",
       "warning":"May still be very expensive; resource guard cannot guarantee short runtime"}
    (project/"provisional64_sector203_preflight.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
