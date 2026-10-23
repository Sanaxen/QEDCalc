"""Resumable bounded exact-symbolic elimination of VP05 modular-support source rows.

Checkpoint contains rational pivot rows AND original-source provenance. Each
checkpoint load replays every saved pivot against literal exported IBP rows.
No A/B exact target proof is claimed by eliminating source rows alone.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json,os
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_weight_audit import ROOT
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr,subtract

BASE=ROOT/"output/three_loop_integral_family_audit"
SOURCE=BASE/"vp05_sector202_exact_source_rows.json.gz"
CERT=BASE/"vp05_sector202_modular_provenance_certificate.json"
CHECKPOINT=BASE/"vp05_sector202_exact_support_checkpoint.json"

def digest(raw):return hashlib.sha256(raw).hexdigest()
def compact_exact(value):
 """Keep a shorter factored rational expression without changing its value."""
 candidate=sp.factor(value)
 if sp.cancel(candidate-value)!=0:
  raise AssertionError("Factored candidate is not symbolically equal")
 return candidate if len(str(candidate))<len(str(value)) else value
def decode_terms(entries,z,d):
 return {tuple(key):expr(value,z,d) for key,value in entries}
def encode_terms(row):
 return [[list(k),str(v)] for k,v in sorted(row.items())]
def replay(trace,rows,z,d):
 out={}
 for rid,factor in trace.items():
  for term in rows[rid]["terms"]:
   key=tuple(term["key"])
   v=sp.cancel(out.get(key,sp.S.Zero)+factor*expr(term["coefficient"],z,d))
   if v:out[key]=v
   else:out.pop(key,None)
 return out
def verify(row,trace,rows,z,d):
 actual=replay(trace,rows,z,d)
 if set(actual)!=set(row) or any(sp.cancel(actual[k]-row[k])!=0 for k in row):
  raise AssertionError("Exact pivot/source provenance mismatch")
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--input",type=Path,default=SOURCE)
 ap.add_argument("--certificate",type=Path,default=CERT)
 ap.add_argument("--checkpoint",type=Path,default=CHECKPOINT)
 ap.add_argument("--rows-per-run",type=int,default=20)
 ap.add_argument("--max-columns",type=int,default=100)
 ap.add_argument("--max-source-support",type=int,default=100)
 ap.add_argument("--max-expression-chars",type=int,default=1200)
 ap.add_argument("--target",choices=["union","A","B"],default="union")
 ap.add_argument("--resume",action="store_true")
 ap.add_argument("--factor-elimination",action="store_true",help="Conditionally factor row and provenance expressions during elimination")
 ap.add_argument("--factor-trigger-chars",type=int,default=900)
 ap.add_argument("--factor-normalization",action="store_true",help="Try shorter exact factored forms after new pivot normalization; does not alter existing checkpoint")
 ap.add_argument("--diagnose-next",action="store_true",help="Inspect only the next source row and never write the checkpoint")
 ap.add_argument("--diagnostic-output",type=Path,default=BASE/"vp05_sector202_exact_support_cap_diagnostic.json")
 args=ap.parse_args()
 if not 1<=args.rows_per_run<=100:ap.error("--rows-per-run must be 1..100")
 if min(args.max_columns,args.max_source_support,args.max_expression_chars)<1:ap.error("Caps must be positive")
 if args.factor_trigger_chars<1 or args.factor_trigger_chars>args.max_expression_chars:ap.error("Factor trigger must lie within expression cap")
 source_raw=args.input.read_bytes();cert_raw=args.certificate.read_bytes()
 with gzip.open(args.input,"rt",encoding="utf-8") as stream:source=json.load(stream)
 if source.get("status")!="ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED" or len(source["rows"])!=2241:
  raise RuntimeError("Unexpected exported original source format")
 rows={r["global_zero_based"]:r for r in source["rows"]}
 cert=json.loads(cert_raw.decode("utf-8-sig"))
 if cert.get("status")!="MODULAR_ORIGINAL_ROW_CERTIFICATE_VERIFIED_NOT_EXACT_PROOF" or cert.get("point")!=[1000003,17,7]:
  raise RuntimeError("Unexpected modular certificate")
 targets=cert["target_results"]
 if len(targets)!=2 or any(t["target_index"]!=i or t["modular_original_replay_verified"] is not True for i,t in enumerate(targets)):
  raise RuntimeError("Missing verified modular target support")
 groups=[set(t["support_original_ids"]) for t in targets]
 for t,g in zip(targets,groups):
  if len(g)!=t["nonzero_original_support"] or sorted(g)!=t["support_original_ids"]:
   raise RuntimeError("Invalid modular source support")
 ids=sorted(groups[0]|groups[1] if args.target=="union" else groups[0] if args.target=="A" else groups[1])
 if any(i not in rows for i in ids):raise RuntimeError("Source ID absent from exported exact rows")
 config={"source_sha256":digest(source_raw),"certificate_sha256":digest(cert_raw),
  "target":args.target,"ids_sha256":digest(json.dumps(ids).encode()),
  "max_columns":args.max_columns,"max_source_support":args.max_source_support,
  "max_expression_chars":args.max_expression_chars}
 z,d=sp.symbols("z d")
 basis={};processed=0;dependent=0
 if args.resume:
  saved=json.loads(args.checkpoint.read_text(encoding="utf-8"))
  if saved.get("version")!=1 or saved.get("config")!=config or saved.get("status")!="EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF":
   raise RuntimeError("Checkpoint source/config mismatch")
  processed=saved["processed"];dependent=saved["dependent"]
  if not 0<=processed<=len(ids):raise RuntimeError("Invalid checkpoint position")
  if not 0<=dependent<=processed:raise RuntimeError("Invalid dependent count")
  for entry in saved["pivots"]:
   lead=tuple(entry["lead"])
   row=decode_terms(entry["row"],z,d)
   trace={int(i):expr(value,z,d) for i,value in entry["trace"]}
   if not row or min(row)!=lead or sp.cancel(row[lead]-1)!=0:
    raise RuntimeError("Checkpoint pivot is not normalized")
   if any(i not in ids[:processed] for i in trace):raise RuntimeError("Checkpoint references unprocessed source")
   if len(row)>args.max_columns or len(trace)>args.max_source_support or max([len(str(v)) for v in list(row.values())+list(trace.values())] or [0])>args.max_expression_chars:
    raise RuntimeError("Checkpoint exceeds safety caps")
   verify(row,trace,rows,z,d)
   if lead in basis:raise RuntimeError("Duplicate checkpoint pivot")
   basis[lead]=(row,trace)
  if len(basis)+dependent!=processed:raise RuntimeError("Checkpoint rank accounting mismatch")
 elif args.checkpoint.exists():
  raise RuntimeError("Checkpoint exists: supply --resume, or use a new --checkpoint path")
 def check(row,trace,stage,rid,pivot=None):
  row_chars=max([len(str(v)) for v in row.values()] or [0])
  trace_chars=max([len(str(v)) for v in trace.values()] or [0])
  chars=max(row_chars,trace_chars)
  if len(row)>args.max_columns or len(trace)>args.max_source_support or chars>args.max_expression_chars:
   if args.diagnose_next:
    candidates=[("row",str(k),str(v)) for k,v in row.items()]+[("trace",str(k),str(v)) for k,v in trace.items()]
    largest=sorted(candidates,key=lambda item:len(item[2]),reverse=True)[:5]
    report={"status":"EXACT_SUPPORT_DIAGNOSTIC_CAP_REACHED_NOT_PROOF",
     "checkpoint_sha256":digest(args.checkpoint.read_bytes()),"processed_saved":processed,
     "next_original_id":rid,"stage":stage,"pivot":list(pivot) if pivot is not None else None,
     "columns":len(row),"source_support":len(trace),"row_expression_chars":row_chars,
     "provenance_expression_chars":trace_chars,"max_expression_chars":args.max_expression_chars,
     "largest_entries":[{"kind":a,"key":b,"chars":len(c),"preview":c[:240]} for a,b,c in largest],
     "checkpoint_modified":False,"exact_target_reduction_proven":False}
    args.diagnostic_output.parent.mkdir(parents=True,exist_ok=True)
    args.diagnostic_output.write_text(json.dumps(report,indent=2)+"\\n",encoding="utf-8")
    print("VP05_SECTOR202_EXACT_SUPPORT_CAP_DIAGNOSTIC "+json.dumps(report,ensure_ascii=True),flush=True)
   raise RuntimeError("Safety cap exceeded at %s original ID %d: columns=%d support=%d row_chars=%d trace_chars=%d"%(stage,rid,len(row),len(trace),row_chars,trace_chars))
 limit=min(len(ids),processed+(1 if args.diagnose_next else args.rows_per_run))
 for position in range(processed,limit):
  rid=ids[position];cur={}
  for term in rows[rid]["terms"]:
   key=tuple(term["key"])
   val=sp.cancel(cur.get(key,sp.S.Zero)+expr(term["coefficient"],z,d))
   if val:cur[key]=val
   else:cur.pop(key,None)
  trace={rid:sp.S.One}
  check(cur,trace,"initial",rid)
  while cur:
   lead=min(cur)
   if lead not in basis:break
   brow,btrace=basis[lead]
   factor=cur[lead]
   subtract(cur,brow,factor)
   subtract(trace,btrace,factor)
   if args.factor_elimination:
    before_row=max((len(str(v)) for v in cur.values()),default=0)
    before_trace=max((len(str(v)) for v in trace.values()),default=0)
    if max(before_row,before_trace)>=args.factor_trigger_chars:
     cur={k:compact_exact(v) for k,v in cur.items()}
     trace={k:compact_exact(v) for k,v in trace.items()}
     print("VP05_SECTOR202_EXACT_FACTOR_ELIMINATION "+json.dumps({"original_id":rid,"pivot":list(lead),"row_chars_before":before_row,"trace_chars_before":before_trace,"row_chars_after":max((len(str(v)) for v in cur.values()),default=0),"trace_chars_after":max((len(str(v)) for v in trace.values()),default=0)}),flush=True)
   check(cur,trace,"elimination",rid,lead)
  if cur:
   lead=min(cur);factor=cur[lead]
   cur={k:sp.cancel(v/factor) for k,v in cur.items()}
   trace={k:sp.cancel(v/factor) for k,v in trace.items()}
   if args.factor_normalization:
    before_row=max((len(str(v)) for v in cur.values()),default=0)
    before_trace=max((len(str(v)) for v in trace.values()),default=0)
    cur={k:compact_exact(v) for k,v in cur.items()}
    trace={k:compact_exact(v) for k,v in trace.items()}
    print("VP05_SECTOR202_EXACT_FACTOR_NORMALIZATION "+json.dumps({"original_id":rid,"row_chars_before":before_row,"trace_chars_before":before_trace,"row_chars_after":max((len(str(v)) for v in cur.values()),default=0),"trace_chars_after":max((len(str(v)) for v in trace.values()),default=0)}),flush=True)
   check(cur,trace,"normalization",rid,lead)
   verify(cur,trace,rows,z,d)
   basis[lead]=(cur,trace)
  else:
   verify({},trace,rows,z,d)
   dependent+=1
  processed=position+1
  print("VP05_SECTOR202_EXACT_SUPPORT_PROGRESS "+json.dumps({"processed":processed,"total":len(ids),"rank":len(basis),"dependent":dependent,"last_original_id":rid}),flush=True)
 if args.diagnose_next:
  print("VP05_SECTOR202_EXACT_SUPPORT_DIAGNOSTIC "+json.dumps({"status":"NEXT_SOURCE_ROW_WITHIN_CAPS","saved_processed":limit-1,"tested_original_id":ids[limit-1] if limit else None,"checkpoint_modified":False,"exact_target_reduction_proven":False}),flush=True)
  return
 payload={"version":1,"status":"EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF",
  "config":config,"processed":processed,"total":len(ids),"dependent":dependent,
  "pivots":[{"lead":list(k),"row":encode_terms(row),"trace":[[i,str(v)] for i,v in sorted(trace.items())]}
            for k,(row,trace) in sorted(basis.items())],
  "source_pivots_exact_replay_verified":True,"exact_target_reduction_proven":False}
 args.checkpoint.parent.mkdir(parents=True,exist_ok=True)
 temp=args.checkpoint.with_name(args.checkpoint.name+".tmp")
 with temp.open("w",encoding="utf-8") as fh:
  json.dump(payload,fh,ensure_ascii=True,separators=(",",":"))
  fh.flush();os.fsync(fh.fileno())
 os.replace(temp,args.checkpoint)
 print("VP05_SECTOR202_EXACT_SUPPORT_CHECKPOINT "+json.dumps({
  "status":payload["status"],"processed":processed,"total":len(ids),
  "rank":len(basis),"dependent":dependent,"complete_source_pass":processed==len(ids),
  "checkpoint":str(args.checkpoint),"exact_target_reduction_proven":False},ensure_ascii=True),flush=True)
if __name__=="__main__":main()
