# Data Contract

This package reads local sanitized sample files only. The registry points to normalized CSV files that preserve the production field shape without carrying real business rows.

## Registry

`data/sample_registry.json`

Required fields:

- `schema_version`
- `status`
- `generated_at`
- `data_as_of`
- `source_manifest`
- `coverage`
- `facts`
- `known_gaps`

`facts` maps logical module names to local CSV paths:

- `fb_channel_daily_monitor`
- `fb_link_type_daily_monitor`
- `fb_material_chain_metrics`
- `fb_target_achievement`
- `fb_new_old_plan_waste`
- `fb_adgroup_tags`

## Normalized Facts

### Channel Daily Monitor

Long-format metric table:

- `task`
- `report`
- `period`
- `business_date`
- `group`
- `metric`
- `value`
- `numeric_value`
- `source_path`
- `source_row`
- `source_col`

### Link Type Daily Monitor

Same long-format shape as channel daily monitor. `group` represents link type.

### Material Chain Metrics

Wide-format material table. Required columns include:

- `period`
- `投放平台`
- `区域等级`
- `投放账户`
- `广告组ID`
- `上线日期`
- `广告ID`
- `广告名称`
- `素材类型`
- `主投 | 消耗`
- `例子数`
- `约课数`
- `例子成本`
- `约课成本`
- `约课率`
- `当月GMV`
- `当月ROI2`
- `滚动GMV`
- `滚动ROI2`
- `空耗金额`
- `空耗金额占比`
- `creative_launch_month`

### Target Achievement

MTD target table. Required columns include:

- `period`
- `data_as_of`
- `主投`
- `辅投`
- `平台`
- `区域等级`
- `全月预算`
- `消耗MTD`
- `MTD消耗进度`
- `主投例子月目标`
- `主投例子数`
- `主投例子MTD达成率`
- `例子成本目标`
- `例子成本`
- `约课成本目标`
- `约课成本`
- `当月GMV目标`
- `当月GMV达成`
- `当月GMV达成率`
- `主投当月ROI目标`
- `主投当月ROI达成`

### New Old Plan Waste

Required columns include:

- `账户类型`
- `周次`
- `汇总 | 消耗`
- `汇总 | 成效`
- `汇总 | 成效成本`
- `新计划 | 消耗`
- `新计划 | 成效`
- `新计划 | 成效成本`
- `老计划 | 消耗`
- `老计划 | 成效`
- `老计划 | 成效成本`
- `广告组维度 | 空耗金额`
- `广告组维度 | 空耗金额占比`
- `广告维度 | 空耗金额`
- `广告维度 | 空耗金额占比`

### Adgroup Tags

Aggregated adgroup-level table only. It must not contain user-level rows.

Required columns include:

- `区域等级`
- `三大区域`
- `渠道一级分类`
- `渠道二级分类`
- `末次渠道名称`
- `投放账户`
- `广告组名称`
- `row_count`
- `is_enable`
- `is_high_potential`

