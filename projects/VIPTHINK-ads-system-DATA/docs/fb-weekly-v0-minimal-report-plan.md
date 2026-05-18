# FB 自动周报底稿 V0 - 最小报表集与导出计划

生成日期：2026-05-18

## 当前产物

本文件是 `/goal` 第一步产物：只基于已有阶段文档和 `runtime/private/smartbi_meta_phase1/` inspect 结果，提出 V0 最小报表集、导出计划和风险判断。

本步骤未导出 SmartBI 报表，未读取明细数据，未写入任何外部系统。

## V0 目标收敛

V0 目标：生成一份可人工补观点的 `FB 自动周报底稿 Markdown`。

V0 不做：

- 不生成投放师观点。
- 不自动判断原因。
- 不给最终调优建议。
- 不做长期历史归因分析。

V0 要做：

- 自动填充周报数据骨架。
- 明确数据来源和时间窗口。
- 提供固定表格结构。
- 标出人工补充位。
- 标出字段缺口和口径待确认项。

## V0 最小报表集

### P0 必须导出

| 优先级 | 报表 | 类型 | 用途 | 为什么必须 | 风险 |
|---|---|---|---|---|---|
| P0 | `REDACTED_REPORT_A` | SPREADSHEET_REPORT | creative_asset维度表现、creative_asset空耗、广告对象字段 | V0 周报的核心表，能覆盖REDACTED_CREATIVE_TYPE、广告ID/名称、消耗、REDACTED_CONVERSION_A、REDACTED_CONVERSION_B、ROI2 等方向 | 参数多，表头可能是透视/多行结构 |
| P0 | `REDACTED_REPORT_B` | SPREADSHEET_REPORT | FB 渠道日监控、区域/REDACTED_DIM_OWNER/整体节奏 | 覆盖 FB 日监控与整体趋势，是周报整体部分的候选来源 | 可能偏汇总，字段粒度待确认 |

### P1 第二批导出

| 优先级 | 报表 | 类型 | 用途 | 为什么暂列 P1 | 风险 |
|---|---|---|---|---|---|
| P1 | `REDACTED_REPORT_C` | SPREADSHEET_REPORT | 链路类型拆解 | inspect 参数少，可能是简洁汇总表，可作为补充 | 可能无法覆盖creative_asset/对象维度 |
| P1 | `REDACTED_REPORT_D` | SPREADSHEET_REPORT | REDACTED_REGION_A/非REDACTED_REGION_A、REDACTED_CREATIVE_TAGS、内部策略标签 | 适合区域/策略测试模块 | 混合REDACTED_INTERNAL_CREATIVE_TAG，口径复杂，V0 可后置 |

### P2 暂不导出，只做 row guard

| 优先级 | 报表 | 类型 | 用途 | 处理方式 |
|---|---|---|---|---|
| P2 | `REDACTED_REPORT_K` | SIMPLE_REPORT | REDACTED_PAGE_FLOW_SOURCE | 先 row guard，不直接导出 |
| P2 | `REDACTED_REPORT_L` | SIMPLE_REPORT | REDACTED_PAGE_FLOW_SOURCE | 先 row guard，不直接导出 |

## 推荐导出顺序

### Step 1：只导出 P0 两张 SPREADSHEET_REPORT

原因：

- 这两张最能支撑 V0 周报底稿。
- 如果这两张能解析出表头和字段，已经可以生成第一版底稿。
- 避免一次导出 4 张后难以定位刷新/解析问题。

导出对象：

1. `REDACTED_REPORT_A`
2. `REDACTED_REPORT_B`

导出参数建议：

- 先使用报表默认参数。
- 不覆盖筛选项。
- 导出后只 inspect workbook，不做业务结论。

理由：当前 inspect 已显示这些报表带有默认时间参数，例如 `2026-05-01`、`2026-05-17`。如果 V0 先跑通流程，默认参数比手工覆盖更稳。

### Step 2：解析 workbook 结构

对导出的 xlsx 运行 workbook inspector，提取：

- sheet 名称
- sheet 行列规模
- 合并单元格情况
- 前 10-20 行样式/内容摘要
- 可能表头行
- 字段候选
- 是否是可机器解析的 tidy table
- 是否需要手写解析规则

### Step 3：决定是否导出 P1

如果 P0 已足够生成 V0 底稿：

- P1 只作为补充模块。

如果 P0 缺少整体达成或区域测试字段：

- 再导出 `REDACTED_REPORT_C` 或 `REDACTED_REPORT_D`。

### Step 4：SIMPLE_REPORT row guard

对 `REDACTED_REPORT_K/REDACTED_REPORT_L` 只做 row guard：

- 不直接导出。
- 先探测行数和类型。
- 超过阈值则暂停，要求筛选。

## V0 周报底稿字段需求

| 周报模块 | 必需字段 | 首选来源 | 缺口处理 |
|---|---|---|---|
| 数据范围 | 开始日期、结束日期/快照日期、报表路径、导出时间 | SmartBI 参数 + run log | 无法识别则手填占位 |
| FB 整体达成 | 指标、目标、实际、达成率 | `REDACTED_REPORT_B` | 若没有目标列，先只填实际值和目标占位 |
| 渠道与区域表现 | 区域/策略、消耗、REDACTED_CONVERSION_A、REDACTED_CONVERSION_B、REDACTED_CONVERSION_C、REDACTED_CONVERSION、成本、ROI2 | `REDACTED_REPORT_B` | 若区域字段缺失，退化为总览 |
| creative_asset维度表现 | REDACTED_CREATIVE_TYPE、广告名称、消耗、曝光、点击、CTR、CVR、REDACTED_CONVERSION_A、REDACTED_CONVERSION_B、REDACTED_CONVERSION_B_COST、ROI2 | `REDACTED_REPORT_A` | 若REDACTED_CREATIVE_TYPE缺失，先按广告名称展示 |
| 空耗/高成本候选 | 对象名称/ID、消耗、成效、成效成本、异常类型 | `REDACTED_REPORT_A` | V0 只列候选，不给停投建议 |
| 人工观点占位 | 本周判断、可能原因、下周动作、协同事项 | 模板 | 永远人工填写 |

## 风险判断

| 风险 | 影响 | 缓解方式 |
|---|---|---|
| SPREADSHEET_REPORT 是透视/格式化工作簿 | 表头可能多行，不能直接 pandas read table | 先 workbook inspect，再写定制解析 |
| 默认参数不是目标周 | 周报时间窗口可能不对 | V0 先跑通；下一轮加入日期覆盖 |
| 目标值不在 P0 报表中 | 整体达成模块只能填实际值 | 用目标占位，后续接目标报表 |
| REDACTED_CREATIVE_FIELDS和广告字段混合 | 字段字典需要区分 Meta 对象与REDACTED_INTERNAL_CREATIVE_TAG | 字段映射草案标记来源与置信度 |
| 导出 xlsx 可能含敏感明细 | 不能进入 docs | 原始文件只放 runtime/private，docs 只放聚合/字段结构 |
| P0 不含空耗率 | 空耗模块无法完整填充 | V0 先做高成本/高消耗低成效候选，后续接空耗监控报表 |

## 受控导出计划

建议用户确认后执行以下动作：

1. 在本项目生成一份临时 SmartBI config，只包含 P0 两张报表。
2. config 输出目录指向：`runtime/private/fb_weekly_v0/smartbi_exports/{task}/{run_date}`。
3. 使用 `date-solution/scripts/smartbi_cli.py run --config <临时config> --task <task> --overwrite --json` 串行导出。
4. 对导出的 xlsx 运行 `date-solution/scripts/inspect_smartbi_workbook.py`。
5. 生成字段结构 JSON。
6. 如果字段结构可用，再生成 V0 周报底稿 Markdown。

## 下一确认闸口

请确认：

1. 是否同意先只导出 P0 两张：`REDACTED_REPORT_A`、`REDACTED_REPORT_B`？
2. 是否同意先使用报表默认参数，不手动覆盖日期？
3. 原始 xlsx 和解析 JSON 是否统一放在 `runtime/private/fb_weekly_v0/`？
4. 如果 P0 解析后缺少目标值或空耗率，是否允许 V0 先用占位，不继续扩大报表范围？
