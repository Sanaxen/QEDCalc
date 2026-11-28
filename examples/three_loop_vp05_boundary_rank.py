"""Rank difference in physical index space, before/after certified substitution.
Saved SYSTEM only; no inference of extended seed completeness.
"""
import argparse,time
from pathlib import Path
from examples import three_loop_vp05_boundary202203_exact as prev
from examples.three_loop_sector203_ffrank_audit import coefficient
from examples.kira_physical_weight_codec import PhysicalWeightCodec,read_permutation
a=prev.a;n=a.n;gap=a.gap;old=a.old
ROOT=n.BASE/"output"/"vp05_boundary_rank45"
SOURCE=prev.ROOT/"report_1795824908682072200.json"
SHA="f2825c2810aa9dc1eed9b7772191d96fee188415bdda3ac1124085ccc536f93c"

def substitute(row,rules,p):
    out={}
    for k,c in row.items():
        for j,v in rules.get(k,{k:1}).items():
            x=(out.get(j,0)+c*v)%p
            if x:out[j]=x
            else:out.pop(j,None)
    return out

def ranks(rows,candidates,p,deadline,cap=2000,guard=lambda:None):
    # Noncandidate columns first. Remaining candidate-only pivots count
    # the intersection of the row space with the candidate coordinate space.
    piv={};operations=0;terms=0;relations=[]
    for i,row in enumerate(rows):
        if i%50==0:guard()
        cur=dict(row)
        while cur:
            if time.monotonic()>=deadline:raise TimeoutError("Rank budget")
            if len(cur)>cap or operations>50000000:raise RuntimeError("Rank fill/operation cap")
            lead=max(cur,key=lambda k:(k not in candidates,k))
            if lead not in piv:
                inv=pow(cur[lead],-1,p)
                normalized={k:c*inv%p for k,c in cur.items()}
                piv[lead]=normalized;terms+=len(normalized)
                if terms>2000000:raise RuntimeError("Stored term cap")
                if lead in candidates:relations.append(normalized)
                break
            factor=cur[lead];base=piv[lead];operations+=len(base)
            for k,v in base.items():
                x=(cur.get(k,0)-factor*v)%p
                if x:cur[k]=x
                else:cur.pop(k,None)
    non=sum(k not in candidates for k in piv)
    return {"rank_E":len(piv),"rank_N":non,"delta":len(piv)-non,
            "candidate_relations":[[[list(k),v] for k,v in sorted(r.items())] for r in relations],
            "operations":operations,"stored_terms":terms}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=2:ap.error("Time cap")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Exact summary SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_BOUNDARY_202203_EXACT_NOT_CLOSURE" or len(data["results"])!=418 or data["deferred"] or data["stop_reason"]:raise RuntimeError("Exact scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    recovery=gap.read(prev.prev.SOURCE)
    manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
    candidates={gap.indices(x) for x in gap.read(manifest)["candidate_masters"]}
    if len(candidates)!=63 or None in candidates or manifest not in pins:raise RuntimeError("Candidate scope")
    mapping=gap.read(prev.prev.prev.prev.prev.SOURCE)["custom_mapping"]
    custom={tuple(k):tuple(e) for k,e,w in mapping}
    project=a.exact.P
    perm=read_permutation((project/"sectormappings/auxiliary.yaml").read_text(encoding="utf-8-sig"),"VP05_full",12)
    mod=a.exact.load_codec(a.exact.ROOT/"output/tools/pyred_weight.py")
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    codec=PhysicalWeightCodec(mod,np=12,bits=bits,iord=ordering,topsectors=[203],permutation=perm)
    def decode(k):return custom[k] if k in custom else codec.decode_key(k,custom_keys=custom)
    raw=[];cache={};reverse={}
    for path in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            row=[]
            for t in terms:
                k=tuple(map(int,t[2:4]))
                if k not in cache:
                    e=decode(k)
                    if e in reverse and reverse[e]!=k:raise RuntimeError("Physical column collision")
                    cache[k]=e;reverse[e]=k
                row.append((cache[k],t[1]))
            raw.append(row)
    if len(raw)!=2678:raise RuntimeError("SYSTEM scope")
    rules={}
    def add_rule(k,items):
        if k in candidates or k in rules or k not in reverse:raise RuntimeError("Rule key scope")
        rem={tuple(j):v for j,v in items}
        if len(rem)!=len(items) or not set(rem)<=candidates:raise RuntimeError("Rule remainder scope")
        rules[k]=rem
    for k,r in recovery["candidate_rules"]:add_rule(tuple(k),r)
    for item in data["results"]:
        k=tuple(item["key"]);e=tuple(item["exponents"]);path=Path(item["path"])
        if path!=prev.ROOT/f"target_{k[0]}_{k[1]}.json" or n.sha(path)!=item["sha256"] or decode(k)!=e:raise RuntimeError("Certificate pin")
        pins[path]=item["sha256"];cert=gap.read(path)
        if cert["source_sha256"]!=prev.SHA or tuple(cert["key"])!=k:raise RuntimeError("Certificate scope")
        add_rule(e,cert["candidate_remainder"])
    if len(rules)!=421:raise RuntimeError("Rule count")
    trials=[]
    for point in prev.prev.ff.POINTS:
        p,z,d=point
        if time.monotonic()>=deadline:raise TimeoutError("Time budget")
        def ev(c):
            if c not in values:values[c]=coefficient(c,z,d,p)
            return values[c]
        values={};rows=[]
        for terms in raw:
            row={}
            for k,c in terms:
                x=(row.get(k,0)+ev(c))%p
                if x:row[k]=x
                else:row.pop(k,None)
            rows.append(row)
        rr={k:{j:v for j,c in rem.items() if (v:=ev(c))} for k,rem in rules.items()}
        before=ranks(rows,candidates,p,deadline,guard=old.memory_guard)
        reduced=[substitute(r,rr,p) for r in rows]
        after=ranks(reduced,candidates,p,deadline,guard=old.memory_guard)
        # Check specialized substitution identities are in sampled row space:
        # rank drop must equal number of independent eliminated coordinates.
        # Exact provenance relies on previously verified pinned certificates.
        consistent=(before["rank_E"]-after["rank_E"]==len(rules) and before["rank_N"]-after["rank_N"]==len(rules))
        item={"point":list(point),"before":before,"after":after,"rank_drop_matches_rules":consistent,
              "terms_before":sum(map(len,rows)),"terms_after":sum(map(len,reduced)),
              "columns_before":len(set().union(*map(set,rows))),"columns_after":len(set().union(*map(set,reduced)))}
        trials.append(item)
        a.v.log("VP05_BOUNDARY_RANK_POINT",**item)
    # If projected rank reaches number of original rows, both generic ranks
    # are forced equal; no probabilistic upper bound is used.
    certified=any(t["before"]["rank_N"]==len(raw) for t in trials)
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    payload={"status":"VP05_BOUNDARY_SAVED_RANK_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},
             "rules":len(rules),"candidate_count":len(candidates),"rows":len(raw),"trials":trials,
             "saved_SYSTEM_independence_certified_by_row_bound":certified,
             "substitution_rank_consistent":all(t["rank_drop_matches_rules"] for t in trials),
             "full_closure_proven":False}
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],rules=len(rules),saved_SYSTEM_independence_certified_by_row_bound=certified,
            substitution_rank_consistent=payload["substitution_rank_consistent"],report=dest.name,sha256=digest,
            elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
if __name__=="__main__":main()
