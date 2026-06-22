# 小红书聚光 Read-only 数据契约 v0

生成日期：2026-05-20

## 目标

本契约基于 2026-05-20 小红书聚光 API read-only spike 的已验证结果，收敛小红书投放数据进入后续数据契约设计的 v0 边界。

本文件只定义 read-only 数据对象、P0/P0.5 事实表建议、字段映射、Architecture Decision 和 Need Confirmation。它不是生产同步方案，不修 SDK，不创建数据库 migration，不修改 A 线素材数据底座 `material_dim` / `material_ad_mapping` 契约。

## 依据

已验证产物：

- Spike 输出：`outputs/xiaohongshu/xhs_api_readonly_spike.md`
- Architecture handoff：`docs/handoff/2026-05-20-xhs-readonly-spike-architecture-handoff.md`
- Spike 程序：`tools/xhs-readonly-spike/main.go`

已成功读取：

| 接口 / 层级 | 结果 |
|---|---|
| campaign list | 可读，本页返回 10 条 |
| unit list | 可读，本页返回 10 条 |
| offline report advertiser | 可读，本页返回 1 条，总数 1 |
| offline report campaign | 可读，本页返回 10 条，总数 32 |
| offline report unit | 可读，本页返回 10 条，总数 32 |
| realtime report advertiser | 可读 |
| realtime report campaign | 可读，本页返回 10 条 |
| realtime report unit | 可读，本页返回 10 条 |
| realtime report creativity | 可读，本页返回 10 条 |

未读通但已定位原因：

| 接口 / 层级 | 当前状态 | 合同影响 |
|---|---|---|
| account balance | SDK/response schema mismatch | 不纳入 P0 投放表现事实表 |
| creativity search | 平台实际返回数据，但 SDK 字段类型不匹配 | 创意维表 / 创意详情放 P0.5 |
| offline report creativity | SDK/response schema mismatch 或接口路径/权限待确认 | 离线创意事实表放 P0.5 |

## 非目标

- 不做生产同步。
- 不修 `github.com/bububa/spotlight-mapi` SDK。
- 不调用任何创建、编辑、状态修改、删除、转化回传接口。
- 不读取、打印或记录 token、refresh token、app secret、完整 advertiser_id。
- 不修改 `material_dim` / `material_ad_mapping`。
- 不把 `note_id` 直接定义为 `material_id`。
- 不把 SDK 模型中存在但未用当前账号读通的字段视为已验证字段。

## 已验证对象层级

当前可进入数据契约的对象层级：

```text
advertiser
  -> campaign
      -> unit
          -> creativity
          -> keyword (搜索推广 / 关键词场景，未作为 P0 验证重点)
```

层级解释：

| 层级 | 小红书字段 | v0 判断 |
|---|---|---|
| 广告主 | `advertiser_id` | 账户级调用必需，P0 保留为事实表维度 |
| 计划 | `campaign_id` | 已通过 list 和 offline/realtime report 验证，P0 |
| 单元 | `unit_id` / unit list 中 `id` | 已通过 list 和 offline/realtime report 验证，P0 |
| 创意 | `creative_id` / `creativity_id` | realtime creativity 已验证，离线创意和 search 仍有 schema 缺口，P0.5 |
| 笔记 | `note_id` | 可作为素材映射候选线索，不能在 v0 直接进入 A 线契约 |
| 关键词 | `keyword_id` / `keyword` | SDK 模型支持，当前未作为 P0 读通对象，P0.5 / P1 |

## P0/P0.5 表建议

| 表名 | 优先级 | 类型 | 进入条件 | 说明 |
|---|---:|---|---|---|
| `xhs_advertiser_daily_fact` | P0 | fact | 已读通 offline/realtime advertiser | 账户级日汇总，用于总览和校验 |
| `xhs_campaign_daily_fact` | P0 | fact | 已读通 campaign list、offline/realtime campaign report | 计划级日事实表，第一版主表 |
| `xhs_unit_daily_fact` | P0 | fact | 已读通 unit list、offline/realtime unit report | 单元级日事实表，第一版主表 |
| `xhs_creativity_realtime_fact` | P0.5 | fact | 已读通 realtime creativity report | 可用于创意层级探索，但不作为稳定离线事实主表 |
| `xhs_creativity_daily_fact` | P0.5 | fact | offline creativity report 修通或 API 同事确认路径/权限 | 创意级离线日事实表，暂不进入 P0 |
| `xhs_creativity_dim` | P0.5 | dim | creativity search schema mismatch 处理后 | 创意详情维表，承接 `note_id`、组件、图片、跳转等字段 |
| `xhs_keyword_daily_fact` | P0.5 / P1 | fact | 关键词报表按搜索推广场景验证后 | 不阻塞 P0 campaign/unit 闭环 |

P0 默认只覆盖已经读通的账户、计划、单元层级。创意层级虽然实时接口已读通，但离线创意与创意详情仍未稳定，因此不应作为 v0 强依赖。

## 表 1：`xhs_advertiser_daily_fact`

中文名：小红书广告主日事实表

用途：

账户级消耗和核心指标汇总，用于总览、对账和下钻前的日级基准。

推荐主键：

```text
channel + advertiser_id + stat_date + data_source
```

字段建议：

| 字段 | 中文名 | P0/P0.5 | 类型建议 | 来源 | 说明 |
|---|---|---:|---|---|---|
| `channel` | 渠道 | P0 | string | 系统常量 | 固定为 `xiaohongshu` 或统一渠道枚举 |
| `advertiser_id` | 广告主 ID | P0 | string | env / API request | 对外展示必须脱敏 |
| `stat_date` | 统计日期 | P0 | date | report `time` / request date | 默认使用自然日 |
| `data_source` | 数据来源 | P0 | enum | 系统生成 | 建议 `offline` / `realtime` |
| `fee` | 消费 | P0 | decimal | report | 小红书原始字段，金额单位需确认 |
| `impression` | 曝光 | P0 | integer | report | 已在 SDK 指标模型中存在 |
| `click` | 点击 | P0 | integer | report | 已在 SDK 指标模型中存在 |
| `ctr` | 点击率 | P0 | decimal | report | 建议保留平台返回值，同时允许分析层重算 |
| `cpm` | 千次曝光成本 | P0 | decimal | report | 建议保留平台返回值 |
| `acp` | 平均点击成本 | P0 | decimal | report | 小红书 SDK 字段，类似 CPC |
| `raw_metric_payload_hash` | 原始指标摘要 | P0.5 | string | 系统生成 | 用于对账，不保存敏感原文 |
| `fetched_at` | 拉取时间 | P0 | datetime | 系统生成 | read-only 获取时间 |

## 表 2：`xhs_campaign_daily_fact`

中文名：小红书计划日事实表

用途：

计划级投放表现事实表。P0 主表。

推荐主键：

```text
channel + advertiser_id + campaign_id + stat_date + data_source
```

字段建议：

| 字段 | 中文名 | P0/P0.5 | 类型建议 | 来源 | 说明 |
|---|---|---:|---|---|---|
| `channel` | 渠道 | P0 | string | 系统常量 | 固定为小红书渠道枚举 |
| `advertiser_id` | 广告主 ID | P0 | string | request/report | 必填，输出需脱敏 |
| `campaign_id` | 计划 ID | P0 | string | campaign list / report | 稳定 ID |
| `campaign_name` | 计划名称 | P0 | string | campaign list / report | 展示和核对字段，不做主键 |
| `stat_date` | 统计日期 | P0 | date | report `time` | 日事实表主粒度 |
| `data_source` | 数据来源 | P0 | enum | 系统生成 | `offline` / `realtime` |
| `campaign_filter_state` | 计划状态 | P0.5 | integer | campaign list / realtime base dto | 状态枚举待确认 |
| `campaign_create_time` | 计划创建时间 | P0.5 | datetime | campaign list / realtime base dto | 用于生命周期分析 |
| `marketing_target` | 营销诉求 | P0.5 | integer/string | campaign list / report split | 枚举需 API/业务确认 |
| `placement` | 广告类型 | P0.5 | integer/string | campaign list / report split | 信息流/搜索/全站智投等 |
| `optimize_target` | 优化目标 | P0.5 | integer/string | campaign list / report split | 需确认业务映射 |
| `promotion_target` | 投放标的 | P0.5 | integer/string | campaign list / report split | 笔记/商品/落地页/直播间等 |
| `bidding_strategy` | 出价方式 | P0.5 | integer/string | campaign list / report split | 手动/自动等 |
| `fee` | 消费 | P0 | decimal | report | 统一指标层可映射为 spend |
| `impression` | 曝光 | P0 | integer | report | 核心指标 |
| `click` | 点击 | P0 | integer | report | 核心指标 |
| `ctr` | 点击率 | P0 | decimal | report | 核心指标 |
| `cpm` | 千次曝光成本 | P0 | decimal | report | 核心指标 |
| `acp` | 平均点击成本 | P0 | decimal | report | 小红书原始字段 |
| `interaction` | 互动量 | P0.5 | integer | report | 进入业务分析前需确认口径 |
| `leads` | 表单提交 | P0.5 | integer | report | 客资场景优先确认 |
| `valid_leads` | 有效表单 | P0.5 | integer | report | 需确认是否依赖回传 |
| `message_consult` | 私信咨询数 | P0.5 | integer | report | 私信场景字段 |
| `fetched_at` | 拉取时间 | P0 | datetime | 系统生成 | 审计字段 |

## 表 3：`xhs_unit_daily_fact`

中文名：小红书单元日事实表

用途：

单元级投放表现事实表。P0 主表。当前最适合作为 Meta `adset` 近似层的候选，但命名上建议保留小红书原生 `unit`。

推荐主键：

```text
channel + advertiser_id + unit_id + stat_date + data_source
```

字段建议：

| 字段 | 中文名 | P0/P0.5 | 类型建议 | 来源 | 说明 |
|---|---|---:|---|---|---|
| `channel` | 渠道 | P0 | string | 系统常量 | 固定为小红书渠道枚举 |
| `advertiser_id` | 广告主 ID | P0 | string | request/report | 必填 |
| `campaign_id` | 计划 ID | P0 | string | unit list / report | 上级计划 |
| `unit_id` | 单元 ID | P0 | string | unit list `id` / report `unit_id` | 需确认二者完全等价 |
| `unit_name` | 单元名称 | P0 | string | unit list / report | 展示和核对字段 |
| `stat_date` | 统计日期 | P0 | date | report `time` | 日事实表主粒度 |
| `data_source` | 数据来源 | P0 | enum | 系统生成 | `offline` / `realtime` |
| `unit_enable` | 单元启停状态 | P0.5 | integer | unit list / realtime base dto | 枚举待确认 |
| `unit_create_time` | 单元创建时间 | P0.5 | datetime | unit list / realtime base dto | 生命周期分析 |
| `event_bid` | 出价 | P0.5 | decimal/integer | unit list / realtime base dto | 单位需确认 |
| `target_type` | 定向类型 | P0.5 | integer/string | unit list | 通投/智能/高级定向等 |
| `note_ids` | 单元绑定笔记 ID 列表 | P0.5 | array<string> | unit list | 只作为候选线索，不进 A 线映射契约 |
| `landing_page_url` | 落地页 URL | P0.5 | string/url | unit list | 如保存需确认隐私和脱敏规则 |
| `unit_external_page_url` | 外链 URL | P0.5 | string/url | unit list | 如保存需确认隐私和脱敏规则 |
| `fee` | 消费 | P0 | decimal | report | 核心指标 |
| `impression` | 曝光 | P0 | integer | report | 核心指标 |
| `click` | 点击 | P0 | integer | report | 核心指标 |
| `ctr` | 点击率 | P0 | decimal | report | 核心指标 |
| `cpm` | 千次曝光成本 | P0 | decimal | report | 核心指标 |
| `acp` | 平均点击成本 | P0 | decimal | report | 小红书原始字段 |
| `interaction` | 互动量 | P0.5 | integer | report | 需确认业务是否 P0 使用 |
| `leads` | 表单提交 | P0.5 | integer | report | 客资场景优先确认 |
| `valid_leads` | 有效表单 | P0.5 | integer | report | 需确认回传依赖 |
| `fetched_at` | 拉取时间 | P0 | datetime | 系统生成 | 审计字段 |

## 表 4：`xhs_creativity_realtime_fact`

中文名：小红书创意实时事实表

优先级：P0.5

用途：

承接已读通的实时创意表现，辅助验证创意层级字段和素材映射候选字段。由于离线创意报表和创意详情 search 尚未稳定读通，本表不作为 v0 正式离线分析主表。

推荐主键：

```text
channel + advertiser_id + creativity_id + stat_date + fetched_at
```

字段建议：

| 字段 | 中文名 | P0/P0.5 | 类型建议 | 来源 | 说明 |
|---|---|---:|---|---|---|
| `channel` | 渠道 | P0.5 | string | 系统常量 | 固定为小红书渠道枚举 |
| `advertiser_id` | 广告主 ID | P0.5 | string | request/report | 必填，展示需脱敏 |
| `campaign_id` | 计划 ID | P0.5 | string | realtime base campaign dto | 上级计划 |
| `unit_id` | 单元 ID | P0.5 | string | realtime base unit / creativity dto | 上级单元 |
| `creativity_id` | 创意 ID | P0.5 | string | realtime base creativity dto | 创意层稳定 ID 候选 |
| `creativity_name` | 创意名称 | P0.5 | string | realtime base creativity dto | 展示和核对字段 |
| `note_id` | 笔记 ID | P0.5 | string | realtime base creativity dto | 素材映射候选线索，非已决映射键 |
| `creativity_type` | 创意类型 | P0.5 | integer/string | realtime base creativity dto | 枚举需确认 |
| `audit_status` | 审核状态 | P0.5 | integer/string | realtime base creativity dto | 枚举需确认 |
| `stat_date` | 统计日期 | P0.5 | date | request date | 实时接口按日期范围请求 |
| `fee` | 消费 | P0.5 | decimal | realtime metric | 核心指标候选 |
| `impression` | 曝光 | P0.5 | integer | realtime metric | 核心指标候选 |
| `click` | 点击 | P0.5 | integer | realtime metric | 核心指标候选 |
| `ctr` | 点击率 | P0.5 | decimal | realtime metric | 核心指标候选 |
| `cpm` | 千次曝光成本 | P0.5 | decimal | realtime metric | 核心指标候选 |
| `fetched_at` | 拉取时间 | P0.5 | datetime | 系统生成 | 实时数据必须带拉取时间 |

## 字段映射

### 层级字段

| 统一概念 | 小红书字段 | P0/P0.5 | 说明 |
|---|---|---:|---|
| channel | 常量 `xiaohongshu` | P0 | 渠道枚举需与全局一致 |
| account / advertiser | `advertiser_id` | P0 | 小红书广告主 ID |
| campaign | `campaign_id` | P0 | 计划层 |
| adset equivalent | `unit_id` / unit list `id` | P0 | 建议保留 `unit` 命名，不强行改成 adset |
| creative | `creative_id` / `creativity_id` | P0.5 | 命名差异需 Architecture 决策 |
| content asset candidate | `note_id` | P0.5 | 素材映射候选，不等于 `material_id` |
| keyword | `keyword_id` / `keyword` | P0.5 / P1 | 搜索推广扩展维度 |

### 指标字段

| 统一指标候选 | 小红书原始字段 | P0/P0.5 | 说明 |
|---|---|---:|---|
| spend | `fee` | P0 | 金额单位需确认 |
| impressions | `impression` | P0 | 曝光 |
| clicks | `click` | P0 | 点击 |
| ctr | `ctr` | P0 | 平台返回点击率 |
| cpm | `cpm` | P0 | 平台返回 CPM |
| cpc / average click cost | `acp` | P0 | 字段名不同于 Meta，需要统一层映射 |
| engagements | `interaction` | P0.5 | 小红书互动口径为点赞/收藏/关注/评论/分享等 |
| leads | `leads` | P0.5 | 客资场景优先字段 |
| valid_leads | `valid_leads` | P0.5 | 可能依赖回传或平台定义 |
| message_consult | `message_consult` | P0.5 | 私信咨询场景字段 |
| conversions | 暂不直接统一 | P0.5 | 需要按表单、私信、电商、直播、外链分别确认 |

## Architecture Decision

### AD-001：v0 先建设 campaign/unit read-only fact，不等待创意详情修通

Decision：

P0 数据契约以 `xhs_campaign_daily_fact` 和 `xhs_unit_daily_fact` 为主，`xhs_advertiser_daily_fact` 做总览和对账。创意层进入 P0.5。

Reason：

campaign/unit 的 list 与 offline/realtime report 已读通，足够支撑第一版投放表现分析。创意 search 与 offline creativity report 存在 SDK/schema mismatch，不应阻塞 P0。

### AD-002：`unit` 保留小红书原生命名，不在 P0 强制改成 `adset`

Decision：

事实表使用 `unit_id` / `unit_name`。跨渠道语义层可以把它解释为 Meta `adset` 的近似层，但底层合同不改名。

Reason：

小红书对象模型不是 Meta 结构的机械复制。保留原生命名可减少误解和字段错配。

### AD-003：`fee` 保留为小红书原始消费字段，统一层再映射 spend

Decision：

小红书事实表保留 `fee`，统一指标层可映射为 `spend`。

Reason：

SDK 和平台字段使用 `fee`，直接改名可能掩盖金额单位、税费、币种或口径差异。

### AD-004：`note_id` 只作为素材映射候选线索，不进入 A 线契约修改

Decision：

本 v0 文档只记录 `note_id` 是 content asset candidate，不把它写入 `material_ad_mapping` 的已决 join key。

Reason：

`note_id` 可能比 `creative_id` 更接近内容资产，但程序化创意、多图/视频、落地页组件和历史素材复用关系尚未确认。

### AD-005：关键词层级不进入 P0

Decision：

关键词层级进入 P0.5 / P1，等待搜索推广场景专项验证。

Reason：

当前 spike 目标优先验证投放对象和主报表，关键词没有作为 P0 实测成功项。

## Need Confirmation

业务 / 数据运营需要确认：

1. `fee` 的金额单位、币种、是否含税，以及与当前小红书周报消费口径是否一致。
2. 小红书报表日期的时区、自然日边界和归因窗口。
3. `leads`、`valid_leads`、`message_consult`、外链转化等字段分别对应业务周报中的哪些指标。
4. 当前账号是否以客资收集为主；若是，P0.5 是否应提升表单/有效表单字段优先级。
5. 是否需要把 realtime 数据用于正式分析，还是只作为当天观察和补充。

API / 技术同事需要确认：

1. `unit list` 的 `id` 与报表中的 `unit_id` 是否完全等价。
2. `creative_id` 与 `creativity_id` 是否同一概念，只是接口命名不同。
3. `creativity search` 中 `item_invalid_reason` 实际可能返回 number，SDK 类型是否需要 patch 或绕过。
4. `offline report creativity` 当前 404/schema mismatch 的原因是接口路径、权限、参数还是 SDK 版本。
5. 关键词报表是否对当前账号和推广类型可用。

Architecture 需要确认：

1. P0 是否只落 `xhs_campaign_daily_fact`、`xhs_unit_daily_fact` 和账户汇总。
2. P0.5 的 `xhs_creativity_realtime_fact` 是否允许作为探索表先存在。
3. 后续是否需要 `xhs_campaign_dim`、`xhs_unit_dim`，还是先把名称/状态字段冗余在 fact 中。
4. `note_id` 后续进入素材映射时，是进候选表、ADR，还是扩展 `material_ad_mapping`。
5. 小红书与 Meta 的统一语义层是否采用 `unit -> adset_equivalent`，还是保留各渠道层级再在 BI 层解释。

## 下一步

建议下一步只做 Architecture 评审，不进入生产同步：

1. Architecture 审核本 v0 文档的 P0/P0.5 边界。
2. 确认 `unit`、`creativity_id`、`note_id`、`fee` 的统一层处理方式。
3. 再交回 Dev / Execution 做一个小切片：生成字段抽取器或 contract fixture，不修 SDK 主体、不接生产库。

通过本闸口前，不应新增写入任务、定时同步、数据库 migration 或 A 线素材契约变更。
