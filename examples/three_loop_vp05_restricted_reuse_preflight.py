"""Read-only reuse preflight for VP05 missing candidate closure at sector granularity.

Uses the SAME strict restricted-equivalence predicate already implemented
in the generic Stage-2 candidate sector closure; never substitutes unrelated
seeds or a single-target certificate.
"""
from __future__ import annotations
import json,re
from collections import defaultdict
from three_loop.master_basis_batch import AUDIT_DIR
from three_loop.master_basis_api import Seed
from examples.three_loop_master_basis_candidate_sector_closure import _restricted_equivalent_audit
STEM="three_loop_vp05_full_masters_r8s3d0"
SEEDS=(Seed(8,6,2),Seed(8,5,3))
def sector(t):
 nums=tuple(map(int,re.fullmatch(r"VP05_full\[(-?\d+(?:,-?\d+){11})\]",t).group(1).split(",")))
 return sum((1<<i) for i,n in enumerate(nums) if n>0)
def main():
 p=AUDIT_DIR/f"{STEM}_candidate_r8s5d2_closure_manifest.json"
 d=json.loads(p.read_text(encoding="utf-8-sig"))
 if d.get("family")!="VP05_full" or d.get("candidate_master_count")!=63:raise RuntimeError("VP05 saved 63-candidate manifest mismatch")
 groups=defaultdict(list)
 for t in d["candidate_masters"]:groups[sector(t)].append(t)
 if len(groups)!=26 or sum(map(len,groups.values()))!=63:raise RuntimeError("Unexpected sector grouping")
 rows=[]
 for seed in SEEDS:
  items=[]
  for sec,targets in sorted(groups.items()):
   ok,reason=_restricted_equivalent_audit("VP05_full",Seed(8,3,0),seed,sec,targets)
   items.append({"sector":sec,"candidate_count":len(targets),"effective_seed":f"r{min(seed.r,sec.bit_count()+seed.d)}s{seed.s}d{seed.d}",
                 "strict_restricted_equivalence_pass":ok,"explanation":reason})
  rows.append({"seed":seed.tag,"strict_reuse_count":sum(x["strict_restricted_equivalence_pass"] for x in items),
               "still_missing_count":sum(not x["strict_restricted_equivalence_pass"] for x in items),"sectors":items})
 print("VP05_STAGE2_RESTRICTED_REUSE "+json.dumps({
  "status":"VP05_STAGE2_RESTRICTED_REUSE_PREFLIGHT","family":"VP05_full",
  "candidate_count":63,"sector_count":26,"rows":rows,
  "note":"Strict matched audits are evidence for exact-sector target retention, not by themselves authorization for whole-family promotion.",
  "whole_family_promotion_allowed":False,"kira_executed":False,"files_modified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
