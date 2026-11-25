"""Read-only C independence diagnostic on all saved restricted SYSTEM rows.

A finite-field rank increment is not an upper bound on generic IBP rank.
No exact C retention or boundary closure is asserted here.
"""
import json
import time
from examples import three_loop_vp05_a_saved_proof_audit as a
from examples import three_loop_vp05_a_confirmed_archive as archive
from examples import three_loop_vp05_stage2_step93_gap_audit as gap
from examples import three_loop_vp05_sector202_quotient_sensitivity as q
from examples import three_loop_sector203_ffrank_audit as ff
from examples import three_loop_vp05_sector202_a_exact_batch as batch

MANIFEST_SHA="c4b285f0066160f0bf443ad2278b6e9dfe183fd033aa78bcbde078ddaf43529e"
POINTS=((1000003,17,7),(1000033,19,11),(1000037,21,15))

def rank_probe(rows,c,m,p,cap=20000):
    pivots={}
    for row in rows:
        ff.insert(row,pivots,p,cap)
    rank=len(pivots)
    alone=ff.insert({c:1},dict(pivots),p,cap)
    combined=dict(pivots)
    m_inc=ff.insert({m:1},combined,p,cap)
    c_inc=ff.insert({c:1},combined,p,cap)
    return {"equation_rank":rank,"C_rank_increment":alone,
            "M_rank_increment":m_inc,"C_rank_increment_modulo_M":c_inc}

def run():
    if batch.sha(archive.DEST/"manifest.json")!=MANIFEST_SHA or batch.sha(archive.DEST/a.proof.OUTPUT.name)!=a.PROOF_SHA:
        raise RuntimeError("Confirmed A archive hash mismatch")
    a.audit()
    if not gap.verified_archive():
        raise RuntimeError("Missing confirmed B archive")
    mod=q.load_codec((q.ROOT/"output/tools/pyred_weight.py").resolve())
    bits,ordering=mod.from_kiradb(str(q.P/"results/kira.db"))
    if ordering!=5:
        raise RuntimeError("Unexpected original codec ordering")
    codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    keys=[(codec.encode(x),139) for x in q.TARGETS]
    if any(tuple(codec.decode(k[0]))!=x for k,x in zip(keys,q.TARGETS)):
        raise RuntimeError("Target codec roundtrip mismatch")
    files=sorted((q.P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    pins={str(f):batch.sha(f) for f in files}
    results=[]
    for p,z,d in POINTS:
        t=time.monotonic()
        try:
            rows=[r for f in files for r in ff.equations(f,p,z,d)]
            if len(rows)!=2678:
                raise RuntimeError("Unexpected full saved SYSTEM count")
            columns=set().union(*(set(r) for r in rows))
            if not set(keys).issubset(columns) or (4,73) not in columns:
                raise RuntimeError("Required target or opaque M absent")
            result=rank_probe(rows,keys[2],(4,73),p)
            result.update({"point":[p,z,d],"rows":len(rows),"columns":len(columns),
                           "elapsed_s":time.monotonic()-t})
        except ZeroDivisionError:
            result={"point":[p,z,d],"status":"SINGULAR_POINT"}
        results.append(result)
        print("VP05_C_RANK_POINT "+json.dumps(result),flush=True)
    if any(batch.sha(f)!=pins[str(f)] for f in files):
        raise RuntimeError("Original SYSTEM changed")
    return {"status":"VP05_C_RESTRICTED_RANK_DIAGNOSTIC_NOT_PROOF",
            "C_key":list(keys[2]),"opaque_M_key":[4,73],
            "points":results,"system_sha256":pins,
            "exact_C_retention_proven":False,"new_boundary_equivalence_proven":False,
            "whole_family_63_closure_proven":False,"kira_executed":False,
            "files_modified":False}

if __name__=="__main__":
    print("VP05_C_RETENTION "+json.dumps(run()),flush=True)
