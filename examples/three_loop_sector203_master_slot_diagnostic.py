"""Inspect whether small SYSTEM integral identifiers denote Kira master slots.

Do not infer numeric slot-to-physical-integral mapping from list order alone.
Checks saved master listing and codec-encoded master integrals. Read-only.
"""
from __future__ import annotations
import argparse, gzip, json, hashlib, re
from pathlib import Path
from collections import Counter
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_weight_audit import load_codec,parse_file_integrals

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--codec-file",type=Path,required=True)
    ap.add_argument("--project",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_master_slot_diagnostic.json"))
    a=ap.parse_args()
    db=a.project/"results/kira.db"
    master_file=a.project/"results/VP05_full/masters"
    if not db.is_file() or not master_file.is_file():ap.error("Missing Kira DB or master list")
    module=load_codec(a.codec_file.resolve())
    bits,ordering=module.from_kiradb(str(db))
    codec=module.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    masters=parse_file_integrals(master_file)
    if not masters:ap.error("No masters found in Kira result")
    for index in masters:
        if len(index)!=12:ap.error("Unexpected master index tuple length")
    counts=Counter()
    heads=Counter()
    eq_count=0
    for path in sorted((a.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        with gzip.open(path,"rt",encoding="utf-8") as f:
            while (marker:=f.readline()):
                if marker.strip()!="Eq":raise ValueError("Bad SYSTEM marker")
                heads[int(f.readline().strip())]+=1
                n=int(f.readline().strip());eq_count+=1
                for _ in range(n):
                    fields=f.readline().split()
                    if len(fields)<4:raise ValueError("Malformed SYSTEM term")
                    counts[(int(fields[2]),int(fields[3]))]+=1
    if eq_count!=2678:ap.error("Wrong source project")
    entries=[]
    for ordinal,index in enumerate(masters,1):
        try:
            weight=int(codec.encode(index))
            sector=int(module.sec_of(index))
            entries.append({"list_position_one_based":ordinal,"exponents":list(index),
               "encoded_weight":weight,"mathematical_sector_mask":sector,
               "appears_as_raw_head":weight in heads,
               "recorded_sector_labels_at_encoded_weight":sorted(s for w,s in counts if w==weight)})
        except Exception as e:
            entries.append({"list_position_one_based":ordinal,"exponents":list(index),"encode_error":str(e)})
    small=[{"key":[w,s],"occurrences":n} for (w,s),n in sorted(counts.items())
           if w<=max(20,len(masters))]
    result={"master_list_count":len(masters),"master_list_sha256":hashlib.sha256(master_file.read_bytes()).hexdigest(),
      "system_equations":eq_count,"small_raw_pairs":small,"masters":entries,
      "small_ids_fit_master_slot_range":all(1<=item["key"][0]<=len(masters) for item in small),
      "master_slot_mapping_verified":False,
      "physical_alias_mapping_verified":False,
      "warning":"A contiguous 1..N small-ID range and N masters is only a hypothesis of slot semantics. Master list position is not a proven slot index."}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("VP05_MASTER_SLOT_DIAGNOSTIC "+json.dumps({**{k:v for k,v in result.items() if k not in ("masters","small_raw_pairs")},
      "small_raw_pairs":small,"master_samples":entries[:16],"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
