"""Verify exact VP05 certificate column keys using external Kira WeightCodec.

GPL Kira codec remains external. Decode/encode round trip is mandatory.
Record the sector comparison explicitly; lower-sector rankings may differ
between stored SYSTEM labels and Kira codec's computed sector.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_weight_audit import load_codec
from examples.three_loop_sector203_integral_id_source_inventory import DEFAULT_PROJECT
from examples.three_loop_sector203_exact_528_target_replay import OUT as CERT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS

TARGET=((10,203),(6,203),(5,201))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=DEFAULT_PROJECT)
 p.add_argument("--codec-file",type=Path,required=True,help="External Kira bootloops-tools pyred_weight.py (GPL), never vendored")
 p.add_argument("--certificate",type=Path,default=CERT)
 p.add_argument("--witness",type=Path,default=WITNESS)
 p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_target_weight_codec_audit.json"))
 a=p.parse_args()
 if not a.certificate.exists():p.error("Exact 528-row source certificate missing")
 proof=json.loads(a.certificate.read_text(encoding="utf-8-sig"))
 if proof.get("original_528_row_exact_replay_verified") is not True:p.error("Original 528-row exact replay has not PASSed")
 if hashlib.sha256(a.witness.read_bytes()).hexdigest()!=proof.get("witness_sha256"):p.error("Witness SHA mismatch")
 witness=json.loads(a.witness.read_text(encoding="utf-8-sig"))["rows"]
 observed={tuple(t["key"]) for row in witness for t in row["terms"]}
 m=load_codec(a.codec_file.resolve())
 db=a.project/"results/kira.db"
 if not db.is_file():p.error("Original Kira database missing: "+str(db))
 bits,ordering=m.from_kiradb(str(db))
 if ordering!=5:p.error("Expected Kira integral_ordering=5")
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 results=[]
 for weight,sector in TARGET:
  item={"weight":weight,"recorded_sector":sector,"present_in_528_source":(weight,sector) in observed}
  try:
   powers=tuple(int(x) for x in codec.decode(weight))
   calc=int(m.sec_of(powers))
   item.update({"exponents":list(powers),"computed_sector":calc,
      "roundtrip_weight":int(codec.encode(powers)),
      "roundtrip_matches":int(codec.encode(powers))==weight,
      "sector_matches_recorded":calc==sector,
      "integral":"VP05_full["+",".join(map(str,powers))+"]"})
  except (ValueError,AssertionError,TypeError) as e:
   item["decode_error"]=str(e)
  results.append(item)
 complete=all(x.get("roundtrip_matches") is True and len(x.get("exponents",[]))==12 and x["present_in_528_source"] for x in results)
 report={"status":"DECODED_WITH_EXTERNAL_KIRA_CODEC" if complete else "UNRESOLVED",
  "project":str(a.project),"codec_file":str(a.codec_file),"database":str(db),
  "bits":bits,"ordering":ordering,"records":results,
  "all_three_decode_and_roundtrip":complete,
  "all_three_recorded_sector_match":all(x.get("sector_matches_recorded") is True for x in results),
  "original_528_row_exact_replay_verified":True,
  "physical_identity_fully_verified":complete and all(x.get("sector_matches_recorded") is True for x in results),
  "note":"Any recorded-sector mismatch, particularly sector 201, requires independent observed rank-remap audit; never silently identify sectors."}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_TARGET_WEIGHT_CODEC "+json.dumps(report,ensure_ascii=False),flush=True)
 if not complete:raise SystemExit(2)
if __name__=="__main__":main()
