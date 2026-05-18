# Meta 投放闭环系统

这是一个独立新项目，用于构建面向投放师本地使用的 Meta read-only 投放闭环产品。

第一阶段目标不是做静态报告页、信息图或平台导航壳，而是完成一条真实可用闭环：

```text
读取真实 Meta 数据
-> 账户 / Campaign / Ad Set / Ad 总览
-> 识别异常或机会
-> 给出诊断证据
-> 生成本地优化草稿
-> 阻断真实写操作
-> 形成报表复盘
```

## 硬约束

- 本项目不继承旧项目的版本包袱、ABC 分工、旧 UI 或旧文档树。
- Meta/Facebook API 只允许 read-only。
- 禁止任何真实广告写操作，包括发布、暂停、预算、出价、creative_asset替换、复制后上线、删除。
- 本地只允许保存草稿、任务、笔记、报表配置和审计日志。
- 所有用户可见内容默认使用简体中文。
- XMP 只作为成熟产品参考，不替代第一条闭环目标。

## 当前阶段

当前已完成 Phase 0 干净初始化、Phase 1 最小工程内核，以及 Phase 2 本地可启动产品骨架：

- 项目边界文档
- 第一条闭环 PRD
- 技术架构草案
- Meta read-only 合同
- 交付计划
- `src/`、`tests/`、`runtime/private/` 初始目录
- Meta read-only adapter interface
- 脱敏 mock fixture
- 诊断、草稿、复盘的本地闭环内核
- 写操作阻断器
- safety tests
- 本地静态产品页面
- 账户总览、Campaign 列表、异常诊断、本地草稿、安全确认、报表复盘
- 浏览器交互验证截图

## 本地私有数据

后续 Meta token、ad account 配置、真实快照和本地运行私有数据只能放在 `runtime/private/` 或本机环境变量中，不写入公开文档或可提交配置。

## 本地启动

先生成本地页面：

```bash
PYTHONPATH=src python3 scripts/build_local_ui.py
```

再启动静态服务：

```bash
python3 -m http.server 8765 --directory runtime/private/local_ui
```

浏览器访问：

```text
http://127.0.0.1:8765/
```

## 真实 Meta Read-only 数据

当前页面默认使用 fixture。要切换到真实 Meta read-only 数据，先创建本地私有配置：

```bash
mkdir -p runtime/private/meta
cp config/examples/meta.env.example runtime/private/meta/.env
```

然后只在 `runtime/private/meta/.env` 填入本机私有值。

先列出当前 token 可见的投放账户：

```bash
PYTHONPATH=src python3 scripts/meta_readonly_live.py --env runtime/private/meta/.env --mode list-accounts
```

选择账户后生成真实 read-only 页面数据：

```bash
PYTHONPATH=src python3 scripts/build_local_ui.py --source live --env runtime/private/meta/.env --account-id act_xxx
```

这个流程只执行 Graph API GET 请求，不包含发布、暂停、预算、出价、creative_asset替换、删除等写操作。

## 验证命令

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
