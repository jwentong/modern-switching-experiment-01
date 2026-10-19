"""生成包头/缓存参数变化证据，默认基线结果保持不变。"""
from pathlib import Path
import csv
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.models import Config
from src.utils import make_traffic, simulate
from src.metrics import summarize

SCENARIOS = ('continuous', 'staggered_burst', 'synchronized_burst', 'light_random')
CONFIGS = {
    'baseline': Config(),
    'header16': Config(header_bits=16),
    'header64': Config(header_bits=64),
    'buffer1024': Config(buffer_payload_bits=1024),
}


def main():
    root = ROOT
    output = root / 'results' / 'extra'
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, cfg in CONFIGS.items():
        for scenario in SCENARIOS:
            arrivals = make_traffic(scenario, cfg)
            for mode in ('circuit', 'packet'):
                raw = simulate(arrivals, cfg, mode)
                metrics = summarize(raw, cfg)
                rows.append(dict(
                    config=label,
                    header_bits=cfg.header_bits,
                    buffer_payload_bits=cfg.buffer_payload_bits,
                    scenario=scenario,
                    mode=mode,
                    **metrics,
                ))
    with (output / 'parameter_sweep.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        'configs': {
            label: {
                'users': cfg.users,
                'ticks': cfg.ticks,
                'slot_bits': cfg.slot_bits,
                'tick_ms': cfg.tick_ms,
                'header_bits': cfg.header_bits,
                'buffer_payload_bits': cfg.buffer_payload_bits,
            }
            for label, cfg in CONFIGS.items()
        },
        'rows': rows,
    }
    (output / 'parameter_sweep.json').write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(f'Generated {len(rows)} rows in {output}')


if __name__ == '__main__':
    main()

