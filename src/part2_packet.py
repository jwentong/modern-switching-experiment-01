"""任务2：补全共享FIFO分组交换发送。"""

"""queue为共享deque[Pending]，原地更新。
remaining_wire_bits已由框架初始化为payload_bits+header_bits，不再重复加包头。
每tick发送不超过slot_bits；必须发完队首再处理下一项。
分组允许跨tick续传，但不得与其他分组交错，不能因大于一个时隙就丢弃。
返回(线速发送比特数,完整发送的Pending列表)；空队列返回(0,[])。
"""

from src.models import Config
def serve_packet(queue, tick, cfg):
    # total_send：记录本tick累计发送的比特总数，初始为0
    total_send = 0
    # completed：保存本tick全部发送完成的分组，初始为空列表
    completed = []
    # budget：本tick剩余可用发送比特额度，上限是cfg.slot_bits
    budget = cfg.slot_bits

    # 循环条件：还有剩余发送额度，并且队列里面还有分组等待发送
    while budget > 0 and len(queue) > 0:
        # 取出队列最前面的分组（队首），FIFO先来先服务
        pkt = queue[0]
        # 本次可以发送的比特数：取【剩余额度】和【这个包还剩下没发的比特】两者里较小的值
        # 两种情况：额度足够一次性发完这个包；额度不够，只能发一部分，剩下留到下一个tick
        send_bits = min(budget, pkt.remaining_wire_bits)

        # 更新这个分组剩余待发送比特，扣掉本次发送的量
        pkt.remaining_wire_bits -= send_bits
        # 累计到本tick总发送比特
        total_send += send_bits
        # 扣减本tick剩余发送额度
        budget -= send_bits

        # 判断：这个分组是否已经全部发送完毕
        if pkt.remaining_wire_bits == 0:
            # 发送完成，加入completed列表
            completed.append(pkt)
            # 从队列头部移除这个已经发完的分组
            queue.popleft()

    # 循环结束：额度用完 / 队列空了。返回本tick发送比特，以及完成的分组列表
    return (total_send, completed)

    #raise NotImplementedError('TODO: implement shared FIFO packet service')
