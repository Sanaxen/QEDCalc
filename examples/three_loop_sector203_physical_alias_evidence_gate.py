"""Read-only VP05 integral-ID evidence gate; never interprets small IDs as exponents.

Combines exact 166-column lineage with raw SYSTEM transcription evidence and
optional codec/bridge audits. A physical-integral claim remains blocked without
explicit verified routing/propagator definitions.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path("output/three_loop_integral_family_audit")
FILES={
 "compressed":ROOT/"vp05_target_symbolic_compressed.equations.json",
 "compressed_replay":ROOT/"vp05_exact_compressed_certificate_replay.json",
 "lineage":ROOT/"vp05_original_528_exact_lineage_full166.json",
 "raw_system":ROOT/"vp05_original_witness_raw_system_exact_replay.json",
 "codec_alias":ROOT/"vp05_target_codec_alias_audit.json",
 "exact_alias_bridges":ROOT/"vp05_small_id_exact_alias_bridges.json",
}
def read(path):
 if not path.is_file():return None,None
 raw=path.read_bytes()
 return json.loads(raw.decode("utf-8-sig")),hashlib.sha256(raw).hexdigest()
def main():
 data={};sha={};present={}
 for name,path in FILES.items():
  data[name],sha[name]=read(path)
  present[name]=data[name] is not None
 packed=data["compressed"] or {};replay=(data["compressed_replay"] or {}).get("summary",{})
 lineage=(data["lineage"] or {}).get("summary",{})
 raw=(data["raw_system"] or {}).get("summary",{})
 codec=(data["codec_alias"] or {}).get("summary",{})
 bridges=data["exact_alias_bridges"] or {}
 keys={(10,203),(6,203),(5,201)}
 compressed_keys={tuple(t["key"]) for row in packed.get("rows",[]) for t in row.get("terms",[])}
 checks={
  "all_target_keys_in_compressed":len(packed.get("rows",[]))==166 and keys<=compressed_keys,
  "compressed_400_columns_exact":replay.get("columns_checked")==400 and replay.get("columns_total")==400 and replay.get("exact_compressed_certificate_verified") is True and replay.get("equations_sha256")==sha["compressed"],
  "all_166_groups_exact":lineage.get("groups_checked")==166 and lineage.get("exact_lineage_verified") is True and lineage.get("compressed_sha256")==sha["compressed"],
  "original_raw_system_exact":raw.get("exact_source_transcription_verified") is True and raw.get("matched_rows")==528 and raw.get("system_equations")==2678 and raw.get("original_sha256")==lineage.get("original_sha256"),
  "target_codec_roundtrip":codec.get("codec_roundtrip_and_source_presence") is True and codec.get("compressed_sha256")==sha["compressed"],
  "three_explicit_aliases":codec.get("all_explicit_aliases_verified") is True and codec.get("alias_expectations_supplied") is True,
  "all_direct_unit_bridges":bridges.get("all_three_target_aliases_verified") is True,
  "physical_propagator_mapping":False,
 }
 # Codec decoding and unit bridges alone do not certify physical routing.
 report={"status":"PHYSICAL_INTEGRAL_MAPPING_NOT_PROVEN",
  "checks":checks,"available_reports":present,"source_sha256":sha,
  "exact_algebraic_chain_verified":all(checks[k] for k in ("all_target_keys_in_compressed","compressed_400_columns_exact","all_166_groups_exact")),
  "raw_system_provenance_verified":checks["original_raw_system_exact"],
  "integral_alias_mapping_verified":False,
  "physical_integral_proof":False,
  "next_step":"Run raw SYSTEM replay if absent; separately supply external GPL pyred_weight.py and explicit physical propagator / 12-exponent declarations for topology-aware verification.",
  "kira_executed":False,"source_files_modified":False}
 print("VP05_PHYSICAL_ALIAS_EVIDENCE_GATE "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
