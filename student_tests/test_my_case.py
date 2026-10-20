"""Self-designed boundary cases with hand-calculated expectations."""

from collections import deque

from src.models import Config, Pending
from src.part1_circuit import serve_circuit
from src.part2_packet import serve_packet


def test_circuit_fills_same_user_but_never_borrows_other_slot():
    # users=2, slot_bits=100.
    # tick 0 belongs to user 0: send 60 from A, then 40 from B (B has 20 left).
    # user 1 must stay untouched even though user 0 has no more budget.
    a = Pending(0, 0, 60, 60)
    b = Pending(0, 0, 60, 60)
    other = Pending(1, 0, 40, 40)
    queues = [deque([a, b]), deque([other])]

    wire, done = serve_circuit(queues, 0, Config(users=2, slot_bits=100))
    assert wire == 100
    assert done == [a]
    assert b.remaining_wire_bits == 20
    assert other.remaining_wire_bits == 40
    assert len(queues[1]) == 1

    # tick 1 belongs to user 1: only its 40-bit record is sent.
    wire, done = serve_circuit(queues, 1, Config(users=2, slot_bits=100))
    assert wire == 40
    assert done == [other]
    assert b.remaining_wire_bits == 20


def test_packet_large_record_spans_ticks_then_fifo_drains():
    # A has 150 payload + 32 header = 182 wire bits; B has 20 + 32 = 52.
    # tick 0: send 128 of A only; A keeps 54, B is not touched.
    # tick 1: finish A (54), then send all of B (52); total 106 < 128.
    a = Pending(0, 0, 150, 182)
    b = Pending(1, 0, 20, 52)
    queue = deque([a, b])

    wire, done = serve_packet(queue, 0, Config())
    assert wire == 128
    assert done == []
    assert a.remaining_wire_bits == 54
    assert b.remaining_wire_bits == 52

    wire, done = serve_packet(queue, 1, Config())
    assert wire == 106
    assert done == [a, b]
    assert not queue
