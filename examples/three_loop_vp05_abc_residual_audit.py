"""Replay the stopped ABC search with explicit cap diagnostics and structure audit.

No new seeds, no Kira, no modified prior evidence. Finite field remainders
are diagnostics, not a proof of physical independence.
"""
import argparse
import os
import time
from pathlib import Path
from collections import Counter
from examples import three_loop_vp05_abc_physical as physical
from examples import three_loop_vp05_residual_structure as structure

gap=physical.gap;n=physical.n;v=physical.v;p=physical.p;f=physical.f
old=physical.old;sp=physical.sp;q=physical.q
ROOT=n.BASE/"output"/"vp05_abc_residual25"
EXPECTED_ROUNDS=6

class Cap(RuntimeError):
    pass

class Trace(physical.exact.Trace):
    def __init__(self,prime,deadline):
        super().__init__(prime,set(),deadline)
        self.peak_fill=0;self.source_index=None;self.next_memory=0
    def guard(self,row):
        self.peak_fill=max(self.peak_fill,len(row))
        if time.monotonic()>=self.deadline:raise TimeoutError("Residual replay budget")
        reasons=[]
        if self.ops>p.MAX_OPS:reasons.append("operations")
        if len(row)>p.MAX_FILL:reasons.append("row_fill")
        if self.terms>p.MAX_TERMS:reasons.append("stored_pivot_terms")
        if reasons:raise Cap(",".join(reasons))
        if self.ops>=self.next_memory:
            old.memory_guard();self.next_memory=self.ops+1024
    def metrics(self):
        return {"rank":len(self.piv),"operations":self.ops,"stored_pivot_terms":self.terms,
                "peak_fill":self.peak_fill,"source_index":self.source_index}

def replay(rows,ends,target,point,deadline):
    engine=Trace(point[0],deadline);checks=[];last=None
    cursor=0
    for rid,end in enumerate(ends):
        try:
            for i in range(cursor,end):
                engine.source_index=i
                engine.insert_source(p.field_row(rows[i],point),i)
            free,deps=physical.trace_row(engine,p.field_row(target,point))
            # Match original per-round cap accounting: original reconstruction
            # starts fresh, and earlier target probes did not consume row budget.
            # Caller uses separate engine per round below.
            result={"round":rid,"point":list(point),"completed":True,
                    "residual": [[list(k),x] for k,x in sorted(free.items())],
                    "target_dependencies":[list(k) for k in deps],
                    "same_residual_as_previous":last==free if last is not None else None,
                    **engine.metrics()}
            last=free;checks.append(result);cursor=end
        except Cap as exc:
            checks.append({"round":rid,"point":list(point),"completed":False,
                           "cap":str(exc),**engine.metrics()})
            break
    return checks

def validate_schedule(raw,rid):
    if not isinstance(raw,list) or any(not isinstance(x,(list,tuple)) or len(x)!=12 or any(type(y)!=int for y in x) for x in raw):
        raise RuntimeError(f"Malformed schedule: round={rid}")
    schedule=[tuple(x) for x in raw]
    expected=tuple(tuple(x) for x in gap.TARGETS)
    if rid==0:
        valid=tuple(schedule)==expected
    else:
        valid=1<=len(schedule)<=physical.BATCH
    if not valid:
        raise RuntimeError(f"Schedule scope: round={rid}, count={len(schedule)}, schedule={schedule}, initial_expected={expected if rid==0 else None}")
    return schedule

def load_rounds(kernel,pins,deadline):
    paths=sorted(physical.ROOT.glob("round[0-9][0-9].json"))
    if len(paths) not in (5,6):raise RuntimeError("Unexpected saved round count")
    rows=[];ends=[];seen=set();inventory=[]
    for rid,path in enumerate(paths):
        if path.name!=f"round{rid:02d}.json" or path.is_symlink():raise RuntimeError("Round path")
        pins[path]=n.sha(path);saved=gap.read(path)
        if saved["source_sha256"]!=physical.SHA or saved["kernel_sha256"]!=f.e.b.c.PIN:raise RuntimeError("Round provenance")
        schedule=validate_schedule(saved["schedule"],rid)
        v.log("VP05_ABC_SAVED_SCHEDULE",round=rid,seed_count=len(schedule),cumulative_seeds=len(seen)+len(schedule),saved_rows=len(saved["rows"]))
        if len(seen)+len(schedule)>physical.MAX_SEEDS:raise RuntimeError(f"Total seed cap: round={rid}")
        if len(saved["rows"])!=len(schedule)*len(kernel):raise RuntimeError(f"Saved row count mismatch: round={rid}")
        expected=[]
        for ex in schedule:
            if ex in seen or not physical.seed_ok(ex):raise RuntimeError("Seed scope")
            seen.add(ex);old.memory_guard()
            for ij,entries in sorted(kernel.items()):
                if time.monotonic()>=deadline:raise TimeoutError("Row replay budget")
                row=q.exact_row(ex,entries,*ij)
                expected.append({"seed":list(ex),"derivative":list(ij),"row":p.encode(row)})
                rows.append(row)
        if expected!=saved["rows"]:raise RuntimeError("Saved original row mismatch")
        ends.append(len(rows))
        inventory.append({"round":rid,"seeds":len(seen),"rows":len(rows),"sha256":pins[path]})
    return rows,ends,inventory

def describe(key,props,candidates,deadline):
    r=structure.r
    lines=r.positive(key)
    item={"integral":list(key),"sector":gap.sector(key),"degrees":list(structure.a.degrees(key)),
          "candidate":key in candidates,"is_ABC":key in gap.TARGETS,
          "rank_certificate":r.rank_certificate(key,props),
          "denominators":[{"line":i+1,"momentum":str(f.a.momentum(props[i])),"mass":props[i].mass,"power":key[i]} for i in lines],
          "numerators":[{"line":i+1,"momentum":str(f.a.momentum(prop)),"mass":prop.mass,"power":-x} for i,(prop,x) in enumerate(zip(props,key)) if x<0]}
    item["massless_factor"]=structure.massless_factor(key,props)
    matches=[]
    for dest in sorted(candidates|set(gap.TARGETS)):
        if dest==key:continue
        if time.monotonic()>=deadline:raise TimeoutError("Affine audit budget")
        match=r.affine_match(key,dest,props,deadline)
        if match:matches.append(match)
    item["affine_matches"]=matches
    return item

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        if (physical.ROOT/"running.lock").exists():raise RuntimeError("Physical search still running")
        if n.sha(physical.SOURCE)!=physical.SHA:raise RuntimeError("ABC report SHA")
        prior=gap.read(physical.SOURCE);relation=prior["combined_relation"]
        if prior["status"]!="VP05_ABC_BOUNDARY_SCOPE_NOT_CLOSURE" or relation["exact_original_source_replay"] is not True or relation["opaque_M_eliminated"] is not True:raise RuntimeError("Relation scope")
        pins={Path(k):d for k,d in prior["inputs"].items()};pins[physical.SOURCE]=physical.SHA
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input SHA")
        if relation["target_exponents"]!=[list(k) for k in gap.TARGETS] or [k for k,x in relation["coefficient_row"]]!=relation["target_keys"]:raise RuntimeError("Target scope")
        target={k:sp.cancel(sp.sympify(x,locals={"z":old.Z,"d":old.D})) for k,(_,x) in zip(gap.TARGETS,relation["coefficient_row"])}
        if len(target)!=3 or any(not x or x.free_symbols-{old.Z,old.D} for x in target.values()):raise RuntimeError("Coefficient scope")
        manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        if manifest not in pins:raise RuntimeError("Manifest not pinned")
        candidates=set(gap.indices(x) for x in gap.read(manifest)["candidate_masters"])
        if len(candidates)!=63 or None in candidates or not set(target)<=candidates:raise RuntimeError("Candidate scope")
        props=old.build_family_spec("VP05_full").propagators;kernel=old.build_kernel(props)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        rows,ends,inventory=load_rounds(kernel,pins,deadline)
        checks=[];keys=set(target)
        for point in physical.POINTS:
            last=None
            for rid,end in enumerate(ends):
                # Exact original schedule/order/caps: rebuild per round, not
                # incremental reuse, so earlier target probes cannot affect cap.
                result=replay(rows[:end],[end],target,point,deadline)[0]
                result["round"]=rid
                if result["completed"]:
                    current=result["residual"]
                    result["same_residual_as_previous"]=last==current if last is not None else None
                    last=current;keys.update(tuple(k) for k,x in current)
                checks.append(result);v.log("VP05_ABC_RESIDUAL_REPLAY",**result)
                if not result["completed"]:break
        records=[]
        for key in sorted(keys):
            item=describe(key,props,candidates,deadline);records.append(item)
            v.log("VP05_ABC_RESIDUAL_STRUCTURE",**item)
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_ABC_RESIDUAL_AUDIT_NOT_PROOF","inputs":{str(k):d for k,d in pins.items()},
                 "rounds":inventory,"checks":checks,"structures":records,"target":p.encode(target),
                 "caps":{"operations":p.MAX_OPS,"row_fill":p.MAX_FILL,"stored_pivot_terms":p.MAX_TERMS},
                 "new_seeds":0,"physical_relation_proven":False,"full_closure_proven":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=physical.scope.c.save(dest,payload)
        v.log("VP05_ABC_RESIDUAL_AUDIT_NOT_PROOF",rounds=len(ends),original_rows=len(rows),
              unique_integrals=len(keys),cap_counts=dict(Counter(x["cap"] for x in checks if not x["completed"])),
              unchanged_remainders=sum(x.get("same_residual_as_previous") is True for x in checks),
              completed_checks=sum(x["completed"] for x in checks),sha256=digest,report=dest.name,
              elapsed_s=time.monotonic()-start,new_seeds=0,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
