"""Fermat in-process row-operation pilot on saved VP05 IBP coefficients.

This benchmarks R_i <- R_i - c*R_j as a chain inside ONE Fermat process.
It is not a full Gaussian elimination and does not prove master relations.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import sympy as sp
from examples.three_loop_sector203_fermat_probe import FOLDER, fermat_batch
from examples.three_loop_sector203_ffrank_audit import coefficient


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--equations",type=Path)
    p.add_argument("--rows",type=int,default=528)
    p.add_argument("--updates",type=int,default=20)
    p.add_argument("--columns",type=int,default=8)
    p.add_argument("--timeout",type=int,default=180)
    p.add_argument("--fermat",default="/home/yamatoyamato/fermat/Ferl7/fer64")
    a=p.parse_args()
    if not (1<=a.updates<=200 and 1<=a.columns<=30):p.error("updates 1..200, columns 1..30")
    paths=[a.equations.resolve()] if a.equations else sorted(FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
    if not paths:p.error("Missing witness JSON")
    rows=json.loads(paths[-1].read_text(encoding="utf-8-sig"))["rows"][:a.rows]
    byrow=[{tuple(t["key"]):t["coefficient"].replace("**","^") for t in r["terms"]} for r in rows]
    pair=None
    for j in range(len(byrow)):
        for i in range(j):
            common=set(byrow[i]) & set(byrow[j])
            if len(common)>=2:
                pair=(i,j,sorted(common))
                break
        if pair:break
    if pair is None:p.error("Cannot find two rows with >=2 common columns")
    i,j,common=pair
    pivot=common[0]
    # Use only actual saved symbolic coefficients. A repeated row subtraction
    # is a microbenchmark of rational arithmetic, not a rank computation.
    keys=sorted(set(byrow[i])|set(byrow[j]))[:a.columns]
    if pivot not in keys:keys=[pivot]+keys[:a.columns-1]
    src=[byrow[i].get(k,"0") for k in keys]
    basis=[byrow[j].get(k,"0") for k in keys]
    alpha=f"({byrow[i][pivot]})/({byrow[j][pivot]})"
    # Construct a single Fermat session with persistent scalar variables.
    # Fermat variable assignments use ':='; print tagged results once.
    # Piped stdin is read as terminal statements, rather than a Fermat file.
    # Here semicolons suppress output and may concatenate successive commands.
    # Avoid &U (uglyprint), which warns of limitations for terminal execution.
    script=["&(t=0)","&(J=z)","&(J=d)",f"fac := {alpha}"]
    for k,(x,y) in enumerate(zip(src,basis)):
        script.append(f"v{k} := ({x})")
        script.append(f"b{k} := ({y})")
    for _ in range(a.updates):
        for k in range(len(keys)):
            script.append(f"v{k} := v{k} - fac*b{k}")
    for k in range(len(keys)):
        script.append(f"!('QEDFERMAT_{k:05d}=',v{k})")
    script.append("&q")
    print("FERMAT_ROW_PILOT_START "+json.dumps({"file":str(paths[-1]),"row_i":i,"row_j":j,
        "pivot":pivot,"columns":len(keys),"updates":a.updates,"commands":len(script)}),flush=True)
    start=time.perf_counter()
    try:
        run=subprocess.run(["wsl","--",a.fermat],input=("\n".join(script)+"\n").encode("utf-8"),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=a.timeout)
        # Windows text=True translates LF to CRLF on stdin; Fermat reports CR
        # (unicode 13) as an invalid token. Byte input preserves literal LF.
        run_stdout=run.stdout.decode("utf-8",errors="replace")
        run_stderr=run.stderr.decode("utf-8",errors="replace")
        ft=time.perf_counter()-start
        if run.returncode:raise RuntimeError(f"Fermat returncode={run.returncode}, stderr={run_stderr[-600:]}, stdout={run_stdout[-600:]}")
        # Fermat can exit with code zero even when script statements fail.
        # Diagnose the FIRST interpreter error, not just a misleading missing output tag.
        if "*** Error" in run_stdout or "*** Inappropriate" in run_stdout:
            at=run_stdout.find("***")
            raise RuntimeError("Fermat interpreter error: "+repr(run_stdout[max(0,at-360):at+700])+"; script_head="+repr(script[:12]))
        # Reuse already validated output framing from the existing Fermat probe,
        # avoiding prompt assumptions at line boundaries.
        import re
        assert re.sub(r"\s*[0-9]\s*>\s*>?\s*$", "", "19\n        0\n\n>").strip()=="19", "single-prompt output regression"
        assert re.sub(r"\s*[0-9]\s*>\s*>?\s*$", "", "( d - 21 ) / ( d - 1 )\n        0\n\n>").strip()=="( d - 21 ) / ( d - 1 )", "rational-output regression"
        outputs=[]
        for k in range(len(keys)):
            tag=f"QEDFERMAT_{k:05d}="
            nt=f"QEDFERMAT_{k+1:05d}="
            begin=run_stdout.rfind(tag)
            end=run_stdout.rfind(nt) if k+1<len(keys) else len(run_stdout)
            if begin<0 or end<begin:raise RuntimeError(f"Missing or misordered Fermat output tag {tag}; tail={run_stdout[-500:]}")
            part=run_stdout[begin+len(tag):end]
            part=re.sub(r"\s*bye\s*$","",part)
            part=re.sub(r"\s*[0-9]\s*>\s*>?\s*$","",part).strip()
            if not part or ">>" in part:raise RuntimeError(f"Unparsed Fermat output k={k}: {part[:240]!r}")
            outputs.append(part)
        z,d=sp.symbols("z d")
        convert=lambda s:sp.sympify(s.replace("^","**"),locals={"z":z,"d":d})
        began=time.perf_counter()
        c=sp.cancel(convert(alpha))
        sym=[sp.cancel(convert(x)-a.updates*c*convert(y)) for x,y in zip(src,basis)]
        st=time.perf_counter()-began
        import ast
        for k,out in enumerate(outputs):
            normalized="".join(out.split())
            try:
                ast.parse(normalized.replace("^","**"),mode="eval")
            except SyntaxError as err:
                raise RuntimeError("Fermat malformed output "+json.dumps({"column":k,"raw_value":out,"normalized":normalized,"source":src[k],"basis":basis[k],"factor":alpha,"stdout_tail":run_stdout[-1000:]},ensure_ascii=False)) from err
        verified_points=0
        for prime,zz,dd in ((1000003,17,7),(1000033,29,11),(1000037,13,19)):
            try:
                factor=coefficient(alpha,zz,dd,prime)
                for k,(x,y,out) in enumerate(zip(src,basis,outputs)):
                    expected=(coefficient(x,zz,dd,prime)-a.updates*factor*coefficient(y,zz,dd,prime))%prime
                    try:
                        actual=coefficient("".join(out.split()),zz,dd,prime)
                    except (SyntaxError,ValueError) as err:
                        raise RuntimeError(f"Fermat coefficient parse failure column={k} output={out!r} prime={prime}") from err
                    if expected!=actual:raise AssertionError(f"Mismatch column={k}, prime={prime}, result={out!r}")
                verified_points+=1
            except ZeroDivisionError:continue
        if not verified_points:raise RuntimeError("No non-singular finite-field verification points")
        print("FERMAT_ROW_PILOT "+json.dumps({"result":"PASS_SAMPLED","columns":len(keys),
            "updates":a.updates,"verified_points":verified_points,
            "fermat_seconds_including_startup":round(ft,4),
            "sympy_seconds_algebra_only":round(st,4),
            "scope":"Repeated in-Fermat row updates, not Gaussian elimination nor exact proof"}),flush=True)
    except (RuntimeError,AssertionError,subprocess.TimeoutExpired,SyntaxError,ValueError) as exc:
        print("FERMAT_ROW_PILOT_ERROR "+json.dumps({"error":str(exc)}),flush=True)
        raise SystemExit(2) from exc


if __name__=="__main__":main()
