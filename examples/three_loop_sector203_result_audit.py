"""Read-only audit: completed sector-203 Kira log versus refined VP05 candidates."""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "kira_vp05_full_preferred_masters_r8s3d0_r7s6d2_sec203_monitored_t1_r5s6d0_"
CANDIDATE = ROOT / "output/three_loop_integral_family_audit/vp05_full_masters_r8s3d0_union_r8s5d2_refined_masters.txt"
INTEGRAL = re.compile(r"VP05_full\[[^\]\r\n]+\]")
HEADER = re.compile(r"Number of master integrals:\s*(\d+)")
def sector(expr):
    entries = [int(x.strip()) for x in expr.split("[", 1)[1].rstrip("]").split(",")]
    return sum((1 << i) for i, x in enumerate(entries) if x > 0)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--project",type=Path)
    args=a.parse_args()
    projects = sorted((ROOT/"output").glob(PREFIX+"*"), key=lambda p:p.stat().st_mtime)
    project = args.project or (projects[-1] if projects else None)
    if project is None or not (project/"kira.log").is_file():
        raise FileNotFoundError("Completed sector-203 project kira.log not found")
    if not CANDIDATE.is_file():
        raise FileNotFoundError(CANDIDATE)
    log=(project/"kira.log").read_text(encoding="utf-8",errors="replace")
    matches=list(HEADER.finditer(log))
    if not matches:
        raise ValueError("Kira master count not found in log")
    count=int(matches[-1].group(1))
    section=log[matches[-1].end():].split("Number of selected equations",1)[0]
    found=INTEGRAL.findall(section)
    if len(found)!=count or len(set(found))!=count:
        raise ValueError(f"log master extraction mismatch: header {count}, extracted {len(found)}")
    candidates=INTEGRAL.findall(CANDIDATE.read_text(encoding="utf-8"))
    if len(set(candidates))!=len(candidates):
        raise ValueError("duplicate entries in candidate list")
    recorded=[x for x in found if sector(x)==203]
    proposed=[x for x in candidates if sector(x)==203]
    report={"project":str(project),"candidate_file":str(CANDIDATE),
            "seed":"r5s6d0","master_count":count,
            "masters_by_sector":{str(s):[x for x in found if sector(x)==s] for s in sorted(set(map(sector,found)))},
            "sector203_masters":recorded,"sector203_candidates":proposed,
            "sector203_overlap":sorted(set(recorded)&set(proposed)),
            "sector203_only_in_kira":sorted(set(recorded)-set(proposed)),
            "sector203_only_in_candidates":sorted(set(proposed)-set(recorded)),
            "note":"Representative overlap is not a proof of equal IBP span or final r7s6d2 closure. No files modified."}
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=="__main__":
    main()
