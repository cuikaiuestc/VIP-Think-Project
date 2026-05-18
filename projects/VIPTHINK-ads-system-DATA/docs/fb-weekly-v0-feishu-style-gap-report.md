# FB 自动周报 V0 飞书样式验收表说明

生成日期：2026-05-18

## 当前产物

- Excel：`runtime/private/fb_weekly_v0/FB自动周报V0_飞书样式验收表.xlsx`
- 本版目标：直接按飞书 FB 周报最终展示块生成验收表，不再让业务从工程细表里筛选。

## 对应飞书位置

| Sheet | 对应飞书周报部分 | 状态 |
|---|---|---|
| `01_FB整体达成` | FB-REDACTED_PRODUCT_LINE -> 整体达成（飞书 sheet: 1AsIod / SkZ0x7） | 结构已对齐；目标、时间进度、ROI2待接入。 |
| `02_REDACTED_SEGMENT_STRATEGY_DATA` | FB-REDACTED_PRODUCT_LINE -> REDACTED_SEGMENT_STRATEGY_DATA（飞书 sheet: KHAXJJ） | 结构已对齐；使用 `REDACTED_REPORT_D` 填充REDACTED_REGION_A策略数据。 |
| `03_REDACTED_CREATIVE_VIEW` | FB-REDACTED_PRODUCT_LINE -> REDACTED_CREATIVE_VIEW / REDACTED_CREATIVE_WASTE_VIEW（飞书 sheet: iuZlU8） | 结构已对齐；使用 `REDACTED_REPORT_A` 按消耗Top展示。 |
| `04_REDACTED_RECENT_CREATIVE_VIEW` | FB-REDACTED_PRODUCT_LINE -> REDACTED_RECENT_CREATIVE_VIEW（飞书 sheet: soaSkB） | 结构已对齐；REDACTED_CREATIVE_PRODUCTION_PERIOD/KOL/预览链接待接入REDACTED_CREATIVE_ASSET_TABLE。 |
| `05_空耗率` | FB-REDACTED_PRODUCT_LINE -> 空耗率（飞书 sheet: tuWkcq） | 结构已对齐；新老计划/广告组维度空耗字段待接入。 |
| `06_REDACTED_REGION_GROUP数据` | FB-REDACTED_PRODUCT_LINE -> REDACTED_REGION_GROUP 数据（飞书 sheet: VpReZd / Y266Lr / 1Virzt） | 结构已对齐；区域映射、目标、语言维度待校准。 |
| `07_定位问题与缺口` | 本次重做定位：为何上一版没有匹配飞书截图预期 | 解释上一版未达预期的原因和本版修正点。 |

## 上一版没有匹配预期的原因

1. 输出视角错了：上一版是 SmartBI 底表整理，不是飞书最终汇报块。
2. 模板锚点错了：没有把飞书正文中的 `1AsIod / SkZ0x7 / KHAXJJ / iuZlU8 / soaSkB / tuWkcq / VpReZd` 作为目标结构。
3. 字段分组错了：整体达成、REDACTED_REGION_A分策略、REDACTED_CREATIVE_VIEW、REDACTED_RECENT_CREATIVE_VIEW、空耗率、REDACTED_REGION_GROUP应拆成独立汇报块。
4. 缺口表达错了：缺少目标、ROI2、creative_asset链接、新老计划等字段时，上一版没有在最终展示结构中显式标注。

## 需要你验收/校准

- `目标字段`：MTD目标、达成率、时间进度是否来自另一个目标表。
- `区域映射`：SmartBI分组里的 `REDACTED_PLATFORM_GROUP_A/REDACTED_PLATFORM_GROUP_B/REDACTED_PLATFORM_GROUP_C/FBREDACTED_REGION_CKOL` 是否对应飞书的REDACTED_REGION_GROUP_A、REDACTED_REGION_B常规、REDACTED_REGION_BKOL等块。
- `消耗口径`：周报采用消耗、消耗不含CPT，还是含CPT。
- `ROI2口径`：整体达成使用当月ROI2还是滚动ROI2。
- `REDACTED_CREATIVE_ASSET_FIELDS`：REDACTED_RECENT_CREATIVE_VIEW需要的 KOL、REDACTED_CREATIVE_PRODUCTION_PERIOD、预览链接是否有独立creative_asset表。
- `空耗口径`：新计划/老计划、广告组维度/广告维度空耗率是否有专项BI报表。
