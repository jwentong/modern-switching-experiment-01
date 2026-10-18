"""任务2：补全共享FIFO分组交换发送。"""
def serve_packet(queue, tick, cfg):
    """queue为共享deque[Pending]，原地更新。
    remaining_wire_bits已由框架初始化为payload_bits+header_bits，不再重复加包头。
    每tick发送不超过slot_bits；必须发完队首再处理下一项。
    分组允许跨tick续传，但不得与其他分组交错，不能因大于一个时隙就丢弃。
    返回(线速发送比特数,完整发送的Pending列表)；空队列返回(0,[])。
    """
   
    # 初始化当前时隙的发送预算、实际发送量和完成列表
    budget = cfg.slot_bits
    sent_bits = 0
    completed = []

    # 只要队列中还有分组，并且当前时隙还有发送预算
    while queue and budget > 0:
        # 取出队首分组，遵循 FIFO
        pending = queue[0]

        # 本次发送不能超过预算，也不能超过分组的剩余长度
        amount = min(budget, pending.remaining_wire_bits)

        # 更新分组剩余长度和时隙预算
        pending.remaining_wire_bits -= amount
        budget -= amount
        sent_bits += amount

        # 只有分组完整发送后，才能将它移出队列
        if pending.remaining_wire_bits == 0:
            completed.append(queue.popleft())
        else:
            # 队首分组未完成，不能发送后面的分组
            break

    return sent_bits, completed

