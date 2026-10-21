"""Bounded, read-only diagnosis of tiny Kira SYSTEM IDs and codec internals.

Inspect source of the external decode method and compare small vs normal IDs.
Does not alter or vendor the GPL external codec.
"""
from __future__ import annotations
import argparse,inspect,json,gzip,hashlib
from collections import Counter,defaultdict
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_weight_audit import load_codec

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--codec-file",type=Path,required=True)
    ap.add_argument("--project",type=Path,default=DEFAULT)
    ap.add_argument("--small-limit",type=int,default=100)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_weight_codec_diagnostic.json"))
    a=ap.parse_args()
    if not 1<=a.small_limit<=10000:ap.error("Invalid small-limit")
    m=load_codec(a.codec_file.resolve())
    db=a.project/"results/kira.db"
    bits,ordering=m.from_kiradb(str(db))
    codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    counts=Counter();locations=defaultdict(list);eq_count=0
    for file in sorted((a.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        with gzip.open(file,"rt",encoding="utf-8") as inp:
            while (line:=inp.readline()):
                if line.strip()!="Eq":raise ValueError("Malformed SYSTEM")
                eqid=inp.readline().strip();n=int(inp.readline().strip());eq_count+=1
                for j in range(n):
                    t=inp.readline().split()
                    if len(t)<4:raise ValueError("Malformed term")
                    k=(int(t[2]),int(t[3]))
                    counts[k]+=1
                    if k[0]<=a.small_limit and len(locations[k])<3:
                        locations[k].append({"file":file.name,"eqid":eqid,"term_index":j,"coefficient":t[1]})
    if eq_count!=2678:ap.error("Unexpected project: not 2678 SYSTEM equations")
    samples=[]
    for key in sorted(k for k in counts if k[0]<=a.small_limit):
        entry={"key":list(key),"count":counts[key],"occurrences":locations[key]}
        try:
            powers=list(codec.decode(key[0]));entry["decoded"]=powers
            entry["roundtrip"]=codec.encode(powers)==key[0]
        except Exception as e:entry["error"]=str(e)
        samples.append(entry)
    def method_info(method):
        try:
            lines,first=inspect.getsourcelines(method)
            relevant=[{"line":first+i,"text":line.strip()[:160]} for i,line in enumerate(lines)
                if any(x in line for x in ("ppw","range","decode","component","bits","raise"))]
            return {"source_file":inspect.getsourcefile(method),"first_line":first,
                "relevant_source_lines":relevant[:45]}
        except (OSError,TypeError) as e:return {"inspection_error":str(e)}
    report={"system_equations":eq_count,"total_distinct_keys":len(counts),
       "small_limit":a.small_limit,"small_pairs":samples,
       "bits":repr(bits),"ordering":ordering,
       "decode_method":method_info(m.WeightCodec.decode),
       "encode_method":method_info(m.WeightCodec.encode),
       "codec_sha256":hashlib.sha256(a.codec_file.read_bytes()).hexdigest(),
       "db_sha256":hashlib.sha256(db.read_bytes()).hexdigest(),
       "physical_alias_mapping_verified":False,
       "note":"Only inspection. No mapping inferred from low numeric IDs."}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("VP05_SMALL_WEIGHT_DIAGNOSTIC "+json.dumps({k:v for k,v in report.items()
      if k not in ("small_pairs",)}|{"small_pairs":samples[:50],"output":str(a.output)},ensure_ascii=False),flush=True)

if __name__=="__main__":main()
