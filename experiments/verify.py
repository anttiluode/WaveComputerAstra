"""Independent receipt checks and full node replay of selected worst-weight bodies."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from astra import chain as C, physics as P
from .analyze import summarize
from .body import job

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',default='results/confirm.json')
    parser.add_argument('--retrain',action='store_true');args=parser.parse_args()
    path=Path(args.receipt);receipt=json.loads(path.read_text());rows=receipt['rows']
    for f,expected in receipt['hashes'].items():
        assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==expected, f'changed: {f}'
    assert len(rows)==96 and len({(r['seed'],r['world']) for r in rows})==96
    expected=json.loads(path.with_name(path.stem+'_summary.json').read_text())
    assert summarize(rows)==expected,'summary does not reproduce'
    reports=[]
    for world in ('strong','weak_first','weak_middle'):
        candidates=[r for r in rows if r['world']==world]
        assert sorted(r['seed'] for r in candidates)==list(range(310001,310033))
        row=max(candidates,key=lambda r:np.max(abs(np.asarray(r['weights']))))
        U=C.Units();W=np.asarray(row['weights']);direction=np.r_[1,np.cumprod(row['relation'])]
        for mode in ('routed','certain'):
            r=C.run(U,W,direction,row['times'],observed=(True,False,False,False),mode=mode,gains=row['gains'])
            f=P.vendored_field();read=[];peak_field=peak_velocity=0.
            for writes in r['writes']:
                f.pre_step()
                for site,v in enumerate(writes):f.set_input(f'write_{site}',v)
                f.step();read.append(f.read_values.copy())
                peak_field=max(peak_field,float(np.max(abs(f.field))))
                peak_velocity=max(peak_velocity,float(np.max(abs(f.vel))))
            relative=float(np.max(abs(np.asarray(read)-r['wave']))/max(np.max(abs(r['wave'])),1e-9))
            assert relative<1e-5,(world,mode,relative)
            assert max(peak_field,peak_velocity)<3.9,'clipping regime reached'
            reports.append(dict(world=world,seed=row['seed'],mode=mode,max_relative_error=relative,
                                peak_grid_field=peak_field,peak_grid_velocity=peak_velocity))
    if args.retrain:
        original=rows[0];fresh=job((original['seed'],original['world']))
        assert fresh==original,'fresh training differs from stored body'
    print(json.dumps(dict(hashes_match=True,summary_reproduces=True,complete_cohort=True,
                          fresh_training_identical=args.retrain,field_replays=reports),indent=2))

if __name__=='__main__':main()
