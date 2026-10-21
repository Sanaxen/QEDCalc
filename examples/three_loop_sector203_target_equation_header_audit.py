"""Audit mandatory VP05 integral weights as equation headers, not only SYSTEM terms.

Kira may place selected integrals in equation heads or symmetry-normalized
forms. This audit is read-only and never guesses any symmetry mapping.
"""
from __future__ import annotations
import argparse,collections,gzip,json,hashlib
from pathlib import Path
from examples.three_loop_sector203_weight_audit import load_codec,parse_file_integrals
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--codec-file",type=Path,default=Path("output/tools/pyred_weight.py"))
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_target_equation_header_audit.json"))
 a=p.parse_args()
 mandatory=a.project/"mandatory_provisional64_sector203.txt"
 db=a.project/"results/kira.db"
 m=load_codec(a.codec_file)
 bits,ordering=m.from_kiradb(str(db))
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 vectors=parse_file_integrals(mandatory)
 if len(vectors)!=5:raise RuntimeError("Expected five mandatory targets")
 targets={}
 for powers in vectors:
  weight=int(codec.encode(powers))
  if tuple(codec.decode(weight))!=powers:raise RuntimeError("Codec roundtrip failed")
  targets[weight]={"integral":"VP05_full["+",".join(map(str,powers))+"]",
    "weight":weight,"codec_sector":int(m.sec_of(powers)),
    "header_occurrences":[],"term_occurrences":[]}
 counts=collections.Counter()
 for file in sorted((a.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  with gzip.open(file,"rt",encoding="utf-8",errors="replace") as f:
   ordinal=0
   while marker:=f.readline():
    if marker.strip()!="Eq":raise RuntimeError("Bad SYSTEM record")
    ordinal+=1;counts["equations"]+=1
    head=int(f.readline().strip());n=int(f.readline().strip())
    if head in targets:
     targets[head]["header_occurrences"].append({"file":file.name,"equation_ordinal":ordinal,"term_count":n})
    for j in range(n):
     term=f.readline().split()
     if len(term)<4:raise RuntimeError("Malformed term")
     counts["terms"]+=1
     weight,sector=int(term[2]),int(term[3])
     if weight in targets:
      targets[weight]["term_occurrences"].append({"file":file.name,"equation_ordinal":ordinal,
        "term_index":j,"sector":sector})
 records=[]
 for target in targets.values():
  records.append({**target,
    "header_count":len(target["header_occurrences"]),
    "term_count":len(target["term_occurrences"]),
    "header_occurrences":target["header_occurrences"][:12],
    "term_occurrences":target["term_occurrences"][:12]})
 jobs=a.project/"jobs.yaml";job_text=jobs.read_text(encoding="utf-8-sig")
 report={"status":"HEADER_AND_TERM_COVERAGE_ONLY",
   "project":str(a.project),"source_equations":counts["equations"],"source_terms":counts["terms"],
   "mandatory_sha256":hashlib.sha256(mandatory.read_bytes()).hexdigest(),
   "jobs_sha256":hashlib.sha256(jobs.read_bytes()).hexdigest(),
   "jobs_declares_mandatory_list":"select_mandatory_list:" in job_text and mandatory.name in job_text,
   "jobs_run_initiate": "run_initiate: true" in job_text,
   "jobs_run_triangular": "run_triangular: true" in job_text,
   "targets":records,
   "any_target_as_head":any(x["header_count"] for x in records),
   "any_target_as_term":any(x["term_count"] for x in records),
   "physical_reduction_proven":False,
   "warning":"Neither absence from headers nor absence from terms proves that seeds were omitted: canonicalization/symmetries and execution history require separate inspection."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VP05_TARGET_EQUATION_HEADER "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
