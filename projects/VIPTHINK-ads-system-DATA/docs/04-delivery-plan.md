# 04 交付计划

## 当前状态

项目已在当前目录完成干净初始化、Phase 1 的最小 read-only adapter、mock fixture、诊断/草稿/复盘内核和写操作阻断测试、Phase 2 的本地可启动产品骨架，并完成 Phase 3 的 live read-only adapter 合同实现。

已完成一次 live read-only 验证；详细运行结果和截图保存在 `runtime/private/`，不进入 GitHub。尚未初始化 GitHub 仓库。

## Phase 0: 干净初始化

交付物：

- `README.md`
- `docs/00-project-charter.md`
- `docs/01-first-closed-loop-prd.md`
- `docs/02-architecture.md`
- `docs/03-meta-readonly-contract.md`
- `docs/04-delivery-plan.md`
- `src/`
- `tests/`
- `runtime/private/`
- `.gitignore`

验收：

- 当前目录是独立项目目录。
- 文档明确不继承旧项目包袱。
- 私有数据目录默认不提交。

## Phase 1: Read-only Adapter 与安全阻断

目标：

- 定义 Meta read-only adapter interface。
- 使用 mock fixture 跑通账户 / Campaign / Ad Set / Ad 摘要。
- 实现 unsafe write blocker。
- 加测试证明危险动作 blocked。

当前结果：

- 已新增 `src/meta_ads_closed_loop/adapters/meta_readonly/`。
- 已新增 `src/meta_ads_closed_loop/domain/diagnostics.py`、`drafts.py`、`reports.py`、`safety.py`。
- 已新增 `tests/fixtures/meta_audit_dataset_minimal.json`。
- 已新增 `tests/test_phase1_closed_loop_core.py`。

验证命令：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

最近结果：

```text
Ran 5 tests in 0.001s
OK
```

停止条件：

- 如果旧项目 connector 迁移会带入 UI、旧文档树或多版本包袱，只迁移读取思想和测试边界。

## Phase 2: 第一条本地闭环页面

目标：

- 本地打开产品骨架。
- 展示账户总览、Campaign 列表、异常诊断、本地优化草稿、安全确认、报表复盘。
- 用户可见内容使用简体中文。

当前结果：

- 已新增 `src/meta_ads_closed_loop/app/local_ui/build.py`。
- 已新增 `src/meta_ads_closed_loop/app/local_ui/static/index.html`。
- 已新增 `src/meta_ads_closed_loop/app/local_ui/static/app.js`。
- 已新增 `src/meta_ads_closed_loop/app/local_ui/static/styles.css`。
- 已新增 `scripts/build_local_ui.py`。
- 已新增 `tests/test_phase2_local_ui.py`。
- 生成页面位于 `runtime/private/local_ui/index.html`。

启动命令：

```bash
PYTHONPATH=src python3 scripts/build_local_ui.py
python3 -m http.server 8765 --directory runtime/private/local_ui
```

本地地址：

```text
http://127.0.0.1:8765/
```

最近验证：

```text
PYTHONPATH=src python3 -m unittest discover -s tests -v
Ran 7 tests in 0.003s
OK
```

浏览器验证：

- 桌面账户总览可加载 7 个指标。
- Campaign 列表可展示 2 行。
- `有诊断` 筛选可用。
- 异常诊断可生成本地草稿。
- 安全确认可模拟暂停并新增 blocked 记录。
- 移动端 390px 宽度无 body 横向溢出。
- 截图保存在 `runtime/private/qa/`。

验收：

- 页面不是静态信息图。
- 投放师能按页面完成一次实际检查流程。

## Phase 3: Live Read-only 验证

目标：

- 使用本地私有凭证读取真实 Meta 数据。
- 不把凭证写入项目。
- 记录验证命令和结果。

当前结果：

- 已新增 `src/meta_ads_closed_loop/adapters/meta_readonly/live.py`。
- 已新增 `scripts/meta_readonly_live.py`。
- 已新增 `config/examples/meta.env.example`。
- 页面已支持 `--source live` 从真实 read-only 数据生成。
- UI 已展示投放账户、Campaign、Ad Set、Ad 和creative_asset基础信息。

凭证边界：

- live read-only 验证使用本机私有 env 或 `runtime/private/meta/.env`。
- 不在文档中记录真实 env 绝对路径、token、账号名称或账号 ID。

验证命令：

```bash
PYTHONPATH=src python3 scripts/meta_readonly_live.py --env runtime/private/meta/.env --mode list-accounts
PYTHONPATH=src python3 scripts/build_local_ui.py --source live --env runtime/private/meta/.env --account-id act_xxx
```

最近 live 验证：

```text
mode: Meta read-only
api_version: v25.0
account_discovery: succeeded
selected_account: redacted_real_account
selected_account_id: redacted
object_tree_read: succeeded
insights_read: succeeded
business_metrics: redacted_real_spend_leads_purchases_lpv
private_evidence_location: runtime/private/
```

说明：

- `objects_read` 是本次分页读取到的对象数量，不一定等于 Meta 账户历史全量上限。
- 诊断和 Campaign 表当前基于近 7 天 insights 有数据的对象。
- REDACTED_CREATIVE_FIELDS当前读取广告关联的 `creative` 引用和可见基础信息，深层creative_asset详情需要单独的 creative 详情读取切片。

停止条件：

- 如果凭证或权限不可用，输出权限缺口清单，不声明实时打通。

## Phase 4: XMP 参考补齐

目标：

- 在第一条闭环可用后，再参考 XMP 补齐工作流。
- 优先考虑自动创建、本地creative_asset资产、任务中心、报表、账号权限等模块。

非目标：

- 不机械复刻 XMP 信息架构。
- 不为了“像平台”牺牲第一条闭环。
