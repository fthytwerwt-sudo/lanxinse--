#!/usr/bin/env python3
"""Audit external course action data and build conservative action mapping artifacts.

The source directory is read-only input. This script writes only derived CSV/MD
artifacts into the repository and intentionally avoids copying raw course text,
media, cache files, or API outputs.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = Path("/Volumes/WD_BLACK/AI解析")

AUDIT_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis" / "10_course_action_data_audit"
KB_DIR = REPO_ROOT / "项目事实_project_facts" / "动作知识库_action_knowledge_base"
LOG_DIR = REPO_ROOT / "执行日志_codex_log"

INVENTORY_PATH = AUDIT_DIR / "课程动作资料文件清单_course_action_source_inventory.csv"
USEFULNESS_PATH = AUDIT_DIR / "课程动作资料可用性分级_course_action_source_usefulness.csv"
ACTION_MAPPING_PATH = KB_DIR / "01_动作问题映射表_action_problem_mapping.csv"
ALIAS_PATH = KB_DIR / "02_动作别名归一表_action_alias_normalization.csv"
TAXONOMY_PATH = KB_DIR / "03_问题分类表_problem_taxonomy.csv"
BRIDGE_PATH = KB_DIR / "04_动作剪辑结构桥接表_action_clip_structure_bridge.csv"
RULES_PATH = KB_DIR / "05_动作应用规则说明_action_application_rules.md"
SCREENING_PATH = KB_DIR / "06_动作知识库接入直播筛选说明_action_knowledge_to_live_screening.md"
REPORT_PATH = LOG_DIR / "117_课程动作资料审计与映射执行报告_course_action_data_audit_report.md"

TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".jsonl",
    ".md",
    ".txt",
    ".srt",
    ".vtt",
    ".yaml",
    ".yml",
}
MEDIA_SUFFIXES = {
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".avi",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".wav",
    ".mp3",
    ".m4a",
}
ARCHIVE_SUFFIXES = {".zip", ".tar", ".gz", ".tgz", ".7z", ".rar"}

NOISE_EXACT_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "_cache",
    "_logs",
    "_state",
    "_tools",
    "site-packages",
    "frames_preview",
}
NOISE_PART_PREFIXES = (".venv", "venv", "vision_venv")
NOISE_PART_SUFFIXES = (".dist-info", ".egg-info")

SENSITIVE_TERM_NOTE = "源内含更细分敏感成人课程词，本知识库只保留高层词族，不展开操作细节。"


@dataclass(frozen=True)
class FileClass:
    file_kind: str
    usefulness_grade: str
    usefulness_type: str
    read_status: str
    recommended_usage: str
    notes: str


def ensure_dirs() -> None:
    for directory in (AUDIT_DIR, KB_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def rel_to_source(path: Path) -> str:
    return path.relative_to(SOURCE_ROOT).as_posix()


def clean_field(value: str) -> str:
    return value.lstrip("\ufeff").strip()


def read_csv_dicts(path: Path, limit: int | None = None) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader):
            if limit is not None and index >= limit:
                break
            yield {clean_field(k or ""): (v or "").strip() for k, v in row.items()}


def read_jsonl(path: Path, limit: int | None = None) -> Iterable[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            if limit is not None and index >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                yield item


def is_mirror_duplicate(parts: tuple[str, ...]) -> bool:
    return any(part.endswith(" 2") for part in parts)


def is_mojibake_alias(parts: tuple[str, ...]) -> bool:
    return any("閫" in part or "绋胯В" in part or part.startswith("璇剧") for part in parts)


def is_noise_path(parts: tuple[str, ...]) -> bool:
    for part in parts:
        lower = part.lower()
        if lower in NOISE_EXACT_PARTS:
            return True
        if lower.startswith(NOISE_PART_PREFIXES):
            return True
        if lower.endswith(NOISE_PART_SUFFIXES):
            return True
    return False


def normalized_duplicate_key(path: Path) -> str:
    parts = []
    for part in path.relative_to(SOURCE_ROOT).parts:
        if part.endswith(" 2"):
            parts.append(part[:-2])
        else:
            parts.append(part)
    return "/".join(parts)


def high_value_kind(path: Path) -> str | None:
    rel = rel_to_source(path)
    name = path.name
    if "sentence_action_shards" in rel or name in {
        "06_讲师动作时间轴_presenter_action_timeline.csv",
        "09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv",
        "07_动作标签库_action_label_library.md",
        "12_数字人动作触发规则_avatar_action_trigger_rules.csv",
    }:
        return "action_core"
    if name in {
        "presenter_actions.jsonl",
        "tri_alignment.jsonl",
        "neural_avatar_bridge_fields.jsonl",
        "prosody_pacing.jsonl",
        "transcript_timeline.jsonl",
    }:
        return "action_core_jsonl"
    if name in {
        "08_关键词术语表_terms_glossary.csv",
        "09_问题_答案_异议_回应_QA_objection_response_bank.csv",
        "knowledge_points.csv",
        "live_bridge_fields.csv",
        "data/live_project_bridge_fields.csv",
    } or "live_project_bridge_fields" in name:
        return "course_text_context"
    if name.startswith(("00_", "11_", "12_", "13_", "14_", "15_", "16_", "17_", "18_")) and path.suffix.lower() in TEXT_SUFFIXES:
        return "support_report_or_manifest"
    if path.suffix.lower() in TEXT_SUFFIXES:
        return "readable_text_reference"
    return None


def classify_file(path: Path) -> FileClass:
    rel_parts = path.relative_to(SOURCE_ROOT).parts
    suffix = path.suffix.lower()
    kind = high_value_kind(path)

    if path.name.startswith("._"):
        return FileClass(
            "appledouble_sidecar",
            "D",
            "系统旁路文件",
            "skipped_appledouble",
            "不进入抽取；只在清单保留。",
            "AppleDouble 文件，不是课程动作资料。",
        )
    if is_mirror_duplicate(rel_parts) or is_mojibake_alias(rel_parts):
        return FileClass(
            kind or "duplicate_or_encoding_alias",
            "D",
            "镜像副本/编码别名",
            "skipped_duplicate",
            "只用于确认来源完整性，不参与知识库抽取。",
            "路径显示为同名副本或编码别名；优先使用主路径。",
        )
    if is_noise_path(rel_parts):
        return FileClass(
            "tool_cache_or_runtime_dependency",
            "D",
            "工具缓存/运行环境",
            "skipped_noise",
            "不进入课程资料抽取。",
            "属于 venv/cache/log/state/tool 目录。",
        )
    if suffix in ARCHIVE_SUFFIXES:
        return FileClass(
            "archive_bundle",
            "C",
            "封装包引用",
            "skipped_archive",
            "只用于确认封装存在；不直接抽取。",
            "压缩包可能包含重复资料，避免双计。",
        )
    if suffix in MEDIA_SUFFIXES:
        return FileClass(
            "media_reference",
            "C",
            "媒体/图片引用",
            "skipped_media",
            "只保留路径和大小；本轮不复制媒体、不做视觉判定。",
            "媒体文件需要另行视觉/人工复核。",
        )
    if kind == "action_core":
        return FileClass(
            "action_core",
            "A",
            "动作核心表",
            "read_for_mapping",
            "用于动作标签、时间轴、逐字稿-动作-课件桥接。",
            "主事实源之一；仍保留 review_flag/confidence 闸门。",
        )
    if kind == "action_core_jsonl":
        return FileClass(
            "action_core_jsonl",
            "A",
            "动作核心 JSONL",
            "read_for_mapping",
            "用于逐句动作、数字人桥接和节奏统计。",
            "只提取字段/计数，不搬运原文。",
        )
    if kind == "course_text_context":
        return FileClass(
            "course_text_context",
            "B",
            "课程文本上下文",
            "read_for_context",
            "用于关键词、问题、风险和直播桥接口径。",
            "文本来源需人工复核；敏感操作细节不写入知识库。",
        )
    if kind == "support_report_or_manifest":
        return FileClass(
            "support_report_or_manifest",
            "C",
            "执行/质量/复核说明",
            "metadata_only",
            "用于理解来源和风险，不作为动作事实源。",
            "只抽取状态边界，不搬运正文。",
        )
    if suffix in TEXT_SUFFIXES:
        return FileClass(
            "readable_text_reference",
            "C",
            "可读文本参考",
            "metadata_only",
            "必要时人工追溯，不参与自动映射。",
            "未命中动作/问题核心字段。",
        )
    return FileClass(
        "other_binary_or_unknown",
        "D",
        "非文本/未知",
        "skipped_unknown",
        "不进入抽取。",
        "无法作为本轮动作知识库输入。",
    )


def build_inventory() -> list[dict[str, str]]:
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(f"source directory not found: {SOURCE_ROOT}")

    files = sorted((p for p in SOURCE_ROOT.rglob("*") if p.is_file()), key=lambda p: rel_to_source(p))
    primary_keys = {
        normalized_duplicate_key(path)
        for path in files
        if not is_mirror_duplicate(path.relative_to(SOURCE_ROOT).parts)
        and not is_mojibake_alias(path.relative_to(SOURCE_ROOT).parts)
    }

    rows: list[dict[str, str]] = []
    for index, path in enumerate(files, start=1):
        rel = rel_to_source(path)
        stat = path.stat()
        klass = classify_file(path)
        duplicate_key = normalized_duplicate_key(path)
        if klass.read_status == "skipped_duplicate" and duplicate_key in primary_keys:
            duplicate_status = "mirror_duplicate_primary_exists"
        elif klass.read_status == "skipped_duplicate":
            duplicate_status = "duplicate_or_encoding_alias_unverified"
        else:
            duplicate_status = "primary_or_unique"
        rows.append(
            {
                "source_file_id": f"SRC{index:05d}",
                "relative_path": rel,
                "absolute_path": str(path),
                "top_level": path.relative_to(SOURCE_ROOT).parts[0],
                "file_name": path.name,
                "extension": path.suffix.lower() or "[none]",
                "size_bytes": str(stat.st_size),
                "modified_time": dt.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "file_kind": klass.file_kind,
                "usefulness_grade": klass.usefulness_grade,
                "usefulness_type": klass.usefulness_type,
                "read_status": klass.read_status,
                "duplicate_key": duplicate_key,
                "duplicate_status": duplicate_status,
                "recommended_usage": klass.recommended_usage,
                "notes": klass.notes,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def inventory_maps(rows: list[dict[str, str]]) -> tuple[dict[str, str], dict[str, list[dict[str, str]]]]:
    rel_to_id = {row["relative_path"]: row["source_file_id"] for row in rows}
    by_name: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_name[row["file_name"]].append(row)
    return rel_to_id, by_name


def source_ids(rows: list[dict[str, str]], *patterns: str, grades: tuple[str, ...] = ("A", "B")) -> str:
    ids = []
    for row in rows:
        if row["usefulness_grade"] not in grades:
            continue
        rel = row["relative_path"]
        if any(pattern in rel for pattern in patterns):
            ids.append(row["source_file_id"])
    return ";".join(sorted(set(ids)))


def primary_paths(rows: list[dict[str, str]], *patterns: str, grades: tuple[str, ...] = ("A", "B")) -> list[Path]:
    paths = []
    for row in rows:
        if row["usefulness_grade"] not in grades:
            continue
        rel = row["relative_path"]
        if any(pattern in rel for pattern in patterns):
            paths.append(SOURCE_ROOT / rel)
    return sorted(paths, key=lambda p: rel_to_source(p))


def collect_source_stats(rows: list[dict[str, str]]) -> dict[str, object]:
    stats: dict[str, object] = {}
    stats["total_files"] = len(rows)
    stats["grade_counts"] = Counter(row["usefulness_grade"] for row in rows)
    stats["kind_counts"] = Counter(row["file_kind"] for row in rows)
    stats["read_status_counts"] = Counter(row["read_status"] for row in rows)
    stats["top_level_counts"] = Counter(row["top_level"] for row in rows)

    action_labels: Counter[str] = Counter()
    action_confidence: Counter[str] = Counter()
    review_flags: Counter[str] = Counter()
    prosody_labels: Counter[str] = Counter()
    bridge_intents: Counter[str] = Counter()
    bridge_risks: Counter[str] = Counter()
    term_counts: Counter[str] = Counter()
    sensitive_keyword_hits: Counter[str] = Counter()
    csv_row_counts: dict[str, int] = {}
    jsonl_row_counts: dict[str, int] = {}

    for path in primary_paths(rows, "06_讲师动作时间轴_presenter_action_timeline.csv"):
        count = 0
        for item in read_csv_dicts(path):
            count += 1
            action_labels[item.get("action_label", "")] += 1
            action_confidence[item.get("confidence", "")] += 1
            review_flags[item.get("review_flag", "")] += 1
        csv_row_counts[rel_to_source(path)] = count

    for path in primary_paths(rows, "09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv"):
        count = 0
        for item in read_csv_dicts(path):
            count += 1
            action_labels[item.get("presenter_action", "")] += 1
            prosody_labels[item.get("prosody_label", "")] += 1
            action_confidence[item.get("confidence", "")] += 1
            review_flags[item.get("review_flag", "")] += 1
        csv_row_counts[rel_to_source(path)] = count

    for path in primary_paths(rows, "12_数字人动作触发规则_avatar_action_trigger_rules.csv"):
        count = 0
        for item in read_csv_dicts(path):
            count += 1
            action_labels[item.get("avatar_action_label", "")] += 1
            action_confidence[item.get("confidence", "")] += 1
            review_flags[item.get("review_flag", "")] += 1
        csv_row_counts[rel_to_source(path)] = count

    for path in primary_paths(rows, "live_project_bridge_fields.csv"):
        count = 0
        for item in read_csv_dicts(path):
            count += 1
            bridge_intents[item.get("content_intent", "")] += 1
            bridge_risks[item.get("risk_level", "")] += 1
            if item.get("human_review_needed"):
                review_flags[f"human_review_needed={item.get('human_review_needed')}"] += 1
        csv_row_counts[rel_to_source(path)] = count

    for path in primary_paths(rows, "08_关键词术语表_terms_glossary.csv"):
        count = 0
        for item in read_csv_dicts(path):
            count += 1
            term = item.get("term", "")
            if term:
                term_counts[term] += 1
            for family, pattern in COURSE_KEYWORD_FAMILIES.items():
                if any(re.search(token, term) for token in pattern):
                    sensitive_keyword_hits[family] += 1
        csv_row_counts[rel_to_source(path)] = count

    for path in primary_paths(rows, "09_问题_答案_异议_回应_QA_objection_response_bank.csv"):
        count = 0
        for item in read_csv_dicts(path):
            count += 1
            review_flags[item.get("review_flag", "")] += 1
        csv_row_counts[rel_to_source(path)] = count

    for path in primary_paths(rows, "knowledge_points.csv"):
        count = 0
        for item in read_csv_dicts(path):
            count += 1
            text = f"{item.get('knowledge_point', '')} {item.get('source_quote', '')}"
            for family, pattern in COURSE_KEYWORD_FAMILIES.items():
                if any(re.search(token, text) for token in pattern):
                    sensitive_keyword_hits[family] += 1
        csv_row_counts[rel_to_source(path)] = count

    for path in primary_paths(rows, "sentence_action_shards", grades=("A",)):
        count = 0
        for item in read_jsonl(path):
            count += 1
            action_labels[str(item.get("final_action_label", ""))] += 1
            action_labels[str(item.get("text_action_label", ""))] += 1
            action_confidence[str(item.get("action_confidence", ""))] += 1
            review_flags[str(item.get("review_flag", ""))] += 1
            prosody_labels[str(item.get("avatar_speech_type", ""))] += 1
        jsonl_row_counts[rel_to_source(path)] = count

    stats["action_labels"] = action_labels
    stats["action_confidence"] = action_confidence
    stats["review_flags"] = review_flags
    stats["prosody_labels"] = prosody_labels
    stats["bridge_intents"] = bridge_intents
    stats["bridge_risks"] = bridge_risks
    stats["term_counts"] = term_counts
    stats["sensitive_keyword_hits"] = sensitive_keyword_hits
    stats["csv_row_counts"] = csv_row_counts
    stats["jsonl_row_counts"] = jsonl_row_counts
    return stats


COURSE_KEYWORD_FAMILIES: dict[str, tuple[str, ...]] = {
    "pelvic_floor_training": (r"盆底", r"盘底", r"收紧", r"放松", r"私密训练", r"私密瑜伽"),
    "breathing_coordination": (r"呼吸", r"气息"),
    "body_position_technique_sensitive": (r"体位", r"姿势", r"侧卧", r"女上位"),
    "touch_or_tool_method_sensitive": (r"按摩", r"精油", r"工具", r"小球"),
    "relationship_communication": (r"亲密关系", r"伴侣", r"沟通", r"情感", r"婚姻"),
    "course_offer_or_business": (r"课程", r"助理", r"报名", r"专场"),
}


def build_action_mapping(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    ids_label = source_ids(rows, "07_动作标签库_action_label_library.md")
    ids_trigger = source_ids(rows, "12_数字人动作触发规则_avatar_action_trigger_rules.csv")
    ids_timeline = source_ids(rows, "06_讲师动作时间轴_presenter_action_timeline.csv", "sentence_action_shards")
    ids_alignment = source_ids(rows, "09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv")
    ids_terms = source_ids(rows, "08_关键词术语表_terms_glossary.csv", "knowledge_points.csv")
    ids_qa = source_ids(rows, "09_问题_答案_异议_回应_QA_objection_response_bank.csv", "live_project_bridge_fields.csv")

    return [
        {
            "normalized_action_id": "presenter_neutral_idle",
            "action_domain": "presenter_avatar_action",
            "normalized_action_name_cn": "自然讲解/默认静止",
            "confirmed_source_basis": "动作标签库与触发规则存在该标签；多处桥接建议仍要求人工复核。",
            "alias_examples": "neutral_idle; 自然静止",
            "target_problem_primary": "presentation_delivery",
            "target_problem_secondary": "course_knowledge_explain",
            "audience_or_scene": "课程讲解、无明确动作词的口播段",
            "primary_key_point": "作为数字人默认动作或口播占位，不代表原视频动作已确认。",
            "wrong_pattern_to_detect": "把默认静止误当作可见真人动作证据。",
            "speech_keyword_family": "normal_explain",
            "visual_evidence_required": "需确认人物可见、表情/视线与口播不冲突。",
            "current_visual_evidence_status": "low_confidence_pending_visual_review",
            "risk_review_items": "visual_review_required",
            "recommended_structure": "痛点问题 + 原因解释 + 方法交付",
            "candidate_use_status": "bridge_only_pending_human_review",
            "source_file_ids": ";".join(filter(None, [ids_label, ids_trigger, ids_alignment])),
            "notes": "可辅助直播资料字段，不可直接作为自动播发动作。",
        },
        {
            "normalized_action_id": "presenter_open_explain",
            "action_domain": "presenter_avatar_action",
            "normalized_action_name_cn": "张手解释/开放讲解",
            "confirmed_source_basis": "动作标签库列出 hand_open_explain；触发规则把 question_prompt 映射到该动作但 confidence=low。",
            "alias_examples": "hand_open_explain; 张手解释",
            "target_problem_primary": "presentation_delivery",
            "target_problem_secondary": "question_answer_bridge",
            "audience_or_scene": "问题提示、解释、承接观众疑问",
            "primary_key_point": "用于提示“正在解释/引导”，不是已确认的原片动作。",
            "wrong_pattern_to_detect": "只有问题句，没有原因链或方法边界。",
            "speech_keyword_family": "question_prompt; normal_explain",
            "visual_evidence_required": "手部打开动作、画面无遮挡、口播同题。",
            "current_visual_evidence_status": "label_defined_but_visual_unconfirmed",
            "risk_review_items": "visual_review_required; customer_review_if_used_in_live_script",
            "recommended_structure": "问题问答 + 原因解释 + 方法边界",
            "candidate_use_status": "bridge_only_pending_human_review",
            "source_file_ids": ";".join(filter(None, [ids_label, ids_trigger])),
            "notes": "仅可作为候选动作意图。",
        },
        {
            "normalized_action_id": "presenter_screen_point_or_highlight",
            "action_domain": "presenter_avatar_action",
            "normalized_action_name_cn": "指向课件/屏幕重点",
            "confirmed_source_basis": "动作标签库含 hand_point_screen、highlight_focus、eye_to_slide、mouse_pointer_move。",
            "alias_examples": "hand_point_screen; highlight_focus; eye_to_slide; mouse_pointer_move",
            "target_problem_primary": "courseware_attention",
            "target_problem_secondary": "visual_focus_bridge",
            "audience_or_scene": "课件图示、重点字幕、步骤提示",
            "primary_key_point": "必须确认被指向的课件/字幕与口播同题。",
            "wrong_pattern_to_detect": "OCR 不可用或课件不可见时仍写成重点已确认。",
            "speech_keyword_family": "重点/看这里/这个位置/这一点",
            "visual_evidence_required": "课件文字/OCR、指向动作、视线或鼠标轨迹至少两项同向。",
            "current_visual_evidence_status": "ocr_or_visual_pending_review",
            "risk_review_items": "visual_review_required; ocr_review_required",
            "recommended_structure": "工具/动作演示 + 发力口令 + 低压跟练收束",
            "candidate_use_status": "screening_helper_pending_visual_review",
            "source_file_ids": ";".join(filter(None, [ids_label, ids_alignment])),
            "notes": "用于帮助剪辑师找课件证据，不代表动作专业性通过。",
        },
        {
            "normalized_action_id": "presenter_step_count_or_page_turn",
            "action_domain": "presenter_avatar_action",
            "normalized_action_name_cn": "步骤数数/翻页承接",
            "confirmed_source_basis": "动作标签库含 hand_counting 与 page_turn。",
            "alias_examples": "hand_counting; page_turn",
            "target_problem_primary": "course_step_explain",
            "target_problem_secondary": "method_sequence",
            "audience_or_scene": "多步骤讲解、组合动作、阶段切换",
            "primary_key_point": "只能说明讲解结构可能分步，不能说明步骤正确。",
            "wrong_pattern_to_detect": "多个动作目标混乱，或缺动作之间承接。",
            "speech_keyword_family": "第一/第二/第三/接下来/然后",
            "visual_evidence_required": "步骤字幕、翻页或手势数数与口播顺序一致。",
            "current_visual_evidence_status": "label_defined_but_visual_unconfirmed",
            "risk_review_items": "visual_review_required; professional_review_if_exercise_method",
            "recommended_structure": "多动作组合 + 同一主题推进 + 轻跟练收束",
            "candidate_use_status": "screening_helper_pending_human_review",
            "source_file_ids": ids_label,
            "notes": "适合做组合段排序提示。",
        },
        {
            "normalized_action_id": "presenter_emphasis_warning_pause",
            "action_domain": "presenter_avatar_action",
            "normalized_action_name_cn": "严肃强调/风险提醒/停顿",
            "confirmed_source_basis": "动作标签库含 serious_emphasis、pause_thinking；触发规则把 warning_reminder 映射为 serious_emphasis 但 confidence=low。",
            "alias_examples": "serious_emphasis; pause_thinking; warning_reminder",
            "target_problem_primary": "risk_boundary",
            "target_problem_secondary": "objection_response",
            "audience_or_scene": "注意事项、禁忌、边界提醒、异议回应",
            "primary_key_point": "风险提醒可以延长保留，但不能扩大成专业结论。",
            "wrong_pattern_to_detect": "只保留承诺句，删掉注意事项/适用边界。",
            "speech_keyword_family": "注意/不要/如果/不适合/需要复核",
            "visual_evidence_required": "表情、语气停顿、字幕或注意事项同向。",
            "current_visual_evidence_status": "text_rule_only_pending_audio_visual_review",
            "risk_review_items": "professional_review_required; compliance_review_required",
            "recommended_structure": "结果前置 + 操作过程 + 注意事项/风险边界",
            "candidate_use_status": "risk_gate_required_before_live_use",
            "source_file_ids": ";".join(filter(None, [ids_label, ids_trigger, ids_qa])),
            "notes": "适合做剪辑保边界提示。",
        },
        {
            "normalized_action_id": "course_pelvic_floor_training_reference",
            "action_domain": "course_text_action_keyword",
            "normalized_action_name_cn": "盆底/私密训练关键词族",
            "confirmed_source_basis": "术语表、知识点与逐字稿桥接中出现训练相关词族；视觉动作完整性未确认。",
            "alias_examples": "盆底肌; 私密训练; 私密瑜伽; 收紧/放松",
            "target_problem_primary": "pelvic_floor_training",
            "target_problem_secondary": "health_or_body_training",
            "audience_or_scene": "训练问答、痛点解释、低压跟练候选",
            "primary_key_point": "只作为文本命中和候选筛选；动作安全性、适用人群与效果需专业复核。",
            "wrong_pattern_to_detect": "口播提到训练，但画面没有完整动作循环或关键部位被遮挡。",
            "speech_keyword_family": "盆底/训练/收紧/放松/发力/呼吸",
            "visual_evidence_required": "完整动作循环、发力方向、呼吸/次数口令、无遮挡关键部位。",
            "current_visual_evidence_status": "text_keyword_confirmed_visual_pending_review",
            "risk_review_items": "professional_review_required; health_claim_review_required",
            "recommended_structure": "痛点/人群点名 + 单动作完整循环 + 坚持建议",
            "candidate_use_status": "screening_candidate_pending_professional_review",
            "source_file_ids": ids_terms,
            "notes": "不得写健康效果已确认。",
        },
        {
            "normalized_action_id": "course_breathing_coordination_reference",
            "action_domain": "course_text_action_keyword",
            "normalized_action_name_cn": "呼吸配合关键词族",
            "confirmed_source_basis": "术语表/知识点中存在呼吸配合类表达；动作同步未确认。",
            "alias_examples": "呼吸; 气息; 配合呼吸",
            "target_problem_primary": "breathing_coordination",
            "target_problem_secondary": "method_boundary",
            "audience_or_scene": "动作口令、跟练提示、注意事项",
            "primary_key_point": "呼吸只可作为口令辅助字段，不可替代动作证据。",
            "wrong_pattern_to_detect": "只有呼吸口令，没有动作起势/回位。",
            "speech_keyword_family": "呼吸/吸气/呼气/配合",
            "visual_evidence_required": "动作节奏与口令同步，至少保留一次完整循环。",
            "current_visual_evidence_status": "text_keyword_confirmed_visual_pending_review",
            "risk_review_items": "professional_review_required",
            "recommended_structure": "工具/动作演示 + 发力口令 + 低压跟练收束",
            "candidate_use_status": "screening_candidate_pending_professional_review",
            "source_file_ids": ids_terms,
            "notes": "适合补充 action_complete_cycle 判断。",
        },
        {
            "normalized_action_id": "course_position_method_reference",
            "action_domain": "course_sensitive_text_action_keyword",
            "normalized_action_name_cn": "亲密姿势方法词族",
            "confirmed_source_basis": "课程文本、术语表与问答中存在亲密姿势/体位类标准词和 ASR 变体；本轮只做高层主题归一。",
            "alias_examples": "体位技巧; 亲密姿势; 侧卧式; 女上位; 传教式; 六九式",
            "target_problem_primary": "posture_selection_problem",
            "target_problem_secondary": "high_sensitive_intimate_instruction",
            "audience_or_scene": "成人亲密关系课程片段筛选",
            "primary_key_point": "只能确认文本主题命中，不能确认动作做法、身体适配或画面可用。",
            "wrong_pattern_to_detect": "把 ASR 归一词或课程主题直接改成可上屏动作教程。",
            "speech_keyword_family": "亲密姿势/体位/适合不适合/怎么选择",
            "visual_evidence_required": "本轮不确认视觉动作；后续需客户、合规与专业边界共同确认。",
            "current_visual_evidence_status": "sensitive_text_only_visual_not_confirmed",
            "risk_review_items": "compliance_review_required; customer_review_required; professional_review_required",
            "recommended_structure": "问题问答 + 原因解释 + 方法边界",
            "candidate_use_status": "do_not_auto_publish_high_sensitive",
            "source_file_ids": ";".join(filter(None, [ids_terms, ids_qa])),
            "notes": SENSITIVE_TERM_NOTE,
        },
        {
            "normalized_action_id": "course_body_position_technique_reference",
            "action_domain": "course_sensitive_text_action_keyword",
            "normalized_action_name_cn": "亲密姿势/体位技巧关键词族",
            "confirmed_source_basis": "课程文本与问答中存在该类主题；本知识库不展开源内具体操作细节。",
            "alias_examples": "体位技巧; 姿势; 亲密姿势词族",
            "target_problem_primary": "body_position_technique_sensitive",
            "target_problem_secondary": "relationship_intimacy_method",
            "audience_or_scene": "成人亲密关系课程片段筛选",
            "primary_key_point": "只能做高层主题筛选和合规待审标记。",
            "wrong_pattern_to_detect": "将敏感课程技巧直接改写成直播话术或动作教程。",
            "speech_keyword_family": "亲密姿势/技巧/适合不适合",
            "visual_evidence_required": "本轮不确认视觉动作；后续需客户、合规与专业边界共同确认。",
            "current_visual_evidence_status": "sensitive_text_only_visual_not_confirmed",
            "risk_review_items": "compliance_review_required; customer_review_required; professional_review_required",
            "recommended_structure": "问题问答 + 原因解释 + 方法边界",
            "candidate_use_status": "do_not_auto_publish_high_sensitive",
            "source_file_ids": ";".join(filter(None, [ids_terms, ids_qa])),
            "notes": SENSITIVE_TERM_NOTE,
        },
        {
            "normalized_action_id": "course_touch_or_tool_method_reference",
            "action_domain": "course_sensitive_text_action_keyword",
            "normalized_action_name_cn": "触碰/工具方法关键词族",
            "confirmed_source_basis": "术语表与知识点中存在工具/触碰类主题；本轮不写入操作说明。",
            "alias_examples": "按摩; 工具/产品辅助词族",
            "target_problem_primary": "touch_or_tool_method_sensitive",
            "target_problem_secondary": "tool_or_product_usage",
            "audience_or_scene": "工具演示、产品辅助、成人课程候选",
            "primary_key_point": "仅作为素材风险和主题标签。",
            "wrong_pattern_to_detect": "看不清工具位置或把敏感步骤写成可直接照做。",
            "speech_keyword_family": "工具/产品/按摩/辅助",
            "visual_evidence_required": "工具位置、接触点、遮挡风险需人工确认；本轮不确认。",
            "current_visual_evidence_status": "sensitive_text_only_visual_not_confirmed",
            "risk_review_items": "compliance_review_required; customer_review_required; professional_review_required",
            "recommended_structure": "工具/动作演示 + 发力口令 + 低压跟练收束",
            "candidate_use_status": "do_not_auto_publish_high_sensitive",
            "source_file_ids": ids_terms,
            "notes": SENSITIVE_TERM_NOTE,
        },
        {
            "normalized_action_id": "course_preparation_context_reference",
            "action_domain": "course_sensitive_context_keyword",
            "normalized_action_name_cn": "准备动作/辅助道具词族",
            "confirmed_source_basis": "课程知识点中存在准备、场地、着装或辅助道具类上下文；本轮只做候选主题标记。",
            "alias_examples": "准备动作; 场地准备; 着装准备; 辅助道具; 枕头",
            "target_problem_primary": "preparation_context",
            "target_problem_secondary": "medium_sensitive_contextual",
            "audience_or_scene": "成人课程前置说明、场景准备、道具提示",
            "primary_key_point": "只作为上下文标签；不代表工具/动作安全性成立。",
            "wrong_pattern_to_detect": "看不清道具或场景，却写成工具演示可用。",
            "speech_keyword_family": "准备/道具/场地/着装",
            "visual_evidence_required": "道具、场景、口播指向需人工确认。",
            "current_visual_evidence_status": "text_confirmed_visual_pending_review",
            "risk_review_items": "compliance_review_required; customer_review_required",
            "recommended_structure": "工具/动作演示 + 发力口令 + 低压跟练收束",
            "candidate_use_status": "screening_candidate_pending_customer_review",
            "source_file_ids": ids_terms,
            "notes": "不得写成工具安全或效果已确认。",
        },
        {
            "normalized_action_id": "course_relationship_problem_reference",
            "action_domain": "course_problem_keyword",
            "normalized_action_name_cn": "亲密关系/伴侣沟通问题",
            "confirmed_source_basis": "课程知识点、问答与直播桥接字段存在亲密关系/伴侣沟通主题。",
            "alias_examples": "亲密关系; 伴侣沟通; 情感互动; 婚姻关系",
            "target_problem_primary": "relationship_communication",
            "target_problem_secondary": "qa_objection_response",
            "audience_or_scene": "直播答疑、课程价值解释、问题承接",
            "primary_key_point": "适合做问题/原因/边界结构，不要求动作演示。",
            "wrong_pattern_to_detect": "只截情绪化痛点，没有原因解释或方法边界。",
            "speech_keyword_family": "伴侣/沟通/关系/情感/困惑",
            "visual_evidence_required": "口播完整主语和原因链；画面只作辅助。",
            "current_visual_evidence_status": "text_context_confirmed_visual_optional",
            "risk_review_items": "customer_review_if_business_claim; compliance_review_if_sensitive",
            "recommended_structure": "痛点问题 + 原因解释 + 方法交付",
            "candidate_use_status": "text_screening_candidate_pending_customer_review",
            "source_file_ids": ";".join(filter(None, [ids_terms, ids_qa])),
            "notes": "不写成情感效果已确认。",
        },
        {
            "normalized_action_id": "course_product_offer_reference",
            "action_domain": "course_business_keyword",
            "normalized_action_name_cn": "课程/助理/报名业务词",
            "confirmed_source_basis": "课程文本上下文中存在课程、助理、专场等业务词。",
            "alias_examples": "课程; 课程助理; 专场; 报名",
            "target_problem_primary": "course_offer_or_business",
            "target_problem_secondary": "business_fact",
            "audience_or_scene": "课程介绍、转化引导、直播资料字段",
            "primary_key_point": "只做业务事实待确认字段，不自动写价格/承诺。",
            "wrong_pattern_to_detect": "把课程介绍改成未经确认的直播销售话术。",
            "speech_keyword_family": "课程/助理/报名/专场",
            "visual_evidence_required": "需客户确认课程名称、价格、权益、链接。",
            "current_visual_evidence_status": "business_text_only_pending_customer_review",
            "risk_review_items": "customer_review_required; business_fact_review_required",
            "recommended_structure": "问题问答 + 原因解释 + 方法边界",
            "candidate_use_status": "business_fact_pending_customer_review",
            "source_file_ids": ids_terms,
            "notes": "不写业务通过。",
        },
        {
            "normalized_action_id": "unknown_or_unusable_visual_action",
            "action_domain": "visual_review_blocker",
            "normalized_action_name_cn": "低置信/不可用视觉动作",
            "confirmed_source_basis": "动作时间轴、三线对照和逐句 JSONL 中大量 low_confidence、no_face、scene_no_presenter、OCR unavailable 类状态。",
            "alias_examples": "low_confidence_action_pending_review; slide_or_scene_no_presenter_detected; no_face_detected; ocr_unavailable_need_manual_review",
            "target_problem_primary": "visual_review_blocker",
            "target_problem_secondary": "manual_review_queue",
            "audience_or_scene": "人工复核索引、不可自动下发动作的候选",
            "primary_key_point": "只用于阻断自动化和排队人工复核。",
            "wrong_pattern_to_detect": "低置信动作直接进入自动播放或剪辑结论。",
            "speech_keyword_family": "不适用",
            "visual_evidence_required": "重新抽帧/人工看原片/视觉模型复核。",
            "current_visual_evidence_status": "blocked_pending_visual_review",
            "risk_review_items": "visual_review_required",
            "recommended_structure": "日期/主题不明素材 + 待视觉复核索引",
            "candidate_use_status": "manual_review_only",
            "source_file_ids": ";".join(filter(None, [ids_timeline, ids_alignment])),
            "notes": "不得升格为动作确认。",
        },
    ]


def build_alias_rows(action_rows: list[dict[str, str]], rows: list[dict[str, str]]) -> list[dict[str, str]]:
    id_by_action = {row["normalized_action_id"]: row for row in action_rows}
    alias_specs = [
        ("neutral_idle", "presenter_neutral_idle", "source_label", "07_动作标签库_action_label_library.md"),
        ("自然静止", "presenter_neutral_idle", "cn_label", "07_动作标签库_action_label_library.md"),
        ("hand_open_explain", "presenter_open_explain", "source_label", "07_动作标签库_action_label_library.md"),
        ("张手解释", "presenter_open_explain", "cn_label", "07_动作标签库_action_label_library.md"),
        ("question_prompt", "presenter_open_explain", "prosody_label", "12_数字人动作触发规则_avatar_action_trigger_rules.csv"),
        ("hand_point_screen", "presenter_screen_point_or_highlight", "source_label", "07_动作标签库_action_label_library.md"),
        ("highlight_focus", "presenter_screen_point_or_highlight", "source_label", "07_动作标签库_action_label_library.md"),
        ("eye_to_slide", "presenter_screen_point_or_highlight", "source_label", "07_动作标签库_action_label_library.md"),
        ("mouse_pointer_move", "presenter_screen_point_or_highlight", "source_label", "07_动作标签库_action_label_library.md"),
        ("hand_counting", "presenter_step_count_or_page_turn", "source_label", "07_动作标签库_action_label_library.md"),
        ("page_turn", "presenter_step_count_or_page_turn", "source_label", "07_动作标签库_action_label_library.md"),
        ("serious_emphasis", "presenter_emphasis_warning_pause", "source_label", "07_动作标签库_action_label_library.md"),
        ("pause_thinking", "presenter_emphasis_warning_pause", "source_label", "07_动作标签库_action_label_library.md"),
        ("warning_reminder", "presenter_emphasis_warning_pause", "prosody_label", "12_数字人动作触发规则_avatar_action_trigger_rules.csv"),
        ("盆底肌", "course_pelvic_floor_training_reference", "course_term", "08_关键词术语表_terms_glossary.csv"),
        ("私密训练", "course_pelvic_floor_training_reference", "course_term", "08_关键词术语表_terms_glossary.csv"),
        ("私密瑜伽", "course_pelvic_floor_training_reference", "course_term", "08_关键词术语表_terms_glossary.csv"),
        ("收紧/放松", "course_pelvic_floor_training_reference", "course_term_family", "knowledge_points.csv"),
        ("呼吸", "course_breathing_coordination_reference", "course_term", "08_关键词术语表_terms_glossary.csv"),
        ("后入式", "course_position_method_reference", "sensitive_course_term", "knowledge_points.csv"),
        ("後入式", "course_position_method_reference", "sensitive_asr_or_traditional_alias_pending_review", "knowledge_points.csv"),
        ("传教式", "course_position_method_reference", "sensitive_course_term", "knowledge_points.csv"),
        ("女上位", "course_position_method_reference", "sensitive_course_term", "knowledge_points.csv"),
        ("六九式", "course_position_method_reference", "sensitive_course_term", "knowledge_points.csv"),
        ("六九的姿势", "course_position_method_reference", "sensitive_course_term", "knowledge_points.csv"),
        ("侧卧式", "course_position_method_reference", "sensitive_asr_alias_pending_review", "knowledge_points.csv"),
        ("策卧室/策务室", "course_position_method_reference", "推测_asr_alias_pending_review", "knowledge_points.csv"),
        ("女骑手/女起手/女尚未", "course_position_method_reference", "推测_asr_alias_pending_review", "knowledge_points.csv"),
        ("体味技巧", "course_position_method_reference", "推测_asr_alias_pending_review", "knowledge_points.csv"),
        ("体位技巧", "course_body_position_technique_reference", "sensitive_course_term", "08_关键词术语表_terms_glossary.csv"),
        ("私命瑜伽/私女一家/私密与家", "course_pelvic_floor_training_reference", "推测_asr_alias_pending_review", "knowledge_points.csv"),
        ("盆底积/盘底机", "course_pelvic_floor_training_reference", "推测_asr_alias_pending_review", "knowledge_points.csv"),
        ("音道", "course_body_position_technique_reference", "推测_asr_alias_pending_review", "knowledge_points.csv"),
        ("防势养生", "course_body_position_technique_reference", "推测_asr_alias_pending_review", "knowledge_points.csv"),
        ("亲密姿势词族", "course_body_position_technique_reference", "sensitive_keyword_family", "knowledge_points.csv"),
        ("按摩/触碰方法词族", "course_touch_or_tool_method_reference", "sensitive_keyword_family", "knowledge_points.csv"),
        ("工具/产品辅助词族", "course_touch_or_tool_method_reference", "sensitive_keyword_family", "knowledge_points.csv"),
        ("准备动作/场地准备/着装准备", "course_preparation_context_reference", "sensitive_context_keyword_family", "knowledge_points.csv"),
        ("辅助道具/枕头", "course_preparation_context_reference", "sensitive_context_keyword_family", "knowledge_points.csv"),
        ("亲密关系", "course_relationship_problem_reference", "course_term", "knowledge_points.csv"),
        ("伴侣沟通", "course_relationship_problem_reference", "course_term_family", "09_问题_答案_异议_回应_QA_objection_response_bank.csv"),
        ("课程", "course_product_offer_reference", "business_term", "08_关键词术语表_terms_glossary.csv"),
        ("课程助理/专场", "course_product_offer_reference", "business_term_family", "knowledge_points.csv"),
        ("low_confidence_action_pending_review", "unknown_or_unusable_visual_action", "source_label", "06_讲师动作时间轴_presenter_action_timeline.csv"),
        ("slide_or_scene_no_presenter_detected", "unknown_or_unusable_visual_action", "source_label", "sentence_action_shards"),
        ("no_face_detected", "unknown_or_unusable_visual_action", "source_status", "sentence_action_shards"),
        ("ocr_unavailable_need_manual_review", "unknown_or_unusable_visual_action", "source_status", "09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv"),
    ]
    output = []
    for index, (alias, action_id, alias_type, pattern) in enumerate(alias_specs, start=1):
        action = id_by_action[action_id]
        output.append(
            {
                "alias_id": f"ALIAS{index:03d}",
                "source_alias": alias,
                "normalized_action_id": action_id,
                "normalized_action_name_cn": action["normalized_action_name_cn"],
                "alias_type": alias_type,
                "source_basis": "source_label_or_keyword_family",
                "source_file_ids": source_ids(rows, pattern, grades=("A", "B")),
                "normalization_status": "ready_for_screening_with_review_gate",
                "review_gate": action["risk_review_items"],
                "notes": "敏感词族不展开源内操作细节。" if "sensitive" in alias_type else "保留 confidence/review_flag 闸门。",
            }
        )
    return output


def build_taxonomy_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    ids_terms = source_ids(rows, "08_关键词术语表_terms_glossary.csv", "knowledge_points.csv")
    ids_action = source_ids(rows, "07_动作标签库_action_label_library.md", "06_讲师动作时间轴_presenter_action_timeline.csv", "sentence_action_shards")
    ids_bridge = source_ids(rows, "live_project_bridge_fields.csv", "09_问题_答案_异议_回应_QA_objection_response_bank.csv")
    return [
        {
            "problem_category_id": "pelvic_floor_training",
            "problem_category_name_cn": "盆底/私密训练",
            "definition": "训练类文本命中，可作为动作候选筛选入口。",
            "source_keyword_families": "盆底/私密训练/收紧/放松",
            "recommended_structure": "痛点/人群点名 + 单动作完整循环 + 坚持建议",
            "required_evidence": "完整动作循环、发力方向、呼吸/次数口令、无遮挡画面。",
            "risk_gate": "professional_review_required; health_claim_review_required",
            "usable_status": "text_keyword_confirmed_visual_pending_review",
            "source_file_ids": ids_terms,
        },
        {
            "problem_category_id": "breathing_coordination",
            "problem_category_name_cn": "呼吸配合",
            "definition": "口令/节奏辅助字段，不能替代动作证据。",
            "source_keyword_families": "呼吸/气息/配合",
            "recommended_structure": "工具/动作演示 + 发力口令 + 低压跟练收束",
            "required_evidence": "口令与动作节奏同步，至少一次完整循环。",
            "risk_gate": "professional_review_required",
            "usable_status": "text_keyword_confirmed_visual_pending_review",
            "source_file_ids": ids_terms,
        },
        {
            "problem_category_id": "relationship_desire_problem",
            "problem_category_name_cn": "亲密关系诉求/伴侣感受",
            "definition": "提升关系、伴侣感受、亲密互动等文本问题候选。",
            "source_keyword_families": "伴侣/亲密关系/愉悦度/感受",
            "recommended_structure": "痛点问题 + 原因解释 + 方法交付",
            "required_evidence": "完整问题句、原因链、方法边界，不写关系改善已成立。",
            "risk_gate": "medium_sensitive_relationship; customer_review_if_business_claim",
            "usable_status": "text_screening_candidate_pending_customer_review",
            "source_file_ids": ";".join(filter(None, [ids_terms, ids_bridge])),
        },
        {
            "problem_category_id": "posture_selection_problem",
            "problem_category_name_cn": "亲密姿势选择问题",
            "definition": "围绕姿势选择、适配、怎么做的敏感课程文本候选。",
            "source_keyword_families": "体位/姿势/适合自己/怎么选择",
            "recommended_structure": "问题问答 + 原因解释 + 方法边界",
            "required_evidence": "仅可保留高层主题和边界；不能写具体操作教程。",
            "risk_gate": "high_sensitive_intimate_instruction; compliance_review_required",
            "usable_status": "do_not_auto_publish_high_sensitive",
            "source_file_ids": ";".join(filter(None, [ids_terms, ids_bridge])),
        },
        {
            "problem_category_id": "body_matching_problem",
            "problem_category_name_cn": "身体适配/结构匹配问题",
            "definition": "身体差异、适配、结构匹配类表达。",
            "source_keyword_families": "身体结构/匹配/适配",
            "recommended_structure": "问题问答 + 原因解释 + 方法边界",
            "required_evidence": "专业与合规复核；不能写身体结论已确认。",
            "risk_gate": "high_sensitive_body_claim; professional_review_required",
            "usable_status": "professional_review_required_before_use",
            "source_file_ids": ids_terms,
        },
        {
            "problem_category_id": "breath_pelvic_floor_control_problem",
            "problem_category_name_cn": "呼吸/盆底控制问题",
            "definition": "呼吸配合、盆底收缩放松、发力方向类问题。",
            "source_keyword_families": "呼吸/盆底/收紧/放松/发力",
            "recommended_structure": "痛点/人群点名 + 单动作完整循环 + 坚持建议",
            "required_evidence": "完整动作循环、口令、发力方向；需专业复核。",
            "risk_gate": "high_health_action_professional; health_claim_review_required",
            "usable_status": "health_action_risk_pending_professional_review",
            "source_file_ids": ids_terms,
        },
        {
            "problem_category_id": "discomfort_symptom_problem",
            "problem_category_name_cn": "不适/症状/健康风险问题",
            "definition": "不舒服、干燥、异味、漏尿、疼痛等症状或健康风险类文本。",
            "source_keyword_families": "不舒服/干燥/异味/漏尿/疼痛",
            "recommended_structure": "问题问答 + 原因解释 + 方法边界",
            "required_evidence": "必须保留非诊断边界和专业复核状态。",
            "risk_gate": "critical_health_claim_review_required; professional_review_required",
            "usable_status": "health_claim_pending_professional_review",
            "source_file_ids": ids_terms,
        },
        {
            "problem_category_id": "product_or_care_usage_problem",
            "problem_category_name_cn": "产品/护理使用问题",
            "definition": "精油、护理产品、工具辅助等产品或护理使用文本。",
            "source_keyword_families": "精油/产品/护理/按摩/工具",
            "recommended_structure": "工具/动作演示 + 发力口令 + 低压跟练收束",
            "required_evidence": "产品功效、使用边界、客户/合规确认。",
            "risk_gate": "critical_product_effect_review_required; customer_review_required",
            "usable_status": "product_effect_pending_customer_compliance_review",
            "source_file_ids": ids_terms,
        },
        {
            "problem_category_id": "body_position_technique_sensitive",
            "problem_category_name_cn": "亲密姿势/体位技巧",
            "definition": "成人亲密关系课程主题，只做高层主题和合规待审标记。",
            "source_keyword_families": "体位技巧/姿势/亲密姿势词族",
            "recommended_structure": "问题问答 + 原因解释 + 方法边界",
            "required_evidence": "客户、合规、专业边界确认；本轮不确认视觉动作。",
            "risk_gate": "compliance_review_required; customer_review_required; professional_review_required",
            "usable_status": "do_not_auto_publish_high_sensitive",
            "source_file_ids": ids_terms,
        },
        {
            "problem_category_id": "touch_or_tool_method_sensitive",
            "problem_category_name_cn": "触碰/工具方法",
            "definition": "工具或触碰类主题，只作为风险和主题标签。",
            "source_keyword_families": "按摩/工具/产品辅助词族",
            "recommended_structure": "工具/动作演示 + 发力口令 + 低压跟练收束",
            "required_evidence": "工具位置、遮挡风险、适用边界均需人工确认。",
            "risk_gate": "compliance_review_required; customer_review_required; professional_review_required",
            "usable_status": "do_not_auto_publish_high_sensitive",
            "source_file_ids": ids_terms,
        },
        {
            "problem_category_id": "relationship_communication",
            "problem_category_name_cn": "亲密关系/伴侣沟通",
            "definition": "问题、原因、方法边界类文本候选。",
            "source_keyword_families": "亲密关系/伴侣/沟通/情感",
            "recommended_structure": "痛点问题 + 原因解释 + 方法交付",
            "required_evidence": "完整主语、原因链、边界句。",
            "risk_gate": "customer_review_if_business_claim; compliance_review_if_sensitive",
            "usable_status": "text_screening_candidate_pending_customer_review",
            "source_file_ids": ";".join(filter(None, [ids_terms, ids_bridge])),
        },
        {
            "problem_category_id": "course_offer_or_business",
            "problem_category_name_cn": "课程/业务事实",
            "definition": "课程、助理、转化相关词，必须客户确认。",
            "source_keyword_families": "课程/助理/报名/专场",
            "recommended_structure": "问题问答 + 原因解释 + 方法边界",
            "required_evidence": "课程名称、权益、价格、链接、口径均需客户确认。",
            "risk_gate": "customer_review_required; business_fact_review_required",
            "usable_status": "business_fact_pending_customer_review",
            "source_file_ids": ids_terms,
        },
        {
            "problem_category_id": "presentation_delivery",
            "problem_category_name_cn": "数字人/讲师呈现动作",
            "definition": "讲解手势、表情、视线、镜头等呈现层动作。",
            "source_keyword_families": "neutral_idle/hand_open_explain/serious_emphasis",
            "recommended_structure": "痛点问题 + 原因解释 + 方法交付",
            "required_evidence": "口播、手势、视线、表情同向。",
            "risk_gate": "visual_review_required",
            "usable_status": "bridge_only_pending_human_review",
            "source_file_ids": ids_action,
        },
        {
            "problem_category_id": "courseware_attention",
            "problem_category_name_cn": "课件/屏幕重点承接",
            "definition": "课件指向、高亮、鼠标或视线关注。",
            "source_keyword_families": "hand_point_screen/highlight_focus/eye_to_slide",
            "recommended_structure": "工具/动作演示 + 发力口令 + 低压跟练收束",
            "required_evidence": "OCR/课件文字和动作指向同题。",
            "risk_gate": "visual_review_required; ocr_review_required",
            "usable_status": "screening_helper_pending_visual_review",
            "source_file_ids": ids_action,
        },
        {
            "problem_category_id": "risk_boundary",
            "problem_category_name_cn": "注意事项/风险边界",
            "definition": "警示、禁忌、适用/不适用边界。",
            "source_keyword_families": "warning_reminder/serious_emphasis/注意/不要",
            "recommended_structure": "结果前置 + 操作过程 + 注意事项/风险边界",
            "required_evidence": "不要删掉风险提醒和适用边界。",
            "risk_gate": "professional_review_required; compliance_review_required",
            "usable_status": "risk_gate_required_before_live_use",
            "source_file_ids": ";".join(filter(None, [ids_action, ids_bridge])),
        },
        {
            "problem_category_id": "visual_review_blocker",
            "problem_category_name_cn": "视觉低置信/不可用",
            "definition": "OCR/人脸/动作/画面不可确认时的阻断类。",
            "source_keyword_families": "low_confidence/no_face/scene_no_presenter/OCR unavailable",
            "recommended_structure": "日期/主题不明素材 + 待视觉复核索引",
            "required_evidence": "重新抽帧、人工看原片或视觉模型复核。",
            "risk_gate": "visual_review_required",
            "usable_status": "manual_review_only",
            "source_file_ids": ids_action,
        },
        {
            "problem_category_id": "live_interaction_noise_problem",
            "problem_category_name_cn": "直播问答碎片/ASR 噪声",
            "definition": "半句问题、ASR 错别字、时间码碎片或证据不足的文本候选。",
            "source_keyword_families": "推测_asr_alias_pending_review/半句问题/source_review_flag",
            "recommended_structure": "日期/主题不明素材 + 待视觉复核索引",
            "required_evidence": "回看上下文、确认别名、补齐完整句。",
            "risk_gate": "low_evidence_extraction_noise; needs_human_review",
            "usable_status": "alias_candidate_pending_review",
            "source_file_ids": ";".join(filter(None, [ids_terms, ids_bridge])),
        },
    ]


def build_bridge_rows(action_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    bridge_specs = [
        (
            "presenter_neutral_idle",
            "痛点问题 + 原因解释 + 方法交付",
            "语气承接",
            "C",
            "口播完整即可；动作只是呈现层。",
            "人物/数字人状态不冲突即可。",
        ),
        (
            "presenter_open_explain",
            "问题问答 + 原因解释 + 方法边界",
            "问题承接",
            "B",
            "问题句、原因句、方法边界完整。",
            "手势、表情、视线同题；否则只作文本候选。",
        ),
        (
            "presenter_screen_point_or_highlight",
            "工具/动作演示 + 发力口令 + 低压跟练收束",
            "字幕承接",
            "B",
            "口播提到位置、步骤、重点。",
            "课件/OCR/指向/鼠标轨迹需同向。",
        ),
        (
            "presenter_step_count_or_page_turn",
            "多动作组合 + 同一主题推进 + 轻跟练收束",
            "方法承接",
            "B",
            "步骤顺序清楚，多个动作服务同一主题。",
            "翻页或数数动作与口播顺序一致。",
        ),
        (
            "presenter_emphasis_warning_pause",
            "结果前置 + 操作过程 + 注意事项/风险边界",
            "异议承接",
            "A",
            "注意事项、适用/不适用边界必须保留。",
            "语气/字幕/表情至少一项能体现风险提醒。",
        ),
        (
            "course_pelvic_floor_training_reference",
            "痛点/人群点名 + 单动作完整循环 + 坚持建议",
            "动作承接",
            "A",
            "同一痛点、动作口令、低压建议完整。",
            "完整动作循环、发力方向、呼吸/次数、无遮挡。",
        ),
        (
            "course_breathing_coordination_reference",
            "工具/动作演示 + 发力口令 + 低压跟练收束",
            "方法承接",
            "B",
            "呼吸口令与动作口令同题。",
            "呼吸节奏与动作起势/回位同步。",
        ),
        (
            "course_position_method_reference",
            "问题问答 + 原因解释 + 方法边界",
            "方法承接",
            "C",
            "只允许高层主题和适用/不适用边界。",
            "本轮不确认视觉；需客户/合规/专业复核。",
        ),
        (
            "course_body_position_technique_reference",
            "问题问答 + 原因解释 + 方法边界",
            "方法承接",
            "C",
            "只允许高层主题和边界，不写敏感细节。",
            "本轮不确认视觉；需客户/合规/专业复核。",
        ),
        (
            "course_touch_or_tool_method_reference",
            "工具/动作演示 + 发力口令 + 低压跟练收束",
            "动作承接",
            "C",
            "只保留高层工具/方法词族和风险标签。",
            "工具位置、接触点、遮挡风险需人工确认。",
        ),
        (
            "course_preparation_context_reference",
            "工具/动作演示 + 发力口令 + 低压跟练收束",
            "字幕承接",
            "C",
            "只保留准备/道具/场景高层上下文。",
            "道具、场景、口播指向需人工确认。",
        ),
        (
            "course_relationship_problem_reference",
            "痛点问题 + 原因解释 + 方法交付",
            "问题承接",
            "A",
            "完整问题、原因、边界，不只截情绪化痛点。",
            "画面不强制，但字幕/口播主语必须完整。",
        ),
        (
            "course_product_offer_reference",
            "问题问答 + 原因解释 + 方法边界",
            "信任承接",
            "C",
            "业务事实需客户确认后才可进入直播话术。",
            "课程名/权益/价格/链接需客户确认。",
        ),
        (
            "unknown_or_unusable_visual_action",
            "日期/主题不明素材 + 待视觉复核索引",
            "none",
            "C",
            "只进人工复核排队。",
            "必须重新视觉复核。",
        ),
    ]
    by_id = {row["normalized_action_id"]: row for row in action_rows}
    output = []
    for index, (action_id, structure, bridge_type, priority, text_req, visual_req) in enumerate(bridge_specs, start=1):
        action = by_id[action_id]
        health_business = "yes" if any(token in action["risk_review_items"] for token in ("professional", "health", "business", "customer", "compliance")) else "no"
        output.append(
            {
                "bridge_id": f"BRIDGE{index:03d}",
                "normalized_action_id": action_id,
                "normalized_action_name_cn": action["normalized_action_name_cn"],
                "usable_structure_name": structure,
                "bridge_type": bridge_type,
                "stage1_priority": priority,
                "required_text_evidence": text_req,
                "required_visual_evidence": visual_req,
                "speech_action_sync_requirement": "说话、动作、表情/画面三条证据同题；任一断裂则 pending_user_visual_review。",
                "recommended_editor_action": "先筛文本完整单元，再看动作/画面证据，最后保留风险边界。",
                "transition_status": "pending_validation",
                "visual_review_status": action["current_visual_evidence_status"],
                "health_business_review_required": health_business,
                "candidate_status": action["candidate_use_status"],
                "manual_review_items": action["risk_review_items"],
                "notes": "不能写 publish_ready 或业务通过。",
            }
        )
    return output


def md_table_from_counts(counter: Counter[str], limit: int = 12) -> str:
    lines = ["| value | count |", "|---|---:|"]
    for value, count in counter.most_common(limit):
        safe_value = value if value else "[empty]"
        lines.append(f"| `{safe_value}` | {count} |")
    if not counter:
        lines.append("| [none] | 0 |")
    return "\n".join(lines)


def write_rules_md(stats: dict[str, object]) -> None:
    now = dt.datetime.now().isoformat(timespec="seconds")
    content = f"""# 动作应用规则说明

状态：`completed_with_pending_user_review`
生成时间：{now}

## 1. 本知识库能做什么

- 用 `/Volumes/WD_BLACK/AI解析` 的课程解析派生产物建立动作/问题/剪辑结构的桥接表。
- 区分两类动作：`presenter_avatar_action`（讲师/数字人呈现动作）与 `course_text_action_keyword`（课程文本中的动作或问题关键词）。
- 给直播素材筛选提供候选字段，而不是直接生成最终话术、健康结论、动作专业判断或发布结论。

## 2. 本知识库不能做什么

- 不能写 `publish_ready`、`business_ready`、`professional_action_passed`。
- 不能把 `text_keyword_confirmed` 写成 `visual_action_confirmed`。
- 不能把课程文本里的敏感操作细节搬进仓库；本轮只保留高层词族和风险闸门。
- 不能忽略源数据里的 `confidence`、`review_flag`、`human_review_needed`。

## 3. 使用顺序

1. 先用 `02_动作别名归一表_action_alias_normalization.csv` 把源标签/词族归一到 `normalized_action_id`。
2. 再用 `01_动作问题映射表_action_problem_mapping.csv` 判断它属于呈现动作、课程动作关键词、业务词还是视觉阻断。
3. 再用 `04_动作剪辑结构桥接表_action_clip_structure_bridge.csv` 选择可尝试的结构公式。
4. 最后人工复核画面、口播、字幕、健康/合规/客户事实，不通过则保持 `pending_user_visual_review`。

## 4. 强制闸门

- `low_confidence`、`pending_review`、`no_face_detected`、`ocr_unavailable`：只进入人工复核。
- 涉及训练、健康、身体效果、适用人群：`professional_review_required`。
- 涉及课程名、价格、报名、权益、客户承诺：`customer_review_required` 与 `business_fact_review_required`。
- 涉及成人亲密关系敏感主题：`compliance_review_required`，不得自动改写成直播话术。

## 5. 源数据状态摘要

### usefulness grade

{md_table_from_counts(stats["grade_counts"])}

### source read status

{md_table_from_counts(stats["read_status_counts"])}

### action confidence

{md_table_from_counts(stats["action_confidence"])}

### review flags

{md_table_from_counts(stats["review_flags"])}

## 6. 字段落库边界

- `source_file_ids` 只追溯派生产物文件，不追溯或复制原始媒体。
- `alias_examples` 是归一口径，不是课程原文摘录。
- 后续若接入自动筛选，默认输出 `candidate_status=pending_user_visual_review`，直到人工确认。
"""
    RULES_PATH.write_text(content, encoding="utf-8")


def write_screening_md(stats: dict[str, object]) -> None:
    now = dt.datetime.now().isoformat(timespec="seconds")
    content = f"""# 动作知识库接入直播筛选说明

状态：`bridge_ready_pending_live_material_validation`
生成时间：{now}

## 1. 接入位置

本知识库应接在直播素材候选筛选的“结构初筛”之后、“人工视觉复核”之前：

1. 直播录屏转写/时间码完成。
2. 候选片段命中问题、动作、课程或风险词族。
3. 用本目录 01-04 表补齐 `normalized_action_id`、`problem_category_id`、`bridge_type`、`candidate_status`。
4. 人工看原片/关键帧，确认 `speech_complete_unit`、`action_complete_cycle`、`visual_obstruction_risk`。
5. 只有人工复核通过后，才允许进入剪辑师加工或更高阶自动化。

## 2. 建议新增或复用字段

- `normalized_action_id`
- `problem_category_id`
- `source_file_ids`
- `speech_keyword_family`
- `speech_complete_unit`
- `action_complete_cycle`
- `visual_obstruction_risk`
- `speech_action_sync`
- `bridge_type`
- `transition_status`
- `visual_review_status`
- `health_business_review_required`
- `business_fact_status`
- `candidate_status`
- `manual_review_items`

## 3. 默认状态规则

- 文本命中：`text_keyword_confirmed_visual_pending_review`
- 呈现动作标签命中：`bridge_only_pending_human_review`
- 视觉低置信：`manual_review_only`
- 涉及健康/训练/效果：`screening_candidate_pending_professional_review`
- 涉及客户业务事实：`business_fact_pending_customer_review`
- 涉及成人亲密关系敏感主题：`do_not_auto_publish_high_sensitive`

## 4. 与五结构的桥接

- `错误/误区先抛 + 正确动作对比 + 原因解释`：只在能看出错误/正确差异时使用。
- `痛点问题 + 原因解释 + 方法交付`：适合文本问题类，但必须保留原因链和边界。
- `痛点/人群点名 + 单动作完整循环 + 坚持建议`：必须看到完整动作循环。
- `工具/动作演示 + 发力口令 + 低压跟练收束`：必须看清工具/身体接触点/口令同步。
- `日期/主题不明素材 + 待视觉复核索引`：低置信、无遮挡不足、OCR 不可用时使用。

## 5. 当前源包对直播筛选的限制

- `course pack` 可提供 chunk-level 时间窗口，但大量动作是低置信占位。
- `sentence workspace` 粒度更细，但同样存在 `human_review_needed=yes` 与视觉采样近邻复核要求。
- 源文本可提示“可能是什么问题/主题”，不能证明“画面动作已经可用”。
- 本轮没有复制原始媒体，没有做新的视觉模型复核，没有写动作专业通过。

## 6. 已抽取的关键计数

### top-level source count

{md_table_from_counts(stats["top_level_counts"], limit=20)}

### bridge intents

{md_table_from_counts(stats["bridge_intents"])}

### bridge risks

{md_table_from_counts(stats["bridge_risks"])}
"""
    SCREENING_PATH.write_text(content, encoding="utf-8")


def write_report(stats: dict[str, object], outputs: list[Path]) -> None:
    now = dt.datetime.now().isoformat(timespec="seconds")
    total = stats["total_files"]
    grade_counts: Counter[str] = stats["grade_counts"]  # type: ignore[assignment]
    kind_counts: Counter[str] = stats["kind_counts"]  # type: ignore[assignment]
    csv_counts: dict[str, int] = stats["csv_row_counts"]  # type: ignore[assignment]
    jsonl_counts: dict[str, int] = stats["jsonl_row_counts"]  # type: ignore[assignment]

    extracted_rows = [
        f"- `{rel}`：{count} rows"
        for rel, count in sorted({**csv_counts, **jsonl_counts}.items())
    ]
    if not extracted_rows:
        extracted_rows = ["- 无高价值表被抽取。"]

    output_rows = [f"- `{path.relative_to(REPO_ROOT).as_posix()}`" for path in outputs]

    content = f"""# 课程动作资料审计与映射执行报告

状态：`course_action_data_audit_generated_pending_user_review`
生成时间：{now}

## 1. 目标

本轮任务为 `course_action_data_audit_and_mapping`：审计 `/Volumes/WD_BLACK/AI解析`，生成课程动作资料清单、可用性分级、动作知识库和直播筛选接入说明。

## 2. 已确认输入边界

- 源目录：`/Volumes/WD_BLACK/AI解析`
- 仓库目录：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--`
- 源目录只读：yes
- 是否复制源包/媒体/cache/API 原始输出：no
- 是否写健康效果成立：no
- 是否写业务通过：no
- 是否写动作专业性通过：no

## 3. 源目录清点摘要

- 总文件数：{total}
- A 类动作核心/JSONL：{grade_counts.get("A", 0)}
- B 类课程文本上下文：{grade_counts.get("B", 0)}
- C 类支撑/封装/媒体引用：{grade_counts.get("C", 0)}
- D 类重复/缓存/运行环境/不可用：{grade_counts.get("D", 0)}

### file_kind top counts

{md_table_from_counts(kind_counts, limit=16)}

## 4. 高价值表抽取摘要

{chr(10).join(extracted_rows)}

## 5. 关键判断

- `course pack` 能提供 chunk-level 时间窗口和动作标签库，但大量记录为低置信占位，不能作为自动动作下发依据。
- `sentence workspace` 粒度更细，可用于候选筛选字段，但仍保留 `human_review_needed` 和视觉近邻复核要求。
- 源包同时包含“讲师/数字人呈现动作”和“课程文本动作/问题关键词”；本轮已拆成两个 action_domain，避免混用。
- 成人亲密关系敏感课程词只保留高层词族与风险闸门，不搬运源内操作细节。

## 6. 本轮输出文件

{chr(10).join(output_rows)}

## 7. 后续使用方式

- 直播素材筛选先用 `02_动作别名归一表` 命中 `normalized_action_id`。
- 再看 `03_问题分类表` 和 `04_动作剪辑结构桥接表` 判断是否进入候选。
- 只要视觉、健康、合规、客户事实任一未确认，就保持 `pending_user_visual_review` 或对应 review gate。

## 8. 待确认项

- 客户是否允许成人亲密关系敏感主题进入直播筛选。
- 哪些课程词族需要合规脱敏或完全禁用。
- 视觉复核是否采用人工、视觉模型或二者组合。
- 业务事实、课程权益、价格、转化话术需要客户另行确认。

## 9. validation plan

- `python3 -m py_compile scripts/audit_course_action_data.py`
- `python3 scripts/audit_course_action_data.py`
- `python3 scripts/check_ali_config_safety.py`
- `git diff --check`
- `git diff --cached --check`
- CSV 行数、表头、状态字段和禁用文件类型抽查。

## 10. commit / push

- 本报告由脚本生成；最终 artifact commit、push 和 remote HEAD 以 Codex 本轮最终回报为准。
"""
    REPORT_PATH.write_text(content, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    inventory_rows = build_inventory()
    usefulness_rows = [
        {
            "source_file_id": row["source_file_id"],
            "relative_path": row["relative_path"],
            "usefulness_grade": row["usefulness_grade"],
            "usefulness_type": row["usefulness_type"],
            "file_kind": row["file_kind"],
            "read_status": row["read_status"],
            "duplicate_status": row["duplicate_status"],
            "recommended_usage": row["recommended_usage"],
            "notes": row["notes"],
        }
        for row in inventory_rows
    ]
    write_csv(INVENTORY_PATH, inventory_rows)
    write_csv(USEFULNESS_PATH, usefulness_rows)

    stats = collect_source_stats(inventory_rows)

    action_rows = build_action_mapping(inventory_rows)
    alias_rows = build_alias_rows(action_rows, inventory_rows)
    taxonomy_rows = build_taxonomy_rows(inventory_rows)
    bridge_rows = build_bridge_rows(action_rows)

    write_csv(ACTION_MAPPING_PATH, action_rows)
    write_csv(ALIAS_PATH, alias_rows)
    write_csv(TAXONOMY_PATH, taxonomy_rows)
    write_csv(BRIDGE_PATH, bridge_rows)
    write_rules_md(stats)
    write_screening_md(stats)
    write_report(
        stats,
        [
            INVENTORY_PATH,
            USEFULNESS_PATH,
            ACTION_MAPPING_PATH,
            ALIAS_PATH,
            TAXONOMY_PATH,
            BRIDGE_PATH,
            RULES_PATH,
            SCREENING_PATH,
            REPORT_PATH,
            REPO_ROOT / "scripts" / "audit_course_action_data.py",
        ],
    )

    print(f"inventory_rows={len(inventory_rows)}")
    print(f"action_mapping_rows={len(action_rows)}")
    print(f"alias_rows={len(alias_rows)}")
    print(f"taxonomy_rows={len(taxonomy_rows)}")
    print(f"bridge_rows={len(bridge_rows)}")
    print(f"source_root={SOURCE_ROOT}")
    print(f"report={REPORT_PATH}")


if __name__ == "__main__":
    main()
