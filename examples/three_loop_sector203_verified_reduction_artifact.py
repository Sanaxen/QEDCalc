"""Read-only VP05 reduction artifact with explicit proof and compatibility boundaries.

Combine previously independently generated exact and provenance reports.
Never turn the unknown historical Kira version or diagram routing into PASS.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_target_scope_preflight import TARGET
from examples.three_loop_sector203_weight_audit import parse_file_integrals
from examples.three_loop_sector203_l2_witness_subset import DEFAULT as PROJECT
AUDIT=Path("output/three_loop_integral_family_audit")
FILES={"compressed":"vp05_target_symbolic_compressed.equations.json",
"certificate":"vp05_exact_compressed_certificate_replay.json",
"lineage":"vp05_original_528_exact_lineage_full166.json",
"raw":"vp05_original_witness_raw_system_exact_replay.json"}
def load(path):
 raw=path.read_bytes();return json.loads(raw.decode("utf-8-sig")),hashlib.sha256(raw).hexdigest()
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project",type=Path,default=PROJECT)
 p.add_argument("--output",type=Path,default=AUDIT/"vp05_verified_reduction_artifact_v1.json")
 a=p.parse_args()
 if a.output.exists():p.error("Refusing to overwrite existing report: "+str(a.output))
 data={};sha={}
 for key,name in FILES.items():data[key],sha[key]=load(AUDIT/name)
 cert=data["certificate"].get("summary",{})
 lineage=data["lineage"].get("summary",{})
 raw=data["raw"].get("summary",{})
 compressed=data["compressed"]
 archive=Path(compressed["source"])
 originalsha=hashlib.sha256(archive.read_bytes()).hexdigest()
 proj=a.project
 preferred=proj/"preferred_provisional64_sector203.txt"
 saved=proj/"results/preferredMasters"
 job=proj/"jobs.yaml"
 xs=parse_file_integrals(preferred);ys=parse_file_integrals(saved)
 expected={10:(1,1,0,1,0,0,1,1,0,0,0,0),6:(1,1,-1,1,0,0,1,1,0,0,0,0),5:(1,0,0,1,0,0,1,1,0,0,0,0)}
 keys={(10,203),(6,203),(5,201)}
 available={tuple(term["key"]) for row in compressed["rows"] for term in row["terms"]}
 checks={
 "exact_400_columns":cert.get("exact_compressed_certificate_verified") is True and cert.get("columns_total")==400 and cert.get("columns_checked")==400,
 "all_166_lineage_exact":lineage.get("exact_lineage_verified") is True and lineage.get("groups_checked")==166,
 "raw_kira_system_replay":raw.get("exact_source_transcription_verified") is True and raw.get("matched_rows")==528 and raw.get("system_equations")==2678,
 "hashes_match":lineage.get("compressed_sha256")==sha["compressed"] and lineage.get("original_sha256")==originalsha and raw.get("original_sha256")==originalsha,
 "preferred_input_matches_saved":len(xs)==10 and xs==ys and all(xs[i-1]==v for i,v in expected.items()),
 "target_keys_present":keys<=available and len(compressed["rows"])==166,
 "preferred_job_reference":'preferred_provisional64_sector203.txt' in job.read_text(encoding="utf-8-sig")
 }
 report={"status":"EXACT_SAVED_KIRA_PROJECT_REDUCTION" if all(checks.values()) else "VERIFICATION_INCOMPLETE",
 "checks":checks,"source_sha256":sha,"original_sha256":originalsha,
 "source_project":str(proj.resolve()),
 "target":{"key":[10,203],"exponents":list(xs[9])},
 "right_hand_side":[{"coefficient":"2/z","key":[6,203],"exponents":list(xs[5])},
 {"coefficient":"-2/z","key":[5,201],"exponents":list(xs[4])}],
 "equation":"z*VP05_full[1,1,0,1,0,0,1,1,0,0,0,0] - 2*VP05_full[1,1,-1,1,0,0,1,1,0,0,0,0] + 2*VP05_full[1,0,0,1,0,0,1,1,0,0,0,0] = 0",
 "domain":"Rational functions in z,d, generic z != 0 for divided reduction",
 "historical_kira_binary_version_verified":False,
 "diagram_momentum_routing_independently_verified":False,
 "globally_complete_master_basis_verified":False,
 "kira_executed":False,"original_files_modified":False}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open("x",encoding="utf-8") as f:json.dump(report,f,indent=2,ensure_ascii=False);f.write("\n")
 print("VP05_VERIFIED_REDUCTION_ARTIFACT "+json.dumps({**report,"output":str(a.output)},ensure_ascii=False),flush=True)
 if not all(checks.values()):raise SystemExit(2)
if __name__=="__main__":main()
