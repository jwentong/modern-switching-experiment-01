from collections import deque

from src.models import Config, Pending
from src.part2_packet import serve_packet


def test_packet_no_double_header_and_partial_not_completed():
    """
    反例目标：揭示两类常见错误
    1) 函数内又加一次 32 bit 包头；
    2) 部分发送被误记为完成。

    手算：
    payload = 200 bit，header = 32 bit
    框架初始化 remaining_wire_bits = 200 + 32 = 232
    slot_bits = 128

    tick 0：发送 min(128, 232) = 128，剩余 104，未完成，交付 0
    tick 1：发送 min(128, 104) = 104，剩余 0，完成，交付 1
    两 tick 总 wire = 128 + 104 = 232，不是 264

    如果函数内重复加头，总 wire 会变成 264；
    如果部分发送误记完成，tick 0 的 done 会非空；
    如果部分发送改了 payload_bits，断言会失败。
    """
    cfg = Config(
        users=1,
        ticks=2,
        slot_bits=128,
        tick_ms=1,
        header_bits=32,
        buffer_payload_bits=4096,
    )

    rec = Pending(
        user=0,
        arrival_tick=0,
        payload_bits=200,
        remaining_wire_bits=232,
    )
    queue = deque([rec])

    wire0, done0 = serve_packet(queue, 0, cfg)
    assert wire0 == 128, f"tick0 应发 128，实际 {wire0}"
    assert done0 == [], "tick0 不应完成，部分发送不能误记交付"
    assert len(queue) == 1, "未完成记录必须留在队列"
    assert queue[0].remaining_wire_bits == 104, "tick0 后应剩 104"
    assert queue[0].payload_bits == 200, "部分发送不能改 payload_bits"

    wire1, done1 = serve_packet(queue, 1, cfg)
    assert wire1 == 104, f"tick1 应发 104，实际 {wire1}"
    assert len(done1) == 1, "tick1 应完成 1 条"
    assert len(queue) == 0, "完成后队列应为空"

    total_wire = wire0 + wire1
    assert total_wire == 232, f"总 wire 应为 232，实际 {total_wire}；264 说明重复加头"