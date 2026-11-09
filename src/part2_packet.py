"""任务2：补全共享FIFO分组交换发送。"""
def serve_packet(queue, tick, cfg):
    """queue为共享deque[Pending]，原地更新。
    remaining_wire_bits已由框架初始化为payload_bits+header_bits，不再重复加包头。
    每tick发送不超过slot_bits；必须发完队首再处理下一项。
    分组允许跨tick续传，但不得与其他分组交错，不能因大于一个时隙就丢弃。
    返回(线速发送比特数,完整发送的Pending列表)；空队列返回(0,[])。
    """
    wire_bits = 0
    completed = []
    budget = cfg.slot_bits
    while queue and budget > 0:
        rec = queue[0]
        if rec.remaining_wire_bits <= budget:
            wire_bits += rec.remaining_wire_bits
            budget -= rec.remaining_wire_bits
            rec.remaining_wire_bits = 0
            completed.append(queue.popleft())
        else:
            wire_bits += budget
            rec.remaining_wire_bits -= budget
            budget = 0
    return (wire_bits, completed)
