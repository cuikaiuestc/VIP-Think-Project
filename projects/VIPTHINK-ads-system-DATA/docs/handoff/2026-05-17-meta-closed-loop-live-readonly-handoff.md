# Handoff

## Resume Focus

继续本项目的 `Meta 投放闭环系统`。当前已经完成干净初始化、mock 闭环、真实 Meta read-only 接入和本地页面展示。不要继续开发，先让新会话读清楚当前状态。

## Current Objective

构建一个面向投放师本地使用的 Meta read-only 投放闭环产品：

读取真实 Meta 数据 -> 查看投放账户 / Campaign / Ad Set / Ad / creative_asset基础信息 -> 诊断异常 -> 生成本地草稿 -> 阻断真实写操作 -> 复盘。

## Confirmed Decisions

- 新项目使用当前目录。
- 旧项目只作为参考库，不继续在旧项目叠版本。
- Meta API 只允许 read-only，禁止发布、暂停、预算、出价、creative_asset替换、删除等真实写操作。
- 本地允许保存草稿、任务、笔记、复盘、审计日志。
- 用户可见页面默认简体中文。
- 已允许使用本机私有 env 做 read-only 验证；真实 env 绝对路径不进入 GitHub。

## Pending Decisions / Blockers

- 是否继续做 deep creative 详情读取：当前只读到广告关联的 `creative` 引用和基础可见信息。
- 当前 Campaign 表和诊断基于近 7 天 insights 有数据的对象，不是全部历史 Campaign。
- `objects_read` 是本次分页读取到的对象数量，不一定等于 Meta 历史全量上限。
- 还没有 Git 初始化、GitHub 推送、生产部署或凭证迁移到新项目。
- 不要把旧项目私有 `.env` 内容复制进代码、文档或提交。

## Artifacts To Read First

- `README.md`
- `docs/00-project-charter.md`
- `docs/01-first-closed-loop-prd.md`
- `docs/03-meta-readonly-contract.md`
- `docs/04-delivery-plan.md`
- `src/meta_ads_closed_loop/adapters/meta_readonly/live.py`
- `src/meta_ads_closed_loop/app/local_ui/build.py`
- `src/meta_ads_closed_loop/app/local_ui/static/app.js`
- `tests/test_phase3_live_adapter_contract.py`

## Changed Files

- Added project docs, README, AGENTS, `.gitignore`
- Added read-only core:
  `/src/meta_ads_closed_loop/adapters/meta_readonly/`
- Added domain core:
  `/src/meta_ads_closed_loop/domain/`
- Added local UI:
  `/src/meta_ads_closed_loop/app/local_ui/`
- Added scripts:
  `/scripts/build_local_ui.py`
  `/scripts/meta_readonly_live.py`
- Added tests:
  `/tests/test_phase1_closed_loop_core.py`
  `/tests/test_phase2_local_ui.py`
  `/tests/test_phase3_live_adapter_contract.py`
- Added env template:
  `/config/examples/meta.env.example`

## Validation Already Run

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Result: `10 tests OK`.

Live Meta read-only validation:

- API version: `v25.0`
- account discovery succeeded.
- selected account name and account id are redacted.
- object tree and insights read succeeded.
- real spend, leads, purchases and LPV are redacted.
- detailed run evidence is stored under `runtime/private/` and must not enter GitHub.

Browser verified:

- Local URL: `http://127.0.0.1:8765/`
- Screenshot evidence is stored under `runtime/private/qa/` and must not enter GitHub.

## Risks / Watchouts

- Do not perform any Meta write operation.
- Do not expose or copy token contents.
- Do not confuse “已读取对象数” with total historical account objects.
- Do not treat current 3 Campaign rows as all Campaigns; those are near-term insight rows.
- Deep creative fields may trigger Graph errors if requested too aggressively; current implementation intentionally uses safer creative reference fields.

## Suggested Next Steps

1. Read the files listed above before editing.
2. If continuing development, first decide the next slice:
   - creative detail read-only enrichment, or
   - account selector UI, or
   - Campaign / Ad Set / Ad drilldown tables, or
   - diagnostics rules based on real Meta data.
3. Keep `read-only` tests passing.
4. If running live again:

```bash
PYTHONPATH=src python3 scripts/build_local_ui.py \
  --source live \
  --env runtime/private/meta/.env \
  --max-pages 10
```

5. Then verify browser at:

```text
http://127.0.0.1:8765/
```

## Suggested Skills

- `product-rd-commander`: product boundary and next slice gate.
- `software-engineering-commander`: implementation and test discipline.
- `paid-ads-growth-expert`: Meta 投放指标与诊断规则。
- `data-analyst`: 数据口径、分页、insights 解释。
- `handoff-builder`: next pause / transfer.

## Do Not Repeat

- 不要重新初始化项目。
- 不要回旧项目继续叠版本。
- 不要再做静态信息图。
- 不要把 XMP 信息架构机械套进来。
- 不要复制旧 UI / v0.1 / v0.2 / v0.3。
- 不要读取或打印真实 token。
- 不要执行任何 Meta 写操作。
