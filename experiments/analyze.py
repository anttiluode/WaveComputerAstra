"""Fixed per-body metrics. Failed gates are findings, not reasons to hide rows."""
import argparse
import json
from pathlib import Path
import numpy as np
from .body import WORLDS

MODES=('peak','matched','clocked','routed','certain','silent')


def distribution(values):
    a=np.asarray(values,float)
    return dict(min=float(np.min(a)),p10=float(np.quantile(a,.1)),median=float(np.median(a)),
                p90=float(np.quantile(a,.9)),max=float(np.max(a)))


def summarize(rows):
    summary={'worlds':{},'gates':{},'n_bodies':len(rows)}
    for world,q in WORLDS.items():
        rr=sorted([r for r in rows if r['world']==world],key=lambda r:r['seed'])
        if not rr: continue
        n=len(rr); bayes=float(np.prod(2*np.array(q)-1)); out={'n':n,'bayes_D':bayes,'modes':{}}
        own=np.array([r['own_chain'] for r in rr])
        for mode in MODES:
            d=np.array([r['modes'][mode]['imagine']['beta'][2] for r in rr])
            d40=np.array([r['modes'][mode]['imagine']['beta40'][2] for r in rr])
            shape=np.array([r['modes'][mode]['imagine']['orthogonal'][2] for r in rr])
            relative=np.abs(d-own)/np.maximum(abs(own),.01)
            cut_b=np.array([r['modes'][mode]['cut_B']['beta'][2] for r in rr])
            cut_c=np.array([r['modes'][mode]['cut_C']['beta'][2] for r in rr])
            rev_b=np.array([r['modes'][mode]['contradict_B']['beta'][2] for r in rr])
            rev_c=np.array([r['modes'][mode]['contradict_C']['beta'][2] for r in rr])
            out['modes'][mode]={
                'D':distribution(d),'bayes_absolute_error':distribution(abs(d-bayes)),
                'own_link_absolute_error':distribution(abs(d-own)),
                'own_link_relative_error':distribution(relative),
                'bodies_within_3pct_own_links':int(np.sum(relative<=.03)),
                'bodies_within_20pct_own_links':int(np.sum(relative<=.20)),
                'correct_sign':int(np.sum(d>0)),
                'within_015_bayes':int(np.sum(abs(d-bayes)<=.15)),
                'both_cuts_remove_80pct':int(np.sum((abs(cut_b)<=.2*np.maximum(abs(d),.01)) &
                                                   (abs(cut_c)<=.2*np.maximum(abs(d),.01)))),
                'B_contradiction_reverses':int(np.sum(rev_b<0)),
                'C_contradiction_reverses':int(np.sum(rev_c<0)),
                'off_template_40':distribution(shape),
                'waveform_error_40':distribution(np.sqrt((d40-bayes)**2+shape**2)),
                'incomplete_reads':float(sum(r['modes'][mode]['imagine']['incomplete'] for r in rr)),
            }
        out['raw_routed_D']=distribution([r['raw_routed_D'] for r in rr])
        out['sample_chain_D']=distribution([r['sample_chain'] for r in rr])
        out['sample_chain_error']=distribution([abs(r['sample_chain']-bayes) for r in rr])
        main=out['modes']['routed']; n28=int(np.ceil(.875*n)); n24=int(np.ceil(.75*n))
        # Thresholds are fixed in PROTOCOL.md before confirmatory seeds run.
        gates={
            'G1_sign':main['correct_sign']>=n28,
            'G2_own_link_fidelity':main['own_link_relative_error']['max']<=.03,
            'G3_bayes_amplitude':main['bayes_absolute_error']['median']<=.10 and main['within_015_bayes']>=n24,
            'G4_causal_cuts':main['both_cuts_remove_80pct']>=n28,
            'G5_contradictory_evidence':min(main['B_contradiction_reverses'],main['C_contradiction_reverses'])>=n28,
            'G6_full_waveform':main['waveform_error_40']['median']<=.20,
            'G7_causal_complete_reads':main['incomplete_reads']==0,
        }
        # Same trained weights; clocked differs from routed only in addressing
        # (including selecting the addressed output). Attribute this as a bundle.
        d_r=np.array([r['modes']['routed']['imagine']['beta'][2] for r in rr])
        d_c=np.array([r['modes']['clocked']['imagine']['beta'][2] for r in rr])
        improved=int(np.sum(abs(d_r-own)+1e-10<abs(d_c-own)))
        out['addressing_improves_fidelity']=improved
        gates['G8_addressing']=improved>=n24
        d_raw=np.array([r['raw_routed_D'] for r in rr])
        out['gain_fit_improves_bayes']=int(np.sum(abs(d_r-bayes)<abs(d_raw-bayes)))
        gates['G9_gain_fit']=out['gain_fit_improves_bayes']>=n24
        summary['worlds'][world]=out;summary['gates'][world]=gates
    if 'strong' in summary['worlds']:
        pairs={}
        for weak in ('weak_first','weak_middle'):
            a={r['seed']:r for r in rows if r['world']=='strong'}
            b={r['seed']:r for r in rows if r['world']==weak}
            seeds=sorted(a.keys()&b.keys()); target=4/7
            if not seeds: continue
            ratios={}
            for mode in ('routed','peak','certain'):
                vals=[b[s]['modes'][mode]['imagine']['beta'][2]/max(abs(a[s]['modes'][mode]['imagine']['beta'][2]),.01)
                      for s in seeds]
                ratios[mode]=np.array(vals)
            wins=int(np.sum(abs(ratios['routed']-target)<abs(ratios['certain']-target)))
            pairs[weak]=dict(target=target,ratios={k:distribution(v) for k,v in ratios.items()},
                            routed_closer_than_certain=wins,
                            passed=bool(abs(np.median(ratios['routed'])-target)<=.15 and wins>=np.ceil(.75*len(seeds))))
        summary['confidence_pairs']=pairs
    summary['all_gates_pass']=bool(all(all(g.values()) for g in summary['gates'].values()) and
                                    all(p['passed'] for p in summary.get('confidence_pairs',{}).values()))
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('receipt');parser.add_argument('--output')
    args=parser.parse_args();data=json.loads(Path(args.receipt).read_text())
    s=summarize(data['rows'] if isinstance(data,dict) else data)
    text=json.dumps(s,indent=2,allow_nan=False)+'\n'
    if args.output:Path(args.output).write_text(text)
    print(json.dumps({'gates':s['gates'],'confidence_pairs':s.get('confidence_pairs'),'all_gates_pass':s['all_gates_pass']},indent=2))

if __name__=='__main__':main()
