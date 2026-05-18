# tests

测试优先覆盖两类风险：

1. read-only 数据读取和标准化是否可用。
2. 所有危险写动作是否被 blocked，且不会触发外部写请求。

当前测试命令：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Phase 1 已覆盖：

- mock read-only adapter 归一化账户、Campaign、Ad Set、Ad 摘要。
- 诊断规则生成本地草稿，且草稿不调用 Meta 写接口。
- 已知危险写动作全部 blocked。
- 未知写动作默认 blocked。
- 闭环复盘统计 read-only 数据、诊断、草稿和 blocked 事件。
