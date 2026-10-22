"""任务2：补全共享FIFO分组交换发送。"""
def serve_packet(queue, tick, cfg):
    """queue为共享deque[Pending]，原地更新。
    remaining_wire_bits已由框架初始化为payload_bits+header_bits，不再重复加包头。
    每tick发送不超过slot_bits；必须发完队首再处理下一项。
    分组允许跨tick续传，但不得与其他分组交错，不能因大于一个时隙就丢弃。
    返回(线速发送比特数,完整发送的Pending列表)；空队列返回(0,[])。
    """
    wire_bits = 0
    completed_records = []
    
    # 共享队列，谁在前面发谁
    while wire_bits < cfg.slot_bits and queue:
        record = queue[0]
        remaining_budget = cfg.slot_bits - wire_bits
        
        if record.remaining_wire_bits <= remaining_budget:
            # 额度够，直接发完
            wire_bits += record.remaining_wire_bits
            record.remaining_wire_bits = 0
            completed_records.append(queue.popleft())
        else:
            # 额度不够，发多少扣多少，留在队首
            wire_bits += remaining_budget
            record.remaining_wire_bits -= remaining_budget
            break
            
    return wire_bits, completed_records
