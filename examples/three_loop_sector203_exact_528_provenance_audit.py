"""Audit exact VP05 certificate inputs and discover compressed-to-SYSTEM provenance.

No symbolic proof is claimed here. Never infer source row identities from
(file,equation_id) because those labels are not unique in original SYSTEM.
Use explicit source row_index and verified exact combination weights.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT

CERT=Path("output/three_loop_integral_family_audit/vp05_exact_target_certificate.json")
WITNESS=Path("output/three_loop_integral_family_audit/vp05_candidate4_witness_20261017_183832.equations.json")
REPORT=Path("output/three_loop_integral_family_audit/vp05_exact_528_provenance_audit.json")
IDENTITY_FIELDS=("source_row_index","source_row_indices","row_index","source_rows","source_equations","linear_combination","combinations","provenance","contributors","parents","origin","source")
def describe(o):
 if isinstance(o,dict):
  return {"kind":"dict","keys":sorted(o.keys()),"sizes":{k:len(v) for k,v in o.items() if isinstance(v,(dict,list))}}
 if isinstance(o,list):return {"kind":"list","length":len(o),"element_keys":sorted(o[0]) if o and isinstance(o[0],dict) else None}
 return {"kind":type(o).__name__}
def audit(args):
 raw=args.equations.read_bytes()
 src=json.loads(raw.decode("utf-8-sig"))
 cert=json.loads(args.certificate.read_text(encoding="utf-8-sig"))
 proof=cert.get("symbolic_result",{})
 if cert.get("source_sha256")!=hashlib.sha256(raw).hexdigest():
  raise ValueError("Certificate source SHA256 mismatch")
 if cert.get("mode")!="full" or proof.get("target_symbolic_proof") is not True or proof.get("compressed_source_exact_replay") is not True:
  raise ValueError("Expected full exact compressed certificate PASS")
 coeff=proof.get("certificate_coefficients",[])
 indices=[x.get("row") for x in coeff]
 if len(indices)!=166 or set(indices)!=set(range(166)):
  raise ValueError("Expected 166 unique exact certificate coefficient rows")
 rows=src.get("rows",[])
 if len(rows)!=166:raise ValueError("Expected 166 compressed source equations")
 fields={}
 for i,r in enumerate(rows):
  matched={k:describe(v) for k,v in r.items() if any(s in k.lower() for s in ("source","parent","origin","proven","combin","row_index","contribut"))}
  for k,v in matched.items():fields.setdefault(k,{"count":0,"example":v});fields[k]["count"]+=1
 witness_info=None
 if args.witness.exists():
  w=json.loads(args.witness.read_text(encoding="utf-8-sig"))
  wr=w.get("rows",[])
  witness_info={"file":str(args.witness),"sha256":hashlib.sha256(args.witness.read_bytes()).hexdigest(),
   "structure":describe(w),"rows":len(wr),
   "first_row":describe(wr[0]) if wr else None,
   "first_row_identity_fields":{k:describe(v) for k,v in wr[0].items() if k in IDENTITY_FIELDS} if wr else {}}
 report={"stage":"exact_provenance_discovery","source":str(args.equations),
  "source_sha256":hashlib.sha256(raw).hexdigest(),
  "certificate":str(args.certificate),"certificate_sha256":hashlib.sha256(args.certificate.read_bytes()).hexdigest(),
  "certificate_support":len(indices),"certificate_exact_compressed_replay_verified":True,
  "compressed_structure":describe(src),"compressed_first_row":describe(rows[0]),
  "compressed_row_provenance_fields":fields,"witness":witness_info,
  "original_528_row_exact_replay_verified":False,
  "status":"INSPECTION_ONLY",
  "next_requirement":"Explicit exact 166x528 transformation with unique original SYSTEM row_index and exact symbolic provenance for each compressed row; then replay exact target coefficients against original SYSTEM rows"}
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("VP05_528_PROVENANCE_AUDIT "+json.dumps({
  "status":report["status"],"compressed_rows":len(rows),"certificate_support":len(indices),
  "provenance_fields":{k:v["count"] for k,v in fields.items()},
  "witness_rows":witness_info["rows"] if witness_info else None,
  "witness_present":witness_info is not None,"output":str(args.output),
  "original_528_row_exact_replay_verified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--equations",type=Path,default=DEFAULT)
 p.add_argument("--certificate",type=Path,default=CERT)
 p.add_argument("--witness",type=Path,default=WITNESS)
 p.add_argument("--output",type=Path,default=REPORT)
 audit(p.parse_args())
