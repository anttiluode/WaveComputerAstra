# The relay is faithful. The prediction is still biased.

The four-event machine carries A → imagined B → imagined C → D through real
wave responses. The addressed, explicitly clocked version preserves each
body's own learned transfers in all 96 confirmation bodies. It does **not**
learn the right answer accurately enough in the strong-link world, and a
simple scalar predictor remains better.

This distinction is the main result. We can now identify a relay that is
faithful without using that fact to excuse inaccurate learning.

## What was built

The inherited impulse-response wave engine and fade/branch node equations are
retained. The geometry changes to four events at apertures 0, 2, 4, 7. There
are only adjacent branch populations, AB, BC, CD, each with 24 clocks. Input
events are separately sensed; the prediction medium sums their learned writes.

The main relay measures a signed amplitude against a local sensory-wave
template using only samples already available. An expected event slot clocks
the pulse; its amplitude carries the measured value. Since ordinary mixtures
contain waves from other writers, an addressed relay reads the previous
branch's contribution and exposes D's contribution as output. Three virtual
wave fields implement that linear decomposition. Their sum matches the total
physical field. A reader with only an unlabelled sensor is **not** given this
ability by physics alone.

Learning has two stages. The original shared-tip residual rule learns branch
weights. A conventional, local, training-only least-squares gain fit then adjusts
six sign-bank amplitudes against observed next-event pulses. It uses no known
world reliability or probe answers. This extra supervised stage is explicitly
part of the design; it is not presented as the original node learning alone.

## The confirmation cohort

[Registration commit](https://github.com/anttiluode/WaveComputerAstra/commit/ee928ed40d8c0668df7fc91b99d33a2af03343fc)
was public before seeds 310001–310032 ran. Each seed has strong, weak-first,
and weak-middle worlds, with identical underlying random numbers, amplitudes,
and timings. All eight relation-sign types appear. Each body trains on 240
episodes, then all six inference designs use the same frozen fitted weights.

The cohort took 439.4 seconds. No confirmation body or threshold was changed
after looking at its result. Raw results, summaries, and earlier development
receipts are included. In total, two registered world-specific conditions fail:
G3 (Bayes amplitude) and G6 (waveform error), both in the strong world.

## Transfer and causality

| Test on addressed design | Strong | Weak first | Weak middle |
|---|---:|---:|---:|
| Correct final sign | 32/32 | 32/32 | 32/32 |
| Within 3% of own measured-link reference | 32/32 | 32/32 | 32/32 |
| Both cuts remove at least 80% of output | 32/32 | 32/32 | 32/32 |
| Contradictory real B reverses D | 32/32 | 32/32 | 32/32 |
| Contradictory real C reverses D | 32/32 | 32/32 | 32/32 |
| Addressing improves transfer vs clocked mixture | 32/32 | 32/32 | 32/32 |

Maximum relative discrepancy from the independently measured signed-link
composition is 9.65e-16. Each link is measured alone for each input sign; the
scalar reference then composes those measured coefficients and the same
amplitude clipping. It is never injected into the wave simulation.

That precision is expected from this construction: fixed clock timing, linear
wave transport, and one well-defined scalar readout. It is an implementation
verification, not evidence of error-free imagination in general.

With identical weights but the mixed field at the input/output, externally
clocked transfer has median relative errors of .213, .247, .423. Peak-based
regeneration gives .344, .447, .998. Addressing removes ambiguity in this
setting, but the intervention includes both input and output selection. We
have not isolated which selection contributes how much.

## Confidence responds, but absolute calibration still misses

Weaken the first transition from .85 to .70 reliability: the correct signed
mean ratio is 4/7=.5714. Routed D falls by a median factor .5702, closer than
the certain-event control in 31/32 paired bodies. Weakening the middle link
gives .5412, closer in 30/32. Both registered tests pass. These are **medians
of paired ratios**, not guarantees about every body's calibration.

| World | Bayes mean | Routed median | Median absolute error | Bodies within .15 |
|---|---:|---:|---:|---:|
| Strong | .343 | .478 | .135 | 17/32 |
| Weak first | .196 | .276 | .080 | 31/32 |
| Weak middle | .196 | .251 | .057 | 29/32 |

The strong world needed median error ≤.10 and at least 24/32 within .15; it
fails both parts. The weaker worlds pass the specified absolute tolerances,
while still showing bias. Gain fitting improves Bayes error over the raw
learner in 30/32, 26/32, and 27/32 bodies. It improves an underpredicting learner
but does not solve calibration. We have not established the exact source of
the remaining bias; training-time jitter versus nominal-time probing and the
restricted waveform/gain model are candidates, not demonstrated explanations.

The ordinary scalar Markov baseline, trained on exactly the same signs, has
median absolute errors .023, .030, .029. The wave circuit has no demonstrated
prediction-accuracy advantage here.

## The full waveform check matters

The relay reads 20 ticks, while a separate test checks amplitude and off-template
shape over 40 ticks at D's aperture. The median normalized waveform errors are
.274, .160, .137. The strong world fails the .20 criterion. Reporting only a
correct sign or a template coefficient would conceal that failure.

The measurement is still a local aperture trace, not reconstruction of the full
96×96 field. The current machine carries a task-defined scalar through waves;
it does not preserve arbitrary waveform information.

## Independent implementation checks

- Eight automated tests pass: direct node equivalence, grid/kernel agreement,
  schedule matching, causal prefixes, no spontaneous messages, relay cuts,
  component summation, and spike-to-wave replay timing.
- All frozen experiment hashes match; the full summary recomputes exactly.
- One complete confirmation body retrains bit-identically.
- For each world, the body with the largest fitted weight is replayed through
  the original grid node in addressed and certain modes. All six wave readouts
  agree within 2.65e-7 relative error. Maximum grid displacement in these
  checks is .875, safely below the ±4 clipping boundary. This is a selected
  physics check, not a proof that every possible input stays linear.

See [verification.json](results/verification.json) for the numerical record.

## What this leaves us with

A working, inspectable four-event wave relay and a reproducible failure map.
The engineering result is that content magnitude, timing, and writer identity
can be separated so one learned step composes with the next. The system still
receives the clock schedule, source identities, presence bits, and route map.
It is episodic, binary, CPU-simulated, and explicitly engineered.

The next useful improvement is a learner that predicts the waveform and
calibrates on independent timings, while retaining these causal controls.
Adding longer chains first would propagate the present learning bias more
faithfully rather than remove it.
