"""Offline combinatorial diagnostic for VP05 sector139 Kira bottleneck.

Counts integral index tuples inside a sector seed envelope, NOT IBP equations,
Kira actual selected systems, CPU work, or memory consumption. Reads stopped
monitor JSONL for resource telemetry. Never starts Kira or changes inputs.
"""
from __future__ import annotations
import argparse
from collections import Counter
from math import comb
from pathlib import Path
import json
from examples.three_loop_sector203_weight_audit import ROOT

SECTORS=(73,200,137,74,67,194,138,131,201,75,202,195,139,203)
DEFAULT_PROJECT=ROOT/"output/kira_vp05_full_provisional64_sec203_r6s6d1_20261016_090739_388470"

def count_sector(sector,r,s,d,n=12):
    lines=sector.bit_count()
    nums=n-lines
    if r<lines:return 0
    maxdots=min(d,r-lines)
    # Each positive index = 1 + dot, each nonpositive = -numerator.
    # Sum of all weak compositions for dots 0..maxdots and numerator 0..s.
    numerator_count=comb(nums+s,s) if nums else 1
    dot_count=sum(comb(lines+j-1,j) for j in range(maxdots))
    dot_count+=comb(lines+maxdots-1,maxdots)
    return dot_count*numerator_count

def log_summary(path):
    if not path.is_file():return {"present":False}
    first,last=None,None
    maxswap=0.0
    sector_counts=Counter()
    samples=0
    for line in path.open(encoding="utf-8"):
        try:row=json.loads(line)
        except json.JSONDecodeError:continue
        samples+=1
        if first is None:first=row
        last=row
        maxswap=max(maxswap,float(row.get("swap_used_gib") or 0))
        sector=row.get("last_sector")
        if sector:sector_counts[str(sector[0])]+=1
    if not samples:return {"present":True,"samples":0}
    return {"present":True,"samples":samples,
        "duration_hours":round(float(last.get("elapsed_s",0))/3600,2),
        "swap_peak_gib":round(maxswap,2),
        "last_sample":last,
        "most_observed_sector_ids":sector_counts.most_common(5)}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
    args=a.parse_args()
    rows=[]
    for sector in SECTORS:
        old=count_sector(sector,5,6,0)
        new=count_sector(sector,6,6,1)
        full=count_sector(sector,7,6,2)
        rows.append({"sector":sector,"positive_lines":sector.bit_count(),
            "r5s6d0":old,"r6s6d1":new,"r7s6d2":full,
            "increment_r6_vs_r5":new-old,
            "ratio_r6_to_r5":round(new/old,3) if old else None,
            "ratio_r7_to_r6":round(full/new,3) if new else None})
    output={"scope":"combinatorial integral-index enumeration; NOT Kira IBP equation count",
        "index_count":12,"sector139":next(r for r in rows if r["sector"]==139),
        "sectors_in_prior_Kira_order":rows,
        "total_over_14_sectors":{k:sum(x[k] for x in rows) for k in ("r5s6d0","r6s6d1","r7s6d2")},
        "stopped_project":str(args.project),
        "monitor":log_summary(args.project/"monitored_metrics.jsonl"),
        "interpretation":"The seed envelope determines allowed powers, but actual Kira symmetry/IBP generation and memory complexity may differ drastically.",
        "recommendation":"Do not use these integral counts as an execution-time estimate. Avoid another heavy Kira job pending target-sector strategy."}
    print(json.dumps(output,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
