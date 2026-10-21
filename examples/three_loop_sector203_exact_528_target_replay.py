"""Final VP05 exact certificate lift and independent original-528 equation replay.

Requires 166 individual exact group certificates, matching input hashes and
the completed 166-row target certificate. Does not trust manifest flags alone.
"""
from __future__ import annotations
import argparse,hashlib,json,multiprocessing as mp,queue
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_exact_target_engine import TARGET,OUT as CERT
from examples.three_loop_sector203_exact_group_lift import coefficients
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS
from examples.three_loop_sector203_exact_group_batch import ROOT

OUT=Path("output/three_loop_integral_family_audit/vp05_original_528_exact_target_certificate.json")
def sha(data):return hashlib.sha256(data).hexdigest()
def worker(a,q):
 try:
  raw=a.equations.read_bytes();wraw=a.witness.read_bytes()
  src=json.loads(raw.decode("utf-8-sig"))["rows"]
  witness=json.loads(wraw.decode("utf-8-sig"))["rows"]
  cert=json.loads(a.certificate.read_text(encoding="utf-8-sig"))
  manifest=json.loads((a.directory/"manifest.json").read_text(encoding="utf-8"))
  if len(src)!=166 or len(witness)!=528:raise ValueError("Wrong source row count")
  if cert.get("source_sha256")!=sha(raw):raise ValueError("Target source SHA mismatch")
  proof=cert.get("symbolic_result",{})
  if proof.get("target_symbolic_proof") is not True or proof.get("compressed_source_exact_replay") is not True:raise ValueError("Incomplete exact target certificate")
  if manifest.get("compressed_sha256")!=sha(raw) or manifest.get("witness_sha256")!=sha(wraw):raise ValueError("Manifest source SHA mismatch")
  if set(manifest["success"])!={str(i) for i in range(166)}:raise ValueError("Missing exact group provenance")
  z,d=sp.symbols("z d")
  coeffs=proof.get("certificate_coefficients",[])
  if len(coeffs)!=166 or {x["row"] for x in coeffs}!=set(range(166)):raise ValueError("Invalid compressed target support")
  c={item["row"]:sp.sympify(item["coefficient"].replace("^","**"),locals={"z":z,"d":d}) for item in coeffs}
  # Coefficient expansion in 528-row LIST order, never by nonunique equation_id.
  weights={}
  for i in range(166):
   entry=manifest["success"][str(i)]
   path=a.directory/entry["file"]
   if path.name!=f"group_{i:03d}.json" or sha(path.read_bytes())!=entry["sha256"]:raise ValueError(f"Group artifact hash mismatch {i}")
   group=json.loads(path.read_text(encoding="utf-8-sig"))
   if group.get("compressed_sha256")!=sha(raw) or group.get("witness_sha256")!=sha(wraw):raise ValueError(f"Group input SHA mismatch {i}")
   row=group["rows"][0]
   if row.get("compressed_row")!=i or row.get("exact_replay_verified") is not True:raise ValueError(f"Missing exact replay {i}")
   members=src[i]["original_rows"]
   if row.get("group_size")!=len(members):raise ValueError("Group size mismatch")
   seen=set()
   for item in row["weights"]:
    j=item["witness_list_index"]
    if j not in members or j in seen or witness[j]["row_index"]!=item["system_row_index"]:raise ValueError(f"Source witness identity mismatch {i}")
    seen.add(j)
    factor=sp.sympify(item["coefficient"].replace("^","**"),locals={"z":z,"d":d})
    weights[j]=weights.get(j,0)+c[i]*factor
   if (i+1)%20==0:print("VP05_528_COMPOSE_STAGE "+json.dumps({"verified_groups":i+1}),flush=True)
  print("VP05_528_COMPOSE_STAGE "+json.dumps({"stage":"original_replay_start","active_witness_rows":len(weights)}),flush=True)
  target={k:sp.sympify(v,locals={"z":z,"d":d}) for k,v in TARGET.items()}
  replay={}
  for count,(j,v) in enumerate(sorted(weights.items()),1):
   if v==0:continue
   for key,coefficient in coefficients(witness[j],z,d).items():
    replay[key]=replay.get(key,0)+v*coefficient
   if count%40==0:print("VP05_528_COMPOSE_STAGE "+json.dumps({"source_rows_replayed":count,"total_source_rows":len(weights)}),flush=True)
  errors=[]
  for key in set(replay)|set(target):
   if sp.cancel(replay.get(key,0)-target.get(key,0))!=0:
    errors.append(list(key))
    if len(errors)>=5:break
  if errors:raise AssertionError("Original 528-row symbolic replay differs at columns "+str(errors))
  result={"status":"PASS","target_symbolic_proof":True,
    "original_528_row_exact_replay_verified":True,"original_source_rows_total":528,
    "original_source_rows_used":sum(sp.cancel(v)!=0 for v in weights.values()),
    "source_sha256":sha(raw),"witness_sha256":sha(wraw),
    "target_certificate_sha256":sha(a.certificate.read_bytes()),
    "manifest_sha256":sha((a.directory/"manifest.json").read_bytes()),
    "original_row_coefficients":[{"witness_list_index":j,
      "system_row_index":witness[j]["row_index"],"coefficient":str(sp.cancel(v))}
      for j,v in sorted(weights.items()) if sp.cancel(v)!=0]}
  a.output.parent.mkdir(parents=True,exist_ok=True)
  tmp=a.output.with_suffix(".json.tmp")
  tmp.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  tmp.replace(a.output)
  q.put(("ok",{"active_original_rows":result["original_source_rows_used"]}))
 except Exception as e:q.put(("error",type(e).__name__+": "+str(e)))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--equations",type=Path,default=DEFAULT)
 p.add_argument("--witness",type=Path,default=WITNESS)
 p.add_argument("--certificate",type=Path,default=CERT)
 p.add_argument("--directory",type=Path,default=ROOT)
 p.add_argument("--output",type=Path,default=OUT)
 p.add_argument("--timeout",type=int,default=1800)
 a=p.parse_args()
 if not 1<=a.timeout<=86400:p.error("Invalid timeout")
 q=mp.Queue();child=mp.Process(target=worker,args=(a,q));child.start();child.join(a.timeout)
 if child.is_alive():
  child.terminate();child.join()
  print("VP05_528_EXACT_TARGET_STATUS "+json.dumps({"status":"TIMEOUT","original_528_row_exact_replay_verified":False}),flush=True)
  raise SystemExit(2)
 try:status,detail=q.get(timeout=3)
 except queue.Empty:raise SystemExit("Worker exited without a result")
 if status!="ok":
  print("VP05_528_EXACT_TARGET_STATUS "+json.dumps({"status":"FAILED","reason":detail,"original_528_row_exact_replay_verified":False}),flush=True)
  raise SystemExit(1)
 print("VP05_528_EXACT_TARGET_STATUS "+json.dumps({"status":"PASS",**detail,"original_528_row_exact_replay_verified":True,"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
