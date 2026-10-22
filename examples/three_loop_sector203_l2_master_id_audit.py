"""Read-only master-numbering consistency audit for original VP05 L2 SYSTEM.

Compares the exact small-ID-to-exponents bridge against positions in the saved
Kira master list. Position matches are only hypotheses, not Kira ID definitions.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT as PROJECT
from examples.three_loop_sector203_weight_audit import load_codec,parse_file_integrals
TARGETS=((10,203),(6,203),(5,201))
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--project",type=Path,default=PROJECT)
 ap.add_argument("--codec-file",type=Path,default=Path("output/tools/pyred_weight.py"))
 ap.add_argument("--bridge-report",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_id_exact_alias_bridges.json"))
 a=ap.parse_args()
 db=a.project/"results/kira.db";master=a.project/"results/VP05_full/masters"
 if not db.is_file() or not master.is_file():ap.error("Missing original L2 Kira database or master file")
 if not a.codec_file.is_file():ap.error("Missing external codec: "+str(a.codec_file))
 m=load_codec(a.codec_file.resolve())
 bits,ordering=m.from_kiradb(str(db))
 if ordering!=5:ap.error("Expected integral ordering 5")
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 exponents=parse_file_integrals(master)
 if not exponents:ap.error("Master file did not contain integral tuples")
 entries=[]
 for idx,x in enumerate(exponents):
  weight=int(codec.encode(x));roundtrip=tuple(map(int,codec.decode(weight)))==tuple(x)
  if not roundtrip:raise RuntimeError("Master weight roundtrip mismatch at "+str(idx))
  entries.append({"position_one_based":idx+1,"position_zero_based":idx,
   "exponents":list(x),"weight":weight,"mathematical_sector":int(m.sec_of(x))})
 bridge_data=json.loads(a.bridge_report.read_text(encoding="utf-8-sig"))
 bridge={tuple(i["key"]):i for i in bridge_data.get("target_results",[])}
 targets=[]
 for weight,sector in TARGETS:
  key=(weight,sector);b=bridge.get(key,{})
  alias=tuple(b.get("exponents") or [])
  matches=[e["position_one_based"] for e in entries if alias and tuple(e["exponents"])==alias]
  one_based=[e for e in entries if e["position_one_based"]==weight]
  zero_based=[e for e in entries if e["position_zero_based"]==weight]
  targets.append({"key":list(key),"direct_unit_bridge":b.get("direct_unit_bridge_alias_verified",False),
   "bridge_exponents":list(alias) if alias else None,
   "bridge_matches_master_positions_one_based":matches,
   "master_at_one_based_numeric_id":one_based,
   "master_at_zero_based_numeric_id":zero_based,
   "numeric_position_identity_proven":False})
 report={"status":"MASTER_POSITION_HYPOTHESIS_ONLY","project":str(a.project.resolve()),
  "master_count":len(entries),"master_entries":entries,"targets":targets,
  "db_sha256":hashlib.sha256(db.read_bytes()).hexdigest(),
  "master_sha256":hashlib.sha256(master.read_bytes()).hexdigest(),
  "codec_sha256":hashlib.sha256(a.codec_file.read_bytes()).hexdigest(),
  "bridge_report_sha256":hashlib.sha256(a.bridge_report.read_bytes()).hexdigest(),
  "master_numbering_convention_verified":False,
  "physical_propagator_mapping_verified":False,"kira_executed":False,"source_files_modified":False}
 print("VP05_L2_MASTER_ID_AUDIT "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
