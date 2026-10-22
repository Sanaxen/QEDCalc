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
 ap.add_argument("--start-row",type=int,default=0,help="Zero-based offset within 2241 selected source rows")
 ap.add_argument("--indices-file",type=Path,help="JSON array of original global_zero_based IDs or object with selected_rows; indices must refer to exported source rows")
 ap.add_argument("--max-columns",type=int,default=100)
 ap.add_argument("--max-expression-chars",type=int,default=1200)
 ap.add_argument("--max-source-support",type=int,default=100)
 ap.add_argument("--mod-prime",type=int,default=1000003)
 ap.add_argument("--mod-z",type=int,default=17)
 ap.add_argument("--mod-d",type=int,default=7)
 args=ap.parse_args()
 if args.rows<1 or args.rows>100:ap.error("--rows must be between 1 and 100")
 if args.start_row<0:ap.error("--start-row must be nonnegative")
 if args.indices_file and args.start_row:ap.error("--indices-file and --start-row cannot be combined")
 if min(args.max_columns,args.max_expression_chars,args.max_source_support)<1:ap.error("All symbolic caps must be positive")
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
 if args.indices_file:
  with args.indices_file.open("r",encoding="utf-8-sig") as stream: selector=json.load(stream)
  if isinstance(selector,dict):
   selector=selector.get("selected_rows")
  if not isinstance(selector,list) or not selector:ap.error("--indices-file must hold a nonempty JSON array or selected_rows array")
  ids=[]
  for item in selector:
   if isinstance(item,dict):item=item.get("global_zero_based")
   if type(item) is not int or item<0:ap.error("Each selected global_zero_based index must be a nonnegative integer")
   ids.append(item)
  if len(ids)!=len(set(ids)):ap.error("Duplicate selected indices")
  if len(ids)>args.rows:ap.error("Indices file has %d entries but --rows=%d; raise --rows explicitly (max 100)" % (len(ids),args.rows))
  available={r["global_zero_based"]:i for i,r in enumerate(rows)}
  missing=[i for i in ids if i not in available]
  if missing:ap.error("Requested original IDs missing from exact source export: %s" % missing[:10])
  chosen=[(available[i],rows[available[i]]) for i in ids]
  selection_mode="explicit_original_ids"
 else:
  if args.start_row+args.rows>len(rows):ap.error("Requested row window exceeds source export")
  chosen=list(enumerate(rows[args.start_row:args.start_row+args.rows],start=args.start_row))
  selection_mode="prefix" if args.start_row==0 else "window"
 z,d=sp.symbols("z d")
 basis={};stats=[];independent=0
 def measure(row,trace,stage,idx):
  max_row=max((len(str(v)) for v in row.values()),default=0)
  max_trace=max((len(str(v)) for v in trace.values()),default=0)
  if (len(row)>args.max_columns or len(trace)>args.max_source_support or
      max(max_row,max_trace)>args.max_expression_chars):
   raise RuntimeError("Symbolic cap reached at row %d (%s): columns=%d support=%d max_row_chars=%d max_trace_chars=%d" %
      (idx,stage,len(row),len(trace),max_row,max_trace))
  return max_row,max_trace
 for ri,record in chosen:
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
  measure(current,trace,"initial",ri)
  while current:
   pivot=min(current)
   if pivot not in basis:break
   brow,btrace=basis[pivot]
   fac=current[pivot]
   subtract(current,brow,fac)
   subtract(trace,btrace,fac)
   reduced+=1
   measure(current,trace,"elimination",ri)
  if current:
   lead=min(current);divisor=current[lead]
   current={k:sp.cancel(v/divisor) for k,v in current.items()}
   trace={k:sp.cancel(v/divisor) for k,v in trace.items()}
   measure(current,trace,"normalization",ri)
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
  row_chars,trace_chars=measure(current,trace,"complete",ri)
  stats.append({"original_index":record["global_zero_based"],"columns":len(current),
    "source_support":len(trace),"reduction_steps":reduced,
    "max_row_expression_chars":row_chars,"max_provenance_expression_chars":trace_chars,
    "exact_provenance_replay":True})
 result={"status":"EXACT_SYMBOLIC_PREFIX_REPLAY_VERIFIED","input":str(args.input),
  "selected_source_rows":len(rows),"rows_checked":len(chosen),"exact_prefix_rank":independent,
  "selection_mode":selection_mode,"start_row":args.start_row if not args.indices_file else None,
  "selected_original_ids":[record["global_zero_based"] for _,record in chosen],
  "original_files":len(data["source_file_sha256"]),"row_statistics":stats,
  "symbolic_caps":{"max_columns":args.max_columns,"max_expression_chars":args.max_expression_chars,"max_source_support":args.max_source_support},
  "observed_maxima":{"columns":max(x["columns"] for x in stats),
    "source_support":max(x["source_support"] for x in stats),
    "reduction_steps":max(x["reduction_steps"] for x in stats),
    "row_expression_chars":max(x["max_row_expression_chars"] for x in stats),
    "provenance_expression_chars":max(x["max_provenance_expression_chars"] for x in stats)},
  "exact_target_reduction_proven":False,"original_kira_sources_modified":False,
  "interpretation":"Symbolic replay of a bounded source-row selection only; full 2241-row target relation not attempted."}
 print("VP05_SECTOR202_EXACT_PREFIX_SMOKE "+json.dumps(result,ensure_ascii=True),flush=True)
if __name__=="__main__":main()
