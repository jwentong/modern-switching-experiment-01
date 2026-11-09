# AI协作记录

工具与模型：DeepSeek 编程助手（代码补全与结果生成）。

## 一项真实协作过程

需求与输入：补全 `src/part1_circuit.py`、`src/part2_packet.py`、`src/metrics.py` 三个 TODO，并生成结果与图表。

AI建议：三个函数采用同一骨架——先确定本 tick 发送预算 `budget = cfg.slot_bits`，循环处理队首记录：若 `remaining_wire_bits <= budget` 则完整发送并 pop 计入完成，否则部分发送并扣减预算、保留剩余 `remaining_wire_bits` 供下个 tick 续传；`summarize` 先做守恒检查再计算各项指标。

我的手算与测试：按文档 6.1 两用户例子手算电路/分组均 37.5% 有效利用率；按 AC02、AC04 核对了跨 tick 续传（200 bit 记录先发 128 再发 72）与共享 FIFO 不交错。随后运行 grading 全套测试，18/18 通过；运行性能脚本得到 8 行结果，守恒成立。

修正或采纳理由：首次生成即通过全部公开测试；另用自拟反例验证了“不借用空时隙”“包头只计一次”“部分发送计积压”三条边界，未发现需修正之处。

我能解释的核心逻辑：避免重加包头——`remaining_wire_bits` 在准入时已含一次包头，发送函数只做扣减；避免借用固定时隙——先算 `user = tick % users` 再只操作该用户队列；避免漏算积压——`summarize` 严格校验 `generated = delivered + dropped + backlog`，不相等抛 ValueError，杜绝用 0 掩盖无送达样本。
