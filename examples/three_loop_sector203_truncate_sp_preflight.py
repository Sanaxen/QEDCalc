"""Offline, non-destructive Kira 3 truncate_sp preflight for VP05 sector203.

Creates a separate preview jobs YAML for each l, NEVER starts Kira.
Counts combinatorial seed tuples, not IBP equations or actual memory.
"""
import argparse
import json
import math
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT
from examples.three_loop_sector139_seed_pressure_audit import SECTORS,count_sector

DEFAULT=ROOT/"output/kira_vp05_full_provisional64_sec203_r6s6d1_20261016_090739_388470"
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--project",type=Path,default=DEFAULT)
    parser.add_argument("--l-values",type=int,nargs="+",default=[2,3,4,5])
    a=parser.parse_args()
    project=a.project.resolve()
    src=project/"jobs.yaml"
    if not src.is_file():parser.error(f"missing jobs: {src}")
    text=src.read_text(encoding="utf-8")
    if "truncate_sp:" in text:parser.error("source already uses truncate_sp; refusing ambiguous substitution")
    required=("sectors: [203], r: 6, s: 6, d: 1","select_mandatory_list:","run_initiate: true","run_triangular: false","run_firefly: false")
    if not all(x in text for x in required):parser.error("unexpected jobs.yaml content")
    selection="      select_integrals:\n"
    if text.count(selection)!=1:parser.error("expected exactly one select_integrals block")
    mfile=project/"mandatory_provisional64_sector203.txt"
    targets=[x.strip() for x in mfile.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(targets)!=5:parser.error("expected five mandatory targets")
    # Formula from Kira 3 paper: s <= max(1, t-l+1, explicit s_max,sector)
    # Explicit s=6 for sector203, no explicit lower-sector override.
    output=[]
    full={s:count_sector(s,6,6,1) for s in SECTORS}
    for l in sorted(set(a.l_values)):
        if l<0 or l>20:parser.error("l out of 0..20 audit safety range")
        caps={s:(6 if s==203 else min(6,max(1,s.bit_count()-l+1))) for s in SECTORS}
        estimates={s:count_sector(s,6,caps[s],1) for s in SECTORS}
        # Separate preview file only; allow rerun if identical, refuse conflict.
        preview=project/f"jobs.truncate_sp_l{l}.preview.yaml"
        modified=text.replace(selection,"      truncate_sp: [1: "+str(l)+"]\n"+selection)
        if preview.exists():
            if preview.read_text(encoding="utf-8")!=modified:parser.error(f"preview exists with different contents: {preview}")
        else:
            preview.write_text(modified,encoding="utf-8",newline="\n")
        total=sum(estimates.values()); baseline=sum(full.values())
        output.append({"l":l,"preview":str(preview),"all_14_index_count":total,
          "baseline_index_count":baseline,"count_ratio":round(total/baseline,4),
          "sector202_s_cap":caps[202],"sector202_index_count":estimates[202],
          "sector139_s_cap":caps[139],"sector139_index_count":estimates[139],
          "sector203_s_cap":caps[203],"sector203_index_count":estimates[203],
          "per_sector":[{"sector":s,"s_cap":caps[s],"index_count":estimates[s]} for s in SECTORS]})
    print(json.dumps({"status":"OFFLINE_PREVIEW_ONLY","source_jobs":str(src),
      "notes":["Kira 3 seed truncation modeled as s <= max(1, t-l+1, explicit s_sector); t=popcount(sector).",
      "These index counts are combinatorial proxies only, not actual Kira equations or resource predictions.",
      "Preview files are not named jobs.yaml and cannot be run by the existing monitored BAT.",
      "Truncation can introduce spurious masters; validation against known ten-master r5s6d0 evidence and later r7s6d2 is required."],
      "proposals":output},indent=2,ensure_ascii=False))
if __name__=="__main__":main()
