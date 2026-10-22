"""Verify proposed low-degree bivariate VP05 sector202 coefficients against saved samples.

25 cross-grid samples are a provenance-preserving transcription of the user's
2026-10-22 log. The six other-prime tests are out of cross-grid holdouts.
This does NOT prove exact original-IBP symbolic identity.
"""
from __future__ import annotations
import json
from fractions import Fraction
from examples.three_loop_vp05_sector202_axis_rational_fit import DATA as AXIS

CROSS=[[11,5,969708,181826,727299,386406],[13,5,666678,8,151546,840965],[19,5,757591,454557,333388,750102],[23,5,151531,90921,545529,477413],[29,5,242444,545470,107,750212],[11,9,811604,652183,246401,483743],[13,9,28994,130443,971047,744628],[19,9,681173,565229,14545,440336],[23,9,115956,521752,768189,831690],[29,9,768135,956538,985614,310038],[11,11,471273,275870,848302,796601],[13,11,390814,448285,78191,589719],[19,11,149437,965530,643733,120811],[23,11,988522,310357,917316,934657],[29,11,747145,827602,172520,845094],[11,13,419056,828581,415898,973860],[13,13,771439,457152,828604,592922],[19,13,828585,342868,561960,792983],[23,13,533348,600013,130232,545415],[29,13,590494,485729,101695,602653],[11,17,354618,191497,904282,575848],[13,17,581570,234051,726983,480119],[19,17,262423,361713,982327,278053],[23,17,716327,446821,308586,714278],[29,17,397180,574483,32025,225013]]
HOLDOUT=[
(17,7,980406,58833,928151,715780,1000003),
(19,11,977055,620720,747204,327718,1000033),
(23,13,466697,400026,203255,454954,1000037),
(29,17,482304,340452,74581,358005,1000039),
(31,19,811403,339664,18994,66362,1000081),
(37,23,128237,461600,133519,900543,1000099),
]
def functions(z,d):
 return [
  Fraction(4*(d*z+4*d-8),3*(3*d-4)),
  Fraction(d*z+10*d-z-14,3*d-4),
  Fraction(d*d*z*z+8*d*d*z+16*d*d-5*d*z*z-8*d*z-16*d+12*z*z-32*z,3*(d-1)*(3*d-4)),
  Fraction(d*d*z*z+2*d*d*z+10*d*d-4*d*z*z+2*d*z-22*d+4*z*z-8*z+12,(d-1)*(3*d-4)),
 ]
def main():
 groups={"cross_grid":(CROSS,1000003),"axis_grid":(AXIS,1000003)}
 results=[]
 for name,(rows,p) in groups.items():
  bad=[]
  for z,d,*vals in rows:
   for i,(f,v) in enumerate(zip(functions(z,d),vals)):
    if f.numerator%p*pow(f.denominator%p,-1,p)%p!=v:
     bad.append([z,d,i])
  results.append({"source":name,"points":len(rows),"mismatches":bad[:10],"pass":not bad})
 bad=[]
 for z,d,*tail in HOLDOUT:
  vals=tail[:4];p=tail[4]
  for i,(f,v) in enumerate(zip(functions(z,d),vals)):
   if f.numerator%p*pow(f.denominator%p,-1,p)%p!=v:bad.append([z,d,p,i])
 results.append({"source":"separate_prime_holdouts","points":len(HOLDOUT),"mismatches":bad,"pass":not bad})
 output={"status":"FINITE_FIELD_BIVARIATE_CANDIDATES_VERIFIED" if all(r["pass"] for r in results) else "MISMATCH",
  "candidate_formulas":["4*(d*z+4*d-8)/(3*(3*d-4))",
   "(d*z+10*d-z-14)/(3*d-4)",
   "(d*d*z*z+8*d*d*z+16*d*d-5*d*z*z-8*d*z-16*d+12*z*z-32*z)/(3*(d-1)*(3*d-4))",
   "(d*d*z*z+2*d*d*z+10*d*d-4*d*z*z+2*d*z-22*d+4*z*z-8*z+12)/((d-1)*(3*d-4))"],
  "checks":results,"exact_symbolic_proof":False,"kira_executed":False,"files_modified":False,
  "note":"Reconstructed from modular samples. Need exact original-row IBP coefficient certificate; finite evaluations cannot prove rational-function identity."}
 print("VP05_SECTOR202_BIVARIATE_CANDIDATE "+json.dumps(output,ensure_ascii=True),flush=True)
 if not all(r["pass"] for r in results):raise SystemExit(2)
if __name__=="__main__":main()
