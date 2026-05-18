# 02 技术架构

## 架构原则

- read-only 优先：所有 Meta 外部 API 访问默认只读。
- local-first：草稿、任务、审计日志、报表配置先保存在本地。
- mock-to-live：没有凭证时使用 mock 数据，有凭证时切换真实 read-only adapter。
- 产品闭环优先：先完成账户总览到复盘的闭环，再补平台模块。
- 安全阻断可测试：所有危险动作必须有明确 blocker 和测试。

## 初始模块

```text
src/
  adapters/
    meta_readonly/
  domain/
    diagnostics/
    drafts/
    reports/
    safety/
  app/
    local_ui/
tests/
  adapters/
  domain/
  safety/
runtime/
  private/
```

当前初始化只创建顶层目录。模块目录将在下一步实现时按最小可用切片创建。

## 数据流

```text
Meta read-only API 或本地快照
-> 数据标准化
-> 指标与对象摘要
-> 诊断规则
-> 本地草稿
-> 安全阻断
-> 报表复盘
```

## 私有数据边界

- token、ad account id、真实快照、运行日志默认属于本地私有数据。
- 私有数据放入 `runtime/private/` 或环境变量。
- `runtime/private/` 已默认加入 `.gitignore`。

## 写操作阻断边界

禁止调用任何会改变 Meta 广告账户状态的 endpoint 或 SDK 方法，包括但不限于：

- 创建、更新、删除 Campaign / Ad Set / Ad
- 暂停或启用广告对象
- 修改预算、出价、排期、受众、creative_asset
- 发布、复制后上线、批量变更

本地允许动作：

- 保存草稿
- 保存任务
- 保存笔记
- 保存报表配置
- 写入本地审计日志

## 下一步工程切片

1. 定义 read-only adapter interface。
2. 加入 mock fixture。
3. 加入 unsafe write blocker。
4. 写 safety tests。
5. 再接入真实 Meta read-only 读取。
