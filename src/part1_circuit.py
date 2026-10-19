from collections import deque
from .models import Pending

def serve_circuit(queues, tick, cfg):
    """
    FR01 固定时隙电路交换
    queues: list[deque[Pending]]，每个用户独立队列
    当前服务用户 = tick % cfg.users；其他用户不能借用时隙
    支持部分发送、同一用户多条报文连续发送
    返回 (wire_bits, completed_records)
    """
    wire_bits = 0
    completed_records = []
    budget = cfg.slot_bits
    selected_user = tick % cfg.users
    q = queues[selected_user]

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
