"""任务1：补全固定时隙电路交换发送。只改本文件内TODO。"""
def serve_circuit(queues, tick, cfg):
    """queues为每用户一个deque[Pending]，原地更新。
    本tick只能服务user=tick % cfg.users，其他用户不能借用其时隙。
    该用户可在slot_bits预算内连续发送多个记录，也可部分发送一个记录。
    返回(本tick实际线速发送比特数, 本tick完整发送的Pending列表)。
    空队列返回(0,[])；记录完全发完才pop并记入完成列表。
    提示：先确定用户，再在该用户队列上按FIFO扣减remaining_wire_bits。
    """
    
    # 确定当前时隙应该服务哪个用户
    user = tick % cfg.users
    queue = queues[user]

    # 初始化发送预算、实际发送量和完成列表
    budget = cfg.slot_bits
    sent_bits = 0
    completed = []

    # 只要还有数据，并且发送预算未用完，就继续发送
    while queue and budget > 0:
        pending = queue[0]

        # 本次发送量不能超过预算或剩余数据量
        amount = min(budget, pending.remaining_wire_bits)

        pending.remaining_wire_bits -= amount
        budget -= amount
        sent_bits += amount

        # 只有整条记录发送完成，才能将它移出队列
        if pending.remaining_wire_bits == 0:
            completed.append(queue.popleft())
        else:
            # 当前记录未完成，保留它，等待下一个时隙
            break

    return sent_bits, completed
