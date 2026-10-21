"""Audit a pre-existing Kira monitored-runner before any physical reduction.

Non-executing review of safety-critical process and resource limits.
Only reports static evidence; cannot certify an actual runtime guard.
"""
from __future__ import annotations
import argparse,ast,hashlib,json,re
from pathlib import Path
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT

OUT=Path("output/three_loop_integral_family_audit/vp05_single_nonmaster_guard_review.json")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source-project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--prepared-project",type=Path,default=Path("output/vp05_single_nonmaster_reduction_prepared"))
 p.add_argument("--plan",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_single_nonmaster_full_stage_plan.json"))
 p.add_argument("--output",type=Path,default=OUT)
 a=p.parse_args()
 runner=a.source_project/"sector203_monitored_kira.py"
 errs=[];findings={}
 if not runner.is_file():errs.append("Missing existing Kira monitor source")
 if not a.plan.is_file():errs.append("Full stage plan missing")
 else:
  plan=json.loads(a.plan.read_text(encoding="utf-8-sig"))
  if plan.get("status")!="FULL_STAGE_PLAN_ONLY" or plan.get("ready_to_execute") is not False:
   errs.append("Plan is not reviewed-only FULL_STAGE_PLAN_ONLY")
 if not a.prepared_project.is_dir():errs.append("Prepared project missing")
 if runner.is_file():
  code=runner.read_text(encoding="utf-8-sig")
  tree=ast.parse(code)
  options=sorted({flag for flag in re.findall(r'["\'](--[a-z][a-z0-9-]+)["\']',code)})
  identifiers=sorted({node.id for node in ast.walk(tree) if isinstance(node,ast.Name)})
  probes={
   "subprocess_present":bool(re.search(r"subprocess|Popen",code)),
   "process_signal_or_termination_present":bool(re.search(r"terminate|kill|SIGTERM|SIGKILL|send_signal",code)),
   "memory_or_swap_observation_present":bool(re.search(r"MemAvailable|Swap|memory|swap|meminfo",code,re.I)),
   "elapsed_time_observation_present":bool(re.search(r"monotonic|time\.time|perf_counter",code)),
   "stop_threshold_option_present":any("stop" in s for s in options),
   "maximum_runtime_option_present":any(x in s for s in options for x in ("duration","timeout","max-hours")),
   "project_root_guard_present":bool(re.search(r"project root",code,re.I)),
   "log_overwrite_refusal_present":bool(re.search(r"refusing to overwrite",code,re.I))
  }
  findings={"source":str(runner),"source_sha256":hashlib.sha256(runner.read_bytes()).hexdigest(),
    "cli_options":options,"probes":probes,
    "source_snippets":[{"line":i,"text":line.strip()[:230]} for i,line in enumerate(code.splitlines(),1)
       if re.search(r"warn|stop|duration|interval|SIG|kill|terminate|refusing to overwrite|project root|swap|memory",line,re.I)][:40]}
 else:findings={}
 report={"status":"GUARD_SOURCE_REVIEW_ONLY" if not errs else "BLOCKED",
  "errors":errs,"monitor":findings,
  "schema_validated_by_kira":False,"runtime_limits_verified":False,
  "ready_to_execute":False,"kira_executed":False,
  "next_requirement":"Human review of exact monitor command invocation, Kira version and schema; non-executing static inspection is not a memory/time limit guarantee."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_SINGLE_NONMASTER_GUARD_REVIEW "+json.dumps(report,ensure_ascii=False),flush=True)
 if errs:raise SystemExit(2)
if __name__=="__main__":main()
