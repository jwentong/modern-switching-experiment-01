

def summarize(raw, cfg):
    """
    任务3：补全指标统计函数
    输入：
        raw: 原始仿真统计结果字典，包含各项比特统计与完成的分组记录
        cfg: 仿真配置对象，包含总ticks数、每个时隙比特、tick对应的毫秒数等参数
    返回：
        指标字典，键名固定不可修改
    规则：
        1. 只使用观察窗口[0,ticks)，不额外追加排空时间；有效载荷仅统计完整交付记录
        2. 需要校验 generated_payload_bits == delivered + dropped + backlog，不相等抛出ValueError
        3. 时延：delay_ticks * cfg.tick_ms；没有完成分组时mean_delay_ms、max_delay_ms返回None，不能填0
        4. loss_ratio：无生成数据时固定为0，避免除零错误
    """
    # 1.从原始raw字典取出预统计的比特量
    # 已经成功交付给上层的有效载荷总比特
    delivered_payload_bits = raw["delivered_payload_bits"]
    # 物理链路上实际发送出去的总比特（payload+包头）
    wire_sent_bits = raw["wire_sent_bits"]
    # 因为队列溢出等原因丢弃的有效载荷比特
    dropped_payload_bits = raw["dropped_payload_bits"]
    # 整个仿真期间一共生成的有效载荷比特总和
    generated_payload_bits = raw["generated_payload_bits"]
    # 当前积压在队列里、还没有发送完成的分组原始payload总和
    backlog_payload_bits = raw["backlog_payload_bits"]
    # completed列表：保存所有完整交付成功的分组记录，每条记录包含payload_bits, delay_ticks, user
    completed = raw["completed"]

    # 2. 数据一致性校验：生成总量 = 交付 + 丢弃 + 队列积压
    # 浮点数比较，用极小阈值判断相等，防止浮点精度误差
    total_check = delivered_payload_bits + dropped_payload_bits + backlog_payload_bits
    if not abs(generated_payload_bits - total_check) < 1e-9:
        raise ValueError("generated != delivered + dropped + backlog")

    # 3. 链路利用率计算
    # 仿真全部时间内链路理论上能够传输的最大比特总数 = 总tick数 × 每个tick时隙比特容量
    total_link_bits = cfg.ticks * cfg.slot_bits
    # 有效载荷利用率：交付的有效载荷 ÷ 链路理论总容量
    payload_utilization = delivered_payload_bits / total_link_bits
    # 线路利用率：物理链路上发出的全部比特（含包头）÷ 链路理论总容量
    wire_utilization = wire_sent_bits / total_link_bits

    # ========== 4. 平均时延、最大时延计算 ==========
    # delay_ticks：分组从产生到交付经历的tick个数；乘以tick_ms转为毫秒
    if len(completed) == 0:
        # 没有任何分组成功交付，时延返回None，不能用0代替（0会误导指标）
        mean_delay_ms = None
        max_delay_ms = None
    else:
        # 遍历所有完成分组，把tick时延转为毫秒
        delay_list = [item["delay_ticks"] * cfg.tick_ms for item in completed]
        mean_delay_ms = sum(delay_list) / len(delay_list)  # 平均时延 ms
        max_delay_ms = max(delay_list)                    # 最大时延 ms

    # ========== 5. 丢包率计算 ==========
    if generated_payload_bits == 0:
        # 全程没有生成任何分组，丢包率直接置0，防止除以0报错
        loss_ratio = 0.0
    else:
        # 丢包率 = 丢弃的payload比特 / 总共生成的payload比特
        loss_ratio = dropped_payload_bits / generated_payload_bits

    # ========== 6. 返回指标字典，键名必须严格保持题目要求的名字 ==========
    return {
        "payload_utilization": payload_utilization,
        "wire_utilization": wire_utilization,
        "mean_delay_ms": mean_delay_ms,
        "max_delay_ms": max_delay_ms,
        "loss_ratio": loss_ratio,
        "backlog_payload_bits": backlog_payload_bits
    }

