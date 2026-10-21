"""Read-only exact VP05 provenance batch progress and remaining group sizes."""
import argparse,json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--equations",type=Path,default=DEFAULT)
 p.add_argument("--manifest",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_exact_group_lifts/manifest.json"))
 a=p.parse_args()
 rows=json.loads(a.equations.read_text(encoding="utf-8-sig"))["rows"]
 state=json.loads(a.manifest.read_text(encoding="utf-8"))
 done={int(k) for k in state.get("success",{})}
 if len(rows)!=166 or any(i<0 or i>=166 for i in done):raise ValueError("Unexpected group state")
 pending=sorted(((len(row["original_rows"]),i) for i,row in enumerate(rows) if i not in done))
 print("VP05_GROUP_REMAINING "+json.dumps({
   "verified":len(done),"remaining":len(pending),
   "size_distribution":dict(sorted(Counter(n for n,_ in pending).items())),
   "groups":[{"row":i,"group_size":n,"attempts":state.get("attempts",{}).get(str(i),0)} for n,i in pending],
   "exact_528_target_replay_verified":False}),flush=True)
if __name__=="__main__":main()
