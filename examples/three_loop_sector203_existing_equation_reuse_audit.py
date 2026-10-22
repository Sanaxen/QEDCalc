"""Read-only inventory of existing VP05 target equations and certificate gap.

No Kira execution, no source modifications, and no claim of exact target proof.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path("output/three_loop_integral_family_audit")
SOURCES={
 "compressed_equations":ROOT/"vp05_target_symbolic_compressed.equations.json",
 "coefficient_groups":ROOT/"vp05_target_coefficient_structure.json",
 "crt_candidate":ROOT/"vp05_two_prime_crt_candidate_audit.json",
 "exact_replay":ROOT/"vp05_exact_compressed_certificate_replay.json",
}
def describe(path):
 if not path.is_file() or path.is_symlink():
  return {"exists":False,"path":str(path)}
 raw=path.read_bytes()
 try:data=json.loads(raw.decode("utf-8-sig"))
 except (ValueError,UnicodeError):return {"exists":True,"json_valid":False,"path":str(path)}
 result={"exists":True,"json_valid":True,"path":str(path),
         "bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()}
 if isinstance(data,dict):
  for key in ("type","original_rows","original_terms","compressed_terms",
              "algebraic_combinations_exact","target_coefficient_ratios_proven",
              "target_identity_proven"):
   if key in data:result[key]=data[key]
  if isinstance(data.get("rows"),list):result["row_count"]=len(data["rows"])
  if isinstance(data.get("summary"),dict):
   result["summary"]={key:data["summary"].get(key) for key in (
    "columns_total","columns_checked","exact_compressed_certificate_verified",
    "original_528_equation_replay","integral_alias_mapping_verified",
    "verdict_counts") if key in data["summary"]}
 return result

def main():
 report={name:describe(path) for name,path in SOURCES.items()}
 compressed=report["compressed_equations"]
 report["reuse_candidate_present"]=(compressed.get("row_count")==166 and
  compressed.get("original_rows")==528 and
  compressed.get("algebraic_combinations_exact") is True)
 replay=report["exact_replay"].get("summary",{})
 report["full_target_identity_proven"]=bool(
  replay.get("exact_compressed_certificate_verified") and
  replay.get("original_528_equation_replay") and
  replay.get("integral_alias_mapping_verified"))
 report["status"]="REUSE_INPUTS_PRESENT_PROOF_PENDING" if report["reuse_candidate_present"] else "REUSE_INPUTS_MISSING_OR_INCOMPLETE"
 report["kira_executed"]=False
 report["source_files_modified"]=False
 print("VP05_EXISTING_EQUATION_REUSE_AUDIT "+json.dumps(report,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
