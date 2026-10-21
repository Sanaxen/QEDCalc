"""Compare direct and expanded VP05 SYSTEM incidence scopes via safe support peeling.

No coefficient arithmetic, no assertion of identity. Only rows from original
2678-equation SYSTEM set. Expansion is by variable incidence, with bounded depth.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_small_id_multiterm_scope import read_rows
from examples.three_loop_sector203_small_id_support_peeling import peel,TARGETS,ANCHOR
from examples.three_loop_sector203_l2_witness_subset import DEFAULT

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,default=DEFAULT)
    p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_id_expanded_support.json"))
    a=p.parse_args()
    rows=read_rows(a.project)
    keys=[{tuple(t["key"]) for t in r["terms"]} for r in rows]
    incidence={}
    for i,ks in enumerate(keys):
        for k in ks: incidence.setdefault(k,set()).add(i)
    protected=TARGETS|{ANCHOR}
    direct=set().union(*(incidence.get(t,set()) for t in TARGETS))
    scopes=[("direct",direct)]
    one_vars=set().union(*(keys[i] for i in direct))
    expanded=set(direct)
    for k in one_vars:expanded.update(incidence.get(k,set()))
    scopes.append(("one_variable_expansion",expanded))
    scopes.append(("entire_system",set(range(len(rows)))))
    summaries=[]
    for name,scope in scopes:
        survivors,rounds=peel(rows,scope,protected)
        present_vars=set().union(*(keys[i] for i in survivors)) if survivors else set()
        target_surviving={str(t):sum(t in keys[i] for i in survivors) for t in sorted(TARGETS)}
        summaries.append({"scope":name,"input_rows":len(scope),"input_variables":len(set().union(*(keys[i] for i in scope))),
            "remaining_rows":len(survivors),"remaining_variables":len(present_vars),
            "peeling_rounds":rounds,"target_surviving_occurrences":target_surviving,
            "surviving_equation_ids":[{"file":rows[i]["file"],"equation_id":rows[i]["equation_id"]} for i in sorted(survivors)]})
    result={"system_equations":len(rows),"targets":[list(t) for t in sorted(TARGETS)],
        "protected":[list(t) for t in sorted(protected)],"scopes":summaries,
        "exact_linear_elimination_performed":False,"physical_alias_verified":False,
        "warning":"Nonempty peeled support is only a necessary condition for a cancellation certificate, not evidence of linear dependence. Empty restricted scopes do not disprove relations using additional equations."}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("VP05_SMALL_ID_EXPANDED_SUPPORT "+json.dumps({
        "system_equations":len(rows),"scope_summary":[{k:v for k,v in s.items() if k!="surviving_equation_ids"} for s in summaries],
        "exact_linear_elimination_performed":False,"physical_alias_verified":False,"output":str(a.output)
    }),flush=True)

if __name__=="__main__":main()
