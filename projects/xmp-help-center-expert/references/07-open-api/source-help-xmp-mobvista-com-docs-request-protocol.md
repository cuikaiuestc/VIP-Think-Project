---
title: "接口请求协议"
source: https://help-xmp.mobvista.com/docs/request_protocol
category: 07-open-api
captured_at: 2026-05-12
status: distilled-source
source_hash: 059bf2f2b1b5e61f
aliases: XMP, Open API
source_type: official_help_center_doc
authority_level: official
confidentiality: public
---

# 接口请求协议

This is a compact distilled note. Use the raw source for audit, exact wording, or re-distillation.

## Key Rules

- ## 二、公共请求参数 1、Headers **参数** **传值** **必填** Content-Type application/json 2、Body **参数** **类型** **必填** **说明** client_id string 向公司管理员或子管理员获取。请确保已开通Open API权限 timestamp int 请求时的unix时间戳 sign string md5(client_secret+timestamp) 其他参数 3、请求示例 "client_id": "xxx",...
- title: "接口请求协议" source_url: "https://help-xmp.mobvista.com/docs/request_protocol" authority_level: "official" confidentiality: "public" captured_at: "2026-05-12" --- # 接口请求协议 ## 一、请求说明 - 大小写敏感：接口参数对大小写严格区分，请确保按文档要求填写。
- public static String getSign(String clientSecret) { long timestamp = System.currentTimeMillis()/1000;

## Use Cases

- Use when the user asks about 07 open api concepts related to 接口请求协议.
- Load this note as supporting evidence, then inspect raw source if exact wording or freshness matters.

## Limitations

- Do not treat this distilled note as the source of truth when exact wording, compliance, or freshness matters.
- Verify against the raw source before making high-stakes recommendations.

## Related Patterns

- `references/09-patterns/xmp-help-routing.md`

## Source Trace

- Input URL: https://help-xmp.mobvista.com/docs/request_protocol
- Final URL: https://help-xmp.mobvista.com/docs/request_protocol
- Row ID: ``
- Raw source: omitted from clean public release
- Capture run: `docs-2026-05-12`
- Raw chars: 1795
- Author: 
- Published at: 
- Tags: 
