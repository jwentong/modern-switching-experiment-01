"""任务2: 补全共享FIFO分组交换发送。只改本文件内TODO。"""
def serve_packet(queue, tick, cfg):
    """queue为共享deque[Pending]，原地更新。
    remaining_wire_bits已由框架初始化为payload_bits+header_bits，不再重复加包头。
    每tick发送不超过slot_bits；必须先发完队首再处理下一项。
    分组允许跨tick续传，但不得与其他分组交错，不能因大于一个时隙就丢弃。
    返回(线速发送比特数, 完整发送的Pending列表)；空队列返回(0,[])。
    """
    sent_bits = 0
    completed_records = []
    budget = cfg.slot_bits

    # 只要共享队列有数据，且本 tick 预算没用完，就继续发
    while queue and budget > 0:
        record = queue[0]

        # 比较预算和剩余 wire_bits 取最小值
        to_send = min(budget, record.remaining_wire_bits)

        record.remaining_wire_bits -= to_send
        budget -= to_send
        sent_bits += to_send

        # 如果发完了，移出队列并记录
        if record.remaining_wire_bits == 0:
            completed_records.append(queue.popleft())

    return sent_bits, completed_records