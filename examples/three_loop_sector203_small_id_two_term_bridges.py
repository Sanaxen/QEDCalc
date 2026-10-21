"""Audit exact two-term Kira SYSTEM equations connecting tiny IDs to encoded weights.

Two-term rows can imply a scalar proportionality, NOT an unconditional alias.
No Kira execution; preserve coefficients and provenance; no numeric guesses.
"""
from __future__ import annotations
import argparse,gzip,json
from collections import defaultdict
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--project",type=Path,default=DEFAULT)
 ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_id_two_term_bridges.json"))
 a=ap.parse_args()
 bridges=defaultdict(list);equations=0;total_two=0
 for file in sorted((a.project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  with gzip.open(file,"rt",encoding="utf-8") as stream:
   while (mark:=stream.readline()):
    if mark.strip()!="Eq":raise ValueError("Bad SYSTEM marker")
    head=stream.readline().strip();n=int(stream.readline().strip());equations+=1
    terms=[]
    for _ in range(n):
     fields=stream.readline().split()
     if len(fields)<4:raise ValueError("Malformed SYSTEM record")
     terms.append({"key":[int(fields[2]),int(fields[3])],"coefficient":fields[1]})
    if n!=2:continue
    total_two+=1
    if any(1<=t["key"][0]<=10 for t in terms):
     small=[t for t in terms if 1<=t["key"][0]<=10]
     for t in small:
      # Literal relation: sum_j coeff_j * integral_j = 0.
      # In a two-term row with exactly one tiny variable, tiny = -(other/tiny)*normal.
      others=[v for v in terms if v is not t]
      bridge={"file":file.name,"equation_id":head,"small":t,"other":others[0],
        "exact_equation":"("+t["coefficient"]+")*I"+str(tuple(t["key"]))+
        " + ("+others[0]["coefficient"]+")*I"+str(tuple(others[0]["key"]))+" = 0"}
      bridges[tuple(t["key"])].append(bridge)
 if equations!=2678:ap.error("Unexpected project; expected 2678 equations")
 result={"project":str(a.project.resolve()),"system_equations":equations,
    "two_term_equations":total_two,
    "small_id_bridges":[{"small_key":list(key),"two_term_bridge_count":len(items),
       "bridges":items[:40],"truncated":len(items)>40} for key,items in sorted(bridges.items())],
    "small_id_to_unique_encoded_integral_verified":False,
    "warning":"An exact two-term equation proves linear proportionality within SYSTEM variables, not necessarily equal integrals; zero/singular coefficients and multiple bridge targets require checks."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("VP05_SMALL_ID_TWO_TERM_BRIDGES "+json.dumps({**result,"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
