"""Corrected restricted C rank and sector203 candidate reduction in saved SYSTEM."""
import argparse,time
from pathlib import Path
from examples import three_loop_vp05_abc_exact_audit as prev
from examples.three_loop_sector203_ffrank_audit import coefficient,insert
from examples.three_loop_sector203_weight_audit import CANDIDATE,parse_file_integrals
from examples.kira_physical_weight_codec import PhysicalWeightCodec,read_permutation,sector
a=prev.a;n=a.n;gap=a.gap;old=a.old
ROOT=n.BASE/"output"/"vp05_abc_rank40"
SOURCE=prev.ROOT/"report_1795818900486211000.json"
SHA="d8c5c9c93f2c191e571007b9a625da7ae4e61a6211d780d3200417d999c1c7ce"
POINTS=((1000003,17,7),(1000033,19,11),(1000037,21,15))
def ranks(rows,point,c,m,cap,deadline):
    p,z,d=point;basis={};cache={}
    for i,terms in enumerate(rows):
        if time.monotonic()>deadline:raise TimeoutError("Rank deadline")
        if i%100==0:old.memory_guard()
        row={}
        for k,s in terms:
            if s not in cache:cache[s]=coefficient(s,z,d,p)
            row[k]=(row.get(k,0)+cache[s])%p
        insert({k:v for k,v in row.items() if v},basis,p,cap)
    raw=len(basis)
    inc_m=insert({m:1},basis,p,cap)
    inc_c=insert({c:1},basis,p,cap)
    return {"point":list(point),"rank_E":raw,"rank_E_M":raw+int(inc_m),"rank_E_M_C":len(basis),
            "full_row_rank":raw==len(rows),"C_independent_mod_M_at_point":inc_c}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=2:ap.error("Time cap")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Decoded audit SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_ABC_DECODED_EXACT_REPLAY_REVIEW_REQUIRED":raise RuntimeError("Audit scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    project=a.exact.P
    perm=read_permutation((project/"sectormappings/auxiliary.yaml").read_text(encoding="utf-8-sig"),"VP05_full",12)
    mod=a.exact.load_codec(a.exact.ROOT/"output/tools/pyred_weight.py")
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    codec=PhysicalWeightCodec(mod,np=12,bits=bits,iord=ordering,topsectors=[203],permutation=perm)
    custom={tuple(k):tuple(ex) for k,ex,w in data["custom_mapping"]}
    reverse={ex:k for k,ex in custom.items()}
    if reverse[gap.TARGETS[2]]!=(3,202):raise RuntimeError("C scope")
    pins[CANDIDATE]=n.sha(CANDIDATE)
    candidates=parse_file_integrals(CANDIDATE)
    top=[ex for ex in candidates if sector(ex)==203]
    if len(top)!=4:raise RuntimeError("Expected four sector203 candidates")
    keys=[reverse[ex] if ex in reverse else (codec.encode(ex),203) for ex in top]
    rows=[];seen=set()
    for f in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if f not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(f):
            row=[(tuple(map(int,t[2:4])),t[1]) for t in terms]
            rows.append(row);seen.update(k for k,c in row)
    if len(rows)!=2678:raise RuntimeError("SYSTEM count")
    if not set(custom)<=seen:raise RuntimeError("Custom coverage")
    probes=[]
    for point in POINTS:
        r=ranks(rows,point,(3,202),(4,73),20000,deadline)
        probes.append(r);a.v.log("VP05_CORRECT_C_RANK",**r)
    # Same successful descending modular DAG engine; absent keys explicitly unresolved.
    tests=[]
    for point in POINTS:
        present=[k for k in keys if k in seen and k not in custom]
        r=prev.prev.prev.probe(rows,point,present,set(custom),deadline,2000)
        tests.append(r)
        a.v.log("VP05_CORRECT_203_POINT",point=list(point),targets=[{k:v for k,v in t.items() if k!="source_ids"} for t in r["targets"]])
    records=[{"exponents":list(ex),"key":list(k),"present":k in seen,"preferred":k in custom} for ex,k in zip(top,keys)]
    payload={"status":"VP05_CORRECT_C_203_RANK_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},
             "C_rank_trials":probes,"sector203_candidates":records,"sector203_trials":tests,
             "C_restricted_independence_certified":any(r["full_row_rank"] and r["rank_E_M"]==len(rows)+1 and r["rank_E_M_C"]==len(rows)+2 for r in probes),
             "full_closure_proven":False}
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],C_restricted_independence_certified=payload["C_restricted_independence_certified"],
            sector203_candidates=records,report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
if __name__=="__main__":main()
