from src.models import Config, Pending
from src.part2_packet import serve_packet
from collections import deque

def test_header():
    cfg = Config(users=4, ticks=10, slot_bits=128, tick_ms=1, header_bits=32, buffer_payload_bits=4096)
    p = Pending(user=0, arrival_tick=0, payload_bits=96, remaining_wire_bits=128)
    q = deque([p])
    wire, comp = serve_packet(q, 0, cfg)
    assert wire == 128
    assert len(comp) == 1