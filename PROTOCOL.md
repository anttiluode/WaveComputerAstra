# Four-event wave chain: prospective protocol

17 November 2026. This file, executable analysis, engine, and development receipts
are to be committed publicly **before** running confirmation seeds 310001–310032.
The receipt records that commit and SHA-256 hashes of all defining files.

## Question

Can a learned A → B → C → D wave circuit carry graded predictions through two
unobserved intermediate events? Separate three possible errors: poor learned
link amplitudes, relay timing, and reading another writer's wave as one's input.

This is a deliberately engineered four-event computer, not an autonomous agent.
Event identities, topology, expected times, sensory-presence bits, and (in the
addressed arm) writer identities are supplied. They are not discovered.

## Fixed experiment

- 32 new seeds, 310001 through 310032 inclusive; all eight relation-sign types.
- Three worlds: strong q=(.85,.85,.85), weak_first=(.70,.85,.85), and
  weak_middle=(.85,.70,.85). Binary, symmetric Markov transitions. No observation
  noise in this first experiment. Exact A-only D means are .343, .196, .196,
  after aligning by the three relation signs.
- 240 training episodes per world/body. A is balanced. Each body has three
  nominal delays sampled independently from 39..54 ticks; each event gets ±3
  ticks of training jitter. Training pulse amplitude is uniform .9..1.1.
- All worlds for a seed reuse identical random draws, timings, and amplitudes;
  changing q changes only the relevant sign-flip threshold.
- 320-tick reset episodes. Sites A=0, B=2, C=4, D=7 of the inherited eight-port,
  96×96 wave medium. Three adjacent branch populations, 24 clocks each. No learned
  skip edges. Physical waves can nevertheless reach other apertures.
- First learn branches with the inherited shared-tip residual rule. Then fit one
  scalar gain per edge/sign bank (six coefficients) on the same training episodes:
  minimize squared error of the final branch waveform's local 20-tick projection
  against the observed next pulse. Gains bounded to [-4,4]. This is an explicit
  supervised least-squares calibration, not part of the original node equations.
  No known q, Bayes answer, or probe result is used by either training stage.

## Six inference arms: identical fitted weights

| Arm | Missing source's clock | Magnitude | What it reads |
|---|---|---|---|
| peak | threshold-triggered canonical regeneration | inherited apical peak / sensory peak | mixed field |
| matched | same regeneration | causal local template projection | mixed field |
| clocked | externally supplied expected event slot | causal local template projection | mixed field |
| routed (main) | same supplied slot | same projection | previous branch's addressed component |
| certain | threshold-triggered regeneration | one | mixed field |
| silent | no missing-input clock | zero | no imagined input |

`routed` uses the linear decomposition of writes into three virtual channels.
Their sum is the shared physical field; channel access is extra infrastructure.
Its reported primary output is D's addressed channel. All arms also report the
total field's D projection. The clocked→routed intervention therefore bundles
addressed input **and output** selection. It is not a free decoder for mixtures.
The peak arm generalizes Claude's mechanism to a changed geometry; it is not
a rerun of the original WaveComputer benchmark.

At a missing input, matched amplitudes use samples already observed, starting
at its supplied event time, for up to 20 ticks. Any clock that fires before the
20-sample read completes is counted. No future sample enters a pulse.
Projection magnitudes are clipped to [0,1] separately for each sign bank.

## Probe and reference measurements

Probe both signs of A, amplitude one, at each body's nominal times. Cases:
A-only imagination; outgoing B cut; outgoing C cut; B seen agreeing; B seen
contradicting; B and C seen agreeing; and C seen contradicting. D is always
withheld during probes. Inference does not update weights.

Primary amplitude: signed projection at the relevant local aperture over 20
ticks, normalized by a unit sensory waveform. Secondary measurements: 40-tick
projection and orthogonal waveform residual. Full 40-tick normalized waveform
error against the Bayes-mean waveform is sqrt((beta40−Bayes)^2+orthogonal^2).
This assesses one aperture, not reconstruction of the entire 96×96 field.

Isolate each learned link and measure its positive and negative transfers.
Compose these six measured coefficients in a separate scalar reference, with
the same magnitude clipping. It is never fed to the circuit. Report absolute
and relative discrepancies for **every body**, plus min/p10/median/p90/max;
relative error denominator is max(abs(reference),.01). A median ratio near one
does not count as individual fidelity.

Also report the raw (before gain fit) routed output and an ordinary scalar
Markov baseline: product of the three empirical training correlations. This
is a baseline, not an additional physical wave computation.

## Fixed success rules

Evaluate G1–G9 separately in **each** world; no pooling to mask failures.

1. G1: routed D has the correct sign in at least 28/32 bodies.
2. G2: **every** body's routed amplitude is within 3% of its own measured-link
   reference (denominator floor .01).
3. G3: median absolute error to Bayes ≤.10, and at least 24/32 bodies within .15.
4. G4: both B and C cuts independently remove at least 80% of D's magnitude
   in at least 28/32 bodies (intact denominator floor .01).
5. G5: contradictory seen B, and contradictory seen C, reverse D in at least
   28/32 bodies each.
6. G6: median normalized 40-tick full waveform error ≤.20.
7. G7: no incomplete 20-tick reads in routed A-only probes.
8. G8: addressed input/output selection improves absolute error to the own-link
   reference over clocked mixed-field inference in at least 24/32 paired bodies;
   require improvement >1e-10, so numerical ties do not win.
9. G9: gain fitting improves absolute Bayes error over raw routed inference in
   at least 24/32 bodies.

G10, separately for weakened first and middle links: the median paired
weak/strong routed D ratio must be within .15 of 4/7, and routed must be closer
to 4/7 than `certain` in at least 24/32 pairs. Ratio denominator is
max(abs(strong output),.01), retaining the weak output's sign.

The machine is fully successful only if all these rules hold. We will publish
failed rules and the ordinary scalar baseline even if they undercut the design.

## Development and limits

Development used seeds 101–106, never confirmation seeds. The first shared-field
prototype had severe composition errors. Addressed clocked transfer removed
those errors on development bodies, as expected from linearity. This is an
engineering construction to be verified, **not a new mathematical discovery**.
Six final development bodies (101–102, three worlds) exercised gain fitting.
Early and final development receipts are retained; thresholds are substantive
targets, not assurances that the preliminary bodies pass them.

The body does not infer sources, learn its clock schedule or routing, grow
structure, operate continuously, carry general probability distributions,
solve variable-quality evidence, or establish computational advantage over
ordinary regression. Confidence here means a signed binary conditional mean.
An exactly transported learned error remains an error. No claim of consciousness
or biological validation is tested. The inherited impulse kernel represents
the unclipped linear regime over a finite horizon, not arbitrary nonlinear runs.
