"""Locate true sector202 targets without changing old encoded certificates."""
import argparse
import time
from pathlib import Path
from collections import Counter,defaultdict
from examples import three_loop_vp05_abc_permutation_audit as prev
from examples.kira_physical_weight_codec import PhysicalWeightCodec,read_permutation,sector

a=prev.a;n=a.n;gap=a.gap;old=a.old
ROOT=n.BASE/"output"/"vp05_abc_correct_targets35"
SOURCE=prev.ROOT/"report_1795816708739025600.json"
SHA="df6a81040e493d2a09e7bae48fecc7d08ffde3654c08353fb1be7531c020f1f3"

def main():
    argparse.ArgumentParser().parse_args()
    start=time.monotonic()
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Permutation report SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_ABC_PERMUTATION_AUDIT_NOT_PROOF":raise RuntimeError("Permutation scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    project=a.exact.P
    aux=project/"sectormappings/auxiliary.yaml"
    if aux not in pins:raise RuntimeError("Unpinned permutation metadata")
    perm=read_permutation(aux.read_text(encoding="utf-8-sig"),"VP05_full",12)
    if list(perm)!=data["permutation"]:raise RuntimeError("Permutation mismatch")
    mod=a.exact.load_codec(a.exact.ROOT/"output/tools/pyred_weight.py")
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    codec=PhysicalWeightCodec(mod,np=12,bits=bits,iord=ordering,topsectors=[203],permutation=perm)
    legacy=gap.read(a.ph.SOURCE)["combined_relation"]
    oldkeys=[tuple(k) for k in legacy["target_keys"]]
    newkeys=[(codec.encode(ex),sector(ex)) for ex in gap.TARGETS]
    if len(set(newkeys))!=3 or set(newkeys)&set(oldkeys):raise RuntimeError("Target key scope")
    support={int(i) for i,c in legacy["original_source_multipliers"]}
    if len(support)!=389:raise RuntimeError("Legacy support scope")
    allkeys=set();occ=defaultdict(list);heads=defaultdict(list);idx=0
    targets=set(oldkeys+newkeys)
    for path in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            keys={tuple(map(int,t[2:4])) for t in terms};allkeys.update(keys)
            for k in keys&targets:occ[k].append(idx)
            for k in targets:
                if int(head)==k[0]:heads[k].append(idx)
            idx+=1
    if idx!=2678:raise RuntimeError("SYSTEM count")
    # In this specific saved project low IDs are conservatively left opaque.
    # This cutoff is not a general Kira encoding rule.
    custom={k for k in allkeys if k[0]<1024}
    counts=Counter();errors=[]
    for key in sorted(allkeys-custom):
        try:codec.decode_key(key,custom_keys=custom);counts["sector_match"]+=1
        except (ValueError,AssertionError,IndexError,KeyError,OverflowError) as exc:
            counts["decode_error"]+=1;errors.append({"key":list(key),"error":str(exc)})
    records=[]
    for label,ex,oldkey,newkey in zip("ABC",gap.TARGETS,oldkeys,newkeys):
        if codec.decode_key(newkey,custom_keys=custom)!=ex:raise RuntimeError("New key roundtrip")
        record={"label":label,"physical_exponents":list(ex),"old_key":list(oldkey),
                "old_key_physical_exponents":list(codec.decode_key(oldkey,custom_keys=custom)),
                "new_key":list(newkey),"new_occurrence_count":len(occ[newkey]),
                "new_head_count":len(heads[newkey]),"new_source_rows":occ[newkey],
                "new_legacy_support_rows":sorted(set(occ[newkey])&support),
                "old_occurrence_count":len(occ[oldkey])}
        records.append(record);a.v.log("VP05_ABC_CORRECT_TARGET",**record)
    payload={"status":"VP05_ABC_CORRECT_TARGET_INVENTORY_NOT_PROOF","inputs":{str(k):v for k,v in pins.items()},
             "permutation":list(perm),"weight_bits":list(bits),"ordering":ordering,
             "system_rows":idx,"columns":len(allkeys),"custom_keys":[list(k) for k in sorted(custom)],
             "decode_counts":dict(counts),"decode_errors":errors,"targets":records,
             "legacy_certificate_applies_to_new_keys":False,"full_closure_proven":False,"registry_changed":False}
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],system_rows=idx,columns=len(allkeys),custom_keys=payload["custom_keys"],
            decode_counts=dict(counts),decode_errors=errors[:10],targets_present=sum(bool(r["new_occurrence_count"]) for r in records),
            legacy_certificate_applies_to_new_keys=False,report=dest.name,sha256=digest,
            elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)

if __name__=="__main__":main()
