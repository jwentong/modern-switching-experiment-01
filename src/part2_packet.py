from collections import deque
from .models import Pending

def serve_packet(queues, tick, cfg):
    wire_bits = 0
    completed_records = []
    budget = cfg.slot_bits

    # 兼容两种输入：
    # 1. 单元测试：queues是deque（报文队列）
    # 2. 集成仿真：queues是list[deque]，取索引0作为全局FIFO
    if isinstance(queues, deque):
        q = queues
    else:
        # queues是列表，取第0个队列作为包交换的全局FIFO
        if len(queues) == 0:
            return (wire_bits, completed_records)
        q = queues[0]

    while budget > 0 and q:
        pkt = q[0]
        send_amt = min(budget, pkt.remaining_wire_bits)
        pkt.remaining_wire_bits -= send_amt
        wire_bits += send_amt
        budget -= send_amt

        if pkt.remaining_wire_bits == 0:
            finished = q.popleft()
            completed_records.append(finished)

    return (wire_bits, completed_records)
