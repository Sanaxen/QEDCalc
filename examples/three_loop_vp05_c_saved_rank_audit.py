"""Read-only audit of the saved C rank certificate using its fixed minor.

Reparse pinned SYSTEM with exact regular-specialization checks, restrict to
the stored ordered columns, and independently eliminate the fixed square
matrix without selecting new pivots. No full-family retention claim.
"""
import json
from examples import three_loop_vp05_c_exact_rank_certificate as cert
from examples import three_loop_vp05_sector202_a_exact_batch as batch

SHA="1ef90dbda58cff51f1e055c1908f71f422f3c2016e0b17b04a47d09cfffa9f5f"

def fixed_minor(rows, columns, p):
    if len(rows)!=len(columns) or len(set(columns))!=len(columns):
        raise ValueError("Expected a square minor with distinct columns")
    lookup={k:i for i,k in enumerate(columns)}
    basis=[]
    residues=[]
    determinant=1
    for i,row in enumerate(rows):
        cur={lookup[k]:v%p for k,v in row.items() if k in lookup and v%p}
        for j in range(i):
            alpha=cur.pop(j,0)
            if alpha:
                for k,v in basis[j].items():
                    x=(cur.get(k,0)-alpha*v)%p
                    if x:cur[k]=x
                    else:cur.pop(k,None)
        divisor=cur.pop(i,0)
        if not divisor:
            raise RuntimeError("Fixed minor has zero leading pivot")
        residues.append(divisor)
        determinant=determinant*divisor%p
        inv=pow(divisor,-1,p)
        basis.append({k:v*inv%p for k,v in cur.items()})
    return residues,determinant

def audit():
    if batch.sha(cert.OUTPUT)!=SHA:
        raise RuntimeError("Saved C certificate SHA mismatch")
    data=json.loads(cert.OUTPUT.read_text(encoding="utf-8"))
    expected={f"SYSTEM_VP05_full_{k}.gz":v for k,v in cert.PINS.items()}
    fields={"status":"VP05_C_RESTRICTED_EXACT_INDEPENDENCE_CERTIFICATE",
        "point":list(cert.POINT),"system_sha256":expected,"rows":2678,
        "term_count":21836,"C_key":list(cert.C),"opaque_M_key":list(cert.M),
        "C_exponents":list(cert.probe.q.TARGETS[2]),
        "exact_rank_E":2678,"exact_rank_E_M":2679,"exact_rank_E_M_C":2680,
        "regular_specialization_verified":True,
        "C_independent_modulo_M_in_pinned_SYSTEM":True,
        "new_boundary_equivalence_proven":False,"whole_family_63_closure_proven":False}
    if any(data.get(k)!=v for k,v in fields.items()):
        raise RuntimeError("Unexpected C certificate metadata")
    files=sorted((cert.probe.q.P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    if {f.name:batch.sha(f) for f in files}!=expected:
        raise RuntimeError("Pinned SYSTEM mismatch")
    p=cert.POINT[0]
    rows,terms=cert.read_rows(files,cert.evaluator(cert.POINT),p)
    if len(rows)!=2678 or terms!=21836:
        raise RuntimeError("Original equation inventory changed")
    minor=data["minor"]
    columns=[tuple(k) for k in minor["ordered_columns"]]
    residues,det=fixed_minor(rows+[{cert.M:1},{cert.C:1}],columns,p)
    if det!=937916 or det!=minor["determinant_mod_p"] or residues!=minor["pivot_residues"]:
        raise AssertionError("Saved fixed minor replay mismatch")
    if batch.sha(cert.OUTPUT)!=SHA or {f.name:batch.sha(f) for f in files}!=expected:
        raise RuntimeError("Protected input changed")
    return {"status":"VP05_C_SAVED_EXACT_RANK_CERTIFICATE_AUDIT_PASS",
            "certificate_sha256":SHA,"determinant_mod_p":det,
            "pivot_residues_verified":len(residues),"term_count":terms,
            "restricted_C_independence_proven":True,
            "new_boundary_equivalence_proven":False,
            "whole_family_63_closure_proven":False,"files_modified":False}

if __name__=="__main__":
    print("VP05_C_SAVED_CERTIFICATE_AUDIT "+json.dumps(audit()),flush=True)
