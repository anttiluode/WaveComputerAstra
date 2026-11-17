"""Matched random schedules and causal readouts for the four-event chain."""
import numpy as np
from astra import chain as C
from astra.physics import kernel, passive, PING_AMP

EPISODES = 240
WORLDS = {"strong":(.85,.85,.85), "weak_first":(.70,.85,.85),
          "weak_middle":(.85,.70,.85)}


def schedule(seed, probabilities, episodes=EPISODES):
    # Draw everything unconditionally, so changing a probability cannot change
    # timings, amplitudes, or another edge's random numbers.
    rng = np.random.default_rng(seed)
    gaps = rng.integers(39,55,size=3)
    a = np.resize([1.,-1.],episodes); rng.shuffle(a)
    flips = rng.random((episodes,3)) < np.asarray(probabilities)
    jitter = rng.integers(-3,4,size=(episodes,4))
    amplitude = rng.uniform(.9,1.1,size=episodes)
    relation = np.array([1 if (seed>>i)&1 else -1 for i in range(3)])
    nominal = np.r_[23,23+np.cumsum(gaps)]
    signs = np.c_[a,a[:,None]*np.cumprod(np.where(flips,1,-1)*relation,axis=1)]
    times = nominal+jitter
    return dict(gaps=gaps,relation=relation,nominal=nominal,signs=signs,
                times=times,amplitude=amplitude)


def fit_gains(U,W,data,spikes):
    """One local scalar least-squares gain per edge and sign bank.

The frozen branch waveform is a feature. Fit its 20-tick local projection to
the actual observed next pulse on TRAINING episodes only. No true q or probe
answer enters. Clocks are teacher-driven, so their recorded firing times are
independent of W; kernel superposition replays final W without rerunning it.
This extra batch calibration is conventional supervised regression, not the
inherited local instantaneous-tip rule. It adjusts amplitude, not shape.
    """
    H=kernel(); xx=np.zeros((3,2)); xy=np.zeros((3,2)); records=[]
    for signs,times,amp,fires in zip(data['signs'],data['times'],data['amplitude'],spikes):
        for p,site in enumerate(C.SITES[1:]):
            t=int(times[p+1]); tpl=passive([(site,t,1.)],C.STEPS)[t:t+C.WINDOW,site]
            y=np.zeros(C.WINDOW)
            for k in np.flatnonzero(U.pop==p):
                for fire in fires[k]:
                    # fire -> branch on next tick -> field on the following tick.
                    ages=np.arange(t,t+C.WINDOW)-fire-2
                    valid=(ages>=0)&(ages<H.shape[1])
                    for s in C.REGIONS[p]:
                        y[valid]+=PING_AMP*W[k,s]*H[s,ages[valid],site]
            prediction=float(y@tpl/(tpl@tpl)); target=float(signs[p+1]*amp)
            bank=0 if signs[p]>0 else 1
            xx[p,bank]+=prediction**2; xy[p,bank]+=prediction*target
            records.append((p,bank,prediction,target))
    gains=np.divide(xy,xx,out=np.zeros_like(xy),where=xx>1e-12)
    # Fixed safety bound on fitted amplitudes, not chosen using probe outcomes.
    gains=np.clip(gains,-4.,4.)
    fitted=W.copy()
    for p in range(3):
        for b,half in enumerate((1,-1)):
            fitted[(U.pop==p)&(U.half==half)]*=gains[p,b]
    before=np.mean([(a-b)**2 for p,h,a,b in records])
    after=np.mean([(gains[p,h]*a-b)**2 for p,h,a,b in records])
    return fitted,dict(gains=gains.tolist(),training_mse_before=float(before),
                        training_mse_after=float(after),max_abs_weight=float(abs(fitted).max()))


def train(seed, world):
    U=C.Units(); data=schedule(seed,WORLDS[world]); W=np.zeros((U.n,8)); spikes=[]
    for signs,times,amp in zip(data['signs'],data['times'],data['amplitude']):
        r=C.run(U,W,signs,times,learn=True,amplitude=amp)
        W=r['weights'];spikes.append(r['fires'])
    fitted,diagnostics=fit_gains(U,W,data,spikes)
    return U,fitted,data,W,diagnostics


def read(U,W,data):
    times=data['nominal']; relation=data['relation']; signs=np.r_[1,np.cumprod(relation)]
    gains=np.ones(3); links=[]; link_banks=[]
    # Each edge measured alone, both signs, without receiving downstream waves.
    # Timing gain is measured locally, never from a desired Bayes answer.
    for p in range(3):
        values=[]; peaks=[]
        for sign in (1,-1):
            ev=np.zeros(4);ev[p]=sign
            r=C.run(U,W,ev,times,cuts=tuple(i for i in range(3) if i!=p))
            values.append(sign*C.measure(r['wave'],p+1,int(times[p+1]),C.WINDOW)['beta'])
            peaks.append(np.max(np.abs(r['wave'][times[p+1]-5:times[p+1]+30,C.SITES[p+1]])))
        links.append(float(np.mean(values)))
        link_banks.append([values[0],-values[1]])
        if p<2:
            gains[p+1]=C.calibration(C.SITES[p+1])[-1]/max(np.mean(peaks),1e-9)
    # Independent scalar replay of each measured signed link. This is an
    # audit reference, never injected into a wave run. Respect input clipping.
    scalar=[]
    for sign in (1,-1):
        x=float(sign)
        for p,banks in enumerate(link_banks):
            x=min(abs(x),1.)*banks[0 if x>=0 else 1]
        scalar.append(sign*signs[-1]*x)
    sample=float(np.prod(np.mean(data['signs'][:,:-1]*data['signs'][:,1:],axis=0))*signs[-1])
    result=dict(links=links,link_banks=link_banks,own_chain=float(np.mean(scalar)),sample_chain=sample,
                gains=gains.tolist(),modes={})
    for mode in ('peak','matched','clocked','routed','certain','silent'):
        cases={}
        for name,observed,ev,cuts in (
            ('imagine',(True,False,False,False),signs,()),
            ('cut_B',(True,False,False,False),signs,(1,)),
            ('cut_C',(True,False,False,False),signs,(2,)),
            ('see_B',(True,True,False,False),signs,()),
            ('contradict_B',(True,True,False,False),signs*np.array([1,-1,1,1]),()),
            ('see_C',(True,True,True,False),signs,()),
            ('contradict_C',(True,True,True,False),signs*np.array([1,1,-1,1]),())):
            probes=[]
            for s in (1,-1):
                r=C.run(U,W,s*ev,times,observed=observed,mode=mode,gains=gains,cuts=cuts)
                output=[r['components'][i-1] if mode=='routed' else r['wave'] for i in (1,2,3)]
                measurements=[C.measure(w,i,int(times[i])) for i,w in zip((1,2,3),output)]
                long=[C.measure(w,i,int(times[i]),40) for i,w in zip((1,2,3),output)]
                probes.append(dict(beta=[s*signs[i+1]*m['beta'] for i,m in enumerate(measurements)],
                    beta40=[s*signs[i+1]*m['beta'] for i,m in enumerate(long)],
                    total_beta=[s*signs[i]*C.measure(r['wave'],i,int(times[i]))['beta'] for i in (1,2,3)],
                    orthogonal=[m['orthogonal'] for m in long],
                    incomplete=r['incomplete_reads'],
                    fired=[sum(bool(r['fires'][k]) for k in np.flatnonzero(U.pop==p)) for p in range(3)]))
            cases[name]={k:np.mean([p[k] for p in probes],axis=0).tolist() for k in probes[0]}
        result['modes'][mode]=cases
    return result


def job(args):
    seed,world=args
    U,W,data,raw,calibration=train(seed,world)
    # A frozen raw-weight comparison, same two signs, addressed transport.
    nominal=data['nominal']; direction=np.r_[1,np.cumprod(data['relation'])]
    raw_values=[]
    for sign in (1,-1):
        r=C.run(U,raw,sign*direction,nominal,observed=(True,False,False,False),mode='routed')
        raw_values.append(sign*direction[-1]*C.measure(r['components'][2],3,int(nominal[3]))['beta'])
    return dict(seed=seed,world=world,relation=data['relation'].tolist(),
        times=data['nominal'].tolist(),weights=W.tolist(),raw_weights=raw.tolist(),
        calibration=calibration,raw_routed_D=float(np.mean(raw_values)),**read(U,W,data))
