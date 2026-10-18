
from collections import deque

from src.models import Config, Pending
from src.part2_packet import serve_packet


def test_packet_finishes_across_two_ticks():
    # 有效载荷97 bit，加32 bit包头，共129 bit
    packet = Pending(0, 0, 97, 129)
    queue = deque([packet])
    cfg = Config(ticks=2, slot_bits=128, header_bits=32)

    # 第一个时隙只能发送128 bit，不能提前宣布完成
    sent, completed = serve_packet(queue, 0, cfg)
    assert sent == 128
    assert completed == []
    assert packet.remaining_wire_bits == 1
    assert len(queue) == 1

    # 第二个时隙发送剩余1 bit，记录才算完成
    sent, completed = serve_packet(queue, 1, cfg)
    assert sent == 1
    assert completed == [packet]
    assert packet.remaining_wire_bits == 0
    assert len(queue) == 0
