import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from examples import three_loop_vp05_final_diagnostic_exact as m

class FinalDiagnosticTests(unittest.TestCase):
    def test_rational_rules(self):
        field,z,d=m.sp.polys.fields.field("z,d",m.sp.QQ)
        x=m.cov.R;y=m.cov.J;k=m.f.a.CAND
        self.assertEqual(m.ce.collapse({x:field.one,y:field.one},{x:{k:z/d},y:{k:-z/d}},field),{})
    def test_points(self):
        self.assertEqual(len(set((*m.old.POINTS,*m.retry.POINTS))),5)
        self.assertTrue(all(m.sp.isprime(pt[0]) for pt in (*m.old.POINTS,*m.retry.POINTS)))
    def test_direct_certificate(self):
        point=m.old.POINTS[1];target=m.cov.R;candidate=m.f.a.CAND
        eng=m.exact.Trace(point[0],{candidate},float("inf"))
        builder=m.retry.DiagnosticExact([],eng,point,float("inf"))
        cert,result=m.retry.make_certificate(builder,[],target,[],[],{target:{candidate:builder.field.one}},[],point)
        self.assertEqual(result,{candidate:builder.field.one})
        self.assertEqual(cert["pivots"],[])

    def test_prior_inventory_without_frontier_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            paths={}
            def make(path,target):
                path.parent.mkdir(parents=True,exist_ok=True)
                m.old.atomic(path,{"target":target})
                return m.n.sha(path)
            proofs=root/"proofs"
            commonroot=root/"common"
            retryroot=root/"retry"
            sec204=[];summary=[]
            # Reverse filename order to ensure no positional assumption.
            for i in range(16):
                target=[204,i]+[0]*10
                sha=make(proofs/f"target{15-i:02d}.json",target)
                sec204.append({"target":target,"certificate_sha256":sha})
                summary.append({"target":target,"sha256":sha})
            jobs=[];commonjobs=[];retryresults=[]
            for sec,count in ((77,3),(71,10),(228,4)):
                targets=[[sec,i]+[0]*10 for i in range(16)]
                commonjobs.append({"sector":sec,"diagnostic_targets":targets})
                results=[]
                for i in range(count):
                    sha=make(commonroot/f"sec{sec}_target{i:02d}.json",targets[i])
                    results.append({"target":targets[i],"certificate_sha256":sha})
                jobs.append({"sector":sec,"results":results})
                if sec==77:
                    for i in range(3,16):
                        sha=make(retryroot/f"target{i:02d}.json",targets[i])
                        retryresults.append({"target":targets[i],"certificate_sha256":sha})
            data={m.retry.SOURCE:{"verified":17,"jobs":jobs},
                  m.s.RETRY:{"results":retryresults,"unresolved":[]},
                  m.c.AUDIT:{"results":sec204},
                  m.c.audit.SOURCE:{"results":summary}}
            read=m.gap.read
            def read_fixture(path):
                if path in data:return data[path]
                return read(path)
            with patch.object(m.c.audit,"PROOFS",proofs), patch.object(m.ce,"ROOT",commonroot), patch.object(m.retry,"ROOT",retryroot), patch.object(m.gap,"read",side_effect=read_fixture):
                pins={}
                done,inventory=m.pin_prior({"jobs":commonjobs},pins)
                self.assertEqual(len(done),46)
                self.assertEqual(len(inventory),46)
                self.assertEqual(len(pins),46)
                # A changed digest must not be accepted.
                sec204[0]["certificate_sha256"]="0"*64
                with self.assertRaisesRegex(RuntimeError,"Sec204 proof summary mismatch"):
                    m.pin_prior({"jobs":commonjobs},{})

if __name__=="__main__":unittest.main()
