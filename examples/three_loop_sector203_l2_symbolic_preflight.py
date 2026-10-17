"""Read-only audit of saved 528-row exact-coefficient VP05 witness subset.

Checks pairing with modular witness by stable row_index (equation IDs may repeat),
replays the original-row modular certificate, inspects exact coefficient sizes
and variable support, and estimates symbolic elimination complexity. Does not
claim a symbolic proof or run Kira.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_ffrank_audit import coefficient
from examples.three_loop_sector203_weight_audit import ROOT

FOLDER=ROOT/"output/three_loop_integral_family_audit"
TARGET={(10,203):17,(6,203):-2,(5,201):2}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=None)
    ap.add_argument("--prime",type=int,default=1000003)
    args=ap.parse_args()
    if args.equations is None:
        paths=sorted(FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
        if not paths:ap.error("No exported .equations.json found; first run witness_subset --save-subset")
        eqpath=paths[-1]
    else:eqpath=args.equations.resolve()
    if not eqpath.name.endswith(".equations.json"):ap.error("Expected .equations.json filename")
    witnesspath=eqpath.with_name(eqpath.name.replace(".equations.json",".modular_witness.json"))
    if not witnesspath.exists():ap.error("Matching .modular_witness.json not found")
    eq=json.loads(eqpath.read_text(encoding="utf-8-sig"))
    wit=json.loads(witnesspath.read_text(encoding="utf-8-sig"))
    rows=eq["rows"]; weights=wit["rows"]
    wbyid={x["row_index"]:x for x in weights}
    if len(rows)!=528 or len(weights)!=528 or len(wbyid)!=len(weights):
        raise ValueError("Expected exactly 528 distinct provenance rows")
    p=int(wit["prime"]); z=int(wit["z"]); d=int(wit["d"])
    if p!=args.prime:ap.error("Witness prime mismatch")
    residual={}
    cols=set()
    lengths=[]
    degrees=Counter()
    totalterms=0
    for row in rows:
        idx=row["row_index"]
        w=wbyid.get(idx)
        if w is None or w["file"]!=row["file"] or w["equation_id"]!=row["equation_id"]:
            raise ValueError(f"Row provenance mismatch at index {idx}")
        terms=row["terms"]
        lengths.append(len(terms));totalterms+=len(terms)
        scalar=int(w["multiplier_mod_p"])
        for term in terms:
            key=tuple(term["key"])
            cols.add(key)
            expr=term["coefficient"]
            degrees["z" if "z" in expr else "no_z"]+=1
            degrees["d" if "d" in expr else "no_d"]+=1
            val=coefficient(expr,z,d,p)
            new=(residual.get(key,0)+scalar*val)%p
            if new:residual[key]=new
            else:residual.pop(key,None)
    expected={k:v%p for k,v in TARGET.items()}
    if residual!=expected:
        diff={str(k):(expected.get(k,0),residual.get(k,0)) for k in set(expected)|set(residual) if expected.get(k,0)!=residual.get(k,0)}
        raise AssertionError("Original symbolic texts fail modular reconstruction: "+str(list(diff.items())[:10]))
    print("SYMBOLIC_PREFLIGHT "+json.dumps({
        "equations_file":str(eqpath),"witness_file":str(witnesspath),
        "rows":len(rows),"distinct_columns":len(cols),
        "total_terms":totalterms,"max_terms_per_row":max(lengths),
        "coefficient_variable_counts":dict(degrees),
        "modular_exact_text_replay_pass":True,
        "modulus":p,"evaluation":{"z":z,"d":d},
        "scope":"Original coefficient text evaluated modulo p, not exact rational-function membership.",
        "next":"Bounded symbolic elimination can now use row_index as a stable key; do not use equation_id alone."
    },ensure_ascii=False),flush=True)

if __name__=="__main__":main()
