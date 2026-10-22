"""Read-only VP05 physical-notation gate: Kira version and propagator definitions.

Verifies the actual saved project topology and preferred target numbering.
Does NOT claim the running executable is the one used historically, or that
a propagator routing has independently been compared to the original diagram.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_weight_audit import parse_file_integrals
from examples.three_loop_sector203_preferred_compact_id_audit import sec
T=(10,6,5)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT)
 a=p.parse_args();root=a.project.resolve()
 job=root/"jobs.yaml";top=root/"config/integralfamilies.yaml";kin=root/"config/kinematics.yaml"
 inp=root/"preferred_provisional64_sector203.txt";saved=root/"results/preferredMasters"
 required=(job,top,kin,inp,saved)
 if not all(f.is_file() for f in required):p.error("Missing saved L2 project input(s)")
 jt=job.read_text(encoding="utf-8-sig");tt=top.read_text(encoding="utf-8-sig")
 kt=kin.read_text(encoding="utf-8-sig")
 preferred=parse_file_integrals(inp);archive=parse_file_integrals(saved)
 # Kira's saved yaml is simple enough to parse 12 ordered propagator entries without PyYAML.
 block=tt.split("    propagators:",1)
 propagators=[]
 if len(block)==2:
  for line in block[1].splitlines():
   m=re.match(r'^\s*-\s*\[\s*["\']([^"\']+)["\']\s*,\s*(.+?)\s*\]\s*$',line)
   if m:propagators.append({"momentum":m.group(1),"mass":m.group(2)})
 expected={10:203,6:203,5:201}
 ids={n:{"integral":"VP05_full["+",".join(map(str,preferred[n-1]))+"]",
          "exponents":list(preferred[n-1]),"sector":sec(preferred[n-1])} for n in T} if len(preferred)>=10 else {}
 checks={
   "job_references_preferred":bool(re.search(r'preferred_masters:\s*["\']?preferred_provisional64_sector203\.txt',jt)),
   "preferred_input_saved_order":len(preferred)==10 and preferred==archive and len(set(preferred))==10,
   "all_three_expected_sectors":len(ids)==3 and all(ids[n]["sector"]==expected[n] for n in T),
   "vp05_topology_named":bool(re.search(r'\bname:\s*["\']?VP05_full\b',tt)),
   "three_loop_momenta":bool(re.search(r'loop_momenta:\s*\[k,\s*l,\s*r\]',tt)),
   "twelve_ordered_propagators":len(propagators)==12,
   "top_level_sector_203":bool(re.search(r'top_level_sectors:\s*\[\s*203\s*\]',tt)),
   "z_and_m2_kinematics":("z" in kt and "m2" in kt)
 }
 version_hits=[]
 for rel in ("kira.log","monitored_kira.log"):
  f=root/rel
  if not f.is_file():continue
  for no,line in enumerate(f.read_text(encoding="utf-8-sig",errors="replace").splitlines(),1):
   if re.search(r'\bKira\b.{0,45}\b(?:version|v?[23]\.\d)|\bversion\s+[23]\.\d',line,re.I):
    version_hits.append({"file":rel,"line":no,"text":line.strip()[:250]})
 report={"status":"SAVED_PROJECT_TOPOLOGY_VERIFIED_VERSION_PENDING" if all(checks.values()) else "SAVED_PROJECT_TOPOLOGY_CHECK_INCOMPLETE",
  "checks":checks,"target_integrals":ids,"ordered_propagators":propagators,
  "kinematics_file":str(kin),"version_log_evidence":version_hits[:15],
  "historical_kira_binary_version_verified":False,
  "kira_cpp_semantics_historical_version_verified":False,
  "diagram_to_propagator_momentum_routing_independently_verified":False,
  "symbolic_target_equation":"z*I10 - 2*I6 + 2*I5 = 0",
  "input_sha256":{f.relative_to(root).as_posix():sha(f) for f in required},
  "kira_executed":False,"project_modified":False,
  "note":"Saved Kira project config anchors the integral notation. It does not independently validate physics diagram routing or identify historical executable version."}
 print("VP05_PHYSICAL_NOTATION_GATE "+json.dumps(report,ensure_ascii=False),flush=True)
 if not all(checks.values()):raise SystemExit(2)
if __name__=="__main__":main()
