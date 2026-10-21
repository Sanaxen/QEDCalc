"""Persistent per-group controller for exact VP05 166-to-528 provenance.

Calls the already tested bounded group solver once per child process.
Outputs a durable manifest with SHA fingerprints; a FAILED/TIMEOUT row
does not erase prior successful proofs. No final 528-row target proof claimed.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,time
from pathlib import Path
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS

ROOT=Path("output/three_loop_integral_family_audit/vp05_exact_group_lifts")
def atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_suffix(path.suffix+".tmp")
 tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 tmp.replace(path)
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--equations",type=Path,default=DEFAULT)
 p.add_argument("--witness",type=Path,default=WITNESS)
 p.add_argument("--directory",type=Path,default=ROOT)
 p.add_argument("--max-groups",type=int,default=10,help="Maximum groups attempted this invocation")
 p.add_argument("--max-group-size",type=int,default=4)
 p.add_argument("--per-group-timeout",type=int,default=120)
 p.add_argument("--stop-on-failure",action="store_true")
 a=p.parse_args()
 if not 1<=a.max_groups<=166:p.error("max-groups out of bounds")
 if not 1<=a.max_group_size<=68:p.error("max-group-size out of bounds")
 if not 1<=a.per_group_timeout<=3600:p.error("per-group-timeout out of bounds")
 source=json.loads(a.equations.read_text(encoding="utf-8-sig"))
 groups=source["rows"]
 if len(groups)!=166:p.error("Expected 166 groups")
 if not a.witness.exists():p.error("528 witness source missing")
 identity={"compressed_sha256":hashlib.sha256(a.equations.read_bytes()).hexdigest(),
           "witness_sha256":hashlib.sha256(a.witness.read_bytes()).hexdigest()}
 manifest=a.directory/"manifest.json"
 if manifest.exists():
  state=json.loads(manifest.read_text(encoding="utf-8"))
  if any(state.get(k)!=v for k,v in identity.items()):p.error("Input SHA mismatch; use a fresh directory")
 else:
  state={**identity,"success":{},"attempts":{},"full_exact_lift_verified":False,
         "original_528_row_target_replay_verified":False}
 todo=sorted(range(166),key=lambda i:(len(groups[i]["original_rows"]),i))
 attempts=0
 for i in todo:
  n=len(groups[i]["original_rows"])
  if n>a.max_group_size or str(i) in state["success"]:continue
  filename=a.directory/(f"group_{i:03d}.json")
  if filename.exists():filename.unlink()
  cmd=[sys.executable,"-m","examples.three_loop_sector203_exact_group_lift",
       "--equations",str(a.equations),"--witness",str(a.witness),
       "--start",str(i),"--count","1","--max-group-size",str(a.max_group_size),
       "--timeout",str(a.per_group_timeout),"--output",str(filename)]
  print("VP05_GROUP_BATCH_START "+json.dumps({"row":i,"group_size":n}),flush=True)
  done=subprocess.run(cmd,check=False)
  attempts+=1
  if done.returncode==0 and filename.exists():
   report=json.loads(filename.read_text(encoding="utf-8"))
   valid=(report.get("compressed_sha256")==identity["compressed_sha256"] and
          report.get("witness_sha256")==identity["witness_sha256"] and
          len(report.get("rows",[]))==1 and
          report["rows"][0].get("compressed_row")==i and
          report["rows"][0].get("exact_replay_verified") is True)
   if not valid:raise RuntimeError("Unexpected group proof artifact: "+str(filename))
   state["success"][str(i)]={"file":filename.name,"sha256":hashlib.sha256(filename.read_bytes()).hexdigest(),
      "group_size":n}
   status="PASS"
  else:status="TIMEOUT_OR_FAILED"
  state["attempts"][str(i)]=state["attempts"].get(str(i),0)+1
  state["full_exact_lift_verified"]=len(state["success"])==166
  atomic(manifest,state)
  print("VP05_GROUP_BATCH_RESULT "+json.dumps({"row":i,"status":status,
     "total_verified":len(state["success"]),"remaining":166-len(state["success"])}),flush=True)
  if status!="PASS" and a.stop_on_failure:break
  if attempts>=a.max_groups:break
 print("VP05_GROUP_BATCH_SUMMARY "+json.dumps({
   "attempted":attempts,"total_verified":len(state["success"]),
   "all_166_groups_verified":len(state["success"])==166,
   "original_528_row_target_replay_verified":False,"manifest":str(manifest)}),flush=True)
if __name__=="__main__":main()
