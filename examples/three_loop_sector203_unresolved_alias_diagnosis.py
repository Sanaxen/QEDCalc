"""Read-only diagnosis of unresolved VP05 small-ID target alias routes.

Inventory existing exact two-term and multi-term SYSTEM relation reports.
Co-occurrence is never interpreted as equality. No Kira or symbolic solve.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path("output/three_loop_integral_family_audit")
TARGETS=((10,203),(6,203),(5,201))
def read(name):
 path=ROOT/name
 if not path.is_file():return None
 return json.loads(path.read_text(encoding="utf-8-sig"))
def main():
 two=read("vp05_small_id_two_term_bridges.json")
 multi=read("vp05_small_id_multiterm_scope.json")
 exact=read("vp05_small_id_exact_alias_bridges.json")
 rows=[]
 for target in TARGETS:
  bridges=next((r for r in (two or {}).get("small_id_bridges",[]) if tuple(r["small_key"])==target),{})
  scope=next((r for r in (multi or {}).get("target_results",[]) if tuple(r["key"])==target),{})
  verified=next((r for r in (exact or {}).get("target_results",[]) if tuple(r["key"])==target),{})
  rows.append({"key":list(target),
   "two_term_bridge_count":bridges.get("two_term_bridge_count"),
   "two_term_examples":bridges.get("bridges",[])[:4],
   "direct_system_rows":scope.get("direct_row_count"),
   "direct_term_count_histogram":scope.get("direct_term_count_histogram"),
   "small_neighbours":scope.get("direct_small_neighbours",[])[:12],
   "connected_rows_two_hops":scope.get("connected_rows_within_two_variable_hops"),
   "direct_unit_bridge_alias_verified":verified.get("direct_unit_bridge_alias_verified",False),
   "alias_exponents":verified.get("exponents"),
   "status":"DIRECT_EXACT_UNIT_BRIDGE" if verified.get("direct_unit_bridge_alias_verified") else "MULTI_EQUATION_EXACT_ALIAS_NOT_ESTABLISHED"})
 report={"status":"SMALL_ID_ALIAS_SCOPE_DIAGNOSIS","targets":rows,
  "raw_system_used":bool(two or multi),"algebraic_target_proof_unchanged":True,
  "physical_propagator_mapping_verified":False,
  "automatic_alias_promotion":False,
  "note":"Two-term proportionality and graph connectivity do not prove a 12-exponent alias. In particular, no alias is assigned to weights 10 or 6 without exact elimination."}
 print("VP05_UNRESOLVED_ALIAS_DIAGNOSIS "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
