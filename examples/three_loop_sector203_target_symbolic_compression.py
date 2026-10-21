"""Build exact rational-weighted symbolic IBP compression rows H_g.

Each H_g=sum_{i in group} r_i E_i is an EXACT algebraic linear combination
of the stored original equations. Ratios between target certificate coefficients
remain modular hypotheses. Never claim that the compressed rows yield a
symbolic target certificate without exact verification.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_fermat_probe import FOLDER
from examples.three_loop_sector203_ffrank_audit import coefficient

DEFAULT_GROUPS=Path("output/three_loop_integral_family_audit/vp05_target_coefficient_structure.json")
DEFAULT_OUT=Path("output/three_loop_integral_family_audit/vp05_target_symbolic_compressed.equations.json")
CHECKS=((1000037,21,15),(1001003,19,53))


def sum_exact(parts):
    """Symbolically combine rational functions without expanding products."""
    z,d=sp.symbols("z d")
    result=sp.Integer(0)
    for factor, raw in parts:
        expression=sp.sympify(str(raw).replace("^","**"),locals={"z":z,"d":d},evaluate=False)
        if expression.free_symbols-{z,d}:
            raise ValueError("unexpected symbols")
        result += sp.Rational(factor.numerator,factor.denominator)*expression
    return sp.cancel(result)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--groups",type=Path,default=DEFAULT_GROUPS)
    ap.add_argument("--equations",type=Path)
    ap.add_argument("--output",type=Path,default=DEFAULT_OUT)
    ap.add_argument("--max-symbolic-terms",type=int,default=5000)
    a=ap.parse_args()
    files=[a.equations.resolve()] if a.equations else sorted(FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
    if not files:
        ap.error("Original witness missing")
    origin=files[-1]
    original=json.loads(origin.read_text(encoding="utf-8-sig"))["rows"][:528]
    groups=json.loads(a.groups.read_text(encoding="utf-8-sig"))["proportional_classes"]
    if len(original)!=528 or len(groups)!=166:
        ap.error("Expected exactly 528 original equations and 166 groups")
    touched=set()
    packed=[]
    original_terms=sum(len(row["terms"]) for row in original)
    processed=0
    for gi,group in enumerate(groups):
        weights={int(x["row"]):Fraction(x["ratio"]) for x in group["ratios_to_representative"]}
        if set(weights)!=set(group["rows"]) or int(group["representative"]) not in weights or weights[int(group["representative"])]!=1:
            ap.error("Inconsistent group definition")
        if touched.intersection(weights):
            ap.error("Overlapping classes")
        touched.update(weights)
        terms=defaultdict(list)
        for i,ratio in weights.items():
            for term in original[i]["terms"]:
                terms[tuple(term["key"])].append((ratio,term["coefficient"]))
        if sum(len(v) for v in terms.values())>a.max_symbolic_terms:
            ap.error("Symbolic term cap exceeded in group")
        symbolic=[]
        for key,parts in sorted(terms.items()):
            expression=sum_exact(parts)
            if expression!=0:
                symbolic.append({"key":list(key),"coefficient":str(expression)})
        packed.append({"group":gi,"representative":group["representative"],
                       "original_rows":sorted(weights),"terms":symbolic})
        processed+=1
        if processed%20==0:
            print("TARGET_SYMBOLIC_COMPRESS_PROGRESS "+json.dumps({"groups_done":processed,"total":len(groups)}),flush=True)
    if touched!=set(range(528)):
        ap.error("Uncovered original rows")
    # Verify ALL compressed coefficient formulas against weighted original row
    # evaluations at two disjoint finite-field points.
    for p,z,d in CHECKS:
        for packed_row,group in zip(packed,groups):
            expected=defaultdict(int)
            for item in group["ratios_to_representative"]:
                q=Fraction(item["ratio"])
                w=q.numerator*pow(q.denominator,-1,p)%p
                for term in original[item["row"]]["terms"]:
                    k=tuple(term["key"])
                    expected[k]=(expected[k]+w*coefficient(term["coefficient"],z,d,p))%p
            expected={k:v for k,v in expected.items() if v}
            got={}
            for term in packed_row["terms"]:
                k=tuple(term["key"])
                val=coefficient(term["coefficient"],z,d,p)
                if val:got[k]=val
            if got!=expected:
                raise RuntimeError(f"Compression replay mismatch group={packed_row['group']} point={(p,z,d)}")
        print("TARGET_SYMBOLIC_COMPRESS_CHECK "+json.dumps({"point":[p,z,d],"groups":len(packed),"verified":True,"proof":False}),flush=True)
    data={"type":"symbolic_exact_linear_combinations","source":str(origin),
          "groups_source":str(a.groups),"rows":packed,
          "original_rows":528,"original_terms":original_terms,
          "compressed_terms":sum(len(row["terms"]) for row in packed),
          "algebraic_combinations_exact":True,
          "target_coefficient_ratios_proven":False,"target_identity_proven":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print("TARGET_SYMBOLIC_COMPRESS_EXPORTED "+json.dumps({
        "file":str(a.output),"original_rows":528,"compressed_rows":len(packed),
        "original_terms":original_terms,"compressed_terms":data["compressed_terms"],
        "target_identity_proven":False}),flush=True)


if __name__=="__main__":
    main()
