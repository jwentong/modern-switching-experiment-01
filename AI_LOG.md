# AI 协作记录

工具与模型：ChatGPT / Codex（用于阅读 README、PRD、模板和现有函数 docstring，梳理模型契约、手算预期与测试思路）。

## 一项真实协作过程

**需求与输入**：

我需要核对 `src/part2_packet.py` 中 `serve_packet(queue, tick, cfg)` 的规则，并设计一个能发现 FIFO 被错误抢占的自拟测试。输入包括 README、PRD、`src/models.py`、`src/utils.py` 和 `serve_packet` 的 docstring。模型约定为：`remaining_wire_bits` 在入队时已经包含一次包头，单 tick 最多发送 `cfg.slot_bits`，必须先发送完共享队列队首，允许跨 tick 续传但不允许记录交错。

**AI 建议**：

建议把每个 tick 的发送逻辑写成“只观察队首”的循环：

1. 初始化本 tick 剩余预算为 `cfg.slot_bits`。
2. 只要队列非空且预算大于 0，就发送 `min(预算, 队首.remaining_wire_bits)`。
3. 仅当队首的 `remaining_wire_bits` 减为 0 时，才 `popleft()` 并记录完成；否则立即结束本 tick。
4. 不在函数中重新增加包头，不修改 `payload_bits`，也不处理非队首记录。

**我的手算与测试**：

我采用 A、B 两条记录的反例：A 的 wire 剩余量为 232 bit，B 为 64 bit，tick 预算为 128 bit。

- Tick 0：只能发送 A 的 128 bit，因此 A 余 104、B 仍为 64、完成列表为空。
- Tick 1：必须先发送 A 的 104 bit，再用余下 24 bit 发送 B，因此 A 完成、B 余 40。

对应断言写入 `student_tests/test_my_case.py`。实现三个 TODO 后，运行：

```powershell
.\.venv\Scripts\python.exe -m pytest student_tests -q
.\.venv\Scripts\python.exe -m pytest grading/test_packet.py -q
```

实际测试输出：`grading/test_packet.py` 为 **4 passed**；`student_tests` 为 **1 passed**。在完成结果文件后，又运行了框架、核心、集成与自拟测试的完整组合，共 **19 passed**；本地自动评分为 **70.0/70 自动项**，人工 30 分待教师复核。

**修正或采纳理由**：

采用该建议是因为它直接对应 PRD 的 AC04：第一 tick 不能提前发送 B，第二 tick 在 A 完成后才可发送 B 的一部分。若代码把包头再次加到 A、在 A 未完成时服务 B，或把部分发送误报为完成，手算和断言都会出现差异。文档研读和手算不能替代实际测试；在提交前必须以本机通过的测试和生成的结果文件为准。

**我能解释的核心逻辑**：

`remaining_wire_bits` 表示尚未在线路上发送的总 bit 数。对分组模式，它由框架初始化为 `payload_bits + header_bits`，因此服务函数只能扣减，不能再次添加 32 bit 包头。FIFO 不交错由“未完成队首时立即结束当前 tick”保证；积压统计的对象则是未完成记录的完整原始 `payload_bits`，而不是剩余 wire bit 或已经发送的部分。
