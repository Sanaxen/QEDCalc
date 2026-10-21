"""Trace VP05 target key namespace in saved 528-row witness, not Kira codec.

Small keys (10,6,5) have not been established as Kira weight values.
Never call WeightCodec.decode on an unproven identifier namespace.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_target_scope_preflight import DEFAULT,TARGET

ROOT=Path("output/three_loop_integral_family_audit")

def read(path):
    raw=path.read_bytes()
    return json.loads(raw.decode("utf-8-sig")),hashlib.sha256(raw).hexdigest()

def summarize(value,limit=16):
    if isinstance(value,dict):
        return {"type":"object","keys":list(value)[:limit],"count":len(value)}
    if isinstance(value,list):
        return {"type":"array","length":len(value),"first_item":str(value[0])[:180] if value else None}
    return {"type":type(value).__name__,"value":str(value)[:180]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--compressed",type=Path,default=DEFAULT)
    p.add_argument("--original",type=Path)
    p.add_argument("--output",type=Path,default=ROOT/"vp05_target_key_namespace_diagnostic.json")
    a=p.parse_args()
    packed,packed_sha=read(a.compressed)
    source_path=a.original or Path(packed["source"])
    if not source_path.is_file():p.error("Missing witness original: "+str(source_path))
    original,source_sha=read(source_path)
    rows=original.get("rows",[])
    if len(rows)!=528 or len(packed.get("rows",[]))!=166:
        p.error("Unexpected equation archive size")
    columns={}
    for rowid,row in enumerate(rows):
        for term in row["terms"]:
            k=tuple(term["key"])
            c=columns.setdefault(k,{"rows":set(),"terms":0})
            c["rows"].add(rowid);c["terms"]+=1
    keys=sorted(columns)
    metadata={k:summarize(v) for k,v in original.items() if k!="rows"}
    records=[]
    for key,coeff in TARGET.items():
        item=columns.get(key)
        record={"key":list(key),"coefficient":coeff,
          "present_in_original":item is not None,
          "original_row_count":len(item["rows"]) if item else 0,
          "original_term_count":item["terms"] if item else 0,
          "sample_original_row_ids":sorted(item["rows"])[:12] if item else [],
          "key_first_element_is_validated_kira_weight":False,
          "physical_integral_mapping_verified":False}
        records.append(record)
    report={"summary":{"original_rows":len(rows),"distinct_column_keys":len(columns),
        "first_component_range":[min(k[0] for k in keys),max(k[0] for k in keys)],
        "first_component_small_ids":sorted({k[0] for k in keys if k[0]<=20}),
        "sector_histogram":dict(sorted(Counter(str(k[1]) for k in keys).items())),
        "original_metadata":metadata,
        "external_codec_decoding_applicable":False,
        "reason":"The source's first key component has not been proven to use the external Kira weight namespace; raw decode attempts fail for keys 10,6,5.",
        "original_sha256":source_sha,"compressed_sha256":packed_sha,
        "alias_mapping_verified":False,"fermat_executed":False,"kira_executed":False},
        "target_keys":records}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("VP05_TARGET_KEY_NAMESPACE "+json.dumps({**report["summary"],"targets":records,"output":str(a.output)},ensure_ascii=False),flush=True)

if __name__=="__main__":main()
