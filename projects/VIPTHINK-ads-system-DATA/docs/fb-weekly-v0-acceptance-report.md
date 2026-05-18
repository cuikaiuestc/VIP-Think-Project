# FB 自动周报 V0 验收表说明

生成日期：2026-05-18

## 当前产物

- Excel：`runtime/private/fb_weekly_v0/FB自动周报V0_验收表.xlsx`
- 目标：直接给业务验收的汇报表，不再让用户阅读工程细底表。
- 范围：只做 FB，不生成投放师观点，不自动写原因分析，不给调优建议。

## Sheet 对应关系

| Sheet | 对应飞书周报部分 | 行数 | 说明 |
|---|---|---:|---|
| `目录_对应飞书位置` | 飞书周报目录对照 | 7 | 目录对照与校准提示。 |
| `FB整体达成` | FB-REDACTED_PRODUCT_LINE -> 整体达成 | 7 | 目标字段未接入，保留目标待接入。 |
| `FB渠道日监控` | FB-REDACTED_PRODUCT_LINE -> 整体达成 / REDACTED_SEGMENT_STRATEGY_DATA | 119 | 由渠道日监控长表整理成汇报表。 |
| `FB链路类型日监控` | FB-REDACTED_PRODUCT_LINE -> REDACTED_SEGMENT_STRATEGY_DATA | 51 | 由链路类型日监控整理为日期 x 链路类型。 |
| `FBcreative_asset表现` | FB-REDACTED_PRODUCT_LINE -> REDACTED_CREATIVE_VIEW / REDACTED_RECENT_CREATIVE_VIEW / REDACTED_REGION_GROUP 数据 -> REDACTED_CREATIVE_TYPE数据 | 100 | 按消耗排序保留Top 100有效creative_asset/广告记录。 |
| `FB空耗高成本候选` | FB-REDACTED_PRODUCT_LINE -> REDACTED_CREATIVE_VIEW -> REDACTED_CREATIVE_WASTE_VIEW / 空耗率 | 100 | 只列候选标签，不输出建议。 |
| `FBREDACTED_SEGMENT_TEST` | FB-REDACTED_PRODUCT_LINE -> REDACTED_SEGMENT_STRATEGY_DATA / REDACTED_REGION_GROUP 数据 | 64 | 保留区域/策略/REDACTED_CREATIVE_TAGS，供验收是否纳入V0。 |
| `数据缺口与人工补充` | 周报人工观点和口径补充区 | 8 | 集中列出口径缺口和人工补充位。 |

## 需要验收/校准

1. `FB整体达成`：目标字段和达成率来源是否另有目标表。
2. `FB渠道日监控`：分组名称是否就是周报正式分组，消耗是否采用含CPT或不含CPT。
3. `FBcreative_asset表现`：REDACTED_CREATIVE_TYPE、广告名称、广告ID、广告组ID是否够用作周报creative_asset展示。
4. `FB空耗高成本候选`：空耗阈值和成效/成效成本口径。
5. `FBREDACTED_SEGMENT_TEST`：是否进入V0，还是留到V1策略分析。

## 当前不能自动生成

- 投放师观点、原因分析、下周动作。
- 目标值和达成率，除非接入目标表。
- 空耗是否应暂停/放量的最终判断。
- REDACTED_CREATIVE_STRATEGY_TAGS的业务含义。
