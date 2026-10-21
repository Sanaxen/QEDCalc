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
    ap.add_argument("--max-rows",type=int,default=320)
    ap.add_argument("--loop-control-rows",action="store_true",
        help="EXPERIMENTAL: Fermat pointer-based row elimination control loop")
    ap.add_argument("--reuse-packed-maps",action="store_true",
        help="reuse one pair of packed index arrays between rows (experimental)")
    ap.add_argument("--packed-sparse-maps",action="store_true",
        help="pack mapping arrays once per row, reducing two map assignments per elimination")
    ap.add_argument("--sparse-array-rows",action="store_true",
        help="per-row compact Fermat arrays with mapped pivot update loops")
    ap.add_argument("--array-loop-rows",action="store_true",
        help="experimental dense Fermat row arrays and in-process loops")
    ap.add_argument("--max-array-cells",type=int,default=20000)
    ap.add_argument("--max-map-cells",type=int,default=100000)
    ap.add_argument("--prune-dead-rows",action="store_true",
        help="omit entire rows not needed for requested verification outputs")
    ap.add_argument("--auto-points",action="store_true",
        help="find three independent prime/specialization points with the same modular elimination trace")
    ap.add_argument("--preflight-only",action="store_true")
    ap.add_argument("--max-commands",type=int,default=4500)
    ap.add_argument("--max-outputs",type=int,default=1000)
    ap.add_argument("--verify-last-rows",type=int,default=0,
        help="0=verify all rows; N=emit/check only last N rows (partial validation)")
    ap.add_argument("--prune-eliminated-pivots",action="store_true",
        help="omit symbolically zero pivot columns after exact normalized elimination")
    ap.add_argument("--timeout",type=int,default=180)
    ap.add_argument("--fermat",default="/home/yamatoyamato/fermat/Ferl7/fer64")
    a=ap.parse_args()
    assert sp.cancel(sp.sympify(explicit_multiplication("((-z)d+2z+2)/(2z)"),locals={"z":sp.Symbol("z"),"d":sp.Symbol("d")})-(-sp.Symbol("z")*sp.Symbol("d")+2*sp.Symbol("z")+2)/(2*sp.Symbol("z")))==0
    if not 1<=a.rows<=a.max_rows<=320:ap.error("pilot bounded to 1..320 rows")
    if a.sparse_array_rows and a.array_loop_rows:ap.error("select only one array mode")
    if a.packed_sparse_maps and not a.sparse_array_rows:ap.error("--packed-sparse-maps requires --sparse-array-rows")
    if a.reuse_packed_maps and not a.packed_sparse_maps:ap.error("--reuse-packed-maps requires --packed-sparse-maps")
    if a.loop_control_rows and not (a.sparse_array_rows and a.packed_sparse_maps and a.reuse_packed_maps):
        ap.error("--loop-control-rows requires --sparse-array-rows --packed-sparse-maps --reuse-packed-maps")
    if a.sparse_array_rows and not a.prune_eliminated_pivots:ap.error("sparse arrays require --prune-eliminated-pivots")
    if a.max_commands<100 or a.max_outputs<1:ap.error("invalid command/output cap")
    if a.max_array_cells<1 or a.max_map_cells<1:ap.error("invalid array/map cell cap")
    if a.verify_last_rows<0:ap.error("--verify-last-rows must be >=0")
    paths=[a.equations.resolve()] if a.equations else sorted(FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
    if not paths:ap.error("No exported witness file")
    path=paths[-1]
    rows=json.loads(path.read_text(encoding="utf-8-sig"))["rows"][:a.rows]
    columns=sorted({tuple(t["key"]) for r in rows for t in r["terms"]},key=order)
    if len(columns)>600:ap.error("too many distinct columns for this pilot")
    bycol={k:n for n,k in enumerate(columns)}
    start=time.perf_counter()
    points=POINTS
    if a.auto_points:
        # Deterministic search; never silently accept a single-point schedule.
        # Distinct prime moduli make it harder to share arithmetic accidents.
        moduli=[1000003,1000033,1000037,1000039,1000081,1000099,
                1000117,1000121,1000133,1000151,1000159,1000171,
                1000183,1000187,1000193,1000199,1000211,1000213,
                1000231,1000249,1000253,1000273,1000289,1000291]
        candidate_points=[(p,17+2*i,7+4*i) for i,p in enumerate(moduli) if sp.isprime(p)]
        groups=[]
        checked=0
        for pt in candidate_points:
            try:
                rr=mod_rows(rows,*pt)
                candidate_schedule,candidate_pivots=modular_echelon(rr,pt[0])
            except (ZeroDivisionError,ValueError) as exc:
                print("FERMAT_GAUSS_POINT_SKIPPED "+json.dumps({"point":pt,"reason":str(exc)[:180]}),flush=True)
                continue
            checked+=1
            group=next((g for g in groups if g["schedule"]==candidate_schedule),None)
            if group is None:
                group={"schedule":candidate_schedule,"items":[]}
                groups.append(group)
            group["items"].append((pt,rr,candidate_pivots))
            if len(group["items"])>=3:
                chosen=group["items"][:3]
                points=tuple(v[0] for v in chosen)
                sample=[v[1] for v in chosen]
                schedule=group["schedule"]
                basepivots=chosen[0][2]
                print("FERMAT_GAUSS_POINTS_SELECTED "+json.dumps({
                    "points":points,"candidates_checked":checked,
                    "distinct_schedules":len(groups),
                    "rank":len(basepivots),"proof":False}),flush=True)
                break
        else:
            print("FERMAT_GAUSS_POINTS_NOT_FOUND "+json.dumps({
                "candidates_checked":checked,"distinct_schedules":len(groups),
                "largest_group":max((len(g["items"]) for g in groups),default=0),
                "scope":"No safe shared schedule; no Fermat run"}),flush=True)
            raise SystemExit(2)
    else:
        sample=[mod_rows(rows,*pt) for pt in points]
        schedule,basepivots=modular_echelon(sample[0],points[0][0])
    # Verify finite-field pivot pattern at independent evaluation points before
    # constructing symbolic Fermat commands; otherwise the plan is unsafe.
    for pt,rr in zip(points[1:],sample[1:]):
        other,_=modular_echelon(rr,pt[0])
        if other!=schedule:
            first=next((i for i,(aa,bb) in enumerate(zip(schedule,other)) if aa!=bb),min(len(schedule),len(other)))
            a_ops,a_lead=schedule[first] if first<len(schedule) else ([],None)
            b_ops,b_lead=other[first] if first<len(other) else ([],None)
            # Find the earliest divergence in the operation trace, rather
            # than comparing only the final pivot and the tail of operations.
            common_prefix=0
            while (common_prefix<min(len(a_ops),len(b_ops)) and
                   a_ops[common_prefix]==b_ops[common_prefix]):
                common_prefix+=1
            first_baseline_op=a_ops[common_prefix] if common_prefix<len(a_ops) else None
            first_different_op=b_ops[common_prefix] if common_prefix<len(b_ops) else None
            # Replay the common operation prefix independently in each field.
            # Inspect BOTH candidate pivot coefficients immediately before
            # their first divergent step. A sampled zero is NOT an exact zero.
            candidates=sorted({tuple(op[1]) for op in (first_baseline_op,first_different_op) if op is not None},key=order)
            probe=[]
            for point,field_rows in ((points[0],sample[0]),(pt,rr)):
                prime=point[0]
                vec=field_rows[first].copy()
                field_pivots={}
                for owner,pivot in a_ops[:common_prefix]:
                    if owner not in field_pivots:
                        # Obtain the normalized owner from the matching
                        # complete-field echelon, not a symbolic assumption.
                        _,all_pivots=modular_echelon(field_rows,prime)
                        field_pivots={row_owner:pv for _,(row_owner,pv) in all_pivots.items()}
                    factor=vec.get(tuple(pivot),0)
                    for k,val in field_pivots[owner].items():
                        n=(vec.get(k,0)-factor*val)%prime
                        if n:vec[k]=n
                        else:vec.pop(k,None)
                probe.append({"p":prime,"z":point[1],"d":point[2],
                    "candidate_coefficients":[{"key":k,"value":vec.get(k,0)} for k in candidates]})
            print("FERMAT_GAUSS_PIVOT_MISMATCH "+json.dumps({
                "rows":len(rows),"first_different_row_zero_based":first,
                "first_different_row_one_based":first+1,
                "baseline_point":{"p":points[0][0],"z":points[0][1],"d":points[0][2]},
                "different_point":{"p":pt[0],"z":pt[1],"d":pt[2]},
                "baseline_lead":a_lead,"different_lead":b_lead,
                "baseline_ops_count":len(a_ops),"different_ops_count":len(b_ops),
                "common_operation_prefix":common_prefix,
                "candidate_pivot_values_after_common_prefix":probe,
                "first_baseline_op":first_baseline_op,
                "first_different_op":first_different_op,
                "baseline_ops_near_divergence":a_ops[max(0,common_prefix-3):common_prefix+4],
                "different_ops_near_divergence":b_ops[max(0,common_prefix-3):common_prefix+4],
                "baseline_ops_tail":a_ops[-8:],"different_ops_tail":b_ops[-8:],
                "scope":"diagnostic only; symbolic schedule not established",
                "proof":False}),flush=True)
            raise SystemExit("FERMAT_GAUSS_PILOT_ERROR different pivot schedules across primes: choose another sample")
    # Keep entries for each processed row in Fermat variables rROWcCOL.
    # Assign once; make row reduction factors from the current lead coefficient
    # since normalized stored pivots have leading coefficient 1.
    script=["&(t=0)","&(J=z)","&(J=d)"]
    first_verify=max(0,len(rows)-a.verify_last_rows) if a.verify_last_rows else 0
    needed=set(range(first_verify,len(rows)))
    if a.prune_dead_rows:
        # Backward dependency closure of rows whose final expressions are emitted.
        # Never decide symbolic zero from modular samples: only skip complete rows
        # that cannot influence ANY chosen verification row in this fixed schedule.
        for i in sorted(tuple(needed),reverse=True):
            needed.update(owner for owner,_ in schedule[i][0])
        # Newly added owners can themselves require earlier owners.
        stack=list(needed)
        while stack:
            i=stack.pop()
            for owner,_ in schedule[i][0]:
                if owner not in needed:
                    needed.add(owner)
                    stack.append(owner)
    else:
        needed=set(range(len(rows)))
    expected=[]
    for i,r in enumerate(rows):
        if i not in needed:
            expected.append(())
            continue
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
            if a.prune_eliminated_pivots and pivot not in owner_cols:
                raise RuntimeError(f"missing normalized pivot {pivot} in owner row {owner}")
            for k in owner_cols:
                if a.prune_eliminated_pivots and k==pivot:
                    continue  # coefficient is identically zero: c - c*1
                if k not in cur:
                    script.append(f"r{i}c{bycol[k]} := 0")
                    cur.add(k)
                script.append(f"r{i}c{bycol[k]} := r{i}c{bycol[k]} - {f}*r{owner}c{bycol[k]}")
            if a.prune_eliminated_pivots:
                cur.discard(pivot)
        if lead is not None:
            divisor=f"n{i}"
            script.append(f"{divisor} := r{i}c{bycol[lead]}")
            for k in sorted(cur,key=order):
                script.append(f"r{i}c{bycol[k]} := r{i}c{bycol[k]}/{divisor}")
        expected.append(tuple(sorted(cur,key=order)))
    array_cells=len(needed)*len(columns) if a.array_loop_rows else 0
    if a.array_loop_rows:
        # Dense arrays preserve all entries. Verify through modular replay.
        script=["&(t=0)","&(J=z)","&(J=d)"]
        for i,r in enumerate(rows):
            if i not in needed:continue
            parts={}
            for term in r["terms"]:
                k=tuple(term["key"])
                parts.setdefault(k,[]).append(term["coefficient"].replace("**","^"))
            entries=["("+"+".join("("+v+")" for v in parts[k])+")" if k in parts else "0" for k in columns]
            script.append("[r{}] := [(".format(i)+",".join(entries)+")]")
            ops,lead=schedule[i]
            for owner,pivot in ops:
                factor="f{}x{}".format(i,owner)
                script.append("{} := r{}[{}]".format(factor,i,bycol[pivot]+1))
                script.append("for j = 1,{} do r{}[j] := r{}[j] - {}*r{}[j] od".format(len(columns),i,i,factor,owner))
            if lead is not None:
                divisor="n{}".format(i)
                script.append("{} := r{}[{}]".format(divisor,i,bycol[lead]+1))
                script.append("for j = 1,{} do r{}[j] := r{}[j]/{} od".format(len(columns),i,i,divisor))
    sparse_cells=0
    max_packed_row_cells=0
    if a.sparse_array_rows:
        # Each live row stores the UNION of original and encountered pivot-row
        # supports. This structural upper bound never relies on sampled zeros.
        # It includes eliminated pivots so their factors can be read safely.
        script=["&(t=0)","&(J=z)","&(J=d)"]
        row_maps={}
        for i,r in enumerate(rows):
            if i not in needed:continue
            parts={}
            for t in r["terms"]:
                k=tuple(t["key"])
                parts.setdefault(k,[]).append(t["coefficient"].replace("**","^"))
            keys=set(parts)
            for owner,pivot in schedule[i][0]:
                keys.add(pivot)
                keys.update(expected[owner])
            lead=schedule[i][1]
            if lead is not None:keys.add(lead)
            ordered=sorted(keys,key=order)
            row_maps[i]={k:j+1 for j,k in enumerate(ordered)}
            sparse_cells+=len(ordered)
            entries=["("+"+".join("("+v+")" for v in parts[k])+")" if k in parts else "0" for k in ordered]
            script.append("[r{}] := [(".format(i)+",".join(entries)+")]")
            if a.loop_control_rows:
                # Fermat's system-wide array-of-arrays pointer. A previous
                # row is never destroyed while subsequent rows depend on it.
                script.append("%[{}] := [r{}]".format(i+1,i))
            if a.packed_sparse_maps:
                # Flatten all per-operation maps into ONE pair of index
                # vectors per live row. Each operation refers to a disjoint
                # 1-based segment of that pair; factors are still captured
                # before their corresponding in-place subtraction.
                packed_dst=[]
                packed_src=[]
                spans=[]
                for owner,pivot in schedule[i][0]:
                    terms=[k for k in expected[owner] if k!=pivot]
                    first=len(packed_dst)+1
                    packed_dst.extend(row_maps[i][k] for k in terms)
                    packed_src.extend(row_maps[owner][k] for k in terms)
                    spans.append((owner,pivot,first,len(packed_dst)))
                max_packed_row_cells=max(max_packed_row_cells,2*len(packed_dst))
                map_tag="" if a.reuse_packed_maps else str(i)
                if packed_dst:
                    script.append("[dm{}] := [(".format(map_tag)+",".join(map(str,packed_dst))+")]")
                    script.append("[sm{}] := [(".format(map_tag)+",".join(map(str,packed_src))+")]")
                if a.loop_control_rows and spans:
                    # One outer Fermat loop over the per-row elimination
                    # schedule. Operator order is unchanged. Metadata arrays
                    # are reused between rows, and owner row arrays are
                    # referenced through Fermat's global pointer table.
                    script.append("[ow] := [("+",".join(str(o+1) for o,_,_,_ in spans)+")]")
                    script.append("[pv] := [("+",".join(str(row_maps[i][p]) for _,p,_,_ in spans)+")]")
                    script.append("[lo] := [("+",".join(str(first) for _,_,first,_ in spans)+")]")
                    script.append("[hi] := [("+",".join(str(last) for _,_,_,last in spans)+")]")
                    # Fermat's interactive terminal input REQUIRES backtick
                    # continuation between physical lines of a compound loop.
                    # Semicolons separate the statements inside its body.
                    script.append("for t = 1,{} do `".format(len(spans)))
                    script.append("fac := r{}[pv[t]]; `".format(i))
                    script.append("for j = lo[t],hi[t] do r{}[dm[j]] := r{}[dm[j]] - fac*%[ow[t]][sm[j]] od `".format(i,i))
                    script.append("od")
                else:
                    for owner,pivot,first,last in spans:
                        factor="f{}x{}".format(i,owner)
                        script.append("{} := r{}[{}]".format(factor,i,row_maps[i][pivot]))
                        if first<=last:
                            script.append("for j = {},{} do r{}[dm{}[j]] := r{}[dm{}[j]] - {}*r{}[sm{}[j]] od".format(first,last,i,map_tag,i,map_tag,factor,owner,map_tag))
            else:
                for owner,pivot in schedule[i][0]:
                    local=row_maps[i]
                    other=row_maps[owner]
                    factor="f{}x{}".format(i,owner)
                    script.append("{} := r{}[{}]".format(factor,i,local[pivot]))
                    terms=[k for k in expected[owner] if k!=pivot]
                    if terms:
                        dst=[local[k] for k in terms]
                        src=[other[k] for k in terms]
                        tag="m{}x{}".format(i,owner)
                        script.append("[d{}] := [(".format(tag)+",".join(map(str,dst))+")]")
                        script.append("[s{}] := [(".format(tag)+",".join(map(str,src))+")]")
                        script.append("for j = 1,{} do r{}[d{}[j]] := r{}[d{}[j]] - {}*r{}[s{}[j]] od".format(len(terms),i,tag,i,tag,factor,owner,tag))
            if lead is not None:
                divisor="n{}".format(i)
                script.append("{} := r{}[{}]".format(divisor,i,row_maps[i][lead]))
                script.append("for j = 1,{} do r{}[j] := r{}[j]/{} od".format(len(ordered),i,i,divisor))
    output_keys=[]
    for i,cols in enumerate(expected):
        if i<first_verify:continue
        for k in cols:
            output_keys.append((i,k))
            n=len(output_keys)-1
            if a.sparse_array_rows:
                script.append(f"!('QEDGAUSS_{n:05d}=',r{i}[{row_maps[i][k]}])")
            elif a.array_loop_rows:
                script.append(f"!('QEDGAUSS_{n:05d}=',r{i}[{bycol[k]+1}])")
            else:
                script.append(f"!('QEDGAUSS_{n:05d}=',r{i}c{bycol[k]})")
    script.append("&q")
    storage_cells=sparse_cells if a.sparse_array_rows else array_cells
    packed_map_cells_written=sum(len(expected[owner])-int(pivot in expected[owner]) for i in needed for owner,pivot in schedule[i][0])*2 if a.packed_sparse_maps else 0
    packed_map_cells=max_packed_row_cells if a.reuse_packed_maps else packed_map_cells_written
    control_cells=4*max((len(schedule[i][0]) for i in needed),default=0) if a.loop_control_rows else 0
    print("FERMAT_GAUSS_PILOT_START "+json.dumps({"rows":len(rows),"columns":len(columns),
        "rank":len(basepivots),"operations":sum(len(x[0]) for x in schedule),
        "outputs":len(output_keys),"commands":len(script),"verified_rows":len(rows)-first_verify,"pivot_pruning":a.prune_eliminated_pivots,"dead_row_pruning":a.prune_dead_rows,"live_rows":len(needed),"array_loop_rows":a.array_loop_rows,"array_cells":storage_cells,"sparse_array_rows":a.sparse_array_rows,"packed_sparse_maps":a.packed_sparse_maps,"packed_map_cells":packed_map_cells,"packed_map_cells_written":packed_map_cells_written,"reuse_packed_maps":a.reuse_packed_maps,"loop_control_rows":a.loop_control_rows,"control_cells":control_cells,"file":str(path)}),flush=True)
    if a.preflight_only:
        print("FERMAT_GAUSS_PREFLIGHT "+json.dumps({"rows":len(rows),"rank":len(basepivots),"columns":len(columns),"operations":sum(len(x[0]) for x in schedule),"outputs":len(output_keys),"commands":len(script),"verified_rows":len(rows)-first_verify,"pivot_pruning":a.prune_eliminated_pivots,"dead_row_pruning":a.prune_dead_rows,"live_rows":len(needed),"array_loop_rows":a.array_loop_rows,"array_cells":storage_cells,"sparse_array_rows":a.sparse_array_rows,"packed_sparse_maps":a.packed_sparse_maps,"packed_map_cells":packed_map_cells,"max_map_cells":a.max_map_cells,"max_array_cells":a.max_array_cells,"max_commands":a.max_commands,"max_outputs":a.max_outputs,"within_caps":len(script)<=a.max_commands and len(output_keys)<=a.max_outputs and storage_cells<=a.max_array_cells and packed_map_cells+control_cells<=a.max_map_cells,"result":"ESTIMATE_ONLY","proof":False}),flush=True)
        return
    try:
        if storage_cells>a.max_array_cells:
            raise RuntimeError(f"array cell cap exceeded: {storage_cells}/{a.max_array_cells}")
        if packed_map_cells+control_cells>a.max_map_cells:
            raise RuntimeError(f"packed map cell cap exceeded: {packed_map_cells}/{a.max_map_cells}")
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
        for p,z,d in points:
            rr=mod_rows(rows,p,z,d)
            basis={}
            for i,((ops,lead),original,cols) in enumerate(zip(schedule,rr,expected)):
                if i not in needed:continue
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
            "verified_primes":[p for p,_,_ in points],"verified_rows":len(rows)-first_verify,"pivot_pruning":a.prune_eliminated_pivots,"dead_row_pruning":a.prune_dead_rows,"live_rows":len(needed),"array_loop_rows":a.array_loop_rows,"array_cells":storage_cells,"sparse_array_rows":a.sparse_array_rows,"packed_sparse_maps":a.packed_sparse_maps,"packed_map_cells":packed_map_cells,"seconds_including_wsl_startup":round(duration,3),
            "scope":"Exact-function elimination executed in Fermat; equality sampled, no symbolic proof"}),flush=True)
    except (RuntimeError,AssertionError,subprocess.TimeoutExpired,ValueError) as exc:
        print("FERMAT_GAUSS_PILOT_ERROR "+json.dumps({"error":str(exc)}),flush=True)
        raise SystemExit(2) from exc

if __name__=="__main__":main()
