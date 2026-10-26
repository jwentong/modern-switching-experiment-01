"""运行学生实现，生成公平比较结果。未完成TODO时会给出清楚提示。"""
from pathlib import Path
import sys,json,csv
if __package__ in (None,''):sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.models import Config
from src.utils import make_traffic,simulate
from src.metrics import summarize
SCENARIOS=('continuous','staggered_burst','synchronized_burst','light_random')

def run(output=None):
    output=Path(output or Path(__file__).resolve().parents[1]/'results');output.mkdir(parents=True,exist_ok=True)
    cfg=Config();rows=[];traces={}
    for scenario in SCENARIOS:
        arrivals=make_traffic(scenario,cfg)
        for mode in ('circuit','packet'):
            raw=simulate(arrivals,cfg,mode);metrics=summarize(raw,cfg)
            rows.append(dict(scenario=scenario,mode=mode,**metrics))
            traces[f'{scenario}/{mode}']=raw
    (output/'comparison.json').write_text(json.dumps(dict(config=cfg.__dict__,rows=rows,traces=traces),ensure_ascii=False,indent=2),encoding='utf-8')
    with (output/'comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    from src.visualization import plot_results
    plot_results(rows,traces,output)
    print('Generated comparison.json, comparison.csv and 3 figures in '+str(output))
    return rows

if __name__=='__main__':
    try:run()
    except NotImplementedError as e:
        print(str(e)+'。请先完成三个TODO函数。',file=sys.stderr);sys.exit(2)
