"""Read-only reconciliation of actual VP05 closure and boundary obligations.

A target identity is not a proof of candidate independence or whole-seed
closure. Classify separately, never generate promotion-ready evidence.
"""
import argparse
from collections import Counter
from pathlib import Path
import time
from examples import three_loop_vp05_final_diagnostic_exact as m
from examples import three_loop_vp05_stage2_sector_inventory as inventory
from three_loop.master_basis_api import Seed

gap=m.gap;n=m.n;v=m.v;p=m.p;c=m.c
ROOT=n.BASE/"output"/"vp05_stage2_coverage21"
REPORT=m.ROOT/"report_1795764409068358000.json"
SHA="596ef6a104d9e8adf34708f6fa6b1e3a1ab38c2a02a2fc39c26812f3ed3763ab"

def keys(items):
    result=[gap.indices(x) for x in items]
    if None in result or len(set(result))!=len(result):raise RuntimeError("Invalid or duplicate integral list")
    return set(result)

def classify(targets,candidates,proofs,rules,restricted,local):
    rows=[]
    for k in sorted(targets):
        sec=gap.sector(k)
        if k in candidates:kind="candidate_identity"
        elif k in proofs:kind="audited_candidate_reduction"
        elif k in rules:kind="replayed_analytic_rule"
        elif k in restricted:kind="restricted_target_evidence_review"
        else:kind="no_direct_target_certificate"
        rows.append({"target":list(k),"sector":sec,"classification":kind,
                     "diagnostic_certificate":proofs.get(k),"analytic_rule":rules.get(k),
                     "restricted_evidence":restricted.get(k),
                     "local_boundary_seeds":sorted(local.get(sec,[])),
                     "candidate_membership_proven_not_independence":k in candidates})
    return rows

def boundary_rows(groups,seed,data,props=None):
    # A passing row is evidence at that seed only, not proof of all targets
    # in the sector. Verify the candidate counts and actual project evidence.
    if data and (data.get("family")!="VP05_full" or data.get("test_seed")!=seed or
                 data.get("candidate_master_count")!=63 or data.get("candidate_envelope")!=gap.CANDIDATE_SEED):
        raise RuntimeError("Local audit scope: "+seed)
    saved={}
    for row in data.get("sector_rows",[]):
        sec=row["sector"]
        if sec in saved or sec not in groups:raise RuntimeError("Unexpected local sector")
        saved[sec]=row
    rows=[]
    for sec,targets in sorted(groups.items()):
        row=saved.get(sec,{})
        live=inventory.analyze_sector(Seed(int(seed[1:seed.index("s")]),int(seed[seed.index("s")+1:seed.index("d")]),int(seed[seed.index("d")+1:])),sec,targets)
        valid=(row.get("stable") is True and not row.get("error") and row.get("target_count")==len(targets)
               and row.get("retained_candidate_count")==len(targets) and row.get("missing_candidate_masters")==[])
        if live["restricted_exact_sector_audit_match"]:kind="restricted_equivalent_review"
        elif valid and live["matching_local_master_inventory"]:kind="saved_local_pass_inventory_match"
        elif live["matching_local_master_inventory"]:kind="local_inventory_only"
        elif valid:kind="saved_local_pass_needs_live_review"
        else:kind="missing_or_failed_local_evidence"
        rows.append({"seed":seed,"sector":sec,"candidate_count":len(targets),"classification":kind,
                     "saved_local_row":row,"live_inventory":live,"full_seed_closure_proven":False})
    return rows

def inspect():
    start=time.monotonic()
    if n.sha(REPORT)!=SHA:raise RuntimeError("Final diagnostic report SHA")
    report=gap.read(REPORT)
    if report.get("status")!="VP05_FINAL_DIAGNOSTIC_EXACT_NOT_CLOSURE" or report.get("diagnostic_verified")!=64 or report.get("prior_verified")!=46 or report.get("new_verified")!=18 or report.get("full_closure_proven") is not False:raise RuntimeError("Diagnostic scope")
    # Protect all recorded inputs, not just the final report. Absolute paths
    # are from the same local project; relocation is intentionally rejected.
    pins={Path(k):d for k,d in report["inputs"].items()}
    pins[REPORT]=SHA
    if any(not k.is_file() or n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Diagnostic input SHA")
    manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
    if manifest not in pins:raise RuntimeError("Manifest not pinned")
    data=gap.read(manifest)
    candidates=keys(data["candidate_masters"]);targets=keys(data["closure_targets"])
    if data.get("family")!="VP05_full" or len(candidates)!=63 or len(targets)!=530:raise RuntimeError("Manifest scope")
    groups=inventory._groups(data["candidate_masters"])
    if len(groups)!=26:raise RuntimeError("Sector scope")
    stage=gap.inspect()
    if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage changed")
    proofs={}
    def add(item,path):
        k=tuple(item["target"]);digest=item.get("certificate_sha256",item.get("sha256"))
        if k in proofs or gap.sector(k)!=item["sector"] or pins.get(path)!=digest or n.sha(path)!=digest:raise RuntimeError("Certificate provenance")
        cert=gap.read(path)
        if tuple(cert["target"])!=k or not set(p.decode(cert["remainder"]))<=candidates or cert.get("full_closure_proven") is not False:raise RuntimeError("Certificate scope")
        proofs[k]={"path":str(path),"sha256":digest,"remainder":cert["remainder"]}
    for item in report["prior_proofs"]:add(item,Path(item["path"]))
    for job in report["jobs"]:
        if job["unresolved"]:raise RuntimeError("Deferred target")
        for item in job["results"]:
            if item["exact_identity_verified"] is not True:raise RuntimeError("New proof flag")
            matches=[path for path,digest in pins.items() if digest==item["certificate_sha256"] and path.parent==m.ROOT and path.name.startswith("sec")]
            if len(matches)!=1:raise RuntimeError("New proof path")
            add(item,matches[0])
    if len(proofs)!=64 or Counter(map(gap.sector,proofs))!={204:16,71:16,77:16,228:16}:raise RuntimeError("Proof inventory")
    rules={tuple(x["integral"]):x["rule"] for x in report["rules"]}
    if len(rules)!=12 or not report["analytic_rules_reproduced"] or any(not set(p.decode(row))<=candidates for row in rules.values()):raise RuntimeError("Rule scope")
    # B has a formal saved archive audit. A/C are not promoted from memory
    # or a matching index; their actual certificates require separate review.
    restricted={gap.TARGETS[1]:{"kind":"Step93_B_original_IBP","archive_verified":stage["step93_target_b"]["formal_archive_verified"],
                               "archive":str(gap.ARCHIVE),"candidate_remainder_not_checked_here":True}}
    boundaries=[];local={}
    for seed in gap.SEEDS:
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_sector_closure_{seed}_audit.json"
        if path.exists():pins[path]=n.sha(path)
        rows=boundary_rows(groups,seed,gap.read(path))
        boundaries.extend(rows)
        for row in rows:
            if row["classification"] in ("restricted_equivalent_review","saved_local_pass_inventory_match","local_inventory_only"):
                local.setdefault(row["sector"],[]).append(seed)
            # Pin live master list and copied target lists where available.
            live=row["live_inventory"]
            paths=[Path(live["project"])/inventory.MANDATORY_NAME,Path(live["project"])/inventory.PREFERRED_NAME]
            if live["local_masters_path"]:paths.append(Path(live["local_masters_path"]))
            for src in paths:
                if src.is_file():pins[src]=n.sha(src)
        v.log("VP05_COVERAGE_BOUNDARY",seed=seed,counts=dict(Counter(x["classification"] for x in rows)),
              review_sectors=[x["sector"] for x in rows if x["classification"] not in ("restricted_equivalent_review","saved_local_pass_inventory_match","local_inventory_only")])
    rows=classify(targets,candidates,proofs,rules,restricted,local)
    counts=dict(Counter(x["classification"] for x in rows))
    missing=[x for x in rows if x["classification"]=="no_direct_target_certificate"]
    sector_counts={}
    for sec in sorted({x["sector"] for x in rows}):
        sector_counts[str(sec)]=dict(Counter(x["classification"] for x in rows if x["sector"]==sec))
    if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
    payload={"status":"VP05_STAGE2_COVERAGE_INVENTORY_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},
             "target_count":530,"candidate_count":63,"diagnostic_proofs":64,
             "diagnostic_manifest_overlap":len(targets&set(proofs)),"analytic_manifest_overlap":len(targets&set(rules)),
             "target_classification_counts":counts,"sector_counts":sector_counts,"targets":rows,
             "missing_direct_target_certificates":missing,"boundary_count":len(boundaries),"boundaries":boundaries,
             "boundary_classification_counts":dict(Counter(x["classification"] for x in boundaries)),
             "sector202_scope":[{"label":label,"target":list(k),"in_manifest":k in targets,"in_candidates":k in candidates,
                                 "formal_archive_verified":label=="B","additional_exact_evidence_review_required":label!="B"} for label,k in zip("ABC",gap.TARGETS)],
             "standard_boundary_status":stage["standard_boundaries"],"full_closure_proven":False,"registry_changed":False,
             "kira_executed":False}
    if len(boundaries)!=78:raise RuntimeError("Boundary count")
    return payload,time.monotonic()-start

def main():
    ap=argparse.ArgumentParser();ap.parse_args()
    payload,elapsed=inspect()
    ROOT.mkdir(exist_ok=True)
    dest=ROOT/f"report_{time.time_ns()}.json";digest=c.save(dest,payload)
    v.log("VP05_STAGE2_COVERAGE_INVENTORY_NOT_CLOSURE",targets=530,candidates=63,diagnostic_proofs=64,
          diagnostic_manifest_overlap=payload["diagnostic_manifest_overlap"],analytic_manifest_overlap=payload["analytic_manifest_overlap"],
          target_counts=payload["target_classification_counts"],boundary_counts=payload["boundary_classification_counts"],
          missing_direct_target_certificates=len(payload["missing_direct_target_certificates"]),sector202_scope=payload["sector202_scope"],
          report=str(dest),sha256=digest,elapsed_s=elapsed,inputs_unchanged=True,full_closure_proven=False)

if __name__=="__main__":main()
