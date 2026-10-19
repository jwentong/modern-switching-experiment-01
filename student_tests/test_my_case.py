from collections import deque

from src.models import Config, Pending
from src.part1_circuit import serve_circuit


def test_circuit_cannot_borrow_other_user_slot():
    # 反例目标：揭示“电路交换错误地把空时隙借给其他用户”的 bug。
    # 手算：2 用户，2 tick，每 tick 128 bit。
    # 只有用户 1 在 tick 0 到达一条 32 bit 记录。
    # tick 0 是用户 0 的时隙，用户 1 不能发 -> wire=0，记录保持 32 bit 未动。
    # tick 1 是用户 1 的时隙，发完 32 bit -> wire=32，记录完成并出队。
    cfg = Config(
        users=2,
        ticks=2,
        slot_bits=128,
        tick_ms=1.0,
        header_bits=32,
        buffer_payload_bits=4096,
    )

    rec = Pending(
        user=1,
        arrival_tick=0,
        payload_bits=32,
        remaining_wire_bits=32,
    )
    queues = [deque(), deque([rec])]

    # tick 0：用户 0 的时隙，用户 1 有数据也不能借
    wire, completed = serve_circuit(queues, 0, cfg)
    assert wire == 0
    assert completed == []
    assert rec.remaining_wire_bits == 32
    assert len(queues[1]) == 1

    # tick 1：用户 1 的时隙，发完 32 bit
    wire, completed = serve_circuit(queues, 1, cfg)
    assert wire == 32
    assert completed == [rec]
    assert len(queues[1]) == 0