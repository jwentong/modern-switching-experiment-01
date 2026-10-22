# AI协作记录

工具与模型：在 VS Code 中使用 GitHub Copilot 协助代码理解、实现、测试设计和报告整理。

## 一项真实协作过程

需求与输入：我要求依次实现 `serve_circuit`、`serve_packet` 和 `summarize`，明确检查 `tick % users`、发送预算、跨 tick 剩余量、包头是否已计入、无时延样本、守恒与积压口径；之后要求为 `student_tests/test_my_case.py` 选一个边界，先列输入与手算预期，再写断言。

AI建议：电路发送只访问当前时隙用户队列，分组发送只扣减框架已初始化的 `remaining_wire_bits`，不得再次加包头；完整记录完成后才出队。指标从完成记录计算时延，空完成列表返回 `None`，并检查 generated = delivered + dropped + backlog。自拟测试选择观察窗口结束时尚未发完的大分组。

我的手算与测试：边界测试配置为 1 用户、1 tick、128 bit/tick、32 bit 包头，tick 0 到达 128 bit payload。完整记录需要 160 wire bit；本窗口发送 128 bit，剩余 32 wire bit。预期 delivered=0、dropped=0、backlog=128 payload bit、wire_sent=128、payload 利用率=0、线路忙碌率=1、平均/最大时延为 `None`。`grading/test_packet.py` 4 项、`grading/test_metrics.py` 3 项通过；`grading/test_circuit.py` 4 项和 `grading/test_integration.py` 3 项通过；`student_tests` 目录测试 1 项通过。性能仿真生成默认 8 组数据，集成测试通过。

修正或采纳理由：采纳逐函数实现并运行对应教师测试的做法。检查 `src/utils.py` 后确认分组 `remaining_wire_bits` 在入队时已设为 payload 加包头，因此没有在发送函数重加包头。自拟用例针对有限窗口边界，不复制教师样例；其手算与测试结果一致，没有编造失败或修正过程。

我能解释的核心逻辑：每 tick 的预算从 `cfg.slot_bits` 开始，发送量为记录剩余 wire bit 与预算的较小值。只有剩余量变成 0 才标记完成并释放对应 payload 缓存；观察窗口结束时仍未完成的记录整体计入 backlog。`summarize` 用完整交付记录统计时延，并检查生成 payload 在交付、丢弃和积压三类间守恒。
