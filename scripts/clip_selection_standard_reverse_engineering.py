#!/usr/bin/env python3
"""选片标准反推。

边界：
- 只读取 /Volumes/WD_BLACK/澜心社剪辑 授权目录内素材与当前仓库事实。
- 排除 AI需要的成片/成品 下的视频；隐藏 AppleDouble 文件不当作视频素材。
- 复用已提交的前序解析结果，不新增外部 API 调用，不提交媒体。
- 对没有前序多模态证据的新增视频，只输出 title/metadata 层解析并标 pending。
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from xml.sax.saxutils import escape


REPO_ROOT = Path(__file__).resolve().parents[1]
AUTHORIZED_BASE = Path("/Volumes/WD_BLACK/澜心社剪辑")
MATERIAL_ROOT = AUTHORIZED_BASE / "剪辑解析数据" / "AI需要的成片"
EXCLUDED_FINISHED_DIR_NAME = "成品"
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv"}

ANALYSIS_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis" / "12_clip_selection_standard_reverse_engineering"
FACT_DIR = REPO_ROOT / "项目事实_project_facts" / "选片标准反推_clip_selection_standard_reverse_engineering"
LOG_DIR = REPO_ROOT / "执行日志_codex_log"

REPORT_112 = LOG_DIR / "112_两条直播录屏正式模拟运行报告_two_live_recording_formal_simulation_report.md"
REPORT_113_REPLAN = LOG_DIR / "113_112结果复审与路线重判报告_112_result_review_route_replanning_report.md"
REPORT_113_V2 = LOG_DIR / "113_直播切片V2架构审核与解析补全报告_live_cutting_v2_architecture_audit_report.md"
REPORT_114 = LOG_DIR / "114_C9623直播切片完整验证报告_c9623_live_cutting_full_validation_report.md"

V2_ANALYSIS_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis" / "10_live_cutting_v2_architecture_audit"
C9623_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis" / "11_c9623_live_cutting_full_validation"
FORMAL_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis" / "09_live_recording_formal_simulation"

AI_TOP100_CSV = V2_ANALYSIS_DIR / "03_AI需要的成片前100解析补全_ai_needed_top100_analysis.csv"
PN_GAP_CSV = V2_ANALYSIS_DIR / "04_正负样本差异结构表_positive_negative_structure_gap.csv"
LIVE_OPPORTUNITY_CSV = V2_ANALYSIS_DIR / "05_直播切片素材结构机会表_live_cutting_opportunity_table.csv"
C9623_CANDIDATE_CSV = C9623_DIR / "05_C9623候选片段评分表_c9623_candidate_scoring.csv"
C9623_EXPORT_CSV = C9623_DIR / "06_C9623导出视频索引_c9623_exported_clip_index.csv"
C9623_REJECTED_CSV = C9623_DIR / "07_C9623弃用片段表_c9623_rejected_segments.csv"
C9623_PACKAGING_CSV = C9623_DIR / "08_C9623人工包装建议表_c9623_manual_packaging_advice.csv"
FORMAL_REJECTED_CSV = FORMAL_DIR / "05_弃用片段表_rejected_segment_table.csv"
FORMAL_RESCUE_CSV = FORMAL_DIR / "07_弃用片段复审与可救回片段表_rejected_segment_recheck_rescue_candidates.csv"

SAMPLE_INVENTORY_CSV = ANALYSIS_DIR / "01_样本来源清单_sample_source_inventory.csv"
POSITIVE_REASON_CSV = ANALYSIS_DIR / "02_正样本选片理由表_positive_selection_reason.csv"
REJECTED_REASON_CSV = ANALYSIS_DIR / "03_弃用弱样本失败原因表_rejected_weak_sample_reason.csv"
TAG_LIBRARY_CSV = ANALYSIS_DIR / "04_选片理由标签库_selection_reason_tag_library.csv"
STANDARD_SAMPLE_MATRIX_CSV = ANALYSIS_DIR / "05_选片标准样本对照表_selection_standard_sample_matrix.csv"
WHY_SELECTED_CSV = ANALYSIS_DIR / "06_别人为什么选反推表_why_selected_reverse_engineering.csv"
C9623_REVIEW_CSV = ANALYSIS_DIR / "07_C9623候选价值复盘表_c9623_candidate_value_review.csv"

STANDARD_REPORT_MD = FACT_DIR / "01_选片标准总报告_clip_selection_standard_report.md"
SCORING_MATRIX_MD = FACT_DIR / "02_可执行评分矩阵_selection_scoring_matrix.md"
RUNTIME_FIELDS_MD = FACT_DIR / "03_Codex选片运行字段设计_codex_selection_runtime_fields.md"
MANUAL_FEEDBACK_MD = FACT_DIR / "04_人审反馈表_manual_review_feedback_sheet.md"
HUMAN_REPORT_DOCX = FACT_DIR / "05_人读版报告_human_readable_report.docx"
HUMAN_REPORT_MD = FACT_DIR / "05_人读版报告_human_readable_report.md"
EXEC_REPORT_MD = LOG_DIR / "115_选片标准反推报告_clip_selection_standard_reverse_engineering_report.md"


SAMPLE_FIELDS = [
    "sample_id",
    "source_scope",
    "relative_path",
    "file_name",
    "top_level_group",
    "excluded_by_user_rule",
    "hidden_resource_fork_skipped",
    "parse_basis",
    "matched_existing_video_id",
    "matched_existing_analysis_status",
    "duration_seconds",
    "width",
    "height",
    "fps",
    "audio_present",
    "file_size_mb",
    "metadata_probe_status",
    "title_hook_type",
    "viewer_problem_tags",
    "core_asset_type",
    "inferred_content_archetype",
    "inferred_route_decision",
    "selection_reason_tags",
    "needs_audio_or_multimodal_review",
    "boundary_status",
]

POSITIVE_FIELDS = [
    "reason_id",
    "sample_id",
    "file_name",
    "parse_basis",
    "why_someone_might_select",
    "first_glance_value",
    "viewer_problem_value",
    "retention_mechanism",
    "visual_value",
    "core_value_carrier",
    "codex_should_learn",
    "content_archetype",
    "route_decision",
    "candidate_status",
    "problem_action_bridge_seconds",
    "native_completeness_score",
    "repackaging_value_score",
    "teachability_score",
    "risk_boundary",
    "confidence",
]

REJECTED_FIELDS = [
    "weak_id",
    "source_table",
    "sample_ref",
    "source_file",
    "start_time",
    "end_time",
    "candidate_status",
    "route_decision",
    "failure_reason_tags",
    "why_not_priority",
    "missing_evidence",
    "manual_packaging_cost",
    "positive_sample_gap",
    "needs_transcript_or_audio",
    "rescue_level",
    "manual_review_items",
]

TAG_FIELDS = [
    "tag_id",
    "tag_name",
    "中文含义",
    "selection_value",
    "high_signal_evidence",
    "low_signal_or_failure",
    "route_fit",
    "status_boundary",
]

STANDARD_MATRIX_FIELDS = [
    "standard_id",
    "standard_name",
    "sample_type",
    "sample_ref",
    "file_or_segment",
    "why_it_matches_or_fails",
    "evidence_basis",
    "next_codex_action",
    "boundary_status",
]

WHY_SELECTED_FIELDS = [
    "pattern_id",
    "selection_reason_tag",
    "why_people_select_it",
    "what_problem_it_solves",
    "what_keeps_viewers",
    "best_route",
    "supporting_sample_count",
    "example_files",
    "failure_counterexample",
    "codex_rule",
]

C9623_REVIEW_FIELDS = [
    "review_id",
    "candidate_id",
    "candidate_status",
    "route_decision",
    "start_time",
    "end_time",
    "priority_score",
    "value_judgment",
    "why_selected_or_exported",
    "why_not_publish_ready",
    "manual_packaging_action",
    "audio_transcript_status",
    "risk_boundary",
    "next_decision",
]


@dataclass
class VideoProbe:
    duration_seconds: str = ""
    width: str = ""
    height: str = ""
    fps: str = ""
    audio_present: str = "unknown"
    file_size_mb: str = ""
    metadata_probe_status: str = "not_probed"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple, set)):
        return "；".join(str(item) for item in value if str(item))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: stringify(row.get(field, "")) for field in fieldnames})


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_command(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True, timeout=timeout, check=False)


def require_boundaries() -> dict[str, str]:
    if not str(REPO_ROOT).startswith(str(AUTHORIZED_BASE)):
        raise RuntimeError(f"blocked_wrong_workspace_root: {REPO_ROOT}")
    if not MATERIAL_ROOT.exists():
        raise RuntimeError(f"blocked_missing_material_root: {MATERIAL_ROOT}")

    top = run_command(["git", "rev-parse", "--show-toplevel"])
    branch = run_command(["git", "branch", "--show-current"])
    remote = run_command(["git", "remote", "-v"])
    status = run_command(["git", "status", "--short"])
    if top.returncode != 0 or Path(top.stdout.strip()) != REPO_ROOT:
        raise RuntimeError("blocked_wrong_workspace_or_remote: git root mismatch")
    if "fthytwerwt-sudo/lanxinse--.git" not in remote.stdout:
        raise RuntimeError("blocked_wrong_remote")

    missing = [
        path
        for path in [
            REPORT_112,
            REPORT_113_REPLAN,
            REPORT_113_V2,
            REPORT_114,
            AI_TOP100_CSV,
            PN_GAP_CSV,
            C9623_CANDIDATE_CSV,
            C9623_EXPORT_CSV,
            C9623_PACKAGING_CSV,
        ]
        if not path.exists()
    ]
    if missing:
        raise RuntimeError("blocked_missing_required_inputs: " + "；".join(str(p.relative_to(REPO_ROOT)) for p in missing))

    return {
        "pwd": str(AUTHORIZED_BASE),
        "repo_root": top.stdout.strip(),
        "branch": branch.stdout.strip(),
        "remote": remote.stdout.strip().replace("\n", " | "),
        "git_status_short": status.stdout.strip() or "clean",
        "ffprobe": shutil.which("ffprobe") or "",
        "ffmpeg": shutil.which("ffmpeg") or "",
    }


def discover_material_videos() -> tuple[list[Path], int, int]:
    videos: list[Path] = []
    excluded_finished = 0
    skipped_hidden = 0
    for path in sorted(MATERIAL_ROOT.rglob("*"), key=lambda p: str(p)):
        if not path.is_file() or path.suffix.lower() not in VIDEO_EXTS:
            continue
        rel_parts = path.relative_to(MATERIAL_ROOT).parts
        if EXCLUDED_FINISHED_DIR_NAME in rel_parts:
            excluded_finished += 1
            continue
        if path.name.startswith("._"):
            skipped_hidden += 1
            continue
        videos.append(path)
    return videos, excluded_finished, skipped_hidden


def ffprobe_video(path: Path) -> VideoProbe:
    size = path.stat().st_size / (1024 * 1024)
    probe = VideoProbe(file_size_mb=f"{size:.3f}")
    if not shutil.which("ffprobe"):
        probe.metadata_probe_status = "ffprobe_unavailable"
        return probe

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate",
        "-of",
        "json",
        str(path),
    ]
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=20, check=False)
    except subprocess.TimeoutExpired:
        probe.metadata_probe_status = "ffprobe_timeout"
        return probe
    if result.returncode != 0:
        probe.metadata_probe_status = "ffprobe_failed"
        return probe
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        probe.metadata_probe_status = "ffprobe_json_parse_failed"
        return probe
    duration = data.get("format", {}).get("duration")
    if duration:
        probe.duration_seconds = f"{float(duration):.3f}"
    video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
    if video_stream:
        probe.width = stringify(video_stream.get("width", ""))
        probe.height = stringify(video_stream.get("height", ""))
        rate = video_stream.get("r_frame_rate", "")
        probe.fps = parse_fps(rate)
    probe.audio_present = "yes" if audio_stream else "no"
    probe.metadata_probe_status = "metadata_only_probe_passed"
    return probe


def parse_fps(rate: str) -> str:
    if not rate or "/" not in rate:
        return rate
    left, right = rate.split("/", 1)
    try:
        den = float(right)
        if den == 0:
            return rate
        return f"{float(left) / den:.3f}"
    except ValueError:
        return rate


def normalize_title(file_name: str) -> str:
    title = Path(file_name).stem
    title = re.sub(r"\d+\.\d+|6\.\d+|6月\d+日|5月\d+日|\(\d+\)|（\d+）", "", title)
    title = title.replace("J", "紧").replace("P底", "盆底").replace("氵", "水")
    return re.sub(r"\s+", " ", title).strip(" -_")


PROBLEM_KEYWORDS = [
    ("leakage_embarrassment", ["漏尿", "漏水", "跑跳", "尴尬", "失控"]),
    ("belly_core_pressure", ["小肚子", "腹", "悬垂腹", "腹直肌", "内压", "胀气", "马甲线"]),
    ("pelvic_floor", ["盆底", "松", "高张", "脱垂", "膨出", "子宫", "前壁", "坠胀"]),
    ("hip_glute_shape", ["臀", "妈妈臀", "臀凹陷", "蜜桃臀", "八爪鱼", "假胯", "胯", "髋"]),
    ("postpartum_or_age_group", ["产后", "妈妈", "女性", "姐妹", "30", "35", "40"]),
    ("posture_back_waist", ["背", "腰", "骨盆", "体态"]),
]


def infer_viewer_problem_tags(title: str) -> list[str]:
    tags: list[str] = []
    for tag, keywords in PROBLEM_KEYWORDS:
        if any(word in title for word in keywords):
            tags.append(tag)
    return tags or ["general_body_management"]


def infer_hook_type(title: str) -> str:
    if "?" in title or "？" in title or any(word in title for word in ["吗", "为什么", "是不是", "能自己好", "先"]):
        return "question_or_misconception_hook"
    if any(word in title for word in ["漏尿", "漏水", "尴尬", "疼痛", "小肚子凸", "脱垂", "膨出", "坠胀"]):
        return "pain_point_hook"
    if any(word in title for word in ["只需", "每天", "分钟", "告别", "变小", "练出", "改善", "不见了"]):
        return "promise_action_hook"
    if any(word in title for word in ["30", "35", "40", "产后", "女性", "妈妈", "姐妹", "宝妈"]):
        return "population_callout_hook"
    return "topic_title_hook"


def infer_core_asset(title: str) -> str:
    action_words = ["动作", "练", "式", "臀桥", "小球", "瑜伽", "蝴蝶", "青蛙", "趴", "开合", "测试"]
    if any(word in title for word in action_words):
        return "visible_action_or_prop_demo"
    if any(word in title for word in ["误区", "为什么", "能自己好", "先减肥", "治疗"]):
        return "semantic_explainer_or_misconception"
    return "result_or_problem_statement"


def infer_content_archetype(title: str, core_asset: str) -> str:
    if core_asset == "semantic_explainer_or_misconception":
        return "native_live_clip_or_explainer_reference"
    if core_asset == "visible_action_or_prop_demo":
        return "single_action_tts_teaching"
    return "problem_hook_reference"


def infer_route_decision(title: str, core_asset: str) -> str:
    if core_asset == "semantic_explainer_or_misconception":
        return "native_or_audio_semantic_review_candidate"
    if core_asset == "visible_action_or_prop_demo":
        return "action_repackaging_reference_candidate"
    return "positive_reference_title_metadata_only"


def infer_reason_tags(row: dict[str, Any], title: str, matched: dict[str, str] | None) -> list[str]:
    tags = set(infer_viewer_problem_tags(title))
    hook = infer_hook_type(title)
    if hook == "pain_point_hook":
        tags.add("pain_point_visualized")
    if hook == "question_or_misconception_hook":
        tags.add("hook_fulfilled_by_body")
    if hook == "population_callout_hook":
        tags.add("target_audience_called_out")
    if hook == "promise_action_hook":
        tags.add("result_promise_front_loaded")
    if "小球" in title or "瑜伽球" in title:
        tags.add("single_method_easy_to_repackage")
    if row.get("core_asset_type") == "visible_action_or_prop_demo":
        tags.add("action_demo_clearly_visible")
        tags.add("single_method_easy_to_repackage")
    if matched:
        if "yes" in matched.get("positive_pattern_match", ""):
            tags.add("high_pattern_reusability")
        if matched.get("subtitle_evidence") or matched.get("tts_action_alignment"):
            tags.add("subtitle_and_action_aligned")
        if matched.get("ending_type"):
            tags.add("ending_naturally_closes")
        if matched.get("problem_action_bridge_seconds", "").replace(".", "", 1).isdigit():
            try:
                if float(matched["problem_action_bridge_seconds"]) <= 6:
                    tags.add("problem_to_action_bridge_short")
            except ValueError:
                pass
        if matched.get("health_action_risk") or matched.get("business_risk"):
            tags.add("risk_pending_not_publish_ready")
    return sorted(tags)


def build_sample_inventory(videos: list[Path], ai_top100: list[dict[str, str]], probe_metadata: bool) -> list[dict[str, Any]]:
    by_name = {row.get("file_name", ""): row for row in ai_top100}
    rows: list[dict[str, Any]] = []
    for index, path in enumerate(videos, start=1):
        rel = path.relative_to(MATERIAL_ROOT)
        title = normalize_title(path.name)
        core_asset = infer_core_asset(title)
        matched = by_name.get(path.name)
        probe = ffprobe_video(path) if probe_metadata else VideoProbe(file_size_mb=f"{path.stat().st_size / (1024 * 1024):.3f}")
        parse_basis = "existing_multimodal_structure_reused" if matched else "title_metadata_only_pending_multimodal_review"
        row: dict[str, Any] = {
            "sample_id": f"ai_needed_{index:03d}",
            "source_scope": "AI需要的成片_non_finished",
            "relative_path": str(rel),
            "file_name": path.name,
            "top_level_group": rel.parts[0] if len(rel.parts) > 1 else "root",
            "excluded_by_user_rule": "no",
            "hidden_resource_fork_skipped": "no",
            "parse_basis": parse_basis,
            "matched_existing_video_id": matched.get("video_id", "") if matched else "",
            "matched_existing_analysis_status": matched.get("analysis_status", "") if matched else "",
            "duration_seconds": probe.duration_seconds,
            "width": probe.width,
            "height": probe.height,
            "fps": probe.fps,
            "audio_present": probe.audio_present,
            "file_size_mb": probe.file_size_mb,
            "metadata_probe_status": probe.metadata_probe_status,
            "title_hook_type": infer_hook_type(title),
            "viewer_problem_tags": infer_viewer_problem_tags(title),
            "core_asset_type": core_asset,
            "inferred_content_archetype": matched.get("content_archetype", "") if matched else infer_content_archetype(title, core_asset),
            "inferred_route_decision": matched.get("route_decision", "") if matched else infer_route_decision(title, core_asset),
            "needs_audio_or_multimodal_review": "no_existing_analysis_reused" if matched else "yes",
            "boundary_status": "positive_reference_not_publish_validation",
        }
        row["selection_reason_tags"] = infer_reason_tags(row, title, matched)
        rows.append(row)
    return rows


def build_positive_reasons(inventory: list[dict[str, Any]], ai_top100: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_name = {row.get("file_name", ""): row for row in ai_top100}
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(inventory, start=1):
        title = normalize_title(item["file_name"])
        matched = by_name.get(item["file_name"])
        problem_tags = stringify(item["viewer_problem_tags"])
        hook = item["title_hook_type"]
        core_asset = item["core_asset_type"]
        if matched:
            why = "前序解析显示开头/动作/收束或再包装价值可复用；本轮只反推选片原因，不确认发布。"
            first_value = matched.get("opening_summary", "") or f"{hook} + {problem_tags}"
            retention = matched.get("middle_delivery_type", "") or matched.get("action_method_summary", "")
            visual_value = matched.get("subtitle_evidence", "")[:180]
            carrier = infer_core_value_carrier(matched, core_asset)
            learn = "学习问题钩子、动作证据、桥接秒数、再包装价值和风险边界如何共同决定是否进池。"
        else:
            why = f"标题层呈现 {hook}，指向 {problem_tags}，且核心资产是 {core_asset}；待多模态复核后才能确认画面/口播成立。"
            first_value = f"{hook}：{title}"
            retention = "title_implied_problem_or_action_route_pending_visual_audio_review"
            visual_value = "pending_multimodal_review；仅能从文件名推断可能有动作/问题，不确认画面内容。"
            carrier = "title_or_metadata_only_pending_review"
            learn = "学习标题层先分流，不把标题承诺当成视觉/口播已成立。"
        rows.append(
            {
                "reason_id": f"positive_reason_{index:03d}",
                "sample_id": item["sample_id"],
                "file_name": item["file_name"],
                "parse_basis": item["parse_basis"],
                "why_someone_might_select": why,
                "first_glance_value": first_value,
                "viewer_problem_value": problem_tags,
                "retention_mechanism": retention,
                "visual_value": visual_value,
                "core_value_carrier": carrier,
                "codex_should_learn": learn,
                "content_archetype": matched.get("content_archetype", item["inferred_content_archetype"]) if matched else item["inferred_content_archetype"],
                "route_decision": matched.get("route_decision", item["inferred_route_decision"]) if matched else item["inferred_route_decision"],
                "candidate_status": matched.get("candidate_status", "pending_multimodal_review") if matched else "title_metadata_only_pending_review",
                "problem_action_bridge_seconds": matched.get("problem_action_bridge_seconds", "pending") if matched else "pending",
                "native_completeness_score": matched.get("native_completeness_score", "pending") if matched else "pending",
                "repackaging_value_score": matched.get("repackaging_value_score", "pending") if matched else "pending",
                "teachability_score": matched.get("teachability_score", "pending") if matched else "pending",
                "risk_boundary": matched.get("health_action_risk", "risk_pending_not_publish_ready") if matched else "pending_multimodal_and_professional_review",
                "confidence": matched.get("confidence", "low_title_only") if matched else "low_title_only",
            }
        )
    return rows


def infer_core_value_carrier(row: dict[str, str], fallback: str) -> str:
    subtitle = row.get("subtitle_evidence", "")
    action = row.get("action_method_summary", "")
    if subtitle and action:
        return "visual_action_plus_subtitle_or_tts"
    if action:
        return "visual_action"
    if row.get("opening_summary"):
        return "opening_semantic_hook"
    return fallback


def failure_tags_from_text(text: str) -> list[str]:
    tags = []
    mapping = [
        ("action_only_no_problem_bridge", ["有动作", "重复动作", "problem_action_bridge", "动作存在"]),
        ("opening_missing", ["无有效开头", "开头缺", "缺乏开头", "观看理由"]),
        ("middle_delivery_missing", ["中段交付缺失", "中段仅", "无步骤", "交付内容模糊"]),
        ("ending_missing", ["结尾", "无收束", "非自然收束"]),
        ("evidence_missing", ["无可验证", "证据", "缺证据"]),
        ("pending_audio_transcript", ["口播", "字幕", "音频", "转写", "听"]),
        ("risk_review_required", ["风险", "医疗", "健康", "业务", "疗效"]),
        ("static_or_repetitive_visual", ["静态", "零散手势", "重复动作"]),
        ("needs_manual_start_end_extension", ["前后文", "扩展", "合并", "前后窗口"]),
        ("continuity_context_insufficient", ["当前窗口", "直播中段", "孤立"]),
        ("lower_priority_not_exported", ["低优先", "not_exported", "lower_priority"]),
        ("visual_evidence_insufficient", ["视觉证据", "画面线索弱"]),
        ("reject_unusable", ["reject_unusable", "不可用", "不建议救回"]),
    ]
    for tag, needles in mapping:
        if any(needle in text for needle in needles):
            tags.append(tag)
    return tags or ["weak_value_pending_human_review"]


def build_rejected_rows(c9623_rejected: list[dict[str, str]], formal_rejected: list[dict[str, str]], formal_rescue: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    formal_rescue_by_id = {row.get("rejected_id", ""): row for row in formal_rescue}

    for index, row in enumerate(c9623_rejected, start=1):
        text = " ".join(
            [
                row.get("why_rejected", ""),
                row.get("original_reject_reason", ""),
                row.get("missing_part", ""),
                row.get("manual_review_items", ""),
            ]
        )
        rows.append(
            {
                "weak_id": f"c9623_weak_{index:03d}",
                "source_table": "C9623弃用片段表",
                "sample_ref": row.get("candidate_id", ""),
                "source_file": row.get("source_file", ""),
                "start_time": row.get("start_time", ""),
                "end_time": row.get("end_time", ""),
                "candidate_status": row.get("candidate_status", ""),
                "route_decision": row.get("route_decision", ""),
                "failure_reason_tags": failure_tags_from_text(text),
                "why_not_priority": row.get("original_reject_reason") or row.get("why_rejected"),
                "missing_evidence": row.get("missing_part", ""),
                "manual_packaging_cost": manual_packaging_cost(row.get("could_be_fixed_by_manual_edit", ""), row.get("needs_transcript_or_audio", "")),
                "positive_sample_gap": "缺少正样本常见的清晰观看理由、动作/方法兑现、自然收束或可解释字幕/TTS。",
                "needs_transcript_or_audio": row.get("needs_transcript_or_audio", ""),
                "rescue_level": row.get("rescue_level", ""),
                "manual_review_items": row.get("manual_review_items", ""),
            }
        )

    base = len(rows)
    for index, row in enumerate(formal_rejected, start=1):
        rescue = formal_rescue_by_id.get(row.get("candidate_id", ""), {})
        text = " ".join([row.get("reject_reason", ""), row.get("notes", ""), rescue.get("reason_for_next_action", "")])
        rows.append(
            {
                "weak_id": f"formal_weak_{index + base:03d}",
                "source_table": "112正式模拟弃用片段表",
                "sample_ref": row.get("candidate_id", ""),
                "source_file": row.get("recording_id", ""),
                "start_time": row.get("start_time", ""),
                "end_time": row.get("end_time", ""),
                "candidate_status": rescue.get("next_action", "rejected_window_needs_context_recheck"),
                "route_decision": rescue.get("recheck_category", "reject_or_rescue_pending"),
                "failure_reason_tags": failure_tags_from_text(text),
                "why_not_priority": row.get("reject_reason", ""),
                "missing_evidence": row.get("missing_part", ""),
                "manual_packaging_cost": manual_packaging_cost(row.get("could_be_fixed_by_manual_edit", ""), rescue.get("needs_transcript_or_audio", "")),
                "positive_sample_gap": "当前窗口不像正样本那样独立完成开头-交付-收束；如要救回，必须扩前后窗口并补音频语义。",
                "needs_transcript_or_audio": rescue.get("needs_transcript_or_audio", "pending"),
                "rescue_level": rescue.get("rescue_level", "pending"),
                "manual_review_items": rescue.get("next_action", "context_window_recheck_before_any_export"),
            }
        )
    return rows


def manual_packaging_cost(could_fix: str, needs_audio: str) -> str:
    if "yes" in needs_audio:
        return "high: 需要听口播/字幕后才能补问题前置、动作要点和风险提示"
    if could_fix == "yes":
        return "medium: 可以人工补边界和字幕，但需确认动作/语义"
    if could_fix == "no":
        return "too_high: 包装成本大于价值"
    return "unclear: 先补证据再判断"


def tag_library_rows() -> list[dict[str, str]]:
    return [
        {
            "tag_id": "tag_01",
            "tag_name": "target_audience_called_out",
            "中文含义": "开头直接点名人群，让观众知道这条在说我",
            "selection_value": "人群清楚时更容易建立停留理由",
            "high_signal_evidence": "30+、40+、产后、妈妈、女性、姐妹等目标人群出现",
            "low_signal_or_failure": "人群泛化，无法判断谁该看",
            "route_fit": "native_clip / action_repackaging / pending_audio_review",
            "status_boundary": "人群标题不等于内容证据已成立",
        },
        {
            "tag_id": "tag_02",
            "tag_name": "pain_point_visualized",
            "中文含义": "痛点被标题、字幕或画面具象化",
            "selection_value": "观众能迅速理解为什么要继续看",
            "high_signal_evidence": "漏尿、坠胀、小肚子凸、脱垂、妈妈臀等具体问题出现",
            "low_signal_or_failure": "只有想拥有、变美等泛愿望",
            "route_fit": "native_clip / action_repackaging / audio_review",
            "status_boundary": "不能把痛点标题当成口播已确认",
        },
        {
            "tag_id": "tag_03",
            "tag_name": "result_promise_front_loaded",
            "中文含义": "结果感前置，先把点击理由给出来",
            "selection_value": "适合做短视频开头，但必须被中段兑现",
            "high_signal_evidence": "肚子平了、臀翘了、告别尴尬、练出等结果承诺",
            "low_signal_or_failure": "只有结果，没有动作/解释/证据",
            "route_fit": "positive_reference / action_repackaging",
            "status_boundary": "结果承诺涉及健康/效果时必须风险复核",
        },
        {
            "tag_id": "tag_04",
            "tag_name": "hook_fulfilled_by_body",
            "中文含义": "开头钩子在中段被方法、解释或动作兑现",
            "selection_value": "这是别人选片的核心：不是标题强，而是钩子能兑现",
            "high_signal_evidence": "问题后进入动作/方法/纠错解释",
            "low_signal_or_failure": "开头很猛，中段没有兑现",
            "route_fit": "native_clip / action_repackaging",
            "status_boundary": "没有音频/字幕时只能部分成立",
        },
        {
            "tag_id": "tag_05",
            "tag_name": "action_demo_clearly_visible",
            "中文含义": "动作主体看得见，能支撑可学可剪",
            "selection_value": "是动作教学再包装的底盘",
            "high_signal_evidence": "动作方向、起止、循环或道具关系可见",
            "low_signal_or_failure": "只有静态坐姿、零散手势、重复无解释动作",
            "route_fit": "action_repackaging",
            "status_boundary": "动作清楚不等于动作专业性通过",
        },
        {
            "tag_id": "tag_06",
            "tag_name": "single_method_easy_to_repackage",
            "中文含义": "单一方法或单一道具动作，容易包装成标准模板",
            "selection_value": "降低人工包装成本，提高复用性",
            "high_signal_evidence": "一个动作、一个小球、一个测试、一个纠错点",
            "low_signal_or_failure": "多个动作混杂，无法稳定归类",
            "route_fit": "action_repackaging / manual_packaging",
            "status_boundary": "可包装不等于发布可用",
        },
        {
            "tag_id": "tag_07",
            "tag_name": "subtitle_and_action_aligned",
            "中文含义": "字幕/口令和动作同题，不是各说各话",
            "selection_value": "让动作教学更容易成立，也方便剪映/CapCut 包装",
            "high_signal_evidence": "字幕标出动作目标、次数、方向或禁忌",
            "low_signal_or_failure": "字幕只喊结果，和动作无关",
            "route_fit": "native_clip / action_repackaging",
            "status_boundary": "当前多为 visual_only_pending_audio_transcript",
        },
        {
            "tag_id": "tag_08",
            "tag_name": "problem_to_action_bridge_short",
            "中文含义": "从问题到动作过渡短，进入教学快",
            "selection_value": "降低跳出率，让切片有开头到中段兑现",
            "high_signal_evidence": "problem_action_bridge_seconds <= 6",
            "low_signal_or_failure": "问题讲很久但没有动作、方法或解释",
            "route_fit": "native_clip / action_repackaging",
            "status_boundary": "没有音频时只能待验证",
        },
        {
            "tag_id": "tag_09",
            "tag_name": "ending_naturally_closes",
            "中文含义": "结尾能自然收住，不靠硬卖或突然中断",
            "selection_value": "片段更容易形成完整人审素材",
            "high_signal_evidence": "动作完成、口播总结、视觉定格或自然收束",
            "low_signal_or_failure": "突然断掉、无总结、只剩直播中段",
            "route_fit": "native_clip / adjacent_merge_candidate",
            "status_boundary": "缺结尾时优先转相邻窗口合并",
        },
        {
            "tag_id": "tag_10",
            "tag_name": "high_pattern_reusability",
            "中文含义": "这套标题和结构可批量复刻，不只是单条偶然可用",
            "selection_value": "让 Codex 后续能稳定按模式挑素材",
            "high_signal_evidence": "人群+痛点+动作/道具+结果兑现可复用",
            "low_signal_or_failure": "只靠单条素材特殊背景或偶然画面",
            "route_fit": "selection_standard_learning",
            "status_boundary": "正样本规律不等于绝对正确",
        },
    ]


STANDARDS = [
    {
        "id": "A",
        "name": "原生口播切片选片标准",
        "fit": "直播里本身有完整表达，能较少人工补写。",
        "pass": ["开头 0-8 秒有观看理由", "口播/字幕说明完整", "中段兑现问题或方法", "结尾自然收束", "画面支撑口播"],
        "fail": ["有话题但没有方法", "只有姿态没有语义", "结尾突然断掉", "需要大量补写才成立"],
        "reject": ["口播不可确认且画面无动作价值", "健康/业务风险无法降级表达"],
        "fields": ["semantic_completeness", "hook_strength", "middle_delivery", "ending_closure", "visual_supports_semantic"],
    },
    {
        "id": "B",
        "name": "动作教学再包装选片标准",
        "fit": "直播画面有动作或道具价值，但需要 TTS/字幕/问题前置包装。",
        "pass": ["动作清楚", "动作循环或关键步骤可见", "小白能看出方向", "可补明确问题", "字幕能标发力点/禁忌/次数"],
        "fail": ["动作存在但看不懂目标", "只有重复摆动", "道具用途不明", "包装后仍无法解释价值"],
        "reject": ["动作风险高且无专业边界", "视觉证据不足以承载教学"],
        "fields": ["visual_action_value", "teaching_action_value", "repackaging_value_score", "repackaging_cost", "risk_deduction"],
    },
    {
        "id": "C",
        "name": "相邻窗口合并选片标准",
        "fit": "单窗口不完整，但前后窗口能组成同一问题链路。",
        "pass": ["前窗口有问题引入", "当前窗口有方法/动作", "后窗口有总结/收束", "合并后仍是同一问题", "合并成本可控"],
        "fail": ["前后窗口主题漂移", "只靠拼接仍缺方法", "合并后过长或节奏散"],
        "reject": ["三个窗口合并后仍没有观看理由或教学交付"],
        "fields": ["need_merge_previous", "need_merge_next", "adjacent_merge_score", "semantic_topic_consistency", "editing_feasibility"],
    },
    {
        "id": "D",
        "name": "待音频复核选片标准",
        "fit": "画面有价值线索，但口播/字幕证据缺失。",
        "pass": ["画面值得听审", "可能有高价值口播", "有动作/道具/表情/手势线索", "听审能决定去留"],
        "fail": ["画面线索弱", "无动作也无互动", "无法推断可能问题"],
        "reject": ["听完口播仍无问题、方法、风险说明"],
        "fields": ["audio_transcript_status", "visual_lead_strength", "possible_problem_signal", "listen_review_priority", "fallback_reject_rule"],
    },
    {
        "id": "E",
        "name": "直接淘汰标准",
        "fit": "不值得剪、不值得包装、不值得听审。",
        "pass": ["动作不清", "无信息增量", "缺上下文且不可补", "风险过高", "只有静态画面或重复手势", "包装成本大于价值"],
        "fail": ["如果有相邻窗口/音频可救回，不应直接淘汰，应转 C/D"],
        "reject": ["满足任一硬淘汰条件且没有救回证据"],
        "fields": ["reject_reason", "rescue_level", "evidence_missing", "risk_deduction", "manual_packaging_cost"],
    },
]


def build_standard_sample_matrix(positive_rows: list[dict[str, Any]], rejected_rows: list[dict[str, Any]], c9623_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    positive_by_tag = defaultdict(list)
    for row in positive_rows:
        for tag in stringify(row.get("viewer_problem_value", "")).split("；"):
            positive_by_tag[tag].append(row)
    c_by_status = defaultdict(list)
    for row in c9623_rows:
        c_by_status[row.get("candidate_status", "")].append(row)

    def add(standard_id: str, standard_name: str, sample_type: str, sample_ref: str, file_or_segment: str, why: str, basis: str, action: str, boundary: str) -> None:
        matrix.append(
            {
                "standard_id": standard_id,
                "standard_name": standard_name,
                "sample_type": sample_type,
                "sample_ref": sample_ref,
                "file_or_segment": file_or_segment,
                "why_it_matches_or_fails": why,
                "evidence_basis": basis,
                "next_codex_action": action,
                "boundary_status": boundary,
            }
        )

    first_existing = next((r for r in positive_rows if r["parse_basis"] == "existing_multimodal_structure_reused"), positive_rows[0] if positive_rows else {})
    first_action = next((r for r in positive_rows if "action_repackaging" in r.get("route_decision", "") or "single_action" in r.get("content_archetype", "")), first_existing)
    first_repack = c_by_status.get("qualified_repackaging", [{}])[0]
    first_merge = c_by_status.get("qualified_merge_candidate", [{}])[0]
    first_audio = c_by_status.get("pending_audio_review", [{}])[0]
    first_reject = next((r for r in rejected_rows if "opening_missing" in stringify(r.get("failure_reason_tags", ""))), rejected_rows[0] if rejected_rows else {})

    add("A", "原生口播切片选片标准", "positive_reference", first_existing.get("sample_id", ""), first_existing.get("file_name", ""), "有前序结构解析，可学习完整开头/中段/结尾字段。", first_existing.get("parse_basis", ""), "若 semantic_completeness 过线，进入 native_clip_candidate。", "pending_user_review_not_publish_ready")
    add("B", "动作教学再包装选片标准", "positive_or_c9623_reference", first_repack.get("candidate_id", first_action.get("sample_id", "")), first_repack.get("start_time", first_action.get("file_name", "")), "画面动作/道具可作为再包装底盘，但要补问题前置和风险提示。", first_repack.get("analysis_status", first_action.get("parse_basis", "")), "进入 action_repackaging_candidate，并要求 TTS/字幕/风险字段齐全。", "pending_audio_or_professional_review")
    add("C", "相邻窗口合并选片标准", "c9623_candidate", first_merge.get("candidate_id", ""), f"{first_merge.get('start_time', '')}-{first_merge.get('end_time', '')}", "单窗口价值不足，需靠前后窗口补问题和收束。", first_merge.get("source_windows", ""), "先合并相邻窗口再重新评分。", "not_export_publish_ready")
    add("D", "待音频复核选片标准", "c9623_candidate", first_audio.get("candidate_id", ""), f"{first_audio.get('start_time', '')}-{first_audio.get('end_time', '')}", "视觉有线索但 transcript_semantic_score 低，必须听口播。", first_audio.get("tts_action_alignment", ""), "转听审，不得猜口播。", "pending_audio_transcript")
    add("E", "直接淘汰标准", "weak_or_rejected", first_reject.get("sample_ref", ""), f"{first_reject.get('start_time', '')}-{first_reject.get('end_time', '')}", first_reject.get("why_not_priority", ""), stringify(first_reject.get("failure_reason_tags", "")), "若无可救回证据，保持 rejected。", "reject_not_quality_judgment")
    return matrix


def build_why_selected_rows(inventory: list[dict[str, Any]], rejected_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tag_counts: Counter[str] = Counter()
    examples: defaultdict[str, list[str]] = defaultdict(list)
    for row in inventory:
        for tag in stringify(row.get("selection_reason_tags", "")).split("；"):
            if tag:
                tag_counts[tag] += 1
                if len(examples[tag]) < 5:
                    examples[tag].append(row.get("file_name", ""))
    weak_examples = {tag: row.get("sample_ref", "") for row in rejected_rows for tag in stringify(row.get("failure_reason_tags", "")).split("；") if tag}
    rows = []
    tag_defs = {row["tag_name"]: row for row in tag_library_rows()}
    for index, (tag, count) in enumerate(tag_counts.most_common(), start=1):
        definition = tag_defs.get(tag, {})
        rows.append(
            {
                "pattern_id": f"why_selected_{index:02d}",
                "selection_reason_tag": tag,
                "why_people_select_it": definition.get("selection_value", "标题或前序解析显示这个主题/问题在样本中高频出现。"),
                "what_problem_it_solves": definition.get("中文含义", tag),
                "what_keeps_viewers": definition.get("high_signal_evidence", "需要通过口播/视觉进一步确认。"),
                "best_route": definition.get("route_fit", "pending_route_after_review"),
                "supporting_sample_count": count,
                "example_files": examples.get(tag, [])[:5],
                "failure_counterexample": weak_examples.get(tag, ""),
                "codex_rule": definition.get("low_signal_or_failure", "不能把标题推断写成内容已确认。"),
            }
        )
    return rows


def build_c9623_review_rows(candidates: list[dict[str, str]], exports: list[dict[str, str]], packaging: list[dict[str, str]]) -> list[dict[str, Any]]:
    export_by_candidate = {row.get("candidate_id", ""): row for row in exports}
    package_by_candidate = {row.get("candidate_id", ""): row for row in packaging}
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(candidates, start=1):
        export = export_by_candidate.get(row.get("candidate_id", ""), {})
        pack = package_by_candidate.get(row.get("candidate_id", ""), {})
        status = row.get("candidate_status", "")
        if status == "qualified_repackaging":
            value = "可做人审动作教学再包装素材；不是发布候选。"
            next_decision = "听口播后补问题前置/TTS/字幕，再决定是否包装。"
        elif status == "qualified_merge_candidate":
            value = "可做相邻窗口合并复核；单窗口不独立成立。"
            next_decision = "扩前后窗口并重算语义完整度。"
        elif status == "pending_audio_review":
            value = "画面线索不足以单独定案，需音频/字幕复核。"
            next_decision = "先听审；不通过则淘汰。"
        else:
            value = "当前证据不足或不可用，保持弃用索引。"
            next_decision = "不导出，除非用户指定人工重判。"
        rows.append(
            {
                "review_id": f"c9623_value_{index:03d}",
                "candidate_id": row.get("candidate_id", ""),
                "candidate_status": status,
                "route_decision": row.get("route_decision", ""),
                "start_time": row.get("start_time", ""),
                "end_time": row.get("end_time", ""),
                "priority_score": row.get("priority_score", ""),
                "value_judgment": value,
                "why_selected_or_exported": row.get("why_selected") or export.get("why_exported", ""),
                "why_not_publish_ready": "pending_audio_transcript / pending_user_review / health_action_risk_pending_professional_review",
                "manual_packaging_action": pack.get("tts_or_voiceover_advice") or row.get("manual_packaging_advice", ""),
                "audio_transcript_status": row.get("tts_action_alignment", "pending_audio_transcript"),
                "risk_boundary": "不确认审美、动作专业性、健康表达、业务转化或发布可用。",
                "next_decision": next_decision,
            }
        )
    return rows


def scoring_matrix_markdown() -> str:
    fields = [
        ("viewer_problem_value", "观众问题价值", "0-10", "具体痛点/人群/场景明确", "泛愿望或无问题", "无可识别观看理由", "漏尿尴尬、小肚子凸、盆底松"),
        ("hook_strength", "开头钩子强度", "0-10", "0-3 秒建立问题或误区", "开头只有寒暄/空镜/口号", "8 秒内仍无观看理由", "70%女性中招的误区"),
        ("visual_action_value", "画面动作价值", "0-10", "动作起止/方向/道具关系清楚", "静态或零散手势", "无动作且无语义", "瑜伽小球动作循环可见"),
        ("teaching_action_value", "教学动作价值", "0-10", "能标步骤、发力点、禁忌、次数", "只看见动但不知道练什么", "动作风险高且不可解释", "臀桥呼吸可拆成步骤"),
        ("semantic_completeness", "语义完整度", "0-10", "开头-中段-结尾闭合", "缺开头/中段/结尾", "无口播/字幕且画面不可解释", "问题提出后有方法和收束"),
        ("problem_action_bridge", "问题动作桥接", "0-10", "0-6 秒进入动作/方法", "问题和动作断裂", "没有桥接证据", "先点痛点，马上演示动作"),
        ("editing_feasibility", "剪辑可行性", "0-10", "起止点清楚、可粗剪、时长可控", "需要大量补拍/补写", "合并后仍不可剪", "单动作 30-60 秒或可合并窗口"),
        ("repackaging_cost", "人工包装成本", "0-10 倒扣", "低成本补 TTS/字幕即可", "要重写结构、重配图、重审风险", "成本大于价值", "动作清楚但缺问题前置"),
        ("risk_deduction", "风险扣分", "0-20 扣分", "风险可通过提示降级", "疗效/健康承诺强", "存在不可控健康/商业风险", "治疗脱垂、越练越紧需谨慎"),
        ("selection_priority", "选片优先级", "P0-P3", "高问题价值+低风险+低包装成本", "仅单一维度高", "淘汰", "P0 原生/P1 再包装/P2 听审/P3 淘汰"),
    ]
    lines = [
        "# 可执行评分矩阵",
        "",
        "状态：`已确认` 本矩阵用于下一轮选片，不代表任何片段已发布通过。",
        "",
        "| 字段 | 中文含义 | 评分范围 | 高分表现 | 低分表现 | 直接淘汰条件 | 示例 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in fields:
        lines.append("| " + " | ".join(f"`{row[0]}`" if i == 0 else row[i] for i in range(len(row))) + " |")
    lines.extend(
        [
            "",
            "## 计算建议",
            "",
            "- `selection_score = viewer_problem_value + hook_strength + visual_action_value + teaching_action_value + semantic_completeness + problem_action_bridge + editing_feasibility - repackaging_cost - risk_deduction`。",
            "- `P0_native`：语义完整度和桥接高，风险低，可直接粗剪成人审片段。",
            "- `P1_repackaging`：视觉动作价值高，但语义/开头缺口可通过 TTS/字幕低成本补齐。",
            "- `P2_audio_review`：画面线索存在，但语义证据缺失，必须先听审。",
            "- `P3_reject`：无问题、无动作、无语义、风险高或包装成本大于价值。",
        ]
    )
    return "\n".join(lines) + "\n"


def runtime_fields_markdown() -> str:
    return """# Codex 选片运行字段设计

状态：`已确认` 这是下一轮 Codex 选片的字段合同；`待验证` 标准仍需用户人审校正。

## 输入字段

- `source_file`：原始直播或成片文件。
- `start_time / end_time / duration_seconds`：候选窗口边界。
- `transcript_text / subtitle_text`：口播与字幕证据；缺失时写 `pending_audio_transcript`。
- `visual_evidence_timecodes`：动作、道具、表情、场景证据时间点。
- `source_neighbors`：前后窗口 id，用于相邻合并。

## 中间判断字段

- `viewer_problem_value`
- `hook_strength`
- `visual_action_value`
- `teaching_action_value`
- `semantic_completeness`
- `problem_action_bridge_seconds`
- `tts_action_alignment`
- `adjacent_merge_score`
- `repackaging_cost`
- `risk_deduction`

## 输出字段

- `content_archetype`
- `route_decision`
- `candidate_status`
- `selection_reason_tags`
- `why_selected`
- `why_rejected`
- `manual_packaging_advice`
- `manual_review_items`

## 候选状态

- `qualified_native_candidate`：原生口播/字幕结构完整，进入人审粗剪。
- `qualified_repackaging`：动作/道具价值成立，但需 TTS/字幕包装。
- `qualified_merge_candidate`：单窗口不完整，需相邻合并。
- `pending_audio_review`：画面有价值线索，但语义证据缺失。
- `reject_unusable`：无剪辑/包装/听审价值或风险过高。

## 导出规则

1. 只导出 `qualified_native_candidate`、`qualified_repackaging`、`qualified_merge_candidate` 的人审素材。
2. `pending_audio_review` 只在抽样听审任务里导出，不进入发布候选。
3. 导出文件必须保留 `pending_user_review` 和风险字段。

## 淘汰规则

1. 无观看理由且无动作/方法证据。
2. 有动作但无法解释目标、方向、发力点或禁忌。
3. 缺上下文且相邻窗口不可补。
4. 健康/业务风险无法通过提示降级。
5. 人工包装成本大于潜在价值。

## 人工复核规则

- 用户人审：判断观感、品牌适配、是否值得继续包装。
- 专业人审：判断动作专业性、禁忌、健康表达。
- 业务人审：判断是否涉及疗效/商业承诺。

## 失败回退规则

- 语义缺失：转 `pending_audio_review`。
- 单窗口不完整：转 `qualified_merge_candidate`。
- 动作可见但无问题：转 `qualified_repackaging` 并要求补问题前置。
- 风险过高：转 `reject_unusable`。
"""


def manual_feedback_markdown() -> str:
    return """# 人审反馈表

状态：`待验证` 本表给用户/人工审片使用，不代表 Codex 已确认审美、动作专业性或业务通过。

## 使用方式

每条候选请填写：

| 字段 | 选项/填写 |
| --- | --- |
| `sample_or_candidate_id` | 对应 CSV 里的 id |
| `human_selection_decision` | keep / package / merge / audio_review / reject |
| `why_human_select_or_reject` | 人工真实原因 |
| `hook_ok` | yes / no / unsure |
| `action_or_semantic_ok` | yes / no / unsure |
| `risk_ok` | yes / no / professional_review_needed |
| `packaging_needed` | none / tts / subtitle / diagram / boundary_extension |
| `priority` | P0 / P1 / P2 / P3 |
| `notes` | 具体修改建议 |

## 人审时必须区分

- `素材值得进池` 不等于 `可以发布`。
- `动作看起来清楚` 不等于 `动作专业性通过`。
- `标题有吸引力` 不等于 `口播/字幕证据成立`。
- `本地导出成功` 不等于 `业务目标通过`。
"""


def standard_report_markdown(counts: dict[str, Any]) -> str:
    standards_text = []
    for standard in STANDARDS:
        standards_text.append(
            f"""## 标准 {standard['id']}：{standard['name']}

适用条件：{standard['fit']}

通过条件：
{bullet_lines(standard['pass'])}

失败条件：
{bullet_lines(standard['fail'])}

淘汰条件：
{bullet_lines(standard['reject'])}

建议字段：{', '.join(f'`{field}`' for field in standard['fields'])}
"""
        )
    return f"""# 选片标准总报告

状态：`已确认` 本轮已生成选片标准、评分矩阵、运行字段和人审反馈表；`待验证` 用户人审是否认可、标准能否稳定用于新直播素材。

## 本轮素材范围

| 项目 | 结果 |
| --- | ---: |
| AI需要的成片非 `成品/` 有效视频 | {counts['material_video_count']} |
| 已排除 `成品/` 视频 | {counts['excluded_finished_count']} |
| 跳过 AppleDouble 隐藏视频文件 | {counts['skipped_hidden_count']} |
| 复用前序 AI 成片解析 | {counts['matched_existing_analysis_count']} |
| 仅标题/元数据层待复核 | {counts['title_metadata_only_count']} |
| C9623 候选 | {counts['c9623_candidate_count']} |
| C9623 本地导出索引 | {counts['c9623_export_count']} |
| C9623 实际导出视频 | {counts['c9623_actual_exported_count']} |
| C9623 人工包装建议 | {counts['c9623_packaging_count']} |
| 弃用/弱样本原因 | {counts['rejected_reason_count']} |

## 核心结论

1. 别人选片通常不是因为“画面动了”，而是因为开头能指向明确人群/痛点，随后能用动作、字幕、口播或道具兑现。
2. 当前项目应同时保留五条路线：原生口播、动作教学再包装、相邻窗口合并、待音频复核、直接淘汰。
3. 动作教学再包装的价值来自“动作可解释 + 问题可前置 + TTS/字幕能补齐教学 + 风险可控”，不是单纯有动作。
4. 只有静态画面、零散手势、重复动作、缺上下文且不可补、强健康/疗效承诺的片段，不应优先进入剪辑池。
5. 下一轮 Codex 必须用 `viewer_problem_value / hook_strength / visual_action_value / semantic_completeness / problem_action_bridge / repackaging_cost / risk_deduction` 等字段判断。
6. 审美、动作专业性、健康表达、业务转化仍全部 `待验证`。
7. `已确认`：C9623 当前没有 `qualified_native` 原生切片候选，不能把本地导出的人审素材写成原生切片已成立。

## 选片标准

{''.join(standards_text)}

## 本轮边界

- 没有新增外部 API 调用。
- 没有提交视频、音频、关键帧、contact sheet 或 API 原始 JSON。
- 没有把 C9623 本地导出写成发布通过。
- 没有把正样本规律写成绝对正确，只作为反推参考。
- 没有把标题层推断写成视觉/口播内容已确认。
"""


def bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def execution_report_markdown(boundary: dict[str, str], counts: dict[str, Any], generated_files: list[Path]) -> str:
    files = "\n".join(f"- `{path.relative_to(REPO_ROOT)}`" for path in generated_files)
    return f"""# 115 选片标准反推报告

任务类型：`clip_selection_standard_reverse_engineering`

状态：`generated_pending_validation_commit_push`

## Impact check

| 项目 | 结果 |
| --- | --- |
| pwd | `{boundary['pwd']}` |
| repo_root | `{boundary['repo_root']}` |
| branch | `{boundary['branch']}` |
| remote | `{boundary['remote']}` |
| git status before write | `{boundary['git_status_short']}` |
| 素材目录 | `{MATERIAL_ROOT}` |
| ffprobe | `{boundary['ffprobe'] or 'unavailable'}` |
| 是否读取本地 outputs | 是，仅读取 C9623 导出索引 CSV，不读取/提交媒体 |
| 是否提交媒体 | 否 |
| 是否涉及 secret | 否 |
| 是否新增脚本 | 是，`scripts/clip_selection_standard_reverse_engineering.py` |

## 读取报告

- `{REPORT_112.relative_to(REPO_ROOT)}`
- `{REPORT_113_REPLAN.relative_to(REPO_ROOT)}`
- `{REPORT_113_V2.relative_to(REPO_ROOT)}`
- `{REPORT_114.relative_to(REPO_ROOT)}`

## 读取样本表

- `{AI_TOP100_CSV.relative_to(REPO_ROOT)}`
- `{PN_GAP_CSV.relative_to(REPO_ROOT)}`
- `{C9623_CANDIDATE_CSV.relative_to(REPO_ROOT)}`
- `{C9623_EXPORT_CSV.relative_to(REPO_ROOT)}`
- `{C9623_PACKAGING_CSV.relative_to(REPO_ROOT)}`
- `{C9623_REJECTED_CSV.relative_to(REPO_ROOT)}`

## 输出统计

| 输出 | 数量 |
| --- | ---: |
| 正样本/AI 成片范围视频 | {counts['material_video_count']} |
| 复用已有解析 | {counts['matched_existing_analysis_count']} |
| 标题/元数据待复核 | {counts['title_metadata_only_count']} |
| 负样本/弱样本原因 | {counts['rejected_reason_count']} |
| C9623 候选价值复盘 | {counts['c9623_candidate_count']} |
| C9623 实际导出视频 | {counts['c9623_actual_exported_count']} |
| 选片理由标签 | {counts['tag_count']} |
| 选片标准 | {counts['standard_count']} |

## 生成文件

{files}

## 边界确认

- 是否提交媒体：否
- 是否提交 API 原始输出：否
- 是否提交 `.env`：否
- 是否提交 API key：否
- 是否写审美通过：否
- 是否写动作专业性通过：否
- 是否写健康表达通过：否
- 是否写业务通过：否
- 是否写稳定批量运行：否

## 后续验证命令

- `python3 -m py_compile scripts/clip_selection_standard_reverse_engineering.py`
- `python3 scripts/clip_selection_standard_reverse_engineering.py --dry-run`
- `python3 scripts/clip_selection_standard_reverse_engineering.py --run`
- `git diff --check`
- `git status --short`
- `git diff --cached --check`
"""


def write_simple_docx(path: Path, title: str, markdown_text: str) -> None:
    """Write a deterministic compact-reference DOCX without external dependencies."""
    path.parent.mkdir(parents=True, exist_ok=True)
    paragraphs: list[tuple[str, str]] = [("Title", title), ("Subtitle", f"生成时间：{now_iso()}｜状态：pending_user_review")]
    for raw in markdown_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            paragraphs.append(("Heading1", line[2:]))
        elif line.startswith("## "):
            paragraphs.append(("Heading2", line[3:]))
        elif line.startswith("### "):
            paragraphs.append(("Heading3", line[4:]))
        elif line.startswith("- "):
            paragraphs.append(("ListParagraph", line[2:]))
        elif line.startswith("|"):
            continue
        else:
            paragraphs.append(("Normal", line))

    body = "\n".join(paragraph_xml(text, style) for style, text in paragraphs[:260])
    document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>
  </w:body>
</w:document>'''
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:eastAsia="Microsoft YaHei"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="200"/></w:pPr><w:rPr><w:b/><w:color w:val="0B2545"/><w:sz w:val="36"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="240"/></w:pPr><w:rPr><w:color w:val="555555"/><w:sz w:val="20"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="360" w:after="200"/></w:pPr><w:rPr><w:b/><w:color w:val="2E74B5"/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="280" w:after="140"/></w:pPr><w:rPr><w:b/><w:color w:val="2E74B5"/><w:sz w:val="26"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="200" w:after="100"/></w:pPr><w:rPr><w:b/><w:color w:val="1F4D78"/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="540" w:hanging="270"/><w:spacing w:after="80" w:line="300" w:lineRule="auto"/></w:pPr></w:style>
</w:styles>'''
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>''')
        docx.writestr("_rels/.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''')
        docx.writestr("word/_rels/document.xml.rels", '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>''')
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("word/styles.xml", styles_xml)


def paragraph_xml(text: str, style: str) -> str:
    safe = escape(text)
    if style == "ListParagraph":
        text_xml = f"• {safe}"
    else:
        text_xml = safe
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style != "Normal" else ""
    return f"<w:p>{style_xml}<w:r><w:t>{text_xml}</w:t></w:r></w:p>"


def run_pipeline(mode: str, probe_metadata: bool) -> dict[str, Any]:
    boundary = require_boundaries()
    videos, excluded_finished, skipped_hidden = discover_material_videos()
    ai_top100 = read_csv(AI_TOP100_CSV)
    pn_gap = read_csv(PN_GAP_CSV)
    c9623_candidates = read_csv(C9623_CANDIDATE_CSV)
    c9623_exports = read_csv(C9623_EXPORT_CSV)
    c9623_packaging = read_csv(C9623_PACKAGING_CSV)
    c9623_rejected = read_csv(C9623_REJECTED_CSV)
    formal_rejected = read_csv(FORMAL_REJECTED_CSV)
    formal_rescue = read_csv(FORMAL_RESCUE_CSV)

    if mode == "dry-run":
        actual_export_count = sum(1 for row in c9623_exports if not row.get("not_exported_reason", "").strip())
        counts = {
            "material_video_count": len(videos),
            "excluded_finished_count": excluded_finished,
            "skipped_hidden_count": skipped_hidden,
            "ai_top100_rows": len(ai_top100),
            "positive_negative_gap_rows": len(pn_gap),
            "c9623_candidate_count": len(c9623_candidates),
            "c9623_export_count": len(c9623_exports),
            "c9623_actual_exported_count": actual_export_count,
            "c9623_packaging_count": len(c9623_packaging),
            "reports_present": 4,
        }
        print(json.dumps({"mode": mode, "boundary": boundary, "counts": counts}, ensure_ascii=False, indent=2))
        return counts

    inventory = build_sample_inventory(videos, ai_top100, probe_metadata=probe_metadata)
    positive_rows = build_positive_reasons(inventory, ai_top100)
    rejected_rows = build_rejected_rows(c9623_rejected, formal_rejected, formal_rescue)
    tag_rows = tag_library_rows()
    standard_matrix = build_standard_sample_matrix(positive_rows, rejected_rows, c9623_candidates)
    why_selected_rows = build_why_selected_rows(inventory, rejected_rows)
    c9623_review_rows = build_c9623_review_rows(c9623_candidates, c9623_exports, c9623_packaging)

    matched_count = sum(1 for row in inventory if row["parse_basis"] == "existing_multimodal_structure_reused")
    actual_export_count = sum(1 for row in c9623_exports if not row.get("not_exported_reason", "").strip())
    counts = {
        "material_video_count": len(videos),
        "excluded_finished_count": excluded_finished,
        "skipped_hidden_count": skipped_hidden,
        "matched_existing_analysis_count": matched_count,
        "title_metadata_only_count": len(inventory) - matched_count,
        "c9623_candidate_count": len(c9623_candidates),
        "c9623_export_count": len(c9623_exports),
        "c9623_actual_exported_count": actual_export_count,
        "c9623_packaging_count": len(c9623_packaging),
        "rejected_reason_count": len(rejected_rows),
        "tag_count": len(tag_rows),
        "standard_count": len(STANDARDS),
    }

    write_csv(SAMPLE_INVENTORY_CSV, SAMPLE_FIELDS, inventory)
    write_csv(POSITIVE_REASON_CSV, POSITIVE_FIELDS, positive_rows)
    write_csv(REJECTED_REASON_CSV, REJECTED_FIELDS, rejected_rows)
    write_csv(TAG_LIBRARY_CSV, TAG_FIELDS, tag_rows)
    write_csv(STANDARD_SAMPLE_MATRIX_CSV, STANDARD_MATRIX_FIELDS, standard_matrix)
    write_csv(WHY_SELECTED_CSV, WHY_SELECTED_FIELDS, why_selected_rows)
    write_csv(C9623_REVIEW_CSV, C9623_REVIEW_FIELDS, c9623_review_rows)

    standard_md = standard_report_markdown(counts)
    scoring_md = scoring_matrix_markdown()
    runtime_md = runtime_fields_markdown()
    feedback_md = manual_feedback_markdown()
    human_md = "\n\n".join([standard_md, scoring_md, runtime_md, feedback_md])
    generated_files = [
        SAMPLE_INVENTORY_CSV,
        POSITIVE_REASON_CSV,
        REJECTED_REASON_CSV,
        TAG_LIBRARY_CSV,
        STANDARD_SAMPLE_MATRIX_CSV,
        WHY_SELECTED_CSV,
        C9623_REVIEW_CSV,
        STANDARD_REPORT_MD,
        SCORING_MATRIX_MD,
        RUNTIME_FIELDS_MD,
        MANUAL_FEEDBACK_MD,
        HUMAN_REPORT_MD,
        HUMAN_REPORT_DOCX,
        EXEC_REPORT_MD,
    ]
    write_text(STANDARD_REPORT_MD, standard_md)
    write_text(SCORING_MATRIX_MD, scoring_md)
    write_text(RUNTIME_FIELDS_MD, runtime_md)
    write_text(MANUAL_FEEDBACK_MD, feedback_md)
    write_text(HUMAN_REPORT_MD, human_md)
    write_simple_docx(HUMAN_REPORT_DOCX, "选片标准反推人读版报告", human_md)
    write_text(EXEC_REPORT_MD, execution_report_markdown(boundary, counts, generated_files))

    verify_outputs(generated_files)
    print(json.dumps({"mode": mode, "counts": counts, "generated_files": [str(p.relative_to(REPO_ROOT)) for p in generated_files]}, ensure_ascii=False, indent=2))
    return counts


def verify_outputs(paths: list[Path]) -> None:
    missing = [str(path.relative_to(REPO_ROOT)) for path in paths if not path.exists()]
    if missing:
        raise RuntimeError("blocked_output_missing: " + "；".join(missing))
    forbidden_exts = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".mp3", ".wav", ".png", ".jpg", ".jpeg", ".json"}
    for path in paths:
        if path.suffix.lower() in forbidden_exts:
            raise RuntimeError(f"blocked_media_or_raw_output_risk: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="反推直播切片选片标准")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="只检查边界和输入数量，不写文件")
    mode.add_argument("--run", action="store_true", help="生成本轮 CSV/MD/DOCX 产物")
    parser.add_argument("--skip-metadata-probe", action="store_true", help="不调用 ffprobe，只写文件大小和标题层解析")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mode = "run" if args.run else "dry-run"
    try:
        run_pipeline(mode, probe_metadata=not args.skip_metadata_probe)
    except Exception as exc:  # noqa: BLE001 - report controlled blocked reason to CLI
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
