"""Read-only structural preflight for symbolic candidate-4 elimination.

Reports the least complex saved exact equations involving target alias 10,
and graph-neighbourhood sizes. Does not perform Kira or symbolic elimination.
"""
from __future__ import annotations
import argparse
import gzip
from collections import Counter, defaultdict
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT

DEFAULT = ROOT / "output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734"
TARGET=(10,203)
MASTERS={(5,201),(6,203),(7,203),(8,203),(9,203)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",type=Path,default=DEFAULT)
    ap.add_argument("--show",type=int,default=5)
    args=ap.parse_args()
    paths=sorted((args.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    if len(paths)!=14:ap.error(f"expected 14 SYSTEM files, got {len(paths)}")
    edges=defaultdict(set)
    target_equations=[]
    nrows=0
    for path in paths:
        with gzip.open(path,"rt",encoding="utf8") as f:
            while (marker:=f.readline()):
                if marker.strip()!="Eq": raise ValueError("malformed SYSTEM record")
                label=f.readline().strip()
                n=int(f.readline().strip())
                terms=[]
                for _ in range(n):
                    parts=f.readline().split()
                    if len(parts)<4:raise ValueError("malformed SYSTEM term")
                    terms.append(((int(parts[2]),int(parts[3])),parts[1]))
                keys=set(k for k,c in terms)
                for k in keys:edges[k].update(keys-{k})
                if TARGET in keys:
                    target_equations.append((n,len(keys-MASTERS-{TARGET}),path.name,label,terms))
                nrows+=1
    print(f"EQUATIONS={nrows} TARGET_EQUATIONS={len(target_equations)} DISTINCT_COLUMNS={len(edges)}")
    print("LOWEST_COMPLEXITY_TARGET_EQUATIONS:")
    for n,nonmaster,filename,label,terms in sorted(target_equations,key=lambda x:(x[1],x[0]))[:args.show]:
        print(f"  file={filename} eq={label} total_terms={n} other_nonmaster_columns={nonmaster}")
        for key,cf in terms:print(f"    {key}  {cf}")
    seen={TARGET}
    frontier={TARGET}
    for distance in range(1,4):
        following=set()
        for x in frontier:following.update(edges[x])
        following-=seen
        seen.update(following)
        frontier=following
        print(f"NEIGHBOURHOOD_DISTANCE={distance} NEW_COLUMNS={len(frontier)} TOTAL_COLUMNS={len(seen)}")
        if not frontier:break
    print("NEXT=Find a small exact equation subset, or reconstruct coefficient C(z,d) by sampled evaluations; this scan alone is not a symbolic reduction.")

if __name__=="__main__":main()
