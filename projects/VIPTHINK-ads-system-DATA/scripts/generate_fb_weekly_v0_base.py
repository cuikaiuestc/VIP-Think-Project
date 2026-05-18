#!/usr/bin/env python3
"""Generate the FB weekly V0 calibration workbook from SmartBI exports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "runtime" / "private" / "fb_weekly_v0"
EXPORT_ROOT = RUN_ROOT / "smartbi_exports"
INSPECT_ROOT = RUN_ROOT / "workbook_inspect"
OUTPUT = RUN_ROOT / "fb_weekly_v0_base_table.xlsx"


REPORTS = {
    "fb_material_chain_metrics": {
        "name": "REDACTED_REPORT_A",
        "path": EXPORT_ROOT / "fb_material_chain_metrics" / "2026-05-18" / "REDACTED_REPORT_A.xlsx",
        "role": "creative_asset维度表现 / 空耗候选",
    },
    "fb_channel_daily_monitor": {
        "name": "REDACTED_REPORT_B",
        "path": EXPORT_ROOT / "fb_channel_daily_monitor" / "2026-05-18" / "REDACTED_REPORT_B.xlsx",
        "role": "渠道与区域日监控",
    },
    "fb_link_type_daily_monitor": {
        "name": "REDACTED_REPORT_C",
        "path": EXPORT_ROOT / "fb_link_type_daily_monitor" / "2026-05-18" / "REDACTED_REPORT_C.xlsx",
        "role": "链路类型日监控",
    },
    "fb_hk_mo_test_report": {
        "name": "REDACTED_REPORT_D",
        "path": EXPORT_ROOT / "fb_hk_mo_test_report" / "2026-05-18" / "REDACTED_REPORT_D.xlsx",
        "role": "REDACTED_REGION_A/非REDACTED_REGION_A策略测试",
    },
}


FIELD_CATEGORY_RULES = [
    ("时间字段", ["日期", "周次", "开始", "结束", "上线"]),
    ("渠道字段", ["REDACTED_DIM_PLATFORM", "渠道", "FB", "链路", "表单", "Whats", "H5"]),
    ("地区字段", ["区域", "地区", "REDACTED_REGION_A", "REDACTED_REGION_GROUP_A", "REDACTED_REGION_B"]),
    ("账户/计划/广告字段", ["投放账户", "广告组", "广告ID", "广告名称", "账户类型", "新计划", "老计划"]),
    ("REDACTED_CREATIVE_FIELDS", ["creative_asset", "KOL", "创意", "REDACTED_CREATIVE_PRODUCTION_PERIOD", "预览链接", "口播"]),
    ("前端投放指标", ["曝光", "点击", "CTR", "CPM", "CVR", "IPM", "消耗"]),
    ("后端REDACTED_CONVERSION指标", ["REDACTED_CONVERSION_A", "REDACTED_CONVERSION_B", "REDACTED_CONVERSION_C", "REDACTED_PAID_EVENT", "REDACTED_PAID_EVENT", "GMV"]),
    ("派生指标", ["成本", "率", "ROI", "空耗", "成效"]),
]


def clean(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, str):
        return value.replace("\n", " ").strip()
    return value


def read_sheet(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path, sheet_name=0, header=None, dtype=object)
    frame = frame.dropna(how="all").dropna(axis=1, how="all")
    return frame.map(clean)


def make_unique(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    result = []
    for raw_name in names:
        name = raw_name or "空列"
        count = seen.get(name, 0) + 1
        seen[name] = count
        result.append(name if count == 1 else f"{name}_{count}")
    return result


def combine_headers(frame: pd.DataFrame, rows: list[int], *, fill_forward: bool = False) -> list[str]:
    headers: list[list[str]] = []
    for row in rows:
        values = ["" if value is None else str(value) for value in frame.iloc[row].tolist()]
        if fill_forward:
            last = ""
            filled = []
            for value in values:
                if value:
                    last = value
                filled.append(last)
            values = filled
        headers.append(values)
    names = []
    for col in range(frame.shape[1]):
        parts = []
        for row_values in headers:
            value = row_values[col].strip()
            if value and value not in parts:
                parts.append(value)
        names.append(" | ".join(parts))
    return make_unique(names)


def fill_down(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    copied = frame.copy()
    for column in columns:
        if column in copied.columns:
            copied[column] = copied[column].replace("", pd.NA).ffill()
    return copied


def normalize_material() -> pd.DataFrame:
    frame = read_sheet(REPORTS["fb_material_chain_metrics"]["path"])
    columns = combine_headers(frame, [6, 7])
    data = frame.iloc[8:].copy()
    data.columns = columns
    data = data.dropna(how="all")
    dimension_cols = [
        "REDACTED_DIM_OWNER",
        "REDACTED_DIM_PLATFORM",
        "REDACTED_DIM_REGION_TIER",
        "投放账户",
        "广告组ID",
        "上线日期",
        "广告ID",
        "广告名称",
        "REDACTED_CREATIVE_TYPE",
    ]
    data = fill_down(data, dimension_cols)
    data.insert(0, "source_report", REPORTS["fb_material_chain_metrics"]["name"])
    data.insert(1, "source_role", REPORTS["fb_material_chain_metrics"]["role"])
    data.insert(2, "source_row", list(range(9, 9 + len(data))))
    return data


def normalize_hkmo() -> pd.DataFrame:
    frame = read_sheet(REPORTS["fb_hk_mo_test_report"]["path"])
    columns = combine_headers(frame, [3, 4])
    data = frame.iloc[5:].copy()
    data.columns = columns
    data = data.dropna(how="all")
    dimension_cols = ["REDACTED_DIM_OWNER_GROUP", "REDACTED_DIM_FORM_CHANNEL", "REDACTED_DIM_REGION_TIER", "REDACTED_DIM_TEST_ITEM", "REDACTED_FLAG_B", "REDACTED_FLAG_A", "creative_asset"]
    data = fill_down(data, dimension_cols)
    data.insert(0, "source_report", REPORTS["fb_hk_mo_test_report"]["name"])
    data.insert(1, "source_role", REPORTS["fb_hk_mo_test_report"]["role"])
    data.insert(2, "source_row", list(range(6, 6 + len(data))))
    return data


def wide_group_to_long(report_key: str) -> pd.DataFrame:
    frame = read_sheet(REPORTS[report_key]["path"])
    header_groups = ["" if value is None else str(value) for value in frame.iloc[2].tolist()]
    metrics = ["" if value is None else str(value) for value in frame.iloc[3].tolist()]
    last_group = ""
    records = []
    for row_index in range(4, len(frame)):
        row = frame.iloc[row_index]
        date_value = row.iloc[0]
        if date_value in (None, ""):
            continue
        for col in range(1, frame.shape[1]):
            group = header_groups[col] or last_group
            if header_groups[col]:
                last_group = header_groups[col]
                group = last_group
            metric = metrics[col]
            value = row.iloc[col]
            if not group or not metric or value in (None, ""):
                continue
            records.append(
                {
                    "source_report": REPORTS[report_key]["name"],
                    "source_role": REPORTS[report_key]["role"],
                    "source_row": row_index + 1,
                    "日期": date_value,
                    "分组": group,
                    "指标": metric,
                    "值": value,
                }
            )
    return pd.DataFrame.from_records(records)


def source_reports() -> pd.DataFrame:
    rows = []
    for key, report in REPORTS.items():
        path = report["path"]
        rows.append(
            {
                "task": key,
                "report_name": report["name"],
                "role": report["role"],
                "xlsx_path": str(path),
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else None,
            }
        )
    return pd.DataFrame(rows)


def report_structures() -> pd.DataFrame:
    rows = []
    for path in sorted(INSPECT_ROOT.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for sheet in data.get("sheets", []):
            rows.append(
                {
                    "inspect_file": path.name,
                    "workbook": data.get("path"),
                    "sheet": sheet.get("name"),
                    "pandas_rows": sheet.get("pandas_rows"),
                    "pandas_columns": sheet.get("pandas_columns"),
                    "merged_range_count": sheet.get("merged_range_count"),
                    "likely_table_type": sheet.get("likely_table_type"),
                    "header_rows": ", ".join(str(item.get("row")) for item in sheet.get("header_candidates", [])[:4]),
                }
            )
    return pd.DataFrame(rows)


def categorize_field(name: str) -> str:
    for category, keywords in FIELD_CATEGORY_RULES:
        if any(keyword.lower() in name.lower() for keyword in keywords):
            return category
    return "待确认字段"


def field_mapping(*frames: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for frame in frames:
        if frame.empty:
            continue
        report_name = str(frame["source_report"].iloc[0]) if "source_report" in frame.columns else ""
        for column in frame.columns:
            if column in {"source_report", "source_role", "source_row"}:
                continue
            rows.append(
                {
                    "source_report": report_name,
                    "field_name": column,
                    "field_category_draft": categorize_field(column),
                    "weekly_module_draft": weekly_module_for_field(column),
                    "needs_user_calibration": "是",
                }
            )
    return pd.DataFrame(rows).drop_duplicates()


def weekly_module_for_field(name: str) -> str:
    if any(key in name for key in ["目标", "达成", "ROI", "GMV"]):
        return "FB整体达成"
    if any(key in name for key in ["日期", "渠道", "区域", "分组", "链路"]):
        return "渠道与区域表现"
    if any(key in name for key in ["creative_asset", "广告名称", "广告ID", "CTR", "CVR", "曝光", "点击"]):
        return "creative_asset维度表现"
    if any(key in name for key in ["空耗", "成效", "成本", "消耗"]):
        return "空耗/高成本候选"
    return "待确认"


def weekly_base_sections() -> pd.DataFrame:
    rows = [
        {"section": "1. 本周数据范围", "required_data": "时间窗口、数据来源、报表更新时间、完整性", "status": "由导出参数和run log填充", "human_placeholder": ""},
        {"section": "2. FB整体达成", "required_data": "目标、实际、达成率、环比/周比", "status": "待从底表校准目标字段", "human_placeholder": "备注占位"},
        {"section": "3. 渠道与区域表现", "required_data": "区域/策略、消耗、REDACTED_CONVERSION_A、REDACTED_CONVERSION_B、REDACTED_CONVERSION_C、REDACTED_CONVERSION、成本、ROI2", "status": "可从日监控/链路类型/REDACTED_REGION_A测试抽取", "human_placeholder": "备注占位"},
        {"section": "4. creative_asset维度表现", "required_data": "REDACTED_CREATIVE_TYPE、广告名称、消耗、曝光、点击、CTR、CVR、REDACTED_CONVERSION_A、REDACTED_CONVERSION_B、REDACTED_CONVERSION_B_COST、ROI2", "status": "可从creative_asset维度表抽取", "human_placeholder": "备注占位"},
        {"section": "5. 空耗/高成本候选", "required_data": "对象、消耗、成效、成效成本、异常类型", "status": "V0只列候选，不生成建议", "human_placeholder": "人工确认位"},
        {"section": "6. 数据缺口", "required_data": "缺口、影响、确认人、是否阻塞", "status": "由校准结果补充", "human_placeholder": ""},
        {"section": "7. 投放师观点占位", "required_data": "本周判断、可能原因、下周动作、协同事项", "status": "V0不自动填写", "human_placeholder": "人工填写"},
    ]
    return pd.DataFrame(rows)


def write_workbook() -> None:
    material = normalize_material()
    channel_long = wide_group_to_long("fb_channel_daily_monitor")
    link_type_long = wide_group_to_long("fb_link_type_daily_monitor")
    hkmo = normalize_hkmo()
    mapping = field_mapping(material, channel_long, link_type_long, hkmo)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
        source_reports().to_excel(writer, sheet_name="source_reports", index=False)
        report_structures().to_excel(writer, sheet_name="report_structures", index=False)
        weekly_base_sections().to_excel(writer, sheet_name="weekly_base_sections", index=False)
        mapping.to_excel(writer, sheet_name="field_mapping_draft", index=False)
        material.to_excel(writer, sheet_name="material_wide", index=False)
        channel_long.to_excel(writer, sheet_name="channel_daily_long", index=False)
        link_type_long.to_excel(writer, sheet_name="link_type_daily_long", index=False)
        hkmo.to_excel(writer, sheet_name="hkmo_strategy_wide", index=False)

        for sheet in writer.book.worksheets:
            sheet.freeze_panes = "A2"
            for column_cells in sheet.columns:
                max_len = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells[:50])
                sheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_len + 2, 10), 36)

    print(OUTPUT)


if __name__ == "__main__":
    write_workbook()
