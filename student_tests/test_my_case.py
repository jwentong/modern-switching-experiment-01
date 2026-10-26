import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from collections import deque
from src.models import Pending
from src.part1_circuit import serve_circuit

class MockCfg:
    def __init__(self, slot_bits, users):
        self.slot_bits = slot_bits
        self.users = users

def test_circuit_large_packet_partial_send():
    cfg = MockCfg(slot_bits=100, users=4)
    queues = [deque() for _ in range(4)]
    big_pkt = Pending(
        user = 0,
        arrival_tick = 0,
        payload_bits = 300,
        remaining_wire_bits = 300
    )
    queues[0].append(big_pkt)

    tick = 0   
    total_sent, completed = serve_circuit(queues, tick, cfg)

    assert total_sent == 100
    assert len(completed) == 0, "部分发送的包不能加入completed！"
    assert queues[0][0].remaining_wire_bits == 200