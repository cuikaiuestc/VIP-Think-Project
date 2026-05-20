# 素材数据底座数据契约 v0

生成日期：2026-05-20

## 目标

本契约定义未来进入数仓、BI 和投放分析体系的素材数据底座 v0。它不依赖当前手工回写表，也不等待数据运营现有表结构。当前任务只定义数据框架，供数据运营、自动化投放系统开发者和素材模块开发者评审。

核心表：

| 表名 | 中文名 | 主用途 |
|---|---|---|
| `material_dim` | 素材资产维表 | 描述一份可直接投放的成品素材及其分析变量 |
| `material_ad_mapping` | 素材与广告对象映射表 | 记录 `material_id -> creative_id -> ad_id`，支持跨渠道投放事实表 join |

## 非目标

- 不做真实数据库 migration。
- 不写业务代码。
- 不接 Meta、小红书、广点通、抖音、Google、TikTok 等 API。
- 不设计素材模块内部系统、审核流、生产流或权限模型。
- 不把当前 BI 回写表作为未来 P0 主架构。
- 不用广告名、素材名、文件名作为主键。
- 不引入复杂素材本体论；P0 只保留投放分析必要字段。

## 核心口径

`material_id` 的定义：

> 公司内部认定的一份“可直接投放的成品素材”。

变体规则：

- 如果语言、字幕、尺寸、时长、剪辑、画面版本、音频版本等变化会影响投放表现分析，应生成新的 `material_id`。
- 如果只是文件存储路径、预览链接、命名格式或非分析变量变化，不应生成新的 `material_id`。
- `parent_material_id` 可作为 P1 字段，用于未来归并同一创意母体下的不同版本，不作为 P0 必填。

ID 边界：

- creative_id 是平台创意对象 ID，不是 `material_id`。
- `video_id`、`image_hash`、`file_name`、`ad_name`、`creative_name` 都不能替代 `material_id`。
- 广告名、素材名、文件名只能作为辅助核对字段或过渡期命名解析线索，不作为主键或稳定 join key。
- 回写表只可作为历史治理线索，不进入未来 P0 主架构。

## 表 1：`material_dim`

中文名：素材资产维表

主键：

```text
material_id
```

推荐唯一约束：

```text
unique(material_id)
```

推荐 join key：

| join 对象 | join key | 说明 |
|---|---|---|
| `material_ad_mapping` | `material_id` | 素材资产到平台广告对象映射 |
| 素材模块内部资产表 | `material_id` | 如素材模块后续自建资产系统，应以此字段对齐 |
| BI/分析层素材表现宽表 | `material_id` | 聚合素材跨渠道、跨账户、跨广告表现 |

### 字段定义

| 字段 | 中文名 | 分组 | P0/P1 | 类型建议 | 必填 | 说明 |
|---|---|---|---|---|---|---|
| `material_id` | 内部素材 ID | 主键与生命周期 | P0 | string | 是 | 公司内部认定的一份可直接投放成品素材的稳定 ID |
| `material_name` | 素材名称 | 主键与生命周期 | P0 | string | 是 | 展示和人工核对字段，不可作为主键 |
| `material_status` | 素材状态 | 主键与生命周期 | P0 | enum/string | 是 | 建议枚举：`active`、`paused`、`archived`、`unknown` |
| `created_at` | 创建时间 | 主键与生命周期 | P0 | datetime | 是 | 素材资产在内部系统首次创建或登记时间 |
| `updated_at` | 更新时间 | 主键与生命周期 | P0 | datetime | 是 | 素材资产元数据最近更新时间 |
| `material_type` | 素材类型 | 素材分析变量 | P0 推荐 | enum/string | 否 | 分析推荐字段，不阻塞首版入仓；例如 image、video、kol、ai_video |
| `format` | 素材格式 | 素材分析变量 | P0 推荐 | enum/string | 否 | 分析推荐字段，不阻塞首版入仓；例如 image、short_video、long_video、carousel |
| `aspect_ratio` | 尺寸比例 | 素材分析变量 | P0 推荐 | string | 否 | 分析推荐字段，不阻塞首版入仓；例如 `9:16`、`1:1`、`16:9` |
| `duration_seconds` | 视频时长秒数 | 素材分析变量 | P0 推荐 | number | 否 | 图片可为空；视频建议填写 |
| `language` | 语言 | 素材分析变量 | P0 推荐 | enum/string | 否 | 分析推荐字段，不阻塞首版入仓；具体枚举待确认 |
| `region_target` | 目标地区 | 素材分析变量 | P0 推荐 | enum/string | 否 | 分析推荐字段，不阻塞首版入仓；素材面向的目标市场或地区分组 |
| `topic` | 题材 | 内容变量 | P0 推荐 | string | 否 | 分析推荐字段，不阻塞首版入仓；P0 不强制复杂标签体系 |
| `selling_point` | 卖点 | 内容变量 | P1 | string | 否 | 评审可选字段；主卖点或诉求 |
| `audience_segment` | 目标人群段 | 内容变量 | P1 | string | 否 | 评审可选字段；如高潜/非高潜等业务人群标签，需确认维护来源 |
| `actor_or_kol` | 演员或 KOL | 内容变量 | P1 | string | 否 | 评审可选字段；涉及隐私或合作信息时可脱敏或仅保留内部代号 |
| `preview_url` | 预览链接 | 管理与核对 | P1 | string/url | 否 | 评审可选字段；人工核对用，不作为系统 join key |
| `source_owner` | 来源负责人 | 管理与核对 | P0 | string | 是 | 素材元数据 owner 或维护方 |
| `naming_code` | 命名编码 | 管理与核对 | P1 | string | 否 | 评审可选字段；文件名/广告名中可解析的辅助编码，不替代 `material_id` |
| `parent_material_id` | 父素材 ID | 扩展字段 | P1 | string | 否 | 用于未来归并同一创意母体的不同变体 |

### 入仓字段门槛

`material_dim` 不应因为分析标签不完整而阻塞首版入仓。字段分三层：

#### identity_required

首版入仓必填，用于保证素材主数据可识别、可追责、可更新：

```text
material_id
material_name
material_status
created_at
updated_at
source_owner
```

#### analysis_recommended

分析推荐字段，应尽量补齐，但缺失时不阻塞首版入仓；数据运营需要记录缺失率，并给出补齐 owner：

```text
material_type
format
aspect_ratio
duration_seconds
language
region_target
topic
```

#### optional_review

评审可选字段，进入 P1 或后续素材模块治理：

```text
selling_point
audience_segment
actor_or_kol
preview_url
naming_code
parent_material_id
```

## 表 2：`material_ad_mapping`

中文名：素材与广告对象映射表

用途：

记录公司内部素材资产与不同广告平台对象之间的映射，使素材维表可以和 Meta、小红书、广点通、抖音、Google、TikTok 等渠道投放事实表 join。

推荐主键：

```text
mapping_id
```

推荐唯一约束：

```text
unique(channel, account_id, platform_ad_id, material_id, valid_from)
```

如果 v0 暂不生成 `mapping_id`，可临时使用以下组合键：

```text
channel + account_id + platform_ad_id + material_id + valid_from
```

如果渠道能稳定取得 `platform_creative_id`，建议额外增加包含 `platform_creative_id` 的唯一约束或质量检查；如果不能稳定取得，不允许伪造 creative key。

推荐 join key：

| join 对象 | join key | 说明 |
|---|---|---|
| `material_dim` | `material_id` | 连接内部素材资产 |
| Meta 投放事实表 | `channel + account_id + platform_ad_id + valid_from/valid_to` | Meta 场景 `platform_ad_id = ad_id`，生产 join 仍必须带账户和有效期 |
| Meta 创意对象表 | `channel + account_id + platform_creative_id` | 仅在 `creative_id` 稳定取得时作为创意层级校验 |
| 其他渠道投放事实表 | `channel + account_id + platform_ad_id + valid_from/valid_to` | 兼容小红书、广点通、抖音、Google、TikTok 等，不要求伪造 creative key |

### 字段定义

| 字段 | 中文名 | 分组 | P0/P1 | 类型建议 | 必填 | 说明 |
|---|---|---|---|---|---|---|
| `mapping_id` | 映射 ID | 映射主键/唯一性设计 | P0 | string | 是 | 映射表技术主键；可由系统生成 |
| `channel` | 渠道 | 映射主键/唯一性设计 | P0 | enum/string | 是 | 例如 meta、xiaohongshu、gdt、douyin、google、tiktok |
| `account_id` | 平台账户 ID | 映射主键/唯一性设计 | P0 | string | 是 | 外部平台账户 ID |
| `campaign_id` | 平台广告计划 ID | 映射主键/唯一性设计 | P1 | string | 否 | 不同渠道层级命名不同，作为聚合和核对字段 |
| `adset_id` | Meta 广告组 ID | 映射主键/唯一性设计 | P1 | string | 否 | Meta 专用层级字段 |
| `equivalent_unit_id` | 等价投放单元 ID | 映射主键/唯一性设计 | P1 | string | 否 | 非 Meta 渠道用于承接广告组/单元/计划组等中间层级 |
| `ad_id` | Meta 广告 ID | 映射主键/唯一性设计 | P1 | string | 否 | Meta 原生字段，推荐同步保留 |
| `platform_ad_id` | 平台广告 ID | 映射主键/唯一性设计 | P0 | string | 是 | 跨渠道统一广告对象 ID；Meta 场景等于 `ad_id` |
| `creative_id` | Meta 创意 ID | 映射主键/唯一性设计 | P1 | string | 否 | Meta 原生字段，推荐同步保留 |
| `platform_creative_id` | 平台创意 ID | 映射主键/唯一性设计 | 条件 P0 | string | 条件必填 | 渠道可稳定取得时 P0 必填；不可取得时必须填写降级规则，并由 Architecture / 数据运营确认；Meta 场景等于 `creative_id` |
| `creative_key_degradation_rule` | 创意键降级规则 | 映射主键/唯一性设计 | 条件 P0 | string | 条件必填 | 当 `platform_creative_id` 不可稳定取得时必填，说明降级到广告级、单元级或人工确认层的规则和责任人 |
| `material_id` | 内部素材 ID | 映射主键/唯一性设计 | P0 | string | 是 | 连接 `material_dim` 的核心字段 |
| `mapping_source` | 映射来源 | 映射质量 | P0 | enum/string | 是 | 建议枚举：`system_created`、`name_parsed`、`manual_confirmed`、`api_inferred`、`historical_backfill` |
| `mapping_confidence` | 映射置信度 | 映射质量 | P0 | number | 是 | 0 到 1；强匹配建议为 1，弱匹配需低于人工确认 |
| `valid_from` | 映射生效开始时间 | 映射有效期 | P0 | datetime | 是 | 映射开始生效时间 |
| `valid_to` | 映射生效结束时间 | 映射有效期 | P0 | datetime | 否 | 当前仍生效时为空 |
| `first_seen_at` | 首次发现时间 | 发现时间 | P0 | datetime | 是 | 系统第一次发现该映射的时间 |
| `last_seen_at` | 最后发现时间 | 发现时间 | P0 | datetime | 是 | 最近一次确认该映射仍存在的时间 |

### 映射来源优先级

| `mapping_source` | 置信度建议 | 说明 |
|---|---:|---|
| `system_created` | 1.00 | 素材模块/投放系统创建广告时直接写入映射，P0 最推荐 |
| `manual_confirmed` | 0.95 | 历史数据由人工确认后写入 |
| `api_inferred` | 0.70-0.90 | 从平台 creative、asset、video/image 关系推断 |
| `name_parsed` | 0.40-0.80 | 从广告名、素材名、文件名解析，只能作为过渡方案 |
| `historical_backfill` | 视规则而定 | 从回写表、旧 BI 表或历史文件回填，只能作为历史线索 |

正式素材表现 join 的默认准入门槛：

- 默认只接受 `system_created` 和 `manual_confirmed`。
- `api_inferred`、`name_parsed`、`historical_backfill` 只能进入候选/待确认层。
- 如果确需把候选映射用于正式分析，必须达到确认阈值，并经过人工或数据运营确认后，才能进入正式素材表现 join。
- 确认阈值由 Architecture / 数据运营评审确定；在确认前，Dev 不应把弱匹配映射当作事实关联。

### 跨渠道字段映射建议

| 统一字段 | Meta | 小红书/广点通/抖音/Google/TikTok 等 | 说明 |
|---|---|---|---|
| `channel` | `meta` | 各渠道标准枚举 | 用于分渠道 join 和过滤 |
| `account_id` | Meta ad account id | 渠道账户 ID | 不可用账户名称替代 |
| `campaign_id` | `campaign_id` | 计划/推广系列 ID | 可选但建议保留 |
| `adset_id` | `adset_id` | 不一定存在 | Meta 专用字段 |
| `equivalent_unit_id` | 可为空或等于 `adset_id` | 广告组/单元/计划组 ID | 兼容非 Meta 层级 |
| `platform_ad_id` | `ad_id` | 渠道广告/创意投放实例 ID | 投放事实表主要 join key |
| `platform_creative_id` | `creative_id` | 渠道创意/素材对象 ID，如稳定可取则填写 | 不稳定或不可取时必须走降级规则，不能伪造 |
| `material_id` | 内部生成 | 内部生成 | 公司内部素材主键 |

## 和投放事实表的 join 方式

P0 生产 join 口径必须带完整条件，避免跨账户误匹配和有效期重复累计：

```sql
fact.channel = mapping.channel
AND fact.account_id = mapping.account_id
AND fact.platform_ad_id = mapping.platform_ad_id
AND fact.date >= mapping.valid_from
AND (mapping.valid_to IS NULL OR fact.date < mapping.valid_to)
```

如渠道稳定提供 `platform_creative_id`，可增加创意层级校验：

```sql
AND fact.platform_creative_id = mapping.platform_creative_id
```

但 `platform_creative_id` 不稳定或不可取时，不应伪造 creative key；必须由 Architecture / 数据运营确认降级规则。

Meta 只按 `ad_id` join 的写法只能作为单账户调试示例，不能作为生产口径：

```text
meta_ad_daily_fact.ad_id -> material_ad_mapping.platform_ad_id
```

生产环境仍必须带上 `channel`、`account_id` 和有效期条件。

如果一条广告对象在不同时间引用不同素材，必须依赖 `valid_from` / `valid_to` 判断某一天应关联哪个 `material_id`。

有效期重叠检查：

- 同一 `channel + account_id + platform_ad_id` 在任意 `fact.date` 只能命中一个有效 `material_id`。
- 如果业务允许多素材组合，必须单独定义组合/分摊规则，不能默认 join 后重复累计。
- 在组合/分摊规则确认前，多命中记录应进入数据质量异常，不进入正式素材表现汇总。

## 数据质量要求

| 检查项 | P0 要求 |
|---|---|
| `material_dim.material_id` 唯一性 | 100% 唯一 |
| `material_ad_mapping.mapping_id` 唯一性 | 100% 唯一 |
| `material_ad_mapping.material_id` 外键覆盖 | 必须能在 `material_dim` 找到 |
| `platform_ad_id` 空值率 | P0 不允许为空 |
| `platform_creative_id` 空值率 | 渠道可稳定取得时 P0 不允许为空；不可稳定取得时必须填写降级规则，并由 Architecture / 数据运营确认 |
| `mapping_confidence` 范围 | 0 到 1 |
| `valid_from` / `valid_to` | 不允许同一 `channel + account_id + platform_ad_id` 在同一 fact date 命中多个有效 `material_id`，除非业务明确支持多素材组合并定义分摊规则 |
| 正式 join 准入 | 默认只接受 `system_created`、`manual_confirmed`；其他来源需确认后才能进入正式 join |
| 名称字段使用 | 只能用于核对，不参与唯一约束 |

## 字段评审动作清单

本节用于人工审计字段是否需要增补、改变量名或调整优先级。默认原则：

- 不改两张大表结构，除非发现字段无法支撑入仓或 join。
- 不把素材模块内部流程字段提前塞进数据底座。
- 不因为分析标签缺失阻塞首版入仓，但必须记录缺失率和补齐 owner。
- 字段命名优先采用跨渠道通用名；平台原生名作为补充字段保留。

### `material_dim` 字段评审

| 字段 | 当前分层 | 是否建议增补 | 变量名是否建议调整 | 优先级是否建议调整 | 评审点 |
|---|---|---|---|---|---|
| `material_id` | identity_required | 不增补 | 不改 | 保持 P0 必填 | 必须由内部生成，不能用平台 ID、文件名或广告名替代 |
| `material_name` | identity_required | 不增补 | 不改 | 保持 P0 必填 | 只做展示和人工核对，不作为 join key |
| `material_status` | identity_required | 不增补 | 不改 | 保持 P0 必填 | 需确认枚举是否够用：active、paused、archived、unknown |
| `created_at` | identity_required | 不增补 | 不改 | 保持 P0 必填 | 需确认是素材创建时间还是首次入仓时间 |
| `updated_at` | identity_required | 不增补 | 不改 | 保持 P0 必填 | 用于增量同步和字段变更追踪 |
| `source_owner` | identity_required | 不增补 | 可评审是否改为 `data_owner` | 保持 P0 必填 | 数据运营需确认 owner 是人、团队还是系统 |
| `material_type` | analysis_recommended | 不增补 | 不改 | 保持 P0 推荐 | 需确认枚举，不阻塞入仓 |
| `format` | analysis_recommended | 不增补 | 可评审是否改为 `media_format` | 保持 P0 推荐 | `format` 可能过泛，开发可评审是否更名以避免与文件格式混淆 |
| `aspect_ratio` | analysis_recommended | 不增补 | 不改 | 保持 P0 推荐 | 用于素材尺寸分析，缺失时记录缺失率 |
| `duration_seconds` | analysis_recommended | 不增补 | 不改 | 保持 P0 推荐 | 图片可空，视频建议补齐 |
| `language` | analysis_recommended | 不增补 | 不改 | 保持 P0 推荐 | 不阻塞入仓，需确认枚举和多语言素材处理方式 |
| `region_target` | analysis_recommended | 不增补 | 可评审是否改为 `target_region` | 保持 P0 推荐 | 需和投放事实表地区维度区分：这是素材目标地区，不一定等于实际投放地区 |
| `topic` | analysis_recommended | 不增补 | 不改 | 保持 P0 推荐 | 题材标签缺失不阻塞入仓 |
| `selling_point` | optional_review | 不增补 | 不改 | 保持 P1 | 可用于后续素材内容分析，P0 不强制 |
| `audience_segment` | optional_review | 不增补 | 不改 | 保持 P1 | 需确认是素材标签、人群包标签，还是投放策略标签 |
| `actor_or_kol` | optional_review | 不增补 | 不改 | 保持 P1 | 涉及隐私或合作信息时建议使用内部代号 |
| `preview_url` | optional_review | 不增补 | 不改 | 保持 P1 | 人工核对字段，不参与 join |
| `naming_code` | optional_review | 不增补 | 不改 | 保持 P1 | 仅作为命名解析线索，不能替代 `material_id` |
| `parent_material_id` | optional_review | 不增补 | 不改 | 保持 P1 | 只有需要归并素材母体时启用 |

### `material_ad_mapping` 字段评审

| 字段 | 当前分层 | 是否建议增补 | 变量名是否建议调整 | 优先级是否建议调整 | 评审点 |
|---|---|---|---|---|---|
| `mapping_id` | P0 | 不增补 | 不改 | 保持 P0 必填 | 技术主键，建议系统生成 |
| `channel` | P0 | 不增补 | 不改 | 保持 P0 必填 | 需确认渠道枚举 |
| `account_id` | P0 | 不增补 | 不改 | 保持 P0 必填 | 防止跨账户 `platform_ad_id` 碰撞 |
| `campaign_id` | P1 | 不增补 | 不改 | 保持 P1 | 主要用于聚合和核对，不作为生产主 join 条件 |
| `adset_id` | P1 | 不增补 | 不改 | 保持 P1 | Meta 专用字段；其他渠道不强行映射 |
| `equivalent_unit_id` | P1 | 不增补 | 可评审是否改为 `platform_unit_id` | 保持 P1 | 用于非 Meta 中间层级；命名是否清晰需开发评审 |
| `ad_id` | P1 | 不增补 | 不改 | 保持 P1 | Meta 原生冗余字段，生产统一用 `platform_ad_id` |
| `platform_ad_id` | P0 | 不增补 | 不改 | 保持 P0 必填 | 跨渠道广告对象 join key |
| `creative_id` | P1 | 不增补 | 不改 | 保持 P1 | Meta 原生冗余字段，不能替代 `material_id` |
| `platform_creative_id` | 条件 P0 | 不增补 | 不改 | 保持条件 P0 | 可稳定取得时必填；不可取得时走降级规则 |
| `creative_key_degradation_rule` | 条件 P0 | 不增补 | 可评审是否改为 `creative_key_fallback_rule` | 保持条件 P0 | 当 `platform_creative_id` 不可稳定取得时必填 |
| `material_id` | P0 | 不增补 | 不改 | 保持 P0 必填 | 连接 `material_dim` 的核心字段 |
| `mapping_source` | P0 | 不增补 | 不改 | 保持 P0 必填 | 正式 join 默认只接受 system_created、manual_confirmed |
| `mapping_confidence` | P0 | 不增补 | 不改 | 保持 P0 必填 | 需确定确认阈值，弱匹配不能直接进正式汇总 |
| `valid_from` | P0 | 不增补 | 不改 | 保持 P0 必填 | 生产 join 必备 |
| `valid_to` | P0 | 不增补 | 不改 | 保持 P0 可空 | 当前有效时为空 |
| `first_seen_at` | P0 | 不增补 | 不改 | 保持 P0 必填 | 用于发现时间审计 |
| `last_seen_at` | P0 | 不增补 | 不改 | 保持 P0 必填 | 用于映射有效性追踪 |

### 可能需要增补但暂不进入 v0 的字段

以下字段不建议直接加入当前 v0，除非评审确认有明确下游使用场景：

| 候选字段 | 所属表 | 暂不加入原因 | 触发加入条件 |
|---|---|---|---|
| `file_hash` | `material_dim` | 容易变成素材系统内部存储字段 | 需要做文件去重或版权审计 |
| `storage_uri` | `material_dim` | 涉及素材存储系统，不是投放分析必需 | 素材模块确认开放稳定只读链接 |
| `approval_status` | `material_dim` | 属于素材审核流程字段 | 素材状态需要拆分“投放状态”和“审核状态”时 |
| `asset_variant_id` | `material_dim` | 当前已有 `parent_material_id` 承接 P1 归并 | 需要精细管理同一素材母体下多个版本 |
| `placement` | `material_ad_mapping` | 更像投放事实表维度 | 需要素材在不同版位映射到不同素材表现时 |
| `landing_page_url` | `material_ad_mapping` | 更像广告/创意对象字段 | 分析确认落地页会影响素材映射判断时 |

## 三个角色的对齐要求

### 数据运营

数据运营需要确认这份契约是否可入仓，以及字段约束能否落地。

| 对齐项 | 必须确认的问题 | 输出物 |
|---|---|---|
| 入仓层级 | `material_dim` 和 `material_ad_mapping` 放在哪一层，是否作为维表/桥表管理 | 数仓层级建议 |
| 字段类型 | 字段类型、时间类型、枚举值是否可执行 | 字段字典 |
| 必填约束 | `identity_required` 和 `material_ad_mapping` P0 字段是否能保证 | 缺失率评估 |
| 更新频率 | 实时写入、小时级同步还是每日批处理 | SLA 和数据延迟 |
| owner | 两张表分别由谁维护，字段变更由谁通知 | owner 清单 |
| join 方式 | 是否认可生产 join 条件：`channel + account_id + platform_ad_id + valid_from/valid_to` | join 口径确认 |
| 数据质量 | 如何检查有效期重叠、多命中、弱匹配误入正式汇总 | DQ 规则草案 |
| 历史治理 | 回写表、旧 BI 表、历史文件如何作为线索进入候选层 | 历史初始化方案 |

### 投放系统开发者

投放系统开发者需要确认系统创建广告或同步广告时，如何写入或维护映射关系。

| 对齐项 | 必须确认的问题 | 输出物 |
|---|---|---|
| 创建时写映射 | 系统创建广告时能否直接写入 `material_id -> platform_creative_id -> platform_ad_id` | 写入时机说明 |
| 平台字段归一 | 各渠道广告对象 ID 如何映射到 `platform_ad_id` | 渠道字段映射表 |
| 创意键降级 | 非 Meta 渠道拿不到稳定 `platform_creative_id` 时如何填写 `creative_key_degradation_rule` | 降级规则 |
| 映射来源 | 哪些场景写 `system_created`，哪些场景只能写候选来源 | `mapping_source` 规则 |
| 正式 join 准入 | 系统侧是否只消费 system_created / manual_confirmed，候选映射是否隔离 | 读取规则 |
| 时间有效期 | 广告更换素材时如何关闭旧映射、开启新映射 | `valid_from` / `valid_to` 更新规则 |

### 素材系统开发者

素材系统开发者需要确认 `material_id` 如何生成，以及哪些素材分析变量能稳定提供。

| 对齐项 | 必须确认的问题 | 输出物 |
|---|---|---|
| `material_id` 生成 | 是否能保证内部唯一、稳定、不复用 | ID 生成规则 |
| 变体规则 | 语言、字幕、尺寸、时长、剪辑变化何时生成新 `material_id` | 变体判断规则 |
| identity 字段 | `material_name`、`material_status`、`created_at`、`updated_at`、`source_owner` 是否可稳定提供 | identity 字段样例 |
| 分析标签 | `material_type`、`format`、`aspect_ratio`、`language`、`region_target`、`topic` 的枚举和缺失率 | 标签字典 |
| 可选字段 | `preview_url`、`naming_code`、`parent_material_id` 是否需要首版提供 | P1 字段反馈 |
| 隐私边界 | `actor_or_kol` 是否可用内部代号替代真实姓名 | 脱敏规则 |

## 数据运营后续评审点

1. 这两张表是否可进入数仓，推荐放在哪一层。
2. 字段类型、必填约束、唯一约束、枚举值是否可落地。
3. `material_id` 由谁生成、何时生成、如何保证唯一。
4. `material_dim` 的 owner 是素材模块、数据运营还是投放系统。
5. `material_ad_mapping` 的 owner 是投放系统、素材模块还是数据运营。
6. 更新频率：创建广告时实时写入，还是每日批处理同步。
7. 历史数据如何初始化，回写表和旧 BI 表只作为线索时由谁人工确认。
8. 与投放事实表的 join key 是否统一为 `channel + account_id + platform_ad_id`。
9. 非 Meta 渠道的 `platform_creative_id` 是否稳定可取，若不可取需给出降级规则。
10. 变更通知机制：字段新增、枚举变更、映射修正由谁通知下游。

## Review Handoff

给 Review / QA 会话重点检查：

- 是否清楚区分 `material_dim` 和 `material_ad_mapping`。
- P0 字段是否足够支撑素材表现分析，又没有过度引入素材系统内部流程字段。
- `material_id`、`creative_id`、`video_id`、`image_hash`、`file_name` 的边界是否清楚。
- 唯一约束和 join key 是否能支撑跨渠道投放事实表 join。
- 是否仍存在依赖当前回写表或广告名硬匹配作为主架构的表述。
