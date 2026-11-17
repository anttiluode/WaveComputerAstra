# WaveComputerAstra

A four-event wave computer that separates **what is predicted, how strongly,
when to relay it, and which branch wrote it**.

Antti Luode's wave-computer research · implementation and experiments by OpenAI
Codex/Astra · 17 November 2026. Built on the verified wave physics and node banks
from [WaveComputer](https://github.com/anttiluode/WaveComputer).

The experiment asks whether A → imagined B → imagined C → D preserves each
body's learned uncertainty. It compares six relay designs, cuts both intermediate
links, tests contradictory real evidence, and checks every body's error. The
addressed version explicitly needs event slots and writer channels. It does not
discover those for itself.

**Confirmation results pending.** The protocol and executable success rules are
published first. Development already shows that a median amplitude near the
right answer can conceal large relay errors, and faithful relay alone does not
repair weak learning.

[Protocol](PROTOCOL.md) · [engine](astra/chain.py) · [experiment](experiments/body.py)
· [analysis](experiments/analyze.py) · [provenance](SOURCES.md)

## Run locally

Python 3.10+; CPU only. From the repository directory:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m experiments.run --cohort smoke --workers 2
```

The core runtime uses NumPy only. OpenCV is for checking the vendored nodes and
rebuilding the wave kernel. A smoke run trains three bodies. The complete fixed
cohort is `python -m experiments.run --cohort confirm --workers 2`.
Existing receipts are never overwritten; use `--output results/new_run.json`.

## Design

Each adjacent link has positive and negative fade-clock banks, with branches
that write into the wave field. Branches first learn from shared prediction
minus sensory target at their tips. A second, explicit training-only regression
fits six amplitude gains using local waveform projections.

The main relay uses a supplied event clock and a causal 20-tick signed template
projection. The pulse's magnitude carries the measured conditional mean. Its
input is the preceding branch's addressed wave component; its output remains
a physical impulse response, not a scalar multiplier substituted for a field.
An independent scalar composition is used only as an audit reference.

Mixed-field, peak-confidence, constant-confidence, and silent alternatives use
the same fitted weights. The total field is retained alongside addressed output.
This makes the extra routing information visible instead of assuming a local
wave is necessarily the intended message.

The [protocol](PROTOCOL.md) describes supplied information, waveform measurements,
failure criteria, development results, and limits. This is a research prototype;
it does not establish that wave computation beats a conventional predictor.
