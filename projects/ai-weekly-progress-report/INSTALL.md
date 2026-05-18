# ai-weekly-progress-report 安装与清理

## 先清理旧版

请先清理旧版 `ai-weekly-progress-report` Skill，再安装新包。

1. 删除当前 AI 工具全局 Skills 目录里的旧版 `ai-weekly-progress-report` 文件夹。
   常见位置：
   - Codex: `~/.codex/skills/ai-weekly-progress-report`
   - TRAE: 对应全局 Skills 目录下的 `ai-weekly-progress-report`
   - QClaw/OpenClaw: 对应全局 Skills 目录下的 `ai-weekly-progress-report`

2. 删除本机旧的周报 profile，避免沿用历史汇报人或团队信息：
   - `~/.ai-weekly-progress-report/profile.json`

3. 不要删除业务项目目录、Codex/Trae/QClaw 的历史对话目录，也不要清空整个 `~/.codex`、`~/.trae`、`~/.qclaw`。
   这些是周报要扫描的证据来源，不是缓存。

## 安装新包

把 `dist/ai-weekly-progress-report-0.2.3.zip` 解压到当前 AI 工具的全局 Skills 目录，目录名必须保持为：

```text
ai-weekly-progress-report
```

安装后确认：

- `ai-weekly-progress-report/VERSION` 是 `0.2.3`
- 包内存在 `SKILL.md`
- 包内存在 `scripts/collect_ai_weekly_report.py`

## 启动正式流程

```text
使用 ai-weekly-progress-report，按正式流程生成本周 AI 周进度汇报。
```
