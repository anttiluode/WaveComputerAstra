# Provenance and attribution

The kernel, vectorized node banks, physics adapter, and four upstream node/shim
files were copied from Antti Luode's MIT-licensed
[WaveComputer at 1673cad](https://github.com/anttiluode/WaveComputer/tree/1673cad1186516c4bb49b6402256ce46ef3dc17b).
They were implemented there by Claude, using nodes developed in
PerceptionLabAI / StateShapedPingRecall / QualiaClaude. Their copyright and
source comments are preserved. The original license is the same MIT license
already present in this repository.

Adaptation here: physics cache path changes from `wavecomputer/` to `astra/`.
The copied physics and node modules are infrastructure, not a claim that the
new chain reproduces the original three-event experiment. Tests compare the
fast wave model and vectorized nodes directly with the vendored implementations.

New here: four-event chain, mixed-field and addressed relay comparisons,
clocked matched projection, local training gain fit, matched schedules, bodywise
calibration audit, causal cuts, distributional reporting, and prospective tests.

Conceptual lineage:

- [QualiaClaude](https://github.com/anttiluode/QualiaClaude): residual learning,
  content versus innovation, latched clocks, timing regeneration.
- [QualiaAstra](https://github.com/anttiluode/QualiaAstra): controlled statistical
  references and the need to distinguish contributions in a mixed field.
- [QualeX](https://github.com/anttiluode/QualeX): synthesis of content, residue,
  confidence, and timing requirements.
- [WaveComputer](https://github.com/anttiluode/WaveComputer): fast impulse-response
  engine and confidence-carrying two-form relay.

The distinction between signed information and pulse timing, linear system
superposition, matched filters, and least squares are established methods.
Their integration and failure tests in this project are the contribution here.
