"""任务1：补全固定时隙电路交换发送。只改本文件内TODO。"""
def serve_circuit(queues, tick, cfg):
    """queues为每用户一个deque[Pending]，原地更新。
    本tick只能服务user=tick % cfg.users，其他用户不能借用其时隙。
    该用户可在slot_bits预算内连续发送多个记录，也可部分发送一个记录。
    返回(本tick实际线速发送比特数, 本tick完整发送的Pending列表)。
    空队列返回(0,[])；记录完全发完才pop并记入完成列表。
    提示：先确定用户，再在该用户队列上按FIFO扣减remaining_wire_bits。
    """
    sent_bits = 0
    completed_records = []
    budget = cfg.slot_bits
    
    # 1. 确定当前 tick 应该服务哪个用户 (0, 1, 2, 或 3)
    current_user = tick % cfg.users
    
    # 2. 获取该用户的专属队列
    current_queue = queues[current_user]
    
    # 3. 如果轮到的人没数据，直接返回 0，别人不能借用
    if not current_queue:
        return 0, []
        
    # 4. 只要队列有数据，并且本 tick 的发送预算还没用完
    while current_queue and budget > 0:
        # 取出队首的记录（先不弹出）
        record = current_queue[0]
        
        # 看看这次能发多少：取"预算"和"这条记录剩余需要发的比特"的较小值
        to_send = min(budget, record.remaining_wire_bits)
        
        # 扣减剩余量、预算，累加已发送量
        record.remaining_wire_bits -= to_send
        budget -= to_send
        sent_bits += to_send
        
        # 如果这条记录彻底发完了，将它从队列弹出，加入完成列表
        if record.remaining_wire_bits == 0:
            completed_records.append(current_queue.popleft())
            
    return sent_bits, completed_records
            
