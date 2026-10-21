"""Check source evidence for small VP05 SYSTEM weights without guessing aliases.

Kira permits manually assigned integral weights and changes during reduction.
Inventory the actual job/config and preferred master files; compare the small
weights across SYSTEM sectors. Read-only and bounded.
"""
from __future__ import annotations
import argparse,gzip,json,re
from collections import defaultdict
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_system_id_source_audit.json"))
    a=ap.parse_args();root=a.project.resolve()
    records=defaultdict(lambda:{"count":0,"sectors":set(),"files":set(),"equation_ids":[]})
    eq=0
    for f in sorted((root/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        with gzip.open(f,"rt",encoding="utf-8") as stream:
            while (marker:=stream.readline()):
                if marker.strip()!="Eq":raise ValueError("Malformed SYSTEM marker")
                eid=stream.readline().strip();n=int(stream.readline().strip());eq+=1
                for _ in range(n):
                    fields=stream.readline().split()
                    if len(fields)<4:raise ValueError("Malformed SYSTEM term")
                    w,s=int(fields[2]),int(fields[3])
                    if 0<=w<=20:
                        entry=records[w];entry["count"]+=1;entry["sectors"].add(s);entry["files"].add(f.name)
                        if len(entry["equation_ids"])<5:entry["equation_ids"].append(eid)
    if eq!=2678:ap.error("Unexpected SYSTEM count")
    found=[];checked=0
    for folder in (root/"config",root/"results/VP05_full"):
        if not folder.is_dir():continue
        for f in folder.rglob("*"):
            if not f.is_file() or f.suffix in (".db",".gz") or f.stat().st_size>2_000_000:continue
            checked+=1
            if checked>300:break
            try:lines=f.read_text(encoding="utf-8",errors="replace").splitlines()
            except OSError:continue
            hits=[{"line":i,"text":line.strip()[:220]} for i,line in enumerate(lines,1)
                if re.search(r"preferred_masters|master|weight|basis|select_integrals|input_system|run_pyred|back_substitution",line,re.I)]
            if hits:found.append({"file":str(f.relative_to(root)),"matched_lines":hits[:25],"hit_count":len(hits)})
    small=[{"weight":w,"count":v["count"],"sectors":sorted(v["sectors"]),
            "files":sorted(v["files"]),"sample_equation_ids":v["equation_ids"]} for w,v in sorted(records.items())]
    out={"project":str(root),"system_equations":eq,"small_weights":small,
         "candidate_files_inspected":min(checked,300),"configuration_evidence":found[:40],
         "small_id_mapping_verified":False,
         "hypotheses":["explicit integral weight assignment","temporary or preferred basis numbering","other Kira-internal identifier"],
         "caution":"None of the hypotheses is established by numeric IDs alone; do not map to master file ordinal."}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("VP05_SMALL_SYSTEM_ID_SOURCE "+json.dumps({**out,"output":str(a.output)},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
