"""Locate the exporter of the saved 528-row VP05 witness and audit raw-key overlap.

No conclusions from matching *counts* alone: literal key matches and exact row
comparison require correct source lineage. This emits code locations to inspect.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_target_scope_preflight import DEFAULT,TARGET
from examples.three_loop_sector203_weight_audit import ROOT

NEEDLES=("vp05_candidate4_witness","equations.json","SYSTEM_VP05_full_",
         "original_rows","selected SYSTEM","witness")
SUFFIXES={".py",".bat",".ps1",".md",".yaml",".yml",".json"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--compressed",type=Path,default=DEFAULT)
    ap.add_argument("--max-source-files",type=int,default=10000)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_witness_producer_trace.json"))
    a=ap.parse_args()
    base=a.root.resolve()
    packed=json.loads(a.compressed.read_text(encoding="utf-8-sig"))
    origin=Path(packed["source"])
    if not origin.is_file():ap.error("Original witness missing: "+str(origin))
    original_raw=origin.read_bytes();data=json.loads(original_raw.decode("utf-8-sig"))
    if len(data.get("rows",[]))!=528:ap.error("Expected 528 witness rows")
    excludes={".git",".venv","venv","node_modules","output","__pycache__","build","dist"}
    found=[];files_checked=0;too_many=False
    for path in base.rglob("*"):
        if any(part in excludes for part in path.relative_to(base).parts[:-1]):continue
        if not path.is_file() or path.suffix.lower() not in SUFFIXES:continue
        files_checked+=1
        if files_checked>a.max_source_files:too_many=True;break
        try:
            if path.stat().st_size>1_500_000:continue
            lines=path.read_text(encoding="utf-8-sig",errors="replace").splitlines()
        except OSError:continue
        hits=[]
        for number,line in enumerate(lines,1):
            lowered=line.lower()
            if any(needle.lower() in lowered for needle in NEEDLES):
                hits.append({"line":number,"text":line.strip()[:230]})
        if hits:
            found.append({"path":str(path.relative_to(base)),"hits":hits[:20],"hit_count":len(hits)})
    found.sort(key=lambda f:(
        0 if "candidate4_witness" in str(f["hits"]).lower() else 1,
        0 if f["path"].endswith(".py") else 1,
        f["path"]))
    witness_columns=Counter(tuple(t["key"]) for row in data["rows"] for t in row["terms"])
    report={"summary":{"original_source":str(origin),
       "original_sha256":hashlib.sha256(original_raw).hexdigest(),
       "source_files_inspected":files_checked,
       "source_search_truncated":too_many,"source_files_with_matches":len(found),
       "target_key_occurrences":{str(k):witness_columns[k] for k in TARGET},
       "origin_to_raw_SYSTEM_mapping_verified":False,
       "physical_alias_mapping_verified":False,
       "warning":"Identifies potential producer code; search matches are not proof of provenance."},
       "source_candidates":found}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("VP05_WITNESS_PRODUCER_TRACE "+json.dumps({**report["summary"],
          "top_source_candidates":found[:18],"output":str(a.output)},ensure_ascii=False),flush=True)

if __name__=="__main__":main()
