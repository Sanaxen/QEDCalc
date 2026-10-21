"""Diagnose whether small raw SYSTEM IDs and large weights share a Kira codec namespace.

Read-only, bounded sampling. Reports codec bits metadata, encode/decode
round-trip examples and error distribution. No physical alias claims.
"""
from __future__ import annotations
import argparse,gzip,json,hashlib
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT as PROJECT
from examples.three_loop_sector203_weight_audit import load_codec
from examples.three_loop_sector203_target_scope_preflight import TARGET

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--codec-file",type=Path,required=True)
    ap.add_argument("--project",type=Path,default=PROJECT)
    ap.add_argument("--max-distinct",type=int,default=5000)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_codec_namespace_probe.json"))
    args=ap.parse_args()
    if not 1<=args.max_distinct<=10000:ap.error("max-distinct must be 1..10000")
    db=args.project/"results/kira.db"
    if not db.is_file():ap.error("Missing Kira db")
    mod=load_codec(args.codec_file.resolve())
    bits,ordering=mod.from_kiradb(str(db))
    codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    files=sorted((args.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    freq=Counter();equations=0
    for file in files:
        with gzip.open(file,"rt",encoding="utf-8") as h:
            while (marker:=h.readline()):
                if marker.strip()!="Eq":raise ValueError("Invalid Eq marker")
                h.readline();n=int(h.readline().strip());equations+=1
                for _ in range(n):
                    t=h.readline().split()
                    if len(t)<4:raise ValueError("Malformed term")
                    freq[(int(t[2]),int(t[3]))]+=1
    if equations!=2678:ap.error(f"Unexpected source, {equations} equations")
    distinct=sorted(freq,key=lambda k:(k[0],k[1]))
    sample=sorted(set(distinct[:min(40,len(distinct))])|set(distinct[-min(40,len(distinct)):])|set(TARGET))
    status=Counter();items=[]
    for key in sample:
        w,s=key
        entry={"key":list(key),"count":freq[key]}
        try:
            indices=tuple(int(i) for i in codec.decode(w))
            entry["indices"]=list(indices)
            entry["computed_sector"]=int(mod.sec_of(indices))
            entry["roundtrip"]=codec.encode(indices)==w
            entry["status"]="roundtrip" if entry["roundtrip"] else "mismatch"
        except Exception as e:
            entry["status"]="decode_error";entry["error"]=str(e)[:240]
        status[entry["status"]]+=1
        items.append(entry)
    report={"summary":{"project":str(args.project.resolve()),"system_equations":equations,
      "distinct_key_count":len(distinct),"minimum_weight":distinct[0][0],
      "maximum_weight":distinct[-1][0],"ordering":ordering,
      "bits_repr":repr(bits)[:350],"db_sha256":hashlib.sha256(db.read_bytes()).hexdigest(),
      "sampled_keys":len(items),"verdict_counts":dict(status),
      "target_decoding_verified":all(i["status"]=="roundtrip" for i in items if tuple(i["key"]) in TARGET),
      "physical_alias_mapping_verified":False,
      "warning":"A successful codec roundtrip checks integer packing only; sector remapping, integral topology and physics remain unverified."},
      "samples":items}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_CODEC_NAMESPACE_PROBE "+json.dumps({**report["summary"],
      "target_samples":[i for i in items if tuple(i["key"]) in TARGET],
      "successful_examples":[i for i in items if i["status"]=="roundtrip"][:5],
      "output":str(args.output)}),flush=True)

if __name__=="__main__":main()
