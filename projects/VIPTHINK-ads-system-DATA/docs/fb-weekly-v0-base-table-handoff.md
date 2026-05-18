# FB 自动周报 V0 底表交付说明

生成日期：2026-05-18

## 当前产物

已基于 SmartBI 中 4 张 Facebook/Meta 投放相关 `SPREADSHEET_REPORT`，生成 V0 自动周报校准底表。

Excel 底表：

```text
runtime/private/fb_weekly_v0/fb_weekly_v0_base_table.xlsx
```

生成脚本：

```text
scripts/generate_fb_weekly_v0_base.py
```

SmartBI 临时导出配置：

```text
runtime/private/fb_weekly_v0/smartbi_fb_weekly_v0_tasks.json
```

## 使用的 SmartBI 报表

| 任务 | 报表 | 用途 | 导出状态 |
|---|---|---|---|
| `fb_material_chain_metrics` | REDACTED_REPORT_A | creative_asset维度表现 / 空耗候选 | 已导出 |
| `fb_channel_daily_monitor` | REDACTED_REPORT_B | 渠道与区域日监控 | 已导出 |
| `fb_link_type_daily_monitor` | REDACTED_REPORT_C | 链路类型日监控 | 已导出 |
| `fb_hk_mo_test_report` | REDACTED_REPORT_D | REDACTED_REGION_A/非REDACTED_REGION_A策略测试 | 已导出 |

说明：

- 首次导出 `REDACTED_REPORT_D` 时遇到一次网络连接重置；重试后成功。
- 未处理 `REDACTED_REPORT_K/REDACTED_REPORT_L`，因为它们是 `SIMPLE_REPORT`，需要单独 row guard。

## Excel Sheet 说明

| Sheet | 行数 | 用途 | 你需要校准什么 |
|---|---:|---|---|
| `source_reports` | 5 | 记录 4 张来源报表和 xlsx 路径 | 确认报表是否就是周报 V0 应使用的来源 |
| `report_structures` | 5 | 记录 workbook 结构、行列数、表类型 | 确认这些表都按透视/格式化表处理是否合理 |
| `weekly_base_sections` | 8 | 周报底稿模块结构 | 确认 V0 周报模块是否够用 |
| `field_mapping_draft` | 78 | 字段分类与周报模块映射草案 | 重点校准字段归类、周报模块、是否可用于 V0 |
| `material_wide` | 2099 | creative_asset维度宽表，保留原始行和展开字段 | 校准creative_asset、广告对象、前后端指标字段 |
| `channel_daily_long` | 1506 | 渠道日监控长表：日期 x 分组 x 指标 | 校准分组名称、指标含义、是否用于整体/区域模块 |
| `link_type_daily_long` | 496 | 链路类型长表：日期 x 链路 x 指标 | 校准 H5/WhatsApp/表单链路字段 |
| `hkmo_strategy_wide` | 71 | REDACTED_REGION_A/非REDACTED_REGION_A策略测试宽表 | 校准策略、REDACTED_CREATIVE_TAGS、内部REDACTED_CONVERSION指标 |

## 当前字段口径状态

已能自动抽取：

- 时间窗口：开始日期、结束日期。
- 渠道/链路：FBREDACTED_REGION_AKOL、FBREDACTED_REGION_A常规、REDACTED_PLATFORM_GROUP_A、REDACTED_REGION_AH5、REDACTED_REGION_AWhatsApp、REDACTED_REGION_A表单等。
- creative_asset/广告对象：广告名称、广告ID、广告组ID、REDACTED_CREATIVE_TYPE、投放账户。
- 前端指标：曝光、点击、CPM、CTR、CVR、IPM、消耗。
- 后端指标：REDACTED_CONVERSION_A_COUNT、REDACTED_CONVERSION_B_COUNT、REDACTED_CONVERSION_C、REDACTED_PAID_EVENT、GMV、ROI2。
- 派生指标：REDACTED_CONVERSION_A_COST、REDACTED_CONVERSION_B_COST、REDACTED_CONVERSION_A_TO_B_RATE、REDACTED_CONVERSION_B_TO_C_RATE、REDACTED_CONVERSION_C_TO_PAID_RATE、当月REDACTED_CONVERSION率、滚动REDACTED_CONVERSION率、空耗金额、空耗占比。

仍需你校准：

- 哪些字段是周报必填，哪些只是辅助字段。
- `成效`、`成效成本` 是否等同于 Meta 成效口径，还是 BI 派生口径。
- `消耗` 与 `消耗(不含CPT)` 是否都要保留。
- `当月ROI2`、`滚动ROI2` 哪个用于 V0 周报。
- `REDACTED_REGION_AKOL`、`REDACTED_REGION_A常规`、`REDACTED_REGION_GROUP_A常规` 等分组是否为正式周报分组。
- `H5`、`WhatsApp`、`表单` 是否作为链路维度进入 V0。
- REDACTED_CREATIVE_FIELDS里哪些属于 Meta 对象，哪些属于REDACTED_INTERNAL_CREATIVE_TAG。

## 下次复跑命令

导出 SmartBI 报表：

```bash
cd <local-tools>
source <local-secret-env>
python3 scripts/smartbi_cli.py run --config ../投放系统demo/runtime/private/fb_weekly_v0/smartbi_fb_weekly_v0_tasks.json --task fb_material_chain_metrics --overwrite --json
python3 scripts/smartbi_cli.py run --config ../投放系统demo/runtime/private/fb_weekly_v0/smartbi_fb_weekly_v0_tasks.json --task fb_channel_daily_monitor --overwrite --json
python3 scripts/smartbi_cli.py run --config ../投放系统demo/runtime/private/fb_weekly_v0/smartbi_fb_weekly_v0_tasks.json --task fb_link_type_daily_monitor --overwrite --json
python3 scripts/smartbi_cli.py run --config ../投放系统demo/runtime/private/fb_weekly_v0/smartbi_fb_weekly_v0_tasks.json --task fb_hk_mo_test_report --overwrite --json
```

重新生成 Excel 底表：

```bash
cd <project-root>
uv run --with pandas --with openpyxl python scripts/generate_fb_weekly_v0_base.py
```

## 下一确认闸口

请先校准 `field_mapping_draft` 和 4 张数据 sheet。

建议你优先确认：

1. `field_mapping_draft` 中哪些字段进入 V0 周报。
2. `material_wide` 中广告/creative_asset维度是否已经满足creative_asset表现模块。
3. `channel_daily_long` 是否能作为整体达成和区域表现来源。
4. `hkmo_strategy_wide` 是否纳入 V0，还是留给 V1。
5. V0 周报输出是否继续生成 Markdown，还是也生成 Excel 版周报。
