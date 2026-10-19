# 包头长度附加实验说明

条件：仅改变 `Config.header_bits`，取值为 0、16、32、48、64 bit；其余参数保持 4 用户、256 tick、每 tick 128 bit、每 tick 1 ms、4096 bit payload 缓存、随机种子 2026。只对 packet 模型扫描，未修改基线 `results/comparison.json` 和 `results/comparison.csv`。

文件：`header_sweep.csv` 为 20 行明细，`header_sweep.json` 保存条件、测试表头和同样的明细。

结论：连续满载时，包头从 0 增至 64 bit，有效载荷利用率从 100.0000% 降至 66.4062%，平均时延从 2.5 ms 增至 35.3706 ms，并在 32 bit 起出现丢失。错峰突发在 0 至 32 bit 时保持 75% 有效载荷利用率，48 bit 起明显下降。同步突发的积压从 1056 bit 增至 1920 bit，轻载随机在 64 bit 时才出现约 1 ms 的平均时延增加。统计复用优势会随负载集中度、包头大小、缓存和观察窗口变化。
