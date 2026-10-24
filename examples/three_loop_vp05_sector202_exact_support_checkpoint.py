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
 ap.add_argument("--fork-from",type=Path,help="One-time immutable source checkpoint for a fresh enlarged-cap checkpoint path")
 ap.add_argument("--rows-per-run",type=int,default=20)
 ap.add_argument("--max-columns",type=int,default=100)
 ap.add_argument("--max-intermediate-columns",type=int,default=None,help="Optional larger cap only during intermediate exact elimination; persisted pivots remain bounded by --max-columns")
 ap.add_argument("--max-source-support",type=int,default=100)
 ap.add_argument("--max-expression-chars",type=int,default=1200)
 ap.add_argument("--target",choices=["union","A","B"],default="union")
 ap.add_argument("--resume",action="store_true")
 ap.add_argument("--factor-elimination",action="store_true",help="Conditionally factor row and provenance expressions during elimination")
 ap.add_argument("--factor-trigger-chars",type=int,default=900)
 ap.add_argument("--factor-normalization",action="store_true",help="Try shorter exact factored forms after new pivot normalization; does not alter existing checkpoint")
 ap.add_argument("--diagnose-next",action="store_true",help="Inspect only the next source row and never write the checkpoint")
 ap.add_argument("--diagnostic-output",type=Path,default=BASE/"vp05_sector202_exact_support_cap_diagnostic.json")
 ap.add_argument("--fixed-path-audit",action="store_true",help="Compare exact pivot path with modular per-point forward elimination")
 ap.add_argument("--fixed-path-output",type=Path,default=BASE/"vp05_sector202_fixed_path_audit.json")
 ap.add_argument("--exact-divergence",action="store_true",help="Read-only exact rational audit of the ID730 pivot at modular divergence step")
 ap.add_argument("--exact-divergence-output",type=Path,default=BASE/"vp05_sector202_exact_divergence.json")
 ap.add_argument("--modular-fill",action="store_true",help="Read-only finite-field forward elimination of the next source row")
 ap.add_argument("--modular-fill-output",type=Path,default=BASE/"vp05_sector202_modular_fill_forward.json")
 ap.add_argument("--trace-fill",action="store_true",help="Record exact elimination fill-in for next row in read-only diagnostic mode")
 ap.add_argument("--fill-output",type=Path,default=BASE/"vp05_sector202_exact_support_fill_trace.json")
 args=ap.parse_args()
 if not 1<=args.rows_per_run<=100:ap.error("--rows-per-run must be 1..100")
 if args.fork_from and (not args.resume or args.checkpoint.resolve()==args.fork_from.resolve()):ap.error("--fork-from requires --resume and a distinct --checkpoint destination")
 if args.trace_fill and (not args.diagnose_next or not args.resume):ap.error("--trace-fill requires --resume --diagnose-next")
 if args.modular_fill and (not args.resume or not args.diagnose_next):ap.error("--modular-fill requires --resume --diagnose-next")
 if args.exact_divergence and (not args.resume or not args.diagnose_next or args.modular_fill):ap.error("--exact-divergence requires --resume --diagnose-next and excludes --modular-fill")
 if min(args.max_columns,args.max_source_support,args.max_expression_chars)<1:ap.error("Caps must be positive")
 if args.max_intermediate_columns is None:args.max_intermediate_columns=args.max_columns
 if args.max_intermediate_columns<args.max_columns:ap.error("--max-intermediate-columns must be >= --max-columns")
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
 if args.fork_from:
  if args.checkpoint.exists():raise RuntimeError("Fork destination already exists; use --resume without --fork-from")
  original_bytes=args.fork_from.read_bytes()
  original=json.loads(original_bytes.decode("utf-8-sig"))
  if original.get("version")!=1 or original.get("status")!="EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF":
   raise RuntimeError("Unrecognized original checkpoint format")
  previous=original.get("config",{})
  core=("source_sha256","certificate_sha256","target","ids_sha256")
  if any(previous.get(key)!=config[key] for key in core):
   raise RuntimeError("Fork input data or selection mismatch")
  caps=("max_columns","max_source_support","max_expression_chars")
  if any(not isinstance(previous.get(key),int) or previous[key]>config[key] for key in caps):
   raise RuntimeError("Fork may only preserve/increase original persisted-pivot caps")
  if original.get("processed")!=298 or original.get("total")!=len(ids):
   raise RuntimeError("Expected original saved checkpoint at 298/389; refusing unexpected fork")
  original["config"]=config
  original["fork_provenance"]={"source_checkpoint":str(args.fork_from),
   "source_sha256":digest(original_bytes),"source_processed":298,
   "previous_caps":{key:previous[key] for key in caps}}
  args.checkpoint.parent.mkdir(parents=True,exist_ok=True)
  # Exclusive creation is deliberate: never overwrite an existing checkpoint.
  with args.checkpoint.open("x",encoding="utf-8") as handle:
   json.dump(original,handle,ensure_ascii=True,separators=(",",":"))
   handle.flush();os.fsync(handle.fileno())
  print("VP05_SECTOR202_EXACT_CHECKPOINT_FORK "+json.dumps({
   "status":"FORK_CREATED_NOT_TARGET_PROOF","source_sha256":digest(original_bytes),
   "destination":str(args.checkpoint),"processed":298,
   "new_caps":{key:config[key] for key in caps},"original_unchanged":True}),flush=True)
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
 if args.fixed_path_audit:
  if not args.resume or not args.diagnose_next:raise RuntimeError("--fixed-path-audit requires --resume --diagnose-next")
  if processed>=len(ids):raise RuntimeError("No remaining source row")
  rid=ids[processed]
  points=[(1000003,17,7),(1000033,19,11),(1000037,21,15)]
  def specialization(v,p,zv,dv):
   n,den=sp.fraction(sp.together(sp.cancel(v)))
   mapping={z:zv,d:dv}
   numerator=int(n.subs(mapping))%p;denominator=int(den.subs(mapping))%p
   if not denominator:raise ZeroDivisionError("Pole at modular point")
   return numerator*pow(denominator,-1,p)%p
  cur={}
  for term in rows[rid]["terms"]:
   key=tuple(term["key"])
   value=sp.cancel(cur.get(key,sp.S.Zero)+expr(term["coefficient"],z,d))
   if value:cur[key]=value
   else:cur.pop(key,None)
  modular=[]
  for p,zv,dv in points:
   try:
    m={}
    for key,value in cur.items():
     v=specialization(value,p,zv,dv)
     if v:m[key]=v
    modular.append({"point":[p,zv,dv],"row":m,"status":"PASS","steps":[]})
   except ZeroDivisionError:
    modular.append({"point":[p,zv,dv],"row":{},"status":"SINGULAR_SPECIALIZATION","steps":[]})
  exact_steps=[];stopped="EXACT_TERMINAL"
  for number in range(1,39):
   if not cur:break
   lead=min(cur)
   if lead not in basis:break
   brow,_=basis[lead];coefficient=cur[lead]
   before_exact=dict(cur)
   step={"step":number,"exact_pivot":list(lead),"exact_columns_before":len(cur),"exact_coefficient_chars":len(str(coefficient))}
   for m in modular:
    if m["status"]!="PASS":continue
    p,zv,dv=m["point"]
    try:
     mc=specialization(coefficient,p,zv,dv)
     # Compare complete finite-field row against exact specialization before
     # applying the next fixed pivot. This identifies the earliest divergence,
     # even if its first affected column is not yet the leading column.
     expected={}
     for ek,ev in cur.items():
      evalue=specialization(ev,p,zv,dv)
      if evalue:expected[ek]=evalue
     discrepant=sorted(k for k in set(expected)|set(m["row"])
                       if expected.get(k,0)!=m["row"].get(k,0))
     if discrepant:
      first=discrepant[0]
      m["status"]="ROW_STATE_MISMATCH"
      m["steps"].append({"step":number,"exact_pivot":list(lead),
        "first_differing_column":list(first),
        "expected_coefficient":expected.get(first,0),
        "tracked_coefficient":m["row"].get(first,0),
        "differing_columns":len(discrepant),
        "exact_columns":len(expected),"tracked_columns":len(m["row"]),
        "pivot_match":bool(m["row"]) and min(m["row"])==lead})
      continue
     pivot_coeff=m["row"].get(lead,0)
     first=list(min(m["row"])) if m["row"] else None
     equal=mc==pivot_coeff
     match=(first==list(lead))
     pivot_values={k:v for k,ev in brow.items() if (v:=specialization(ev,p,zv,dv))!=0}
     if not equal:
      m["status"]="COEFFICIENT_MISMATCH"
      m["steps"].append({"step":number,"exact_pivot":list(lead),
        "first_modular_pivot":first,"exact_coefficient_mod_p":mc,
        "tracked_modular_coefficient":pivot_coeff,"modular_columns_before":len(m["row"]),
        "pivot_match":match})
      continue
     before_modular=dict(m["row"])
     m["before_row"]=dict(m["row"])
     for k,v in pivot_values.items():
      updated=(m["row"].get(k,0)-mc*v)%p
      if updated:m["row"][k]=updated
      else:m["row"].pop(k,None)
     m["steps"].append({"step":number,"first_modular_pivot":first,
       "exact_pivot":list(lead),"pivot_match":match,"coefficient":mc,
       "modular_columns_after":len(m["row"])})
    except ZeroDivisionError:
     m["status"]="SINGULAR_SPECIALIZATION";m["steps"].append({"step":number,"error":"pole"})
   subtract(cur,brow,coefficient)
   for m in modular:
    if m["status"]!="PASS":continue
    p,zv,dv=m["point"]
    try:
     expected_after={k:v for k,ev in cur.items()
         if (v:=specialization(ev,p,zv,dv))!=0}
     mismatch=sorted(k for k in set(expected_after)|set(m["row"])
                      if expected_after.get(k,0)!=m["row"].get(k,0))
     if mismatch:
      k=mismatch[0]
      m["status"]="POST_ELIMINATION_MISMATCH"
      m["steps"].append({"step":number,"exact_pivot":list(lead),
        "first_differing_column":list(k),"expected_after":expected_after.get(k,0),
        "tracked_after":m["row"].get(k,0),
        "tracked_before_mod_p":m["before_row"].get(k,0),"pivot_row_coefficient":specialization(brow.get(k,sp.S.Zero),p,zv,dv),
        "elimination_multiplier":specialization(coefficient,p,zv,dv),
        "exact_before_expression":str(before_exact.get(k,sp.S.Zero)),
        "exact_multiplier_expression":str(coefficient),
        "exact_pivot_row_expression":str(brow.get(k,sp.S.Zero)),
        "exact_after_expression":str(cur.get(k,sp.S.Zero)),
        "symbolic_expected_after":str(sp.cancel(before_exact.get(k,sp.S.Zero)-coefficient*brow.get(k,sp.S.Zero))),
        "symbolic_subtraction_matches_stored":sp.cancel(cur.get(k,sp.S.Zero)-(before_exact.get(k,sp.S.Zero)-coefficient*brow.get(k,sp.S.Zero)))==0,
        "exact_before_mod_p":specialization(before_exact.get(k,sp.S.Zero),p,zv,dv),
        "predicted_modular_after":(specialization(before_exact.get(k,sp.S.Zero),p,zv,dv)-specialization(coefficient,p,zv,dv)*specialization(brow.get(k,sp.S.Zero),p,zv,dv))%p,
        "difference_columns":len(mismatch),"pivot_match":True})
    except ZeroDivisionError:
     m["status"]="SINGULAR_SPECIALIZATION"
   exact_steps.append(step)
   if len(cur)>args.max_intermediate_columns:
    stopped="EXACT_INTERMEDIATE_COLUMN_CAP";break
   if max((len(str(v)) for v in cur.values()),default=0)>args.max_expression_chars:
    stopped="EXACT_EXPRESSION_CAP";break
  report={"status":"FIXED_PATH_AUDIT_NOT_TARGET_PROOF","saved_processed":processed,
   "original_id":rid,"checkpoint_sha256":digest(args.checkpoint.read_bytes()),
   "exact_steps":exact_steps,"exact_status":stopped,
   "points":[{"point":m["point"],"status":m["status"],"steps":m["steps"],
     "first_path_mismatch":next((x for x in m["steps"] if not x.get("pivot_match",True) or "tracked_modular_coefficient" in x or "first_differing_column" in x),None),
     "final_columns":len(m["row"])} for m in modular],
   "checkpoint_modified":False,"exact_target_reduction_proven":False}
  args.fixed_path_output.parent.mkdir(parents=True,exist_ok=True)
  args.fixed_path_output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
  print("VP05_SECTOR202_FIXED_PATH "+json.dumps({"status":report["status"],
   "exact_steps":len(exact_steps),"exact_status":stopped,
   "points":[{"point":m["point"],"status":m["status"],
     "first_path_mismatch":next((x for x in m["steps"] if not x.get("pivot_match",True) or "tracked_modular_coefficient" in x or "first_differing_column" in x),None)}
     for m in modular],"checkpoint_modified":False,
   "output":str(args.fixed_path_output)}),flush=True)
  return
 if args.exact_divergence:
  if processed>=len(ids):raise RuntimeError("No next source row")
  rid=ids[processed]
  if rid!=730:raise RuntimeError("Exact divergence audit expects original ID730")
  candidate=(166578162499584,139)
  points=[(1000003,17,7),(1000033,19,11),(1000037,21,15)]
  current={}
  for term in rows[rid]["terms"]:
   key=tuple(term["key"])
   v=sp.cancel(current.get(key,sp.S.Zero)+expr(term["coefficient"],z,d))
   if v:current[key]=v
   else:current.pop(key,None)
  pivot_path=[];status="TARGET_PIVOT_NOT_REACHED"
  for step in range(1,39):
   lead=min(current) if current else None
   if lead is None or lead not in basis:
    status="ELIMINATION_TERMINATED_BEFORE_TARGET";break
   if step==38:
    value=sp.cancel(current.get(candidate,sp.S.Zero))
    num,den=sp.fraction(sp.together(value))
    evaluations=[]
    for p,zv,dv in points:
     n=int(num.subs({z:zv,d:dv}))%p
     denominator=int(den.subs({z:zv,d:dv}))%p
     modular_value=(n*pow(denominator,-1,p)%p) if denominator else None
     evaluations.append({"point":[p,zv,dv],"numerator_mod_p":n,"denominator_mod_p":denominator,
       "coefficient_mod_p":modular_value,"defined":denominator!=0})
    report={"status":"EXACT_DIVERGENCE_COEFFICIENT_AUDIT_NOT_TARGET_PROOF",
      "checkpoint_sha256":digest(args.checkpoint.read_bytes()),"saved_processed":processed,
      "original_id":rid,"exact_step":step,"exact_lead":list(lead),"candidate_pivot":list(candidate),
      "candidate_coefficient":str(value),"numerator":str(num),"denominator":str(den),
      "symbolically_zero":value==0,"evaluations":evaluations,
      "pivot_path":pivot_path,"checkpoint_modified":False,"exact_target_reduction_proven":False}
    args.exact_divergence_output.parent.mkdir(parents=True,exist_ok=True)
    args.exact_divergence_output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_SECTOR202_EXACT_DIVERGENCE "+json.dumps({
      "status":report["status"],"exact_step":step,"exact_lead":list(lead),
      "candidate_pivot":list(candidate),"symbolically_zero":value==0,
      "coefficient_chars":len(str(value)),"evaluations":evaluations,
      "output":str(args.exact_divergence_output),"checkpoint_modified":False}),flush=True)
    return
   brow,_=basis[lead]
   subtract(current,brow,current[lead])
   pivot_path.append(list(lead))
   if len(current)>args.max_intermediate_columns:
    status="INTERMEDIATE_COLUMN_CAP_BEFORE_TARGET";break
   if max((len(str(v)) for v in current.values()),default=0)>args.max_expression_chars:
    status="EXPRESSION_CAP_BEFORE_TARGET";break
  print("VP05_SECTOR202_EXACT_DIVERGENCE "+json.dumps({
   "status":status,"steps":len(pivot_path),"last_lead":pivot_path[-1] if pivot_path else None,
   "checkpoint_modified":False}),flush=True)
  return
 if args.modular_fill:
  if processed>=len(ids):raise RuntimeError("No next source row")
  rid=ids[processed]
  points=[(1000003,17,7),(1000033,19,11),(1000037,21,15)]
  def mod_value(v,p,zv,dv):
   numer,denom=sp.fraction(sp.together(sp.cancel(v)))
   substitutions={z:zv,d:dv}
   nn=int(numer.subs(substitutions))%p
   dd=int(denom.subs(substitutions))%p
   if dd==0:raise ZeroDivisionError("Specialization denominator is zero")
   return nn*pow(dd,-1,p)%p
  reports=[];row_states=[]
  for prime,zv,dv in points:
   try:
    modular_basis={}
    modular_trace={}
    for pivot,(brow,btrace) in sorted(basis.items()):
     vals={k:vv for k,v in brow.items() if (vv:=mod_value(v,prime,zv,dv))!=0}
     if vals.get(pivot)!=1:raise RuntimeError("Modular pivot failed specialization")
     modular_basis[pivot]=vals
     modular_trace[pivot]={i:vv for i,v in btrace.items() if (vv:=mod_value(v,prime,zv,dv))!=0}
    current={}
    for term in rows[rid]["terms"]:
     k=tuple(term["key"])
     v=mod_value(expr(term["coefficient"],z,d),prime,zv,dv)
     v=(current.get(k,0)+v)%prime
     if v:current[k]=v
     else:current.pop(k,None)
    provenance={rid:1}
    initial=len(current);initial_support=len(provenance);steps=[];states=[]
    while current:
     lead=min(current)
     if lead not in modular_basis:break
     prow=modular_basis[lead];ptrace=modular_trace[lead]
     factor=current[lead];before=len(current);support_before=len(provenance)
     states.append(dict(current))
     for k,value in prow.items():
      candidate=(current.get(k,0)-factor*value)%prime
      if candidate:current[k]=candidate
      else:current.pop(k,None)
     for original_id,value in ptrace.items():
      candidate=(provenance.get(original_id,0)-factor*value)%prime
      if candidate:provenance[original_id]=candidate
      else:provenance.pop(original_id,None)
     steps.append({"step":len(steps)+1,"pivot":list(lead),"before_columns":before,"pivot_columns":len(prow),"after_columns":len(current),
       "support_before":support_before,"support_after":len(provenance),"pivot_support":len(ptrace)})
    row_states.append(states)
    reports.append({"point":[prime,zv,dv],"status":"PASS","initial_columns":initial,
      "steps":steps,"peak_columns":max([initial]+[x["after_columns"] for x in steps]),
      "final_columns":len(current),"initial_support":initial_support,
      "peak_support":max([initial_support]+[x["support_after"] for x in steps]),
      "final_support":len(provenance),"terminal_lead":list(min(current)) if current else None,
      "terminal_lead_is_new_pivot":bool(current) and min(current) not in modular_basis})
   except (ZeroDivisionError,ValueError) as ex:
    row_states.append([])
    reports.append({"point":[prime,zv,dv],"status":"SPECIALIZATION_SKIPPED","reason":str(ex)})
  differences=[]
  for a in range(len(reports)):
   for b in range(a+1,len(reports)):
    if reports[a]["status"]!="PASS" or reports[b]["status"]!="PASS":continue
    path_a=reports[a]["steps"];path_b=reports[b]["steps"]
    common=min(len(path_a),len(path_b))
    i=next((j for j in range(common) if path_a[j]["pivot"]!=path_b[j]["pivot"]),common)
    if i==common and len(path_a)==len(path_b):
     differences.append({"points":[reports[a]["point"],reports[b]["point"]],"status":"IDENTICAL_PIVOT_PATH","steps":common})
     continue
    lead_a=tuple(path_a[i]["pivot"]) if i<len(path_a) else None
    lead_b=tuple(path_b[i]["pivot"]) if i<len(path_b) else None
    state_a=row_states[a][i] if i<len(row_states[a]) else {}
    state_b=row_states[b][i] if i<len(row_states[b]) else {}
    differences.append({"points":[reports[a]["point"],reports[b]["point"]],
      "status":"FIRST_PIVOT_DIVERGENCE","step_one_based":i+1,
      "pivot_at_a":list(lead_a) if lead_a else None,
      "pivot_at_b":list(lead_b) if lead_b else None,
      "a_pivot_coefficient_at_a":state_a.get(lead_a) if lead_a else None,
      "a_pivot_coefficient_at_b":state_b.get(lead_a,0) if lead_a else None,
      "b_pivot_coefficient_at_a":state_a.get(lead_b,0) if lead_b else None,
      "b_pivot_coefficient_at_b":state_b.get(lead_b) if lead_b else None,
      "columns_before_a":len(state_a),"columns_before_b":len(state_b)})
  result={"status":"MODULAR_FILL_DIAGNOSTIC_NOT_EXACT_PROOF","saved_processed":processed,
   "original_id":rid,"checkpoint_sha256":digest(args.checkpoint.read_bytes()),
   "points":reports,"path_comparisons":differences,"checkpoint_modified":False,"exact_target_reduction_proven":False}
  args.modular_fill_output.parent.mkdir(parents=True,exist_ok=True)
  args.modular_fill_output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
  print("VP05_SECTOR202_MODULAR_FILL "+json.dumps({"status":result["status"],"original_id":rid,
    "summary":[{"point":r["point"],"status":r["status"],"peak_columns":r.get("peak_columns"),"final_columns":r.get("final_columns"),"peak_support":r.get("peak_support"),"final_support":r.get("final_support"),"steps":len(r.get("steps",[]))} for r in reports],
    "path_comparisons":differences,"output":str(args.modular_fill_output),"checkpoint_modified":False}),flush=True)
  return
 def check(row,trace,stage,rid,pivot=None):
  column_cap=args.max_intermediate_columns if stage=="elimination" else args.max_columns
  row_chars=max([len(str(v)) for v in row.values()] or [0])
  trace_chars=max([len(str(v)) for v in trace.values()] or [0])
  chars=max(row_chars,trace_chars)
  if len(row)>column_cap or len(trace)>args.max_source_support or chars>args.max_expression_chars:
   if args.diagnose_next:
    candidates=[("row",str(k),str(v)) for k,v in row.items()]+[("trace",str(k),str(v)) for k,v in trace.items()]
    largest=sorted(candidates,key=lambda item:len(item[2]),reverse=True)[:5]
    report={"status":"EXACT_SUPPORT_DIAGNOSTIC_CAP_REACHED_NOT_PROOF",
     "checkpoint_sha256":digest(args.checkpoint.read_bytes()),"processed_saved":processed,
     "next_original_id":rid,"stage":stage,"pivot":list(pivot) if pivot is not None else None,
     "columns":len(row),"column_cap":column_cap,"source_support":len(trace),"row_expression_chars":row_chars,
     "provenance_expression_chars":trace_chars,"max_expression_chars":args.max_expression_chars,
     "largest_entries":[{"kind":a,"key":b,"chars":len(c),"preview":c[:240]} for a,b,c in largest],
     "checkpoint_modified":False,"exact_target_reduction_proven":False}
    args.diagnostic_output.parent.mkdir(parents=True,exist_ok=True)
    args.diagnostic_output.write_text(json.dumps(report,indent=2)+"\\n",encoding="utf-8")
    print("VP05_SECTOR202_EXACT_SUPPORT_CAP_DIAGNOSTIC "+json.dumps(report,ensure_ascii=True),flush=True)
   raise RuntimeError("Safety cap exceeded at %s original ID %d: columns=%d support=%d row_chars=%d trace_chars=%d"%(stage,rid,len(row),len(trace),row_chars,trace_chars))
 fill_steps=[]
 def save_fill(rid,status):
  if not args.trace_fill:return
  report={"status":status,"source_checkpoint_sha256":digest(args.checkpoint.read_bytes()),
   "saved_processed":saved["processed"],"next_original_id":rid,
   "steps":fill_steps,"max_columns_observed":max((x["after_columns"] for x in fill_steps),default=0),
   "checkpoint_modified":False,"exact_target_reduction_proven":False}
  args.fill_output.parent.mkdir(parents=True,exist_ok=True)
  args.fill_output.write_text(json.dumps(report,indent=2)+"\\n",encoding="utf-8")
  print("VP05_SECTOR202_FILL_TRACE "+json.dumps({"status":status,"next_original_id":rid,"step_count":len(fill_steps),"max_columns_observed":report["max_columns_observed"],"output":str(args.fill_output),"checkpoint_modified":False}),flush=True)
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
   if args.trace_fill:
    previous_keys=set(cur);basis_keys=set(brow)
    before_columns=len(cur)
    pivot_support=len(brow)
    novel_columns=len(basis_keys-previous_keys)
   subtract(cur,brow,factor)
   subtract(trace,btrace,factor)
   if args.factor_elimination:
    before_row=max((len(str(v)) for v in cur.values()),default=0)
    before_trace=max((len(str(v)) for v in trace.values()),default=0)
    if max(before_row,before_trace)>=args.factor_trigger_chars:
     cur={k:compact_exact(v) for k,v in cur.items()}
     trace={k:compact_exact(v) for k,v in trace.items()}
     print("VP05_SECTOR202_EXACT_FACTOR_ELIMINATION "+json.dumps({"original_id":rid,"pivot":list(lead),"row_chars_before":before_row,"trace_chars_before":before_trace,"row_chars_after":max((len(str(v)) for v in cur.values()),default=0),"trace_chars_after":max((len(str(v)) for v in trace.values()),default=0)}),flush=True)
   if args.trace_fill:
    fill_steps.append({"step":len(fill_steps)+1,"pivot":list(lead),
      "before_columns":before_columns,"pivot_row_columns":pivot_support,
      "new_columns_from_pivot":novel_columns,"after_columns":len(cur),
      "actual_fill_delta":len(cur)-before_columns,"source_support_after":len(trace),
      "row_chars_after":max((len(str(v)) for v in cur.values()),default=0),
      "trace_chars_after":max((len(str(v)) for v in trace.values()),default=0)})
   if args.trace_fill and (len(cur)>args.max_intermediate_columns or len(trace)>args.max_source_support or max([len(str(v)) for v in list(cur.values())+list(trace.values())] or [0])>args.max_expression_chars):
    save_fill(rid,"FILL_TRACE_SAFETY_CAP_REACHED_NOT_PROOF")
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
  if args.trace_fill:save_fill(ids[limit-1],"FILL_TRACE_NEXT_ROW_WITHIN_CAPS")
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
