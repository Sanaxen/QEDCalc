"""Independently replay corrected A/B certificates and inspect preferred ID mapping."""
import argparse,time
from pathlib import Path
from examples import three_loop_vp05_abc_correct_exact as prev
from examples.kira_physical_weight_codec import PhysicalWeightCodec,read_permutation,sector
a=prev.a;n=a.n;gap=a.gap;old=a.old;sp=a.sp
ROOT=n.BASE/"output"/"vp05_abc_exact_audit39"
SOURCE=prev.ROOT/"report_1795818793674830000.json"
SHA="bef1baaf475b7c68a48876d6dfd8671c7b3d10c4d2a264ee8956916b892571b3"
def preferred(text):
    out={}
    import re
    for line in text.splitlines():
        if not line.strip():continue
        match=re.fullmatch(r"VP05_full\[([^\]]+)\]",line.strip())
        if not match:raise ValueError("Unexpected preferred entry")
        ex=tuple(map(int,match[1].split(",")))
        if len(ex)!=12 or ex in out.values():raise ValueError("Preferred integral scope")
        out[(len(out)+1,sector(ex))]=ex
    return out

def main():
    argparse.ArgumentParser().parse_args()
    start=time.monotonic()
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Exact report SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_ABC_CORRECT_ENCODED_EXACT_REPLAY":raise RuntimeError("Exact scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    project=a.exact.P;path=project/"results/preferredMasters"
    if path not in pins:raise RuntimeError("Unpinned preferred masters")
    custom=preferred(path.read_text(encoding="utf-8-sig"))
    inventory=gap.read(prev.prev.SOURCE)
    if set(custom)!={tuple(k) for k in inventory["custom_keys"]}:raise RuntimeError("Custom key coverage")
    if custom[(3,202)]!=gap.TARGETS[2]:raise RuntimeError("C mapping")
    perm=read_permutation((project/"sectormappings/auxiliary.yaml").read_text(encoding="utf-8-sig"),"VP05_full",12)
    mod=a.exact.load_codec(a.exact.ROOT/"output/tools/pyred_weight.py")
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    codec=PhysicalWeightCodec(mod,np=12,bits=bits,iord=ordering,topsectors=[203],permutation=perm)
    weights={k:codec.encode(ex) for k,ex in custom.items()}
    if len(set(weights.values()))!=10:raise RuntimeError("Preferred default collision")
    field,z,d=sp.polys.fields.field("z,d",sp.QQ)
    def coef(x):return field.from_expr(sp.sympify(x.replace("^","**"),locals={"z":old.Z,"d":old.D}))
    def decode(k):return custom[k] if k in custom else codec.decode_key(k,custom_keys=custom)
    ids={int(i) for t in data["results"] for i,c in t["source_multipliers"]}
    rows={};seen=set();idx=0
    for f in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if f not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(f):
            for t in terms:seen.add(tuple(map(int,t[2:4])))
            if idx in ids:
                row={}
                for t in terms:prev.add(row,{decode(tuple(map(int,t[2:4]))):coef(t[1])},field.one)
                rows[idx]=row
            idx+=1
    if idx!=2678 or set(rows)!=ids:raise RuntimeError("Original scope")
    if any((w,k[1]) in seen for k,w in weights.items()):raise RuntimeError("Preferred default also present; review assignment")
    results=[]
    for label,t,ex in zip("AB",data["results"],gap.TARGETS):
        if decode(tuple(t["key"]))!=ex:raise RuntimeError("Target identity")
        rem={}
        for k,c in t["remainder"]:prev.add(rem,{decode(tuple(k)):coef(c)},field.one)
        trace={int(i):coef(c) for i,c in t["source_multipliers"]}
        expected={ex:field.one};prev.add(expected,rem,-field.one)
        if prev.replay(trace,rows)!=expected:raise RuntimeError("Independent decoded replay mismatch")
        rec={"label":label,"target":list(ex),"remainder":[[list(k),str(v.as_expr())] for k,v in sorted(rem.items())],"support":len(trace),"decoded_original_system_replay":True}
        results.append(rec);a.v.log("VP05_ABC_DECODED_EXACT_TARGET",**rec)
    payload={"status":"VP05_ABC_DECODED_EXACT_REPLAY_REVIEW_REQUIRED","inputs":{str(k):v for k,v in pins.items()},
             "custom_mapping":[[list(k),list(ex),weights[k]] for k,ex in sorted(custom.items())],
             "results":results,"preferred_order_source_semantics":"public Kira-derived source; local binary version not independently verified",
             "independent_physical_ibp_generation_verified":False,"full_closure_proven":False}
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],custom_mapping=payload["custom_mapping"],targets_verified=len(results),source_union=len(ids),report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
if __name__=="__main__":main()
