"""Finite-field row-space checks on VP05 peeled scopes; sampled evidence only.

Reuse the project's audited coefficient parser and modular elimination.
Never claim a symbolic identity, physical alias, or unique exponent mapping.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_small_id_multiterm_scope import read_rows
from examples.three_loop_sector203_small_id_support_peeling import peel,TARGETS,ANCHOR
from examples.three_loop_sector203_l2_witness_subset import DEFAULT
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_target_rowspace_audit import eliminate

POINTS=((1000037,21,15),(1001003,19,53))
def scopes(rows):
    keys=[{tuple(t["key"]) for t in r["terms"]} for r in rows]
    idx={}
    for i,ks in enumerate(keys):
        for k in ks:idx.setdefault(k,set()).add(i)
    direct=set().union(*(idx.get(t,set()) for t in TARGETS))
    varset=set().union(*(keys[i] for i in direct))
    expanded=set(direct)
    for key in varset:expanded.update(idx.get(key,set()))
    return [("one_variable_expansion",expanded),("entire_system",set(range(len(rows))))]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,default=DEFAULT)
    p.add_argument("--include-full-system",action="store_true",help="Also test 2639-row full peeled scope (slower)")
    p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_id_expanded_modular.json"))
    a=p.parse_args()
    rows=read_rows(a.project)
    results=[]
    for name,selected in scopes(rows):
        if name=="entire_system" and not a.include_full_system:
            continue
        active,rounds=peel(rows,selected,TARGETS|{ANCHOR})
        scoped=[rows[i] for i in sorted(active)]
        for prime,z,d in POINTS:
            sample=mod_rows(scoped,prime,z,d)
            targets={
                "single_10":{(10,203):1},
                "single_6":{(6,203):1},
                "target_combination":{(10,203):z%prime,(6,203):(-2)%prime,(5,201):2%prime},
            }
            for label,target in targets.items():
                check=eliminate(sample,target.copy(),prime)
                results.append({"scope":name,"input_rows":len(selected),"peeled_rows":len(scoped),
                    "point":[prime,z,d],"test":label,
                    "rank":check["rank"],"target_in_rowspace":check["target_in_rowspace"],
                    "target_remainder_size":check["target_remainder_size"],
                    "target_remainder_sample":check["target_remainder_sample"],
                    "replay_verified":check["certificate_original_equation_replay_verified"],
                    "certificate_support_count":check["certificate_support_count"],
                    "certificate_original_equation_ids":[{"file":scoped[i]["file"],"equation_id":scoped[i]["equation_id"]}
                        for i in check["certificate_row_ids"]] if check["target_in_rowspace"] else [],
                    "coefficients_mod_prime":[{"file":scoped[int(i)]["file"],
                        "equation_id":scoped[int(i)]["equation_id"],"coefficient":v}
                        for i,v in sorted(check["certificate_coefficients"].items())]
                        if check["target_in_rowspace"] else []})
                print("VP05_SMALL_ID_MODULAR_POINT "+json.dumps({
                    k:v for k,v in results[-1].items()
                    if k not in ("certificate_original_equation_ids","coefficients_mod_prime")}),flush=True)
    output={"system_equations":len(rows),"points":list(map(list,POINTS)),"results":results,
        "symbolic_proof":False,"physical_alias_verified":False,
        "warning":"Modular membership and replay hold only at sampled points; non-membership at a sampled point does not establish generic non-membership when rational coefficient specialization can change rank."}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("VP05_SMALL_ID_MODULAR_SUMMARY "+json.dumps({
        "tests":len(results),"sampled_replays_pass":all(not r["target_in_rowspace"] or r["replay_verified"] for r in results),
        "symbolic_proof":False,"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
