"""Bounded read-only modular span audit for VP05 sector202 saved L2 equations.

Finite-field checks are diagnostics, NOT exact symbolic coefficients/proofs.
Keep Kira opaque small-ID columns intact; never equate them with masters.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_sector203_ffrank_audit import equations,insert
from examples.three_loop_vp05_sector202_target_id_bridge import TARGETS
PROJECT=ROOT/"output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734"
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--max-fill",type=int,default=15000)
 ap.add_argument("--max-seconds",type=float,default=90.0)
 ap.add_argument("--max-rows",type=int,default=2678)
 a=ap.parse_args()
 m=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
 bits,ordering=m.from_kiradb(str(PROJECT/"results/kira.db"))
 if ordering!=5:raise ValueError("Unexpected codec")
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 target_keys=[(codec.encode(x),139) for x in TARGETS]
 files=sorted((PROJECT/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
 pivots={};present=set();start=time.monotonic();processed=0;error=None
 try:
  for file in files:
   for row in equations(file,1000003,17,7):
    if processed>=a.max_rows:break
    if time.monotonic()-start>a.max_seconds:raise TimeoutError("wall-time budget exceeded")
    present.update(row)
    insert(row,pivots,1000003,a.max_fill)
    processed+=1
   if processed>=a.max_rows:break
 except Exception as exc:error=type(exc).__name__+": "+str(exc)[:200]
 probes=[]
 if error is None and processed==2678:
  for x,key in zip(TARGETS,target_keys):
   if key not in present:
    probes.append({"exponents":list(x),"present":False})
    continue
   after=pivots.copy()
   try:
    inc=insert({key:1},after,1000003,a.max_fill)
    probes.append({"exponents":list(x),"present":True,"in_raw_saved_rowspan_mod_p":not inc})
   except Exception as exc:probes.append({"exponents":list(x),"present":True,"error":str(exc)[:150]})
 print("VP05_SECTOR202_SAVED_MODULAR_SPAN "+json.dumps({
  "status":"COMPLETE_FINITE_FIELD_DIAGNOSTIC" if error is None and processed==2678 else "INCOMPLETE_RESOURCE_BOUNDED",
  "equations_processed":processed,"equations_expected":2678,"rank":len(pivots),
  "unique_columns_seen":len(present),"prime":1000003,"z":17,"d":7,
  "raw_target_rowspace_probes":probes,"error":error,
  "max_seconds":a.max_seconds,"max_fill":a.max_fill,
  "warning":"Raw rowspace is not quotient modulo master basis. A target absent from raw rowspace may still reduce to masters; no exact coefficients are reconstructed.",
  "kira_executed":False,"files_modified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
