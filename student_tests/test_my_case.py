from collections import deque
from src.models import Pending, Config
from src.part2_packet import serve_packet

def test_my_case_header_once():
    # 手算预期：payload 96 + header 32 = 128。若重复加头则变为 160。
    record = Pending(user=0, arrival_tick=0, payload_bits=96, remaining_wire_bits=128)
    q = deque([record])
    cfg = Config(users=1, ticks=1, slot_bits=128, tick_ms=1, header_bits=32, buffer_payload_bits=1000)
    
    wire_bits, completed = serve_packet(q, 0, cfg)
    
    # 断言
    assert wire_bits == 128, "错误：应当发送128 bit，不能重复加包头"
    assert len(completed) == 1, "错误：记录应当已经完成并被弹出"