r"""参数变化分析（选做）：改变包头长度与缓存容量，观察结论的适用条件。

结果写入 results/extra/，不改变默认基线 results/ 下的 8 组数据。
运行：.\.venv\Scripts\python.exe results/extra/param_sweep.py
"""
from pathlib import Path
import csv
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.models import Config
from src.utils import make_traffic, simulate
from src.metrics import summarize

OUT = Path(__file__).resolve().parent
FIELDS = ['experiment', 'parameter', 'scenario', 'mode', 'payload_utilization',
          'wire_utilization', 'mean_delay_ms', 'max_delay_ms', 'loss_ratio',
          'backlog_payload_bits', 'generated_payload_bits', 'delivered_payload_bits',
          'dropped_payload_bits']


def measure(cfg, scenario, mode):
    raw = simulate(make_traffic(scenario, cfg), cfg, mode)
    return summarize(raw, cfg), raw


def main():
    rows = []
    # 1) 包头长度：电路不使用包头，用于对照分组开销随头长变化的敏感性
    for header in (0, 16, 32, 64):
        cfg = Config(header_bits=header)
        for scenario in ('continuous', 'staggered_burst'):
            for mode in ('circuit', 'packet'):
                metrics, raw = measure(cfg, scenario, mode)
                rows.append(dict(experiment='header_bits', parameter=header,
                                 scenario=scenario, mode=mode, **metrics,
                                 generated_payload_bits=raw['generated_payload_bits'],
                                 delivered_payload_bits=raw['delivered_payload_bits'],
                                 dropped_payload_bits=raw['dropped_payload_bits']))
    # 2) 缓存容量：两模型共用同一准入规则，观察丢弃与积压如何此消彼长
    for buffer_bits in (512, 1024, 2048, 4096, 8192):
        cfg = Config(buffer_payload_bits=buffer_bits)
        for scenario in ('continuous', 'staggered_burst'):
            for mode in ('circuit', 'packet'):
                metrics, raw = measure(cfg, scenario, mode)
                rows.append(dict(experiment='buffer_bits', parameter=buffer_bits,
                                 scenario=scenario, mode=mode, **metrics,
                                 generated_payload_bits=raw['generated_payload_bits'],
                                 delivered_payload_bits=raw['delivered_payload_bits'],
                                 dropped_payload_bits=raw['dropped_payload_bits']))

    with (OUT / 'param_sweep.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f'wrote {len(rows)} rows to {OUT / "param_sweep.csv"}')
    for r in rows:
        if r['experiment'] == 'header_bits':
            print(f"header={r['parameter']:>2} {r['scenario']:<16} {r['mode']:<8} "
                  f"payload={r['payload_utilization']:.4f} wire={r['wire_utilization']:.4f} "
                  f"loss={r['loss_ratio']:.4f} backlog={r['backlog_payload_bits']}")
        else:
            print(f"buffer={r['parameter']:>5} {r['scenario']:<16} {r['mode']:<8} "
                  f"payload={r['payload_utilization']:.4f} loss={r['loss_ratio']:.4f} "
                  f"mean_delay={r['mean_delay_ms']} backlog={r['backlog_payload_bits']}")


if __name__ == '__main__':
    main()
