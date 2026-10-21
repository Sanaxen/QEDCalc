"""VP05 exact target certificate engine (SymPy, bounded child process).

Default runs an exact prefix diagnostic only; --full explicitly requests the
complete 166-row target identity. A child process enforces a wall-clock cap.
Success is an exact identity in the COMPRESSED system, not a proof that the
compressed rows have been symbolically replayed back to 528 original rows.
"""
from __future__ import annotations
import argparse,hashlib,json,multiprocessing as mp,queue,time,pickle,os
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_fermat_gaussian_pilot import order
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT,OUTPUT
from examples.three_loop_sector203_exact_prefix_smoke import parse_coeff

OUT=Path("output/three_loop_integral_family_audit/vp05_exact_target_certificate.json")
TARGET={(10,203):"z",(6,203):"-2",(5,201):"2"}

def exact_zero(x):
    return sp.cancel(x)==0

def store_checkpoint(path, fingerprint, normalized, factors, divisors, leads):
    state={"version":1,"fingerprint":fingerprint,"normalized":normalized,
           "factors":factors,"divisors":divisors,"leads":leads}
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    with tmp.open("wb") as f:
        pickle.dump(state,f,protocol=pickle.HIGHEST_PROTOCOL)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp,path)

def load_checkpoint(path,fingerprint):
    # SECURITY: pickle is executable. Only load checkpoints created locally
    # by this program; never accept an untrusted checkpoint file.
    with path.open("rb") as f:state=pickle.load(f)
    if state.get("version")!=1 or state.get("fingerprint")!=fingerprint:
        raise ValueError("Checkpoint source/schedule mismatch")
    out=tuple(state[k] for k in ("normalized","factors","divisors","leads"))
    if len(set(map(len,out)))!=1:raise ValueError("Corrupt checkpoint")
    return out

def calculate(rows,schedule,full,cap_terms,checkpoint=None,fingerprint=None,checkpoint_every=10):
    z,d=sp.symbols("z d")
    sources=[]
    normalized,factors,divisors,leads=load_checkpoint(checkpoint,fingerprint) if checkpoint and checkpoint.exists() else ([],[],[],[])
    start_row=len(normalized)
    if start_row>len(rows):raise ValueError("Checkpoint longer than selected system")
    if start_row:print("VP05_EXACT_TARGET_RESUME "+json.dumps({"completed_rows":start_row}),flush=True)
    for i,row in enumerate(rows):
        src={}
        for t in row["terms"]:
            k=tuple(t["key"])
            src[k]=sp.cancel(src.get(k,0)+parse_coeff(t["coefficient"],z,d))
        src={k:v for k,v in src.items() if v!=0}
        sources.append(src)
        if i<start_row:continue
        vec=dict(src)
        ops=[]
        for op in schedule[i]["operations"]:
            j=op["owner"];pivot=tuple(op["pivot"])
            if j>=i:raise AssertionError("Forward reference in modular schedule")
            fac=sp.cancel(vec.get(pivot,0))
            # An exact zero here indicates modular schedule contains an
            # unnecessary step; never silently assume its meaning.
            if fac==0:raise AssertionError(("symbolically zero scheduled factor",i,j,pivot))
            ops.append((j,fac))
            for k,v in normalized[j].items():
                n=sp.cancel(vec.get(k,0)-fac*v)
                if n:vec[k]=n
                else:vec.pop(k,None)
            if vec.get(pivot,0)!=0:raise AssertionError(("pivot not eliminated",i,j))
            if len(vec)>cap_terms:raise RuntimeError(("intermediate column cap",i,len(vec)))
        lead=tuple(schedule[i]["lead"])
        if not vec or min(vec,key=order)!=lead:
            raise AssertionError(("symbolic pivot differs from modular schedule",i,lead))
        div=sp.cancel(vec[lead])
        if div==0:raise AssertionError(("zero symbolic divisor",i))
        norm={k:sp.cancel(v/div) for k,v in vec.items()}
        if not exact_zero(norm[lead]-1):raise AssertionError("normalization failed")
        normalized.append(norm);factors.append(ops);divisors.append(div);leads.append(lead)
        if checkpoint and ((i+1)%checkpoint_every==0 or i+1==len(rows)):
            store_checkpoint(checkpoint,fingerprint,normalized,factors,divisors,leads)
            print("VP05_EXACT_TARGET_CHECKPOINT "+json.dumps({"rows_saved":i+1,"checkpoint":str(checkpoint)}),flush=True)
        print("VP05_EXACT_TARGET_ROW "+json.dumps({"row_zero_based":i,"columns":len(norm),
            "eliminations":len(ops),"full_target":full}),flush=True)
    if not full:
        return {"rows_checked":len(rows),"prefix_exact_pivots_verified":True,
                "target_symbolic_proof":False,"original_528_row_replay":False}
    print("VP05_EXACT_TARGET_STAGE "+json.dumps({"stage":"target_elimination_start","rows":len(rows)}),flush=True)
    pivot_map={lead:i for i,lead in enumerate(leads)}
    target={k:parse_coeff(v,z,d) for k,v in TARGET.items()}
    original=dict(target);g={}
    while target:
        key=min(target,key=order)
        if key not in pivot_map:raise AssertionError(("unresolved exact target column",key))
        j=pivot_map[key]
        fac=sp.cancel(target[key])
        g[j]=sp.cancel(g.get(j,0)+fac)
        for k,v in normalized[j].items():
            n=sp.cancel(target.get(k,0)-fac*v)
            if n:target[k]=n
            else:target.pop(k,None)
        if len(target)>cap_terms:raise RuntimeError("Target elimination column cap")
    print("VP05_EXACT_TARGET_STAGE "+json.dumps({"stage":"reverse_substitution_start","pivot_owners":len(g)}),flush=True)
    cert={}
    for i in range(len(rows)-1,-1,-1):
        gi=sp.cancel(g.get(i,0))
        if gi==0:continue
        ci=sp.cancel(gi/divisors[i])
        cert[i]=ci
        for j,fac in factors[i]:
            g[j]=sp.cancel(g.get(j,0)-ci*fac)
    print("VP05_EXACT_TARGET_STAGE "+json.dumps({"stage":"exact_replay_start","certificate_support":len(cert)}),flush=True)
    rebuilt={}
    for i,ci in cert.items():
        for k,v in sources[i].items():
            rebuilt[k]=rebuilt.get(k,0)+ci*v
    wrong=[list(k) for k in sorted(set(rebuilt)|set(original)) if not exact_zero(rebuilt.get(k,0)-original.get(k,0))]
    if wrong:raise AssertionError(("exact compressed source replay failed",wrong[:8]))
    return {"rows_checked":len(rows),"certificate_support":len(cert),
       "certificate_coefficients":[{"row":i,"coefficient":str(cert[i])} for i in sorted(cert)],
       "target_symbolic_proof":True,"compressed_source_exact_replay":True,
       "original_528_row_replay":False}

def child(rows,schedule,full,cap_terms,result_queue,checkpoint,fingerprint,checkpoint_every,result_path):
    try:
        payload=calculate(rows,schedule,full,cap_terms,checkpoint,fingerprint,checkpoint_every)
        # Never pass the potentially enormous certificate through multiprocessing.Queue:
        # the Queue feeder can block at process shutdown while parent waits on join.
        result_path.parent.mkdir(parents=True,exist_ok=True)
        tmp=result_path.with_suffix(result_path.suffix+".tmp")
        with tmp.open("w",encoding="utf-8") as f:
            json.dump(payload,f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp,result_path)
        result_queue.put(("ok",str(result_path)))
    except Exception as e:
        result_queue.put(("error",str(type(e).__name__)+": "+str(e)))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--equations",type=Path,default=DEFAULT)
    p.add_argument("--plan",type=Path,default=OUTPUT)
    p.add_argument("--output",type=Path,default=OUT)
    p.add_argument("--rows",type=int,default=7)
    p.add_argument("--full",action="store_true",help="Explicitly authorize potentially costly 166-row symbolic run")
    p.add_argument("--timeout",type=int,default=120)
    p.add_argument("--max-intermediate-columns",type=int,default=450)
    p.add_argument("--checkpoint",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_exact_target_checkpoint.pkl"))
    p.add_argument("--checkpoint-every",type=int,default=10)
    p.add_argument("--resume",action="store_true",help="Use trusted local checkpoint; never load third-party pickle")
    p.add_argument("--no-checkpoint",action="store_true")
    a=p.parse_args()
    if a.full and a.rows!=7:p.error("--full uses all 166 rows; omit --rows")
    if not a.full and not 1<=a.rows<=7:p.error("Prefix limited to 1..7 rows")
    if not 1<=a.timeout<=3600:p.error("Timeout must be 1..3600 seconds")
    if not 1<=a.checkpoint_every<=166:p.error("checkpoint-every must be 1..166")
    if a.resume and (a.no_checkpoint or not a.full):p.error("--resume requires --full and checkpointing")
    raw=a.equations.read_bytes()
    plan=json.loads(a.plan.read_text(encoding="utf-8-sig"))
    if hashlib.sha256(raw).hexdigest()!=plan["source_sha256"]:p.error("Source digest mismatch")
    if not plan["shared_pivot_schedule"] or not plan["shared_target_owner_order"]:
        p.error("Saved modular plans inconsistent")
    data=json.loads(raw.decode("utf-8-sig"))
    if len(data["rows"])!=166:p.error("Expected 166-row compressed system")
    n=166 if a.full else a.rows
    fingerprint=hashlib.sha256(raw+json.dumps(plan["points"][0]["schedule"],sort_keys=True).encode()).hexdigest()
    checkpoint=a.checkpoint if a.full and not a.no_checkpoint else None
    if checkpoint and checkpoint.exists() and not a.resume:p.error("Checkpoint exists; use --resume or choose a new --checkpoint path")
    if a.resume and not checkpoint.exists():p.error("No existing checkpoint")
    result_path=a.output.with_suffix(a.output.suffix+".worker")
    if result_path.exists():result_path.unlink()
    q=mp.Queue()
    proc=mp.Process(target=child,args=(data["rows"][:n],plan["points"][0]["schedule"][:n],
                                       a.full,a.max_intermediate_columns,q,checkpoint,fingerprint,a.checkpoint_every,result_path))
    proc.start()
    proc.join(a.timeout)
    if proc.is_alive():
        proc.terminate();proc.join()
        print("VP05_EXACT_TARGET_STATUS "+json.dumps({"status":"TIMEOUT","seconds":a.timeout,
          "symbolic_proof":False,"resume_available":bool(checkpoint and checkpoint.exists())}),flush=True)
        raise SystemExit(2)
    try:status,payload=q.get(timeout=2)
    except queue.Empty:raise SystemExit("Symbolic worker exited without result")
    if status!="ok":
        print("VP05_EXACT_TARGET_STATUS "+json.dumps({"status":"FAILED","reason":payload,"symbolic_proof":False}),flush=True)
        raise SystemExit(1)
    payload=json.loads(result_path.read_text(encoding="utf-8"))
    result={"source":str(a.equations),"source_sha256":hashlib.sha256(raw).hexdigest(),
            "mode":"full" if a.full else "prefix","symbolic_result":payload,
            "warning":"Only compressed source symbolic identity is certified if full PASS; exact lift to original 528 SYSTEM rows remains unverified."}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    result_path.unlink()
    print("VP05_EXACT_TARGET_STATUS "+json.dumps({"status":"PASS",**{k:v for k,v in payload.items() if k!="certificate_coefficients"},
        "output":str(a.output)}),flush=True)
if __name__=="__main__":main()
