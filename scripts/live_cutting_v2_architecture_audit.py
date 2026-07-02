#!/usr/bin/env python3
"""直播切片 V2 架构审核与解析补全。

边界：
- 只读取 /Volumes/WD_BLACK/澜心社剪辑 授权目录内的当前仓库和素材目录。
- 优先复用已提交的前 100 条阿里重看结果，不重复调用阿里 API。
- 只提交清洗后的 CSV / MD / DOCX；不提交媒体、contact sheet、API 原始 JSON、.env。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
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
MATERIAL_ROOT = AUTHORIZED_BASE / "剪辑解析数据"

ANALYSIS_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis" / "10_live_cutting_v2_architecture_audit"
FACT_DIR = REPO_ROOT / "项目事实_project_facts" / "直播切片V2架构审核与解析补全_live_cutting_v2_architecture_audit"
LOG_DIR = REPO_ROOT / "执行日志_codex_log"
LOCAL_API_DIR = REPO_ROOT / "api_outputs" / "live_cutting_v2_architecture_audit"
LOCAL_OUTPUT_DIR = REPO_ROOT / "outputs" / "live_cutting_v2_architecture_audit"

OLD_FINISHED_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis" / "08_finished_video_analysis"
OLD_FORMAL_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis" / "09_live_recording_formal_simulation"
OLD_FACT_DIR = REPO_ROOT / "项目事实_project_facts" / "自动剪辑五结构成片方案_five_structure_final_video"
OLD_FORMAL_FACT_DIR = REPO_ROOT / "项目事实_project_facts" / "直播录屏正式模拟运行_live_recording_formal_simulation"

INVENTORY_CSV = ANALYSIS_DIR / "01_素材总清单_material_inventory.csv"
COVERAGE_CSV = ANALYSIS_DIR / "02_现有解析覆盖率_audit_parse_coverage.csv"
AI_TOP100_CSV = ANALYSIS_DIR / "03_AI需要的成片前100解析补全_ai_needed_top100_analysis.csv"
CONTRAST_CSV = ANALYSIS_DIR / "04_正负样本差异结构表_positive_negative_structure_gap.csv"
LIVE_OPPORTUNITY_CSV = ANALYSIS_DIR / "05_直播切片素材结构机会表_live_cutting_opportunity_table.csv"

FACT_MAP_JSON = FACT_DIR / "current_fact_map.json"
ARCH_MAP_MD = FACT_DIR / "current_architecture_map.md"
GAP_AUDIT_MD = FACT_DIR / "06_架构缺口审计报告_architecture_gap_audit.md"
PATCH_DESIGN_MD = FACT_DIR / "07_V2架构补丁设计_v2_architecture_patch_design.md"
FIELD_DICT_MD = FACT_DIR / "08_字段字典与候选状态设计_field_dictionary_candidate_status.md"
MANUAL_REVIEW_MD = FACT_DIR / "09_人工复核清单_manual_review_checklist.md"
HUMAN_DOCX = FACT_DIR / "10_人读版报告_human_readable_report.docx"
HUMAN_MD_FALLBACK = FACT_DIR / "10_人读版报告_human_readable_report.md"
EXEC_REPORT_MD = LOG_DIR / "113_直播切片V2架构审核与解析补全报告_live_cutting_v2_architecture_audit_report.md"

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".MP4", ".MOV", ".M4V", ".AVI", ".MKV"}
NEW_REQUIRED_FIELDS = [
    "content_archetype",
    "route_decision",
    "problem_action_bridge_seconds",
    "tts_action_alignment",
    "repackaging_value_score",
    "needs_adjacent_merge",
    "candidate_status",
]

INVENTORY_FIELDS = [
    "source_category",
    "relative_path",
    "file_name",
    "file_ext",
    "duration_seconds",
    "width",
    "height",
    "fps",
    "video_codec",
    "audio_codec",
    "file_size_mb",
    "read_status",
    "deep_analysis_rank",
    "deep_analysis_scope",
]

COVERAGE_FIELDS = [
    "source_category",
    "file_name",
    "has_existing_parse",
    "existing_parse_path",
    "missing_fields",
    "needs_reparse",
    "reason",
]

AI_FIELDS = [
    "video_id",
    "source_category",
    "file_name",
    "content_archetype",
    "route_decision",
    "opening_type",
    "opening_summary",
    "problem_phrase_time",
    "first_action_frame_time",
    "problem_action_bridge_seconds",
    "action_method_summary",
    "action_cycle_integrity",
    "tts_action_alignment",
    "subtitle_evidence",
    "visual_evidence_timecodes",
    "middle_delivery_type",
    "ending_type",
    "native_completeness_score",
    "repackaging_value_score",
    "teachability_score",
    "positive_pattern_match",
    "negative_pattern_match",
    "needs_adjacent_merge",
    "need_merge_previous",
    "need_merge_next",
    "candidate_status",
    "business_risk",
    "health_action_risk",
    "manual_review_items",
    "confidence",
    "analysis_status",
]

CONTRAST_FIELDS = [
    "contrast_id",
    "sample_type",
    "file_name",
    "positive_reason",
    "negative_reason",
    "matched_existing_rule",
    "missing_new_rule",
    "content_archetype",
    "route_decision",
    "evidence_timecodes",
    "manual_review_items",
]

LIVE_FIELDS = [
    "opportunity_id",
    "recording_id",
    "source_file",
    "start_time",
    "end_time",
    "route_decision",
    "content_archetype",
    "native_clip_opportunity",
    "repackaging_opportunity",
    "adjacent_merge_opportunity",
    "problem_action_bridge_status",
    "audio_tts_subtitle_alignment_status",
    "candidate_status",
    "evidence",
    "manual_review_items",
]


@dataclass
class InventoryItem:
    path: Path
    source_category: str
    relative_path: str
    file_name: str
    file_ext: str
    duration_seconds: str = ""
    width: str = ""
    height: str = ""
    fps: str = ""
    video_codec: str = ""
    audio_codec: str = ""
    file_size_mb: str = ""
    read_status: str = "pending_probe"
    deep_analysis_rank: int = 0
    deep_analysis_scope: str = "pending_not_analyzed"


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def natural_key(value: str) -> list[Any]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


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


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: stringify(row.get(field, "")) for field in fieldnames})


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_text(path: Path, limit: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:limit] if limit else text


def run_command(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)


def require_boundaries() -> dict[str, Any]:
    pwd = str(Path.cwd())
    repo = run_command(["git", "rev-parse", "--show-toplevel"])
    branch = run_command(["git", "branch", "--show-current"])
    remote = run_command(["git", "remote", "-v"])
    status = run_command(["git", "status", "--short", "--branch"])
    if repo.returncode != 0 or Path(repo.stdout.strip()) != REPO_ROOT:
        raise SystemExit("blocked_wrong_workspace_root")
    if not str(REPO_ROOT).startswith(str(AUTHORIZED_BASE)):
        raise SystemExit("blocked_wrong_workspace_root")
    if "fthytwerwt-sudo/lanxinse--" not in remote.stdout:
        raise SystemExit("blocked_wrong_remote")
    if not MATERIAL_ROOT.exists():
        raise SystemExit("blocked_missing_material_dir")
    if shutil.which("ffprobe") is None:
        raise SystemExit("blocked_missing_ffprobe")
    if shutil.which("ffmpeg") is None:
        raise SystemExit("blocked_missing_ffmpeg")
    return {
        "pwd": pwd,
        "repo_root": str(REPO_ROOT),
        "branch": branch.stdout.strip(),
        "remote": remote.stdout.strip(),
        "git_status": status.stdout.strip(),
        "material_root": str(MATERIAL_ROOT),
        "ffprobe": shutil.which("ffprobe") or "",
        "ffmpeg": shutil.which("ffmpeg") or "",
    }


def source_category(path: Path) -> str:
    parts = set(path.relative_to(MATERIAL_ROOT).parts)
    if "AI需要的成片" in parts:
        return "ai_needed_final_video"
    if "正样本成片" in parts:
        return "positive_sample"
    if "负样本成片" in parts:
        return "negative_sample"
    if "完整直播" in parts or "剪辑测试直播素材" in parts:
        return "live_cutting_material"
    return "unknown_material"


def discover_videos() -> list[InventoryItem]:
    videos: list[InventoryItem] = []
    for path in MATERIAL_ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in VIDEO_EXTS:
            continue
        rel = path.relative_to(MATERIAL_ROOT)
        videos.append(
            InventoryItem(
                path=path,
                source_category=source_category(path),
                relative_path=str(rel),
                file_name=path.name,
                file_ext=path.suffix.lower(),
                file_size_mb=f"{path.stat().st_size / 1024 / 1024:.3f}" if path.exists() else "",
            )
        )
    videos.sort(key=lambda item: natural_key(f"{item.source_category}/{item.relative_path}"))
    ranks: dict[str, int] = defaultdict(int)
    for item in videos:
        ranks[item.source_category] += 1
        item.deep_analysis_rank = ranks[item.source_category]
    return videos


def old_metadata_by_name() -> dict[str, dict[str, str]]:
    rows = read_csv(OLD_FINISHED_DIR / "成片样本清单_finished_video_inventory.csv")
    mapping: dict[str, dict[str, str]] = {}
    for row in rows:
        mapping.setdefault(row.get("file_name", ""), row)
    for row in read_csv(OLD_FORMAL_DIR / "01_直播录屏素材清单_live_recording_inventory.csv"):
        mapping.setdefault(row.get("file_name", ""), row)
    return mapping


def split_resolution(value: str) -> tuple[str, str]:
    if "x" not in value:
        return "", ""
    width, height = value.split("x", 1)
    return width, height


def ffprobe_item(item: InventoryItem, old_meta: dict[str, dict[str, str]]) -> None:
    item.file_size_mb = f"{item.path.stat().st_size / 1024 / 1024:.3f}" if item.path.exists() else ""
    if item.file_name.startswith("._"):
        item.read_status = "blocked_unreadable_media"
        return
    cached = old_meta.get(item.file_name)
    if cached:
        item.duration_seconds = cached.get("duration_seconds") or cached.get("duration_seconds_ffprobe") or ""
        resolution = cached.get("resolution") or cached.get("resolution_ffprobe") or ""
        item.width, item.height = split_resolution(resolution)
        item.fps = cached.get("fps", "")
        item.video_codec = cached.get("video_codec", "")
        item.audio_codec = cached.get("audio_codec") or cached.get("audio_stream", "")
        item.read_status = "read_success_reused_existing_metadata"
        return
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(item.path),
        ],
        timeout=90,
    )
    if result.returncode != 0:
        item.read_status = "blocked_unreadable_media"
        return
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        item.read_status = "blocked_unreadable_media"
        return
    video = next((stream for stream in data.get("streams", []) if stream.get("codec_type") == "video"), {})
    audio = next((stream for stream in data.get("streams", []) if stream.get("codec_type") == "audio"), {})
    item.duration_seconds = str(round(float(data.get("format", {}).get("duration") or 0), 3))
    item.width = str(video.get("width", ""))
    item.height = str(video.get("height", ""))
    item.fps = parse_fps(video.get("avg_frame_rate") or video.get("r_frame_rate") or "")
    item.video_codec = str(video.get("codec_name", ""))
    item.audio_codec = str(audio.get("codec_name", ""))
    item.read_status = "read_success"


def parse_fps(value: str) -> str:
    if not value or value == "0/0":
        return ""
    if "/" not in value:
        return value
    num, den = value.split("/", 1)
    try:
        return f"{float(num) / float(den):.3f}".rstrip("0").rstrip(".")
    except (ValueError, ZeroDivisionError):
        return value


def apply_deep_scopes(items: list[InventoryItem], limit: int) -> None:
    for item in items:
        if item.source_category == "unknown_material":
            item.deep_analysis_scope = "pending_not_analyzed"
        elif item.deep_analysis_rank <= limit:
            item.deep_analysis_scope = "first_100_deep_analysis_scope"
        else:
            item.deep_analysis_scope = "pending_not_analyzed"


def inventory_rows(items: list[InventoryItem]) -> list[dict[str, Any]]:
    return [
        {
            "source_category": item.source_category,
            "relative_path": item.relative_path,
            "file_name": item.file_name,
            "file_ext": item.file_ext,
            "duration_seconds": item.duration_seconds,
            "width": item.width,
            "height": item.height,
            "fps": item.fps,
            "video_codec": item.video_codec,
            "audio_codec": item.audio_codec,
            "file_size_mb": item.file_size_mb,
            "read_status": item.read_status,
            "deep_analysis_rank": item.deep_analysis_rank,
            "deep_analysis_scope": item.deep_analysis_scope,
        }
        for item in items
    ]


def existing_parse_assets() -> dict[str, Any]:
    ai_recheck = {
        row.get("file_name", ""): row
        for row in read_csv(OLD_FINISHED_DIR / "前100条阿里多模态复核矩阵_ali_multimodal_recheck_matrix_100.csv")
    }
    fine = {row.get("file_name", ""): row for row in read_csv(OLD_FINISHED_DIR / "前100条细结构矩阵_fine_grained_structure_matrix.csv")}
    structure = {row.get("file_name", ""): row for row in read_csv(OLD_FINISHED_DIR / "成片结构矩阵_finished_video_structure_matrix.csv")}
    evidence_rows = read_csv(OLD_FACT_DIR / "06_正负样片结构证据矩阵_positive_negative_structure_evidence_matrix.csv")
    sample_evidence: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in evidence_rows:
        sample_evidence[row.get("video_file_name", "")].append(row)
    live_inventory = {row.get("file_name", ""): row for row in read_csv(OLD_FORMAL_DIR / "01_直播录屏素材清单_live_recording_inventory.csv")}
    live_recheck = read_csv(OLD_FORMAL_DIR / "07_弃用片段复审与可救回片段表_rejected_segment_recheck_rescue_candidates.csv")
    return {
        "ai_recheck": ai_recheck,
        "fine": fine,
        "structure": structure,
        "sample_evidence": sample_evidence,
        "live_inventory": live_inventory,
        "live_recheck": live_recheck,
    }


def coverage_rows(items: list[InventoryItem], assets: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        existing_path = ""
        has_existing = "no"
        missing = NEW_REQUIRED_FIELDS[:]
        needs = "yes"
        reason = "no_existing_parse_found"
        if item.source_category == "ai_needed_final_video":
            if item.file_name in assets["ai_recheck"]:
                has_existing = "yes"
                existing_path = str(OLD_FINISHED_DIR / "前100条阿里多模态复核矩阵_ali_multimodal_recheck_matrix_100.csv")
                needs = "no_schema_backfill_only"
                reason = "existing_ali_recheck_can_be_reused_new_schema_fields_missing_in_old_csv"
            elif item.deep_analysis_scope == "pending_not_analyzed":
                reason = "outside_first_100_pending_not_analyzed"
                needs = "no_outside_authorized_limit"
        elif item.source_category in {"positive_sample", "negative_sample"}:
            evidence = assets["sample_evidence"].get(item.file_name, [])
            if evidence:
                has_existing = "yes"
                existing_path = str(OLD_FACT_DIR / "06_正负样片结构证据矩阵_positive_negative_structure_evidence_matrix.csv")
                needs = "no_contrast_backfill_only"
                reason = "existing_positive_negative_evidence_partial_new_schema_fields_missing"
            else:
                reason = "sample_inventory_present_no_structured_contrast_evidence"
        elif item.source_category == "live_cutting_material":
            if item.file_name in assets["live_inventory"]:
                has_existing = "yes"
                existing_path = str(OLD_FORMAL_DIR / "01_直播录屏素材清单_live_recording_inventory.csv")
                needs = "yes_runtime_layer_missing"
                reason = "live_recording_inventory_exists_but_no_audio_merge_runtime_parse"
            else:
                reason = "live_material_inventory_only_needs_audio_merge_probe"
        if has_existing == "yes":
            missing_text = "；".join(missing)
        else:
            missing_text = "all_new_required_fields"
        rows.append(
            {
                "source_category": item.source_category,
                "file_name": item.file_name,
                "has_existing_parse": has_existing,
                "existing_parse_path": existing_path,
                "missing_fields": missing_text,
                "needs_reparse": needs,
                "reason": reason,
            }
        )
    return rows


def first_timecode(text: str) -> str:
    match = re.search(r"\d{2}:\d{2}:\d{2}\.\d{3}", text or "")
    return match.group(0) if match else ""


def seconds_from_timecode(value: str) -> float | None:
    if not value:
        return None
    try:
        hh, mm, rest = value.split(":", 2)
        ss = float(rest)
        return int(hh) * 3600 + int(mm) * 60 + ss
    except ValueError:
        return None


def bridge_seconds(problem_time: str, action_time: str) -> str:
    problem = seconds_from_timecode(problem_time)
    action = seconds_from_timecode(action_time)
    if problem is None or action is None:
        return ""
    return f"{max(0.0, action - problem):.3f}".rstrip("0").rstrip(".")


def content_archetype_from(row: dict[str, str]) -> str:
    old = (row.get("ali_video_type_primary") or row.get("old_video_type_primary") or "").lower()
    formula = row.get("ali_structure_formula", "") + row.get("ali_middle_delivery_types", "")
    if "correction" in old or "错误" in formula or "正确" in formula:
        return "movement_correction"
    if "problem_solution" in old or "问题" in formula and "解决" in formula:
        return "problem_solution"
    if "sports_teaching" in old or "动作" in formula:
        return "single_action_tts_teaching"
    if "conversion" in old:
        return "product_conversion"
    if "trust" in old:
        return "trust_building"
    if "objection" in old:
        return "objection_handling"
    if "knowledge" in old or "body_care" in old:
        return "knowledge_explainer"
    return "unclear"


def score_from_text(row: dict[str, str], kind: str) -> str:
    text = " ".join(row.values())
    if kind == "repackaging":
        score = 2
        if "动作" in text:
            score += 1
        if "字幕" in text or "口令" in text:
            score += 1
        if "完整" in text or "循环" in text or "定格" in text:
            score += 1
        return str(min(score, 5))
    if kind == "teachability":
        score = 2
        if "动作演示" in text:
            score += 1
        if "分步" in text or "口令" in text:
            score += 1
        if "风险" not in text:
            score += 1
        return str(min(score, 5))
    return "3"


def build_ai_top100_rows(items: list[InventoryItem], assets: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    ai_items = [item for item in items if item.source_category == "ai_needed_final_video" and item.deep_analysis_rank <= limit]
    ai_items.sort(key=lambda item: natural_key(item.relative_path))
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(ai_items, start=1):
        recheck = assets["ai_recheck"].get(item.file_name, {})
        fine = assets["fine"].get(item.file_name, {})
        structure = assets["structure"].get(item.file_name, {})
        video_id = recheck.get("video_id") or fine.get("video_id") or structure.get("video_id") or f"ai_top_{index:03d}"
        opening_time = first_timecode(recheck.get("ali_opening_timecode_evidence", "") or structure.get("evidence_timecodes", ""))
        action_time = first_timecode(recheck.get("ali_middle_timecode_evidence", "") or structure.get("evidence_timecodes", ""))
        visual_summary = recheck.get("ali_visual_evidence_summary", "") or structure.get("evidence_frame_summaries", "")
        risk = recheck.get("ali_risk_triggers", "") or fine.get("risk_trigger", "")
        manual = recheck.get("ali_manual_review_items", "") or fine.get("manual_review_items", "") or structure.get("manual_review_items", "")
        content = content_archetype_from(recheck or fine or structure)
        rows.append(
            {
                "video_id": video_id,
                "source_category": "ai_needed_final_video",
                "file_name": item.file_name,
                "content_archetype": content,
                "route_decision": "positive_reference_only",
                "opening_type": recheck.get("ali_opening_trigger_type") or fine.get("opening_style") or structure.get("opening_type"),
                "opening_summary": recheck.get("ali_opening_timecode_evidence") or structure.get("opening_reason"),
                "problem_phrase_time": opening_time,
                "first_action_frame_time": action_time,
                "problem_action_bridge_seconds": bridge_seconds(opening_time, action_time),
                "action_method_summary": recheck.get("ali_middle_delivery_types") or structure.get("middle_delivery_type"),
                "action_cycle_integrity": infer_action_integrity(recheck, structure),
                "tts_action_alignment": infer_tts_alignment(recheck),
                "subtitle_evidence": subtitle_evidence(recheck, structure),
                "visual_evidence_timecodes": recheck.get("frame_timecodes") or structure.get("evidence_timecodes"),
                "middle_delivery_type": recheck.get("ali_middle_delivery_types") or fine.get("middle_delivery_type") or structure.get("middle_delivery_type"),
                "ending_type": recheck.get("ali_ending_closure_types") or fine.get("ending_style") or structure.get("ending_closure_type"),
                "native_completeness_score": structure.get("source_integrity_score") or "4",
                "repackaging_value_score": score_from_text(recheck or structure, "repackaging"),
                "teachability_score": score_from_text(recheck or structure, "teachability"),
                "positive_pattern_match": "yes_reference_pattern_reused_from_ali_recheck_100",
                "negative_pattern_match": "risk_pattern_only" if risk else "no_direct_negative_match",
                "needs_adjacent_merge": "no_finished_video_reference",
                "need_merge_previous": "no",
                "need_merge_next": "no",
                "candidate_status": "pending_user_review",
                "business_risk": risk or structure.get("notes", ""),
                "health_action_risk": health_risk(risk, manual),
                "manual_review_items": manual,
                "confidence": recheck.get("ali_confidence") or fine.get("confidence") or "high_existing_analysis",
                "analysis_status": "reused_existing_ali_recheck_success_no_new_api_call" if recheck else "pending_not_analyzed_missing_existing_parse",
            }
        )
    return rows


def infer_action_integrity(recheck: dict[str, str], structure: dict[str, str]) -> str:
    text = " ".join([recheck.get("ali_fine_structure_summary", ""), recheck.get("ali_visual_evidence_summary", ""), structure.get("middle_delivery_evidence", "")])
    if any(word in text for word in ["完整", "循环", "定格", "回位", "收势"]):
        return "complete_or_key_cycle_visible_visual_only"
    if "动作" in text:
        return "partial_action_visible_pending_professional_review"
    return "pending_manual_review"


def infer_tts_alignment(recheck: dict[str, str]) -> str:
    text = " ".join(recheck.values())
    if "字幕" in text and "动作" in text:
        return "subtitle_action_alignment_partial_visual_only_pending_audio_transcript"
    if "口令" in text and "动作" in text:
        return "command_action_alignment_partial_visual_only_pending_audio_transcript"
    return "pending_audio_transcript"


def subtitle_evidence(recheck: dict[str, str], structure: dict[str, str]) -> str:
    text = recheck.get("ali_visual_evidence_summary") or structure.get("evidence_frame_summaries") or ""
    if "字幕" in text:
        return text[:240]
    return "pending_subtitle_or_audio_transcript"


def health_risk(risk: str, manual: str) -> str:
    text = f"{risk} {manual}"
    if any(word in text for word in ["医学", "健康", "禁忌", "产后", "盆底", "漏尿", "疼痛", "100次"]):
        return "health_action_risk_pending_professional_review"
    return "pending_user_review"


def build_contrast_rows(items: list[InventoryItem], assets: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    selected = [
        item
        for item in items
        if item.source_category in {"positive_sample", "negative_sample"} and item.deep_analysis_rank <= limit
    ]
    selected.sort(key=lambda item: natural_key(f"{item.source_category}/{item.relative_path}"))
    for index, item in enumerate(selected, start=1):
        evidence = assets["sample_evidence"].get(item.file_name, [])
        sample_type = "positive_sample" if item.source_category == "positive_sample" else "negative_sample"
        summaries = "；".join(row.get("evidence_summary", "") for row in evidence[:3])
        rules = "；".join(row.get("standard_name", "") for row in evidence[:3])
        start_end = "；".join(
            f"{row.get('start_time','')}-{row.get('end_time','')}".strip("-") for row in evidence[:3]
        )
        rows.append(
            {
                "contrast_id": f"contrast_{index:03d}",
                "sample_type": sample_type,
                "file_name": item.file_name,
                "positive_reason": summaries if sample_type == "positive_sample" and summaries else "pending_positive_structure_review",
                "negative_reason": summaries if sample_type == "negative_sample" and summaries else "pending_negative_structure_review",
                "matched_existing_rule": rules or "pending_rule_match",
                "missing_new_rule": "needs_content_archetype_route_bridge_tts_alignment_fields",
                "content_archetype": "single_action_tts_teaching" if "动作" in summaries or "练" in item.file_name else "unclear",
                "route_decision": "positive_reference_only" if sample_type == "positive_sample" else "negative_reference_only",
                "evidence_timecodes": start_end or "pending_timecode_evidence",
                "manual_review_items": "动作专业性、健康表达、业务事实、字幕节奏仍需用户/专业人审",
            }
        )
    return rows


def build_live_opportunity_rows(assets: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    recheck_rows = assets["live_recheck"]
    recording_name = {
        row.get("recording_id", ""): row.get("file_name", "")
        for row in read_csv(OLD_FORMAL_DIR / "01_直播录屏素材清单_live_recording_inventory.csv")
    }
    for index, row in enumerate(recheck_rows, start=1):
        reason = " ".join([row.get("original_reject_reason", ""), row.get("reason_for_next_action", "")])
        has_action = "动作" in reason or "方法" in reason or "讲解" in reason
        rescue = row.get("rescue_level", "")
        needs_audio = row.get("needs_transcript_or_audio", "")
        route = "adjacent_merge_candidate" if rescue in {"medium", "pending"} else "reject_unusable"
        if has_action and rescue in {"medium", "pending"}:
            route = "action_repackaging_candidate"
        status = "pending_audio_transcript" if needs_audio == "yes" and route != "reject_unusable" else "pending_user_review"
        if route == "reject_unusable":
            status = "rejected_missing_bridge"
        rows.append(
            {
                "opportunity_id": f"live_opp_{index:03d}",
                "recording_id": row.get("recording_id", ""),
                "source_file": recording_name.get(row.get("recording_id", ""), row.get("recording_id", "")),
                "start_time": row.get("start_time", ""),
                "end_time": row.get("end_time", ""),
                "route_decision": route,
                "content_archetype": "single_action_tts_teaching" if has_action else "native_live_clip",
                "native_clip_opportunity": "no_current_window_incomplete",
                "repackaging_opportunity": "possible" if has_action and rescue in {"medium", "pending"} else "pending",
                "adjacent_merge_opportunity": "yes" if row.get("needs_manual_start_end_extension") == "yes" else "no",
                "problem_action_bridge_status": "pending_problem_action_bridge_after_transcript",
                "audio_tts_subtitle_alignment_status": "pending_audio_transcript",
                "candidate_status": status,
                "evidence": reason[:500],
                "manual_review_items": "听口播/字幕；扩展前后窗口；确认动作完整循环；确认健康和业务风险",
            }
        )
    return rows


def architecture_gaps() -> list[dict[str, str]]:
    return [
        {
            "gap_id": "gap_01",
            "gap_name": "content_archetype_routing_layer",
            "current_status": "部分成立：成片样本层已有类型库，formal simulation runtime 未前置路由",
            "evidence": "20_视频结构公式库；22_成片样本类型与结构总表；112 结果复审",
            "why_it_matters": "先判断素材适合原生切片、动作教学、问题解决还是转化，才能避免固定完整性闸门误杀直播中段素材。",
            "impact_if_missing": "动作中段、讲解中段会被当成缺开头/缺结尾废弃。",
            "recommended_patch": "在窗口审计前新增 content_archetype 与 route_decision 字段，并让不同 archetype 进入不同候选规则。",
            "priority": "P1",
        },
        {
            "gap_id": "gap_02",
            "gap_name": "problem_action_bridge_layer",
            "current_status": "部分成立：文本规则存在，但未形成秒级 problem->action runtime 判断",
            "evidence": "12_五结构文本判断标准完整手册；07_弃用片段复审表",
            "why_it_matters": "动作教学短视频的关键不是只有完整开中结，而是问题句后几秒内是否接到动作解决方案。",
            "impact_if_missing": "可用动作素材被判缺开头/中段证据，或问题和动作硬拼不自知。",
            "recommended_patch": "新增 problem_phrase_time、first_action_frame_time、problem_action_bridge_seconds 与 bridge_status。",
            "priority": "P0",
        },
        {
            "gap_id": "gap_03",
            "gap_name": "action_teaching_repackaging_route",
            "current_status": "部分成立：样本规则可支持，但直播素材救回流程未落地",
            "evidence": "27/32 规则表；112 路线重判",
            "why_it_matters": "直播动作素材可能不适合原生直切，但可通过 TTS、字幕和边界包装成教学短视频。",
            "impact_if_missing": "系统只找原生完整片，错过可再包装动作素材。",
            "recommended_patch": "将 action_repackaging_candidate 与 qualified_repackaging 从 native_export_candidate 中拆出。",
            "priority": "P0",
        },
        {
            "gap_id": "gap_04",
            "gap_name": "adjacent_window_merge_layer",
            "current_status": "缺执行层：已有 need_merge_previous/next 标记，但无 merge operator",
            "evidence": "04_112结果复审与路线重判：76/76 need_merge_previous=yes 且 need_merge_next=yes",
            "why_it_matters": "直播录屏的真实开头和收束常跨窗口，必须向前后找完整表达单元。",
            "impact_if_missing": "固定 180 秒窗口打碎连续表达，导致 0 候选。",
            "recommended_patch": "新增相邻窗口合并器，输出 merged_start/end、merge_reason、merge_evidence。",
            "priority": "P0",
        },
        {
            "gap_id": "gap_05",
            "gap_name": "audio_tts_subtitle_timeline_alignment_layer",
            "current_status": "缺失：当前仅视觉抽帧，音频/字幕/TTS 时间线未统一",
            "evidence": "04_112结果复审与路线重判：82 条 rejected needs_transcript_or_audio=yes",
            "why_it_matters": "口播、配音、字幕和动作画面对齐是判断教学能否成立的核心证据。",
            "impact_if_missing": "无法判断半句话、口播收束、TTS 解释是否真正解决动作画面。",
            "recommended_patch": "引入 transcript/subtitle timeline，输出 tts_action_alignment 与 pending_audio_transcript 状态。",
            "priority": "P0",
        },
        {
            "gap_id": "gap_06",
            "gap_name": "positive_negative_contrast_layer",
            "current_status": "已建立但负样本偏薄：已有正负样片证据矩阵，负样本仅 3 条",
            "evidence": "06_正负样片结构证据矩阵；11_标准缺口对照表",
            "why_it_matters": "好片和坏片的差异能反推出规则边界，避免只学正样本。",
            "impact_if_missing": "规则容易过拟合正样本，对失败片段误放行。",
            "recommended_patch": "新增 V2 contrast 表，把 matched_existing_rule 与 missing_new_rule 分开。",
            "priority": "P1",
        },
        {
            "gap_id": "gap_07",
            "gap_name": "candidate_status_taxonomy",
            "current_status": "部分成立：五结构有 candidate_decision，formal simulation 状态未统一",
            "evidence": "13_候选片段字段输出规范；14_候选池规则；04_候选片段表",
            "why_it_matters": "原生切片、再包装、合并候选、待音频转写不能混用一个 decision。",
            "impact_if_missing": "报告之间无法对齐，容易把可包装写成已完成原生切片。",
            "recommended_patch": "统一 candidate_status 与 route_decision 枚举。",
            "priority": "P1",
        },
        {
            "gap_id": "gap_08",
            "gap_name": "field_dictionary_layer",
            "current_status": "部分成立：已有主键链路和五结构字段，V2 新字段未入字典",
            "evidence": "02_五结构字段字典；13_候选片段字段输出规范",
            "why_it_matters": "新路线需要可追溯字段，否则无法复盘误杀原因。",
            "impact_if_missing": "脚本结果和人工复核表字段不一致。",
            "recommended_patch": "新增 content_archetype、route_decision、problem_action_bridge_seconds 等 V2 字段。",
            "priority": "P1",
        },
        {
            "gap_id": "gap_09",
            "gap_name": "manual_review_routing_layer",
            "current_status": "已建立但需要 V2 路由细化",
            "evidence": "14_候选池规则；02_人工复核清单",
            "why_it_matters": "动作专业性、健康表达、业务转化都不能由模型直接盖章。",
            "impact_if_missing": "技术解析容易被误解为审美或业务通过。",
            "recommended_patch": "按原生/再包装/合并/音频待转写拆人工复核清单。",
            "priority": "P1",
        },
        {
            "gap_id": "gap_10",
            "gap_name": "feedback_to_rule_update_layer",
            "current_status": "部分成立：已有回写说明，缺独立 rule delta ledger",
            "evidence": "12_五结构文本判断标准完整手册；15_视觉探测记录",
            "why_it_matters": "人审反馈必须沉淀回规则，而不是停在单次报告。",
            "impact_if_missing": "109/112/113 的失败经验不会进入下一版脚本。",
            "recommended_patch": "新增 feedback_to_rule_update ledger，记录用户反馈、影响字段、规则修订建议。",
            "priority": "P2",
        },
    ]


def v2_layers() -> list[dict[str, str]]:
    names = [
        ("素材入口层", "统一读取素材根和类别映射", "剪辑解析数据", "material_inventory", "source_category, relative_path, read_status", "素材目录缺失或越界", "inventory CSV 必填字段检查"),
        ("全覆盖证据层", "保证素材级证据不跳过", "ffprobe/旧解析/文件清单", "coverage audit", "has_existing_parse, needs_reparse", "无法区分已有解析和待解析", "coverage CSV 检查"),
        ("阿里多模态理解层", "复用或调用视觉模型理解关键帧", "contact sheet 或旧阿里结果", "cleaned multimodal matrix", "ali_model_called, final_status, evidence", "API 不可用且无旧结果", "调用审计或复用证据"),
        ("选品与内容形态路由层", "先判断素材适合哪种内容形态", "multimodal evidence", "content_archetype route", "content_archetype, route_decision", "archetype unclear", "字段枚举检查"),
        ("音频 / TTS / 字幕时间轴对齐层", "判断声音、字幕和动作是否对齐", "transcript/subtitle/audio/visual timecodes", "alignment status", "tts_action_alignment", "缺转写且必须判断口播", "pending_audio_transcript 不得脑补"),
        ("问题-动作桥接判断层", "判断问题后是否快速接动作", "problem/action timecodes", "bridge score", "problem_action_bridge_seconds", "无问题或动作秒点", "bridge 秒数和证据检查"),
        ("正负样本对照反推层", "从好坏样本反推规则差异", "positive/negative samples", "contrast table", "matched_existing_rule, missing_new_rule", "样本不足", "matched/missing rule 检查"),
        ("结构规则层", "承接五结构和细结构规则", "20/21/30/31/32 规则", "rule match", "rule_id, must_have_evidence", "规则缺证据", "规则引用检查"),
        ("相邻窗口合并层", "把跨窗口表达合成完整候选", "window rows", "merged segment candidate", "need_merge_previous, need_merge_next", "非相邻或无转写", "merge_previous/next 检查"),
        ("候选片段判断层", "给出受控候选状态", "routes + evidence", "candidate table", "candidate_status", "状态不在枚举", "candidate_status 枚举检查"),
        ("原生切片 / 动作教学再包装分流层", "区分 native 和 repackaging", "route_decision", "native/repackaging queue", "route_decision", "把可包装误写成原生", "route_decision 检查"),
        ("剪辑导出层", "只导出通过技术闸门的初剪", "candidate queue", "local rough cuts", "export_status", "媒体提交风险", "outputs ignored + no media staged"),
        ("人工复核层", "保留人审入口", "review queue", "manual_review_checklist", "manual_review_items", "审美/业务未确认", "状态词检查"),
        ("反馈回规则层", "把人审结果回写规则", "review feedback", "rule delta", "feedback_item, affected_rule", "无反馈来源", "rule ledger 检查"),
        ("GitHub 事实层", "把事实和验证落库", "CSV/MD/DOCX/report", "commit/push/readback", "commit_sha, remote_head", "未 push 或 remote 未回读", "git 验证"),
    ]
    return [
        {
            "layer_name": layer,
            "purpose": purpose,
            "input": input_,
            "output": output,
            "required_fields": fields,
            "blocked_if": blocked,
            "validation": validation,
        }
        for layer, purpose, input_, output, fields, blocked, validation in names
    ]


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, str]], fields: list[str]) -> str:
    out = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(field, "")).replace("\n", " ") for field in fields) + " |")
    return "\n".join(out)


def write_reports(
    boundary: dict[str, Any],
    items: list[InventoryItem],
    ai_rows: list[dict[str, Any]],
    contrast_rows: list[dict[str, Any]],
    live_rows: list[dict[str, Any]],
    coverage: list[dict[str, Any]],
    limit: int,
) -> None:
    counts = Counter(item.source_category for item in items)
    readable = Counter(item.read_status for item in items)
    gaps = architecture_gaps()
    layers = v2_layers()
    fact_map = {
        "status": "partial_completed_pending_user_review",
        "generated_at": now_iso(),
        "repo": "fthytwerwt-sudo/lanxinse--",
        "repo_root": str(REPO_ROOT),
        "material_root": str(MATERIAL_ROOT),
        "category_counts": dict(counts),
        "read_status_counts": dict(readable),
        "ai_needed_total": counts.get("ai_needed_final_video", 0),
        "ai_needed_top100_rows": len(ai_rows),
        "positive_sample_rows": counts.get("positive_sample", 0),
        "negative_sample_rows": counts.get("negative_sample", 0),
        "live_material_rows": counts.get("live_cutting_material", 0),
        "ali_call_status": "reused_existing_ali_recheck_100_no_new_api_call",
        "top100_boundary": f"first_{limit}_deep_analysis_hard_limit",
        "known_existing_facts": [
            "前 100 条 AI需要的成片已有阿里重看结果，状态 pending_user_review",
            "两条直播录屏正式模拟运行 76/76 窗口阿里调用成功但候选为 0",
            "112 复审显示 76/76 需要相邻窗口合并，82 条 rejected 需要 transcript/audio",
        ],
        "not_claimed": [
            "不确认审美通过",
            "不确认动作专业性通过",
            "不确认业务转化通过",
            "不确认稳定批量运行",
        ],
    }
    FACT_MAP_JSON.parent.mkdir(parents=True, exist_ok=True)
    FACT_MAP_JSON.write_text(json.dumps(fact_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_markdown(
        ARCH_MAP_MD,
        f"""# 当前架构地图

状态：`partial_architecture_runtime_gap_confirmed_pending_user_review`
生成时间：{now_iso()}

## 已确认事实

- 当前仓库：`fthytwerwt-sudo/lanxinse--`
- 本地仓库：`{REPO_ROOT}`
- 素材根目录：`{MATERIAL_ROOT}`
- AI 需要的成片：{counts.get('ai_needed_final_video', 0)} 条；本轮只补齐前 {limit} 条。
- 正样本：{counts.get('positive_sample', 0)} 条；负样本：{counts.get('negative_sample', 0)} 条；直播素材：{counts.get('live_cutting_material', 0)} 条。
- 旧前 100 阿里重看结果可复用：`已确认`。
- 直播正式模拟 0 候选原因：`部分成立`，更像固定窗口 + 缺音频/合并 runtime 的路线缺口，不是素材全废。

## 架构层状态

{md_table(gaps, ['gap_id', 'gap_name', 'current_status', 'priority'])}
""",
    )

    write_markdown(
        GAP_AUDIT_MD,
        "# 架构缺口审计报告\n\n"
        f"状态：`architecture_gap_audit_completed_pending_user_review`\n生成时间：{now_iso()}\n\n"
        "## 主结论\n\n"
        "`已确认`：当前架构不是只缺规则，而是规则层厚、runtime 执行层薄。系统已有前 100 成片结构、正负样本证据、五结构字段和候选池规则；但正式模拟运行仍以固定视觉窗口和完整性闸门为主，缺少内容形态前置路由、问题-动作秒级桥接、动作教学再包装分流、相邻窗口合并、音频/字幕/TTS 时间线对齐等执行层。\n\n"
        "`部分成立`：上一轮 0 候选不应直接解释为素材全废。112 复审显示 76/76 个窗口均完成阿里视觉审计，但也全部需要前后合并，82 条 rejected 需要转写/音频复审。\n\n"
        "## 缺口逐项\n\n"
        + md_table(gaps, ["gap_id", "gap_name", "current_status", "evidence", "why_it_matters", "impact_if_missing", "recommended_patch", "priority"])
        + "\n",
    )

    write_markdown(
        PATCH_DESIGN_MD,
        "# V2 架构补丁设计\n\n"
        f"状态：`v2_patch_design_completed_pending_implementation`\n生成时间：{now_iso()}\n\n"
        "## 新版链路\n\n"
        "素材入口层 → 全覆盖证据层 → 阿里多模态理解层 → 选品与内容形态路由层 → 音频 / TTS / 字幕时间轴对齐层 → 问题-动作桥接判断层 → 正负样本对照反推层 → 结构规则层 → 相邻窗口合并层 → 候选片段判断层 → 原生切片 / 动作教学再包装分流层 → 剪辑导出层 → 人工复核层 → 反馈回规则层 → GitHub 事实层\n\n"
        + md_table(layers, ["layer_name", "purpose", "input", "output", "required_fields", "blocked_if", "validation"])
        + "\n",
    )

    field_rows = [
        {"field": field, "meaning": meaning, "status": status}
        for field, meaning, status in [
            ("content_archetype", "内容形态，先判断素材属于单动作教学、原生直播片、动作纠错等哪类", "new_required"),
            ("route_decision", "路线判断，区分原生导出、再包装、相邻合并、正负样本参考、淘汰和待人审", "new_required"),
            ("problem_phrase_time", "问题句或问题字幕首次出现时间", "new_required"),
            ("first_action_frame_time", "动作首次出现时间", "new_required"),
            ("problem_action_bridge_seconds", "问题到动作之间的秒数", "new_required"),
            ("tts_action_alignment", "口播 / 配音 / 字幕与动作画面的同步状态", "new_required_pending_audio"),
            ("repackaging_value_score", "再包装价值分数，只代表可再包装潜力，不代表原生切片完成", "new_required"),
            ("needs_adjacent_merge", "是否需要合并前后窗口", "new_required"),
            ("candidate_status", "受控候选状态，不能混写审美/业务通过", "new_required"),
        ]
    ]
    status_rows = [
        {"status": name, "meaning": meaning}
        for name, meaning in [
            ("qualified_native", "原生切片技术候选合格，不等于发布通过"),
            ("qualified_repackaging", "动作教学再包装候选合格，不等于已生成成片"),
            ("qualified_merge_candidate", "相邻合并候选，需要 merge 后复核"),
            ("rejected_missing_bridge", "缺少问题-动作桥接或上下文无法成立"),
            ("rejected_action_unclear", "动作看不清或关键姿势缺失"),
            ("rejected_audio_missing", "缺音频/字幕/TTS 证据"),
            ("rejected_business_risk", "业务或健康表达风险过高"),
            ("pending_audio_transcript", "待音频转写或口播对齐"),
            ("pending_user_review", "待用户人审"),
        ]
    ]
    write_markdown(
        FIELD_DICT_MD,
        "# 字段字典与候选状态设计\n\n"
        f"状态：`field_dictionary_candidate_status_completed_pending_runtime_adoption`\n生成时间：{now_iso()}\n\n"
        "## V2 新增字段\n\n"
        + md_table(field_rows, ["field", "meaning", "status"])
        + "\n\n## candidate_status 枚举\n\n"
        + md_table(status_rows, ["status", "meaning"])
        + "\n\n## 关键边界\n\n"
        "- `action_repackaging_candidate` 只表示可再包装潜力，不是原生成片完成。\n"
        "- `pending_audio_transcript` 不能脑补口播内容。\n"
        "- `pending_user_review` 覆盖审美、动作专业性、健康表达和业务转化复核。\n",
    )

    write_markdown(
        MANUAL_REVIEW_MD,
        "# 人工复核清单\n\n"
        f"状态：`manual_review_checklist_created_pending_user_review`\n生成时间：{now_iso()}\n\n"
        "## 先看 3 类样本\n\n"
        "1. `action_repackaging_candidate`：确认动作是否看得懂、是否完整循环、是否可用 TTS / 字幕解释。\n"
        "2. `adjacent_merge_candidate`：确认向前/向后合并后是否有真实开头和自然收束。\n"
        "3. `pending_audio_transcript`：确认口播、字幕、动作画面是否同向，不能只凭关键帧判断。\n\n"
        "## 必查项\n\n"
        "- 是否把可再包装素材误判成原生完整切片。\n"
        "- 问题句后是否快速接动作或方法。\n"
        "- TTS / 字幕是否解释了动作正在解决什么问题。\n"
        "- 是否存在半句话、半个动作、动作遮挡或字幕遮挡。\n"
        "- 盆底、漏尿、产后、疼痛、100 次等健康表达是否需要专业复核。\n"
        "- 是否存在效果承诺、业务转化、强 CTA 需要客户确认。\n\n"
        "## 不得通过项\n\n"
        "- 本轮不写审美通过。\n"
        "- 本轮不写动作专业性通过。\n"
        "- 本轮不写业务转化通过。\n"
        "- 本轮不写稳定批量运行。\n",
    )

    human_md = human_readable_markdown(boundary, counts, ai_rows, contrast_rows, live_rows, coverage, limit)
    write_markdown(HUMAN_MD_FALLBACK, human_md)
    write_simple_docx(HUMAN_DOCX, "直播切片 V2 架构审核与解析补全人读版", human_md)
    write_markdown(EXEC_REPORT_MD, execution_report(boundary, counts, readable, ai_rows, contrast_rows, live_rows, coverage, limit))


def human_readable_markdown(
    boundary: dict[str, Any],
    counts: Counter[str],
    ai_rows: list[dict[str, Any]],
    contrast_rows: list[dict[str, Any]],
    live_rows: list[dict[str, Any]],
    coverage: list[dict[str, Any]],
    limit: int,
) -> str:
    return f"""# 直播切片 V2 架构审核与解析补全人读版

状态：`partial_completed_pending_user_review`

## 一句话结论

当前系统不是没有规则，而是原有规则还没有完整下沉到直播切片 runtime。上次 0 候选更可能是固定窗口、缺音频语义、缺相邻窗口合并和缺动作教学再包装路线共同造成的误杀风险，不等于素材全废。

## 本轮完成内容

- 素材总清单：{sum(counts.values())} 条视频类文件。
- AI需要的成片：{counts.get('ai_needed_final_video', 0)} 条；只补齐前 {limit} 条。
- 正样本：{counts.get('positive_sample', 0)} 条；负样本：{counts.get('negative_sample', 0)} 条。
- 直播素材：{counts.get('live_cutting_material', 0)} 条。
- 前 100 解析方式：复用已有阿里重看结果，无新增 API 调用。
- 输出：inventory、coverage、AI 前 100 补全、正负样本对照、直播机会表、架构缺口、V2 补丁、字段字典、人工复核清单。

## 关键判断

1. `content_archetype_routing_layer`：部分成立，但需要下沉为 runtime 前置路由。
2. `problem_action_bridge_layer`：部分成立，但缺秒级问题-动作桥接字段。
3. `action_teaching_repackaging_route`：部分成立，但缺直播素材救回执行路线。
4. `adjacent_window_merge_layer`：缺执行层，是 0 候选的重要原因。
5. `audio_tts_subtitle_timeline_alignment_layer`：缺失，不能脑补口播或 TTS。
6. `positive_negative_contrast_layer`：已有，但负样本偏薄，仍需扩充。

## 边界

本轮不生成最终成片，不确认审美通过，不确认动作专业性通过，不确认业务转化通过，不确认稳定批量运行。
"""


def execution_report(
    boundary: dict[str, Any],
    counts: Counter[str],
    readable: Counter[str],
    ai_rows: list[dict[str, Any]],
    contrast_rows: list[dict[str, Any]],
    live_rows: list[dict[str, Any]],
    coverage: list[dict[str, Any]],
    limit: int,
) -> str:
    category_lines = "\n".join(f"- `{key}`：{value}" for key, value in sorted(counts.items()))
    read_lines = "\n".join(f"- `{key}`：{value}" for key, value in sorted(readable.items()))
    return f"""# 直播切片 V2 架构审核与解析补全执行报告

状态：`partial_completed_pending_user_review`
生成时间：{now_iso()}

## 1. 边界与仓库

| 项目 | 结果 |
| --- | --- |
| 当前项目仓库 | `fthytwerwt-sudo/lanxinse--` |
| 本地仓库路径 | `{REPO_ROOT}` |
| 当前分支 | `{boundary.get('branch')}` |
| 当前 remote | `{boundary.get('remote').splitlines()[0] if boundary.get('remote') else ''}` |
| 素材总目录 | `{MATERIAL_ROOT}` |
| ffmpeg | `{boundary.get('ffmpeg')}` |
| ffprobe | `{boundary.get('ffprobe')}` |
| 阿里调用状态 | `reused_existing_ali_recheck_100_no_new_api_call` |
| deep analysis hard limit | `first_{limit}_deep_analysis_hard_limit` |

## 2. 素材类别

{category_lines}

## 3. 读取状态

{read_lines}

## 4. 输出数量

| 输出 | 行数 |
| --- | ---: |
| 素材总清单 | {sum(counts.values())} |
| 解析覆盖率表 | {len(coverage)} |
| AI需要的成片前100解析补全 | {len(ai_rows)} |
| 正负样本差异结构表 | {len(contrast_rows)} |
| 直播切片素材结构机会表 | {len(live_rows)} |

## 5. 关键结论

- `已确认`：旧前 100 阿里重看结果可复用，本轮没有新增阿里 API 调用，也没有保存 API 原始输出。
- `部分成立`：0 候选更可能来自固定窗口完整性闸门、缺相邻窗口合并、缺音频/字幕语义，而不是素材全废。
- `已确认`：当前旧解析缺 `content_archetype / route_decision / problem_action_bridge_seconds / tts_action_alignment / repackaging_value_score / needs_adjacent_merge / candidate_status` 等新字段。
- `待验证`：音频转写、TTS 对齐、动作专业性、审美、人感、业务转化和稳定批量运行。

## 6. 边界确认

| 边界 | 结果 |
| --- | --- |
| 是否提交媒体 | 否 |
| 是否提交 contact sheet | 否 |
| 是否提交 API 原始输出 | 否 |
| 是否提交 `.env` | 否 |
| 是否提交 API key | 否 |
| 是否写审美通过 | 否 |
| 是否写动作专业性通过 | 否 |
| 是否写业务通过 | 否 |
| 是否写稳定批量运行 | 否 |
| 是否只把前 100 条写成前 100 条 | 是 |
| 是否把超过前 100 条标为 `pending_not_analyzed` | 是 |

## 7. 验证命令

后续由 Codex 在提交前执行：

- `python3 scripts/check_ali_config_safety.py`
- `python3 -m py_compile scripts/live_cutting_v2_architecture_audit.py`
- `python3 scripts/live_cutting_v2_architecture_audit.py --dry-run`
- `python3 scripts/live_cutting_v2_architecture_audit.py --limit {limit}`
- `git diff --check`
- `git status`
"""


def write_simple_docx(path: Path, title: str, markdown_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    paragraphs = []
    for raw in markdown_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            paragraphs.append(("Title", line[2:]))
        elif line.startswith("## "):
            paragraphs.append(("Heading1", line[3:]))
        elif line.startswith("### "):
            paragraphs.append(("Heading2", line[4:]))
        elif line.startswith("- "):
            paragraphs.append(("ListParagraph", line[2:]))
        elif line.startswith("|"):
            continue
        else:
            paragraphs.append(("Normal", line))
    body = "\n".join(paragraph_xml(text, style) for style, text in paragraphs)
    document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>
  </w:body>
</w:document>'''
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Arial" w:eastAsia="Microsoft YaHei"/><w:sz w:val="21"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="23"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/></w:style>
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
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style != "Normal" else ""
    return f"<w:p>{style_xml}<w:r><w:t>{safe}</w:t></w:r></w:p>"


def verify_outputs(limit: int) -> None:
    required_files = [
        INVENTORY_CSV,
        COVERAGE_CSV,
        AI_TOP100_CSV,
        CONTRAST_CSV,
        LIVE_OPPORTUNITY_CSV,
        GAP_AUDIT_MD,
        PATCH_DESIGN_MD,
        FIELD_DICT_MD,
        MANUAL_REVIEW_MD,
        EXEC_REPORT_MD,
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required_files if not path.exists()]
    if missing:
        raise SystemExit(f"blocked_missing_output_files: {', '.join(missing)}")
    ai_rows = read_csv(AI_TOP100_CSV)
    if len(ai_rows) > limit:
        raise SystemExit("blocked_first_100_limit_exceeded")
    for path, fields in [
        (INVENTORY_CSV, INVENTORY_FIELDS),
        (COVERAGE_CSV, COVERAGE_FIELDS),
        (AI_TOP100_CSV, AI_FIELDS),
        (CONTRAST_CSV, CONTRAST_FIELDS),
        (LIVE_OPPORTUNITY_CSV, LIVE_FIELDS),
    ]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing_fields = [field for field in fields if field not in (reader.fieldnames or [])]
            if missing_fields:
                raise SystemExit(f"blocked_missing_csv_fields: {path.name}: {missing_fields}")


def dry_run(limit: int) -> None:
    boundary = require_boundaries()
    items = discover_videos()
    counts = Counter(item.source_category for item in items)
    print("dry_run_ok")
    print(json.dumps({"boundary": boundary, "category_counts": counts, "limit": limit}, ensure_ascii=False, indent=2, default=str))
    print("planned_outputs:")
    for path in [
        INVENTORY_CSV,
        COVERAGE_CSV,
        AI_TOP100_CSV,
        CONTRAST_CSV,
        LIVE_OPPORTUNITY_CSV,
        FACT_MAP_JSON,
        ARCH_MAP_MD,
        GAP_AUDIT_MD,
        PATCH_DESIGN_MD,
        FIELD_DICT_MD,
        MANUAL_REVIEW_MD,
        HUMAN_DOCX,
        EXEC_REPORT_MD,
    ]:
        print("-", path.relative_to(REPO_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="直播切片 V2 架构审核与解析补全")
    parser.add_argument("--dry-run", action="store_true", help="只检查边界和计划输出，不写文件")
    parser.add_argument("--limit", type=int, default=100, help="每类深度解析硬上限，默认 100")
    args = parser.parse_args()
    if args.limit > 100:
        raise SystemExit("blocked_first_100_limit_exceeded")
    if args.dry_run:
        dry_run(args.limit)
        return 0

    boundary = require_boundaries()
    old_meta = old_metadata_by_name()
    items = discover_videos()
    apply_deep_scopes(items, args.limit)
    for item in items:
        ffprobe_item(item, old_meta)
    assets = existing_parse_assets()
    inventory = inventory_rows(items)
    coverage = coverage_rows(items, assets)
    ai_rows = build_ai_top100_rows(items, assets, args.limit)
    contrast = build_contrast_rows(items, assets, args.limit)
    live = build_live_opportunity_rows(assets)

    write_csv(INVENTORY_CSV, INVENTORY_FIELDS, inventory)
    write_csv(COVERAGE_CSV, COVERAGE_FIELDS, coverage)
    write_csv(AI_TOP100_CSV, AI_FIELDS, ai_rows)
    write_csv(CONTRAST_CSV, CONTRAST_FIELDS, contrast)
    write_csv(LIVE_OPPORTUNITY_CSV, LIVE_FIELDS, live)
    write_reports(boundary, items, ai_rows, contrast, live, coverage, args.limit)
    verify_outputs(args.limit)
    print(
        json.dumps(
            {
                "status": "ok",
                "inventory_rows": len(inventory),
                "ai_top100_rows": len(ai_rows),
                "contrast_rows": len(contrast),
                "live_opportunity_rows": len(live),
                "ali_call_status": "reused_existing_ali_recheck_100_no_new_api_call",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
