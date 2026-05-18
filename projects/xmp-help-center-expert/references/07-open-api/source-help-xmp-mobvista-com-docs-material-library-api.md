---
title: "素材库API"
source: https://help-xmp.mobvista.com/docs/material_library_api
category: 07-open-api
captured_at: 2026-05-12
status: distilled-source
source_hash: 328ef0493cf47ee2
aliases: XMP
source_type: official_help_center_doc
authority_level: official
confidentiality: public
---

# 素材库API

This is a compact distilled note. Use the raw source for audit, exact wording, or re-distillation.

## Key Rules

- sync或空表示同步，返回参数有user_material_id data.file_sign string 源文件md5校验，可空。当有值时，会对下载的url文件进行校验。校验成功后才会入库。
- data.filter_duplicate Boolean 过滤重复素材，默认false。当为true表示，如果当前文件夹存在相同md5的素材时，则直接返回成功。允许名称不一致；
- 如果为false，则允许重复上传，名称相同时会自动增加数字后缀。

## Use Cases

- Use when the user asks about 07 open api concepts related to 素材库API.
- Load this note as supporting evidence, then inspect raw source if exact wording or freshness matters.

## Limitations

- Do not treat this distilled note as the source of truth when exact wording, compliance, or freshness matters.
- Verify against the raw source before making high-stakes recommendations.

## Related Patterns

- None mapped yet.

## Source Trace

- Input URL: https://help-xmp.mobvista.com/docs/material_library_api
- Final URL: https://help-xmp.mobvista.com/docs/material_library_api
- Row ID: ``
- Raw source: omitted from clean public release
- Capture run: `docs-2026-05-12`
- Raw chars: 18143
- Author: 
- Published at: 
- Tags: 
