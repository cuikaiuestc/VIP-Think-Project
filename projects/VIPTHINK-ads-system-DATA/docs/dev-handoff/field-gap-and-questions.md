# 字段缺口与开发反馈问题清单

生成日期：2026-05-18

## 必须先确认的判断

当前 4 张 FB `SPREADSHEET_REPORT` 都是 `pivot_dashboard`，不适合作为稳定系统源表。开发同事需要先反馈：

1. 是否接受短期解析 BI 透视 workbook？
2. 是否要求直接拿底层 SQL / 回写表 / 明细源表？
3. 是否接受先用 `REDACTED_REPORT_A` 做 P0 样本验证？

如果开发同事不接受透视表解析，本分支下一步应停止扩展 BI 看板字段，转向找底层数据源。

## P0 阻塞问题

| 问题 | 影响 | 需要谁反馈 |
|---|---|---|
| `广告ID` 是否稳定等于 Meta `ad_id`？ | 决定能否 join Meta 和内部REDACTED_CONVERSION | 开发 + 数据运营 |
| `广告组ID` 是否稳定等于 Meta `adset_id`？ | 决定 adset 粒度建模 | 开发 + 数据运营 |
| 是否存在 `campaign_id`、`account_id`？ | 当前报表只看到投放账户/广告组/广告，账户 ID 不明确 | 数据运营 |
| `投放账户` 是名称还是 ID？ | 名称不能做稳定主键 | 数据运营 |
| `REDACTED_CONVERSION_A_COUNT` 的归因规则是什么？ | 决定内部REDACTED_CONVERSION事实表口径 | 业务 + 数据运营 |
| `REDACTED_CONVERSION_B_COUNT` 的归因规则是什么？ | 决定REDACTED_CONVERSION_B_COST和优化判断 | 业务 + 数据运营 |
| `REDACTED_CONVERSION_C_COUNT`、`REDACTED_PAID_EVENT`、`GMV` 是当月还是滚动？ | 防止当月/滚动口径混用 | 业务 + 数据运营 |
| `消耗` 是否含 CPT？ | 报表中出现 `消耗`、`消耗(不含CPT)`，成本口径可能不一致 | 数据运营 |
| `ROI2` 公式是什么？ | 不能由开发猜公式 | 业务 + 数据运营 |
| `空耗金额/空耗占比` 定义是什么？ | 自动化系统是否能复刻空耗判断 | 业务 + 数据运营 |

## 字段来源缺口

### Meta/Facebook 字段

需要确认这些 BI 字段是否直接来自 Meta 下载数据：

- 广告ID
- 广告组ID
- 广告名称
- 投放账户
- 曝光
- 点击
- CPM
- CTR
- CVR
- 消耗

开发反馈问题：

```text
这些字段未来是否计划由 Meta API 自动拉取？
如果是，BI 字段只作为历史校验，不应作为长期系统源。
```

### 内部业务字段

这些字段 Meta API 不能直接提供：

- REDACTED_CONVERSION_A_COUNT
- REDACTED_CONVERSION_B_COUNT
- REDACTED_CONVERSION_C_COUNT
- REDACTED_PAID_EVENT
- GMV
- 当月REDACTED_PAID_EVENT
- 滚动REDACTED_PAID_EVENT

开发反馈问题：

```text
内部REDACTED_CONVERSION_COUNT据是否已有底层表？
能否按 ad_id/adset_id/date 粒度回传？
如果不能，最低可接受粒度是什么？
```

### REDACTED_INTERNAL_TAG字段

这些字段更像creative_asset或策略标签：

- REDACTED_CREATIVE_TYPE
- REDACTED_FLAG_A
- REDACTED_FLAG_B
- REDACTED_FLAG_C
- REDACTED_CREATIVE_SOURCE
- REDACTED_CREATIVE_PRODUCTION_PERIOD
- KOL
- REDACTED_CREATIVE_FORMAT_TAG
- REDACTED_REQUESTER

开发反馈问题：

```text
这些标签是否应该进入自动化投放系统？
如果进入，来源是 BI、creative_asset管理表，还是人工维护？
```

## 报表级反馈问题

| 报表 | 当前判断 | 反馈问题 |
|---|---|---|
| REDACTED_REPORT_A | 最有价值，但仍是 pivot_dashboard | 是否可接受作为短期 P0 样本？是否能提供底层 SQL？ |
| REDACTED_REPORT_B | 横向透视，缺对象主键 | 是否只作为看板校验，不进入系统接入？ |
| REDACTED_REPORT_C | 日期 x 链路类型透视 | 是否只作为趋势分析，不进入 P0？ |
| REDACTED_REPORT_D | 策略标签丰富，但主键弱 | 是否作为标签参考，而非事实表？ |
| REDACTED_REPORT_K | SIMPLE_REPORT，row guard 2406 | 是否允许下一步导出表头判断源表价值？ |
| REDACTED_REPORT_L | SIMPLE_REPORT，row guard 1121 | 是否允许下一步导出表头判断源表价值？ |

## 给开发同事的最小反馈模板

请开发同事按下面格式反馈：

```text
1. P0 数据源路线：
   A. 临时解析 BI 导出
   B. 找底层 SQL/回写表
   C. Meta API + 内部REDACTED_CONVERSION表

2. 可接受的最小主键：
   ad_id + date / adset_id + date / account + date / 其他

3. 不能接受的字段：
   ...

4. 需要业务确认的口径：
   ...

5. 需要新增 sample fixture 吗：
   是 / 否

6. 下一步开发前必须补齐：
   ...
```

## 建议停止条件

如果开发同事确认“不接受解析 BI 透视表作为系统数据源”，本分支不要继续抽取更多 `SPREADSHEET_REPORT` 字段，应改为：

```text
寻找底层回写表 / SQL / SIMPLE_REPORT 明细源
```

这是更低返工风险的路线。
