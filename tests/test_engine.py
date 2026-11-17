"""Physics/node equivalence, causal isolation, and schedule independence."""
import sys
from pathlib import Path
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'vendor/tests')]
from astra import chain as C, physics as P, nodes as N
from experiments.body import schedule


class EngineTests(unittest.TestCase):
    def test_matched_schedules(self):
        a=schedule(123,(.85,.85,.85)); b=schedule(123,(.70,.85,.85))
        for k in ('gaps','relation','nominal','times','amplitude'):
            np.testing.assert_array_equal(a[k],b[k])
        # Conditional transition randomness for downstream edges is unchanged.
        np.testing.assert_array_equal(a['signs'][:,1]*a['signs'][:,2],b['signs'][:,1]*b['signs'][:,2])
        np.testing.assert_array_equal(a['signs'][:,2]*a['signs'][:,3],b['signs'][:,2]*b['signs'][:,3])

    def test_future_events_do_not_affect_past(self):
        u=C.Units();w=np.random.default_rng(4).normal(0,.05,(u.n,8))*u.mask
        times=(23,66,110,156)
        a=C.run(u,w,(1,1,1,1),times)
        b=C.run(u,w,(1,1,-1,-1),times)
        np.testing.assert_array_equal(a['wave'][:110],b['wave'][:110])
        np.testing.assert_array_equal(a['weights'],w)

    def test_components_sum_to_physical_field(self):
        u=C.Units();w=np.random.default_rng(5).normal(0,.05,(u.n,8))*u.mask
        r=C.run(u,w,(1,-1,1,-1),(23,66,110,156),mode='routed')
        np.testing.assert_allclose(r['components'].sum(0),r['wave'],atol=2e-15,rtol=2e-13)
        plain=C.run(u,w,(1,-1,1,-1),(23,66,110,156),mode='peak')
        np.testing.assert_allclose(plain['wave'],r['wave'],atol=1e-15)

    def test_addressed_cuts_stop_output(self):
        u=C.Units();w=np.zeros((u.n,8))
        for p in range(3):w[u.pop==p]=.06*u.half[u.pop==p,None]*u.mask[u.pop==p]
        for cut in ((0,),(1,),(2,)):
            r=C.run(u,w,(1,0,0,0),(23,66,110,156),observed=(True,False,False,False),mode='routed',cuts=cut)
            np.testing.assert_array_equal(r['components'][2],0.)

    def test_no_evidence_no_message(self):
        u=C.Units();w=np.ones((u.n,8))*.02*u.mask
        r=C.run(u,w,(0,0,0,0),(23,66,110,156),observed=(False,False,False,False),mode='routed')
        np.testing.assert_array_equal(r['wave'],0.)

    def test_projection_replay_equals_live_wave(self):
        # This checks the fire -> write +2 convention used by training gain fit.
        u=C.Units();w=np.random.default_rng(6).normal(0,.05,(u.n,8))*u.mask
        r=C.run(u,w,(1,-1,1,-1),(23,66,110,156),mode='routed')
        H=P.kernel(); replay=np.zeros_like(r['components'])
        for k,fires in enumerate(r['fires']):
            p=u.pop[k]
            for fire in fires:
                start=fire+2; length=C.STEPS-start
                for s in C.REGIONS[p]:replay[p,start:]+=P.PING_AMP*w[k,s]*H[s,:length]
        np.testing.assert_allclose(replay,r['components'],atol=2e-15,rtol=2e-13)

    def test_wavefield_matches_vendored_node(self):
        f=P.vendored_field(); fast=P.Field(240);rng=np.random.default_rng(12)
        writes=rng.normal(0,.05,(240,8))*(rng.random((240,8))<.15)
        a=[];b=[]
        for w in writes:
            f.pre_step()
            for s,v in enumerate(w):f.set_input(f'write_{s}',v)
            f.step();a.append(f.read_values.copy());b.append(fast.step(w).copy())
        a=np.array(a);b=np.array(b)
        error=np.max(abs(a-b))/np.max(abs(a))
        self.assertLess(error,1e-5)

    def test_vector_nodes_match_vendored_nodes(self):
        from host_shim import load
        fade=load(ROOT/'vendor/nodes/fading_history_spike_node.py','FadingHistorySpikeNode')
        branch=load(ROOT/'vendor/nodes/damping_return_node.py','DampingReturnNode')
        rng=np.random.default_rng(11);n=24;T=400
        decay=rng.uniform(.85,.98,n);arm=rng.uniform(.02,.1,n);rel=arm*rng.uniform(.1,.5,n)
        refs=[fade(d,a,r,.24,7) for d,a,r in zip(decay,arm,rel)]
        fast=N.FadeClocks(decay,arm,rel,.24,7)
        W=rng.normal(0,.3,(n,8));grefs=[]
        rule=dict(C.RULE,learning_rate=.05)
        for w in W:
            b=branch()
            for k,v in rule.items():setattr(b,k,v)
            b.weights=w.tolist();b.learn_enabled=1;b._render=lambda *a:None;grefs.append(b)
        for f in refs:f._render=lambda *a:None
        gf=N.Branches(W,**rule,learn=True)
        x=np.zeros((T,n))
        for k in range(n):
            t=int(rng.integers(0,20))
            while t<T:
                x[t:t+3,k]=rng.uniform(.15,.4);t+=int(rng.integers(15,45))
        site=rng.normal(0,.1,(T,n,8));prev=np.zeros(n);pulses=0
        for t in range(T):
            for k,u in enumerate(refs):u.pre_step();u.set_input('signal_in',x[t,k]);u.step()
            fast.step(x[t]);pr=np.array([u.pulse for u in refs]);pulses+=np.count_nonzero(pr)
            np.testing.assert_array_equal(pr,fast.pulse)
            for k,g in enumerate(grefs):
                g.pre_step();g.set_input('pre_spike',prev[k])
                for s in range(8):g.set_input(f'site_{s}',site[t,k,s])
                g.step()
            gf.step(prev,site[t]);np.testing.assert_array_equal([g.weights for g in grefs],gf.W);prev=pr
        self.assertGreater(pulses,100)

if __name__=='__main__':unittest.main()
