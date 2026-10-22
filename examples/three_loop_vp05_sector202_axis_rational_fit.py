"""VP05 sector202 17-point axis rational-fit audit from saved user run.

These are finite-field observed values, not exact symbolic IBP coefficients.
Use held-out values for every fitted model and reject nonunique solutions.
"""
from __future__ import annotations
import json
P=1000003
# (z,d,a_C,a_small4,b_C,b_small4) from 2026-10-22 --grid log.
DATA=[
(11,7,921579,235302,281070,656909),
(13,7,941188,176479,294148,617707),
(17,7,980406,58833,928151,715780),
(19,7,12,10,549073,853055),
(23,7,39230,882367,398764,304079),
(29,7,98057,705898,692915,421809),
(31,7,117666,647075,529528,912038),
(37,7,176493,470606,255058,735673),
(41,7,215711,352960,751822,245556),
(17,5,60618,636375,454592,22810),
(17,9,463780,86966,855119,222923),
(17,11,229896,793115,475908,251824),
(17,13,476202,714297,901635,2482),
(17,17,35471,319159,266004,831223),
(17,19,503156,94349,304729,529456),
(17,23,564114,230779,225222,798010),
(17,29,755032,891578,392475,716546),
]
def fit(samples,m,n):
 k=m+n+1;mat=[]
 for x,y in samples:
  mat.append([pow(x,j,P) for j in range(m+1)]+[(-y*pow(x,j,P))%P for j in range(1,n+1)]+[y])
 pivots=[];r=0
 for c in range(k):
  pivot=next((j for j in range(r,len(mat)) if mat[j][c]%P),None)
  if pivot is None:continue
  mat[r],mat[pivot]=mat[pivot],mat[r]
  inv=pow(mat[r][c]%P,-1,P)
  mat[r]=[v*inv%P for v in mat[r]]
  for i in range(len(mat)):
   if i==r or not mat[i][c]:continue
   fac=mat[i][c];mat[i]=[(u-fac*v)%P for u,v in zip(mat[i],mat[r])]
  pivots.append(c);r+=1
 if any(not any(row[:k]) and row[k] for row in mat):return None
 if r!=k:return None
 sol=[0]*k
 for i,c in enumerate(pivots):sol[c]=mat[i][-1]
 def check(x,y):
  numerator=sum(sol[j]*pow(x,j,P) for j in range(m+1))%P
  denominator=(1+sum(sol[m+j]*pow(x,j,P) for j in range(1,n+1)))%P
  return denominator!=0 and numerator==y*denominator%P
 return sol if all(check(x,y) for x,y in samples) else None
def main():
 reports=[]
 for axis in ("z","d"):
  data=[row for row in DATA if (row[1]==7 if axis=="z" else row[0]==17)]
  data.sort(key=lambda r:r[0 if axis=="z" else 1])
  for index,name in enumerate(("A_C","A_small4","B_C","B_small4"),2):
   samples=[(row[0 if axis=="z" else 1],row[index]) for row in data]
   options=[]
   for m in range(4):
    for n in range(4):
     if m+n+1>len(samples)-2:continue
     tr=samples[:m+n+1];test=samples[m+n+1:]
     coeff=fit(tr,m,n)
     if coeff is None:continue
     num=coeff[:m+1];den=[1]+coeff[m+1:]
     if all((sum(num[j]*pow(x,j,P) for j in range(len(num)))-
             y*sum(den[j]*pow(x,j,P) for j in range(len(den))))%P==0
            and sum(den[j]*pow(x,j,P) for j in range(len(den)))%P
            for x,y in test):
      options.append({"numerator_degree_bound":m,"denominator_degree_bound":n,
       "numerator_mod_p":num,"denominator_mod_p":den,
       "training_points":len(tr),"holdout_points":len(test)})
   options.sort(key=lambda x:(x["numerator_degree_bound"]+x["denominator_degree_bound"],
                                  x["denominator_degree_bound"],x["numerator_degree_bound"]))
   reports.append({"axis":axis,"coefficient":name,"data_points":len(samples),
    "best_verified_axis_model":options[0] if options else None})
 print("VP05_SECTOR202_AXIS_RATIONAL_FIT "+json.dumps({
  "status":"FINITE_FIELD_AXIS_FITS_WITH_HOLDOUTS","prime":P,
  "grid_samples":len(DATA),"results":reports,
  "exact_bivariate_coefficient_proof":False,
  "limitations":"Axis-restricted Padé fits using a single prime and independent in-axis holdouts. Cross terms vanish on axes, bivariate coefficients not uniquely determined; exact original-equation replay is required.",
  "kira_executed":False,"files_modified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
