"""Replay a stored body through the actual engine and export local wave traces."""
import argparse
import json
from pathlib import Path
import numpy as np
from astra import chain as C
from .body import WORLDS

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=310001)
    parser.add_argument('--world',choices=tuple(WORLDS),default='strong')
    parser.add_argument('--mode',choices=('peak','matched','clocked','routed','certain','silent'),default='routed')
    parser.add_argument('--probe',choices=('imagine','cut_B','cut_C','see_B','contradict_B','see_C','contradict_C'),default='imagine')
    parser.add_argument('--output',default=None)
    args=parser.parse_args()
    rows=json.loads((ROOT/'results/confirm.json').read_text())['rows']
    row=next((r for r in rows if r['seed']==args.seed and r['world']==args.world),None)
    if row is None:raise SystemExit('No such stored body')
    signs=np.r_[1,np.cumprod(row['relation'])];observed=[True,False,False,False];cuts=()
    if args.probe in ('see_B','contradict_B','see_C','contradict_C'):observed[1]=True
    if args.probe in ('see_C','contradict_C'):observed[2]=True
    if args.probe=='contradict_B':signs[1]*=-1
    if args.probe=='contradict_C':signs[2]*=-1
    if args.probe=='cut_B':cuts=(1,)
    if args.probe=='cut_C':cuts=(2,)
    result=C.run(C.Units(),np.asarray(row['weights']),signs,row['times'],observed=observed,
                 mode=args.mode,cuts=cuts,gains=row['gains'])
    wave=result['components'][2] if args.mode=='routed' else result['wave']
    measure=C.measure(wave,3,row['times'][3]);print(json.dumps(measure,indent=2))
    if args.output:
        dest=Path(args.output)
        if dest.exists():raise SystemExit(f'Refusing to overwrite {dest}')
        table=np.c_[np.arange(C.STEPS),wave[:,C.SITES],result['wave'][:,C.SITES]]
        np.savetxt(dest,table,delimiter=',',header='tick,selected_A,selected_B,selected_C,selected_D,total_A,total_B,total_C,total_D',comments='')
        print('Wrote',dest)

if __name__=='__main__':main()
