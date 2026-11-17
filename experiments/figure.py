"""Plot every confirmation body; use fixed deterministic visual jitter only."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt']='WaveComputerAstra'
import matplotlib.pyplot as plt
from .body import WORLDS

ROOT=Path(__file__).resolve().parents[1]


def main():
    rows=json.loads((ROOT/'results/confirm.json').read_text())['rows']
    fig,axes=plt.subplots(1,3,figsize=(15,4.8),layout='constrained')
    colors=['#8b97a6','#138b83','#cf8033'];labels=['Raw wave learning','With gain fit','Scalar baseline']
    rng=np.random.default_rng(0)
    for j,(world,q) in enumerate(WORLDS.items()):
        rr=[r for r in rows if r['world']==world]
        series=[[r['raw_routed_D'] for r in rr],
                [r['modes']['routed']['imagine']['beta'][2] for r in rr],
                [r['sample_chain'] for r in rr]]
        for k,values in enumerate(series):
            x=j+(k-1)*.22
            axes[0].scatter(x+rng.uniform(-.045,.045,len(rr)),values,s=12,color=colors[k],alpha=.65,
                            label=labels[k] if j==0 else None)
            axes[0].plot([x-.07,x+.07],[np.median(values)]*2,color=colors[k],lw=3)
        target=float(np.prod(2*np.array(q)-1))
        axes[0].plot([j-.36,j+.36],[target]*2,color='black',linestyle='--',lw=1.2,label='Exact mean' if j==0 else None)
    axes[0].set(xticks=range(3),xticklabels=['Strong','Weak first','Weak middle'],ylabel='Predicted D mean',title='Learning accuracy')
    axes[0].legend(fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.12),ncol=2)
    for j,mode in enumerate(('peak','matched','clocked','routed')):
        errors=[max(1e-12,abs(r['modes'][mode]['imagine']['beta'][2]-r['own_chain'])/max(abs(r['own_chain']),.01)) for r in rows]
        axes[1].scatter(j+rng.uniform(-.17,.17,len(rows)),errors,s=10,alpha=.6,color='#138b83' if mode=='routed' else '#8064a2')
    axes[1].axhline(.03,color='black',ls='--',lw=1.2,label='3% threshold')
    axes[1].set(yscale='log',xticks=range(4),xticklabels=['Peak','Matched','Clocked','Addressed'],
                ylabel='Absolute relative error (floor 10⁻¹²)',title='Relay error: all 96 bodies')
    axes[1].legend(fontsize=8)
    for j,(world,q) in enumerate(WORLDS.items()):
        target=float(np.prod(2*np.array(q)-1));rr=[r for r in rows if r['world']==world]
        values=[np.hypot(r['modes']['routed']['imagine']['beta40'][2]-target,
                          r['modes']['routed']['imagine']['orthogonal'][2]) for r in rr]
        axes[2].scatter(j+rng.uniform(-.16,.16,len(rr)),values,s=15,alpha=.7,color='#138b83')
        axes[2].plot([j-.2,j+.2],[np.median(values)]*2,color='#138b83',lw=3)
    axes[2].axhline(.2,color='black',ls='--',lw=1.2,label='Median success threshold')
    axes[2].set(xticks=range(3),xticklabels=['Strong','Weak first','Weak middle'],
                ylabel='Normalized waveform error, 40 ticks',title='Amplitude is not the whole wave')
    axes[2].legend(fontsize=8)
    for ax in axes:
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.18)
    fig.suptitle('WaveComputerAstra · 32 bodies × 3 matched worlds · registered confirmation cohort',fontsize=13)
    fig.savefig(ROOT/'results/overview.png',dpi=170)
    svg=ROOT/'results/overview.svg'
    fig.savefig(svg,metadata={'Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)

if __name__=='__main__':main()
