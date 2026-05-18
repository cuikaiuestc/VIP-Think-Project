# BI/Meta 报表整理 - 阶段 0 项目与工具盘点

生成日期：2026-05-18

## 当前产物

本阶段只完成本地项目与工具盘点，未读取 SmartBI，未读取真实 Meta，未访问数据库，未执行任何写操作。

结论：

- 当前项目是 `Meta 投放闭环系统`，中心能力是 Meta/Facebook read-only 投放数据读取、本地诊断、本地草稿和报表复盘。
- 当前项目具备 Meta readonly 参考能力，可作为后续 BI 字段映射中的 Meta 字段参考来源。
- 当前项目内未内置 SmartBI CLI、SmartBI 配置、SmartBI 报表目录读取脚本或 BI 报表导出样例。
- 用户已确认 SmartBI Data CLI 位于本机跨项目工具目录；公开文档不记录本机绝对路径。
- 因此阶段 1 可以复用 `date-solution` 的 SmartBI Data CLI 做只读目录/字段探测；但目标目录、报表范围和是否只读元数据仍需在执行前确认。
- 已用用户授权的本地凭证文件完成 SmartBI 目录只读探测，确认目标入口为 `REDACTED_INTERNAL_BI_ROOT`。

验证命令：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

验证结果：

```text
Ran 10 tests in 0.004s
OK
```

## 已发现的本地相关文件

项目文件数量：

- `rg --files`：62 个文件，包含 `runtime/private` 与 `__pycache__`。
- 排除 `runtime/private` 与 `__pycache__` 后：35 个文件。

与 Meta/Facebook/BI/投放强相关的本地文件：

| 文件 | 用途判断 | 阶段 1 可复用性 |
|---|---|---|
| `README.md` | 项目边界、Meta read-only 启动方式、安全约束 | 高 |
| `docs/03-meta-readonly-contract.md` | Meta/Facebook 只读合同、凭证处理、禁止写入范围 | 高 |
| `docs/04-delivery-plan.md` | 当前交付状态、live readonly 验证命令、已读字段范围 | 高 |
| `docs/handoff/2026-05-17-meta-closed-loop-live-readonly-handoff.md` | 上次 live readonly 验证交接与注意事项 | 中高 |
| `config/examples/meta.env.example` | Meta 本地私有配置模板 | 中 |
| `scripts/meta_readonly_live.py` | Meta 账户发现与 snapshot 只读导出入口 | 高 |
| `scripts/build_local_ui.py` | 基于 fixture 或 live Meta 数据生成本地页面 | 中 |
| `src/meta_ads_closed_loop/adapters/meta_readonly/live.py` | Meta Graph API GET-only live adapter | 高 |
| `src/meta_ads_closed_loop/adapters/meta_readonly/adapter.py` | Meta 字段标准化与 action_type 归类 | 高 |
| `src/meta_ads_closed_loop/adapters/meta_readonly/models.py` | 标准化后的 Campaign/Ad Set/Ad 数据模型 | 高 |
| `tests/fixtures/meta_audit_dataset_minimal.json` | 脱敏 Meta-like fixture | 中高 |
| `tests/test_phase3_live_adapter_contract.py` | live adapter 合同测试和脱敏测试 | 高 |

当前项目内未发现：

- 内置 SmartBI CLI。
- 内置 SmartBI 登录或目录读取配置。
- 内置 SmartBI 报表导出脚本。
- BI 回写表样例。
- BI 报表字段导出文件。
- “REDACTED_ADS_DOMAIN”目录结构缓存。

## 可安全使用的工具

### SmartBI Data CLI 只读工具

SmartBI CLI 不在当前项目内，而是在本机跨项目工具目录：

```text
<local-tools>/scripts/smartbi_cli.py
```

配套文档：

```text
<local-tools>/docs/smartbi_cli_v1.md
```

主配置：

```text
<local-tools>/configs/smartbi_tasks.json
```

SmartBI 服务地址：

```text
https://bi.61info.cn/smartbi/vision
```

已验证命令：

```bash
cd <local-tools>
python3 scripts/smartbi_cli.py --help
python3 scripts/validate_smartbi_config.py configs/smartbi_tasks.json
python3 scripts/smartbi_cli.py run --config configs/smartbi_tasks.json --task outbound_quality_hk_nonbulk_previous_week --dry-run --json
python3 scripts/smoke_smartbi_cli.py --json
```

验证结果：

- CLI 支持 `catalog-list`、`inspect-report`、`catalog-draft`、`run` 等命令。
- `configs/smartbi_tasks.json` 校验通过。
- dry-run 成功，不登录 BI，不读取真实报表。
- smoke 检查通过，包含 `no_plaintext_secrets`。
- 当前维护配置里的任务路径是 `分析报表/REDACTED_BUSINESS_LINE/海外产运/外呼/...`，不是本次 Facebook 投放报表目录。

可用于阶段 1 的只读命令形态：

```bash
cd <local-tools>
python3 scripts/smartbi_cli.py catalog-list --path '待确认的SmartBI目录路径'
python3 scripts/smartbi_cli.py catalog-draft --path '待确认的SmartBI目录路径' --out outputs/bi_catalog_drafts/facebook_ads_catalog_draft_2026-05-18.json --json
python3 scripts/smartbi_cli.py inspect-report --report-id '待确认report_id' --report-path '待确认report_path' --json
```

凭证规则：

- 不写入配置文件。
- 通过 `SMARTBI_USERNAME`、`SMARTBI_PASSWORD` 环境变量或 CLI 参数传入。
- 阶段 1 优先做目录与字段结构探测；如需导出明细，先暂停确认。
- 本机可用的凭证文件不进入 GitHub；只允许 source 后注入环境变量，不在报告中打印账号或密码。

### 已验证的 SmartBI 目标目录

已串行执行：

```bash
source <local-secret-env>
python3 scripts/smartbi_cli.py catalog-list --path '分析报表/REDACTED_BUSINESS_LINE' --json
python3 scripts/smartbi_cli.py catalog-list --path 'REDACTED_INTERNAL_BI_ROOT' --json
python3 scripts/smartbi_cli.py catalog-list --path 'REDACTED_INTERNAL_BI_ROOT' --recursive --max-depth 3 --json
```

确认 SmartBI 入口：

```text
REDACTED_INTERNAL_BI_ROOT
```

一级分支：

| 分支 | 类型 | 路径 |
|---|---|---|
| REDACTED_FOLDER_A | DEFAULT_TREENODE | `REDACTED_INTERNAL_BI_ROOT/REDACTED_FOLDER_A` |
| REDACTED_FOLDER_B | DEFAULT_TREENODE | `REDACTED_INTERNAL_BI_ROOT/REDACTED_FOLDER_B` |

初步候选报表：

| 报表 | 类型 | 初步用途判断 |
|---|---|---|
| REDACTED_REPORT_M | SPREADSHEET_REPORT | 目标达成/周期监控 |
| 投放分渠道目标达成 | SPREADSHEET_REPORT | 渠道目标达成 |
| REDACTED_REPORT_E | SPREADSHEET_REPORT | 区域维度全链路 |
| REDACTED_REPORT_F | SPREADSHEET_REPORT | 城市/REDACTED_DIM_REGION_TIER维度 |
| REDACTED_REPORT_G | SPREADSHEET_REPORT | 日REDACTED_CONVERSION_A_COST |
| 投放日播报 | SPREADSHEET_REPORT | 日常经营播报 |
| REDACTED_REPORT_A | SPREADSHEET_REPORT | Facebook creative_asset维度链路 |
| 投放渠道REDACTED_CONVERSION漏斗达成_周维度 | SPREADSHEET_REPORT | 渠道漏斗周维度 |
| 投放渠道REDACTED_CONVERSION漏斗累计达成_周维度 | SPREADSHEET_REPORT | 渠道漏斗累计达成 |
| REDACTED_REPORT_B | SPREADSHEET_REPORT | Facebook 渠道日监控 |
| REDACTED_REPORT_H | SPREADSHEET_REPORT | 广告空耗异常 |
| REDACTED_REPORT_I | SPREADSHEET_REPORT | 新老计划空耗异常 |
| REDACTED_REPORT_C | SPREADSHEET_REPORT | Facebook 链路类型日监控 |
| REDACTED_REPORT_D | SPREADSHEET_REPORT | Facebook 区域测试 |
| REDACTED_REPORT_K | SIMPLE_REPORT | REDACTED_PAGE_FLOW_SOURCE/源表候选 |
| REDACTED_REPORT_L | SIMPLE_REPORT | REDACTED_PAGE_FLOW_SOURCE/源表候选 |
| REDACTED_REPORT_J | SPREADSHEET_REPORT | REDACTED_PAGE_FLOW |
| 投放APPREDACTED_CONVERSION漏斗 | SPREADSHEET_REPORT | App REDACTED_CONVERSION漏斗 |

### 本项目使用 SmartBI Data CLI 的判断

`SmartBI Data CLI` 应作为跨项目只读能力层复用，不建议复制进当前 `投放系统demo`。

推荐分层：

| 层级 | 放置位置 | 职责 |
|---|---|---|
| CLI 能力层 | `date-solution/scripts/smartbi_cli.py` 及相关 helper | 登录、目录读取、报表 inspect、catalog draft、受控导出 |
| 报表需求层 | 当前项目 `docs/` 或后续 `configs/` | 记录本项目要盘点哪些 SmartBI 路径、报表、字段、过滤条件和产物要求 |
| 运行产物层 | 优先 `runtime/private/` 或 `date-solution/outputs/` | 保存原始 catalog JSON、导出文件、run log；不提交敏感明细 |
| 整理产物层 | 当前项目 `docs/` | 保存脱敏后的报表资产清单、字段字典、差异表和分析任务框架 |

原因：

- CLI 已经把“具体报表要求”从“读取能力”里解耦：任务配置保存 report id、path、filter、output；CLI 只负责按配置执行。
- 本项目需要沉淀的是 Facebook/Meta 投放报表口径和字段映射，不需要拥有 SmartBI 登录/导出实现。
- 复制 CLI 会造成维护分叉；跨项目复用 `date-solution` 的 CLI 更稳。
- 当前项目可以只保存一份轻量的 SmartBI 盘点任务说明，必要时再生成项目专属 config draft。

### Meta readonly 参考工具

当前项目可安全使用以下本地工具作为 Meta 字段参考，不应把它们当作 BI 真实口径：

```bash
PYTHONPATH=src python3 scripts/meta_readonly_live.py --env runtime/private/meta/.env --mode list-accounts
```

用途：

- 发现 token 可见的 Meta 投放账户。
- 只执行 Graph API GET 请求。
- 输出 token 时使用脱敏展示。

```bash
PYTHONPATH=src python3 scripts/meta_readonly_live.py --env runtime/private/meta/.env --mode snapshot --account-id act_xxx --max-pages 1
```

用途：

- 读取指定账户的只读 snapshot。
- 默认输出到 `runtime/private/meta/live_snapshot.json`。
- 可用于生成 Meta 字段参考清单。

```bash
PYTHONPATH=src python3 scripts/build_local_ui.py --source live --env runtime/private/meta/.env --account-id act_xxx
```

用途：

- 用真实 Meta readonly 数据生成本地页面。
- 不包含发布、暂停、预算、出价、creative_asset替换、删除等写操作。

### 已确认的 Meta 字段参考范围

账户字段：

- `id`
- `name`
- `currency`
- `timezone_name`
- `account_status`
- `amount_spent`
- `balance`
- `spend_cap`
- `business`

Campaign 对象字段：

- `id`
- `name`
- `objective`
- `status`
- `effective_status`
- `buying_type`
- `bid_strategy`
- `daily_budget`
- `lifetime_budget`
- `created_time`
- `updated_time`

Ad Set 对象字段：

- `id`
- `name`
- `campaign_id`
- `optimization_goal`
- `billing_event`
- `bid_strategy`
- `daily_budget`
- `lifetime_budget`
- `status`
- `effective_status`
- `created_time`
- `updated_time`

Ad 与REDACTED_CREATIVE_FIELDS：

- `id`
- `name`
- `campaign_id`
- `adset_id`
- `creative.id`
- `creative.name`
- `creative.title`
- `creative.body`
- `creative.thumbnail_url`
- `creative.image_url`
- `creative.video_id`
- `creative.object_story_spec`
- `status`
- `effective_status`
- `created_time`
- `updated_time`

Insights 字段：

- `date_start`
- `date_stop`
- `campaign_id`
- `campaign_name`
- `adset_id`
- `adset_name`
- `ad_id`
- `ad_name`
- `spend`
- `impressions`
- `reach`
- `frequency`
- `clicks`
- `inline_link_clicks`
- `ctr`
- `cpc`
- `cpm`
- `actions`
- `cost_per_action_type`

当前本地标准化 action_type 归类：

| 标准指标 | Meta action_type |
|---|---|
| leads | `lead`, `onsite_conversion.lead`, `onsite_conversion.lead_grouped`, `onsite_web_lead`, `offsite_complete_registration_add_meta_leads` |
| purchases | `purchase`, `omni_purchase`, `web_in_store_purchase`, `web_app_in_store_purchase`, `onsite_web_purchase`, `onsite_web_app_purchase`, `offsite_conversion.fb_pixel_purchase` |
| landing_page_views | `landing_page_view`, `omni_landing_page_view` |

标准化后的本地模型字段：

- Campaign：`id`, `name`, `status`, `spend`, `impressions`, `clicks`, `leads`, `purchases`, `landing_page_views`, `currency`, `cpl`, `cpa`, `ctr`
- Ad Set：`id`, `name`, `campaign_id`, `campaign_name`, `status`, `spend`, `impressions`, `clicks`, `landing_page_views`, `leads`, `purchases`, `currency`, `cpl`, `cpa`, `ctr`
- Ad：`id`, `name`, `campaign_id`, `campaign_name`, `adset_id`, `adset_name`, `status`, `spend`, `impressions`, `clicks`, `landing_page_views`, `leads`, `purchases`, `currency`, `creative`, `cpl`, `cpa`, `ctr`

## 不能做的动作

当前阶段不能做：

- 不能在未确认读取边界前导出 SmartBI 明细数据。
- 不能声明已经拿到 BI 报表资产清单。
- 不能把 Meta fixture 或 live adapter 字段等同于 BI 报表字段。
- 不能输出 BI 字段口径结论。
- 不能访问或打印真实 Meta token。
- 不能读取、写入或修改 SmartBI、数据库、广告账户。
- 不能上传、发布、push 到 GitHub。
- 不能创建 recurring automation。

## 建议进入阶段 1 的条件

满足以下任一条件后，可以进入阶段 1：

1. 用户确认阶段 1 只做目录、报表类型、参数和字段结构探测，暂不导出明细。
2. 用户确认是否优先 inspect 全部 Facebook/Meta 候选报表，还是先选 3-5 张核心报表。
3. 用户确认原始 catalog JSON/run log 放在 `runtime/private/` 或 `date-solution/outputs/`。
4. 用户提供或确认必须优先核对的内部业务字段。
5. 如需补充，用户提供 SmartBI 报表截图、字段样例或投放师手动下载的 Meta 表头。

进入阶段 1 前，建议先确认：

- SmartBI 目标路径是否为“REDACTED_ADS_DOMAIN”一级目录。
- 是否允许读取子目录。
- 是否只读取目录和字段结构，暂不导出明细行。
- 是否有必须优先处理的 3-5 张核心报表。
- 是否允许使用已有 Meta readonly 字段作为字段映射参考。

## 下一确认闸口

请确认以下问题后再进入阶段 1：

1. 阶段 1 是否只 inspect 报表参数和结构，暂不导出任何明细？
2. Facebook/Meta 候选报表是否全部纳入，还是优先这几张：`REDACTED_REPORT_A`、`REDACTED_REPORT_B`、`REDACTED_REPORT_C`、`REDACTED_REPORT_D`？
3. `REDACTED_REPORT_K/REDACTED_REPORT_L` 是不是这次也要纳入？它们是 `SIMPLE_REPORT`，需要单独 row guard。
4. 内部业务字段中，哪些必须优先核对：REDACTED_CONVERSION_A_COUNT、REDACTED_CONVERSION_B_COUNT、REDACTED_CONVERSION_C_COUNT、REDACTED_CONVERSION_COUNT、REDACTED_PAID_EVENT、REDACTED_REVENUE、ROI？
5. Meta 字段参考是否以当前项目的 readonly adapter 为准，还是以投放师手动下载的 Meta 表头为准？
6. 最终整理产物是否继续落在本项目 `docs/` 下，原始运行产物放在 `runtime/private/`？
