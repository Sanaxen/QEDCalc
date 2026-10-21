"""Structural peeling of VP05 SYSTEM equations incident on unresolved tiny IDs.

Read-only. Repeatedly remove equations containing a variable unique to the
selected equation set. Such equations cannot participate in a nontrivial linear
combination cancelling all non-target variables (assuming nonzero coefficients).
This is only a necessary-support preflight, NOT a rank or alias proof.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_small_id_multiterm_scope import read_rows
from examples.three_loop_sector203_l2_witness_subset import DEFAULT

TARGETS={(10,203),(6,203)}
ANCHOR=(5,201)

def peel(rows, selected, protected):
    active=set(selected)
    rounds=[]
    while True:
        occurrence=Counter()
        for i in active:
            occurrence.update({tuple(t["key"]) for t in rows[i]["terms"]})
        unique={v for v,n in occurrence.items() if n==1 and v not in protected}
        removed={i for i in active if any(tuple(t["key"]) in unique for t in rows[i]["terms"])}
        if not removed: break
        rounds.append({"unique_unprotected_variables":len(unique),"discarded_rows":len(removed)})
        active-=removed
    return active,rounds

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_id_support_peeling.json"))
    a=ap.parse_args()
    rows=read_rows(a.project)
    incidence={}
    for i,r in enumerate(rows):
        for t in r["terms"]:
            incidence.setdefault(tuple(t["key"]),set()).add(i)
    initial=set().union(*(incidence.get(k,set()) for k in TARGETS))
    # The proven (5,201) alias may be kept as an independent symbolic anchor.
    protected=TARGETS|{ANCHOR}
    active,rounds=peel(rows,initial,protected)
    def rowdesc(i):
        r=rows[i]
        return {"file":r["file"],"equation_id":r["equation_id"],"term_count":r["term_count"],
                "terms":r["terms"]}
    result={"system_equations":len(rows),"target_keys":[list(k) for k in sorted(TARGETS)],
       "protected_keys":[list(k) for k in sorted(protected)],
       "initial_direct_union_rows":len(initial),"peeling_rounds":rounds,
       "remaining_rows":len(active),
       "target_remaining_occurrences":{str(k):sum(i in active for i in incidence.get(k,())) for k in sorted(TARGETS)},
       "surviving_equations":[rowdesc(i) for i in sorted(active)],
       "removed_equation_provenance":[{"file":rows[i]["file"],"equation_id":rows[i]["equation_id"]} for i in sorted(initial-active)],
       "exact_elimination_performed":False,"alias_verified":False,
       "warning":"A discarded row cannot appear in a cancellation supported solely on the selected initial rows; adding further SYSTEM rows can restore it. Structural support is not algebraic rank or a physical-integral alias."}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("VP05_SMALL_ID_SUPPORT_PEELING "+json.dumps({k:v for k,v in result.items() if k not in ("surviving_equations","removed_equation_provenance")}|{"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
