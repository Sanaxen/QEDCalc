"""Inspect original_rows representation without evaluating its provenance as proof."""
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS

def shape(x):
 if isinstance(x,dict):return {"type":"dict","keys":list(x)[:15],"size":len(x),"sample":{k:shape(v) for k,v in list(x.items())[:2]}}
 if isinstance(x,list):return {"type":"list","size":len(x),"first":shape(x[0]) if x else None}
 if isinstance(x,str):return {"type":"str","length":len(x),"sample":x[:180]}
 return {"type":type(x).__name__,"sample":x}
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--equations",type=Path,default=DEFAULT)
 ap.add_argument("--witness",type=Path,default=WITNESS)
 a=ap.parse_args()
 src=json.loads(a.equations.read_text(encoding="utf-8-sig"))
 witness=json.loads(a.witness.read_text(encoding="utf-8-sig"))
 print("VP05_ORIGINAL_ROWS_FORMAT "+json.dumps({
  "compressed_samples":[{"row":i,"original_rows":shape(src["rows"][i].get("original_rows")),"row_fields":list(src["rows"][i])} for i in (0,1,5,82,165)],
  "witness_samples":[{"row":i,"row_fields":list(witness["rows"][i]),"row_index":witness["rows"][i].get("row_index")} for i in (0,1,527)],
  "exact_replay_verified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
