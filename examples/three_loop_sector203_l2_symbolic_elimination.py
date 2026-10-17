"""Bounded exact Q(z,d) elimination on saved VP05 candidate4 witness rows.

Start with --max-rows 40; raise cautiously after inspecting fill sizes.
All operations are read-only. PASS requires zero symbolic residual and
independent exact row-combination verification. Partial runs are diagnostic.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp
from examples.three_loop_sector203_weight_audit import ROOT

FOLDER=ROOT/"output/three_loop_integral_family_audit"
I10=(10,203)
I6=(6,203)
I5=(5,201)
MASTERS={I5,I6,(7,203),(8,203),(9,203)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path)
    ap.add_argument("--max-rows",type=int,default=40)
    ap.add_argument("--max-columns",type=int,default=120)
    ap.add_argument("--max-expression-chars",type=int,default=1000)
    ap.add_argument("--progress-every",type=int,default=10)
    ap.add_argument("--max-source-support",type=int,default=528)
    args=ap.parse_args()
    if args.max_rows < 1:ap.error("--max-rows must be positive")
    if args.equations: path=args.equations.resolve()
    else:
        files=sorted(FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
        if not files:ap.error("No witness export found")
        path=files[-1]
    raw=json.loads(path.read_text(encoding="utf-8-sig"))["rows"]
    if len(raw)!=528:ap.error(f"Expected 528 original rows, got {len(raw)}")
    z,d=sp.symbols("z d")
    locals_={"z":z,"d":d}
    # Coefficient parser is restricted to an explicit SymPy symbol whitelist.
    def parse(s):return sp.sympify(s.replace("^","**"),locals=locals_,evaluate=True)
    def normalize(v):
        return sp.cancel(v)
    current_row=[0]
    peaks={"equation_chars":0,"provenance_chars":0,"columns":0,"support":0}
    def check_caps(row,trace):
        peaks["columns"]=max(peaks["columns"],len(row))
        peaks["support"]=max(peaks["support"],len(trace))
        if len(row)>args.max_columns or len(trace)>args.max_source_support:
            raise RuntimeError(f"CAP_EXCEEDED columns={len(row)} source_support={len(trace)}")
        for category, terms in (("equation", row), ("provenance", trace)):
            for key,value in terms.items():
                length=len(str(value))
                peak_key="equation_chars" if category=="equation" else "provenance_chars"
                peaks[peak_key]=max(peaks[peak_key],length)
                if length>args.max_expression_chars:
                    print("SYMBOLIC_CAP_DIAGNOSTIC "+json.dumps({"row_number":current_row[0],"category":category,"key":str(key),"expression_chars":length,"expression_cap":args.max_expression_chars,"row_columns":len(row),"source_support":len(trace),"pivot_count":len(pivots)}),flush=True)
                    raise RuntimeError("CAP_EXCEEDED expression character length")
    def subtract(row, base, factor):
        for k,b in base.items():
            v=normalize(row.get(k,sp.S.Zero)-factor*b)
            if v==0:row.pop(k,None)
            else:row[k]=v
    def reduce(row,trace,pivots):
        order=lambda k:(k in MASTERS,k[0],k[1])
        while row:
            lead=min(row,key=order)
            if lead not in pivots:return lead
            base,btrace=pivots[lead]
            factor=row[lead]
            subtract(row,base,factor)
            subtract(trace,btrace,factor)
            check_caps(row,trace)
        return None
    pivots={}
    limit=min(args.max_rows,len(raw))
    for idx,item in enumerate(raw[:limit]):
        current_row[0]=idx+1
        row={}
        for term in item["terms"]:
            key=tuple(term["key"])
            v=normalize(row.get(key,0)+parse(term["coefficient"]))
            if v==0:row.pop(key,None)
            else:row[key]=v
        trace={idx:sp.S.One}
        lead=reduce(row,trace,pivots)
        if lead is not None:
            inv=1/row[lead]
            row={k:normalize(v*inv) for k,v in row.items()}
            trace={k:normalize(v*inv) for k,v in trace.items()}
            check_caps(row,trace)
            pivots[lead]=(row,trace)
        if (idx+1)%args.progress_every==0:
            print("SYMBOLIC_PROGRESS "+json.dumps({"rows":idx+1,"total":limit,"rank":len(pivots),"peaks":peaks}),flush=True)
    if limit<len(raw):
        print("SYMBOLIC_DIAGNOSTIC "+json.dumps({"rows_processed":limit,"rank":len(pivots),"result":"PARTIAL_ONLY","proof":False,"peaks":peaks}),flush=True)
        return
    target={I10:z,I6:sp.Integer(-2),I5:sp.Integer(2)}
    remainder=dict(target)
    trace={}
    missing=reduce(remainder,trace,pivots)
    if remainder:
        print("SYMBOLIC_RESULT "+json.dumps({"rows":limit,"rank":len(pivots),"result":"NOT_PROVED","missing_pivot":list(missing) if missing else None,"remaining_terms":len(remainder),"sample_residual":[[list(k),str(v)] for k,v in list(remainder.items())[:8]]}),flush=True)
        return
    # target = -sum(trace[i]*original_row[i]); verify again with original symbolic text.
    reconstructed={}
    for i,t in trace.items():
        for term in raw[i]["terms"]:
            key=tuple(term["key"])
            v=normalize(reconstructed.get(key,0)-t*parse(term["coefficient"]))
            if v==0:reconstructed.pop(key,None)
            else:reconstructed[key]=v
            check_caps(reconstructed,{})
    difference={}
    for key in set(target)|set(reconstructed):
        delta=normalize(reconstructed.get(key,0)-target.get(key,0))
        if delta!=0:difference[key]=delta
    if difference:
        raise AssertionError(f"Symbolic original-row replay FAILED, residual columns: {len(difference)}")
    print("SYMBOLIC_RESULT "+json.dumps({"rows":limit,"rank":len(pivots),"result":"EXACT_CERTIFICATE_PASS","proof":True,"source_support":len(trace),"target":"z*I10-2*I6+2*I5","verified_original_rows":True}),flush=True)


if __name__=="__main__":main()
