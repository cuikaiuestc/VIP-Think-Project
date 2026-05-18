# BI/Meta 报表整理 - 阶段 1 Facebook 报表元数据盘点

生成日期：2026-05-18

## 当前产物

本阶段完成 SmartBI 只读元数据探测：

- 已读取目录：`REDACTED_INTERNAL_BI_ROOT`
- 已保存目录快照：`runtime/private/smartbi_meta_phase1/catalog_overseas_ads_depth3.json`
- 已 inspect 4 张 Facebook/Meta 候选 `SPREADSHEET_REPORT`
- 已保存 inspect 原始 JSON：`runtime/private/smartbi_meta_phase1/`
- 未导出报表明细。
- 未读取 `SIMPLE_REPORT` 明细。
- 未写入 SmartBI、数据库、广告账户或 GitHub。

执行方式：

```bash
source <local-secret-env>
cd <local-tools>
python3 scripts/smartbi_cli.py inspect-report --report-id <report_id> --report-path <report_path> --json
```

说明：

- `inspect-report` 能拿到 `SPREADSHEET_REPORT` 的 report id、路径、可见 sheet、参数和 config task draft。
- 它不能直接拿到报表表体字段列名。
- 真正的字段字典需要下一步做受控导出后再用 workbook inspector 解析，或针对 `SIMPLE_REPORT` 先做 row guard。

## BI 报表资产清单

| 报表名称 | SmartBI 路径 | 类型 | Sheet | 参数数 | 初步用途 | 风险 |
|---|---|---|---|---:|---|---|
| REDACTED_REPORT_A | `REDACTED_INTERNAL_BI_ROOT/REDACTED_FOLDER_A/REDACTED_REPORT_A` | SPREADSHEET_REPORT | Sheet1 | 16 | creative_asset维度链路指标，连接 Meta 广告/creative_asset与后端链路指标 | 未导出表体，字段列名待确认 |
| REDACTED_REPORT_B | `REDACTED_INTERNAL_BI_ROOT/REDACTED_FOLDER_A/REDACTED_REPORT_B` | SPREADSHEET_REPORT | Sheet1 | 7 | FB 渠道日监控，偏渠道/区域/REDACTED_DIM_OWNER视角 | 未导出表体，字段列名待确认 |
| REDACTED_REPORT_C | `REDACTED_INTERNAL_BI_ROOT/REDACTED_FOLDER_A/REDACTED_REPORT_C` | SPREADSHEET_REPORT | Sheet1 | 2 | FB 链路类型日监控，偏日期快照视角 | 参数少，实际维度需看表体 |
| REDACTED_REPORT_D | `REDACTED_INTERNAL_BI_ROOT/REDACTED_FOLDER_A/REDACTED_REPORT_D` | SPREADSHEET_REPORT | Sheet1 | 17 | REDACTED_REGION_A/非REDACTED_REGION_A区域测试，含creative_asset、创意、广告对象过滤 | 可能混合creative_asset属性、REDACTED_INTERNAL_TAG和 Meta 广告对象 |

## 参数与字段线索

这些是 SmartBI 参数，不等同于最终表体字段，但可作为字段字典的第一批线索。

| 字段/参数 | 出现报表 | 初步来源判断 | 类型 | 置信度 | 待确认问题 |
|---|---|---|---|---|---|
| 开始日期 | 4/4 | BI 参数 | 时间过滤 | 高 | 是否所有报表都按自然日/业务日一致处理？ |
| 结束日期/快照日期 | 4/4 | BI 参数 | 时间过滤/快照口径 | 高 | `结束日期` 与 `快照日期` 是否等价？ |
| REDACTED_DIM_REGION_TIER | FB 渠道日监控、creative_asset维度、REDACTED_REGION_A测试 | 内部维度 | 区域维度 | 中 | 与国家/城市/REDACTED_DIM_REGION_TIER如何映射？ |
| REDACTED_DIM_REGION_SEGMENT | FB 渠道日监控 | 内部维度 | 区域维度 | 中 | 是否对应国家/市场，如REDACTED_REGION_SET、新马等？ |
| REDACTED_DIM_PLATFORM_WEEKLY | FB 渠道日监控、REDACTED_REGION_A测试 | BI 改名字段/渠道维度 | REDACTED_DIM_PLATFORM | 中 | `REDACTED_PLATFORM_VALUE` 是否就是 Meta/Facebook 数据来源？ |
| REDACTED_DIM_OWNER_WEEKLY | FB 渠道日监控 | 内部维度 | REDACTED_DIM_OWNER/负责人 | 中 | 是否代表投放负责人或账户归属？ |
| 近N天 | FB 渠道日监控 | BI 参数 | 时间窗口 | 中 | 与开始日期/快照日期是否叠加过滤？ |
| 投放账户 | creative_asset维度、REDACTED_REGION_A测试 | Meta/BI 改名字段 | 账户维度 | 中 | 是否对应 Meta `account_id/account_name`？ |
| 广告组ID | creative_asset维度、REDACTED_REGION_A测试 | Meta 字段候选 | Ad Set ID | 高 | 是否对应 Meta `adset_id`？ |
| 广告ID | creative_asset维度、REDACTED_REGION_A测试 | Meta 字段候选 | Ad ID | 高 | 是否对应 Meta `ad_id`？ |
| 广告名称 | creative_asset维度、REDACTED_REGION_A测试 | Meta 字段候选 | Ad Name | 高 | 是否对应 Meta `ad_name`？ |
| 上线日期/上线开始日期/上线结束日期 | creative_asset维度 | BI/Meta 混合候选 | 投放开始时间 | 中 | 是否来自 Meta `created_time`，还是内部投放上线日期？ |
| creative_asset | REDACTED_REGION_A测试 | REDACTED_INTERNAL_CREATIVE_TAG/creative_asset维度 | creative_asset属性 | 中 | 是否对应 creative、内部creative_asset ID，还是 BI 标签？ |
| REDACTED_CREATIVE_TYPE | REDACTED_REGION_A测试 | REDACTED_INTERNAL_CREATIVE_TAG | creative_asset属性 | 中 | 是否有枚举字典？ |
| REDACTED_CREATIVE_SOURCE | REDACTED_REGION_A测试 | REDACTED_INTERNAL_CREATIVE_TAG | creative_asset来源 | 中 | 是否与REDACTED_CREATIVE_PRODUCTION流程关联？ |
| REDACTED_CREATIVE_PRODUCTION_PERIOD | REDACTED_REGION_A测试 | REDACTED_INTERNAL_CREATIVE_TAG | 时间/REDACTED_CREATIVE_PRODUCTION | 中 | 是否是creative_asset产出月，不是投放月份？ |
| REDACTED_REQUESTER | REDACTED_REGION_A测试 | REDACTED_INTERNAL_WORKFLOW_FIELD | REDACTED_CREATIVE_REQUESTER | 中 | 是否允许进入共享字段字典？ |
| REDACTED_FLAG_A | REDACTED_REGION_A测试 | REDACTED_INTERNAL_TAG | creative_asset/线索质量 | 中 | 口径由谁维护？ |
| REDACTED_FLAG_B | REDACTED_REGION_A测试 | REDACTED_INTERNAL_TAG | creative_asset/运营标签 | 中 | 口径由谁维护？ |
| REDACTED_FLAG_C | REDACTED_REGION_A测试 | REDACTED_INTERNAL_TAG | creative_asset/线索标签 | 中 | 口径由谁维护？ |
| REDACTED_CREATIVE_FORMAT_TAG | REDACTED_REGION_A测试 | REDACTED_INTERNAL_CREATIVE_TAG | REDACTED_CREATIVE_FORMAT | 中 | 是否是二元标签或分类字段？ |

## 字段差异与缺口表

| 问题类型 | 字段/报表 | 现象 | 影响 | 建议处理 | 是否需确认 |
|---|---|---|---|---|---|
| Meta 字段改名 | `广告组ID`、`广告ID`、`广告名称` | 参数高度疑似 Meta `adset_id/ad_id/ad_name` | 可作为 Meta-BI 映射起点 | 导出表体后核对实际列名和值格式 | 是 |
| 账户字段不完整 | `投放账户` | 只看到账户名称/过滤参数，未见 account id | 与 Meta account join 可能不稳 | 检查表体是否含账户 ID 或账户名 | 是 |
| 日期口径不明 | `开始日期`、`结束日期`、`快照日期`、`近N天` | 同类报表使用不同日期参数 | 周期达成/日监控可能不可直接比较 | 建立日期口径表 | 是 |
| REDACTED_INTERNAL_TAG混入 | REDACTED_REGION_A测试报表 | creative_asset、REDACTED_FLAG_A、REDACTED_FLAG_B、REDACTED_FLAG_C、REDACTED_CREATIVE_SOURCE等 | 这些不是 Meta 原始字段 | 分为REDACTED_INTERNAL_CREATIVE_TAG，不放入 Meta 字段 | 是 |
| 表体字段缺失 | 4 张 SPREADSHEET_REPORT | inspect 不返回表体列名 | 不能完成字段字典 | 需要受控导出 + workbook inspect | 是 |
| SIMPLE_REPORT 未处理 | 落地页 V2/V3 | 目录中存在 `SIMPLE_REPORT` | 可能更像源表/明细，字段价值高 | 先 probe row count，再决定是否导出 | 是 |

## 投放分析任务框架

| 任务 | 业务问题 | 所需字段 | 可用报表 | 当前缺口 | 可支持的决策 | 不能支持的决策 |
|---|---|---|---|---|---|---|
| creative_asset后端REDACTED_CONVERSION分析 | 哪些 FB creative_asset带来有效REDACTED_CONVERSION_A、REDACTED_CONVERSION_B、REDACTED_CONVERSION_C、REDACTED_CONVERSION？ | 广告ID、广告名称、广告组ID、投放账户、creative_asset、REDACTED_CREATIVE_TYPE、内部REDACTED_CONVERSION字段 | REDACTED_REPORT_A、REDACTED_REPORT_D | 表体指标列、内部REDACTED_CONVERSION字段未确认 | 确定字段核对方向和creative_asset分析主报表 | 不能判断creative_asset好坏 |
| FB 渠道日监控 | FB 渠道每日消耗、线索、REDACTED_CONVERSION是否异常？ | 日期、渠道、区域、消耗、REDACTED_CONVERSION_A/REDACTED_CONVERSION、成本 | REDACTED_REPORT_B、REDACTED_REPORT_C | 表体指标列未确认 | 建立日监控报表资产清单 | 不能做趋势结论 |
| 区域/REDACTED_REGION_A测试分析 | REDACTED_REGION_A与非REDACTED_REGION_A投放表现是否不同？ | REDACTED_DIM_REGION_TIER、REDACTED_DIM_REGION_SEGMENT、REDACTED_DIM_PLATFORM、REDACTED_CREATIVE_TAGS、REDACTED_CONVERSION指标 | REDACTED_REPORT_D | REDACTED_REGION_A/非REDACTED_REGION_A定义和指标列未确认 | 明确需要核对的分组字段 | 不能判断区域策略 |
| 漏斗达成监控 | FB 链路从花费到内部后端REDACTED_CONVERSION的漏斗是否达成？ | spend、click、lead、REDACTED_CONVERSION_A、REDACTED_CONVERSION_B、REDACTED_CONVERSION_C、REDACTED_CONVERSION、目标 | 4 张 FB 报表 + 后续全链路/漏斗报表 | Meta 与内部指标 join 口径未确认 | 形成下一批候选报表列表 | 不能确认目标完成率 |
| 数据自动化准备 | 哪些 BI 字段可映射 Meta API，哪些只能来自内部系统？ | Meta 对象 ID、内部业务 ID、日期、账户、creative_asset ID | creative_asset维度与日监控报表 | 主键/粒度缺失 | 识别自动化字段映射入口 | 不能设计最终回传方案 |

## 推荐下一步

阶段 1A 已完成：目录与 4 张核心 FB 报表 inspect。

阶段 1B 建议做两件事，但需要确认：

1. 对这 4 张 `SPREADSHEET_REPORT` 做受控导出，然后运行 workbook inspector，只提取 sheet 结构、表头、行列规模，不做业务结论。
2. 对 `REDACTED_REPORT_K/REDACTED_REPORT_L` 这两个 `SIMPLE_REPORT` 先做 row guard；如果行数过大，要求 SmartBI 侧筛选后再导出。

## 下一确认闸口

请确认：

1. 是否允许对这 4 张 `SPREADSHEET_REPORT` 做受控导出，用于提取表头和字段结构？
2. 导出时是否使用默认参数，还是要限定时间窗口，例如 2026-05-01 到 2026-05-17？
3. 是否把 `REDACTED_REPORT_K/REDACTED_REPORT_L` 纳入下一轮 row guard？
4. 字段字典优先服务哪个业务问题：creative_asset后端REDACTED_CONVERSION、FB 日监控、REDACTED_REGION_A测试，还是整体漏斗达成？
