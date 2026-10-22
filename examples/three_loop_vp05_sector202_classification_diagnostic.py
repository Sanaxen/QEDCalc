"""Read-only diagnosis of sector 202 restricted FireFly classification.

A successful classification does not imply retention of every candidate.
This audit makes no automatic basis or registry changes.
"""
from __future__ import annotations
import json
from pathlib import Path
from three_loop.master_basis_batch import AUDIT_DIR

FILE="three_loop_vp05_full_firefly_numerator_r8s3d0_r6s6d2_sec202_audit.json"
FIELDS=("schema_version","stage","family","sector","firefly_seed","audit_pass",
        "conclusion","targets","target_status","target_classification",
        "target_classifications","master_count","master_integrals",
        "master_masters","masters","missing_targets","unresolved_targets",
        "errors","pass","checks")
def main():
 path=AUDIT_DIR/FILE
 if not path.is_file():
  raise SystemExit(f"Missing original restricted audit: {path}")
 data=json.loads(path.read_text(encoding="utf-8-sig"))
 if data.get("sector")!=202 or str(data.get("firefly_seed"))!="r6s6d2":
  raise SystemExit("Saved sector/seed mismatch; refusing diagnostic")
 selected={key:data[key] for key in FIELDS if key in data}
 extra={}
 for key,val in data.items():
  if key not in selected:
   if isinstance(val,(dict,list)):extra[key]={"type":type(val).__name__,"length":len(val)}
   else:extra[key]=str(val)[:200]
 report={"status":"VP05_STAGE2_SECTOR202_CLASSIFICATION_DIAGNOSTIC",
  "source":str(path),"selected_evidence":selected,"other_fields":extra,
  "conclusion_requires_review":True,
  "proves_all_three_sector202_candidates_retained":False,
  "authorizes_candidate_refinement":False,
  "authorizes_promotion":False,
  "kira_executed":False,"source_modified":False}
 print("VP05_STAGE2_SECTOR202_CLASSIFICATION "+json.dumps(report,ensure_ascii=False,default=str),flush=True)
if __name__=="__main__":main()
