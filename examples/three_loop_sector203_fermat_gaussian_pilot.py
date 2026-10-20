"""Exact Fermat sparse IBP Gaussian-elimination pilot with independent modular replay.

Plans pivot operations using a finite-field sample, then executes that SAME
sequence as rational functions in one Fermat process. Tests symbolic outputs
against independent modular Gaussian elimination; NOT an exact IBP certificate.
Small bounded row counts only. No Kira or repository outputs are modified.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from pathlib import Path

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

from examples.three_loop_sector203_fermat_probe import FOLDER
from examples.three_loop_sector203_ffrank_audit import coefficient

MASTERS={(5,201),(6,203),(7,203),(8,203),(9,203)}
POINTS=((1000003,17,7),(1000033,29,11),(1000037,13,19))

def order(k):
    return (k in MASTERS,k[0],k[1])

def mod_rows(rows,p,z,d):
    out=[]
    for r in rows:
        vec={}
        for t in r["terms"]:
            k=tuple(t["key"])
            val=(vec.get(k,0)+coefficient(t["coefficient"],z,d,p))%p
            if val:vec[k]=val
            else:vec.pop(k,None)
        out.append(vec)
    return out

def modular_echelon(rows,p):
    pivots={}
    schedule=[]
    for idx,original in enumerate(rows):
        vec=original.copy()
        ops=[]
        while vec:
            lead=min(vec,key=order)
            if lead not in pivots:break
            owner,pivot=pivots[lead]
            fac=vec[lead]
            ops.append((owner,lead))
            for k,b in pivot.items():
                val=(vec.get(k,0)-fac*b)%p
                if val:vec[k]=val
                else:vec.pop(k,None)
        if vec:
            lead=min(vec,key=order)
            inv=pow(vec[lead],-1,p)
            vec={k:v*inv%p for k,v in vec.items()}
            pivots[lead]=(idx,vec.copy())
            schedule.append((ops,lead))
        else:
            schedule.append((ops,None))
    return schedule,pivots

def parse_outputs(stdout,number):
    values=[]
    for i in range(number):
        tag=f"QEDGAUSS_{i:05d}="
        nxt=f"QEDGAUSS_{i+1:05d}="
        begin=stdout.rfind(tag)
        end=stdout.rfind(nxt) if i+1<number else len(stdout)
        if begin<0 or end<begin:raise ValueError(f"Output markers out of order for {tag}, tail={stdout[-900:]!r}")
        part=stdout[begin+len(tag):end]
        part=re.sub(r"\s*bye\s*$","",part)
        part=re.sub(r"\s*[0-9]\s*>\s*>?\s*$","",part).strip()
        if not part or ">>" in part or "QEDGAUSS_" in part:
            raise ValueError(f"Unparsed Fermat output {i}: {part[:400]!r}")
        values.append("".join(part.split()))
    return values

def explicit_multiplication(value):
    """Convert Fermat implicit products (2z, (-z)d, 2(d+1)) to explicit *."""
    z,d=sp.symbols("z d")
    # Fermat uses backticks for line continuation in long printed formulas.
    # They are display artefacts, never algebraic operators.
    value=value.replace("`","")
    parsed=parse_expr(value.replace("^","**"),local_dict={"z":z,"d":d},
        global_dict={"Integer":sp.Integer,"Rational":sp.Rational,"Symbol":sp.Symbol,
                     "Pow":sp.Pow,"Mul":sp.Mul,"Add":sp.Add},
        transformations=standard_transformations+(implicit_multiplication_application,),
        evaluate=False)
    if parsed.free_symbols-{z,d}:
        raise ValueError(f"Unexpected Fermat symbols: {parsed.free_symbols-{z,d}}")
    return str(parsed)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path)
    ap.add_argument("--rows",type=int,default=12)
    ap.add_argument("--max-rows",type=int,default=100)
    ap.add_argument("--preflight-only",action="store_true")
    ap.add_argument("--max-commands",type=int,default=4500)
    ap.add_argument("--max-outputs",type=int,default=1000)
    ap.add_argument("--timeout",type=int,default=180)
    ap.add_argument("--fermat",default="/home/yamatoyamato/fermat/Ferl7/fer64")
    a=ap.parse_args()
    assert sp.cancel(sp.sympify(explicit_multiplication("((-z)d+2z+2)/(2z)"),locals={"z":sp.Symbol("z"),"d":sp.Symbol("d")})-(-sp.Symbol("z")*sp.Symbol("d")+2*sp.Symbol("z")+2)/(2*sp.Symbol("z")))==0
    if not 1<=a.rows<=a.max_rows<=100:ap.error("pilot bounded to 1..100 rows")
    if a.max_commands<100 or a.max_outputs<1:ap.error("invalid command/output cap")
    paths=[a.equations.resolve()] if a.equations else sorted(FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
    if not paths:ap.error("No exported witness file")
    path=paths[-1]
    rows=json.loads(path.read_text(encoding="utf-8-sig"))["rows"][:a.rows]
    columns=sorted({tuple(t["key"]) for r in rows for t in r["terms"]},key=order)
    if len(columns)>300:ap.error("too many distinct columns for this pilot")
    bycol={k:n for n,k in enumerate(columns)}
    start=time.perf_counter()
    sample=[mod_rows(rows,*pt) for pt in POINTS]
    schedule,basepivots=modular_echelon(sample[0],POINTS[0][0])
    # Verify finite-field pivot pattern at independent evaluation points before
    # constructing symbolic Fermat commands; otherwise the plan is unsafe.
    for pt,rr in zip(POINTS[1:],sample[1:]):
        other,_=modular_echelon(rr,pt[0])
        if other!=schedule:
            raise SystemExit("FERMAT_GAUSS_PILOT_ERROR different pivot schedules across primes: choose another sample")
    # Keep entries for each processed row in Fermat variables rROWcCOL.
    # Assign once; make row reduction factors from the current lead coefficient
    # since normalized stored pivots have leading coefficient 1.
    script=["&(t=0)","&(J=z)","&(J=d)"]
    expected=[]
    for i,r in enumerate(rows):
        values={}
        for t in r["terms"]:
            k=tuple(t["key"])
            values.setdefault(k,[]).append(t["coefficient"].replace("**","^"))
        cur=set(values)
        for k,parts in values.items():
            script.append(f"r{i}c{bycol[k]} := ("+"+".join(f"({v})" for v in parts)+")")
        ops,lead=schedule[i]
        for owner,pivot in ops:
            # Set the factor using the current pivot coefficient.
            f=f"f{i}x{owner}"
            script.append(f"{f} := r{i}c{bycol[pivot]}")
            # A pivot row may have undergone fills. Fetch ALL entries that
            # exist symbolically after owner was normalized.
            owner_cols=expected[owner]
            for k in owner_cols:
                if k not in cur:
                    script.append(f"r{i}c{bycol[k]} := 0")
                    cur.add(k)
                script.append(f"r{i}c{bycol[k]} := r{i}c{bycol[k]} - {f}*r{owner}c{bycol[k]}")
        if lead is not None:
            divisor=f"n{i}"
            script.append(f"{divisor} := r{i}c{bycol[lead]}")
            for k in sorted(cur,key=order):
                script.append(f"r{i}c{bycol[k]} := r{i}c{bycol[k]}/{divisor}")
        expected.append(tuple(sorted(cur,key=order)))
    output_keys=[]
    for i,cols in enumerate(expected):
        for k in cols:
            output_keys.append((i,k))
            n=len(output_keys)-1
            script.append(f"!('QEDGAUSS_{n:05d}=',r{i}c{bycol[k]})")
    script.append("&q")
    print("FERMAT_GAUSS_PILOT_START "+json.dumps({"rows":len(rows),"columns":len(columns),
        "rank":len(basepivots),"operations":sum(len(x[0]) for x in schedule),
        "outputs":len(output_keys),"commands":len(script),"file":str(path)}),flush=True)
    if a.preflight_only:
        print("FERMAT_GAUSS_PREFLIGHT "+json.dumps({"rows":len(rows),"rank":len(basepivots),"columns":len(columns),"operations":sum(len(x[0]) for x in schedule),"outputs":len(output_keys),"commands":len(script),"max_commands":a.max_commands,"max_outputs":a.max_outputs,"within_caps":len(script)<=a.max_commands and len(output_keys)<=a.max_outputs,"result":"ESTIMATE_ONLY","proof":False}),flush=True)
        return
    try:
        if len(script)>a.max_commands or len(output_keys)>a.max_outputs:
            raise RuntimeError(f"pilot cap exceeded: commands={len(script)}/{a.max_commands}, outputs={len(output_keys)}/{a.max_outputs}; run --preflight-only and do not raise caps without reviewing scope")
        run=subprocess.run(["wsl","--",a.fermat],input=("\n".join(script)+"\n").encode(),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=a.timeout)
        stdout=run.stdout.decode("utf-8",errors="replace")
        duration=time.perf_counter()-start
        if run.returncode or "*** Error" in stdout or "*** Inappropriate" in stdout:
            at=stdout.find("***")
            raise RuntimeError(f"Fermat interpreter error/exit={run.returncode}, context={stdout[max(0,at-100):at+600]!r}")
        actual=parse_outputs(stdout,len(output_keys))
        # Fermat prints products without *, e.g. ((-z)d+2z+2)/(2z).
        # Normalize before reusing the established finite-field AST evaluator.
        normalized=[]
        for output_index,v in enumerate(actual):
            try:
                normalized.append(explicit_multiplication(v))
            except Exception as exc:
                row_id, integral=output_keys[output_index]
                raise RuntimeError("Fermat normalization failure "+json.dumps({"output_index":output_index,"row":row_id,"integral":integral,"raw_output":v[:700]},default=str)) from exc
        actual=normalized
        # Compare row-by-row against independent modular elimination;
        # no SymPy reduction and no assumption Fermat zero-pivots stay zero.
        for p,z,d in POINTS:
            rr=mod_rows(rows,p,z,d)
            basis={}
            for i,((ops,lead),original,cols) in enumerate(zip(schedule,rr,expected)):
                vec=original.copy()
                for owner,pivot in ops:
                    factor=vec.get(pivot,0)
                    for k,v in basis[owner].items():
                        new=(vec.get(k,0)-factor*v)%p
                        if new:vec[k]=new
                        else:vec.pop(k,None)
                if lead is not None:
                    if vec.get(lead,0)==0:raise RuntimeError(f"vanishing pivot row={i} at p={p}")
                    inv=pow(vec[lead],-1,p)
                    vec={k:v*inv%p for k,v in vec.items()}
                basis[i]=vec
            for (i,k),v in zip(output_keys,actual):
                try:observed=coefficient(v,z,d,p)
                except Exception as e:raise RuntimeError(f"Invalid Fermat expression row={i} key={k}, value={v!r}") from e
                expected_val=basis[i].get(k,0)
                if observed!=expected_val:
                    raise AssertionError(f"Mismatch row={i}, col={k}, p={p}: Fermat {observed}, modular {expected_val}, text={v[:120]!r}")
        print("FERMAT_GAUSS_PILOT "+json.dumps({"result":"PASS_SAMPLED","rows":len(rows),
            "rank":len(basepivots),"operations":sum(len(x[0]) for x in schedule),
            "verified_primes":[p for p,_,_ in POINTS],"seconds_including_wsl_startup":round(duration,3),
            "scope":"Exact-function elimination executed in Fermat; equality sampled, no symbolic proof"}),flush=True)
    except (RuntimeError,AssertionError,subprocess.TimeoutExpired,ValueError) as exc:
        print("FERMAT_GAUSS_PILOT_ERROR "+json.dumps({"error":str(exc)}),flush=True)
        raise SystemExit(2) from exc

if __name__=="__main__":main()
