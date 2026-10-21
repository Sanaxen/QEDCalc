"""Safe, non-executing audit of VP05 Kira monitor timeout/swap termination logic.

Static AST inspection plus synthetic predicate truth table. Never spawns Kira
or test subprocesses, never sends signals, and never claims runtime validation.
"""
from __future__ import annotations
import argparse,ast,hashlib,json,re
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source-project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_monitor_stop_logic_preflight.json"))
 a=p.parse_args()
 f=a.source_project/"sector203_monitored_kira.py"
 if not f.is_file():p.error("Original monitor source absent")
 source=f.read_text(encoding="utf-8-sig")
 tree=ast.parse(source)
 predicates={
  "explicit_max_seconds_option":bool(re.search(r'add_argument\([\x22\x27]--max-seconds',source)),
  "time_stop_reason":'reason = "time_stop"' in source or "reason = 'time_stop'" in source,
  "swap_stop_reason":'reason = "swap_stop"' in source or "reason = 'swap_stop'" in source,
  "process_group_term":bool(re.search(r"os\.killpg\(proc\.pid,\s*signal\.SIGTERM\)",source)),
  "process_group_kill":bool(re.search(r"os\.killpg\(proc\.pid,\s*signal\.SIGKILL\)",source)),
  "timeout_exit_code":bool(re.search(r"124\s+if\s+reason\s*==\s*[\x22\x27]time_stop",source)),
  "swap_exit_code":bool(re.search(r"125\s+if\s+reason\s*==\s*[\x22\x27]swap_stop",source)),
  "no_unbounded_runtime_assumed":True}
 # Truth table is reference model, NOT execution of script predicates.
 cases=[]
 for max_seconds in (0,30):
  for elapsed in (0,31):
   for swap,stop in ((0,10),(11,10)):
    reason="swap_stop" if swap>=stop else ("time_stop" if max_seconds and elapsed>=max_seconds else None)
    cases.append({"max_seconds":max_seconds,"elapsed_seconds":elapsed,
      "swap_used_gib":swap,"swap_stop_gib":stop,"expected_reference_reason":reason})
 report={"status":"STATIC_STOP_LOGIC_REVIEW_ONLY",
   "monitor":str(f),"source_sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
   "checks":predicates,"all_static_checks_pass":all(predicates.values()),
   "reference_truth_table":cases,
   "runtime_stop_test_executed":False,"actual_process_termination_verified":False,
   "ready_to_execute_kira":False,
   "requirement":"Separate controlled subprocess test, monitored RAM and swap safety policy, Kira schema validation and user approval before full reduction."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print("VP05_MONITOR_STOP_LOGIC "+json.dumps({k:v for k,v in report.items() if k!="reference_truth_table"}),flush=True)
 if not report["all_static_checks_pass"]:raise SystemExit(2)
if __name__=="__main__":main()
