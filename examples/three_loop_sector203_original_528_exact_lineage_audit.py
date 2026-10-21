"""Exact rational audit of compressed VP05 rows back to 528 original IBP rows.

Checks each compressed row's declared weighted original equations in Q(z,d),
column by column. Pilot defaults to five groups; 166 checks complete lineage.
This does not verify the meaning of integral aliases/weight-code identifiers.
"""
from __future__ import annotations
import argparse,hashlib,json,time
from collections import defaultdict,Counter
from fractions import Fraction
from pathlib import Path
from examples.three_loop_sector203_target_symbolic_compression import DEFAULT_GROUPS,sum_exact
from examples.three_loop_sector203_target_scope_preflight import DEFAULT

ROOT=Path("output/three_loop_integral_family_audit")

def load(path):
    raw=path.read_bytes()
    return json.loads(raw.decode("utf-8-sig")),hashlib.sha256(raw).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--compressed",type=Path,default=DEFAULT)
    ap.add_argument("--groups",type=Path,default=DEFAULT_GROUPS)
    ap.add_argument("--original",type=Path,help="Override compressed archive's original source path")
    ap.add_argument("--max-groups",type=int,default=5)
    ap.add_argument("--max-source-terms",type=int,default=20000)
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_original_528_exact_lineage_audit.json")
    a=ap.parse_args()
    if not 1<=a.max_groups<=166 or not 1<=a.max_source_terms<=20000:ap.error("Bad caps")
    packed,packed_sha=load(a.compressed)
    groups,groups_sha=load(a.groups)
    original_path=a.original or Path(packed["source"])
    if not original_path.is_file():
        ap.error("Missing original 528-row witness file: "+str(original_path))
    source,source_sha=load(original_path)
    compressed_rows=packed.get("rows",[])
    group_rows=groups.get("proportional_classes",[])
    originals=source.get("rows",[])
    if (packed.get("type")!="symbolic_exact_linear_combinations"
        or len(compressed_rows)!=166 or len(group_rows)!=166 or len(originals)!=528):
        ap.error("Unexpected original/group/compressed archive shape")
    original_terms=sum(len(r["terms"]) for r in originals)
    if original_terms>a.max_source_terms:
        ap.error("Original source input exceeds term cap")
    touched=set()
    for i,(row,g) in enumerate(zip(compressed_rows,group_rows)):
        weights={int(w["row"]):Fraction(w["ratio"]) for w in g["ratios_to_representative"]}
        if (row["group"]!=i or set(weights)!=set(g["rows"])
            or sorted(weights)!=row["original_rows"]
            or row["representative"]!=g["representative"]
            or weights.get(int(g["representative"]))!=1):
            ap.error("Inconsistent group representation "+str(i))
        if set(weights)&touched:ap.error("Overlapping original rows")
        touched.update(weights)
    if touched!=set(range(528)):
        ap.error("528 original rows not partitioned by groups")
    verified=[];tally=Counter()
    for i in range(a.max_groups):
        started=time.perf_counter()
        row=compressed_rows[i]
        group=group_rows[i]
        weights={int(w["row"]):Fraction(w["ratio"]) for w in group["ratios_to_representative"]}
        summands=defaultdict(list)
        for original_id,weight in weights.items():
            for term in originals[original_id]["terms"]:
                summands[tuple(term["key"])].append((weight,term["coefficient"]))
        packed_terms=defaultdict(list)
        for term in row["terms"]:
            packed_terms[tuple(term["key"])].append((Fraction(1),term["coefficient"]))
        failures=[]
        for key in sorted(set(summands)|set(packed_terms)):
            delta=sum_exact(summands.get(key,[])+[(-fac,expr) for fac,expr in packed_terms.get(key,[])])
            if delta!=0:failures.append({"column":list(key),"residual":str(delta)[:250]})
        status="exact_match" if not failures else "exact_mismatch"
        tally[status]+=1
        record={"group":i,"original_rows":len(weights),"columns":len(set(summands)|set(packed_terms)),
            "status":status,"failures":failures[:8],"seconds":round(time.perf_counter()-started,3)}
        verified.append(record)
        print("VP05_ORIGINAL_LINEAGE_GROUP "+json.dumps({k:v for k,v in record.items() if k!="failures"}),flush=True)
        if failures:break
    complete=(len(verified)==166 and all(r["status"]=="exact_match" for r in verified))
    report={"summary":{"original_rows":528,"compressed_rows":166,
      "group_partition_exact":True,"groups_checked":len(verified),"group_verdicts":dict(tally),
      "exact_lineage_verified":complete,"integral_alias_mapping_verified":False,
      "compressed_sha256":packed_sha,"groups_sha256":groups_sha,"original_sha256":source_sha,
      "original_source":str(original_path),"original_terms":original_terms,
      "fermat_executed":False},"groups":verified}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_ORIGINAL_528_LINEAGE "+json.dumps({**report["summary"],"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
