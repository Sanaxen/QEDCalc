"""Bounded exact Q(z,d) replay of reconstructed VP05 compressed-row certificate.

Builds target - sum_r C_r(z,d) E_r(z,d), column by column.
Each sum is checked using SymPy exact cancellation. A column is only marked
proven when its exact numerator is zero. Default tests 5 columns; select
--max-columns 400 for full proof attempt. 20000-operation input budget is
a guard, not a measured bound on SymPy intermediate memory.
"""
from __future__ import annotations
import argparse,ast,hashlib,json,time
from collections import defaultdict,Counter
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_certificate_interpolation_trial import powers
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT

ROOT=Path("output/three_loop_integral_family_audit")
Z,D=sp.symbols("z d")

def parse(expr):
    # Restrict coefficients to arithmetic in z,d and integer constants.
    def walk(n):
        if isinstance(n,ast.Constant) and type(n.value) is int:return sp.Integer(n.value)
        if isinstance(n,ast.Name) and n.id in ("z","d"):return Z if n.id=="z" else D
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)):
            x=walk(n.operand);return -x if isinstance(n.op,ast.USub) else x
        if isinstance(n,ast.BinOp):
            a=walk(n.left);b=walk(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div):return a/b
            if isinstance(n.op,ast.Pow) and b.is_Integer and 0<=int(b)<=24:return a**int(b)
        raise ValueError("Unsafe/unsupported symbolic coefficient: "+expr[:120])
    return walk(ast.parse(expr.replace("^","**"),mode="eval").body)

def coefficient(model,tag):
    terms=model["coefficients"][tag]
    degree=model["degree_pair"][0 if tag=="numerator" else 1]
    mons=powers(degree)
    if len(terms)!=len(mons):raise ValueError("CRT monomial length mismatch")
    out=sp.Integer(0)
    for t,(i,j) in zip(terms,mons):
        rat=t["rational_candidate"]
        if rat is None:raise ValueError("Missing exact rational candidate")
        out+=sp.Rational(rat[0],rat[1])*Z**i*D**j
    return sp.Poly(out,Z,D).as_expr()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--crt",type=Path,default=ROOT/"vp05_two_prime_crt_candidate_audit.json")
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_exact_compressed_certificate_replay.json")
    ap.add_argument("--max-columns",type=int,default=5)
    ap.add_argument("--max-input-terms",type=int,default=20000)
    ap.add_argument("--max-seconds-per-column",type=int,default=45)
    args=ap.parse_args()
    if not 1<=args.max_columns<=400 or args.max_input_terms>20000 or args.max_input_terms<1:
        ap.error("Invalid bounded input")
    crtbytes=args.crt.read_bytes();eqbytes=args.equations.read_bytes()
    trial=json.loads(crtbytes.decode("utf-8-sig"))
    eq=json.loads(eqbytes.decode("utf-8-sig"))
    if len(eq["rows"])!=166 or len(trial["rows"])!=166:
        ap.error("Expected exactly 166 compressed equations and models")
    if eq.get("type")!="symbolic_exact_linear_combinations":
        ap.error("Invalid compressed equation type")
    models={x["row"]:x for x in trial["rows"]}
    if set(models)!=set(range(166)) or not all(x["all_coefficients_reconstructed"] for x in models.values()):
        ap.error("Incomplete CRT model coverage")
    columns=defaultdict(list);source_terms=0
    for row,eqrow in enumerate(eq["rows"]):
        for term in eqrow["terms"]:
            columns[tuple(term["key"])].append((row,term["coefficient"]))
            source_terms+=1
    if set(TARGET)-set(columns):ap.error("Target column absent")
    if source_terms>args.max_input_terms:
        ap.error("Compressed source terms exceed declared input cap")
    # Attempt columns in ascending incidence count for bounded diagnostics.
    order=sorted(columns,key=lambda key:(len(columns[key]),key))
    selected=order[:args.max_columns]
    needed=sorted({i for key in selected for i,_ in columns[key]})
    rational={}
    for row in needed:
        model=models[row]
        num=coefficient(model,"numerator")
        den=coefficient(model,"denominator")
        if den==0:raise ValueError("Zero denominator at compressed row "+str(row))
        rational[row]=num/den
    records=[];counts=Counter()
    for key in selected:
        started=time.perf_counter()
        try:
            target=parse(TARGET[key]) if key in TARGET else sp.Integer(0)
            current=target
            for row,src in columns[key]:
                current=current-rational[row]*parse(src)
            # cancel computes an exact polynomial fraction over Q(z,d).
            reduced=sp.cancel(current)
            numerator,denominator=sp.fraction(reduced)
            zero=(numerator==0)
            elapsed=time.perf_counter()-started
            if elapsed>args.max_seconds_per_column:
                verdict="resource_limit_exceeded"
            else:
                verdict="exact_zero" if zero else "exact_nonzero"
            records.append({"column":list(key),"input_equation_terms":len(columns[key]),
                "status":verdict,"seconds":round(elapsed,3),
                "nonzero_numerator_excerpt":None if zero else str(numerator)[:300]})
            counts[verdict]+=1
        except (MemoryError,ValueError,NotImplementedError) as exc:
            counts["inconclusive"]+=1
            records.append({"column":list(key),"status":"inconclusive","reason":str(exc)[:250]})
        print("VP05_EXACT_COLUMN "+json.dumps(records[-1]),flush=True)
        if records[-1]["status"]=="resource_limit_exceeded":break
    all_columns_checked=(len(records)==len(columns))
    proof=all_columns_checked and all(x["status"]=="exact_zero" for x in records)
    summary={"compressed_rows":166,"columns_total":len(columns),"columns_checked":len(records),
       "verdict_counts":dict(counts),"exact_compressed_certificate_verified":proof,
       "original_528_equation_replay":False,"integral_alias_mapping_verified":False,
       "input_terms":source_terms,"max_input_terms":args.max_input_terms,
       "crt_sha256":hashlib.sha256(crtbytes).hexdigest(),
       "equations_sha256":hashlib.sha256(eqbytes).hexdigest(),
       "fermat_executed":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({"summary":summary,"columns":records},indent=2)+"\n",encoding="utf-8")
    print("VP05_EXACT_COMPRESSED_REPLAY "+json.dumps({**summary,"output":str(args.output)}),flush=True)

if __name__=="__main__":main()
