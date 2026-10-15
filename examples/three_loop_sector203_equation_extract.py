"""Read-only extraction of saved SYSTEM equations containing sector-203 candidate weights."""
from __future__ import annotations
import argparse
import gzip
import json
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT, RUN, CANDIDATE, load_codec, parse_file_integrals

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--codec-file",type=Path,required=True)
    p.add_argument("--project",type=Path,default=ROOT/"output"/RUN)
    p.add_argument("--max-examples",type=int,default=3)
    args=p.parse_args()
    project=args.project.resolve()
    codec_module=load_codec(args.codec_file.resolve())
    bits,ordering=codec_module.from_kiradb(str(project/"results/kira.db"))
    if ordering!=5:
        p.error("Expected ordering=5")
    codec=codec_module.WeightCodec(12,bits,ordering,topsectors=[203])
    candidates=[x for x in parse_file_integrals(CANDIDATE) if codec_module.sec_of(x)==203]
    if len(candidates)!=4:
        p.error("Expected four sector-203 candidates")
    weights={codec.encode(x):i+1 for i,x in enumerate(candidates)}
    count={str(i):{"equations":0,"as_head":0,"examples":[]} for i in range(1,5)}
    total=0
    for file in sorted((project/"tmp/VP05_full").glob("SYSTEM_*.gz")):
        with gzip.open(file,"rt",encoding="utf-8") as fh:
            while (marker:=fh.readline()):
                if marker.strip()!="Eq":
                    p.error("Malformed equation marker")
                head=int(fh.readline().strip())
                n=int(fh.readline().strip())
                terms=[fh.readline().split() for _ in range(n)]
                total+=1
                hits=set()
                for t in terms:
                    if len(t)<4:
                        p.error("Malformed equation term")
                    if int(t[3])==203 and int(t[2]) in weights:
                        hits.add(weights[int(t[2])])
                for i in hits:
                    item=count[str(i)]
                    item["equations"]+=1
                    if head==codec.encode(candidates[i-1]):
                        item["as_head"]+=1
                    if len(item["examples"])<args.max_examples:
                        item["examples"].append({"file":file.name,"head_weight":head,
                          "terms":[{"coefficient":t[1],"weight":int(t[2]),"sector":int(t[3])} for t in terms]})
    print(json.dumps({"scope":"read-only selected equations, not all generated IBPs",
      "project":str(project),"scanned_equations":total,
      "candidates":[{"index":i,"integral":"VP05_full["+",".join(map(str,candidates[i-1]))+"]",
        "weight":codec.encode(candidates[i-1]),**count[str(i)]} for i in range(1,5)],
      "limitation":"coefficient relations not solved; stored head is not necessarily a completed reduction; no rank/closure proof"},
      indent=2,ensure_ascii=False))
if __name__=="__main__":
    main()
