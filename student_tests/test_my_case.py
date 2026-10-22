"""Observation-window boundary: an unfinished packet remains payload backlog.

Input: one user, one tick, 128 wire bits per tick, a 32-bit header, and one
128-bit payload arriving at tick 0. The packet needs 160 wire bits, so the
only tick sends 128 bits and leaves 32 wire bits outstanding. At the window
end, no record is complete: delivered=0, backlog=128 payload bits,
wire_sent=128, dropped=0, and both delay metrics have no sample.
"""
from src.metrics import summarize
from src.models import Arrival, Config
from src.utils import simulate


def test_packet_pending_at_observation_window_end():
    config = Config(users=1, ticks=1, slot_bits=128, header_bits=32)
    arrivals = [Arrival(tick=0, user=0, payload_bits=128)]

    raw = simulate(arrivals, config, mode='packet')
    metrics = summarize(raw, config)

    assert raw['wire_sent_bits'] == 128
    assert raw['delivered_payload_bits'] == 0
    assert raw['dropped_payload_bits'] == 0
    assert raw['backlog_payload_bits'] == 128
    assert metrics['payload_utilization'] == 0
    assert metrics['wire_utilization'] == 1
    assert metrics['mean_delay_ms'] is None
    assert metrics['max_delay_ms'] is None
    assert metrics['loss_ratio'] == 0