"""任务1：补全固定时隙电路交换发送。只改本文件内TODO。"""

"""queues为每用户一个deque[Pending]，原地更新。
本tick只能服务user=tick % cfg.users，其他用户不能借用其时隙。
该用户可在slot_bits预算内连续发送多个记录，也可部分发送一个记录。
返回(本tick实际线速发送比特数, 本tick完整发送的Pending列表)。
空队列返回(0,[])；记录完全发完才pop并记入完成列表。
提示：先确定用户，再在该用户队列上按FIFO扣减remaining_wire_bits。
"""
from collections import deque
from src.models import Config, Pending


def serve_circuit(queues: list[deque[Pending]], tick: int, cfg: Config) -> tuple[int, list[Pending]]:
    # 计算当前tick分配给哪个用户
    current_user = tick % cfg.users
    user_queue = queues[current_user]

    budget = cfg.slot_bits   # 本tick带宽预算
    wire_bits = 0            # 本tick实际发出比特
    completed_records = []   # 本tick发送完成的报文

    # 预算还有剩余，并且当前用户队列还有报文
    while budget > 0 and len(user_queue) > 0:
        p = user_queue[0]   # 取队首报文，不弹出

        # 这一轮可以发送多少：取预算 和 剩余待发送比特 的较小值
        send_this_time = min(budget, p.remaining_wire_bits)

        # 更新报文剩余待发送比特
        p.remaining_wire_bits -= send_this_time
        wire_bits += send_this_time
        budget -= send_this_time

        # 判断：这条报文全部发完了
        if p.remaining_wire_bits == 0:
            completed_records.append(p)
            user_queue.popleft()
    return (wire_bits, completed_records)



# raise NotImplementedError('TODO: implement fixed-slot circuit service')
