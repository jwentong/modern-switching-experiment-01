# AI协作记录

工具与模型：OpenAI Codex 桌面版 AI 编程助手。使用方式为在本地仓库中解释模型、补全三个指定 TODO、运行测试并复核结果；学生信息为张志伟，2024280016。

## 一项真实协作过程

需求与输入：先读取课程 PRD、`README.md`、`docs/model_contract.md`、`src/models.py`、三个任务函数及公开测试，只修改 `src/part1_circuit.py`、`src/part2_packet.py` 和 `src/metrics.py`，不修改教师测试、评分脚本或接口。输入包含每用户队列、共享 FIFO、`slot_bits` 预算、`tick % users` 时隙映射、已经初始化一次包头费用和 `remaining_wire_bits` 的跨 tick 语义。

AI建议：电路函数先计算本 tick 用户，只在对应队列上循环发送；分组函数直接处理共享队首，不在每 tick 重加包头；两者都用 `min(预算, remaining_wire_bits)` 更新剩余量，完整归零后才弹出并记录完成。指标函数只按完整交付统计 payload，时延只使用完成记录，无完成样本返回 `None`，并在统计前验证 generated、delivered、dropped、backlog 的守恒关系。

我的手算与测试：两用户手算中，tick 0 只有用户 1 到达 96 bit，电路 tick 0 空闲、tick 1 发送并在 tick 2 边界完成，时延 2 ms；分组在 tick 0 发送 96+32=128 bit，并在 tick 1 边界完成，时延 1 ms。公开测试运行结果是环境与框架 `4 passed`、三个核心测试文件 `11 passed`、集成测试 `3 passed`。此外，我编写了两个独立边界测试：固定时隙不能借用且部分发送不交付，以及 200 bit payload 跨 tick 时保留 104 bit 且不重加包头；运行结果为 `2 passed`。

修正或采纳理由：首次实现已经满足公开测试和教师参考结果，因此没有虚构错误或修正过程。我采纳该实现，是因为它严格按队首发送、预算不超额、只有剩余量归零才完成；随后用自拟边界用例复核了公开测试未单独覆盖的资源借用和重复包头风险。生成结果后，`results/comparison.csv` 与 `examples/teacher_results/comparison.csv` 一致，说明指标口径和事件顺序一致。

我能解释的核心逻辑：发送函数每轮只处理当前队首，发送量不能超过本 tick 剩余预算，也不能超过记录剩余 wire bit。部分发送时只减少 `remaining_wire_bits`，payload 和完成状态均不变；完整归零后才弹出并交付。分组记录的 `payload_bits + header_bits` 只在准入时初始化一次，之后跨 tick 只递减剩余量。电路函数在进入循环前用 `tick % cfg.users` 固定服务对象，因此其他用户即使有积压也不能借用本用户时隙。指标函数先做守恒检查：生成 payload 必须等于完整交付、尾丢弃和未完成积压之和；平均时延只统计完成记录，无完成样本返回 `None`，避免把失败或积压误写成低时延。
