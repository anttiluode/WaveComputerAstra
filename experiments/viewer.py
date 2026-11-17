"""Build an offline viewer from recorded measurements. No web dependencies."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

PAGE=r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WaveComputerAstra — the confidence audit</title>
<style>
:root{color-scheme:dark;font:16px/1.5 system-ui,sans-serif;background:#0b121d;color:#e2eaf5}
*{box-sizing:border-box}body{max-width:1180px;margin:0 auto;padding:32px 22px}h1{font-size:clamp(28px,4vw,48px);line-height:1.1;margin:12px 0}h2{font-size:20px;margin:0 0 14px}p{max-width:850px;color:#afbed1}.eyebrow{color:#73d8c6;letter-spacing:.12em;font-size:12px;text-transform:uppercase}.note{padding:13px 16px;border-left:3px solid #e7b572;background:#202332}.controls{display:flex;gap:16px;flex-wrap:wrap;margin:28px 0}label{font-size:13px;color:#afbed1;display:grid;gap:6px}select{padding:10px 12px;background:#152234;color:#e2eaf5;border:1px solid #34465e;border-radius:7px;font:inherit;min-width:140px}.grid{display:grid;grid-template-columns:1.1fr 1fr;gap:20px}.panel{border:1px solid #263950;border-radius:14px;background:#111d2b;padding:22px;margin-bottom:20px}.muted{font-size:13px;color:#94a8c1}.stats{display:flex;gap:30px;flex-wrap:wrap}.stat b{display:block;font-size:26px;color:#73d8c6}.stat span{font-size:12px;color:#afbed1}svg{width:100%;height:auto}.nodes{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:20px 0}.node{padding:14px;background:#182a3c;border-radius:10px;text-align:center}.node b{display:block;font-size:24px;color:#73d8c6}.node span{font-size:12px;color:#afbed1}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:9px 6px;border-bottom:1px solid #293c53;text-align:right}th:first-child,td:first-child{text-align:left}a{color:#73d8c6}button{background:#284965;color:white;border:0;padding:8px 13px;border-radius:6px;cursor:pointer;font:inherit}.pass{color:#73d8c6}.fail{color:#f0ac8f}.footer{font-size:13px;color:#94a8c1;margin:28px 0}code{color:#c4dcfa;font-size:12px;overflow-wrap:anywhere}@media(max-width:760px){.grid{grid-template-columns:1fr}body{padding:22px 14px}.panel{padding:16px}}
</style>
<div class="eyebrow">Antti Luode · WaveComputerAstra · 17 November 2026</div>
<h1>Can a wave carry uncertainty<br>through two imagined steps?</h1>
<p>A → B → C → D. These are recorded results from 96 independently trained bodies. Inspect individual failures as well as the average. The browser does not retrain or simulate the machine.</p>
<div class="note" id="verdict"></div>
<div class="controls">
<label>World<select id="world"><option value="strong">Strong links</option><option value="weak_first">Weaker A → B</option><option value="weak_middle">Weaker B → C</option></select></label>
<label>Relay<select id="mode"><option value="routed">Addressed + clocked</option><option value="clocked">Clocked, mixed field</option><option value="matched">Matched, regenerated</option><option value="peak">Peak, regenerated</option><option value="certain">Certain, regenerated</option><option value="silent">No imagined relay</option></select></label>
<label>Body<select id="seed"></select></label>
<label>Compare amplitude to<select id="reference"><option value="own">Its own learned links</option><option value="bayes">Exact world expectation</option></select></label>
</div>
<div class="grid"><section class="panel"><h2>Every body, not just the median</h2><div id="scatter"></div><p class="muted">Each dot is one body. The diagonal is exact agreement. The highlighted dot is the selected body. Both axes show signed mean amplitude.</p><div class="stats" id="stats"></div></section>
<section class="panel"><h2>Intervene in this body</h2><label>Probe<select id="probe"><option value="imagine">A alone: imagine B and C</option><option value="cut_B">Cut outgoing B</option><option value="cut_C">Cut outgoing C</option><option value="see_B">See agreeing B</option><option value="contradict_B">See contradictory B</option><option value="see_C">See agreeing B and C</option><option value="contradict_C">See contradictory C</option></select></label><div class="nodes" id="nodes"></div><p class="muted">Predicted waves at the three destinations, aligned to the world's relation signs. A negative D after contradictory evidence means the circuit changed its answer.</p><table id="bodytable"></table><p class="muted" id="modeinfo"></p></section></div>
<section class="panel"><h2>What passed, what failed</h2><p class="muted">Fixed rules for the main addressed design, set publicly before the confirmation cohort ran. Changing the relay above does not change these registered rules.</p><div id="gates"></div></section>
<p class="footer">Writer addresses, event identities, expected times, and sensory-presence bits are supplied. Addressed output is one wave component; mixed-field output includes every writer. Good scalar transport is not proof of accurate waveform reconstruction, autonomous source recognition, or an advantage over ordinary regression.<br><a href="https://github.com/anttiluode/WaveComputerAstra">Source &amp; receipts</a> · <a href="https://github.com/anttiluode/WaveComputerAstra/blob/main/PROTOCOL.md">Protocol</a></p>
<script>
const DATA=__DATA__;
const $=id=>document.getElementById(id),fmt=x=>Number(x).toFixed(3);
for(const r of DATA.rows.filter(r=>r.world==='strong'))$('seed').add(new Option(r.seed,r.seed));
const names={G1_sign:'Correct direction',G2_own_link_fidelity:'Every body preserves learned links',G3_bayes_amplitude:'Amplitude agrees with the world',G4_causal_cuts:'Both intermediate links are necessary',G5_contradictory_evidence:'Real evidence reverses the answer',G6_full_waveform:'Wave shape and amplitude',G7_causal_complete_reads:'Complete causal reads',G8_addressing:'Addressing improves transfer',G9_gain_fit:'Gain fit improves learning'};
$('verdict').textContent=DATA.summary.all_gates_pass?'All registered rules passed. Inspect the per-body results below.':'The machine passed some registered tests and failed others. Exact transport and accurate learned predictions are separate questions.';
function update(){
const world=$('world').value,mode=$('mode').value,seed=+$('seed').value,probe=$('probe').value,ref=$('reference').value;
const rows=DATA.rows.filter(r=>r.world===world),row=rows.find(r=>r.seed===seed),s=DATA.summary.worlds[world],m=s.modes[mode],v=row.modes[mode][probe];
const pts=rows.map(r=>({x:ref==='own'?r.own_chain:s.bayes_D,y:r.modes[mode].imagine.beta[2],seed:r.seed}));
let lo=Math.min(0,...pts.flatMap(p=>[p.x,p.y])),hi=Math.max(.5,...pts.flatMap(p=>[p.x,p.y]));let pad=(hi-lo)*.1;lo-=pad;hi+=pad;
const xx=x=>56+(x-lo)/(hi-lo)*360,yy=y=>335-(y-lo)/(hi-lo)*285;
let svg='<svg viewBox="0 0 460 390" role="img" aria-label="Predicted amplitude against reference for all bodies">';
for(let i=0;i<=4;i++){const a=lo+(hi-lo)*i/4;svg+=`<line x1="56" y1="${yy(a)}" x2="416" y2="${yy(a)}" stroke="#263950"/><text x="48" y="${yy(a)+4}" fill="#94a8c1" font-size="10" text-anchor="end">${fmt(a)}</text><text x="${xx(a)}" y="354" fill="#94a8c1" font-size="10" text-anchor="middle">${fmt(a)}</text>`;}
svg+=`<line x1="56" y1="335" x2="416" y2="50" stroke="#94a8c1" stroke-dasharray="5 5"/>`;
for(const p of pts)svg+=`<circle cx="${xx(p.x)}" cy="${yy(p.y)}" r="${p.seed===seed?6:3.5}" fill="${p.seed===seed?'#f2bc79':'#73d8c6'}" opacity=".85"><title>Body ${p.seed}: ${fmt(p.y)} vs ${fmt(p.x)}</title></circle>`;
svg+='<text x="236" y="380" text-anchor="middle" fill="#afbed1" font-size="12">Reference amplitude</text><text x="56" y="24" fill="#afbed1" font-size="12">Wave output</text></svg>';
$('scatter').innerHTML=svg;
const error=ref==='own'?m.own_link_relative_error.median:m.bayes_absolute_error.median;
$('stats').innerHTML=`<div class="stat"><b>${ref==='own'?(100*error).toFixed(2)+'%':fmt(error)}</b><span>Median ${ref==='own'?'relative transfer':'absolute world'} error</span></div><div class="stat"><b>${m.correct_sign}/32</b><span>Correct direction</span></div>`;
$('nodes').innerHTML=v.beta.map((x,i)=>`<div class="node">${'BCD'[i]}<b>${fmt(x)}</b><span>mean amplitude</span></div>`).join('');
$('bodytable').innerHTML=`<tr><th>Measurement</th><th>Value</th></tr><tr><td>Selected D output</td><td>${fmt(v.beta[2])}</td></tr><tr><td>Total mixed-field D</td><td>${fmt(v.total_beta[2])}</td></tr><tr><td>A-only learned-link reference</td><td>${fmt(row.own_chain)}</td></tr><tr><td>A-only exact world expectation</td><td>${fmt(s.bayes_D)}</td></tr><tr><td>A-only ordinary scalar baseline</td><td>${fmt(row.sample_chain)}</td></tr><tr><td>Off-template shape error, 40 ticks</td><td>${fmt(v.orthogonal[2])}</td></tr>`;
$('modeinfo').textContent=mode==='routed'?'Addressed input and output; externally supplied clock. This is extra routing infrastructure.':mode==='clocked'?'Same supplied clock and amplitude reader, but both input and output use the mixed field.':'Regeneration alternatives use the same fitted weights. This is a changed four-event geometry, not a reproduction of Claude’s original benchmark.';
const gates=DATA.summary.gates[world];let html='<table><tr><th>Registered test</th><th>Result</th></tr>';
for(const [k,pass] of Object.entries(gates))html+=`<tr><td>${names[k]}</td><td class="${pass?'pass':'fail'}">${pass?'PASS':'FAIL'}</td></tr>`;
for(const [w,p] of Object.entries(DATA.summary.confidence_pairs))html+=`<tr><td>Confidence responds to ${w.replace('_',' ')}</td><td class="${p.passed?'pass':'fail'}">${p.passed?'PASS':'FAIL'}</td></tr>`;
$('gates').innerHTML=html+'</table>';
}
for(const id of ['world','mode','seed','reference','probe'])$(id).addEventListener('change',update);update();
</script></html>'''


def main():
    data=json.loads((ROOT/'results/confirm.json').read_text())
    rows=[{k:r[k] for k in ('seed','world','modes','own_chain','sample_chain')} for r in data['rows']]
    summary=json.loads((ROOT/'results/confirm_summary.json').read_text())
    payload=json.dumps(dict(rows=rows,summary=summary),separators=(',',':'),allow_nan=False).replace('<','\\u003c')
    (ROOT/'index.html').write_text(PAGE.replace('__DATA__',payload))
    print('Wrote index.html (self-contained; opens offline).')

if __name__=='__main__':main()
