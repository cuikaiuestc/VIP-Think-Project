# 自动化投放系统数据交接包 v0

生成日期：2026-05-18

## 结论先行

这 4 张 SmartBI FB 报表可以作为业务理解和字段发现入口，但不建议直接作为自动化投放系统的 P0 源表。

主要原因：

- 4 张导出的 `SPREADSHEET_REPORT` 都被结构检查判定为 `pivot_dashboard`。
- 它们普遍存在多层表头、合并单元格、总计行/总计列、横向展开指标。
- 只有 `REDACTED_REPORT_A` 同时包含 `广告ID`、`广告组ID`、`广告名称` 等疑似 Meta join key，但仍混有总计层级和透视结构。
- 如果开发同事要做稳定系统接入，P0 应优先追底层回写表、SQL 来源或可导出的明细源表，而不是直接解析 BI 看板。

建议给开发同事的默认判断：

| 报表 | 判断 |
|---|---|
| REDACTED_REPORT_A | 最有价值的字段发现入口；可作为临时验证样本，不建议长期作为 P0 源表 |
| REDACTED_REPORT_B | 辅助展示/监控源；不建议作为系统源表 |
| REDACTED_REPORT_C | 辅助展示/链路趋势源；不建议作为系统源表 |
| REDACTED_REPORT_D | 策略/REDACTED_CREATIVE_TAGS参考；不建议作为系统源表 |
| REDACTED_REPORT_K/REDACTED_REPORT_L | `SIMPLE_REPORT`，row guard 通过；更像原始数据候选，下一步可考虑受控导出表头 |

## 交付文件

| 文件 | 用途 |
|---|---|
| `docs/dev-handoff/bi-report-assets.csv` | 4 张 FB 报表资产、导出结构和可接入性判断 |
| `docs/dev-handoff/field-access-priority.csv` | 字段接入优先级和来源判断 |
| `docs/dev-handoff/field-gap-and-questions.md` | 需要业务/开发反馈的问题 |
| `runtime/private/smartbi_handoff_v0/` | 私有原始运行产物，含导出 workbook、inspect JSON、row guard JSON |

## 执行范围

SmartBI 目标目录：

```text
REDACTED_INTERNAL_BI_ROOT
```

已受控导出的 4 张 `SPREADSHEET_REPORT`：

| 报表 | 行数 | 列数 | 合并单元格 | 类型判断 | 接入判断 |
|---|---:|---:|---:|---|---|
| REDACTED_REPORT_A | 2106 | 36 | 96 | pivot_dashboard | 字段发现入口；不建议直接 P0 |
| REDACTED_REPORT_B | 23 | 86 | 11 | pivot_dashboard | 辅助展示源 |
| REDACTED_REPORT_C | 23 | 29 | 5 | pivot_dashboard | 辅助展示源 |
| REDACTED_REPORT_D | 75 | 33 | 16 | pivot_dashboard | 策略标签参考 |

`SIMPLE_REPORT` row guard：

| 报表 | 行数 | 阈值 | 结果 |
|---|---:|---:|---|
| REDACTED_REPORT_K | 2406 | 5000 | 可在确认后受控导出 |
| REDACTED_REPORT_L | 1121 | 5000 | 可在确认后受控导出 |

## P0 数据源建议

严格按开发接入稳定性判断：

1. 不把 4 张 `SPREADSHEET_REPORT` 直接定为 P0 源表。
2. 把 `REDACTED_REPORT_A` 作为字段发现和临时样本。
3. 优先要求数据运营提供这几张报表背后的 SQL、回写表或明细表。
4. 若短期无法拿到底层表，再用 `REDACTED_REPORT_A` 做一次临时解析验证，但要写明技术债。
5. 下一步优先检查 `REDACTED_REPORT_K/REDACTED_REPORT_L`，因为它们是 `SIMPLE_REPORT`，更可能像明细源表。

## 字段接入判断

### 可作为 P0 候选

这些字段对自动化投放系统第一条闭环最关键，但仍需确认口径：

| 标准字段 | BI 字段 | 判断 |
|---|---|---|
| `ad_id` | 广告ID | 疑似 Meta `ad_id`，可作为核心 join key 候选 |
| `adset_id` | 广告组ID | 疑似 Meta `adset_id`，可作为核心 join key 候选 |
| `report_date` | 日期/开始日期/结束日期 | 时间分区和窗口字段 |
| `platform` | REDACTED_DIM_PLATFORM/REDACTED_PLATFORM_VALUE/REDACTED_DIM_COST_PLATFORM | 渠道过滤字段 |
| `spend` | 消耗 | Meta/BI 回写字段候选 |
| `lead_count` | REDACTED_CONVERSION_A_COUNT | 内部业务字段 |
| `booking_count` | REDACTED_CONVERSION_B_COUNT | 内部业务字段 |
| `show_count` | REDACTED_CONVERSION_C_COUNT | 内部业务字段 |
| `lead_cost` | REDACTED_CONVERSION_A_COST | BI 派生字段，需确认公式 |
| `booking_cost` | REDACTED_CONVERSION_B_COST | BI 派生字段，需确认公式 |

### P1 字段

适合后续诊断/优化，但不阻塞 P0：

- `ad_name` / 广告名称
- `account_name` / 投放账户
- `region_tier` / REDACTED_DIM_REGION_TIER
- `region_segment` / REDACTED_DIM_REGION_SEGMENT
- `creative_type` / REDACTED_CREATIVE_TYPE
- `launch_date` / 上线日期
- `gmv` / GMV
- `roi2` / ROI2
- `waste_spend` / 空耗金额
- `waste_rate` / 空耗占比
- `lead_to_booking_rate` / REDACTED_CONVERSION_A_TO_B_RATE
- `booking_to_show_rate` / REDACTED_CONVERSION_B_TO_C_RATE

### 暂不接

这些字段不建议进入 P0 系统模型：

- `成效`
- `成效成本`
- `REDACTED_REQUESTER`
- `预览链接`
- `REDACTED_CREATIVE_FORMAT_TAG`
- 任何只在透视表总计层级出现、没有稳定明细粒度的字段

## Meta / 内部 / 派生边界

| 类型 | 字段REDACTED_CONVERSION_A | 判断 |
|---|---|---|
| 疑似 Meta 字段 | 广告ID、广告组ID、广告名称、曝光、点击、CPM、CTR、CVR、消耗 | 需要确认是否来自 Meta 下载回写，还是 BI SQL 二次计算 |
| 内部业务字段 | REDACTED_CONVERSION_A_COUNT、REDACTED_CONVERSION_B_COUNT、REDACTED_CONVERSION_C_COUNT、REDACTED_PAID_EVENT、GMV | Meta API 不能直接提供，必须来自内部业务系统 |
| BI 派生字段 | REDACTED_CONVERSION_A_COST、REDACTED_CONVERSION_B_COST、ROI2、空耗占比、REDACTED_CONVERSION_A_TO_B_RATE、REDACTED_CONVERSION_C_TO_PAID_RATE | 不建议开发猜公式，必须拿 SQL 或口径说明 |
| REDACTED_INTERNAL_TAG | REDACTED_CREATIVE_TYPE、REDACTED_FLAG_A、REDACTED_FLAG_B、REDACTED_CREATIVE_SOURCE、REDACTED_CREATIVE_PRODUCTION_PERIOD | 需要确认维护系统和枚举 |

## 对开发同事的交接口径

请开发同事先评审以下判断：

1. 是否接受临时解析 `SPREADSHEET_REPORT` 透视表作为 P0 过渡方案？
2. 如果不接受，是否需要数据运营提供底层 SQL 或回写表？
3. 系统模型是否需要以 `ad_id + date` 作为第一层事实表主键？
4. 内部REDACTED_CONVERSION字段是否需要单独建 `backend_conversion_fact`？
5. Meta 原始字段是否未来应由 Meta API 自动拉取，替代投放师手动上传？

## 推荐 P0 数据模型草案

这不是最终 schema，只是给开发评审的最小方向：

```text
meta_ad_fact
- date
- account_id / account_name
- campaign_id / campaign_name
- adset_id / adset_name
- ad_id / ad_name
- spend
- impressions
- clicks
- cpm
- ctr
- cvr

backend_conversion_fact
- date
- ad_id
- adset_id
- region_tier
- region_segment
- lead_count
- booking_count
- show_count
- paid_course_count
- gmv

creative_label_dim
- ad_id / creative_id
- creative_type
- production_month
- creative_source
- is_high_potential
- is_enabled
```

## 下一步建议

本交接包可以先发给开发同事评审。不要继续在本分支扩大字段整理，除非开发反馈确认要走哪条路线：

- 路线 A：用 BI 透视导出做临时 P0。
- 路线 B：追底层 SQL/回写表。
- 路线 C：直接接 Meta API + 内部REDACTED_CONVERSION表，BI 只作为校验和业务看板。

我的建议是路线 B 或 C，路线 A 只能作为短期验证。
