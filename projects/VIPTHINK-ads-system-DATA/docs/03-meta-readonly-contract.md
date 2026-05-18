# 03 Meta Read-only 合同

## 合同目标

本合同定义本项目如何安全读取 Meta/Facebook 投放数据，以及哪些行为被明确禁止。

## 允许读取

允许读取用于本地诊断和复盘的账户、Campaign、Ad Set、Ad、insights 和基础对象状态数据。

读取结果可用于：

- 账户总览
- Campaign / Ad Set / Ad 列表
- 指标计算
- 异常诊断
- 本地优化草稿
- 本地报表复盘

## 禁止写入

禁止任何真实 Meta 写操作，包括：

- 发布广告
- 暂停或启用 Campaign / Ad Set / Ad
- 修改预算
- 修改出价
- 修改creative_asset
- 修改受众
- 修改排期
- 复制对象并上线
- 删除对象
- 任何会改变广告账户真实状态的 API 调用

## 本地替代动作

当用户触发危险动作时，系统只能执行本地替代动作：

- 显示 blocked 状态
- 生成本地草稿
- 写入本地审计日志
- 生成待人工处理任务

## 凭证处理

- 凭证不写入 README、docs、测试 fixture 或提交记录。
- 凭证优先从环境变量或 `runtime/private/` 下的本地私有配置读取。
- 对外展示、日志和报表必须脱敏。

## 测试要求

每个 adapter 必须满足：

- read-only 调用可以被单元测试或集成测试验证。
- 写操作方法不存在，或存在时永远返回 blocked。
- blocked 结果不应触发任何外部 HTTP 写请求。
- 测试 fixture 不包含真实 token。

## 权限不可用时的行为

如果 Meta 权限、token 或 ad account 不可用：

1. 不伪造“已实时打通”。
2. 使用 mock-to-live adapter 跑通产品闭环。
3. 输出权限缺口清单。
4. 等用户补齐本地私有凭证后再验证真实 read-only。

## 本项目当前接入方式

私有配置模板：

```text
config/examples/meta.env.example
```

本地私有配置位置：

```text
runtime/private/meta/.env
```

账户发现命令：

```bash
PYTHONPATH=src python3 scripts/meta_readonly_live.py --env runtime/private/meta/.env --mode list-accounts
```

真实 read-only 页面生成命令：

```bash
PYTHONPATH=src python3 scripts/build_local_ui.py --source live --env runtime/private/meta/.env --account-id act_xxx
```

读取范围：

- 可见投放账户列表。
- 选定账户的 Campaign。
- 选定账户的 Ad Set。
- 选定账户的 Ad。
- Ad 关联creative_asset基础信息。
- Campaign / Ad Set / Ad 层 insights。

仍然禁止：

- 任何非 GET 请求。
- 任何改变 Meta 广告账户状态的动作。
