"""Inspect VP05 exact single-target rule against standard Stage-2 candidate basis.

Read-only. A relation involving an out-of-basis integral is NOT itself a
linear dependence among the candidate masters.
"""
from __future__ import annotations
import json,re
from collections import Counter
from three_loop.master_basis_batch import AUDIT_DIR
from three_loop.vp05_verified_reduction import TARGET,MASTER_5,MASTER_6,load_verified_vp05_rule,DEFAULT_ARTIFACT

def parse(s):
 m=re.fullmatch(r"VP05_full\[(-?\d+(?:,-?\d+){11})\]",str(s))
 if m is None:raise ValueError("unexpected candidate format")
 return tuple(map(int,m.group(1).split(",")))
def sector(v):
 return sum(1<<i for i,n in enumerate(v) if n>0)
def main():
 p=AUDIT_DIR/"three_loop_vp05_full_masters_r8s3d0_candidate_r8s5d2_closure_manifest.json"
 d=json.loads(p.read_text(encoding="utf-8-sig"))
 assert d.get("candidate_master_count")==63 and d.get("family")=="VP05_full"
 cand={parse(x) for x in d["candidate_masters"]}
 assert len(cand)==63
 proof=load_verified_vp05_rule(DEFAULT_ARTIFACT)
 assert proof.target==TARGET
 in_sector=[list(x) for x in sorted(cand) if sector(x)==203]
 related={"target":{"exponents":list(TARGET),"in_candidate":TARGET in cand},
  "rhs_6":{"exponents":list(MASTER_6),"in_candidate":MASTER_6 in cand},
  "rhs_5":{"exponents":list(MASTER_5),"in_candidate":MASTER_5 in cand}}
 report={"status":"VP05_STAGE2_CROSS_BASIS_RELATION_AUDIT",
  "candidate_count":len(cand),"sector_203_candidate_count":len(in_sector),
  "sector_203_candidates":in_sector,"relation_terms":related,
  "relation_exactly_verified_from_saved_certificate":True,
  "rhs_outside_basis":MASTER_6 not in cand,
  "proves_63_candidates_linearly_dependent":False,
  "proves_63_candidates_complete":False,
  "proof_of_I6_reducibility_to_standard_63_available":False,
  "next_step":"Find an independently verified I6 -> standard63 identity before treating this as a candidate-basis redundancy; separately settle r8s6d2 and r8s5d3 closure.",
  "kira_executed":False,"sources_modified":False}
 print("VP05_STAGE2_CROSS_BASIS "+json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
