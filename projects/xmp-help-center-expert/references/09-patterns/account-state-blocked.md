---
title: "XMP 账号内状态阻断场景"
source: "https://help-xmp.mobvista.com/"
category: "09-patterns"
captured_at: "2026-05-13"
status: "derived-pattern"
source_hash: "manual"
aliases: "账号状态, 权限不足, 不能投放, 报错, 后台状态, delivery issue"
---

# XMP 账号内状态阻断场景

## Key Rules

- 公共帮助中心不能确认用户的账号权限、后台状态、投放结果、接口 token、广告账号绑定、审批或实时错误。
- 对这类问题使用 `blocked` 或 `tentative`，并要求用户提供 XMP 后台截图、错误提示、页面路径、账号角色或接口错误码。
- 可以给出帮助中心中应检查的文档入口，但不能把它当成具体账号诊断结论。

## Use Cases

- 我的账号为什么不能投放。
- 为什么看不到按钮或没有权限。
- API 为什么报错。
- 定时报表、素材同步、广告创建为什么失败。

## Official References

- `references/url_map.md`
- `references/09-patterns/xmp-help-routing.md`
- Relevant concrete reference after the user provides the affected module.

## Limitations

- 该模式本身不是官方故障原因说明，只是回答边界与证据要求。

## Source Trace

- Source URL: https://help-xmp.mobvista.com/
