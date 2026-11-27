"""Reaudit restricted ABC evidence and eliminate opaque M before reuse.

The resulting candidate-only relation is in the saved Kira column space.
Physical interpretation requires a separate source/column mapping audit.
Never revise the candidate set or mark a boundary closed here.
"""
import gzip
import time
from pathlib import Path
from collections import Counter
from examples import three_loop_vp05_stage2_boundary_recovery as recovery
from examples import three_loop_vp05_abc_stage2_scope_inventory as abc
from examples import three_loop_vp05_sector202_target_b_step93_formal_promotion as b
from examples import three_loop_vp05_sector202_target_exact_reduction as exact
from examples import three_loop_vp05_a_saved_proof_audit as a
from examples import three_loop_vp05_c_saved_rank_audit as ca
from examples import three_loop_vp05_a_confirmed_archive as archive
from examples import three_loop_sector203_weight_audit as weight

gap=recovery.gap;n=recovery.n;v=recovery.v;c=recovery.c;sp=exact.sp
ROOT=n.BASE/"output"/"vp05_abc_boundary_scope23"
SOURCE=recovery.ROOT/"report_1795766922672670100.json"
SHA="c61fe4a04509aa107aa8a111edc39f0e181f3066c3b917f03f992946ac782553"
OPAQUE=(4,73)

def eliminate(a_row,b_row,a_trace,b_trace,keys,field):
    if set(a_row)!={keys[0],keys[2],OPAQUE} or set(b_row)!={keys[1],keys[2],OPAQUE}:
        raise RuntimeError("Unexpected A/B support")
    if a_row[keys[0]]!=field.one or b_row[keys[1]]!=field.one:
        raise RuntimeError("Target normalization")
    scale_a=-b_row[OPAQUE];scale_b=a_row[OPAQUE]
    def combine(left,right):
        out={}
        for k in set(left)|set(right):
            value=scale_a*left.get(k,field.zero)+scale_b*right.get(k,field.zero)
            if value:out[k]=value
        return out
    row=combine(a_row,b_row);trace=combine(a_trace,b_trace)
    if OPAQUE in row or set(row)!={*keys} or not trace:
        raise RuntimeError("Opaque cancellation or candidate relation scope")
    return row,trace,(scale_a,scale_b)

def scope_rows(rows):
    result=[]
    for row in rows:
        if row["local_evidence_present"]:continue
        sec=row["sector"]
        result.append({"seed":row["seed"],"sector":sec,"candidate_count":row["candidate_count"],
                       "contains_202":sec&202==202,"contains_203":sec&203==203,
                       "abc_relation_directly_in_sector":sec==202,
                       "restricted_source_equivalence_proven":False,
                       "boundary_closed":False})
    return result

def inspect():
    start=time.monotonic()
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Recovery SHA")
    prior=gap.read(SOURCE)
    if prior.get("status")!="VP05_BOUNDARY_RECOVERY_NOT_CLOSURE" or prior.get("local_evidence_total")!=57:raise RuntimeError("Recovery scope")
    pins={Path(k):d for k,d in prior["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Recovery input SHA")
    abc_info=abc.run()
    if not all(abc_info["candidate_target_coverage"].values()):raise RuntimeError("ABC candidate coverage")
    aa=a.audit();bb=b.post_audit();cc=ca.audit()
    if aa["status"]!="VP05_A_SAVED_PROOF_READ_ONLY_AUDIT_PASS" or bb["status"]!="B_STEP93_FORMAL_ARTIFACT_POST_AUDIT_PASS" or cc["status"]!="VP05_C_SAVED_EXACT_RANK_CERTIFICATE_AUDIT_PASS":
        raise RuntimeError("ABC audit")
    v.log("VP05_ABC_REAUDITED",A=aa["status"],B=bb["status"],C=cc["status"],C_scope="restricted SYSTEM only")
    ap=archive.DEST/a.proof.OUTPUT.name;bp=b.PACKAGE/"evidence/proof_step93.json"
    bsrc=b.PACKAGE/"evidence/original_source_rows.json.gz"
    pins.update({ap:a.PROOF_SHA,bp:b.EXPECTED_PROOF,exact.SOURCE:a.batch.SOURCE_SHA,
                 bsrc:a.batch.SOURCE_SHA,ca.cert.OUTPUT:ca.SHA,
                 archive.DEST/"manifest.json":"c4b285f0066160f0bf443ad2278b6e9dfe183fd033aa78bcbde078ddaf43529e",
                 b.MANIFEST:gap.EXPECTED_MANIFEST_SHA256})
    if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("ABC archive/source SHA")
    ar=gap.read(ap);br=gap.read(bp)
    if ar["source_sha256"]!=br["source_sha256"] or ar["source_sha256"]!=pins[exact.SOURCE]:
        raise RuntimeError("A/B do not share source")
    codecfile=exact.ROOT/"output/tools/pyred_weight.py";db=exact.P/"results/kira.db"
    for path in (codecfile,db):pins[path]=n.sha(path)
    mod=exact.load_codec(codecfile);bits,ordering=mod.from_kiradb(str(db))
    if ordering!=5:raise RuntimeError("Codec ordering")
    codec=mod.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
    keys=[(codec.encode(k),139) for k in gap.TARGETS]
    if any(tuple(codec.decode(k[0]))!=ex for k,ex in zip(keys,gap.TARGETS)) or keys[2]!=ca.cert.C:raise RuntimeError("ABC key bridge")
    field,z,d=sp.polys.fields.field("z,d",sp.QQ)
    def coef(x):return field.from_expr(sp.sympify(str(x).replace("^","**"),locals={"z":sp.Symbol("z"),"d":sp.Symbol("d")}))
    def decode(items,trace=False):
        out={}
        for key,value in items:
            k=int(key) if trace else tuple(key)
            if k in out:raise RuntimeError("Duplicate key")
            out[k]=coef(value)
        return out
    arow=decode(ar["target_terms"]);brow=decode(br["target_terms"])
    at=decode(ar["source_multipliers"],True);bt=decode(br["source_multipliers"],True)
    if len(at)!=339 or len(bt)!=389:raise RuntimeError("Multiplier count")
    row,trace,scales=eliminate(arow,brow,at,bt,keys,field)
    with gzip.open(exact.SOURCE,"rt",encoding="utf-8") as fh:
        import json
        source=json.load(fh)
    originals={int(x["global_zero_based"]):x for x in source["rows"]}
    if len(originals)!=2241 or not set(trace)<=set(originals):raise RuntimeError("Original source scope")
    replay={}
    for rid,mult in sorted(trace.items()):
        for term in originals[rid]["terms"]:
            k=tuple(term["key"])
            val=replay.get(k,field.zero)+mult*coef(term["coefficient"])
            if val:replay[k]=val
            else:replay.pop(k,None)
    if replay!=row:raise RuntimeError("Combined original source replay mismatch")
    relation={"target_keys":[list(k) for k in keys],"target_exponents":[list(k) for k in gap.TARGETS],
              "coefficient_row":[[list(k),str(row[k].as_expr())] for k in keys],
              "scales":[str(x.as_expr()) for x in scales],
              "original_source_multipliers":[[k,str(x.as_expr())] for k,x in sorted(trace.items())],
              "opaque_M_eliminated":True,"exact_original_source_replay":True,
              "physical_source_mapping_independently_verified":False,
              "candidate_revision_review_required":True}
    v.log("VP05_ABC_COMBINED_RELATION",coefficient_row=relation["coefficient_row"],source_support=len(trace),opaque_M_eliminated=True,exact_original_source_replay=True)
    # Restricted sector203 evidence discovery only. Do not trust filenames
    # or promote a compressed-source identity into an original-source proof.
    sector203=[]
    for path in sorted(gap.AUDIT.glob("vp05_target_symbolic*.json")):
        if path.is_symlink() or not path.is_file():raise RuntimeError("Linked sector203 evidence")
        digest=n.sha(path);pins[path]=digest
        entry={"path":str(path),"sha256":digest,"bytes":path.stat().st_size}
        if entry["bytes"]<=32*1024**2:
            data=gap.read(path)
            for k in ("status","target_symbolic_proof","compressed_source_exact_replay","original_528_row_replay","rank","rows_saved","source_sha256"):
                if k in data:entry[k]=data[k]
        sector203.append(entry)
    rows=scope_rows(prior["boundaries"])
    if len(rows)!=21:raise RuntimeError("Boundary scope")
    for item in rows:v.log("VP05_ABC_BOUNDARY_SCOPE",**item)
    if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
    return {"status":"VP05_ABC_BOUNDARY_SCOPE_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},
            "audits":{"A":aa,"B":bb,"C":cc},"combined_relation":relation,
            "sector203_artifact_inventory":sector203,"boundaries":rows,
            "local_evidence_total":57,"candidate_count":63,"full_closure_proven":False,
            "registry_changed":False,"elapsed_s":time.monotonic()-start}

def main():
    payload=inspect();ROOT.mkdir(exist_ok=True)
    dest=ROOT/f"report_{time.time_ns()}.json";digest=c.save(dest,payload)
    v.log("VP05_ABC_BOUNDARY_SCOPE_NOT_CLOSURE",boundary_count=len(payload["boundaries"]),
          contains_202=sum(x["contains_202"] for x in payload["boundaries"]),
          contains_203=sum(x["contains_203"] for x in payload["boundaries"]),
          combined_source_support=len(payload["combined_relation"]["original_source_multipliers"]),
          sector203_artifacts=len(payload["sector203_artifact_inventory"]),
          opaque_M_eliminated=True,physical_mapping_verified=False,local_evidence_total=57,
          sha256=digest,report=dest.name,elapsed_s=payload["elapsed_s"],inputs_unchanged=True,full_closure_proven=False)

if __name__=="__main__":main()
