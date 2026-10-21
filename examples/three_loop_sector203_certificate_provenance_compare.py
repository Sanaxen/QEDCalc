"""Compare VP05 old witness and new full-SYSTEM certificate by source equation IDs.

Read-only. Checks provenance sets, exact original coefficient text, and
independently replays saved modular coefficients against original SYSTEM rows.
The certificate vectors can differ between evaluation points even when row IDs match.
"""
from __future__ import annotations
import argparse,glob,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_small_id_multiterm_scope import read_rows
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_target_rowspace_audit import residue

TARGET={(10,203):"z",(6,203):"-2",(5,201):"2"}
def identity(row):return (row["file"],str(row["equation_id"]))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT)
 p.add_argument("--new-audit",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_id_expanded_modular.json"))
 p.add_argument("--old-witness",type=Path,help="Original vp05_candidate4_witness_*.equations.json (defaults to latest matching)")
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_certificate_provenance_compare.json"))
 a=p.parse_args()
 if a.old_witness:
  oldpath=a.old_witness
 else:
  files=sorted(Path("output/three_loop_integral_family_audit").glob("vp05_candidate4_witness_*.equations.json"))
  if not files:p.error("No old witness JSON found; supply --old-witness")
  oldpath=files[-1]
 rows=read_rows(a.project)
 lookup={identity(row):row for row in rows}
 if len(lookup)!=len(rows):p.error("Duplicated SYSTEM (file,equation_id) identities")
 old=json.loads(oldpath.read_text(encoding="utf-8-sig"))["rows"]
 oldmap={identity(r):r for r in old}
 if len(oldmap)!=len(old):p.error("Duplicate old-witness equation identities")
 missing_old=set(oldmap)-set(lookup)
 original_mismatches=[]
 for key in sorted(set(oldmap)&set(lookup)):
  def norm(terms):return sorted((tuple(t["key"]),str(t["coefficient"])) for t in terms)
  if norm(oldmap[key]["terms"])!=norm(lookup[key]["terms"]):original_mismatches.append(key)
 audit=json.loads(a.new_audit.read_text(encoding="utf-8-sig"))
 outcomes=[]
 for entry in audit["results"]:
  if entry["scope"]!="entire_system" or entry["test"]!="target_combination":continue
  point=entry["point"];prime,z,d=point
  saved=entry.get("coefficients_mod_prime",[])
  cmap={identity(x):int(x["coefficient"])%prime for x in saved}
  if len(cmap)!=len(saved):raise ValueError("Duplicate coefficient source identities")
  if not entry["target_in_rowspace"] or not entry["replay_verified"]:raise ValueError("Expected certified full-system result")
  missing=set(cmap)-set(lookup)
  actual={}
  for key,multiplier in cmap.items():
   if key not in lookup:continue
   row=mod_rows([lookup[key]],prime,z,d)[0]
   for var,value in row.items():
    update=(actual.get(var,0)+multiplier*value)%prime
    if update:actual[var]=update
    else:actual.pop(var,None)
  expected={key:residue(coeff,prime,z,d) for key,coeff in TARGET.items()}
  expected={key:value for key,value in expected.items() if value}
  outcomes.append({"point":point,"new_count":len(cmap),"old_count":len(oldmap),
    "intersection_count":len(set(cmap)&set(oldmap)),
    "only_new_count":len(set(cmap)-set(oldmap)),
    "only_old_count":len(set(oldmap)-set(cmap)),
    "only_new_sample":[list(k) for k in sorted(set(cmap)-set(oldmap))[:10]],
    "only_old_sample":[list(k) for k in sorted(set(oldmap)-set(cmap))[:10]],
    "replay_from_saved_coefficients_verified":not missing and actual==expected,
    "missing_new_ids":len(missing)})
 if len(outcomes)!=2:raise ValueError("Expected two full-system target-combination results")
 result={"old_source":str(oldpath),"new_source":str(a.new_audit),
  "old_source_sha256":hashlib.sha256(oldpath.read_bytes()).hexdigest(),
  "new_source_sha256":hashlib.sha256(a.new_audit.read_bytes()).hexdigest(),
  "old_rows":len(old),"old_ids_missing_from_system":len(missing_old),
  "old_exact_term_mismatches":len(original_mismatches),
  "points":outcomes,
  "same_support_all_points":all(x["only_new_count"]==x["only_old_count"]==0 for x in outcomes),
  "symbolic_proof":False,
  "warning":"Matching equation IDs and modular replay do not prove equality of symbolic certificate multipliers or a physical alias."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("VP05_CERTIFICATE_PROVENANCE_COMPARE "+json.dumps({**result,"output":str(a.output)}),flush=True)
 if missing_old or original_mismatches or not all(x["replay_from_saved_coefficients_verified"] for x in outcomes):raise SystemExit(1)
if __name__=="__main__":main()
