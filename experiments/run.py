"""Run the sealed cohort, or an explicitly separate smoke/development cohort."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
import numpy as np
from .body import job, WORLDS
from .analyze import summarize

ROOT=Path(__file__).resolve().parents[1]
FILES=('PROTOCOL.md','astra/chain.py','astra/nodes.py','astra/physics.py','astra/kernel.npz',
       'experiments/body.py','experiments/analyze.py','experiments/run.py')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cohort',choices=('confirm','dev','smoke'),default='smoke')
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--output',default=None)
    args=parser.parse_args()
    seeds=range(310001,310033) if args.cohort=='confirm' else range(101,107) if args.cohort=='dev' else (101,)
    path=Path(args.output or ROOT/'results'/f'{args.cohort}.json')
    if path.exists():raise SystemExit(f'Refusing to overwrite {path}; choose another --output.')
    path.parent.mkdir(parents=True,exist_ok=True)
    hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in FILES}
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    started=time.time(); rows=[]; jobs=[(s,w) for s in seeds for w in WORLDS]
    with ProcessPoolExecutor(args.workers) as pool:
        for r in pool.map(job,jobs):
            rows.append(r)
            print(f'{len(rows)}/{len(jobs)} {r["seed"]} {r["world"]} {time.time()-started:.1f}s',flush=True)
            # Recoverable checkpoint; final file exists only once the batch completes.
            path.with_suffix('.partial.json').write_text(json.dumps(rows,allow_nan=False))
    data=dict(cohort=args.cohort,commit=commit,hashes=hashes,python=platform.python_version(),
              numpy=np.__version__,seconds=time.time()-started,rows=rows)
    path.write_text(json.dumps(data,separators=(',',':'),allow_nan=False)+'\n')
    path.with_suffix('.partial.json').unlink()
    summary=summarize(rows)
    path.with_name(path.stem+'_summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print('All gates pass:',summary['all_gates_pass'])

if __name__=='__main__':main()
