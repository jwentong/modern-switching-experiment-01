目的：解释固定时隙预留与共享 FIFO 的资源使用差异，识别统计复用收益和包头代价。



模型与参数：users=4, ticks=256, slot\_bits=128, tick\_ms=1, header\_bits=32, buffer\_payload\_bits=4096；事件顺序、窗口结束规则。



两用户手算：



模型	发送过程	完成时间	有效利用率	线路忙碌率

电路	tick 0 闲置，tick 1 发 96	2 ms	96/256=37.5%	37.5%

分组	tick 0 发 128	1 ms	96/256=37.5%	128/256=50%

结论：相同有效利用率不等于相同时延。



四场景结果：把 results/comparison.csv 的 8 行贴进来，分别解释 continuous、staggered\_burst、synchronized\_burst、light\_random 下 circuit 与 packet 的利用率、时延、丢失、积压。



自拟反例：输入、手算预期、断言依据、揭示的错误（用上一轮给的模板）。



参数变化分析：如果做了 results/extra/，说明改了哪个参数、条件、结果。



局限：单链路、已建立承载、不模拟传播/误码/重传/多跳/建链时延，不能据此评价真实系统总体优劣。



AI 协作说明：用了什么工具、哪些建议采纳、如何验证、哪些修正。



参考资料：README、docs/model\_contract.md、src/models.py、PRD、公开测试。

