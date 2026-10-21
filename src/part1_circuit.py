"""任务1：补全固定时隙电路交换发送。只改本文件内TODO。"""
from collections import deque

def serve_circuit(queues, tick, cfg):
    """queues为每用户一个deque[Pending]，原地更新。
    本tick只能服务user=tick % cfg.users，其他用户不能借用其时隙。
    该用户可在slot_bits预算内连续发送多个记录，也可部分发送一个记录。
    返回(本tick实际线速发送比特数, 本tick完整发送的Pending列表)。
    空队列返回(0,[])；记录完全发完才pop并记入完成列表。
    提示：先确定用户，再在该用户队列上按FIFO扣减remaining_wire_bits。
    """

    sent_bits = 0
    completed = []
    # 电路交换：当前tick分配给 tick % cfg.users 这个用户
    user = tick % cfg.users
    user_queue = queues[user]
    if not user_queue:
        return (sent_bits, completed)

    budget = cfg.slot_bits
    while budget > 0 and user_queue:
        pkt = user_queue[0]
        if pkt.remaining_wire_bits <= budget:
            # 本次可以全部发完
            send = pkt.remaining_wire_bits
            sent_bits += send
            budget -= send
            pkt.remaining_wire_bits = 0
            completed.append(user_queue.popleft())
        else:
            # 只能发一部分，包留在队首，不弹出！
            send = budget
            sent_bits += send
            pkt.remaining_wire_bits -= send
            budget = 0
    return (sent_bits, completed)

