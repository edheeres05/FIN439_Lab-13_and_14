import unittest
import numpy as np
from engine import metrics,review,grid,load_prices,BENCH
class Tests(unittest.TestCase):
    def test_cost_known_answer(self):
        mu=np.array([.08,.04]);cov=np.diag([.04,.01]);w=np.array([.6,.4]);current=np.array([.5,.5])
        g,n,v,t,c=metrics(w,mu,cov,current,10)
        self.assertAlmostEqual(g[0],.064);self.assertAlmostEqual(t[0],.1)
        self.assertAlmostEqual(c[0],.0002);self.assertAlmostEqual(n[0],.0637872)
        self.assertAlmostEqual(v[0],np.sqrt(.016))
    def test_grid(self):
        w=grid();self.assertEqual(len(w),53130);self.assertTrue(np.allclose(w.sum(1),1));self.assertTrue((w>=0).all())
    def test_missing_provenance_date(self):
        with self.assertRaises(ValueError):review(decision_date='2026-10-21')
    def test_infeasible(self):self.assertEqual(review(target=.9)['feasible_grid_count'],0)
    def test_drawdown_boundary(self):self.assertTrue(review(drawdown=.15)['paused'])
    def test_stale_data_blocks_all(self):self.assertTrue(all('Stale data' in r['failed_rules'] for r in review()['rows']))
    def test_bad_weights(self):
        for w in [np.zeros(6),np.full(6,np.nan),np.array([-.1,.1,0,0,0,1])]:
            with self.assertRaises(ValueError):review(current=w)
    def test_turnover_budget(self):
        r=review(prior_turnover=.25)
        for row in r['rows']:
            if row['one_way_turnover']>1e-8:self.assertIn('Rolling turnover',row['failed_rules'])
    def test_snapshot(self):self.assertEqual(load_prices().shape,(60,6))
if __name__=='__main__':unittest.main()
