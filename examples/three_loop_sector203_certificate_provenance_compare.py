"""Audit old VP05 witness against saved modular certificate, without assuming unique heads.

Original SYSTEM row_index is authoritative for the old witness. Legacy modular
exports contain only (file,equation_id), so ambiguous duplicate heads with
different equation content are reported as unresolved, never guessed.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
from examples.three_loop_sector203_small_id_multiterm_scope import read_rows
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_target_rowspace_audit import residue

TARGET={(10,203):"z",(6,203):"-2",(5,201):"2"}
def identity(r):return (r["file"],str(r["equation_id"]))
def signature(r):
 return tuple(sorted((tuple(t["key"]),str(t["coefficient"])) for t in r["terms"]))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT)
 p.add_argument("--new-audit",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_id_expanded_modular.json"))
 p.add_argument("--old-witness",type=Path)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_certificate_provenance_compare.json"))
 a=p.parse_args()
 files=sorted(Path("output/three_loop_integral_family_audit").glob("vp05_candidate4_witness_*.equations.json"))
 oldpath=a.old_witness or (files[-1] if files else None)
 if oldpath is None:p.error("No old witness found; use --old-witness")
 rows=read_rows(a.project)
 groups=defaultdict(list)
 for i,row in enumerate(rows):groups[identity(row)].append(i)
 old=json.loads(oldpath.read_text(encoding="utf-8-sig"))["rows"]
 old_indices=[];old_bad=[]
 for r in old:
  i=r.get("row_index")
  if not isinstance(i,int) or i<0 or i>=len(rows) or identity(r)!=identity(rows[i]) or signature(r)!=signature(rows[i]):
   old_bad.append({"row_index":i,"identity":list(identity(r))})
  else:old_indices.append(i)
 old_set=set(old_indices)
 audit=json.loads(a.new_audit.read_text(encoding="utf-8-sig"))
 outcomes=[]
 for entry in audit["results"]:
  if entry["scope"]!="entire_system" or entry["test"]!="target_combination":continue
  prime,z,d=entry["point"]
  saved=entry.get("coefficients_mod_prime",[])
  ambiguity=[]
  mapped=[]
  for item in saved:
   key=identity(item)
   candidates=groups.get(key,[])
   if "row_index" in item:
    i=item["row_index"]
    if not isinstance(i,int) or i not in candidates:
     ambiguity.append({"identity":list(key),"reason":"invalid supplied row_index"})
     continue
   elif len(candidates)==1:i=candidates[0]
   elif candidates and len({signature(rows[j]) for j in candidates})==1:
    # Equivalent original coefficient rows: safe for replay but not for support-ID identity.
    i=candidates[0]
   else:
    ambiguity.append({"identity":list(key),"reason":"duplicate equation head has distinct raw rows or is missing"})
    continue
   mapped.append((i,int(item["coefficient"])%prime,len(candidates)))
  ambiguous_support=sum(n>1 and "row_index" not in item for (_,_,n),item in zip(mapped,saved)) if not ambiguity else None
  # For ambiguous duplicate identities with identical terms, replay is valid,
  # but original row-ID overlap is not established.
  actual={}
  for i,multiplier,_ in mapped:
   for key,value in mod_rows([rows[i]],prime,z,d)[0].items():
    val=(actual.get(key,0)+multiplier*value)%prime
    if val:actual[key]=val
    else:actual.pop(key,None)
  expected={k:residue(v,prime,z,d) for k,v in TARGET.items()}
  expected={k:v for k,v in expected.items() if v}
  new_ids={i for i,_,n in mapped if n==1}
  old_unambiguous={i for i in old_set if len(groups[identity(rows[i])])==1}
  outcomes.append({"point":[prime,z,d],"saved_coefficient_count":len(saved),
   "unambiguous_new_id_count":len(new_ids),"ambiguous_duplicate_head_count":sum(n>1 for _,_,n in mapped)+len(ambiguity),
   "unresolved_ambiguous_entries":ambiguity[:20],"unresolved_ambiguous_count":len(ambiguity),
   "unambiguous_id_intersection":len(new_ids&old_unambiguous),
   "new_unambiguous_only":len(new_ids-old_set),
   "old_unambiguous_only":len(old_unambiguous-new_ids),
   "replay_from_saved_coefficients_verified":not ambiguity and actual==expected,
   "exact_support_identity_verified":not ambiguity and all(n==1 for _,_,n in mapped) and len(new_ids)==len(saved) and new_ids==old_set,
   "source_reported_replay":entry["replay_verified"]})
 result={"old_source":str(oldpath),"new_source":str(a.new_audit),
  "old_source_sha256":hashlib.sha256(oldpath.read_bytes()).hexdigest(),
  "new_source_sha256":hashlib.sha256(a.new_audit.read_bytes()).hexdigest(),
  "system_rows":len(rows),"duplicate_head_groups":sum(len(v)>1 for v in groups.values()),
  "old_rows":len(old),"old_rows_valid_by_original_index":len(old_indices),
  "old_invalid_count":len(old_bad),"old_invalid_sample":old_bad[:10],
  "points":outcomes,"symbolic_proof":False,
  "warning":"Legacy saved modular coefficients lack original row_index. Equal duplicate-head rows permit replay but not exact per-row provenance. Distinct duplicate-head rows are unresolved until modular export records original row_index."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("VP05_CERTIFICATE_PROVENANCE_COMPARE "+json.dumps({**result,"output":str(a.output)}),flush=True)
 if old_bad or not all(x["replay_from_saved_coefficients_verified"] for x in outcomes):raise SystemExit(1)
if __name__=="__main__":main()
