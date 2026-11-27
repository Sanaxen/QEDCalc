"""Lift old sector203 compressed proof using original rational group weights.
Validate directly against pinned raw SYSTEM in corrected physical index space.
"""
import argparse,time
from pathlib import Path
from fractions import Fraction
from examples import three_loop_vp05_correct_rank as prev
from examples import three_loop_sector203_exact_target_engine as engine
from examples import three_loop_sector203_exact_528_provenance_audit as lineage
from examples.kira_physical_weight_codec import PhysicalWeightCodec,read_permutation
a=prev.a;n=a.n;gap=a.gap;old=a.old;sp=a.sp
ROOT=n.BASE/"output"/"vp05_203_exact_lift41"
SOURCE=prev.ROOT/"report_1795819993875904100.json"
SHA="de076a182ec04b0ca0a8f6ea91aee451df87d76368d0847744a69c77b4385827"

def add(row,other,factor):
    for k,v in other.items():
        x=row.get(k,0)+factor*v
        if x:row[k]=x
        else:row.pop(k,None)

def lift(groups,packed,coeffs,witness,rows,field,deadline):
    trace={};touched=set()
    for i,g in enumerate(groups):
        if time.monotonic()>deadline:raise TimeoutError("Lift deadline")
        old.memory_guard()
        weights={int(x["row"]):Fraction(x["ratio"]) for x in g["ratios_to_representative"]}
        if len(weights)!=len(g["ratios_to_representative"]) or set(weights)!=set(g["rows"]) or set(weights)!=set(packed[i]["original_rows"]) or touched&set(weights):
            raise RuntimeError("Group coverage")
        if weights[int(g["representative"])]!=1:raise RuntimeError("Representative")
        touched.update(weights)
        for j,w in weights.items():
            rid=int(witness[j]["row_index"])
            f=field.one*w.numerator/w.denominator
            add(trace,{rid:coeffs[i]*f},field.one)
    if touched!=set(range(528)):raise RuntimeError("Witness partition")
    return trace

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Time cap")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Rank report SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_CORRECT_C_203_RANK_NOT_CLOSURE" or not data["C_restricted_independence_certified"]:raise RuntimeError("Rank scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    def read(path):
        path=Path(path)
        if not path.is_absolute():path=n.BASE/path
        digest=n.sha(path)
        if path in pins and pins[path]!=digest:raise RuntimeError("Old artifact SHA")
        pins[path]=digest
        return gap.read(path)
    packed=read(lineage.DEFAULT);cert=read(engine.OUT)
    witness=read(packed["source"])["rows"];groups=read(packed["groups_source"])["proportional_classes"]
    if len(witness)!=528 or len(groups)!=166 or len(packed["rows"])!=166:raise RuntimeError("Old scope")
    packed_path=Path(lineage.DEFAULT)
    if not packed_path.is_absolute():packed_path=n.BASE/packed_path
    if cert["source_sha256"]!=n.sha(packed_path):raise RuntimeError("Certificate source SHA")
    proof=cert["symbolic_result"]
    if not proof["target_symbolic_proof"] or not proof["compressed_source_exact_replay"]:raise RuntimeError("Old proof scope")
    field,z,d=sp.polys.fields.field("z,d",sp.QQ)
    def coef(c):return field.from_expr(sp.sympify(str(c).replace("^","**"),locals={"z":old.Z,"d":old.D}))
    coeffs={int(t["row"]):coef(t["coefficient"]) for t in proof["certificate_coefficients"]}
    if set(coeffs)!=set(range(166)):raise RuntimeError("Certificate coverage")
    project=a.exact.P
    mapping=gap.read(prev.SOURCE)["custom_mapping"]
    custom={tuple(k):tuple(ex) for k,ex,w in mapping}
    perm=read_permutation((project/"sectormappings/auxiliary.yaml").read_text(encoding="utf-8-sig"),"VP05_full",12)
    mod=a.exact.load_codec(a.exact.ROOT/"output/tools/pyred_weight.py")
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    codec=PhysicalWeightCodec(mod,np=12,bits=bits,iord=ordering,topsectors=[203],permutation=perm)
    def decode(k):return custom[k] if k in custom else codec.decode_key(k,custom_keys=custom)
    wanted={int(r["row_index"]):r for r in witness}
    if len(wanted)!=528:raise RuntimeError("Duplicate witness")
    rows={};idx=0
    for path in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            if idx in wanted:
                w=wanted[idx]
                literal=[{"key":list(map(int,t[2:4])),"coefficient":t[1]} for t in terms]
                if w["file"]!=path.name or str(w["equation_id"])!=str(head) or w["terms"]!=literal:raise RuntimeError("Witness transcription mismatch")
                row={}
                for t in literal:add(row,{decode(tuple(t["key"])):coef(t["coefficient"])},field.one)
                rows[idx]=row
            idx+=1
    if idx!=2678 or set(rows)!=set(wanted):raise RuntimeError("Original coverage")
    trace=lift(groups,packed["rows"],coeffs,witness,rows,field,deadline)
    expected={}
    for k,c in engine.TARGET.items():add(expected,{decode(k):coef(c)},field.one)
    actual={}
    for j,(rid,c) in enumerate(sorted(trace.items()),1):
        if time.monotonic()>deadline:raise TimeoutError("Replay deadline")
        if j%10==0:old.memory_guard()
        add(actual,rows[rid],c)
        if j%40==0:a.v.log("VP05_203_LIFT_PROGRESS",rows=j,total=len(trace),columns=len(actual),elapsed_s=time.monotonic()-start)
    if actual!=expected:raise RuntimeError("Original physical-index replay mismatch")
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    payload={"status":"VP05_203_ORIGINAL_EXACT_LIFT_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},
             "target":[[list(k),str(c.as_expr())] for k,c in sorted(expected.items())],
             "source_multipliers":[[i,str(c.as_expr())] for i,c in sorted(trace.items())],
             "original_528_row_replay":True,"physical_index_system_replay":True,
             "independent_physical_ibp_generation_verified":False,"full_closure_proven":False}
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],target=payload["target"],original_rows=528,source_support=len(trace),report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
if __name__=="__main__":main()
