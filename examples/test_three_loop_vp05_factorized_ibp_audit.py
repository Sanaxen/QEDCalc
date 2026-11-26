import unittest
from examples import three_loop_vp05_factorized_ibp_audit as m

class AuditTests(unittest.TestCase):
    def test_classification(self):
        ex=list(m.f.scalar(69))
        self.assertEqual(m.classify(tuple(ex),69),"factorized")
        ex[0]=0
        self.assertEqual(m.classify(tuple(ex),69),"scaleless_subset")
        ex[1]=1
        self.assertEqual(m.classify(tuple(ex),69),"unsupported_sector")
    def test_residual(self):
        x=m.f.scalar(69)
        y=list(x);y[0]=2;y=tuple(y)
        self.assertEqual(m.audit_row({x:m.f.D-2,y:-2},69,lambda k:1 if k==x else m.f.D/2-1)["status"],"PASS")
        self.assertEqual(m.audit_row({x:m.f.sp.S.One},69,lambda k:1)["status"],"FAIL")
        z=list(x);z[1]=1
        self.assertEqual(m.audit_row({x:m.f.sp.S.One,tuple(z):1},69,lambda k:1)["status"],"UNSUPPORTED")
    def test_actual_scalar_ibps(self):
        spec=m.old.build_family_spec("VP05_full")
        kernel=m.old.build_kernel(spec.propagators)
        for sec in m.f.SECTORS:
            r=m.f.Reducer(spec.propagators,sec,float("inf"))
            for ij,entries in kernel.items():
                row=m.f.e.m.q.exact_row(m.f.scalar(sec),entries,*ij)
                self.assertEqual(m.audit_row(row,sec,r.reduce)["status"],"PASS")
            r.close()
    def test_begin_seed_resets_budget_not_cache(self):
        class Stub:
            count=2000001
            cache={"existing":1}
            def guard(self):
                if self.count>0:raise RuntimeError("budget not reset")
        r=Stub()
        m.begin_seed(r)
        self.assertEqual(r.count,0)
        self.assertEqual(r.cache,{"existing":1})
    def test_checksum(self):
        self.assertNotEqual(m.checksum({"a":1}),m.checksum({"a":2}))

if __name__=="__main__":unittest.main()
