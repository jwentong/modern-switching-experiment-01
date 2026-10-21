"""Generate the Experiment 1 Word report from verified local outputs."""
from __future__ import annotations

import csv
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "实验一_电路交换与分组交换实验报告.docx"
BLUE = "1F4E79"
LIGHT_BLUE = "D9EAF7"


def set_font(run, size=10.5, bold=False, color=None, name="宋体"):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)


def shade(cell, fill):
    element = OxmlElement("w:shd")
    element.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(element)


def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.style = f"Heading {level}"
    r = p.add_run(text)
    set_font(r, 16 if level == 1 else 13, True, (31, 78, 121), "黑体")


def add_body(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0.28)
    p.paragraph_format.line_spacing = 1.35
    set_font(p.add_run(text))


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.line_spacing = 1.2
    set_font(p.add_run(text))


def set_cell(cell, text, header=False, size=8.5):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(str(text))
    set_font(run, size, header, (255, 255, 255) if header else None)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    if header:
        shade(cell, BLUE)


def add_table(doc, headers, rows, size=8.5):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, header in enumerate(headers):
        set_cell(table.cell(0, i), header, True, size)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell(cells[i], value, False, size)
    return table


def pct(value):
    return f"{float(value) * 100:.2f}%"


def fixed(value):
    return f"{float(value):.2f}"


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run(text), 9, False, (89, 89, 89))


def main():
    results = list(csv.DictReader((ROOT / "results" / "comparison.csv").open(encoding="utf-8-sig")))
    sensitivity = list(csv.DictReader((ROOT / "results" / "extra" / "header_sensitivity.csv").open(encoding="utf-8-sig")))

    doc = Document()
    section = doc.sections[0]
    section.top_margin = section.bottom_margin = Inches(0.65)
    section.left_margin = section.right_margin = Inches(0.7)
    normal = doc.styles["Normal"]
    normal.font.name = "宋体"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.font.size = Pt(10.5)

    # Cover
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    set_font(p.add_run("现代交换原理实验报告"), 20, True, (31, 78, 121), "黑体")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run("实验一：电路交换与分组交换"), 16, True, None, "黑体")
    doc.add_paragraph()
    info = doc.add_table(rows=4, cols=2)
    info.style = "Table Grid"
    info.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row, label, value in [
        (0, "姓名", "<待填写>"),
        (1, "学号", "<待填写>"),
        (2, "班级", "<待填写>"),
        (3, "实验日期", "2026-10-21"),
    ]:
        set_cell(info.cell(row, 0), label, False, 10.5)
        shade(info.cell(row, 0), LIGHT_BLUE)
        set_cell(info.cell(row, 1), value, False, 10.5)
    add_body(doc, "本报告依据课程 README、实验一 PRD、实际源代码、自动化测试及本机生成的结果文件撰写。姓名、学号和班级因未提供而保留待填写项。")
    doc.add_page_break()

    add_heading(doc, "一、实验目的与要求")
    add_body(doc, "本实验以相同的业务到达序列、链路容量、缓存配额和观察窗口为基础，公平比较固定时隙电路交换与共享 FIFO 分组交换。实验重点是理解固定资源预留、统计复用、包头开销、队列排队、尾丢弃和有限观察窗口对效率、时延、丢失和积压的共同影响。")
    for item in [
        "补全 serve_circuit、serve_packet 和 summarize 三个函数，保持教师提供的接口、测试和评分规则不变。",
        "使用 4 用户、256 tick、每 tick 1 ms、每 tick 128 bit、32 bit 包头和 4096 bit payload 缓存的默认配置，比较四类业务。",
        "生成 8 组结果、JSON/CSV 和三张图，编写独立边界反例，并完成报告和 AI 协作记录。",
        "同时解释有效载荷利用率、线路忙碌率、完成时延、丢失率和积压，确保 generated=delivered+dropped+backlog。",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "二、实验方法与步骤")
    for index, item in enumerate([
        "阅读 README、PRD、数据类型和函数 docstring，确认到达先于发送、完成发生在 tick 结束边界以及窗口结束不追加排空。",
        "创建项目虚拟环境，安装 numpy、matplotlib、pytest；通过环境检查和框架测试。",
        "实现电路服务：仅服务 tick % users 对应队列，在预算内按 FIFO 发送，空时隙不借用。",
        "实现分组服务：共享 FIFO、包头仅计一次、队首可跨 tick 续传且不允许后续记录抢占。",
        "实现指标统计及守恒检查；无完成记录时平均和最大时延返回 None。",
        "运行公开测试、集成测试和自拟反例，生成性能结果及图表。",
        "在 continuous 场景将包头改为 0、32、64 bit，补充参数敏感性分析。",
    ], 1):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.3
        set_font(p.add_run(f"{index}. {item}"))

    add_heading(doc, "三、实验过程及内容")
    add_heading(doc, "1. 核心逻辑实现", 2)
    add_body(doc, "电路交换函数先依据 tick % cfg.users 选取唯一可服务用户队列。在剩余预算大于零且队列非空时，发送量取预算和队首 remaining_wire_bits 的较小值。记录未完成时保留队首并结束当前 tick；记录完成后出队，若预算仍有余量则继续发送该用户下一条记录。")
    add_body(doc, "分组交换函数采用共享 FIFO。框架在准入时已把 remaining_wire_bits 设为 payload_bits+header_bits，因此服务函数只能扣减该字段，不能重复增加包头。队首未完成时立即停止当前 tick，保证后续记录不能交错或抢占。")
    add_body(doc, "指标函数先验证 payload 守恒，再按观察窗口内的 completed 记录计算时延；有效载荷利用率只计完整交付 payload，线路忙碌率还包含包头和未完成记录已发送的 wire bit。")

    add_heading(doc, "2. 两用户手工推演", 2)
    add_body(doc, "设 2 用户、2 tick、每 tick 1 ms、容量 128 bit、包头 32 bit，缓存足够。仅在 tick 0 有用户 1 到达一条 96 bit 记录。tick 0 电路模式服务用户 0 因而空闲，tick 1 才发送用户 1 的 96 bit，于 2 ms 完成；分组模式在 tick 0 直接发送 96+32=128 wire bit，于 1 ms 完成。两种模式有效载荷利用率均为 37.5%，但线路忙碌率分别为 37.5% 和 50.0%，时延分别为 2 ms 和 1 ms。")
    add_table(doc, ["tick", "到达", "电路服务", "分组服务", "完成情况"], [
        ["0", "用户1：96 bit", "服务用户0，空闲", "发送128 wire bit", "分组于1 ms完成"],
        ["1", "无", "发送用户1的96 bit", "无", "电路于2 ms完成"],
    ])

    add_heading(doc, "3. 自拟反例与测试", 2)
    add_body(doc, "自拟测试构造共享 FIFO 中的 A、B 两条记录：A 的 remaining_wire_bits 为 232，B 为 64，每 tick 预算为 128。第一个 tick 只能发送 A 的前 128 bit，因此 A 余 104、B 仍为 64；第二个 tick 先完成 A 的 104 bit，再发送 B 的 24 bit，B 余 40。该反例验证了大队首跨 tick 续传时，后续记录不得抢占或交错发送。")
    add_body(doc, "实际验证结果：环境检查通过；框架、公开核心、集成和自拟测试合计 19 passed。本地自动评分为 70.0/70 自动项，教师人工复核的 30 分尚未计入最终成绩。")

    add_heading(doc, "四、实验结果")
    add_body(doc, "以下数据来自本机实际生成的 results/comparison.csv，随机业务场景使用固定种子 2026。")
    add_table(doc, ["场景", "模型", "有效载荷利用率", "线路忙碌率", "平均时延(ms)", "最大时延(ms)", "丢失率", "积压(bit)"], [
        [r["scenario"], r["mode"], pct(r["payload_utilization"]), pct(r["wire_utilization"]), fixed(r["mean_delay_ms"]), fixed(r["max_delay_ms"]), pct(r["loss_ratio"]), f"{int(float(r['backlog_payload_bits'])):,}"]
        for r in results
    ], 7.5)

    add_heading(doc, "1. 结果分析", 2)
    for item in [
        "连续满载下，电路交换与到达模式匹配，达到 100.00% 有效载荷利用率且无丢失。分组模式虽达到 100.00% 线路忙碌率，但包头导致有效载荷利用率降至 79.69%，并出现 8.98% 丢失和 3712 bit 积压。",
        "错峰突发下，共享 FIFO 可复用其他用户未使用的时隙，分组模式达到 75.00% 有效载荷利用率、1.00 ms 平均时延、零丢失和零积压；固定时隙不能借用空资源，性能较差。",
        "同步突发下两个模型都有排队和窗口末尾积压。本配置中电路模式完成更多 payload，平均和最大时延均低于分组模式，说明统计复用并非在所有负载下都占优。",
        "轻载随机下两种模式均完整交付所有 payload；分组模式将平均时延由 3.11 ms 降至 1.10 ms，但更高的线路忙碌率主要来自包头开销。",
    ]:
        add_bullet(doc, item)

    for filename, caption in [
        ("comparison_metrics.png", "图1  四类业务下两种交换方式的指标比较"),
        ("queue_occupancy.png", "图2  各场景下的队列 payload 占用轨迹"),
        ("pcm_frame_view.png", "图3  PCM 帧视图（教学辅助示例）"),
    ]:
        doc.add_picture(str(ROOT / "results" / filename), width=Inches(6.0))
        add_caption(doc, caption)

    add_heading(doc, "2. 包头敏感性分析", 2)
    add_body(doc, "仅将分组模式 header_bits 设置为 0、32、64，其他参数、连续满载业务和观察窗口保持默认。附加数据保存在 results/extra/header_sensitivity.csv。")
    add_table(doc, ["包头(bit)", "有效载荷利用率", "平均时延(ms)", "最大时延(ms)", "丢失率", "积压(bit)"], [
        [r["header_bits"], pct(r["payload_utilization"]), fixed(r["mean_delay_ms"]), fixed(r["max_delay_ms"]), pct(r["loss_ratio"]), f"{int(float(r['backlog_payload_bits'])):,}"]
        for r in sensitivity
    ], 8)
    add_body(doc, "包头从 0 bit 增加到 64 bit 时，有效载荷利用率从 100.00% 降至 66.41%，平均时延从 2.50 ms 升至 35.37 ms，丢失率升至 21.88%。这说明在链路容量固定时，封装开销会减少可用于 payload 的容量，并放大时延、尾丢弃和积压。")

    add_heading(doc, "五、结论与局限")
    add_body(doc, "本实验表明不存在在所有业务下均绝对占优的交换方式。来源不均衡或轻载时，共享 FIFO 的统计复用可降低时延；连续满载和同步突发时，分组包头及 FIFO 排队可能抵消共享收益。评价时必须同时检查交付量、时延、丢失和积压，不能只看线路忙碌率。")
    add_body(doc, "本实验为单链路离散时钟教学模型，未模拟建链、传播时延、误码、重传、多跳路由和真实设备的全部存储开销；窗口结束时不追加排空。因此结论用于说明资源分配机制及其适用条件，不应直接外推为真实通信网络的整体性能结论。")

    add_heading(doc, "六、参考资料")
    for item in [
        "课程仓库 README.md：实验规则、运行命令和提交要求。",
        "《实验一 PRD：电路交换与分组交换》V1.2（2026-10-18）：模型约定、验收标准和评分要求。",
        "src/models.py、src/utils.py 和 grading/：数据模型、仿真框架和公开测试。",
        "本机生成的 results/comparison.csv、results/comparison.json、三张 PNG 图及 results/extra/header_sensitivity.csv。",
    ]:
        add_bullet(doc, item)

    doc.core_properties.title = "实验一：电路交换与分组交换实验报告"
    doc.core_properties.author = "<待填写>"
    doc.save(OUTPUT)
    print(OUTPUT)
    print(f"size={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    main()
