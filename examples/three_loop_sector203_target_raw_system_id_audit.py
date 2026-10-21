"""Check small VP05 witness column IDs directly against saved Kira SYSTEM terms.

Never decode a numeric key as a Kira weight until its namespace is established.
This is a source-origin diagnostic, not physical alias verification.
"""
from __future__ import annotations
import argparse,gzip,json,hashlib
from collections import Counter,defaultdict
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,RUN
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",type=Path,default=ROOT/"output"/RUN)
    ap.add_argument("--compressed",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_target_raw_system_id_audit.json"))
    a=ap.parse_args()
    source=json.loads(a.compressed.read_text(encoding="utf-8-sig"))
    original=Path(source["source"])
    if not original.is_file():ap.error("Saved 528-row witness missing")
    witness=json.loads(original.read_text(encoding="utf-8-sig"))
    if len(witness.get("rows",[]))!=528:ap.error("Unexpected witness length")
    folder=a.project/"tmp/VP05_full"
    files=sorted(folder.glob("SYSTEM_VP05_full_*.gz"))
    if not files:ap.error("No saved Kira SYSTEM files in "+str(folder))
    raw=defaultdict(lambda:{"count":0,"files":set(),"sample_coefficients":[],"sample_equations":[]})
    total=0;terms=0
    for file in files:
        with gzip.open(file,"rt",encoding="utf-8") as handle:
            while (line:=handle.readline()):
                if line.strip()!="Eq":raise ValueError("Unexpected SYSTEM marker in "+str(file))
                head=handle.readline().strip()
                n=int(handle.readline().strip()); total+=1
                for _ in range(n):
                    fields=handle.readline().split()
                    if len(fields)<4:raise ValueError("Malformed SYSTEM term")
                    weight,sector=int(fields[2]),int(fields[3]);terms+=1
                    key=(weight,sector)
                    if key in TARGET or weight<=20:
                        item=raw[key];item["count"]+=1;item["files"].add(file.name)
                        if len(item["sample_coefficients"])<4:item["sample_coefficients"].append(fields[1])
                        if len(item["sample_equations"])<4:item["sample_equations"].append({"head":head,"fields":fields[:4]})
    witness_counts=Counter(tuple(term["key"]) for row in witness["rows"] for term in row["terms"])
    records=[]
    for key in sorted(set(TARGET)|set(raw)):
        item=raw.get(key)
        records.append({"key":list(key),"is_target":key in TARGET,
          "original_witness_terms":witness_counts.get(key,0),
          "raw_system_terms":item["count"] if item else 0,
          "raw_system_files":sorted(item["files"]) if item else [],
          "raw_coefficients":item["sample_coefficients"] if item else [],
          "raw_equation_samples":item["sample_equations"] if item else []})
    result={"summary":{"system_files":len(files),"system_equations":total,"system_terms":terms,
      "original_witness_rows":528,"small_id_records":len(records),
      "targets_present_in_raw_system":all(key in raw for key in TARGET),
      "physical_aliases_verified":False,
      "warning":"A raw SYSTEM key occurrence establishes transcription/namespace origin, not a 12-exponent physical-integral interpretation.",
      "original_sha256":hashlib.sha256(original.read_bytes()).hexdigest()},
      "records":records}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("VP05_RAW_SYSTEM_ID_AUDIT "+json.dumps({**result["summary"],
        "target_records":[r for r in records if r["is_target"]],"output":str(a.output)},ensure_ascii=False),flush=True)

if __name__=="__main__":main()
