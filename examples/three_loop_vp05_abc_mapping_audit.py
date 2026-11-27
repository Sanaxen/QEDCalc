"""Audit original Kira source bytes and decoded physical IBP rows.

A codec roundtrip is not independent evidence of physical column identity.
Direct exact proportional row matches are sufficient local evidence only;
unmatched rows may be transformed, symmetry-reduced or truncated.
"""
import argparse
import gzip
import json
import os
import time
from pathlib import Path
from collections import Counter,defaultdict
from examples import three_loop_vp05_abc_bubble_syzygy as sy
from examples import three_loop_vp05_abc_physical as ph

gap=ph.gap;n=ph.n;v=ph.v;old=ph.old;sp=ph.sp;p=ph.p
scope=ph.scope;exact=scope.exact
ROOT=n.BASE/"output"/"vp05_abc_mapping31"
SOURCE=sy.ROOT/"report_1795815894232675500.json"
SHA="dd1b48e66ee81cdfa1e17aab57285dba3b29bc3df73db3bd0486b8b2aa9b5034"

def parse_system(path):
    with gzip.open(path,"rt",encoding="utf-8") as fh:
        ordinal=0
        while marker:=fh.readline():
            if marker.strip()!="Eq":raise RuntimeError("SYSTEM marker")
            head=fh.readline().strip();count=int(fh.readline())
            ordinal+=1;terms=[]
            for _ in range(count):
                fields=fh.readline().split()
                if len(fields)<4:raise RuntimeError("SYSTEM term")
                terms.append(fields)
            yield ordinal,head,terms

def proportional(left,right):
    if not left or set(left)!=set(right):return None
    k=min(left);scale=left[k]/right[k]
    return scale if all(left[j]==scale*right[j] for j in left) else None

def match(row,kernel,field,deadline):
    # For a direct unsymmetrized IBP, every nonzero term must arise
    # from at least one kernel shift of the same seed and derivative.
    common=None
    for k in sorted(row):
        options={(seed,ij) for seed,derivs in ph.inv.inverse_seeds(k,kernel).items()
                 for ij in derivs}
        common=options if common is None else common&options
        if not common:return []
    matches=[]
    for seed,ij in sorted(common):
        if time.monotonic()>=deadline:raise TimeoutError("Mapping budget")
        raw=ph.q.exact_row(seed,kernel[ij],*ij)
        rr={k:field.from_expr(sp.sympify(c)) for k,c in raw.items() if c}
        scale=proportional(row,rr)
        if scale is not None:
            matches.append({"seed":list(seed),"derivative":list(ij),"scale":str(scale.as_expr())})
    return matches

def inspect(pins,deadline):
    relation=gap.read(ph.SOURCE)["combined_relation"]
    if not relation["exact_original_source_replay"] or not relation["opaque_M_eliminated"]:raise RuntimeError("ABC scope")
    selected={int(i) for i,c in relation["original_source_multipliers"]}
    if len(selected)!=389:raise RuntimeError("Support count")
    with gzip.open(exact.SOURCE,"rt",encoding="utf-8") as fh:bundle=json.load(fh)
    if bundle["status"]!="ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED":raise RuntimeError("Export scope")
    records={int(r["global_zero_based"]):r for r in bundle["rows"]}
    if len(records)!=2241 or not selected<=set(records):raise RuntimeError("Export inventory")
    project=exact.P
    if Path(bundle["source_project"]).resolve()!=project.resolve():raise RuntimeError("Source project mismatch")
    folder=project/"tmp/VP05_full"
    files=sorted(folder.glob("SYSTEM_VP05_full_*.gz"))
    if set(x.name for x in files)!=set(bundle["source_file_sha256"]):raise RuntimeError("SYSTEM inventory")
    cfg={}
    for path in sorted((project/"config").glob("*.yaml")):
        pins[path]=n.sha(path);cfg[path.name]=path.read_text(encoding="utf-8-sig")
    codecfile=exact.ROOT/"output/tools/pyred_weight.py";db=project/"results/kira.db"
    if any(path not in pins for path in (codecfile,db,exact.SOURCE)):raise RuntimeError("Missing pinned source metadata")
    mod=exact.load_codec(codecfile);bits,ordering=mod.from_kiradb(str(db))
    if ordering!=5:raise RuntimeError("Codec ordering")
    codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    targets=[tuple(k) for k in relation["target_keys"]]
    if any(tuple(codec.decode(k[0]))!=ex or codec.encode(ex)!=k[0] for k,ex in zip(targets,gap.TARGETS)):
        raise RuntimeError("Target codec mismatch")
    selected_rows=[];global_id=0;field0=Counter();extra_fields=Counter()
    for path in files:
        digest=n.sha(path)
        if digest!=bundle["source_file_sha256"][path.name]:raise RuntimeError("SYSTEM SHA")
        if path in pins and pins[path]!=digest:raise RuntimeError("Pinned SYSTEM SHA")
        pins[path]=digest
        for ordinal,head,terms in parse_system(path):
            if global_id in selected:
                saved=records[global_id]
                actual=[{"key":[int(t[2]),int(t[3])],"coefficient":t[1]} for t in terms]
                if (saved["file"],saved["ordinal"],saved["equation_id"],saved["terms"])!=(path.name,ordinal,head,actual):
                    raise RuntimeError("Literal source replay mismatch")
                selected_rows.append(saved)
                field0.update(t[0] for t in terms);extra_fields.update(len(t) for t in terms)
            global_id+=1
    if global_id!=bundle["saved_equation_count"] or len(selected_rows)!=389:raise RuntimeError("SYSTEM coverage")
    v.log("VP05_ABC_MAPPING_SOURCE",rows=len(selected_rows),system_rows=global_id,first_field_counts=dict(field0),term_field_counts=dict(extra_fields))
    keys={tuple(t["key"]) for row in selected_rows for t in row["terms"]}
    decoded={};opaque={};sectors=defaultdict(Counter);reverse=defaultdict(list)
    for k in sorted(keys):
        if k[0]<1024:
            opaque[k]="small ID deliberately unassigned";continue
        try:
            ex=tuple(codec.decode(k[0]))
            if len(ex)!=12 or codec.encode(ex)!=k[0]:raise ValueError("Roundtrip")
            decoded[k]=ex;reverse[ex].append(k);sectors[k[1]][gap.sector(ex)]+=1
        except (ValueError,AssertionError,IndexError,KeyError,OverflowError) as exc:
            opaque[k]=str(exc)
    collisions={ex:ks for ex,ks in reverse.items() if len(ks)>1}
    # Do not identify colliding columns or infer a physical map from
    # consistency of rank labels alone.
    ambiguous={k for ks in collisions.values() for k in ks}
    v.log("VP05_ABC_MAPPING_COLUMNS",columns=len(keys),decoded=len(decoded),opaque=len(opaque),collisions=len(collisions),
          sector_map={str(k):{str(sec):count for sec,count in c.items()} for k,c in sectors.items()})
    props=old.build_family_spec("VP05_full").propagators;kernel=old.build_kernel(props)
    if old.digest(kernel)!=ph.f.e.b.c.PIN:raise RuntimeError("Kernel")
    field,z,d=sp.polys.fields.field("z,d",sp.QQ)
    checks=[]
    for idx,row in enumerate(selected_rows):
        if time.monotonic()>=deadline:raise TimeoutError("Mapping budget")
        old.memory_guard()
        rk={tuple(t["key"]) for t in row["terms"]}
        blocked=rk&(set(opaque)|ambiguous)
        rec={"id":row["global_zero_based"],"file":row["file"],"equation_id":row["equation_id"],"blocked":[list(k) for k in sorted(blocked)]}
        if blocked:rec["status"]="OPAQUE_OR_COLLISION";rec["matches"]=[]
        else:
            rr={}
            for t in row["terms"]:
                k=decoded[tuple(t["key"])]
                c=field.from_expr(sp.sympify(t["coefficient"].replace("^","**"),locals={"z":old.Z,"d":old.D}))
                vv=rr.get(k,field.zero)+c
                if vv:rr[k]=vv
                else:rr.pop(k,None)
            rec["matches"]=match(rr,kernel,field,deadline)
            rec["status"]="DIRECT_EXACT_MATCH" if rec["matches"] else "NO_DIRECT_MATCH"
            rec["decoded_row"]=[[list(k),str(c.as_expr())] for k,c in sorted(rr.items())]
        checks.append(rec)
        if (idx+1)%50==0:v.log("VP05_ABC_MAPPING_PROGRESS",processed=idx+1,counts=dict(Counter(r["status"] for r in checks)))
    return {"source_rows":len(checks),"literal_source_replay":True,"columns":len(keys),
            "decoded":[[list(k),list(ex)] for k,ex in sorted(decoded.items())],
            "opaque":[[list(k),reason] for k,reason in sorted(opaque.items())],
            "collisions":[[list(ex),[list(k) for k in ks]] for ex,ks in sorted(collisions.items())],
            "sector_map":{str(k):{str(sec):count for sec,count in c.items()} for k,c in sectors.items()},"checks":checks,
            "config_text":cfg,"physical_propagators":[{"momentum":str(ph.f.a.momentum(prop)),"mass":prop.mass} for prop in props],
            "target_keys":[list(k) for k in targets],"counts":dict(Counter(r["status"] for r in checks)),
            "physical_source_mapping_independently_verified":False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        if n.sha(SOURCE)!=SHA:raise RuntimeError("Syzygy SHA")
        data=gap.read(SOURCE)
        if data["status"]!="VP05_ABC_BUBBLE_SYZYGY_RESIDUAL_NOT_PROOF":raise RuntimeError("Syzygy scope")
        pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
        if pins.get(ph.SOURCE)!=ph.SHA or any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
        result=inspect(pins,deadline)
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        status="VP05_ABC_MAPPING_AUDIT_NOT_PROOF"
        payload={"status":status,"inputs":{str(k):v for k,v in pins.items()},"result":result,"full_closure_proven":False,"registry_changed":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=scope.c.save(dest,payload)
        v.log(status,source_rows=result["source_rows"],columns=result["columns"],decoded=len(result["decoded"]),
              opaque=result["opaque"],collisions=result["collisions"],counts=result["counts"],
              sector_map=result["sector_map"],literal_source_replay=True,physical_source_mapping_independently_verified=False,
              report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
