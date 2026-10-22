# AI 协作记录

## 真实需求
实现 `serve_circuit` 和 `serve_packet` 中的核心发送循环逻辑，需要处理跨 tick 部分发送、预算控制、包头扣除等问题。

## 建议与验证
- **AI 建议**：使用 `while wire_bits < cfg.slot_bits and q:` 循环，通过 `remaining_wire_bits <= remaining_budget` 判断是整体发送还是部分发送。
- **我的验证**：基于 AC04 和 AC05 的规则，我在本地终端用 `pytest grading/test_packet.py` 运行了 4 项测试，全部通过，证明不会发生记录交错和重复加包头。

## 采纳与修正
代码采纳了 AI 的 `while` 循环结构。但在编写 `metrics.py` 时，我结合老师提供的 docstring，修正了无完成记录时时延应返回 `None` 的逻辑，防止用 0 冒充低时延。
