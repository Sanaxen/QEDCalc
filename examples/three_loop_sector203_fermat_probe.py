"""Read-only Fermat arithmetic microbenchmark on VP05 witness coefficients.

This deliberately benchmarks algebra only; it is NOT a symbolic IBP proof.
Fermat is launched once for a batch, via the user's WSL installation.
"""
from __future__ import annotations
import argparse, json, subprocess, time
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_weight_audit import ROOT
from examples.three_loop_sector203_ffrank_audit import coefficient

FOLDER=ROOT/"output/three_loop_integral_family_audit"

def fermat_batch(exprs,binary,timeout):
    script=["&(t=0);","&U;","&(J=z);","&(J=d);"]
    script += [f"!('QEDFERMAT_{i:05d}=',({e}));" for i,e in enumerate(exprs)]
    script += ["&q;"]
    start=time.perf_counter()
    run=subprocess.run(["wsl","--",binary],input="\n".join(script)+"\n",text=True,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    elapsed=time.perf_counter()-start
    if run.returncode:
        raise RuntimeError(f"Fermat exit={run.returncode}, stderr={run.stderr[-1200:]}, stdout={run.stdout[-1200:]}")
    results=[]
    for i in range(len(exprs)):
        tag=f"QEDFERMAT_{i:05d}="
        start_at=run.stdout.find(tag)
        if start_at<0:raise RuntimeError(f"Missing {tag}; output tail={run.stdout[-1200:]}")
        start_at+=len(tag)
        end_at=run.stdout.find(";",start_at)
        if end_at<0:raise RuntimeError(f"Missing Fermat terminator for {tag}; stdout={run.stdout[start_at:start_at+300]}")
        results.append(run.stdout[start_at:end_at].strip())
    return results,elapsed

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--equations",type=Path)
    p.add_argument("--rows",type=int,default=40)
    p.add_argument("--samples",type=int,default=30)
    p.add_argument("--timeout",type=int,default=120)
    p.add_argument("--fermat",default="/home/yamatoyamato/fermat/Ferl7/fer64")
    a=p.parse_args()
    if a.rows<1 or a.samples<1:p.error("--rows and --samples must be positive")
    files=[a.equations.resolve()] if a.equations else sorted(FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
    if not files:p.error("No VP05 witness .equations.json found")
    file=files[-1]
    rows=json.loads(file.read_text(encoding="utf-8-sig"))["rows"]
    coeffs=[t["coefficient"].replace("**","^") for row in rows[:a.rows] for t in row["terms"] if "z" in t["coefficient"] or "d" in t["coefficient"]]
    exprs=[]
    if len(coeffs)>=2:
        for i in range(a.samples):
            x,y=coeffs[i%len(coeffs)],coeffs[(7*i+1)%len(coeffs)]
            exprs.append(f"(({x})-({y})*({x}))/({y})")
    else:exprs=["(z^2-1)/(z-1)"]
    print("FERMAT_PROBE_START "+json.dumps({"file":str(file),"rows_scanned":min(a.rows,len(rows)),"expressions":len(exprs)}),flush=True)
    try:
        values,ft=fermat_batch(exprs,a.fermat,a.timeout)
        z,d=sp.symbols("z d")
        began=time.perf_counter()
        expected=[sp.cancel(sp.sympify(s.replace("^","**"),locals={"z":z,"d":d})) for s in exprs]
        st=time.perf_counter()-began
        for i,(value,expr) in enumerate(zip(values,exprs)):
            # Fermat formatting can contain whitespace; normalize it for finite-field verification.
            normalized="".join(value.split())
            verified=0
            for prime,z0,d0 in ((1000003,17,7),(1000033,29,11)):
                try:
                    if coefficient(normalized,z0,d0,prime)!=coefficient(expr,z0,d0,prime):
                        raise AssertionError(f"sample={i}, modulus={prime}, got={value!r}")
                    verified+=1
                except ZeroDivisionError:pass
            if verified==0:
                if sp.cancel(sp.sympify(normalized.replace("^","**"),locals={"z":z,"d":d})-expected[i])!=0:
                    raise AssertionError(f"singular sample {i} failed exact equality")
        print("FERMAT_PROBE "+json.dumps({"result":"PASS_SAMPLED","expressions":len(exprs),
         "fermat_seconds":round(ft,3),"sympy_seconds":round(st,3),
         "speedup_sympy_over_fermat":round(st/ft,3) if ft else None,
         "scope":"Algebra microbenchmark, not symbolic IBP elimination or proof"}),flush=True)
    except (OSError,subprocess.TimeoutExpired,RuntimeError,AssertionError,ValueError) as exc:
        print("FERMAT_PROBE_ERROR "+json.dumps({"error":str(exc)}),flush=True)
        raise SystemExit(2) from exc

if __name__=="__main__":main()
