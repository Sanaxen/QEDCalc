"""Read-only two-term bridge and decoded-sector structural audit."""
import argparse
import time
from pathlib import Path
from collections import Counter
from examples import three_loop_vp05_abc_system_fields as prev
from examples import three_loop_vp05_abc_banana as b

a=prev.a;sp=a.sp;n=a.n;gap=a.gap;old=a.old
ROOT=n.BASE/"output"/"vp05_abc_bridge33"
SOURCE=prev.ROOT/"report_1795816431612812500.json"
SHA="c3f651bee3ef77f500b6e53dc4da1afe0027341bde7d08bd5990185de72f1bf8"
OPAQUE={(4,73),(5,201)}

def two_term(terms):
    if len(terms)!=2:return None
    keys=[tuple(map(int,t[2:4])) for t in terms]
    if len(set(keys))!=2:return None
    c=[sp.cancel(sp.sympify(t[1].replace("^","**"),locals={"z":old.Z,"d":old.D})) for t in terms]
    if not all(c):return None
    return keys,sp.cancel(-c[1]/c[0])

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Fields report SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_ABC_SYSTEM_FIELDS_INVENTORY_NOT_PROOF":raise RuntimeError("Fields scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if pins.get(prev.SOURCE)!=prev.SHA or any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    project=a.exact.P
    codecfile=a.exact.ROOT/"output/tools/pyred_weight.py";db=project/"results/kira.db"
    mod=a.exact.load_codec(codecfile);bits,ordering=mod.from_kiradb(str(db))
    if ordering!=5:raise RuntimeError("Ordering")
    codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    props=old.build_family_spec("VP05_full").propagators
    if old.digest(old.build_kernel(props))!=a.ph.f.e.b.c.PIN:raise RuntimeError("Kernel")
    selected={r["id"] for r in data["selected_rows"]}
    keys=set();bridges=[];idx=0;length_matches=0;aux_zero=0;total_terms=0
    for path in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            if time.monotonic()>=deadline:raise TimeoutError("Bridge budget")
            total_terms+=len(terms)
            length_matches+=sum(t[0]==str(len(terms)) for t in terms)
            aux_zero+=sum(t[4:]==["0","0"] for t in terms)
            if idx in selected:keys.update(tuple(map(int,t[2:4])) for t in terms)
            pair=two_term(terms)
            if pair:
                kk,ratio=pair
                if set(kk)&OPAQUE or idx in selected:
                    bridges.append({"id":idx,"file":path.name,"ordinal":ordinal,"selected":idx in selected,
                                    "keys":[list(k) for k in kk],"ratio_first_to_second":str(ratio)})
                    keys.update(kk)
            idx+=1
    if idx!=2678:raise RuntimeError("SYSTEM count")
    decoded={};counts=Counter();sector_counts={}
    for k in sorted(keys):
        if k[0]<1024:continue
        try:
            ex=tuple(codec.decode(k[0]))
            if len(ex)!=12 or codec.encode(ex)!=k[0]:continue
        except (ValueError,AssertionError,IndexError,KeyError,OverflowError):continue
        rank=b.s.r.rank_certificate(ex,props)
        status="FREE_LOOP_ZERO" if rank["scaleless_free_loop"] else "NOT_FREE_LOOP_ZERO"
        counts[status]+=1
        sec=str(gap.sector(ex));sector_counts.setdefault(sec,Counter())[status]+=1
        decoded[k]={"exponents":list(ex),"physical_sector":gap.sector(ex),"rank_certificate":rank,"status":status}
    for item in bridges:
        item["decoded"]=[decoded.get(tuple(k)) for k in item["keys"]]
        # Only a diagnostic under the current decoder, not identification.
        if any(tuple(k) in OPAQUE for k in item["keys"]):
            b.v.log("VP05_ABC_OPAQUE_BRIDGE",**item)
    # Conditional consistency check of the physical interpretation of
    # selected decoded three-line sectors. No substitution into proofs.
    payload={"status":"VP05_ABC_BRIDGE_AUDIT_NOT_PROOF","inputs":{str(k):v for k,v in pins.items()},
             "system_rows":idx,"total_terms":total_terms,"first_field_length_matches":length_matches,
             "aux_zero_terms":aux_zero,"decoded":[[list(k),r] for k,r in sorted(decoded.items())],
             "structural_counts":dict(counts),"sector_counts":{k:dict(v) for k,v in sector_counts.items()},
             "bridges":bridges,"physical_mapping_verified":False,"full_closure_proven":False}
    import json
    payload=json.loads(json.dumps(payload))
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    b.v.log(payload["status"],system_rows=idx,total_terms=total_terms,first_field_length_matches=length_matches,
            aux_zero_terms=aux_zero,structural_counts=payload["structural_counts"],sector_counts=payload["sector_counts"],
            bridges=len(bridges),opaque_bridges=sum(any(tuple(k) in OPAQUE for k in r["keys"]) for r in bridges),
            report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)

if __name__=="__main__":main()
