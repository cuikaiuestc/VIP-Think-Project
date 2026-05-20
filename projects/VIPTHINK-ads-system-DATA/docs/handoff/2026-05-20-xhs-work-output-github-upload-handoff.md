# 2026-05-20 小红书 Read-only Spike 今日产出与 GitHub 上传 Handoff

## 给 Architecture 的判断目标

本 handoff 用于 Architecture / Product Design 会话汇总 2026-05-20 Dev2 / Execution 会话的小红书聚光 read-only spike 工作，并判断今日是否、以及如何上传 GitHub。

本文件不是上传执行指令。当前不初始化 Git、不提交、不 push。是否上传由 Architecture 确认。

## 今日阶段目标

任务目标：

- 使用 `github.com/bububa/spotlight-mapi` 做小红书聚光 API read-only spike。
- 验证当前 token 是否能读取投放对象和报表。
- 输出对象层级、字段、报表粒度、缺口清单。
- 基于 spike 结果补一份小红书 read-only 数据契约 v0。
- 不修 SDK，不做生产同步，不改 A 线 `material_dim` / `material_ad_mapping` 契约。

## 今日完成结论

结论：今日阶段目标已基本达成，可以进入 Architecture 审核和 GitHub 上传安排判断。

已达成：

- SDK 已安装并可编译运行。
- token / advertiser_id 从本地私密 env 读取，未写入代码或公开配置。
- 成功读取 campaign list、unit list、离线账户/计划/单元报表、实时账户/计划/单元/创意报表。
- 失败接口均有明确阻塞原因，主要是 SDK/接口 schema mismatch。
- 已产出 Architecture handoff。
- 已产出 `xiaohongshu-readonly-data-contract-v0.md`。
- 未修改 A 线素材数据底座契约。
- 未调用任何写接口。

未完成 / 不应今天继续做：

- 不修 `bububa/spotlight-mapi` SDK。
- 不绕过 SDK 做原始响应采集。
- 不做生产同步。
- 不做数据库 migration。
- 不推导或修改 `note_id -> material_id` 的正式映射契约。

## 今日产物清单

### 建议上传 GitHub

这些文件不包含真实 token，且属于项目可复用资产，建议纳入今日上传候选：

| 文件 | 类型 | 建议 | 原因 |
|---|---|---|---|
| `config/examples/xhs.env.example` | 示例配置 | 上传 | 只含占位字段，用于团队复现配置方式 |
| `tools/xhs-readonly-spike/go.mod` | spike module | 上传 | 记录 SDK 版本和最小验证工具依赖 |
| `tools/xhs-readonly-spike/go.sum` | spike module lock | 上传 | 保证 spike 可复现 |
| `tools/xhs-readonly-spike/main.go` | spike 程序 | 上传 | 只读验证程序，含脱敏与错误分类逻辑 |
| `docs/handoff/2026-05-20-xhs-readonly-spike-architecture-handoff.md` | Architecture handoff | 上传 | 给 Architecture 审核阶段目标是否达成 |
| `docs/handoff/2026-05-20-xhs-work-output-github-upload-handoff.md` | 本文件 | 上传 | 说明今日上传范围与风险 |
| `docs/data-contract/xiaohongshu-readonly-data-contract-v0.md` | 数据契约草案 | 上传 | 今日最重要的可评审产物 |

### 谨慎上传 / 默认不上传

| 文件 | 建议 | 原因 |
|---|---|---|
| `outputs/xiaohongshu/xhs_api_readonly_spike.md` | 默认不上传，除非 Architecture 确认 | 虽然已脱敏且不含 token，但包含真实账号接口验证结果、返回数量和平台接口状态，属于内部运行证据。更适合本地留存或做脱敏摘要后再上传。 |

### 禁止上传

| 路径 | 原因 |
|---|---|
| `config/private/xhs/.env` | 含真实 token / app secret / advertiser_id，占位文件也位于私密路径，`.gitignore` 已覆盖 |
| `config/private/` | 私密配置目录 |
| `runtime/private/` | 私密运行产物目录 |
| 任何 `.env` / `.env.*` | `.gitignore` 已覆盖，禁止提交 |
| 任何真实 API 原始响应 | 可能含账号、素材、链接、投放对象细节 |

## Read-only 验证结果摘要

成功接口：

| 接口 / 层级 | 结果 |
|---|---|
| campaign list | 成功，本页返回 10 条 |
| unit list | 成功，本页返回 10 条 |
| offline report advertiser | 成功，本页返回 1 条，总数 1 |
| offline report campaign | 成功，本页返回 10 条，总数 32 |
| offline report unit | 成功，本页返回 10 条，总数 32 |
| realtime report advertiser | 成功 |
| realtime report campaign | 成功，本页返回 10 条 |
| realtime report unit | 成功，本页返回 10 条 |
| realtime report creativity | 成功，本页返回 10 条 |

失败但已定位：

| 接口 / 层级 | 状态 | 判断 |
|---|---|---|
| account balance | 404 + SDK decode mismatch | 非 P0 投放表现阻塞项 |
| creativity search | 平台实际返回数据，但 SDK 字段类型不匹配 | 创意详情 / 创意维表进入 P0.5 |
| offline report creativity | 404 + SDK decode mismatch | 创意离线事实表进入 P0.5，需后续确认路径/权限/SDK |

## 数据契约输出摘要

新增文件：

`docs/data-contract/xiaohongshu-readonly-data-contract-v0.md`

该文档已收敛：

- 已验证对象层级：`advertiser -> campaign -> unit -> creativity / keyword`
- P0 表：
  - `xhs_advertiser_daily_fact`
  - `xhs_campaign_daily_fact`
  - `xhs_unit_daily_fact`
- P0.5 表：
  - `xhs_creativity_realtime_fact`
  - `xhs_creativity_daily_fact`
  - `xhs_creativity_dim`
  - `xhs_keyword_daily_fact`
- 字段映射：
  - `fee -> spend` 只在统一层映射，底层保留 `fee`
  - `unit_id` 保留小红书原生命名，不强行改成 `adset`
  - `note_id` 只作为素材映射候选线索，不等于 `material_id`
- Architecture Decision：
  - campaign/unit 先行
  - 创意层 P0.5
  - `unit` 保留原生命名
  - `fee` 保留原始字段
  - `note_id` 不进入 A 线契约
  - 关键词层级不进入 P0

## Architecture 需要今日拍板

建议 Architecture 只拍板上传安排，不在今天扩展工程范围。

需要确认：

1. 今天 GitHub 是否上传 spike 程序和数据契约草案。
2. `outputs/xiaohongshu/xhs_api_readonly_spike.md` 是否上传。
   - 默认建议不上传。
   - 如需上传，建议先复制成更短的公开摘要，去掉接口返回数量、token masked prefix、advertiser_id masked pattern 和真实运行时间。
3. 是否接受 P0 只包含 advertiser/campaign/unit，创意层进入 P0.5。
4. 是否接受 `note_id` 仅作为素材映射候选线索，不改 A 线 `material_ad_mapping`。
5. 是否要求在上传前把 `tools/xhs-readonly-spike/main.go` 中的接口列表再加一段 read-only guard 注释。

## 推荐上传包

如果 Architecture 今天同意上传，推荐最小上传包：

```text
config/examples/xhs.env.example
tools/xhs-readonly-spike/go.mod
tools/xhs-readonly-spike/go.sum
tools/xhs-readonly-spike/main.go
docs/handoff/2026-05-20-xhs-readonly-spike-architecture-handoff.md
docs/handoff/2026-05-20-xhs-work-output-github-upload-handoff.md
docs/data-contract/xiaohongshu-readonly-data-contract-v0.md
```

不建议今日上传：

```text
outputs/xiaohongshu/xhs_api_readonly_spike.md
config/private/
runtime/private/
```

## Suggested Commit Message

如果后续由 GitHub 会话执行提交，建议提交信息：

```text
Add Xiaohongshu read-only spike contract
```

建议 PR / 提交说明要点：

```text
- Add a read-only Xiaohongshu Spotlight API spike using bububa/spotlight-mapi.
- Add xhs env example without secrets.
- Document verified object hierarchy, readable report grains, and SDK schema gaps.
- Add Xiaohongshu read-only data contract v0 with P0/P0.5 table boundaries.
- Keep material_dim and material_ad_mapping unchanged; note_id remains an Architecture Decision.
```

## Safety Checklist Before Upload

上传前请确认：

- `config/private/` 未进入上传范围。
- `.env` / `.env.*` 未进入上传范围。
- `outputs/xiaohongshu/xhs_api_readonly_spike.md` 默认不上传。
- 没有完整 token、refresh token、app secret、advertiser_id。
- 没有原始 API 响应。
- 没有 GitHub push 到公开仓库前的隐私确认缺口。
- A 线 `material_dim` / `material_ad_mapping` 未被修改。

## 下一步建议

Architecture 今日建议只做一个判断：

```text
是否按“推荐上传包”进入 GitHub 上传准备。
```

如果确认，再交给 GitHub / Dev 会话做上传前的最后安全扫描和实际提交；不要在 Architecture 会话里继续修 SDK 或扩展生产同步。
