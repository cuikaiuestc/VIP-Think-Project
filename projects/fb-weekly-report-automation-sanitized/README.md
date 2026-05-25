# FB 周报自动化 1.0 裁剪版 / 脱敏版

这是 FB 周报自动化生成器的公司内部展示/协作版本。当前仓库包已经做强脱敏和能力裁剪，只保留从 sample registry 与 sample normalized facts 生成 Markdown / Excel / HTML 周报的最小可演示流程。

本包不适合完全公开传播。需要生产接入、完整数据刷新、问答助手、诊断策略或自动化决策能力的同事，请联系项目 owner。

## 项目能力

- 读取 registry 中登记的本地 normalized facts。
- 对标投放团队目前产出的 FB 渠道周报，生成 Markdown、Excel、HTML 示例输出。
- 输出模块状态表，区分 auto / partial / manual / blocked。
- 输出数据提取链路审计，标明每个模块的数据来源、时间窗、过滤条件与人工边界。
- 保留 manual material supplement CSV，用于素材展示链接、素材图片文件、人工备注等人工字段。
- 提供脱敏检查脚本，检查常见凭证形态、真实本机路径、手机号、IP、真实业务标识等风险。

## 不包含什么

- 不包含真实业务数据、真实 raw snapshots、真实 normalized facts。
- 不包含 SmartBI DATA CLI 源码、登录流程、刷新任务或私有配置。
- 不包含 FB 投放问答助手大脑、投放诊断策略、route contract、paid-ads expert 逻辑。
- 不包含 Meta、SmartBI、Feishu 的任何凭证。
- 不写 Feishu，不写 Obsidian，不调用 Meta API，不触碰广告账户。
- 不输出自动停投、加预算、调结构等经营动作建议。

## 目录结构

```text
.
├── data/
│   ├── manual_material_supplement_template.csv
│   ├── sample_manifest.json
│   ├── sample_registry.json
│   └── normalized_facts/
├── docs/
│   ├── DATA_CONTRACT.md
│   ├── SECURITY_BOUNDARY.md
│   └── SMARTBI_INTERFACE.md
├── scripts/
│   ├── check_sanitization.py
│   └── generate_fb_weekly_report.py
├── outputs/generated/
├── pyproject.toml
└── requirements.txt
```

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_fb_weekly_report.py
python scripts/check_sanitization.py
```

默认输出：

- `outputs/generated/FB_weekly_report_sanitized_2026-05-25.md`
- `outputs/generated/FB_weekly_report_sanitized_2026-05-25.xlsx`
- `outputs/generated/FB_weekly_report_sanitized_2026-05-25.html`
- `outputs/generated/FB_weekly_report_sanitized_2026-05-25_manifest.json`

## 输入数据契约

入口文件是 `data/sample_registry.json`。registry 只登记本地 sample facts，不刷新外部数据。

核心字段：

- `status`: sample registry 状态。
- `data_as_of`: 示例数据日期。
- `coverage`: 示例时间窗覆盖情况。
- `facts`: 各模块读取的 normalized facts 路径。
- `known_gaps`: manual / partial / blocked 边界。

normalized facts 使用 CSV，字段结构见 [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md)。

## 输出文件

生成器会写入 `outputs/generated/`：

- Markdown：适合代码审阅和文档转发。
- Excel：适合周报表格检查。
- HTML：适合浏览器预览。
- manifest：记录生成时间、输出路径、模块状态和执行边界。

## 安全与合规边界

本包只用于公司内部展示/协作。所有样例数据均为 mock/sample，仅保留字段结构和生成流程。生产接入必须在 owner 确认后，单独接入受控数据刷新流程，并继续保留人工确认边界。

GitHub 推送前必须确认仓库可见性、分支和 owner 授权。如果目标仓库可被外部访问，必须再次确认后才能 push。

## 维护者联系说明

完整能力包括 SmartBI DATA CLI 刷新、真实数据 registry、FB 投放问答助手、投放诊断策略和生产接入流程。本裁剪包不含这些能力。如需接入，请联系项目 owner。
