"""Export exact original VP05 sector202 IBP rows selected by modular provenance.

This is an input bundle for subsequent symbolic proof, not a proof itself.
Read-only Kira project; output under output/three_loop_integral_family_audit.
"""
from __future__ import annotations
import argparse,gzip,hashlib,io,json
from contextlib import redirect_stdout
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT
from examples.three_loop_vp05_sector202_quotient_sensitivity import P
from examples.three_loop_vp05_sector202_symbolic_source_preflight import main as preflight
PREFIX="VP05_SECTOR202_SOURCE_PROOF_PREFLIGHT "

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--output",type=Path,default=ROOT/"output/three_loop_integral_family_audit/vp05_sector202_exact_source_rows.json.gz")
 args=parser.parse_args()
 # The preflight consumes argparse: call with a clean argv.
 import sys
 old=sys.argv
 buffer=io.StringIO()
 try:
  sys.argv=[old[0]]
  with redirect_stdout(buffer):preflight()
 finally:sys.argv=old
 lines=[line for line in buffer.getvalue().splitlines() if line.startswith(PREFIX)]
 if len(lines)!=1:raise RuntimeError("Missing modular provenance report")
 provenance=json.loads(lines[0][len(PREFIX):])
 if not all(t["verified"] for t in provenance["target_tests"]):
  raise RuntimeError("Modular target replay failed")
 chosen={r["global_zero_based"]:r for r in provenance["selected_rows"]}
 if len(chosen)!=provenance["union_source_rows"]:raise RuntimeError("Duplicate provenance index")
 rows=[];digests={};index=0
 for source in sorted((P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  digests[source.name]=hashlib.sha256(source.read_bytes()).hexdigest()
  with gzip.open(source,"rt",encoding="utf-8") as stream:
   ordinal=0
   while marker:=stream.readline():
    if marker.strip()!="Eq":raise ValueError("Malformed original SYSTEM record")
    equation_id=stream.readline().strip()
    n=int(stream.readline().strip());ordinal+=1
    terms=[]
    for _ in range(n):
     fields=stream.readline().split()
     if len(fields)<4:raise ValueError("Malformed original SYSTEM term")
     if index in chosen:
      terms.append({"key":[int(fields[2]),int(fields[3])],"coefficient":fields[1]})
    if index in chosen:
     item=chosen[index]
     if item["file"]!=source.name or item["ordinal"]!=ordinal or item["equation_id"]!=equation_id:
      raise RuntimeError("Original row metadata mismatch")
     rows.append({"global_zero_based":index,"file":source.name,
                  "ordinal":ordinal,"equation_id":equation_id,"terms":terms})
    index+=1
 if index!=2678 or len(rows)!=len(chosen):raise RuntimeError("Provenance coverage mismatch")
 bundle={"status":"ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED",
  "source_project":str(P),"modular_point":provenance["point"],
  "source_file_sha256":digests,"saved_equation_count":index,
  "selected_equation_count":len(rows),"rows":rows,
  "exact_symbolic_certificate_verified":False}
 args.output.parent.mkdir(parents=True,exist_ok=True)
 with gzip.open(args.output,"wt",encoding="utf-8") as target:
  json.dump(bundle,target,ensure_ascii=True,separators=(",",":"))
 print("VP05_SECTOR202_EXACT_SOURCE_EXPORT "+json.dumps({
   "status":"EXPORTED_NOT_PROVEN","file":str(args.output),
   "selected_rows":len(rows),"terms":sum(len(r["terms"]) for r in rows),
   "original_files":len(digests),"source_sha256_recorded":True,
   "exact_symbolic_certificate_verified":False,"kira_executed":False,
   "original_files_modified":False},ensure_ascii=True),flush=True)
if __name__=="__main__":main()
