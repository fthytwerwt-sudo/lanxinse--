#!/usr/bin/env python3
"""Build the selected AI analysis extract pack for the clipping project.

The external source directory is read-only input. This script copies only small,
high-value text artifacts and writes redacted/traceable extracts for large
tables. It intentionally avoids media, archives, caches, secrets, and raw API
outputs.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = Path("/Volumes/WD_BLACK/AI解析")
SOURCE_ROOT_WITH_SPACE = Path("/Volumes/WD_BLACK/AI 解析")

AUDIT_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis" / "10_course_action_data_audit"
OUTPUT_DIR = (
    REPO_ROOT
    / "项目资料源_selected_source_materials"
    / "AI解析精选资料包_selected_ai_analysis_extract_pack"
)
COPY_DIR = OUTPUT_DIR / "03_精选资料副本_selected_source_files"
EXTRACT_DIR = OUTPUT_DIR / "04_大表关键摘录_large_table_extracts"
VALIDATION_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis" / "11_selected_source_extract_pack"
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

README_PATH = OUTPUT_DIR / "00_精选资料包说明_readme.md"
COPY_MANIFEST_PATH = OUTPUT_DIR / "01_复制文件清单_selected_source_copy_manifest.csv"
EXTRACT_MANIFEST_PATH = OUTPUT_DIR / "02_摘录资料清单_selected_extract_manifest.csv"
TRACEABILITY_PATH = OUTPUT_DIR / "05_源资料到动作知识库追溯表_source_to_action_traceability.csv"
SKIPPED_REPORT_PATH = OUTPUT_DIR / "06_不复制文件说明_skipped_source_files_report.md"
ACTION_TRACE_PATH = KB_DIR / "07_动作知识库来源追溯说明_action_source_traceability.md"
VALIDATION_PATH = VALIDATION_DIR / "精选复制执行校验_selected_source_copy_validation.csv"
PROBE_PATH = VALIDATION_DIR / "复制候选探针_copy_candidate_probe.csv"
REPORT_PATH = LOG_DIR / "118_AI解析精选资料复制与摘录执行报告_selected_ai_analysis_extract_pack_report.md"

COPY_SIZE_LIMIT_BYTES = 10 * 1024 * 1024
TABLE_ROW_COPY_LIMIT = 10_000
MAX_EXTRACT_ROWS = 80
MAX_SCAN_LINES = 250_000
ALWAYS_SAMPLE_ROWS = 12

ALLOWED_COPY_SUFFIXES = {".csv", ".json", ".jsonl", ".md", ".txt", ".docx"}
TABLE_SUFFIXES = {".csv", ".jsonl"}
FORBIDDEN_SUFFIXES = {
    ".mp4",
    ".mov",
    ".mkv",
    ".m4v",
    ".avi",
    ".mp3",
    ".wav",
    ".aac",
    ".m4a",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".7z",
    ".rar",
}
FORBIDDEN_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "_cache",
    "_logs",
    "_state",
    "_tools",
    "site-packages",
    "frames_preview",
    "api_outputs",
    "outputs",
}
SECRET_PATTERNS = [
    re.compile(r"api[_-]?key", re.I),
    re.compile(r"secret", re.I),
    re.compile(r"token", re.I),
    re.compile(r"cookie", re.I),
    re.compile(r"\.env$", re.I),
]

SENSITIVE_TERMS = [
    "亲密",
    "情趣",
    "性",
    "性交",
    "性伴侣",
    "性器",
    "阴",
    "阴道",
    "阴茎",
    "阴蒂",
    "私密",
    "丁丁",
    "蛋蛋",
    "前列腺",
    "高潮",
    "撸",
    "插入",
    "包皮",
    "蘑菇头",
    "体位",
    "盆底",
]
SENSITIVE_RE = re.compile("|".join(re.escape(term) for term in SENSITIVE_TERMS))

KEY_FIELD_HINTS = [
    "id",
    "lesson",
    "chunk",
    "start",
    "end",
    "time",
    "source",
    "ref",
    "text",
    "transcript",
    "clean",
    "raw",
    "quote",
    "action",
    "label",
    "description",
    "body",
    "expression",
    "gaze",
    "camera",
    "slide",
    "visual",
    "focus",
    "prosody",
    "pacing",
    "bridge",
    "risk",
    "review",
    "confidence",
    "keyword",
    "term",
    "question",
    "answer",
    "response",
    "problem",
    "topic",
    "usage",
]
TEXT_VALUE_FIELDS = {
    "source_text",
    "raw_text",
    "clean_text",
    "transcript_text",
    "source_quote",
    "answer_or_response",
    "question_or_objection",
    "knowledge_point",
    "possible_value",
    "definition_or_context",
}


@dataclass
class Candidate:
    source_file_id: str
    relative_path: str
    absolute_path: Path
    usefulness_grade: str
    usefulness_type: str
    file_kind: str
    extension: str
    size_bytes: int
    recommended_usage: str
    notes: str
    row_count_if_table: str = ""
    has_sensitive_sample: bool = False
    copy_decision: str = ""
    decision_reason: str = ""
    target_path: Path | None = None


def clean_field(value: str | None) -> str:
    return (value or "").lstrip("\ufeff").strip()


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            {clean_field(key): clean_field(value) for key, value in row.items()}
            for row in reader
        ]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def short_hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]


def safe_name(candidate: Candidate, suffix: str | None = None) -> str:
    stem = Path(candidate.relative_path).stem
    ext = suffix if suffix is not None else candidate.extension
    cleaned = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", stem).strip("_")
    if len(cleaned) > 90:
        cleaned = cleaned[:90]
    return f"{candidate.source_file_id}_{short_hash_text(candidate.relative_path)}_{cleaned}{ext}"


def source_parts(candidate: Candidate) -> set[str]:
    return {part.lower() for part in Path(candidate.relative_path).parts}


def is_forbidden_source(candidate: Candidate) -> bool:
    if candidate.extension.lower() in FORBIDDEN_SUFFIXES:
        return True
    parts = source_parts(candidate)
    if parts & FORBIDDEN_PARTS:
        return True
    if candidate.absolute_path.name.startswith("._"):
        return True
    return any(pattern.search(candidate.relative_path) for pattern in SECRET_PATTERNS)


def row_count_capped(path: Path, suffix: str) -> str:
    if suffix not in TABLE_SUFFIXES:
        return ""
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
            count = 0
            if suffix == ".csv":
                for _ in csv.reader(handle):
                    count += 1
                    if count > TABLE_ROW_COPY_LIMIT + 1:
                        return f">{TABLE_ROW_COPY_LIMIT}"
                return str(max(count - 1, 0))
            for line in handle:
                if line.strip():
                    count += 1
                    if count > TABLE_ROW_COPY_LIMIT:
                        return f">{TABLE_ROW_COPY_LIMIT}"
            return str(count)
    except OSError:
        return "unreadable"


def file_has_sensitive_sample(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            sample = handle.read(256 * 1024)
    except OSError:
        return False
    return bool(SENSITIVE_RE.search(sample))


def parse_source_ids(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[;,]", value or "") if part.strip()]


def build_kb_indexes() -> dict[str, Any]:
    action_rows = read_csv_dicts(ACTION_MAPPING_PATH)
    alias_rows = read_csv_dicts(ALIAS_PATH)
    taxonomy_rows = read_csv_dicts(TAXONOMY_PATH)
    bridge_rows = read_csv_dicts(BRIDGE_PATH)

    action_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    problem_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    bridge_by_action: dict[str, dict[str, str]] = {}
    keywords: set[str] = set()

    for row in bridge_rows:
        bridge_by_action[row.get("normalized_action_id", "")] = row

    for row in action_rows:
        for field in (
            "normalized_action_id",
            "normalized_action_name_cn",
            "alias_examples",
            "speech_keyword_family",
            "target_problem_primary",
            "target_problem_secondary",
            "recommended_structure",
        ):
            for part in re.split(r"[;/,，、\s]+", row.get(field, "")):
                part = part.strip()
                if len(part) >= 2 and part not in {"pending", "review", "normal"}:
                    keywords.add(part)
        for source_id in parse_source_ids(row.get("source_file_ids", "")):
            action_by_source[source_id].append(row)

    for row in alias_rows:
        for field in ("source_alias", "normalized_action_id", "normalized_action_name_cn"):
            value = row.get(field, "").strip()
            if len(value) >= 2:
                keywords.add(value)
        for source_id in parse_source_ids(row.get("source_file_ids", "")):
            action_by_source[source_id].append(
                {
                    "normalized_action_id": row.get("normalized_action_id", ""),
                    "normalized_action_name_cn": row.get("normalized_action_name_cn", ""),
                    "target_problem_primary": "",
                    "target_problem_secondary": "",
                    "confirmed_source_basis": row.get("source_basis", ""),
                    "candidate_use_status": row.get("normalization_status", ""),
                }
            )

    for row in taxonomy_rows:
        for field in (
            "problem_category_id",
            "problem_category_name_cn",
            "source_keyword_families",
            "recommended_structure",
        ):
            for part in re.split(r"[;/,，、\s]+", row.get(field, "")):
                part = part.strip()
                if len(part) >= 2:
                    keywords.add(part)
        for source_id in parse_source_ids(row.get("source_file_ids", "")):
            problem_by_source[source_id].append(row)

    return {
        "actions": action_rows,
        "taxonomy": taxonomy_rows,
        "bridges": bridge_rows,
        "action_by_source": action_by_source,
        "problem_by_source": problem_by_source,
        "bridge_by_action": bridge_by_action,
        "keywords": sorted(keywords, key=len, reverse=True),
    }


def load_candidates() -> list[Candidate]:
    inventory_rows = read_csv_dicts(INVENTORY_PATH)
    usefulness_rows = {
        row["source_file_id"]: row for row in read_csv_dicts(USEFULNESS_PATH)
    }
    candidates: list[Candidate] = []
    for row in inventory_rows:
        grade = row.get("usefulness_grade", "")
        if grade not in {"A", "B"}:
            continue
        use_row = usefulness_rows.get(row["source_file_id"], {})
        absolute_path = Path(row["absolute_path"])
        candidate = Candidate(
            source_file_id=row["source_file_id"],
            relative_path=row["relative_path"],
            absolute_path=absolute_path,
            usefulness_grade=grade,
            usefulness_type=use_row.get("usefulness_type", row.get("usefulness_type", "")),
            file_kind=use_row.get("file_kind", row.get("file_kind", "")),
            extension=row.get("extension", "").lower(),
            size_bytes=int(row.get("size_bytes", "0") or 0),
            recommended_usage=use_row.get(
                "recommended_usage", row.get("recommended_usage", "")
            ),
            notes=use_row.get("notes", row.get("notes", "")),
        )
        candidate.row_count_if_table = row_count_capped(absolute_path, candidate.extension)
        candidate.has_sensitive_sample = file_has_sensitive_sample(absolute_path)
        candidates.append(candidate)
    return candidates


def decide_candidate(candidate: Candidate) -> None:
    if not candidate.absolute_path.exists():
        candidate.copy_decision = "skip"
        candidate.decision_reason = "源文件不存在，无法安全复制或摘录。"
        return
    if is_forbidden_source(candidate):
        candidate.copy_decision = "skip"
        candidate.decision_reason = "命中媒体/缓存/压缩包/secret/AppleDouble 禁止规则。"
        return
    if candidate.extension not in ALLOWED_COPY_SUFFIXES:
        candidate.copy_decision = "index_only"
        candidate.decision_reason = "不是本轮允许复制的文本/表格/文档解析产物。"
        return
    if candidate.extension in TABLE_SUFFIXES:
        too_many_rows = candidate.row_count_if_table.startswith(">")
        too_large = candidate.size_bytes > COPY_SIZE_LIMIT_BYTES
        sensitive_course_text = (
            candidate.has_sensitive_sample
            and candidate.file_kind == "course_text_context"
        )
        if too_many_rows or too_large or sensitive_course_text:
            candidate.copy_decision = "extract_rows"
            reasons = []
            if too_many_rows:
                reasons.append(f"行数超过 {TABLE_ROW_COPY_LIMIT}")
            if too_large:
                reasons.append("体积超过 10MB")
            if sensitive_course_text:
                reasons.append("课程文本命中敏感词，仅保留高层摘录")
            candidate.decision_reason = "；".join(reasons)
            return
        candidate.copy_decision = "copy_full"
        candidate.decision_reason = "A/B 类小体积表格，行数未超过阈值，可完整复制。"
        return
    if candidate.extension == ".md" and candidate.has_sensitive_sample:
        candidate.copy_decision = "extract_summary"
        candidate.decision_reason = "Markdown 命中敏感成人亲密关系内容，只生成高层摘要摘录。"
        return
    if candidate.size_bytes <= COPY_SIZE_LIMIT_BYTES:
        candidate.copy_decision = "copy_full"
        candidate.decision_reason = "A/B 类小体积文本资料，可完整复制。"
        return
    candidate.copy_decision = "extract_summary"
    candidate.decision_reason = "非表格文本超过 10MB，只生成摘要摘录。"


def contains_keyword(text: str, keywords: list[str]) -> bool:
    if not text:
        return False
    return any(keyword and keyword in text for keyword in keywords)


def redact_sensitive(value: Any, field_name: str = "") -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    else:
        text = str(value)
    text = text.replace("\r", " ").replace("\n", " ").strip()
    if SENSITIVE_RE.search(text):
        family_text = "/".join(classify_sensitive_families(text))
        return (
            f"[已脱敏_仅保留高层词族:{family_text}; "
            "原文细节未复制; review_gate=professional_review_required]"
        )
    limit = 240 if field_name in TEXT_VALUE_FIELDS else 420
    if len(text) > limit:
        return text[:limit] + "...[truncated]"
    return text


def classify_sensitive_families(text: str) -> list[str]:
    families: list[str] = []
    if any(term in text for term in ("亲密", "情趣", "性交", "性伴侣", "体位")):
        families.append("adult_intimacy_risk")
    if any(term in text for term in ("丁丁", "蛋蛋", "阴", "阴道", "阴茎", "阴蒂", "包皮", "蘑菇头")):
        families.append("adult_body_part_risk")
    if any(term in text for term in ("前列腺", "盆底", "私密")):
        families.append("pelvic_floor_or_private_health_risk")
    if any(term in text for term in ("高潮", "性器")):
        families.append("sexual_response_risk")
    if any(term in text for term in ("撸", "插入", "按摩")):
        families.append("sensitive_operation_risk")
    if not families:
        families.append("sensitive_adult_or_health_risk")
    return families


def selected_columns(fieldnames: Iterable[str]) -> list[str]:
    fields = list(fieldnames)
    chosen: list[str] = []
    for field in fields:
        lower = field.lower()
        if any(hint in lower for hint in KEY_FIELD_HINTS):
            chosen.append(field)
    if not chosen:
        chosen = fields[:12]
    for field in fields[:6]:
        if field not in chosen:
            chosen.append(field)
    return chosen[:28]


def selected_keys_from_json(item: dict[str, Any]) -> list[str]:
    keys = selected_columns(item.keys())
    if not keys:
        keys = list(item.keys())[:20]
    return keys


def compact_ranges(numbers: list[int]) -> str:
    if not numbers:
        return ""
    numbers = sorted(set(numbers))
    ranges: list[str] = []
    start = prev = numbers[0]
    for number in numbers[1:]:
        if number == prev + 1:
            prev = number
            continue
        ranges.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = number
    ranges.append(str(start) if start == prev else f"{start}-{prev}")
    return ";".join(ranges)


def copy_full(candidate: Candidate) -> dict[str, Any]:
    target = COPY_DIR / safe_name(candidate)
    target.parent.mkdir(parents=True, exist_ok=True)
    source_sha256 = sha256_file(candidate.absolute_path)
    normalization = "byte_identical"
    if candidate.extension in {".csv", ".json", ".jsonl", ".md", ".txt"}:
        text = candidate.absolute_path.read_text(encoding="utf-8-sig", errors="replace")
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        with target.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(normalized)
        normalization = "line_endings_lf"
    else:
        shutil.copyfile(candidate.absolute_path, target)
    candidate.target_path = target
    return {
        "source_sha256": source_sha256,
        "target_sha256": sha256_file(target),
        "target_path": target,
        "target_normalization": normalization,
    }


def normalize_extract_row(
    source_file_id: str,
    source_path: str,
    line_number: int,
    row: dict[str, Any],
    columns: list[str],
) -> dict[str, str]:
    output = {
        "_source_file_id": source_file_id,
        "_source_line_number": str(line_number),
        "_source_path": source_path,
    }
    for column in columns:
        output[column] = redact_sensitive(row.get(column, ""), column)
    return output


def extract_csv(candidate: Candidate, keywords: list[str]) -> tuple[Path, list[int], list[str], int, str]:
    target = EXTRACT_DIR / safe_name(candidate, "_extract.csv")
    target.parent.mkdir(parents=True, exist_ok=True)
    selected_rows: list[tuple[int, dict[str, str]]] = []
    scanned = 0
    columns: list[str] = []
    stop_reason = "scan_completed"

    with candidate.absolute_path.open(
        "r", encoding="utf-8-sig", errors="replace", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        columns = selected_columns(reader.fieldnames or [])
        for line_number, row in enumerate(reader, start=2):
            scanned = line_number - 1
            row_text = " ".join(row.get(field, "") for field in columns)
            should_select = len(selected_rows) < ALWAYS_SAMPLE_ROWS or contains_keyword(
                row_text, keywords
            )
            if should_select:
                selected_rows.append((line_number, row))
            if len(selected_rows) >= MAX_EXTRACT_ROWS and scanned >= ALWAYS_SAMPLE_ROWS:
                stop_reason = "selected_row_limit_reached"
                break
            if scanned >= MAX_SCAN_LINES:
                stop_reason = f"scan_capped_at_{MAX_SCAN_LINES}_rows"
                break

    output_fields = ["_source_file_id", "_source_line_number", "_source_path"] + columns
    output_rows = [
        normalize_extract_row(
            candidate.source_file_id,
            candidate.relative_path,
            line_number,
            row,
            columns,
        )
        for line_number, row in selected_rows
    ]
    write_csv(target, output_rows, output_fields)
    return target, [line_number for line_number, _ in selected_rows], output_fields, scanned, stop_reason


def extract_jsonl(candidate: Candidate, keywords: list[str]) -> tuple[Path, list[int], list[str], int, str]:
    target = EXTRACT_DIR / safe_name(candidate, "_extract.jsonl")
    target.parent.mkdir(parents=True, exist_ok=True)
    selected: list[tuple[int, dict[str, Any], list[str]]] = []
    scanned = 0
    columns_seen: list[str] = []
    stop_reason = "scan_completed"

    with candidate.absolute_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            scanned = line_number
            stripped = line.strip()
            if not stripped:
                continue
            should_select = len(selected) < ALWAYS_SAMPLE_ROWS or contains_keyword(
                stripped, keywords
            )
            if should_select:
                try:
                    item = json.loads(stripped)
                except json.JSONDecodeError:
                    item = {"raw_line": stripped}
                if not isinstance(item, dict):
                    item = {"raw_value": item}
                columns = selected_keys_from_json(item)
                for column in columns:
                    if column not in columns_seen:
                        columns_seen.append(column)
                selected.append((line_number, item, columns))
            if len(selected) >= MAX_EXTRACT_ROWS and scanned >= ALWAYS_SAMPLE_ROWS:
                stop_reason = "selected_row_limit_reached"
                break
            if scanned >= MAX_SCAN_LINES:
                stop_reason = f"scan_capped_at_{MAX_SCAN_LINES}_lines"
                break

    with target.open("w", encoding="utf-8") as handle:
        for line_number, item, columns in selected:
            row = normalize_extract_row(
                candidate.source_file_id,
                candidate.relative_path,
                line_number,
                item,
                columns,
            )
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    output_fields = ["_source_file_id", "_source_line_number", "_source_path"] + columns_seen
    return target, [line_number for line_number, _, _ in selected], output_fields, scanned, stop_reason


def extract_markdown_summary(candidate: Candidate) -> tuple[Path, list[int], list[str], int, str]:
    target = EXTRACT_DIR / safe_name(candidate, "_summary.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    selected: list[tuple[int, str]] = []
    scanned = 0
    with candidate.absolute_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            scanned = line_number
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#") or len(selected) < ALWAYS_SAMPLE_ROWS:
                selected.append((line_number, stripped))
            elif any(key in stripped for key in ("直播", "桥接", "review", "复核", "风险")):
                selected.append((line_number, stripped))
            if len(selected) >= MAX_EXTRACT_ROWS:
                break

    with target.open("w", encoding="utf-8") as handle:
        handle.write(f"# {candidate.source_file_id} 高层摘要摘录\n\n")
        handle.write(f"- source_path: `{candidate.relative_path}`\n")
        handle.write("- sensitive_handling: 原文命中敏感成人亲密关系词，本摘录只保留高层词族、风险闸门和来源行号。\n\n")
        handle.write("| source_line | redacted_summary |\n")
        handle.write("|---:|---|\n")
        for line_number, text in selected:
            handle.write(f"| {line_number} | {redact_sensitive(text)} |\n")
    return target, [line_number for line_number, _ in selected], [
        "source_line",
        "redacted_summary",
    ], scanned, "summary_selected"


def extract_candidate(candidate: Candidate, keywords: list[str]) -> dict[str, Any]:
    if candidate.extension == ".csv":
        target, line_numbers, columns, scanned, stop_reason = extract_csv(candidate, keywords)
    elif candidate.extension == ".jsonl":
        target, line_numbers, columns, scanned, stop_reason = extract_jsonl(candidate, keywords)
    else:
        target, line_numbers, columns, scanned, stop_reason = extract_markdown_summary(candidate)
    candidate.target_path = target
    return {
        "target_path": target,
        "line_numbers": line_numbers,
        "columns": columns,
        "scanned_rows": scanned,
        "stop_reason": stop_reason,
    }


def rel_repo(path: Path | None) -> str:
    if path is None:
        return ""
    return path.relative_to(REPO_ROOT).as_posix()


def why_needed(candidate: Candidate, kb_indexes: dict[str, Any]) -> str:
    action_count = len(kb_indexes["action_by_source"].get(candidate.source_file_id, []))
    problem_count = len(kb_indexes["problem_by_source"].get(candidate.source_file_id, []))
    basis = []
    if action_count:
        basis.append(f"被动作知识库引用 {action_count} 次")
    if problem_count:
        basis.append(f"被问题分类引用 {problem_count} 次")
    if not basis:
        basis.append(candidate.recommended_usage)
    return "；".join(basis)


def source_action_ids(candidate: Candidate, kb_indexes: dict[str, Any]) -> str:
    ids = {
        row.get("normalized_action_id", "")
        for row in kb_indexes["action_by_source"].get(candidate.source_file_id, [])
        if row.get("normalized_action_id", "")
    }
    return ";".join(sorted(ids))


def source_problem_ids(candidate: Candidate, kb_indexes: dict[str, Any]) -> str:
    ids = set()
    for row in kb_indexes["action_by_source"].get(candidate.source_file_id, []):
        for field in ("target_problem_primary", "target_problem_secondary"):
            if row.get(field, ""):
                ids.add(row[field])
    for row in kb_indexes["problem_by_source"].get(candidate.source_file_id, []):
        if row.get("problem_category_id", ""):
            ids.add(row["problem_category_id"])
    return ";".join(sorted(ids))


def build_traceability(candidates: list[Candidate], kb_indexes: dict[str, Any]) -> list[dict[str, str]]:
    candidate_by_id = {candidate.source_file_id: candidate for candidate in candidates}
    rows: list[dict[str, str]] = []
    trace_index = 1
    for source_id, actions in sorted(kb_indexes["action_by_source"].items()):
        candidate = candidate_by_id.get(source_id)
        if candidate is None:
            continue
        copied_or_extracted_path = rel_repo(candidate.target_path)
        for action in actions:
            action_id = action.get("normalized_action_id", "")
            bridge = kb_indexes["bridge_by_action"].get(action_id, {})
            problem_ids = [
                action.get("target_problem_primary", ""),
                action.get("target_problem_secondary", ""),
            ]
            problem_id = ";".join(sorted({p for p in problem_ids if p}))
            rows.append(
                {
                    "trace_id": f"TRACE{trace_index:04d}",
                    "source_file_id": source_id,
                    "source_path": candidate.relative_path,
                    "copied_or_extracted_path": copied_or_extracted_path,
                    "action_id": action_id,
                    "problem_id": problem_id,
                    "bridge_id": bridge.get("bridge_id", ""),
                    "evidence_type": candidate.copy_decision,
                    "evidence_summary": redact_sensitive(
                        action.get("confirmed_source_basis", "")
                        or action.get("candidate_use_status", "")
                        or why_needed(candidate, kb_indexes)
                    ),
                    "review_gate": bridge.get("manual_review_items", "")
                    or action.get("risk_review_items", "")
                    or "pending_user_review",
                }
            )
            trace_index += 1
    for source_id, problems in sorted(kb_indexes["problem_by_source"].items()):
        candidate = candidate_by_id.get(source_id)
        if candidate is None:
            continue
        for problem in problems:
            rows.append(
                {
                    "trace_id": f"TRACE{trace_index:04d}",
                    "source_file_id": source_id,
                    "source_path": candidate.relative_path,
                    "copied_or_extracted_path": rel_repo(candidate.target_path),
                    "action_id": "",
                    "problem_id": problem.get("problem_category_id", ""),
                    "bridge_id": "",
                    "evidence_type": candidate.copy_decision,
                    "evidence_summary": redact_sensitive(
                        problem.get("definition", "")
                        or problem.get("source_keyword_families", "")
                    ),
                    "review_gate": problem.get("risk_gate", "")
                    or "pending_user_review",
                }
            )
            trace_index += 1
    return rows


def build_readme(candidates: list[Candidate], copy_rows: list[dict[str, Any]], extract_rows: list[dict[str, Any]]) -> None:
    decision_counts = Counter(candidate.copy_decision for candidate in candidates)
    README_PATH.parent.mkdir(parents=True, exist_ok=True)
    README_PATH.write_text(
        "\n".join(
            [
                "# AI解析精选资料包说明",
                "",
                "状态：`selected_extract_pack_generated_pending_user_review`",
                "",
                "## 已确认",
                "",
                f"- 当前实际源目录：`{SOURCE_ROOT}`。",
                f"- 用户补充的 `WD_BLACK-AI 解析` 口径已核对；磁盘上 `/Volumes/WD_BLACK/AI 解析` 不存在，本轮按实际存在路径 `{SOURCE_ROOT}` 只读执行。",
                "- 本包不是完整 `AI解析` 目录，也不是移动、删除、重命名原目录。",
                "- 本包只保存当前剪辑项目后续判断动作、问题、剪辑结构需要的精选副本、关键摘录和来源追溯。",
                "- 完整复制的文本副本会统一为 LF 行尾以通过 Git 校验；清单中分别记录 `source_sha256`、`target_sha256` 和 `target_normalization`。",
                "",
                "## 处理结果",
                "",
                f"- A/B 候选文件：{len(candidates)} 个。",
                f"- 完整复制：{decision_counts.get('copy_full', 0)} 个。",
                f"- 行级摘录：{decision_counts.get('extract_rows', 0)} 个。",
                f"- 摘要摘录：{decision_counts.get('extract_summary', 0)} 个。",
                f"- 只索引/跳过：{decision_counts.get('index_only', 0) + decision_counts.get('skip', 0)} 个。",
                "",
                "## 后续 Codex 使用方式",
                "",
                "1. 先读 `01_复制文件清单_selected_source_copy_manifest.csv` 判断哪些源文件已完整复制。",
                "2. 再读 `02_摘录资料清单_selected_extract_manifest.csv` 和 `04_大表关键摘录_large_table_extracts/` 获取大表关键字段、来源行号和脱敏摘录。",
                "3. 用 `05_源资料到动作知识库追溯表_source_to_action_traceability.csv` 连接动作、问题、剪辑结构桥接关系。",
                "4. 对任何涉及视觉、健康效果、成人亲密关系、业务承诺的内容，保持 `pending_user_review` 或对应复核闸门。",
                "",
                "## 禁止外推",
                "",
                "- 本包不代表健康效果成立。",
                "- 本包不代表动作专业性通过。",
                "- 本包不代表审美、人感或业务通过。",
                "- 本包不代表可以直接进入直播候选片段筛选。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def build_skipped_report(candidates: list[Candidate]) -> None:
    inventory_rows = read_csv_dicts(INVENTORY_PATH)
    grade_counts = Counter(row.get("usefulness_grade", "") for row in inventory_rows)
    kind_counts = Counter(row.get("file_kind", "") for row in inventory_rows)
    decision_counts = Counter(candidate.copy_decision for candidate in candidates)
    lines = [
        "# 不复制文件说明",
        "",
        "状态：`skipped_files_index_generated`",
        "",
        "## 总体分级",
        "",
        "| grade | count |",
        "|---|---:|",
    ]
    for grade, count in sorted(grade_counts.items()):
        lines.append(f"| `{grade}` | {count} |")
    lines.extend(
        [
            "",
            "## 文件类型 Top 12",
            "",
            "| file_kind | count |",
            "|---|---:|",
        ]
    )
    for kind, count in kind_counts.most_common(12):
        lines.append(f"| `{kind}` | {count} |")
    lines.extend(
        [
            "",
            "## A/B 候选处理决策",
            "",
            "| decision | count |",
            "|---|---:|",
        ]
    )
    for decision, count in sorted(decision_counts.items()):
        lines.append(f"| `{decision}` | {count} |")
    lines.extend(
        [
            "",
            "## 跳过规则",
            "",
            "- C 类只在上一轮 inventory/usefulness 表中保留索引，原则上不复制。",
            "- D 类为重复、缓存、运行环境、AppleDouble、不可用文件，不复制。",
            "- 媒体、图片、音频、zip、cache、`.env`、secret、API 原始输出不复制。",
            "- 敏感成人亲密关系内容不复制具体操作细节，只在摘录中保留高层词族、来源行号和复核闸门。",
            "",
            "## A/B 未完整复制明细",
            "",
            "| source_file_id | grade | decision | relative_path | reason |",
            "|---|---|---|---|---|",
        ]
    )
    for candidate in candidates:
        if candidate.copy_decision != "copy_full":
            lines.append(
                "| {source_file_id} | {grade} | `{decision}` | `{path}` | {reason} |".format(
                    source_file_id=candidate.source_file_id,
                    grade=candidate.usefulness_grade,
                    decision=candidate.copy_decision,
                    path=candidate.relative_path,
                    reason=candidate.decision_reason.replace("|", "/"),
                )
            )
    lines.append("")
    SKIPPED_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_action_trace_doc(copy_count: int, extract_count: int, trace_count: int) -> None:
    ACTION_TRACE_PATH.write_text(
        "\n".join(
            [
                "# 动作知识库来源追溯说明",
                "",
                "状态：`action_source_traceability_added_pending_user_review`",
                "",
                "## 已确认",
                "",
                f"- 精选资料包目录：`{rel_repo(OUTPUT_DIR)}`。",
                f"- 完整复制清单：`{rel_repo(COPY_MANIFEST_PATH)}`，记录 {copy_count} 个完整副本。",
                f"- 摘录清单：`{rel_repo(EXTRACT_MANIFEST_PATH)}`，记录 {extract_count} 个摘录产物。",
                f"- 源资料到动作知识库追溯表：`{rel_repo(TRACEABILITY_PATH)}`，记录 {trace_count} 条追溯关系。",
                "",
                "## 使用顺序",
                "",
                "1. 用动作知识库 01-04 表确定 `normalized_action_id`、`problem_id`、`bridge_id`。",
                "2. 到 `05_源资料到动作知识库追溯表_source_to_action_traceability.csv` 找对应 `source_file_id`。",
                "3. 如果 `copied_or_extracted_path` 指向 `03_精选资料副本_selected_source_files/`，可读取完整副本。",
                "4. 如果指向 `04_大表关键摘录_large_table_extracts/`，只能读取摘录字段和来源行号，不得外推全量源内容。",
                "",
                "## 复核闸门",
                "",
                "- `visual_review_required`：需要画面、动作、说话同步复核。",
                "- `professional_review_required`：涉及动作专业性或健康风险，不写已确认。",
                "- `customer_review_if_used_in_live_script`：进入直播话术前需要客户确认。",
                "- `pending_user_review`：本轮技术落库完成后仍需用户人审。",
                "",
                "## 禁止外推",
                "",
                "- 追溯成立只说明来源可查，不说明动作真实可见。",
                "- 文本命中只说明候选关系，不说明视频画面连续或说话连续。",
                "- 涉及敏感成人亲密关系内容时，只保留高层词族和风险闸门，不复制可照做细节。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def scan_output_for_forbidden_files() -> list[str]:
    violations: list[str] = []
    if not OUTPUT_DIR.exists():
        return ["output_dir_missing"]
    for path in OUTPUT_DIR.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(OUTPUT_DIR).as_posix()
        suffix = path.suffix.lower()
        if path.name.startswith("._"):
            violations.append(rel)
        if suffix in FORBIDDEN_SUFFIXES:
            violations.append(rel)
        if any(part in FORBIDDEN_PARTS for part in path.parts):
            violations.append(rel)
        if any(pattern.search(path.name) for pattern in SECRET_PATTERNS):
            violations.append(rel)
    return sorted(set(violations))


def remove_appledouble_sidecars(*roots: Path) -> int:
    removed = 0
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("._*"):
            if path.is_file():
                path.unlink()
                removed += 1
    return removed


def validate_outputs(
    copy_rows: list[dict[str, Any]],
    extract_rows: list[dict[str, Any]],
    trace_rows: list[dict[str, str]],
    source_stat_before: tuple[int, int],
    source_stat_after: tuple[int, int],
) -> list[dict[str, str]]:
    forbidden_files = scan_output_for_forbidden_files()
    output_size = sum(path.stat().st_size for path in OUTPUT_DIR.rglob("*") if path.is_file())
    validations = [
        {
            "check_id": "VAL001",
            "check_item": "source_dir_exists",
            "status": "passed" if SOURCE_ROOT.exists() else "failed",
            "evidence": str(SOURCE_ROOT),
        },
        {
            "check_id": "VAL002",
            "check_item": "source_dir_not_modified_by_script",
            "status": "passed" if source_stat_before == source_stat_after else "failed",
            "evidence": f"before={source_stat_before}; after={source_stat_after}",
        },
        {
            "check_id": "VAL003",
            "check_item": "no_forbidden_output_files",
            "status": "passed" if not forbidden_files else "failed",
            "evidence": ";".join(forbidden_files) or "no media/cache/archive/env/secret files found",
        },
        {
            "check_id": "VAL004",
            "check_item": "copy_manifest_has_hashes",
            "status": "passed"
            if all(row.get("source_sha256") and row.get("target_sha256") for row in copy_rows)
            else "failed",
            "evidence": f"copy_rows={len(copy_rows)}",
        },
        {
            "check_id": "VAL005",
            "check_item": "extract_manifest_has_source_ranges",
            "status": "passed"
            if all(row.get("source_row_range") for row in extract_rows)
            else "failed",
            "evidence": f"extract_rows={len(extract_rows)}",
        },
        {
            "check_id": "VAL006",
            "check_item": "traceability_generated",
            "status": "passed" if trace_rows else "failed",
            "evidence": f"trace_rows={len(trace_rows)}",
        },
        {
            "check_id": "VAL007",
            "check_item": "output_size_not_abnormally_large",
            "status": "passed" if output_size < 100 * 1024 * 1024 else "failed",
            "evidence": f"output_size_bytes={output_size}",
        },
        {
            "check_id": "VAL008",
            "check_item": "space_path_probe",
            "status": "passed" if SOURCE_ROOT.exists() and not SOURCE_ROOT_WITH_SPACE.exists() else "failed",
            "evidence": f"actual={SOURCE_ROOT}; space_variant_exists={SOURCE_ROOT_WITH_SPACE.exists()}",
        },
    ]
    return validations


def build_report(
    candidates: list[Candidate],
    copy_rows: list[dict[str, Any]],
    extract_rows: list[dict[str, Any]],
    trace_rows: list[dict[str, str]],
    validations: list[dict[str, str]],
    source_file_count: int,
    source_dir_size_text: str,
) -> None:
    decision_counts = Counter(candidate.copy_decision for candidate in candidates)
    validation_status = "passed" if all(row["status"] == "passed" for row in validations) else "failed"
    REPORT_PATH.write_text(
        "\n".join(
            [
                "# AI解析精选资料复制与摘录执行报告",
                "",
                "状态：`selected_ai_analysis_extract_pack_generated_pending_user_review`",
                f"生成时间：{dt.datetime.now().isoformat(timespec='seconds')}",
                "",
                "## 1. 本轮目标",
                "",
                "从外部 `AI解析` 源目录中复制/摘录当前剪辑项目后续需要的课程动作资料，形成可追溯、可复用、可给后续 Codex 判断使用的精选资料包。",
                "",
                "## 2. 已确认边界",
                "",
                f"- 仓库：`{REPO_ROOT}`",
                f"- 源目录实际路径：`{SOURCE_ROOT}`",
                f"- `/Volumes/WD_BLACK/AI 解析` 是否存在：`{SOURCE_ROOT_WITH_SPACE.exists()}`",
                "- 源目录处理方式：只读，不移动、不删除、不重命名、不覆盖。",
                "- 本轮不复制媒体、缓存、zip、secret、API 原始输出。",
                "- 完整复制文本副本统一为 LF 行尾，源/目标 hash 分开记录。",
                "- 本轮不写健康效果成立、动作专业性通过、审美通过或业务通过。",
                "",
                "## 3. 复制候选探针",
                "",
                f"- 源目录文件总数：{source_file_count}",
                f"- 源目录体积：{source_dir_size_text}",
                f"- A/B 候选：{len(candidates)}",
                f"- A 类：{sum(1 for c in candidates if c.usefulness_grade == 'A')}",
                f"- B 类：{sum(1 for c in candidates if c.usefulness_grade == 'B')}",
                f"- 完整复制：{decision_counts.get('copy_full', 0)}",
                f"- 行级摘录：{decision_counts.get('extract_rows', 0)}",
                f"- 摘要摘录：{decision_counts.get('extract_summary', 0)}",
                f"- 只索引：{decision_counts.get('index_only', 0)}",
                f"- 跳过：{decision_counts.get('skip', 0)}",
                "",
                "## 4. 输出文件",
                "",
                f"- `{rel_repo(README_PATH)}`",
                f"- `{rel_repo(COPY_MANIFEST_PATH)}`",
                f"- `{rel_repo(EXTRACT_MANIFEST_PATH)}`",
                f"- `{rel_repo(COPY_DIR)}/`",
                f"- `{rel_repo(EXTRACT_DIR)}/`",
                f"- `{rel_repo(TRACEABILITY_PATH)}`",
                f"- `{rel_repo(SKIPPED_REPORT_PATH)}`",
                f"- `{rel_repo(ACTION_TRACE_PATH)}`",
                f"- `{rel_repo(VALIDATION_PATH)}`",
                f"- `{rel_repo(PROBE_PATH)}`",
                "",
                "## 5. 校验摘要",
                "",
                f"- validation_status：`{validation_status}`",
                f"- copy_manifest_rows：{len(copy_rows)}",
                f"- extract_manifest_rows：{len(extract_rows)}",
                f"- traceability_rows：{len(trace_rows)}",
                "",
                "| check_id | check_item | status | evidence |",
                "|---|---|---|---|",
                *[
                    f"| {row['check_id']} | {row['check_item']} | `{row['status']}` | {row['evidence'].replace('|', '/')} |"
                    for row in validations
                ],
                "",
                "## 6. 待用户人审",
                "",
                "- 精选副本是否足够后续 Codex 使用：`待验证`。",
                "- 敏感主题是否允许进入直播筛选：`待验证`。",
                "- 视觉、说话连续性、动作专业性、业务承诺：`待验证`。",
                "",
                "## 7. commit / push",
                "",
                "- 本报告由脚本生成；最终 commit、push、remote HEAD readback 以 Codex 本轮最终回报为准。",
                "",
            ]
        ),
        encoding="utf-8",
    )


def source_stat() -> tuple[int, int]:
    stat = SOURCE_ROOT.stat()
    return int(stat.st_mtime), int(stat.st_size)


def count_source_files() -> int:
    return sum(1 for path in SOURCE_ROOT.rglob("*") if path.is_file())


def source_dir_size_text() -> str:
    total = 0
    for path in SOURCE_ROOT.rglob("*"):
        if path.is_file():
            try:
                total += path.stat().st_size
            except OSError:
                continue
    return f"{total / (1024 ** 3):.2f}GB"


def main() -> None:
    required = [
        INVENTORY_PATH,
        USEFULNESS_PATH,
        ACTION_MAPPING_PATH,
        ALIAS_PATH,
        TAXONOMY_PATH,
        BRIDGE_PATH,
        RULES_PATH,
        SCREENING_PATH,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"blocked_missing_required_inputs: {missing}")
    if not SOURCE_ROOT.exists():
        raise SystemExit(f"blocked_missing_source_dir: {SOURCE_ROOT}")

    for directory in (OUTPUT_DIR, COPY_DIR, EXTRACT_DIR, VALIDATION_DIR, KB_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    source_before = source_stat()
    kb_indexes = build_kb_indexes()
    candidates = load_candidates()
    for candidate in candidates:
        decide_candidate(candidate)

    copy_rows: list[dict[str, Any]] = []
    extract_rows: list[dict[str, Any]] = []
    probe_rows: list[dict[str, Any]] = []

    for candidate in candidates:
        probe_rows.append(
            {
                "source_file_id": candidate.source_file_id,
                "source_path": candidate.relative_path,
                "usefulness_grade": candidate.usefulness_grade,
                "source_role": candidate.usefulness_type,
                "file_size_mb": f"{candidate.size_bytes / (1024 * 1024):.3f}",
                "row_count_if_table": candidate.row_count_if_table,
                "has_sensitive_sample": "yes" if candidate.has_sensitive_sample else "no",
                "copy_decision": candidate.copy_decision,
                "decision_reason": candidate.decision_reason,
            }
        )
        if candidate.copy_decision == "copy_full":
            result = copy_full(candidate)
            copy_rows.append(
                {
                    "copy_id": f"COPY{len(copy_rows) + 1:04d}",
                    "source_file_id": candidate.source_file_id,
                    "source_path": candidate.relative_path,
                    "target_path": rel_repo(result["target_path"]),
                    "copy_mode": "copy_full",
                    "source_sha256": result["source_sha256"],
                    "target_sha256": result["target_sha256"],
                    "target_normalization": result["target_normalization"],
                    "file_size_kb": f"{candidate.size_bytes / 1024:.2f}",
                    "why_needed": why_needed(candidate, kb_indexes),
                    "used_by_action_ids": source_action_ids(candidate, kb_indexes),
                    "used_by_problem_ids": source_problem_ids(candidate, kb_indexes),
                    "review_status": "pending_user_review",
                }
            )
        elif candidate.copy_decision in {"extract_rows", "extract_summary"}:
            result = extract_candidate(candidate, kb_indexes["keywords"])
            extract_rows.append(
                {
                    "extract_id": f"EXTRACT{len(extract_rows) + 1:04d}",
                    "source_file_id": candidate.source_file_id,
                    "source_path": candidate.relative_path,
                    "extract_path": rel_repo(result["target_path"]),
                    "extract_mode": candidate.copy_decision,
                    "source_row_range": compact_ranges(result["line_numbers"]),
                    "selected_columns": ";".join(result["columns"]),
                    "row_count": str(len(result["line_numbers"])),
                    "why_extracted": f"{candidate.decision_reason}；{why_needed(candidate, kb_indexes)}",
                    "review_status": "pending_user_review",
                    "scanned_rows_or_lines": str(result["scanned_rows"]),
                    "extract_stop_reason": result["stop_reason"],
                    "sensitive_handling": "redacted_high_level_only"
                    if candidate.has_sensitive_sample
                    else "not_detected_in_sample",
                }
            )

    trace_rows = build_traceability(candidates, kb_indexes)
    source_after = source_stat()

    write_csv(
        PROBE_PATH,
        probe_rows,
        [
            "source_file_id",
            "source_path",
            "usefulness_grade",
            "source_role",
            "file_size_mb",
            "row_count_if_table",
            "has_sensitive_sample",
            "copy_decision",
            "decision_reason",
        ],
    )
    write_csv(
        COPY_MANIFEST_PATH,
        copy_rows,
        [
            "copy_id",
            "source_file_id",
            "source_path",
            "target_path",
            "copy_mode",
            "source_sha256",
            "target_sha256",
            "target_normalization",
            "file_size_kb",
            "why_needed",
            "used_by_action_ids",
            "used_by_problem_ids",
            "review_status",
        ],
    )
    write_csv(
        EXTRACT_MANIFEST_PATH,
        extract_rows,
        [
            "extract_id",
            "source_file_id",
            "source_path",
            "extract_path",
            "extract_mode",
            "source_row_range",
            "selected_columns",
            "row_count",
            "why_extracted",
            "review_status",
            "scanned_rows_or_lines",
            "extract_stop_reason",
            "sensitive_handling",
        ],
    )
    write_csv(
        TRACEABILITY_PATH,
        trace_rows,
        [
            "trace_id",
            "source_file_id",
            "source_path",
            "copied_or_extracted_path",
            "action_id",
            "problem_id",
            "bridge_id",
            "evidence_type",
            "evidence_summary",
            "review_gate",
        ],
    )
    build_readme(candidates, copy_rows, extract_rows)
    build_skipped_report(candidates)
    build_action_trace_doc(len(copy_rows), len(extract_rows), len(trace_rows))

    removed_sidecars = remove_appledouble_sidecars(OUTPUT_DIR, VALIDATION_DIR)
    validations = validate_outputs(copy_rows, extract_rows, trace_rows, source_before, source_after)
    if removed_sidecars:
        validations.append(
            {
                "check_id": "VAL009",
                "check_item": "appledouble_sidecars_removed",
                "status": "passed",
                "evidence": f"removed_sidecars={removed_sidecars}",
            }
        )
    write_csv(VALIDATION_PATH, validations, ["check_id", "check_item", "status", "evidence"])
    build_report(
        candidates,
        copy_rows,
        extract_rows,
        trace_rows,
        validations,
        count_source_files(),
        source_dir_size_text(),
    )
    remove_appledouble_sidecars(OUTPUT_DIR, VALIDATION_DIR)

    failed = [row for row in validations if row["status"] != "passed"]
    print(
        json.dumps(
            {
                "status": "generated" if not failed else "generated_with_validation_failures",
                "candidates": len(candidates),
                "copy_rows": len(copy_rows),
                "extract_rows": len(extract_rows),
                "trace_rows": len(trace_rows),
                "validation_failed": failed,
                "output_dir": rel_repo(OUTPUT_DIR),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
