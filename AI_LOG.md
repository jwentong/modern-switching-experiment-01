  # AI协作记录

工具与模型：AI 编程助手（辅助排错与代码逻辑审查）。

## 一项真实协作过程

需求与输入：我负责实现 serve_circuit 和 serve_packet 函数，但在首次完成 serve_packet 后测试报错，且 summarize 中的 raw 数据结构不清楚。我需要AI协助排查Python缩进报错，并提供针对共享队列的发送逻辑以及守恒检查的实现建议。

AI建议：AI 建议在 serve_packet 中使用一个 while queue and budget > 0 的循环，每次取队首记录，计算 min(budget, record.remaining_wire_bits) 并扣减。对于 metrics.py，AI建议从 raw[completed] 列表中提取 delay_ticks 并求和，若为空则返回None，同时严格按照公式检查生成量是否等于交付量加丢弃量加积压量。

我的手算与测试：
1. 我手算了两用户两tick的小例子：tick0用户1到达96bit，分组需加上32bit包头为128bit。结果验证了只要在发送时判断 remaining_wire_bits 递减到0，就能正确交付。
2. 实际测试时，test_packet.py 一度报错 IndentationError: unindent does not match any outer indentation level。AI提示我复制代码时多带了一行 def 定义，导致代码缩进全乱了。我删掉多余行后，grading/test_packet.py 的4项测试全部通过。
3. 在运行 grading/test_metrics.py 时，我使用AI提供的代码，顺利让3项指标测试通过，包括守恒检查中故意传入不平等数据抛出ValueError的用例。

修正或采纳理由：我采纳了AI的发送逻辑建议，因为该逻辑正确实现了“不抢占、跨 tick 续传”的要求；同时修正了复制代码造成的缩进错误。对于分组交换，采纳了AI提醒的“不要再额外加包头”的边界验证。

我能解释的核心逻辑：
1. 如何避免重加包头：在 serve_packet 中直接使用 record.remaining_wire_bits，因为框架在数据入队时已经算好了 payload_bits + header_bits，我只负责扣减剩余比特，不关心包头。
2. 如何避免借用固定时隙：在 serve_circuit 中，必须严格计算 current_user = tick % cfg.users，并且只操作 queues[current_user] 这个队列。即使其他队列积压严重，当前tick轮到的用户如果没有数据，也必须返回 0。
3. 如何统计遗漏积压：在summarize中，严格断言generated_payload_bits ==delivered_paylo 
ad_bits + dropped_payload_bits + raw['backlog_payload_bits']，积压量直接取raw中的客观值，不遗漏任何没发完的数据。

自拟反例设计与验证：我编写了 test_my_case.py，针对“电路交换误借用时隙”设计了反例。我手算的预期是tick 0只服务用户0，因此当前用户为空时sent_bits必须为0。AI协助我构造了Pending数据，并使用了deque模拟队列。运行测试通过（1 passed），验证了代码逻辑没有越权借用他人时隙。