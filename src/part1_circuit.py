"""任务1：补全固定时隙电路交换发送。只改本文件内TODO。"""
def serve_circuit(queues, tick, cfg):
    """queues为每用户一个deque[Pending]，原地更新。
    本tick只能服务user=tick % cfg.users，其他用户不能借用其时隙。
    该用户可在slot_bits预算内连续发送多个记录，也可部分发送一个记录。
    返回(本tick实际线速发送比特数, 本tick完整发送的Pending列表)。
    空队列返回(0,[])；记录完全发完才pop并记入完成列表。
    提示：先确定用户，再在该用户队列上按FIFO扣减remaining_wire_bits。
    """
        # 1. 先确定当前享受服务的用户（取余运算）
    current_user = tick % cfg.users
    
    # 2. 获取该用户的专属队列
    q = queues[current_user]
    
    # 3. 根据提示：空队列返回(0, [])，其他用户不能借用时限
    if not q:
        return 0, []
        
    # 初始化变量
    wire_bits_sent = 0
    completed_records = []
    budget = cfg.slot_bits
    
    # 4. 按FIFO扣减remaining_wire_bits，只要队列有数据且预算没花完
    while q and budget > 0:
        record = q[0] # 只查看队首，不弹出
        
        # 决定本次发多少：受限于当前记录的剩余长度 和 剩余预算
        bits_to_send = min(record.remaining_wire_bits, budget)
        
        # 扣减
        record.remaining_wire_bits -= bits_to_send
        budget -= bits_to_send
        wire_bits_sent += bits_to_send
        
        # 5. 记录完全发完才pop并记入完成列表
        if record.remaining_wire_bits == 0:
            q.popleft() # 发完了，从队列移除
            completed_records.append(record)
            
    # 返回实际发送比特数，和完整发送的列表
    return wire_bits_sent, completed_records
