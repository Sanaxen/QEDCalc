"""Finite-field rank audit of saved sector-203 SYSTEM equations. Read-only.

This is a limited, sampled rank analysis of selected equations, NOT a proof
of full Kira IBP closure or final r7s6d2 master sufficiency.
"""
from __future__ import annotations
import argparse
import ast
import gzip
import json
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT, RUN, CANDIDATE, load_codec, parse_file_integrals

def coefficient(s, z, d, prime):
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value % prime
        if isinstance(node, ast.Name) and node.id in ("z", "d"):
            return (z if node.id == "z" else d) % prime
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -visit(node.operand) % prime
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return visit(node.operand)
        if isinstance(node, ast.BinOp):
            a,b=visit(node.left),visit(node.right)
            if isinstance(node.op, ast.Add): return (a+b)%prime
            if isinstance(node.op, ast.Sub): return (a-b)%prime
            if isinstance(node.op, ast.Mult): return a*b%prime
            if isinstance(node.op, ast.Div):
                if b==0: raise ZeroDivisionError("singular coefficient evaluation")
                return a*pow(b,-1,prime)%prime
            if isinstance(node.op, ast.Pow):
                if not isinstance(node.right,ast.Constant) or type(node.right.value) is not int or abs(node.right.value)>100:
                    raise ValueError("unsupported exponent")
                return pow(a,node.right.value,prime)
        raise ValueError(f"unsupported coefficient expression: {s!r}")
    return visit(ast.parse(s.replace("^","**"), mode="eval").body)

def equations(path, prime, z, d):
    rows=[]
    with gzip.open(path,"rt",encoding="utf-8") as f:
        while (marker:=f.readline()):
            if marker.strip()!="Eq": raise ValueError("bad equation marker")
            f.readline()
            n=int(f.readline().strip())
            row={}
            for _ in range(n):
                data=f.readline().split()
                if len(data)<4: raise ValueError("bad term")
                key=(int(data[2]),int(data[3]))
                val=coefficient(data[1],z,d,prime)
                row[key]=(row.get(key,0)+val)%prime
            rows.append({k:v for k,v in row.items() if v})
    return rows

def insert(row, pivots, p, cap):
    cur=row.copy()
    while cur:
        lead=min(cur)
        if lead not in pivots:
            inv=pow(cur[lead],-1,p)
            pivots[lead]={k:v*inv%p for k,v in cur.items()}
            return True
        base=pivots[lead]
        alpha=cur[lead]
        for k,v in base.items():
            next_v=(cur.get(k,0)-alpha*v)%p
            if next_v: cur[k]=next_v
            else: cur.pop(k,None)
        if len(cur)>cap: raise RuntimeError(f"sparse fill exceeded cap {cap}; abort without conclusions")
    return False

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--project",type=Path,default=ROOT/"output"/RUN)
    a.add_argument("--codec-file",type=Path,required=True)
    a.add_argument("--prime",type=int,default=1000003)
    a.add_argument("--z",type=int,default=17)
    a.add_argument("--d",type=int,default=7)
    a.add_argument("--max-fill",type=int,default=25000)
    args=a.parse_args()
    p=args.prime
    if p!=1000003: a.error("this version uses fixed known prime 1000003")
    project=args.project.resolve()
    codec_module=load_codec(args.codec_file.resolve())
    bits,ordering=codec_module.from_kiradb(str(project/"results/kira.db"))
    if ordering!=5: a.error("unexpected ordering")
    codec=codec_module.WeightCodec(12,bits,ordering,topsectors=[203])
    candidates=[x for x in parse_file_integrals(CANDIDATE) if codec_module.sec_of(x)==203]
    masters=parse_file_integrals(project/"results/VP05_full/masters")
    if len(candidates)!=4 or len(masters)!=10: a.error("unexpected candidate or master count")
    files=list(sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")))
    rows=[]
    for file in files: rows.extend(equations(file,p,args.z,args.d))
    if len(rows)!=3317: a.error(f"unexpected SYSTEM equation count {len(rows)}")
    pivots={}
    for i,row in enumerate(rows,1):
        insert(row,pivots,p,args.max_fill)
        if i%500==0: print(f"RANK_PROGRESS equations={i}/3317 pivots={len(pivots)}",flush=True)
    raw_rank=len(pivots)
    # Candidate vs master span is tested in equation quotient:
    # candidate belongs to span(masters) + rowspan(equations) iff
    # adding candidate after all masters does not increase rank.
    # This statement only pertains to the *saved selected equations*.
    augmented=dict(pivots)
    present=set(k for row in rows for k in row)
    master_status=[]
    for integral in masters:
        key=(codec.encode(integral),codec_module.sec_of(integral))
        # Lower-sector codec ranks do not match Kira's sector mapping.
        # Therefore only inject sector-203 master weights.
        if key[1]!=203: continue
        if key not in present: raise ValueError(f"sector203 master absent from saved equations: {integral}")
        added=insert({key:1},augmented,p,args.max_fill)
        master_status.append({"integral":list(integral),"rank_increase":added})
    candidate_status=[]
    for integral in candidates:
        key=(codec.encode(integral),203)
        if key not in present: raise ValueError(f"candidate absent: {integral}")
        probe=dict(augmented)
        increases=insert({key:1},probe,p,args.max_fill)
        candidate_status.append({"integral":list(integral),"rank_increase_after_sector203_masters":increases,
            "in_saved_equation_plus_sector203_masters_span":not increases})
    print(json.dumps({"scope":"saved selected Kira SYSTEM equations at seed r5s6d0; lower-sector masters not explicitly injected",
      "prime":p,"z":args.z,"d":args.d,"equations":len(rows),"rank":raw_rank,
      "sector203_master_rank_increments":master_status,
      "candidate_status":candidate_status,
      "caveat":"probabilistic single-point rank; not full symbolic reduction or r7s6d2 closure; lower sectors remain formal columns"},
      indent=2))
if __name__=="__main__": main()
