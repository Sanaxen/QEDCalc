"""Read-only inventory of preferred-master metadata and exact two-term aliases."""
import argparse
import time
import re
from pathlib import Path
from examples import three_loop_vp05_abc_correct_targets as prev
from examples.kira_physical_weight_codec import PhysicalWeightCodec,read_permutation
a=prev.a;n=a.n;gap=a.gap;old=a.old;sp=a.sp
ROOT=n.BASE/"output"/"vp05_abc_custom_ids36"
SOURCE=prev.ROOT/"report_1795816848815526000.json"
SHA="45c5a306d0050cf7475857cc7ea92298b13e147fd53147453d61cf1e61aedc56"

def alias(terms,custom):
    if len(terms)!=2:return None
    keys=[tuple(map(int,t[2:4])) for t in terms]
    if len(set(keys))!=2 or sum(k in custom for k in keys)!=1:return None
    i=0 if keys[0] in custom else 1
    c=[sp.cancel(sp.sympify(t[1].replace("^","**"),locals={"d":old.D,"z":old.Z})) for t in terms]
    if not all(c):return None
    return keys[i],keys[1-i],sp.cancel(-c[1-i]/c[i])

def main():
    argparse.ArgumentParser().parse_args()
    start=time.monotonic()
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Target report SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_ABC_CORRECT_TARGET_INVENTORY_NOT_PROOF":raise RuntimeError("Target scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    project=a.exact.P;aux=project/"sectormappings/auxiliary.yaml"
    perm=read_permutation(aux.read_text(encoding="utf-8-sig"),"VP05_full",12)
    if list(perm)!=data["permutation"]:raise RuntimeError("Permutation mismatch")
    mod=a.exact.load_codec(a.exact.ROOT/"output/tools/pyred_weight.py")
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    codec=PhysicalWeightCodec(mod,np=12,bits=bits,iord=ordering,topsectors=[203],permutation=perm)
    custom={tuple(k) for k in data["custom_keys"]}
    bridges=[];idx=0
    for path in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            item=alias(terms,custom)
            if item:
                k,j,c=item
                ex=codec.decode_key(j,custom_keys=custom)
                record={"id":idx,"custom":list(k),"default":list(j),"exponents":list(ex),"custom_equals_default_times":str(c),"unit":c==1}
                bridges.append(record)
                if k[1]==202:a.v.log("VP05_ABC_CUSTOM202_BRIDGE",**record)
            idx+=1
    if idx!=2678:raise RuntimeError("SYSTEM count")
    # Inventory named files only; names/order are evidence leads, not a proof.
    metadata=[]
    for path in sorted(project.rglob("*")):
        if not path.is_file() or path.is_symlink():continue
        name=path.name.lower()
        if not ("master" in name or name.endswith((".yaml",".yml"))):continue
        if path.stat().st_size>1024*1024:continue
        try:content=path.read_text(encoding="utf-8-sig")
        except UnicodeError:continue
        pins[path]=n.sha(path)
        matches=re.findall(r"VP05_full\s*\[([^\]]+)\]",content)
        metadata.append({"path":str(path.relative_to(project)),"content":content,"integrals":matches})
    payload={"status":"VP05_ABC_CUSTOM_ID_INVENTORY_NOT_PROOF","inputs":{str(k):v for k,v in pins.items()},
             "bridges":bridges,"metadata":metadata,"custom_keys":data["custom_keys"],
             "physical_mapping_verified":False,"full_closure_proven":False}
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],bridges=len(bridges),sector202_bridges=sum(r["custom"][1]==202 for r in bridges),
            metadata=[{"path":r["path"],"integrals":r["integrals"],"content":r["content"] if len(r["content"])<=12000 else None} for r in metadata],
            report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
if __name__=="__main__":main()
