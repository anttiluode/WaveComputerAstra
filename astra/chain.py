"""A strict four-event chain on the inherited eight-aperture wave field.

Only adjacent branches exist: AB, BC, CD. Source masks and expected event
times are supplied by the experiment, not inferred from the wave. Missing
sources can drive clocks from the shared prediction field. Learning still
uses the shared residual at branch tips, with the inherited local rule.
"""
from functools import lru_cache
import numpy as np
from .physics import Field, passive, N, PING_AMP
from .nodes import FadeClocks, Branches

SITES = (0, 2, 4, 7)
REGIONS = ((1, 2), (3, 4), (6, 7))
STEPS = 320
RULE = dict(learning_rate=.03, listen_from=3, listen_to=5,
            self_response=.71, max_weight=2., sign=1.)
WINDOW = 20


@lru_cache(None)
def calibration(site):
    """Label-blind clocks: decay bank and thresholds from a unit sensory wave.

Same decay range as the inherited clocks, 12 latched release times roughly
24..78 ticks. No training outcomes or held-out bodies enter calibration.
    """
    decay = np.linspace(.892, .9731, 12)
    wave = passive([(site, 0, 1.)], 160)[:, site]
    trace = np.zeros(12); peak = np.zeros(12)
    for x in wave:
        trace = decay * trace + (1-decay)*max(0., x)
        peak = np.maximum(peak, trace)
    pk = np.max(np.abs(wave))
    cross = np.flatnonzero(np.abs(wave) >= .5*pk)[0]
    return decay, peak, wave, int(cross), float(pk)


class Units:
    def __init__(self):
        self.pop = np.repeat(np.arange(3), 24)
        self.half = np.tile(np.repeat([1., -1.], 12), 3)
        self.decay = np.concatenate([np.tile(calibration(s)[0], 2) for s in SITES[:3]])
        self.peak = np.concatenate([np.tile(calibration(s)[1], 2) for s in SITES[:3]])
        self.mask = np.zeros((72, N), bool)
        for p, region in enumerate(REGIONS):
            self.mask[self.pop == p, region[0]:region[-1]+1] = True
        self.n = len(self.pop)


def run(U, weights, signs, times, observed=(True, True, True, True),
        mode="peak", gains=(1., 1., 1.), learn=False, cuts=(), amplitude=1.):
    """Run one reset episode. modes: peak, matched, clocked, routed, certain, silent.

peak: inherited twoform mechanism, generalized to both missing sources.
matched: same timing, but ping magnitude is the causal signed projection
         onto the local unit sensory waveform over the expected 20-tick slot.
         Read only samples available before the pulse; record incomplete reads.
certain: regenerated timing, magnitude one (overconfidence control).
clocked: explicit expected event slots drive the clocks; causal matched wave
         magnitude drives the pulse. Both sign banks clock, but only the bank
         matching the measured sign sends a nonzero pulse. No timing gain.
routed: clocked, but read the previous branch's wave contribution, not the
        mixture. The writer's address is supplied. Components still sum to
        the same physical field; these are linear virtual channels, not a
        claim that an unlabelled sensor could separate them unaided.
silent: missing evidence does not relay (causal control).

Perception always drives clocks with its own sensory channel. D is a training
target, never an input. An observed zero is silence, not an imagined event.
cuts remove outgoing populations 0=AB,1=BC,2=CD, before wave propagation.
    """
    if mode not in ("peak", "matched", "clocked", "routed", "certain", "silent"):
        raise ValueError(mode)
    times = np.asarray(times, int)
    if len(times) != 4 or np.any(np.diff(times) <= 0) or times[-1]+50 > STEPS:
        raise ValueError("four increasing event times with a 50-tick readout tail required")
    sensory = [passive([(s, int(t), float(a)*amplitude)], STEPS) if seen and a else
               np.zeros((STEPS, N)) for s,t,a,seen in zip(SITES,times,signs,observed)]
    target = np.zeros((STEPS, N))
    for p, region in enumerate(REGIONS):
        target[:, region] = sensory[p+1][:, region]
    clocks = FadeClocks(U.decay, .8*U.peak, .2*U.peak, PING_AMP, STEPS+1)
    br = Branches(weights, **RULE, learn=learn)
    field = Field(STEPS)
    channels = [Field(STEPS) for _ in range(3)] if mode == "routed" else None
    components = np.zeros((3,STEPS,N)) if channels else None
    cutmask = np.isin(U.pop, cuts)
    pred = np.zeros(N); pulse = np.zeros(U.n); branch_out = np.zeros((U.n,N))
    closed = np.zeros(U.n, bool); last = np.zeros(U.n)
    apical = np.zeros(U.n); peaks = np.zeros(U.n)
    crossing = [None]*3; polarity = np.zeros(3)
    numerator = np.zeros(3); denominator = np.zeros(3); nread = np.zeros(3, int)
    templates = [passive([(s,int(t),1.)],STEPS)[:,s] for s,t in zip(SITES[:3],times[:3])]
    waves = np.zeros((STEPS,N)); writes = np.zeros_like(waves)
    sizes = np.full(U.n, np.nan); fires = [[] for _ in range(U.n)]
    incomplete = 0
    for tick in range(STEPS):
        src = np.zeros(U.n); size = np.ones(U.n)
        for p, site in enumerate(SITES[:3]):
            ix = U.pop == p
            if tick == 0:
                continue
            raw = components[p-1,tick-1,site] if channels and p>0 else pred[site]
            apical[ix] = U.decay[ix]*apical[ix] + (1-U.decay[ix])*np.maximum(0., U.half[ix]*raw)
            peaks[ix] = np.maximum(peaks[ix],apical[ix])
            j = tick-1
            if times[p] <= j < times[p]+WINDOW:
                v = templates[p][j]
                numerator[p] += raw*v
                denominator[p] += v*v
                nread[p] += 1
            if observed[p]:
                src[ix] = sensory[p][j,site]
                continue
            if mode == "silent":
                continue
            if mode in ("clocked", "routed"):
                src[ix] = U.half[ix]*templates[p][j]
                strength = numerator[p]/max(denominator[p],1e-15)
                size[ix] = np.clip(U.half[ix]*strength,0.,1.)
                continue
            _,_,canonical,cross,pk = calibration(site)
            scaled = gains[p]*raw
            if crossing[p] is None and abs(scaled) >= .5*pk:
                crossing[p] = tick; polarity[p] = np.sign(scaled)
            if crossing[p] is None:
                src[ix] = scaled
            else:
                k = tick-crossing[p]+cross
                src[ix] = polarity[p]*canonical[k] if k < len(canonical) else 0.
            if mode == "peak":
                size[ix] = np.minimum(1., peaks[ix]/U.peak[ix])
            elif mode == "matched":
                strength = numerator[p]/max(denominator[p],1e-15)
                size[ix] = np.clip(U.half[ix]*strength,0.,1.)
        clocks.amplitude = PING_AMP*size
        x = np.maximum(0.,U.half*src); x[closed] = 0.
        tip = np.where(U.mask, (pred-target[max(0,tick-1)])[None,:],0.)
        wr = np.where(U.mask & ~cutmask[:,None],branch_out,0.).sum(0)
        new_pred = field.step(wr)
        if channels:
            for p, channel in enumerate(channels):
                components[p,tick] = channel.step(np.where(U.mask & ~cutmask[:,None]
                    & (U.pop==p)[:,None],branch_out,0.).sum(0))
        fire = clocks.step(x)
        branch_out = br.step(pulse,tip)
        for k in np.flatnonzero(fire):
            fires[k].append(tick); sizes[k] = size[k]
            if mode in ("matched", "clocked", "routed") and not observed[U.pop[k]] and nread[U.pop[k]] < WINDOW:
                incomplete += 1
        closed = np.where(fire,False,closed | (clocks.armed & (clocks.trace < last)))
        last = clocks.trace.copy(); pred = new_pred.copy(); pulse = clocks.pulse.copy()
        waves[tick] = pred; writes[tick] = wr
    return dict(wave=waves, weights=np.where(U.mask,br.W,0.), sizes=sizes,
                fires=fires, writes=writes, incomplete_reads=incomplete,
                strengths=numerator/np.maximum(denominator,1e-15), crossing=crossing,
                components=components)


def measure(wave, event, onset, window=WINDOW):
    """Local signed template projection PLUS off-template waveform error.

Orthogonal error is relative to a unit sensory waveform, not to a possibly
zero desired mean. Reports both sign/amplitude and shape, not just a score.
    """
    site = SITES[event]
    template = passive([(site,int(onset),1.)],STEPS)[onset:onset+window,site]
    y = wave[onset:onset+window,site]
    norm = float(template @ template)
    beta = float(y @ template / norm)
    orth = float(np.sqrt(np.sum((y-beta*template)**2)/norm))
    return dict(beta=beta, orthogonal=orth)
