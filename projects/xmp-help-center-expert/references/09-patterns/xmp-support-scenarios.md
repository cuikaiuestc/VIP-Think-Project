---
title: "XMP 支持问题场景索引"
source: "https://help-xmp.mobvista.com/"
category: "09-patterns"
captured_at: "2026-05-12"
status: "derived-pattern"
source_hash: "homepage-2026-05-12"
aliases: "XMP 支持场景, 添加广告账号, 创建广告, 素材报表, 团队和用户管理"
---

# XMP 支持问题场景索引

## Key Rules

- 首页的“热门搜索”和“热门内容”可视为高频支持问题集合。
- 高频支持问题优先围绕广告账号、广告创建、素材报表、素材库、看板、FAQ、团队和用户管理。
- 回答支持问题时，应先明确用户是在找入口、概念解释、操作步骤、排错，还是 API 对接；当前首页知识只可靠覆盖入口和分类判断。

## Use Cases

- 用户说“我不知道去哪设置/查看/创建”。
- 用户只给出 XMP 功能名，需要判断应该查哪个模块。
- 构建后续 crawler 或知识库 refresh 的优先级列表。

## Scenario Priority

| Priority | Scenario | Homepage Evidence | Follow-up Need |
|---|---|---|---|
| P0 | 添加广告账号 | 热门搜索、热门内容、管理分类均出现 | 需要子页面补充操作步骤和权限要求 |
| P0 | 创建广告 | 热门搜索、热门内容、推广分类均出现 | 需要子页面补充创建流程和字段说明 |
| P0 | 素材报表 | 热门搜索、热门内容出现 | 需要子页面补充指标、筛选和导出说明 |
| P1 | XMP 素材库 | 热门内容、素材分类出现 | 需要子页面补充素材管理规则 |
| P1 | 看板 | 热门内容出现 | 需要子页面补充报表看板范围 |
| P1 | 团队和用户管理 | 热门搜索、管理分类出现 | 需要子页面补充角色和权限 |
| P2 | Open API | 分类出现，且包含请求协议、广告报表 API、素材报表 API、素材库 API | 需要完整 API 文档正文 |
| P2 | 功能更新公告 | 分类出现，按年份组织 | 需要按年份子页面抽取变更记录 |

## Suggested Validation Queries

- “XMP 怎么添加广告账号？”
- “XMP 创建广告的文档入口在哪里？”
- “素材报表和 XMP 素材库分别在哪个模块？”
- “XMP Open API 入口有哪些？”
- “哪里看 2026 年功能更新公告？”

## Limitations

- 这里是支持场景索引，不是操作手册。
- 对字段、按钮、权限、错误提示、API 参数的回答必须依赖后续子页面或产品内证据。

## Source Trace

- Raw capture: omitted from clean public release
- Manifest: omitted from clean public release
- Source URL: https://help-xmp.mobvista.com/

