"""Audit VP05 target keys against raw Kira SYSTEM equations and project config.

The target keys are copied verbatim from a truncated L2 SYSTEM project.
This verifies source provenance but does not infer physical integral aliases.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json
from pathlib import Path
from collections import Counter
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT as PACKED

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,default=DEFAULT)
    p.add_argument("--compressed",type=Path,default=PACKED)
    p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_target_raw_system_audit.json"))
    a=p.parse_args()
    packed=json.loads(a.compressed.read_text(encoding="utf-8-sig"))
    source=Path(packed["source"])
    if not source.is_file():p.error("Original witness missing: "+str(source))
    original=json.loads(source.read_text(encoding="utf-8-sig"))
    witness=original["rows"]
    if len(witness)!=528:p.error("Expected 528 witness rows")
    files=sorted((a.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    if not files:p.error("No raw SYSTEM files at "+str(a.project))
    matches=0;counter=Counter();found={key:[] for key in TARGET}
    index=0;next_witness=0;errors=[]
    for path in files:
        with gzip.open(path,"rt",encoding="utf-8") as f:
            while line:=f.readline():
                if line.strip()!="Eq":raise RuntimeError("Bad SYSTEM marker")
                eqid=f.readline().strip()
                length=int(f.readline().strip())
                terms=[]
                for _ in range(length):
                    fields=f.readline().split()
                    if len(fields)<4:raise RuntimeError("Bad SYSTEM term")
                    key=(int(fields[2]),int(fields[3]))
                    terms.append({"key":list(key),"coefficient":fields[1]})
                    if key in found:found[key].append({"row_index":index,"file":path.name,"equation_id":eqid})
                if next_witness<len(witness) and index==witness[next_witness]["row_index"]:
                    w=witness[next_witness]
                    if w["file"]!=path.name or str(w["equation_id"])!=eqid or w["terms"]!=terms:
                        errors.append({"row_index":index,"reason":"Raw SYSTEM mismatch with saved witness"})
                    else:matches+=1
                    next_witness+=1
                index+=1
    if index!=2678 or matches!=528 or errors:
        raise RuntimeError("Raw SYSTEM replay failed: "+json.dumps({"rows":index,"matches":matches,"errors":errors[:3]}))
    for key,refs in found.items():counter[str(key)]=len(refs)
    report={"summary":{"raw_system_equations":index,"witness_rows_matched_byte_text":matches,
      "source_target_presence":all(found.values()),
      "target_raw_occurrences":dict(counter),
      "source_project":str(a.project),
      "integral_alias_mapping_verified":False,
      "witness_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
      "fermat_executed":False,"kira_executed":False},
      "target_occurrence_samples":{str(key):refs[:10] for key,refs in found.items()}}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_RAW_SYSTEM_TARGET_AUDIT "+json.dumps({**report["summary"],"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
