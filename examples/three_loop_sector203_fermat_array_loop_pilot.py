"""Probe Fermat native arrays and for-loop for VP05 coefficient row updates.

Single Fermat process; finite-field checks at three independent points.
This syntax pilot precedes replacing thousands of scalar commands in the
full Fermat Gaussian engine. Does not constitute an IBP symbolic proof.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from examples.three_loop_sector203_ffrank_audit import coefficient
from examples.three_loop_sector203_fermat_probe import FOLDER
from examples.three_loop_sector203_fermat_gaussian_pilot import POINTS,parse_outputs,explicit_multiplication

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--equations",type=Path)
    p.add_argument("--updates",type=int,default=20)
    p.add_argument("--timeout",type=int,default=90)
    p.add_argument("--fermat",default="/home/yamatoyamato/fermat/Ferl7/fer64")
    a=p.parse_args()
    if not 1<=a.updates<=200:p.error("updates must be 1..200")
    paths=[a.equations.resolve()] if a.equations else sorted(FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
    if not paths:p.error("Missing equations JSON")
    rows=json.loads(paths[-1].read_text(encoding="utf-8-sig"))["rows"]
    pair=None
    for j in range(min(50,len(rows))):
        rj={tuple(t["key"]):t["coefficient"] for t in rows[j]["terms"]}
        for i in range(j):
            ri={tuple(t["key"]):t["coefficient"] for t in rows[i]["terms"]}
            common=sorted(set(ri)&set(rj))
            if len(common)>=2:
                pair=(i,j,ri,rj,common)
                break
        if pair:break
    if not pair:p.error("Cannot find witness row pair")
    i,j,ri,rj,common=pair
    keys=sorted(set(ri)|set(rj))
    if len(keys)>20:p.error("pilot row pair exceeds 20 columns")
    src=[ri.get(k,"0").replace("**","^") for k in keys]
    basis=[rj.get(k,"0").replace("**","^") for k in keys]
    alpha=f"({ri[common[0]]})/({rj[common[0]]})"
    # Fermat manual: [v] := [(expr,expr,...)] creates vector.
    # Loop syntax: for j = 1,n do v[j] := v[j]-fac*b[j] od
    script=["&(t=0)","&(J=z)","&(J=d)",f"fac := {alpha}",
            "[v] := [("+",".join(f"({x})" for x in src)+")]",
            "[b] := [("+",".join(f"({y})" for y in basis)+")]"]
    for _ in range(a.updates):
        script.append(f"for j = 1,{len(keys)} do v[j] := v[j] - fac*b[j] od")
    for k in range(len(keys)):
        script.append(f"!('QEDGAUSS_{k:05d}=',v[{k+1}])")
    script.append("&q")
    print("FERMAT_ARRAY_LOOP_START "+json.dumps({"rows":[i,j],"columns":len(keys),"updates":a.updates,
        "commands":len(script),"file":str(paths[-1])}),flush=True)
    t0=time.perf_counter()
    try:
        run=subprocess.run(["wsl","--",a.fermat],input=("\n".join(script)+"\n").encode("utf-8"),
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=a.timeout)
        stdout=run.stdout.decode("utf-8",errors="replace")
        if run.returncode or "*** Error" in stdout or "*** Inappropriate" in stdout:
            offset=stdout.find("***")
            raise RuntimeError("Fermat interpreter failure: "+repr(stdout[max(0,offset-200):offset+700]))
        output=[explicit_multiplication(v) for v in parse_outputs(stdout,len(keys))]
        verified=0
        for prime,z,d in POINTS:
            try:
                factor=coefficient(alpha,z,d,prime)
                for k,(x,y,value) in enumerate(zip(src,basis,output)):
                    want=(coefficient(x,z,d,prime)-a.updates*factor*coefficient(y,z,d,prime))%prime
                    got=coefficient(value,z,d,prime)
                    if got!=want:raise AssertionError(f"Mismatch col={k}, p={prime}: got={got}, want={want}")
                verified+=1
            except ZeroDivisionError:continue
        if verified<2:raise RuntimeError(f"Too few nonsingular verification points: {verified}")
        print("FERMAT_ARRAY_LOOP "+json.dumps({"result":"PASS_SAMPLED","columns":len(keys),
            "updates":a.updates,"verified_points":verified,"commands":len(script),
            "seconds_including_startup":round(time.perf_counter()-t0,3),
            "scope":"Native array/loop row update, not multi-row Gaussian proof"}),flush=True)
    except (RuntimeError,AssertionError,ValueError,subprocess.TimeoutExpired) as exc:
        print("FERMAT_ARRAY_LOOP_ERROR "+json.dumps({"error":str(exc)}),flush=True)
        raise SystemExit(2) from exc

if __name__=="__main__":main()
