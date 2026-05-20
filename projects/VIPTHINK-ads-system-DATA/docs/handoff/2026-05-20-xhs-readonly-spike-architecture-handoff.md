# 小红书聚光 Read-only Spike - Architecture Handoff

## Resume Focus

本 handoff 交给 Architecture / Product Design 会话，用于审核 2026-05-20 的 Dev2 / B 线“小红书聚光 API read-only spike”是否达成阶段目标。

当前会话只负责 B 线 read-only 验证。A 线“素材数据底座 v0”的 `material_dim` / `material_ad_mapping` 契约未修改。所有会影响素材映射设计的发现只记录为 `Need Architecture Decision`。

## Stage Goal

使用 `github.com/bububa/spotlight-mapi` 做最小只读验证，确认当前小红书账号 token 是否能读取投放对象和报表数据，并输出：

- 小红书对象层级。
- 稳定 ID 和字段观察。
- 报表粒度与可读指标。
- 与 Meta 字段模型差异。
- 缺口清单。
- 需要 Architecture 判断的素材映射问题。

## Stage Result

结论：阶段目标基本达成，可以进入 Architecture 层的小红书 read-only 数据契约设计评审，但不应直接修改 A 线素材映射契约。

理由：

- token 和 advertiser_id 已从本地私密 env 读取，未写入代码或公开配置。
- 已成功读取核心对象列表：campaign list、unit list。
- 已成功读取核心报表：离线账户/计划/单元报表，实时账户/计划/单元/创意报表。
- 已确认小红书对象层级可按 `advertiser -> campaign -> unit -> creativity / keyword` 进入架构讨论。
- 创意查询和创意离线报表仍有 SDK/平台响应结构不匹配，需要后续技术处理或 API 同事确认。

不建议现在直接进入生产化同步或素材映射契约变更。下一步应是 Architecture 先确认字段模型与事实表边界。

## Acceptance Review

| 验收项 | 结果 | 证据 / 说明 |
|---|---:|---|
| SDK 安装或阻塞原因明确 | 达成 | `tools/xhs-readonly-spike/go.mod` 使用 `github.com/bububa/spotlight-mapi v1.1.2`，`go test ./...` 通过。 |
| token 从本地 env 读取，未泄露 | 达成 | 私密文件位于 `config/private/xhs/.env`，该目录已被 `.gitignore` 覆盖；输出只显示脱敏状态。 |
| 至少尝试一个 read-only 接口 | 达成 | 实际尝试 12 个 read-only step。 |
| 输出对象层级、字段、报表粒度、缺口清单 | 达成 | 见 `outputs/xiaohongshu/xhs_api_readonly_spike.md`。 |
| 不修改 A 线素材数据底座契约 | 达成 | 未修改 `docs/data-contract/material-data-foundation-contract-v0.md`。 |
| 不调用任何写接口 | 达成 | 程序只引用 account balance、campaign list、unit list、creativity search、offline/realtime report。 |
| 失败接口和原因明确 | 达成 | 失败均记录为 SDK/响应结构不匹配，未中断后续接口。 |

## Artifacts

- Spike 程序：`tools/xhs-readonly-spike/main.go`
- Go module：`tools/xhs-readonly-spike/go.mod`
- 示例配置：`config/examples/xhs.env.example`
- 私密配置：`config/private/xhs/.env`，不要读取、打印、提交或复制内容
- 输出报告：`outputs/xiaohongshu/xhs_api_readonly_spike.md`

## Commands Run

```bash
go -C tools/xhs-readonly-spike run . \
  --env /Users/takuya/Documents/Codex/projects/投放系统demo/config/private/xhs/.env \
  --output /Users/takuya/Documents/Codex/projects/投放系统demo/outputs/xiaohongshu/xhs_api_readonly_spike.md

cd /Users/takuya/Documents/Codex/projects/投放系统demo/tools/xhs-readonly-spike
go test ./...
```

Result:

- `go test ./...`: passed, no test files.
- Spike run: completed and wrote the markdown output.

## Interface Results

Successful:

| Interface | Result |
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

Failed / needs follow-up:

| Interface | Failure Type | Current Read |
|---|---|---|
| account balance | SDK/response schema mismatch | 返回 404 + SDK JSON decode mismatch；不是核心对象/报表阻塞项。 |
| creativity search | SDK field schema mismatch | 平台实际返回数据，但 SDK 中 `item_invalid_reason` 类型与实际响应不一致，导致 decode fail。 |
| offline report creativity | SDK/response schema mismatch | 返回 404 + SDK JSON decode mismatch；需确认接口路径、权限或 SDK 版本。 |

## Object Model Observed

当前可进入 Architecture 讨论的对象层级：

```text
advertiser
  -> campaign
      -> unit
          -> creativity
          -> keyword (搜索推广/关键词场景)
```

稳定 ID 初步判断：

- `advertiser_id`: 广告主级调用必需。
- `campaign_id`: 列表和报表均支持。
- `unit_id`: 报表和实时模型使用；unit list 中字段名为 `id`。
- `creative_id` / `creativity_id`: 创意查询使用 `creative_id`，报表维度使用 `creativity_id`。
- `note_id`: 创意和报表可能返回，是素材映射候选字段，但不能由 Dev2 直接纳入 A 线契约。
- `keyword_id` / `keyword`: 关键词报表模型支持，适用于搜索推广场景。

## Report Grain And Metrics

已验证可读粒度：

- 离线账户级。
- 离线计划级。
- 离线单元级。
- 实时账户级。
- 实时计划级。
- 实时单元级。
- 实时创意级。

SDK 模型显示但仍需业务/API 确认的理论粒度：

- `DAY / HOUR / SUMMARY`
- `date/hour + campaign_id`
- `date/hour + unit_id`
- `date/hour + creativity_id`
- keyword 维度在搜索推广场景下可能独立存在。

可用指标字段：

- 消费：`fee`，对应统一口径中的 spend 候选。
- 曝光/点击：`impression`、`click`、`ctr`、`cpm`、`acp`。
- 互动：like、comment、collect、follow、share、interaction、cpi。
- 表单/私信/外链/电商/直播：SDK 模型中存在，但需按业务目标确认是否进入第一版字段。

## Architecture Interpretation

小红书不像 Meta 那样天然落在 `campaign -> adset -> ad -> creative` 的拆分里。当前更稳妥的 Architecture 判断是：

- `campaign` 可映射统一 campaign 层。
- `unit` 可作为 Meta `adset` 的近似层，但需保留 channel-specific 命名风险。
- `creativity` 是投放创意对象，同时可能绑定 `note_id`、落地页、图片、组件、程序化信息。
- `note_id` 可能比 `creative_id` 更接近内容素材资产，但是否作为 `material_id` 映射候选键必须由 Architecture 决定。

## Need Architecture Decision

1. 是否把小红书 `note_id` 纳入素材映射候选键，还是只作为平台创意属性保留。
2. 小红书 `creative_id` 与 `creativity_id` 命名差异进入统一契约时如何规范。
3. `unit` 是否在统一模型中映射为 `adset` 层，还是保留 `xhs_unit` 这种 channel-specific 层级名。
4. 创意图片 `image` / `creativity_image`、跳转字段 `jump_url`、落地页 `page_id` 是否允许参与 `material_id` 半自动匹配。
5. 关键词层级是否进入第一版数据契约，还是作为搜索推广扩展事实表。
6. 小红书消费字段 `fee` 的金额单位、时区、归因窗口是否与当前业务周报口径一致。
7. 第一版小红书数据契约是否只覆盖 campaign/unit 事实表，还是同步设计 creativity 事实表。

## Recommended Next Gate

Architecture 会话建议先产出一个小红书 read-only 数据契约草案，而不是修改 A 线素材契约：

- `xhs_campaign_daily_fact`
- `xhs_unit_daily_fact`
- `xhs_creativity_daily_fact` 是否进入 v0，由 Architecture 决定
- `xhs_creativity_dim` 或只作为事实表冗余字段，由 Architecture 决定
- `note_id -> material_id` 映射策略只记录 ADR，不直接落 A 线契约

建议 Architecture 审核通过后再交回 Dev / Execution 做下一步：

1. 绕过或修补 SDK schema mismatch，只读拿到 creativity search 的安全摘要字段。
2. 确认 offline creativity report 的接口路径/权限/SDK 版本。
3. 将已验证字段整理成小红书 read-only fact contract draft。

## Safety Notes

- 不要读取或复制 `config/private/xhs/.env` 内容。
- 不要把 token、refresh token、app secret、完整 advertiser_id 写入文档、代码或 Git。
- 不要调用 create/update/status/delete/conversion 回传接口。
- 不要在 Architecture 会话中直接改 `material_dim` / `material_ad_mapping`，先输出 ADR 或契约草案。
