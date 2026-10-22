"""Bounded exact-symbolic smoke test for exported VP05 sector202 original rows.

Verify literal Kira coefficients against a modular evaluation and construct
small exact row-echelon prefixes with independent exact original-row replay.
No claim of target reduction proof from a prefix.
"""
from __future__ import annotations
import argparse,gzip,json,hashlib
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_weight_audit import ROOT
from examples.three_loop_sector203_ffrank_audit import coefficient

DEFAULT=ROOT/"output/three_loop_integral_family_audit/vp05_sector202_exact_source_rows.json.gz"

def expr(raw,z,d):
 val=sp.sympify(raw.replace("^","**"),locals={"z":z,"d":d})
 if val.free_symbols-{z,d}:raise ValueError("Unrecognized coefficient symbol")
 return val

def subtract(dest,source,mult):
 for k,v in source.items():
  t=sp.cancel(dest.get(k,sp.S.Zero)-mult*v)
  if t==0:dest.pop(k,None)
  else:dest[k]=t

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--input",type=Path,default=DEFAULT)
 ap.add_argument("--rows",type=int,default=6)
 ap.add_argument("--max-columns",type=int,default=100)
 ap.add_argument("--max-expression-chars",type=int,default=1200)
 ap.add_argument("--mod-prime",type=int,default=1000003)
 ap.add_argument("--mod-z",type=int,default=17)
 ap.add_argument("--mod-d",type=int,default=7)
 args=ap.parse_args()
 if args.rows<1 or args.rows>20:ap.error("--rows must be between 1 and 20")
 with gzip.open(args.input,"rt",encoding="utf-8") as f:data=json.load(f)
 if data.get("status")!="ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED":raise RuntimeError("Unexpected export format")
 rows=data["rows"]
 if len(rows)!=data["selected_equation_count"] or len(rows)!=2241:raise RuntimeError("Wrong original row count")
 if len(data["source_file_sha256"])!=14:raise RuntimeError("Unexpected original source count")
 prev=-1
 for r in rows:
  if r["global_zero_based"]<=prev:raise RuntimeError("Nonmonotonic provenance indices")
  prev=r["global_zero_based"]
  if not r["terms"]:raise RuntimeError("Empty source row")
 z,d=sp.symbols("z d")
 basis={};stats=[];independent=0
 for ri,record in enumerate(rows[:args.rows]):
  current={}
  for t in record["terms"]:
   key=tuple(t["key"]);v=expr(t["coefficient"],z,d)
   current[key]=sp.cancel(current.get(key,0)+v)
   if current[key]==0:current.pop(key)
   modular=coefficient(t["coefficient"],args.mod_z,args.mod_d,args.mod_prime)
   evaluated=v.subs({z:args.mod_z,d:args.mod_d})
   rational=sp.cancel(evaluated)
   if rational.q%args.mod_prime==0:raise RuntimeError("Singular modular coefficient")
   residue=int(rational.p)%args.mod_prime*pow(int(rational.q)%args.mod_prime,-1,args.mod_prime)%args.mod_prime
   if residue!=modular:raise RuntimeError("Exact/modular coefficient mismatch")
  original=dict(current);trace={ri:sp.S.One};reduced=0
  while current:
   pivot=min(current)
   if pivot not in basis:break
   brow,btrace=basis[pivot]
   fac=current[pivot]
   subtract(current,brow,fac)
   subtract(trace,btrace,fac)
   reduced+=1
   if len(current)>args.max_columns or any(len(str(x))>args.max_expression_chars for x in current.values()):
    raise RuntimeError("Symbolic cap reached; retry fewer rows")
  if current:
   lead=min(current);divisor=current[lead]
   current={k:sp.cancel(v/divisor) for k,v in current.items()}
   trace={k:sp.cancel(v/divisor) for k,v in trace.items()}
   if len(current)>args.max_columns or any(len(str(x))>args.max_expression_chars for x in [*current.values(),*trace.values()]):
    raise RuntimeError("Symbolic cap reached; retry fewer rows")
   replay={}
   for idx,factor in trace.items():
    for t in rows[idx]["terms"]:
     key=tuple(t["key"])
     value=sp.cancel(replay.get(key,0)+factor*expr(t["coefficient"],z,d))
     if value:replay[key]=value
     else:replay.pop(key,None)
   if set(replay)!=set(current) or any(sp.cancel(replay[k]-current[k])!=0 for k in current):
    raise AssertionError("Exact original row provenance replay mismatch")
   basis[lead]=(current,trace);independent+=1
  stats.append({"original_index":record["global_zero_based"],"columns":len(current),
    "source_support":len(trace),"reduction_steps":reduced,"exact_provenance_replay":True})
 result={"status":"EXACT_SYMBOLIC_PREFIX_REPLAY_VERIFIED","input":str(args.input),
  "selected_source_rows":len(rows),"rows_checked":args.rows,"exact_prefix_rank":independent,
  "original_files":len(data["source_file_sha256"]),"row_statistics":stats,
  "exact_target_reduction_proven":False,"original_kira_sources_modified":False,
  "interpretation":"Symbolic replay of bounded original-row prefix only; full 2241-row target relation not attempted."}
 print("VP05_SECTOR202_EXACT_PREFIX_SMOKE "+json.dumps(result,ensure_ascii=True),flush=True)
if __name__=="__main__":main()
