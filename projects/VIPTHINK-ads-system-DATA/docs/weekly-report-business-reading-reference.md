# 投放周报业务解读参考

来源：用户提供的内部投放周会 Feishu 文档；原始文档名称不进入 GitHub。

读取方式：

- 使用 `lark-cli docs +fetch --api-version v2 --as user` 读取文档结构。
- 使用 `lark-cli sheets +info/+read --as user` 读取嵌入表格元信息和 FB 段落关键 sheet。
- 原始读取结果仅保存在 `runtime/private/lark_docs/`，本文只保留脱敏后的业务结构和字段设计启发。

## 当前产物

这份周报对本项目的价值，不是提供一份固定模板，而是暴露投放团队如何解释数据：

1. 先看整体目标达成。
2. 再按渠道、地区、策略、计划、新老creative_asset、REDACTED_CREATIVE_TYPE、广告对象拆解。
3. 找出问题所在的链路指标，例如量少、REDACTED_CONVERSION_B_RATE低、CTR 低、CVR 未恢复、空耗高。
4. 给出原因假设，例如creative_asset衰退、假期流量质量、出价难跑、搜索结果异常、落地页需要测试。
5. 最后落到下周动作，例如复制老计划、测新creative_asset、暂停高成本词、引入自动化删creative_asset、更新落地页。

所以后续“BI 原始数据自动生成周报”不能只做字段字典；必须同时产出一套可解释的周报生成规则。

## 周报结构模式

| 层级 | 周报中的表现 | 自动化含义 |
|---|---|---|
| 总览 | 投放整体、汇总关键数据、整体数据、REDACTED_REGION_A/非REDACTED_REGION_A | 先生成整体 dashboard 和目标达成摘要 |
| 渠道 | 小红书、FB、谷歌、广点通、抖音、ASA | 每个渠道有独立诊断模板 |
| 地区 | REDACTED_REGION_A、非REDACTED_REGION_A、REDACTED_REGION_GROUP_A、REDACTED_REGION_B | 地区是核心控制维度，不应只做总量 |
| 策略/链路 | 分策略、链路类型、表单、REDACTED_FLAG_B、REDACTED_FLAG_A、KOL、常规 | 需要保留内部策略标签，不是 Meta 原始字段 |
| creative_asset | REDACTED_CREATIVE_TYPE、广告名称、REDACTED_RECENT_CREATIVE_VIEW、creative_asset空耗 | creative_asset维度是 FB 周报核心 |
| 行动 | 本周调优动作、暂停、复制、提需、落地页测试 | 周报最终要生成操作建议，不只是结论 |

## FB 段落的业务读数方式

FB 周报段落的核心问题不是“Meta 数据怎么样”，而是：

```text
FB 是否完成目标
-> 哪个地区/策略/链路拖累
-> 哪些creative_asset/广告在跑量或空耗
-> 哪些REDACTED_CREATIVE_TYPE符合REDACTED_CONVERSION_B_COST目标
-> 下周要复制、暂停、提需或继续测试什么
```

已读取到的 FB 关键表格线索：

| 表格语境 | 核心字段 | 解读用途 |
|---|---|---|
| 整体达成 | MTD目标、达成、达成率、REDACTED_CONVERSION_A、REDACTED_CONVERSION_B、REDACTED_CONVERSION_C、REDACTED_PAID_EVENT、GMV、ROI2 | 判断是否达成阶段目标 |
| 分策略数据 | 地区、链路、REDACTED_FLAG_B、REDACTED_FLAG_A、cpm、ctr、cvr、消耗、REDACTED_CONVERSION_A_COUNT、REDACTED_CONVERSION_A_COST、REDACTED_CONVERSION_B_COST、REDACTED_CONVERSION_A_TO_B_RATE、REDACTED_CONVERSION_B_TO_C_RATE、REDACTED_CONVERSION_C_TO_PAID_RATE、REDACTED_CONVERSION_A_TO_PAID_RATE | 判断策略组合是否有效 |
| creative_asset维度空耗 | 地区、REDACTED_CREATIVE_TYPE、广告名称、cpm、ctr、cvr、消耗、REDACTED_CONVERSION_A_COUNT、REDACTED_CONVERSION_A_COST、REDACTED_CONVERSION_B_COST、ROI2 | 识别creative_asset层面的有效/空耗 |
| REDACTED_RECENT_CREATIVE_VIEW | REDACTED_CREATIVE_PRODUCTION_PERIOD、KOL、上线日期、预览链接、投放地区、REDACTED_CREATIVE_TYPE、广告名称、播放进度、消耗、REDACTED_CONVERSION_A、REDACTED_CONVERSION_B_COST | 追踪REDACTED_RECENT_CREATIVE_VIEW和creative_asset生命周期 |
| 空耗率 | 账户类型、周次、汇总、新计划、老计划、广告组维度、广告维度、消耗、成效、成效成本 | 判断空耗来自新计划、老计划、广告组还是广告 |
| 区域REDACTED_CREATIVE_TYPE | 语言、REDACTED_CREATIVE_TYPE、CTR、CPM、CVR、曝光、点击、消耗、REDACTED_CONVERSION_COUNT、REDACTED_CONVERSION成本、REDACTED_CONVERSION_B_COST、REDACTED_CONVERSION_B_RATE、REDACTED_CONVERSION_C率、REDACTED_PAID_EVENT、GMV、ROI2 | 判断不同地区适合什么REDACTED_CREATIVE_TYPE |

周报文字里的 FB 业务判断示例，抽象成规则后大致是：

| 观察 | 解释 | 动作 |
|---|---|---|
| 某REDACTED_CREATIVE_TYPE符合目标REDACTED_CONVERSION_B_COST | 可继续放量或作为creative_asset方向 | 增加同类creative_asset供给 |
| 某REDACTED_CREATIVE_TYPE排序靠后且成本不达标 | 不作为当前优先方向 | 暂停或降权测试 |
| 新老计划空耗高 | 需要定位空耗来自计划、广告组还是广告 | 关停/复查高空耗对象 |
| 跑量creative_asset主要来自老creative_asset | 存在creative_asset衰退风险 | 复制老计划并补充新creative_asset |
| CTR/CVR 低 | 创意或落地页吸引力不足 | 调整creative_asset/落地页/文案 |

## 对 BI 字段字典的启发

字段字典不能只按来源分为 Meta / 内部 / 派生，还需要增加“周报用途”。

建议字段字典增加这些列：

| 字段字典列 | 作用 |
|---|---|
| 周报模块 | 整体达成 / FB 日监控 / creative_asset空耗 / 地区REDACTED_CREATIVE_TYPE / 漏斗 |
| 业务动作 | 放量 / 暂停 / 复查 / 提需 / 复制计划 / 落地页测试 |
| 判断方向 | 越高越好 / 越低越好 / 需与目标比较 / 需与上周比较 |
| 阈值来源 | 固定阈值 / 目标表 / 历史分位 / 人工确认 |
| 归因粒度 | 渠道 / 地区 / 策略 / 计划 / 广告组 / 广告 / creative_asset |
| 是否可自动解释 | 是 / 部分 / 否 |

## 对自动生成周报的方案启发

自动周报不应一开始追求“完全替代投放师判断”。更合理的轻量版是：

```text
BI 原始数据
-> 标准化字段与口径
-> 生成固定结构的周报底稿
-> 规则引擎给出候选异常和候选动作
-> 投放师补充原因假设与最终动作
```

### V0 应生成什么

| 模块 | 自动生成内容 | 人工仍需确认 |
|---|---|---|
| 整体达成 | 目标、达成、达成率、环比/周比 | 目标是否正确 |
| FB creative_asset | Top 消耗、Top REDACTED_CONVERSION_A、Top 空耗、高REDACTED_CONVERSION_B_COSTcreative_asset | 是否真的要停/放量 |
| 地区策略 | REDACTED_REGION_A、REDACTED_REGION_GROUP_A、REDACTED_REGION_B等分组表现 | 地区策略背景 |
| REDACTED_CREATIVE_TYPE | 图片、KOL、AI视频、深蓝视频等表现排序 | creative_asset分类是否准确 |
| 异常 | 量少、成本升高、CTR/CVR 低、空耗高 | 原因假设 |
| 下周动作草稿 | 暂停候选、复制候选、提需候选、落地页测试候选 | 最终动作与优先级 |

### 需要的输入

| 输入 | 来源 |
|---|---|
| BI 报表原始数据 | SmartBI |
| Meta 对象字段 | Meta readonly adapter 或投放师下载表 |
| 目标表 | BI 或人工维护 |
| REDACTED_CREATIVE_TAGS | BI 内部字段/creative_asset表 |
| 地区/策略标签 | BI 内部字段 |
| 上周/本月基线 | BI 历史数据 |
| 本周人工动作 | 投放师补充或任务系统 |

## 当前不能自动化的部分

这份周报里有些判断来自 BI 外部：

- 搜索结果排查。
- 负面联想词检查。
- 落地页视觉/文案判断。
- creative_asset提需方向。
- KOL 达人邀约。
- 假期、流量质量等背景解释。

这些不能从 BI 原始数据直接生成，只能在自动周报里作为“需要人工补充”的原因槽位。

## 对下一阶段 BI 盘点的影响

下一阶段字段盘点应优先覆盖这些报表能力：

1. `REDACTED_REPORT_A`：用于creative_asset后端REDACTED_CONVERSION和creative_asset空耗。
2. `REDACTED_REPORT_B`：用于 FB 日监控和目标节奏。
3. `REDACTED_REPORT_C`：用于链路类型拆解。
4. `REDACTED_REPORT_D`：用于区域/策略测试。
5. `REDACTED_REPORT_K/REDACTED_REPORT_L`：用于REDACTED_PAGE_FLOW，需先做 `SIMPLE_REPORT` row guard。

优先字段：

- 日期：开始日期、结束日期、快照日期、周次、周期。
- 渠道：REDACTED_DIM_PLATFORM、渠道、FB、REDACTED_PLATFORM_VALUE。
- 地区：REDACTED_REGION_A、非REDACTED_REGION_A、REDACTED_REGION_GROUP_A、REDACTED_REGION_B、REDACTED_DIM_REGION_TIER、REDACTED_DIM_REGION_SEGMENT。
- 对象：投放账户、计划、广告组ID、广告ID、广告名称。
- creative_asset：creative_asset、REDACTED_CREATIVE_TYPE、REDACTED_CREATIVE_PRODUCTION_PERIOD、上线日期、KOL、REDACTED_CREATIVE_SOURCE、预览链接。
- 前端指标：曝光、点击、CTR、CPM、CVR、消耗。
- 后端指标：REDACTED_CONVERSION_A、REDACTED_CONVERSION_B、REDACTED_CONVERSION_C、REDACTED_PAID_EVENT、GMV、ROI2。
- 派生指标：REDACTED_CONVERSION_A_COST、REDACTED_CONVERSION_B_COST、REDACTED_CONVERSION成本、REDACTED_CONVERSION_A_TO_B_RATE、REDACTED_CONVERSION_B_TO_C_RATE、REDACTED_CONVERSION_C_TO_PAID_RATE、REDACTED_CONVERSION_A_TO_PAID_RATE、空耗率。

## 下一确认闸口

进入“自动周报方案设计”前，需要确认：

1. 自动周报先服务哪个范围：只做 FB，还是覆盖小红书/谷歌/广点通/抖音/ASA？
2. V0 是否接受“自动生成底稿 + 人工补原因/动作”，而不是全自动定稿？
3. 周报目标表从哪里来：BI 现有报表、人工 Excel，还是投放师维护？
4. REDACTED_CREATIVE_TAGS和策略标签以 BI 字段为准，还是需要另接creative_asset管理表？
5. 输出形态优先是 Markdown、Feishu 文档、Excel，还是本地 HTML 报告？
