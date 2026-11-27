"""Recovery gate: compare physical candidate basis and local boundary evidence.

Retain historical evidence at its original limited scope, never mark closure.
"""
import argparse,time
from pathlib import Path
from examples import three_loop_vp05_203_exact_lift as prev
from examples import three_loop_vp05_stage2_boundary_recovery as recovery
from examples import three_loop_vp05_stage2_coverage_inventory as coverage
from examples import three_loop_sector203_weight_audit as weight
a=prev.a;n=a.n;gap=a.gap;sp=a.sp;old=a.old
ROOT=n.BASE/"output"/"vp05_recovery_gate42"
SOURCE=prev.ROOT/"report_1795820541102928900.json"
SHA="08a3f4fb2da87bd77b898d4671ff35cd9c9d769cb24bca1876824f5f30473ccf"
BOUNDARY=recovery.ROOT/"report_1795766922672670100.json"
BOUNDARY_SHA="c61fe4a04509aa107aa8a111edc39f0e181f3066c3b917f03f992946ac782553"

def basis_exchange(candidates,targets,rows,field):
    # rows express targets in alternative preferred integrals and common basis.
    missing=sorted(set().union(*(set(r) for r in rows))-candidates)
    if len(missing)!=2 or not set(targets)<=candidates:raise RuntimeError("Unexpected ABC basis exchange scope")
    a,b=rows
    u,v=missing
    det=a.get(u,0)*b.get(v,0)-a.get(v,0)*b.get(u,0)
    if not det:raise RuntimeError("Singular basis exchange")
    ra={targets[0]:field.one};rb={targets[1]:field.one}
    for k,c in a.items():
        if k not in missing:prev.add(ra,{k:c},-field.one)
    for k,c in b.items():
        if k not in missing:prev.add(rb,{k:c},-field.one)
    invu={};invv={}
    prev.add(invu,ra,b.get(v,0)/det);prev.add(invu,rb,-a.get(v,0)/det)
    prev.add(invv,ra,-b.get(u,0)/det);prev.add(invv,rb,a.get(u,0)/det)
    rules={u:invu,v:invv}
    for target,row in zip(targets,rows):
        replay={}
        for k,c in row.items():prev.add(replay,rules.get(k,{k:field.one}),c)
        if replay!={target:field.one}:raise RuntimeError("Basis exchange replay")
    if any(not set(r)<=candidates for r in rules.values()):raise RuntimeError("Noncandidate remainder")
    return det,rules

def main():
    argparse.ArgumentParser().parse_args()
    start=time.monotonic()
    if n.sha(SOURCE)!=SHA or n.sha(BOUNDARY)!=BOUNDARY_SHA:raise RuntimeError("Recovery report SHA")
    data=gap.read(SOURCE);boundary=gap.read(BOUNDARY)
    if data["status"]!="VP05_203_ORIGINAL_EXACT_LIFT_NOT_CLOSURE" or not data["original_528_row_replay"] or not data["physical_index_system_replay"]:raise RuntimeError("203 scope")
    if boundary["status"]!="VP05_BOUNDARY_RECOVERY_NOT_CLOSURE" or boundary["local_evidence_total"]!=57:raise RuntimeError("Boundary scope")
    pins={Path(k):v for k,v in data["inputs"].items()}
    for k,v in boundary["inputs"].items():
        path=Path(k)
        if path in pins and pins[path]!=v:raise RuntimeError("Conflicting evidence SHA")
        pins[path]=v
    pins[SOURCE]=SHA;pins[BOUNDARY]=BOUNDARY_SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
    candidates,targets=coverage.manifest_scope(gap.read(manifest))
    if manifest not in pins or weight.CANDIDATE not in pins:raise RuntimeError("Unpinned candidate evidence")
    legacy_list=weight.parse_file_integrals(weight.CANDIDATE)
    legacy=set(legacy_list)
    if not legacy or len(legacy)!=len(legacy_list) or any(len(k)!=12 for k in legacy):raise RuntimeError("Invalid legacy candidate inventory")
    comparison={"legacy_count":len(legacy),"manifest_count":len(candidates),"common_count":len(legacy&candidates),
                "legacy_only":[list(k) for k in sorted(legacy-candidates)],
                "manifest_only":[list(k) for k in sorted(candidates-legacy)],
                "exact_set_match":legacy==candidates}
    a.v.log("VP05_RECOVERY_CANDIDATE_COMPARISON",**comparison)
    # The pinned Stage-2 manifest is authoritative for the recovery gate.
    # Legacy list disagreement is retained explicitly, not used as a proof of equivalence.
    decoded=gap.read(prev.prev.SOURCE)
    if not all(t["decoded_original_system_replay"] for t in decoded["results"]):raise RuntimeError("ABC replay scope")
    field,z,d=sp.polys.fields.field("z,d",sp.QQ)
    def coef(x):return field.from_expr(sp.sympify(x.replace("^","**"),locals={"z":old.Z,"d":old.D}))
    rows=[{tuple(k):coef(c) for k,c in t["remainder"]} for t in decoded["results"]]
    if len(rows)!=2 or [tuple(t["target"]) for t in decoded["results"]]!=list(gap.TARGETS[:2]):raise RuntimeError("ABC target scope")
    # Report actual scope even when the earlier assumed 2x2 exchange is not applicable.
    abc_missing=set().union(*(set(r) for r in rows))-candidates
    abc_membership=[k in candidates for k in gap.TARGETS]
    a.v.log("VP05_RECOVERY_ABC_SCOPE",ABC_in_manifest=abc_membership,
            remainder_outside_manifest=[list(k) for k in sorted(abc_missing)])
    det=None;rules={};issues=[]
    if len(abc_missing)==2 and all(abc_membership[:2]):
        try:det,rules=basis_exchange(candidates,gap.TARGETS[:2],rows,field)
        except RuntimeError as exc:issues.append(str(exc))
    else:
        issues.append("ABC basis exchange scope differs from assumption")
    relation={tuple(k):coef(c) for k,c in data["target"]}
    noncandidate=set(relation)-candidates
    a.v.log("VP05_RECOVERY_203_SCOPE",relation_in_manifest=[list(k) for k in sorted(set(relation)&candidates)],
            relation_outside_manifest=[list(k) for k in sorted(noncandidate)])
    if len(noncandidate)==1:
        k=next(iter(noncandidate));scale=relation[k]
        rules[k]={j:-c/scale for j,c in relation.items() if j!=k}
    else:issues.append("203 relation scope differs from assumption")
    if any(not set(r)<=candidates for r in rules.values()):raise RuntimeError("Noncandidate remainder")
    enc=lambda row:[[list(k),str(c.as_expr())] for k,c in sorted(row.items())]
    a.v.log("VP05_RECOVERY_BASIS_EXCHANGE",determinant=str(det.as_expr()) if det is not None else None,issues=issues,rules=[[list(k),enc(r)] for k,r in sorted(rules.items())])
    # Re-run original read-only local master-list and archive validators.
    fresh=recovery.inspect()
    oldrows={(r["seed"],r["sector"]):r for r in boundary["boundaries"]}
    newrows={(r["seed"],r["sector"]):r for r in fresh["boundaries"]}
    if len(oldrows)!=78 or set(oldrows)!=set(newrows):raise RuntimeError("Boundary row coverage")
    differences=[];sources={}
    for key,r in oldrows.items():
        nr=newrows[key]
        if r["candidate_count"]!=nr["candidate_count"] or r["local_evidence_present"]!=nr["local_evidence_present"]:differences.append(list(key))
        if not nr["local_evidence_present"]:continue
        if (nr.get("isolated_evidence") or {}).get("state")=="completed_local_retained":kind="isolated_physical_master_inventory"
        elif nr["classification"]=="restricted_equivalent_review":kind="restricted_retention_audit"
        else:kind="physical_master_inventory"
        sources[kind]=sources.get(kind,0)+1
    if differences or fresh["local_evidence_total"]!=57:raise RuntimeError("Boundary recovery changed: "+str(differences))
    for key,digest in fresh["inputs"].items():
        path=Path(key)
        if path in pins and pins[path]!=digest:raise RuntimeError("Fresh evidence SHA mismatch")
        pins[path]=digest
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    payload={"status":"VP05_RECOVERY_GATE_REVIEW_REQUIRED","inputs":{str(k):v for k,v in pins.items()},
             "candidate_count":len(candidates),"closure_target_count":len(targets),
             "ABC_basis_exchange_determinant":str(det.as_expr()) if det is not None else None,"candidate_comparison":comparison,"ABC_in_manifest":abc_membership,"review_issues":issues,"candidate_rules":[[list(k),enc(r)] for k,r in sorted(rules.items())],
             "local_evidence_total":57,"local_evidence_sources":sources,"boundary_counts":fresh["counts"],
             "boundary_scope":"local evidence only; restricted retention audits not whole seed closure",
             "remaining_boundaries":[list(k) for k,r in sorted(newrows.items()) if not r["local_evidence_present"]],
             "full_closure_proven":False,"registry_changed":False}
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],candidate_count=len(candidates),local_evidence_total=57,local_evidence_sources=sources,
            boundary_counts=fresh["counts"],remaining_boundaries=payload["remaining_boundaries"],
            determinant=payload["ABC_basis_exchange_determinant"],candidate_comparison=comparison,review_issues=issues,report=dest.name,sha256=digest,
            elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
if __name__=="__main__":main()
