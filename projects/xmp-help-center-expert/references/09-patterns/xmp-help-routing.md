---
title: "XMP 帮助中心入口路由"
source: "https://help-xmp.mobvista.com/"
category: "09-patterns"
captured_at: "2026-05-12"
status: "derived-pattern"
source_hash: "homepage-2026-05-12"
aliases: "XMP 帮助中心, XMP 文档入口, XMP 功能入口, XMP 导航"
---

# XMP 帮助中心入口路由

## Key Rules

- `XMP 帮助中心`首页是导航层，不是详细功能说明页；回答具体操作步骤前，应优先跳转或检索对应子页面。
- 首页显示的高频入口包括：添加广告账号、创建广告、AI 助手、素材报表、团队和用户管理。
- 首页的产品知识可按八个方向路由：推广、素材、管理、工具、AI 助手、XMP Open API、功能更新公告、快速入门/官网/博客入口。
- 当用户问“在哪里找”或“入口是什么”时，首页信息足够回答；当用户问“怎么操作”时，首页只提供候选文档入口，不足以给出完整步骤。

## Use Cases

- 用户问 XMP 帮助中心有哪些模块。
- 用户问某个 XMP 功能的文档入口。
- 需要判断一个问题应该进入“投放 / 素材 / 管理 / 工具 / AI / API / 更新公告”哪个知识区。

## Routing Map

| User Intent | Best Entry |
|---|---|
| 快速上手 XMP | `XMP 快速入门指南` -> `/docs/start-quickly` |
| 添加或管理广告账号 | `管理` -> `添加广告账号` -> `/docs/ZHB4DA` |
| 创建广告或批量管理广告 | `推广` -> `创建广告` / `批量管理广告` |
| 看素材效果或管理素材 | `素材` -> `素材报表` / `XMP 素材库` / `素材编辑` |
| 团队、用户、模板、产品管理 | `管理` -> `管理团队和用户` / `广告模板` / `产品管理` |
| Facebook、TikTok、YouTube、任务、定时报表 | `工具` 分类 |
| 自动优化、自动创建广告、一键上单 | `AI 助手` 分类 |
| API 对接、接口协议、广告/素材报表 API | `XMP Open API` 分类 |
| 版本变化和新功能 | `功能更新公告` 分类，按年份进入 |

## Limitations

- 当前知识层只包含首页，不包含各子页面的正文。
- 首页链接名称可作为检索线索，但不能替代子页面的操作细节、字段定义、权限限制或 API 参数说明。

## Source Trace

- Raw capture: omitted from clean public release
- Manifest: omitted from clean public release
- Source URL: https://help-xmp.mobvista.com/

