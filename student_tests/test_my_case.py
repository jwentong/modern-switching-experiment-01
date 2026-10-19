from src.metrics import summarize
from src.models import Arrival, Config
from src.utils import simulate


def test_packet_finishes_head_then_keeps_window_backlog():
    cfg = Config(users=2, ticks=2, slot_bits=64, tick_ms=0.5, header_bits=16)
    arrivals = [
        Arrival(tick=0, user=1, payload_bits=100),
        Arrival(tick=1, user=0, payload_bits=80),
    ]

    raw = simulate(arrivals, cfg, 'packet')
    metrics = summarize(raw, cfg)

    assert raw['wire_sent_bits'] == 128
    assert raw['delivered_payload_bits'] == 100
    assert raw['dropped_payload_bits'] == 0
    assert raw['backlog_payload_bits'] == 80
    assert raw['completed'] == [
        {'user': 1, 'payload_bits': 100, 'delay_ticks': 2},
    ]
    assert metrics['mean_delay_ms'] == 1.0
    assert metrics['max_delay_ms'] == 1.0
    assert metrics['backlog_payload_bits'] == 80
    assert (
        raw['generated_payload_bits']
        == raw['delivered_payload_bits']
        + raw['dropped_payload_bits']
        + raw['backlog_payload_bits']
    )
