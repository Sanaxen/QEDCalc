"""Read actual Kira auxiliary permutation; do not infer it from residuals."""
import argparse
import json
import re
import time
from pathlib import Path
from collections import Counter
from examples import three_loop_vp05_abc_bridge_audit as prev

a=prev.a;n=a.n;gap=a.gap;old=a.old
ROOT=n.BASE/"output"/"vp05_abc_permutation34"
SOURCE=prev.ROOT/"report_1795816554729002900.json"
SHA="13e4281ea9ad5102d7969dc6440a438f4666ff9bcb4049bd6364cfe355cc8435"

def validate_perm(values,np):
    if len(values)!=np or sorted(values)!=list(range(np)):
        raise ValueError("Expected zero-based Kira permutation")
    return tuple(values)

def mask_to_internal(mask,perm):
    return sum(1<<i for i,j in enumerate(perm) if mask&(1<<j))

def to_physical(indices,perm):
    out=[0]*len(perm)
    for i,j in enumerate(perm):out[j]=indices[i]
    return tuple(out)

def to_internal(indices,perm):
    return tuple(indices[j] for j in perm)

def read_permutation(text,np):
    # Kira's writer emits a single family record and a flow-style permutation.
    names=re.findall(r'^\s*-\s*name:\s*["\']?([^"\'\s]+)',text,re.M)
    values=re.findall(r'^\s*permutation:\s*\[([^\]]+)\]',text,re.M)
    if names!=["VP05_full"] or len(values)!=1:
        raise RuntimeError("Unexpected auxiliary family/permutation format")
    return validate_perm([int(x.strip()) for x in values[0].split(",")],np)

def main():
    ap=argparse.ArgumentParser();args=ap.parse_args()
    start=time.monotonic()
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Bridge SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_ABC_BRIDGE_AUDIT_NOT_PROOF":raise RuntimeError("Bridge scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    project=a.exact.P
    # Source Kira ReadYamlFiles.cpp writes this metadata in outputDir.
    candidates=sorted(project.rglob("auxiliary.yaml"))
    found=[]
    for path in candidates:
        if path.parent.name!="sectormappings":continue
        if path.is_symlink():raise RuntimeError("Linked auxiliary file")
        pins[path]=n.sha(path)
        content=path.read_text(encoding="utf-8-sig")
        found.append({"path":str(path),"content":content,"permutation":list(read_permutation(content,12))})
    if not found:
        result={"status":"VP05_ABC_PERMUTATION_METADATA_MISSING_NOT_PROOF","metadata":[]}
    else:
        perms={tuple(r["permutation"]) for r in found}
        if len(perms)!=1:raise RuntimeError("Conflicting auxiliary permutations")
        perm=perms.pop()
        mod=a.exact.load_codec(a.exact.ROOT/"output/tools/pyred_weight.py")
        bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
        top=mask_to_internal(203,perm)
        codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[top])
        props=old.build_family_spec("VP05_full").propagators
        if old.digest(old.build_kernel(props))!=a.ph.f.e.b.c.PIN:raise RuntimeError("Kernel")
        mapped={};counts=Counter();sector_counts={}
        for key,prior in data["decoded"]:
            k=tuple(key)
            ex=to_physical(codec.decode(k[0]),perm)
            if codec.encode(to_internal(ex,perm))!=k[0]:raise RuntimeError("Roundtrip")
            rank=prev.b.s.r.rank_certificate(ex,props)
            status="FREE_LOOP_ZERO" if rank["scaleless_free_loop"] else "NOT_FREE_LOOP_ZERO"
            counts[status]+=1
            sec=str(gap.sector(ex));sector_counts.setdefault(sec,Counter())[status]+=1
            mapped[k]={"exponents":list(ex),"sector":gap.sector(ex),"old_exponents":prior["exponents"],"rank_certificate":rank}
        bridges=[]
        for item in data["bridges"]:
            if any(tuple(k) in prev.OPAQUE for k in item["keys"]):
                row={**item,"corrected":[mapped.get(tuple(k)) for k in item["keys"]]}
                bridges.append(row);a.v.log("VP05_ABC_PERMUTED_BRIDGE",**row)
        relation=gap.read(a.ph.SOURCE)["combined_relation"]
        targets=[]
        for key,expected in zip(relation["target_keys"],gap.TARGETS):
            ex=to_physical(codec.decode(key[0]),perm)
            targets.append({"key":key,"old_expected":list(expected),"corrected":list(ex),"unchanged":ex==expected})
        result={"status":"VP05_ABC_PERMUTATION_AUDIT_NOT_PROOF","metadata":found,"permutation":list(perm),
                "internal_topsector":top,"counts":dict(counts),"sector_counts":{k:dict(v) for k,v in sector_counts.items()},
                "targets":targets,"bridges":bridges,"mapped":[[list(k),v] for k,v in sorted(mapped.items())]}
    payload={**result,"inputs":{str(k):v for k,v in pins.items()},"physical_mapping_verified":False,"full_closure_proven":False}
    payload=json.loads(json.dumps(payload))
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(result["status"],metadata=found,permutation=result.get("permutation"),internal_topsector=result.get("internal_topsector"),
            counts=result.get("counts"),sector_counts=result.get("sector_counts"),targets=result.get("targets"),
            report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)

if __name__=="__main__":main()
