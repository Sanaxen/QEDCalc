"""Verify original two-term equalities and decode their large Kira integral weights.

Read-only. A two-term equality is proven only when raw coefficients are exactly
+1 and -1, the source term keys are distinct, and the codec round-trips.
Only such entries are promoted to direct small-ID-to-exponents aliases.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json
from collections import defaultdict
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT as PROJECT
from examples.three_loop_sector203_weight_audit import load_codec
from examples.three_loop_sector203_target_scope_preflight import TARGET

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--codec-file",type=Path,required=True)
    p.add_argument("--project",type=Path,default=PROJECT)
    p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_id_exact_alias_bridges.json"))
    a=p.parse_args();root=a.project.resolve()
    db=root/"results/kira.db"
    if not db.is_file():p.error("Missing Kira database")
    m=load_codec(a.codec_file.resolve())
    bits,ordering=m.from_kiradb(str(db))
    if ordering!=5:p.error("Unexpected ordering")
    codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    found=defaultdict(list)
    equations=0
    for path in sorted((root/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        with gzip.open(path,"rt",encoding="utf-8") as h:
            while (marker:=h.readline()):
                if marker.strip()!="Eq":raise ValueError("Unexpected marker")
                head=h.readline().strip();n=int(h.readline().strip());equations+=1
                terms=[]
                for _ in range(n):
                    fields=h.readline().split()
                    if len(fields)<4:raise ValueError("Invalid SYSTEM term")
                    terms.append((tuple(map(int,fields[2:4])),fields[1]))
                if len(terms)!=2:continue
                small=[(k,c) for k,c in terms if 1<=k[0]<=10]
                large=[(k,c) for k,c in terms if k[0]>10]
                if len(small)!=1 or len(large)!=1:continue
                sk,sc=small[0];lk,lc=large[0]
                if (sc,lc) not in (("1","-1"),("-1","1")):continue
                record={"small_key":list(sk),"large_key":list(lk),
                    "source_file":path.name,"equation_id":head,
                    "source_coefficients":[sc,lc]}
                try:
                    decoded=tuple(map(int,codec.decode(lk[0])))
                    if len(decoded)!=12 or codec.encode(decoded)!=lk[0]:
                        raise ValueError("Codec roundtrip mismatch")
                    record["decoded_exponents"]=list(decoded)
                    record["decoded_mathematical_sector"]=int(m.sec_of(decoded))
                    record["codec_roundtrip_verified"]=True
                except (ValueError,AssertionError) as e:
                    record["codec_roundtrip_verified"]=False;record["decode_error"]=str(e)
                found[sk].append(record)
    if equations!=2678:p.error("Wrong source equation count")
    results=[]
    for key,items in sorted(found.items()):
        decoded={tuple(i["decoded_exponents"]) for i in items if i.get("codec_roundtrip_verified")}
        all_decoded=all(i.get("codec_roundtrip_verified") for i in items)
        consistent=all_decoded and len(decoded)>=1
        results.append({"small_key":list(key),"exact_unit_two_term_bridges":len(items),
            "all_decoded":all_decoded,"all_bridges_decoded":consistent,"different_but_equivalent_exponent_tuples":len(decoded),
            "alias_exponents":list(sorted(decoded)[0]) if consistent else None,
            "bridges":items})
    bykey={tuple(x["small_key"]):x for x in results}
    target_results=[]
    for k in TARGET:
        v=bykey.get(k)
        target_results.append({"key":list(k),
            "direct_unit_bridge_alias_verified":bool(v and v["all_bridges_decoded"]),
            "exponents":v["alias_exponents"] if v else None,
            "bridge_count":v["exact_unit_two_term_bridges"] if v else 0})
    result={"system_equations":equations,"ordering":ordering,
        "codec_sha256":hashlib.sha256(a.codec_file.read_bytes()).hexdigest(),
        "db_sha256":hashlib.sha256(db.read_bytes()).hexdigest(),
        "target_results":target_results,"small_id_results":results,
        "all_three_target_aliases_verified":all(r["direct_unit_bridge_alias_verified"] for r in target_results),
        "physical_propagator_mapping_verified":False,
        "warning":"Raw SYSTEM two-term equalities and codec round trips are exact for the stored encoding; topology/denominator definitions require a separate check."}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("VP05_EXACT_ALIAS_BRIDGES "+json.dumps({**{k:v for k,v in result.items() if k!="small_id_results"},
        "small_id_summary":[{k:v for k,v in item.items() if k!="bridges"} for item in results],
        "output":str(a.output)}),flush=True)

if __name__=="__main__":main()
