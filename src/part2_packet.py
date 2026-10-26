"""任务2：补全共享FIFO分组交换发送。"""
def serve_packet(queue, tick, cfg):
    """queue为共享deque[Pending]，原地更新。
    remaining_wire_bits已由框架初始化为payload_bits+header_bits，不再重复加包头。
    每tick发送不超过slot_bits；必须发完队首再处理下一项。
    分组允许跨tick续传，但不得与其他分组交错，不能因大于一个时隙就丢弃。
    返回(线速发送比特数,完整发送的Pending列表)；空队列返回(0,[])。
    """
    # 1. 如果共享队列为空，直接返回
    if not queue:
        return 0, []
        
    wire_bits_sent = 0
    completed_records = []
    budget = cfg.slot_bits
    
    # 2. 只要队列有数据且预算没花完，就一直发
    while queue and budget > 0:
        record = queue[0]  # 看队首
        
        # 3. 决定发多少（remaining_wire_bits已经包含了包头，千万别手动加头了！）
        bits_to_send = min(record.remaining_wire_bits, budget)
        
        record.remaining_wire_bits -= bits_to_send
        budget -= bits_to_send
        wire_bits_sent += bits_to_send
        
        # 4. 如果发完了，弹出队列，加入完成列表
        if record.remaining_wire_bits == 0:
            queue.popleft()
            completed_records.append(record)
            
    return wire_bits_sent, completed_records
