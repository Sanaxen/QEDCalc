"""Audit physical-integral identity of three VP05 target weight/sector keys.

Uses external Kira pyred_weight.py and actual kira.db metadata. Does not
assume recorded proper-subsector rank is its mathematical sector mask.
Requires explicit expected 12-exponent tuples for physical interpretation.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_weight_audit import load_codec
from examples.three_loop_sector203_l2_witness_subset import DEFAULT as L2_PROJECT
from examples.three_loop_sector203_target_scope_preflight import DEFAULT,TARGET

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--codec-file",type=Path,required=True)
    ap.add_argument("--project",type=Path,default=L2_PROJECT)
    ap.add_argument("--compressed",type=Path,default=DEFAULT)
    ap.add_argument("--expect",type=Path,help="JSON with key 'targets': [{key:[weight,sector],exponents:[12 integers]}]")
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_target_codec_alias_audit.json"))
    a=ap.parse_args()
    project=a.project.resolve(); db=project/"results/kira.db"
    if not db.is_file():ap.error("Missing L2 Kira database; pass --project")
    # Reject an unrelated project: the 528-row proof uses this exact witness source.
    import gzip
    from collections import Counter
    files=sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    occurrences=Counter();eq_count=0
    for path in files:
        with gzip.open(path,"rt",encoding="utf-8") as handle:
            while (marker:=handle.readline()):
                if marker.strip()!="Eq":ap.error("Invalid SYSTEM marker")
                handle.readline()
                n=int(handle.readline().strip());eq_count+=1
                for _ in range(n):
                    fields=handle.readline().split()
                    if len(fields)<4:ap.error("Invalid SYSTEM term")
                    key=(int(fields[2]),int(fields[3]))
                    if key in TARGET:occurrences[key]+=1
    if eq_count!=2678 or not all(occurrences[k]>0 for k in TARGET):
        ap.error(f"Wrong source project: equations={eq_count}, target counts={dict(occurrences)}; expected L2 witness source")
    m=load_codec(a.codec_file.resolve())
    bits,ordering=m.from_kiradb(str(db))
    if ordering!=5:ap.error("Unexpected integral ordering")
    codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    raw=a.compressed.read_bytes();eq=json.loads(raw.decode("utf-8-sig"))
    if len(eq["rows"])!=166 or eq.get("type")!="symbolic_exact_linear_combinations":
        ap.error("Unexpected compressed equations")
    available={tuple(t["key"]) for row in eq["rows"] for t in row["terms"]}
    expected={}
    if a.expect:
        spec=json.loads(a.expect.read_text(encoding="utf-8-sig"))
        for item in spec["targets"]:
            k=tuple(item["key"]);v=tuple(item["exponents"])
            if k not in TARGET or len(v)!=12 or k in expected:
                ap.error("Invalid target alias declaration")
            expected[k]=v
    records=[];decode_ok=True;alias_ok=bool(a.expect) and set(expected)==set(TARGET)
    decoded_ids=[]
    for key,coeff in TARGET.items():
        weight,recorded_sector=key
        record={"key":list(key),"target_coefficient":coeff,
                "present_in_compressed_equations":key in available}
        try:
            indices=tuple(int(i) for i in codec.decode(weight))
            computed_sector=int(m.sec_of(indices))
            roundtrip=codec.encode(indices)==weight
            record.update({"decoded_exponents":list(indices),"decoded_sector_mask":computed_sector,
                "recorded_sector":recorded_sector,
                "sector_label_matches_decoded_mask":recorded_sector==computed_sector,
                "codec_roundtrip":roundtrip})
            decoded_ids.append(indices)
            decode_ok &= roundtrip and key in available
            if key in expected:
                match=indices==expected[key] and int(m.sec_of(expected[key]))==computed_sector
                record["explicit_alias_match"]=match
                alias_ok &= match
            else:record["explicit_alias_match"]=None
        except Exception as exc:
            record["error"]=str(exc)[:300];decode_ok=False;alias_ok=False
        records.append(record)
    # Do not infer sector-rank remapping from just three keys.
    report={"summary":{"ordering":ordering,"topsector":203,"source_project":str(project),
        "system_equations":eq_count,"raw_target_occurrences":{str(k):occurrences[k] for k in TARGET},
        "target_keys":len(TARGET),"codec_roundtrip_and_source_presence":decode_ok,
        "all_explicit_aliases_verified":alias_ok,
        "alias_expectations_supplied":bool(a.expect),
        "distinct_decoded_integrals":len(set(decoded_ids)),
        "integral_alias_mapping_verified":alias_ok and decode_ok,
        "warning":"Codec decoding is not a verification that a declared physical topology has the expected propagator ordering or momentum routing. Proper subsector recorded ranks may differ from mathematical bitmask.",
        "compressed_sha256":hashlib.sha256(raw).hexdigest(),
        "codec_sha256":hashlib.sha256(a.codec_file.read_bytes()).hexdigest(),
        "db_sha256":hashlib.sha256(db.read_bytes()).hexdigest(),
        "fermat_executed":False,"kira_executed":False},"targets":records}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_TARGET_CODEC_ALIAS_AUDIT "+json.dumps({**report["summary"],"target_details":records,"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
