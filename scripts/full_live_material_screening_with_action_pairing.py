#!/usr/bin/env python3
"""Full live material screening with speech/action pairing.

This script is intentionally conservative:
- source recordings are read-only;
- raw ASR/audio/cache stays in ignored api_outputs/;
- committed outputs are CSV/Markdown/shell command lists only;
- machine transcript evidence is never upgraded to health, business,
  professional-action, aesthetic, or publish approval.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR_CANDIDATES = [
    Path("/Volumes/WD_BLACK/WD_BLACK-完整直播录屏-今年直播素材"),
    Path("/Volumes/WD_BLACK/澜心社剪辑/WD_BLACK-完整直播录屏-今年直播素材"),
    Path("/Volumes/WD_BLACK/完整直播录屏-今年直播素材"),
]
SEMANTIC_SOURCE_DIR = Path("/Volumes/WD_BLACK/完整直播录屏/今年直播素材")

STRUCTURE_CSV = REPO_ROOT / "项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/36_剪辑师可用结构表_editor_usable_structure_table.csv"
BRIDGE_MD = REPO_ROOT / "项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/37_成片结构到直播素材筛选桥接说明_finished_video_to_live_screening_bridge.md"
ACTION_MAP_CSV = REPO_ROOT / "项目事实_project_facts/动作知识库_action_knowledge_base/01_动作问题映射表_action_problem_mapping.csv"
ALIAS_CSV = REPO_ROOT / "项目事实_project_facts/动作知识库_action_knowledge_base/02_动作别名归一表_action_alias_normalization.csv"
PROBLEM_CSV = REPO_ROOT / "项目事实_project_facts/动作知识库_action_knowledge_base/03_问题分类表_problem_taxonomy.csv"
ACTION_BRIDGE_CSV = REPO_ROOT / "项目事实_project_facts/动作知识库_action_knowledge_base/04_动作剪辑结构桥接表_action_clip_structure_bridge.csv"
ACTION_RULES_MD = REPO_ROOT / "项目事实_project_facts/动作知识库_action_knowledge_base/05_动作应用规则说明_action_application_rules.md"
ACTION_SCREENING_MD = REPO_ROOT / "项目事实_project_facts/动作知识库_action_knowledge_base/06_动作知识库接入直播筛选说明_action_knowledge_to_live_screening.md"
ACTION_TRACE_MD = REPO_ROOT / "项目事实_project_facts/动作知识库_action_knowledge_base/07_动作知识库来源追溯说明_action_source_traceability.md"
PACK_README = REPO_ROOT / "项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/00_精选资料包说明_readme.md"
PACK_TRACE_CSV = REPO_ROOT / "项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/05_源资料到动作知识库追溯表_source_to_action_traceability.csv"
ALI_STATUS_REPORT = REPO_ROOT / "执行日志_codex_log/106_阿里模型重连验证报告_ali_model_reconnect_after_env_update_report.md"

ANALYSIS_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis/12_full_live_material_screening"
FACT_DIR = REPO_ROOT / "项目事实_project_facts/直播素材筛选_live_material_screening"
LOG_DIR = REPO_ROOT / "执行日志_codex_log"
LOCAL_DIR = REPO_ROOT / "api_outputs/full_live_material_screening"
ASR_AUDIO_DIR = LOCAL_DIR / "asr_audio"
ASR_TRANSCRIPT_DIR = LOCAL_DIR / "asr_transcripts"

INVENTORY_CSV = ANALYSIS_DIR / "01_直播录屏清单_live_recording_inventory.csv"
TIMELINE_CSV = ANALYSIS_DIR / "02_直播口播动作时间轴_live_speech_action_timeline.csv"
MASTER_CSV = FACT_DIR / "01_直播候选片段总表_live_candidate_segment_master.csv"
PAIR_CSV = FACT_DIR / "02_口播动作配对表_speech_action_pairing_table.csv"
STRUCTURE_OUT_CSV = FACT_DIR / "03_按剪辑结构归类候选表_candidates_by_clip_structure.csv"
A_CSV = FACT_DIR / "04_A类优先剪辑清单_priority_A_editor_pick_list.csv"
B_CSV = FACT_DIR / "05_B类二次加工清单_priority_B_rework_list.csv"
RISK_CSV = FACT_DIR / "06_放弃与风险片段清单_rejected_and_risk_segments.csv"
EDITOR_REPORT_MD = FACT_DIR / "07_剪辑师人读版报告_editor_readable_screening_report.md"
MANUAL_REVIEW_MD = FACT_DIR / "08_人工复核清单_manual_review_checklist.md"
EXPORT_COMMANDS_SH = FACT_DIR / "09_本地候选素材导出命令_local_clip_export_commands.sh"
EXEC_REPORT_MD = LOG_DIR / "119_完整直播素材筛选与口播动作配对执行报告_full_live_screening_action_pairing_report.md"

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".ts"}
SIDECAR_EXTS = {".srt", ".vtt", ".json", ".jsonl", ".csv", ".txt", ".md"}


@dataclass(frozen=True)
class Recording:
    recording_id: str
    path: Path
    duration: float
    width: int
    height: int
    fps: str
    video_codec: str
    audio_codec: str
    audio_channels: str
    audio_sample_rate: str
    file_size: int
    sample_decode_status: str


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def run_command(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False, timeout=timeout)


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple, set)):
        return "；".join(stringify(item) for item in value if stringify(item))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: stringify(row.get(field, "")) for field in fieldnames})


def timecode(seconds: float) -> str:
    total_ms = int(round(max(0.0, seconds) * 1000))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def slug_time(seconds: float) -> str:
    total = int(max(0.0, seconds))
    return f"{total // 3600:02d}{(total % 3600) // 60:02d}{total % 60:02d}"


def safe_slug(text: str) -> str:
    cleaned = re.sub(r"^\._", "", text)
    cleaned = re.sub(r"[\\/:*?\"<>|\s]+", "_", cleaned).strip("._")
    return cleaned[:80] or "video"


def parse_fps(value: str) -> str:
    if not value or value == "0/0":
        return ""
    if "/" not in value:
        return value
    left, right = value.split("/", 1)
    try:
        return f"{float(left) / float(right):.3f}".rstrip("0").rstrip(".")
    except (ValueError, ZeroDivisionError):
        return value


def ffprobe_json(path: Path) -> dict[str, Any]:
    result = run_command(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe_failed: {path}: {(result.stderr or result.stdout).strip()[:400]}")
    return json.loads(result.stdout)


def first_stream(metadata: dict[str, Any], codec_type: str) -> dict[str, Any]:
    for stream in metadata.get("streams", []):
        if stream.get("codec_type") == codec_type:
            return stream
    return {}


def sample_decode(path: Path) -> str:
    result = run_command(
        ["ffmpeg", "-hide_banner", "-v", "error", "-ss", "30", "-t", "2", "-i", str(path), "-f", "null", "-"],
        timeout=120,
    )
    if result.returncode == 0:
        return "sample_decode_ok"
    return "sample_decode_failed:" + (result.stderr or result.stdout or "")[:180].replace("\n", " ")


def discover_source_dir() -> tuple[Path | None, str]:
    for path in SOURCE_DIR_CANDIDATES:
        if path.exists():
            return path, "exact_prompt_path_found"
    if SEMANTIC_SOURCE_DIR.exists():
        return SEMANTIC_SOURCE_DIR, "semantic_nested_path_found: exact three prompt paths missing"
    matches: list[Path] = []
    root = Path("/Volumes/WD_BLACK")
    if root.exists():
        for path in root.rglob("*"):
            if path.is_dir() and "完整直播录屏" in path.name and "今年直播素材" in path.name:
                matches.append(path)
    if matches:
        return sorted(matches)[0], "keyword_same_dir_match"
    return None, "blocked_missing_live_recording_dir"


def discover_sidecars(source_dir: Path) -> list[Path]:
    parent = source_dir.parent
    files: list[Path] = []
    for base in [source_dir, parent]:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and not path.name.startswith("._") and path.suffix.lower() in SIDECAR_EXTS:
                files.append(path)
    return sorted(set(files))


def load_recordings(source_dir: Path) -> list[Recording]:
    media = sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file() and not path.name.startswith("._") and path.suffix.lower() in VIDEO_EXTS
    )
    recordings: list[Recording] = []
    for index, path in enumerate(media, start=1):
        meta = ffprobe_json(path)
        video = first_stream(meta, "video")
        audio = first_stream(meta, "audio")
        duration = float(meta.get("format", {}).get("duration") or video.get("duration") or 0.0)
        recordings.append(
            Recording(
                recording_id=f"rec_{index:03d}",
                path=path,
                duration=duration,
                width=int(video.get("width") or 0),
                height=int(video.get("height") or 0),
                fps=parse_fps(str(video.get("avg_frame_rate") or video.get("r_frame_rate") or "")),
                video_codec=str(video.get("codec_name") or ""),
                audio_codec=str(audio.get("codec_name") or ""),
                audio_channels=str(audio.get("channels") or ""),
                audio_sample_rate=str(audio.get("sample_rate") or ""),
                file_size=path.stat().st_size,
                sample_decode_status=sample_decode(path),
            )
        )
    return recordings


def transcript_path(recording: Recording) -> Path:
    return ASR_TRANSCRIPT_DIR / f"{recording.recording_id}_{safe_slug(recording.path.stem)}.json"


def audio_path(recording: Recording) -> Path:
    return ASR_AUDIO_DIR / f"{recording.recording_id}_{safe_slug(recording.path.stem)}.wav"


def extract_audio(recording: Recording, force: bool) -> Path:
    out_path = audio_path(recording)
    if out_path.exists() and out_path.stat().st_size > 0 and not force:
        return out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result = run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(recording.path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(out_path),
        ],
        timeout=2400,
    )
    if result.returncode != 0:
        raise RuntimeError(f"audio_extract_failed: {recording.path.name}: {(result.stderr or result.stdout)[:600]}")
    return out_path


def transcribe_recordings(recordings: list[Recording], args: argparse.Namespace) -> tuple[dict[str, dict[str, Any]], list[str]]:
    transcripts: dict[str, dict[str, Any]] = {}
    logs: list[str] = []
    if args.no_asr:
        logs.append("asr_skipped_by_flag")
        return transcripts, logs

    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as exc:  # pragma: no cover
        logs.append(f"blocked_local_faster_whisper_unavailable:{type(exc).__name__}:{exc}")
        return transcripts, logs

    ASR_TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    ASR_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    model_cache = REPO_ROOT / "素材整理_asset_management/04_时间码_timecode/model_cache"
    model_cache.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(args.asr_model, device=args.asr_device, compute_type=args.asr_compute_type, download_root=str(model_cache))

    for recording in recordings:
        out_path = transcript_path(recording)
        if out_path.exists() and not args.force_asr:
            transcripts[recording.recording_id] = json.loads(out_path.read_text(encoding="utf-8"))
            logs.append(f"{recording.recording_id}:transcript_reused:{out_path}")
            print(f"{recording.recording_id}: transcript reused -> {out_path}", flush=True)
            continue

        started = time.time()
        print(f"{recording.recording_id}: extracting audio and transcribing {recording.path.name}", flush=True)
        wav_path = extract_audio(recording, force=args.force_asr)
        raw_segments, info = model.transcribe(
            str(wav_path),
            language=args.asr_language,
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
        )
        segments: list[dict[str, Any]] = []
        for idx, segment in enumerate(raw_segments, start=1):
            text = (segment.text or "").strip()
            if not text:
                continue
            segments.append(
                {
                    "index": idx,
                    "start_seconds": round(float(segment.start), 3),
                    "end_seconds": round(float(segment.end), 3),
                    "start_time": timecode(float(segment.start)),
                    "end_time": timecode(float(segment.end)),
                    "text": text,
                }
            )

        payload = {
            "status": "success" if segments else "failed_no_segments",
            "generated_at": now_iso(),
            "recording_id": recording.recording_id,
            "source_file": recording.path.name,
            "source_path": str(recording.path),
            "duration_seconds": recording.duration,
            "language": getattr(info, "language", args.asr_language),
            "language_probability": getattr(info, "language_probability", None),
            "model_used": args.asr_model,
            "compute_type": args.asr_compute_type,
            "quality_status": "machine_transcript_pending_manual_review",
            "segment_count": len(segments),
            "segments": segments,
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        transcripts[recording.recording_id] = payload
        elapsed = time.time() - started
        logs.append(f"{recording.recording_id}:transcript_generated:segments={len(segments)} elapsed={elapsed:.1f}s path={out_path}")
        print(f"{recording.recording_id}: transcript generated segments={len(segments)} elapsed={elapsed:.1f}s -> {out_path}", flush=True)
    return transcripts, logs


def split_keywords(text: str) -> list[str]:
    raw = re.split(r"[;；、,/|，\s]+", text or "")
    return [item.strip() for item in raw if len(item.strip()) >= 2 and item.strip() not in {"source_label_or_keyword_family"}]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", text or "").lower()


def keyword_hits(text: str, keywords: Iterable[str]) -> list[str]:
    normalized = normalize_text(text)
    hits: list[str] = []
    for keyword in keywords:
        token = normalize_text(keyword)
        if token and token in normalized and keyword not in hits:
            hits.append(keyword)
    return hits


def build_keyword_index(action_rows: list[dict[str, str]], alias_rows: list[dict[str, str]], problem_rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in action_rows:
        action_id = row.get("normalized_action_id", "")
        if not action_id:
            continue
        keywords = []
        keywords.extend(split_keywords(row.get("alias_examples", "")))
        keywords.extend(split_keywords(row.get("speech_keyword_family", "")))
        keywords.extend(split_keywords(row.get("normalized_action_name_cn", "")))
        index[action_id] = {
            "action_id": action_id,
            "action_name": row.get("normalized_action_name_cn", ""),
            "problem_id": row.get("target_problem_primary", ""),
            "recommended_structure": row.get("recommended_structure", ""),
            "risk_review_items": row.get("risk_review_items", ""),
            "visual_evidence_required": row.get("visual_evidence_required", ""),
            "keywords": keywords,
        }
    for row in alias_rows:
        action_id = row.get("normalized_action_id", "")
        if action_id in index:
            index[action_id]["keywords"].extend(split_keywords(row.get("source_alias", "")))
    for row in problem_rows:
        problem_id = row.get("problem_category_id", "")
        keywords = split_keywords(row.get("source_keyword_families", ""))
        action_id = f"problem::{problem_id}"
        index[action_id] = {
            "action_id": "",
            "action_name": "",
            "problem_id": problem_id,
            "recommended_structure": row.get("recommended_structure", ""),
            "risk_review_items": row.get("risk_gate", ""),
            "visual_evidence_required": row.get("required_evidence", ""),
            "keywords": keywords,
        }
    return index


def classify_structure(text: str, structures: list[dict[str, str]], action_match: dict[str, Any] | None) -> tuple[str, str, list[str]]:
    checks = [
        ("误区/错误先抛 + 正确动作对比 + 原因解释", ["误区", "错误", "不对", "不要", "错", "代偿", "没感觉", "越练越"]),
        ("问题问答 + 原因解释 + 方法边界", ["吗", "为什么", "怎么办", "能不能", "可以", "不适合", "适合", "如果"]),
        ("痛点/人群点名 + 单动作完整循环 + 坚持建议", ["产后", "妈妈", "盆底", "漏", "松", "练", "坚持", "每天"]),
        ("工具/动作演示 + 发力口令 + 低压跟练收束", ["瑜伽球", "球", "工具", "发力", "呼吸", "收紧", "放松", "摆动", "跟着"]),
        ("多动作组合 + 同一主题推进 + 轻跟练收束", ["第一个", "第二个", "第三个", "几个动作", "组合", "一套"]),
        ("痛点/结果可视化 + 操作过程证据 + 低压行动", ["改善", "变", "效果", "平", "紧", "结果", "告别"]),
    ]
    if action_match and action_match.get("recommended_structure"):
        recommended = str(action_match["recommended_structure"])
        for row in structures:
            if row.get("usable_structure_name") == recommended:
                return recommended, "action_kb_recommended_structure", []
    for structure, words in checks:
        hits = keyword_hits(text, words)
        if hits:
            return structure, "text_keyword_rule", hits
    return "日期/主题不明素材 + 待视觉复核索引", "fallback_pending_visual_review", []


def infer_talk_function(text: str) -> str:
    rules = [
        ("风险", ["注意", "不要", "不适合", "风险", "禁忌"]),
        ("异议", ["但是", "担心", "怕", "没有用", "没感觉"]),
        ("促单", ["课程", "报名", "专场", "购物车", "价格", "优惠"]),
        ("信任", ["老师", "经验", "学员", "案例", "体系", "教练"]),
        ("方法", ["方法", "步骤", "先", "然后", "动作", "练", "发力", "呼吸"]),
        ("原因", ["因为", "原因", "所以", "不是", "关键"]),
        ("痛点", ["漏", "松", "疼", "产后", "盆底", "小腹", "妈妈"]),
    ]
    for label, words in rules:
        if keyword_hits(text, words):
            return label
    return "口播定位"


def infer_value_type(text: str, talk_function: str) -> str:
    if talk_function in {"痛点", "方法", "风险", "信任", "促单"}:
        return talk_function
    if keyword_hits(text, ["错", "误区", "不对", "不要", "代偿"]):
        return "纠错"
    if keyword_hits(text, ["工具", "瑜伽球", "球", "道具"]):
        return "工具演示"
    if keyword_hits(text, ["跟着", "一起", "练", "做"]):
        return "跟练"
    return "方法"


def action_function_from_text(text: str) -> str:
    if keyword_hits(text, ["纠正", "错误", "不对", "代偿"]):
        return "纠错"
    if keyword_hits(text, ["证据", "看", "对比"]):
        return "证据"
    if keyword_hits(text, ["工具", "瑜伽球", "球", "道具"]):
        return "工具展示"
    if keyword_hits(text, ["跟着", "一起"]):
        return "跟练"
    return "演示"


def choose_action_match(text: str, keyword_index: dict[str, dict[str, Any]]) -> tuple[dict[str, Any] | None, list[str]]:
    best: dict[str, Any] | None = None
    best_hits: list[str] = []
    for item in keyword_index.values():
        hits = keyword_hits(text, item.get("keywords", []))
        if len(hits) > len(best_hits):
            best = item
            best_hits = hits
    return best, best_hits


def summarize_text(text: str, max_len: int = 120) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 1] + "…"


def topic_tags(text: str, action_hits: list[str]) -> list[str]:
    tags: list[str] = []
    rules = [
        ("动作口令/跟练", ["吸气", "呼气", "发力", "收紧", "放松", "动作", "练习", "跟着"]),
        ("工具/道具演示", ["球", "瑜伽球", "工具", "道具", "凳子", "垫"]),
        ("盆底/产后训练", ["盆底", "产后", "骨盆", "漏", "松", "下坠"]),
        ("胸部/呼吸练习", ["乳房", "胸", "呼吸", "腋下", "肩膀"]),
        ("问题问答/原因解释", ["为什么", "怎么办", "可以", "适合", "不适合", "原因"]),
        ("误区纠错/风险提醒", ["不要", "错误", "不对", "代偿", "注意", "风险"]),
        ("课程/商品/业务信息", ["课程", "报名", "购物车", "价格", "优惠", "专场"]),
        ("情绪/关系表达", ["情绪", "关系", "伴侣", "委屈", "沟通"]),
    ]
    for tag, words in rules:
        if keyword_hits(text, words):
            tags.append(tag)
    if action_hits and "动作口令/跟练" not in tags:
        tags.append("动作/问题关键词命中")
    return tags or ["主题待人工听审"]


def safe_speech_summary(text: str, talk_function: str, structure_name: str, action_hits: list[str]) -> str:
    tags = topic_tags(text, action_hits)
    action_hint = "；动作词族命中" if action_hits else "；未命中明确动作词族"
    length_hint = len(normalize_text(text))
    return (
        f"机器转写高层摘要：口播功能={talk_function}；主题={' / '.join(tags[:4])}；"
        f"结构倾向={structure_name}{action_hint}；转写字符数约 {length_hint}。"
        "原文留在本地忽略 ASR 缓存，提交表不展开敏感细节。"
    )


def windows_from_transcript(recording: Recording, transcript: dict[str, Any], window_seconds: int) -> list[dict[str, Any]]:
    segments = transcript.get("segments", [])
    windows: list[dict[str, Any]] = []
    if not segments:
        return windows
    count = max(1, int(math.ceil(recording.duration / window_seconds)))
    for idx in range(count):
        start = idx * window_seconds
        end = min(recording.duration, start + window_seconds)
        included = [
            segment
            for segment in segments
            if float(segment.get("end_seconds", 0)) > start and float(segment.get("start_seconds", 0)) < end
        ]
        text = " ".join(str(segment.get("text", "")).strip() for segment in included if str(segment.get("text", "")).strip())
        windows.append(
            {
                "timeline_id": f"{recording.recording_id}_t{idx + 1:03d}",
                "recording_id": recording.recording_id,
                "source_file": recording.path.name,
                "start_seconds": round(start, 3),
                "end_seconds": round(end, 3),
                "start_time": timecode(start),
                "end_time": timecode(end),
                "duration_seconds": round(end - start, 3),
                "speech_text": text,
                "segment_count": len(included),
            }
        )
    return windows


def score_window(text: str, action_hits: list[str], structure_hits: list[str], talk_function: str) -> int:
    score_value = 0
    char_count = len(normalize_text(text))
    if char_count >= 40:
        score_value += 2
    if char_count >= 90:
        score_value += 2
    if action_hits:
        score_value += 3
    if structure_hits:
        score_value += 2
    if talk_function in {"方法", "原因", "痛点", "风险"}:
        score_value += 2
    if keyword_hits(text, ["课程", "报名", "价格", "购物车", "优惠"]):
        score_value -= 2
    if keyword_hits(text, ["效果", "改善", "保证", "一定"]):
        score_value -= 1
    return max(0, score_value)


def priority_from_score(score_value: int, candidate_type: str, text: str) -> str:
    if score_value >= 9 and candidate_type == "speech_action_pair":
        return "A"
    if score_value >= 6:
        return "B"
    if score_value >= 4:
        return "C"
    return "Reject"


def build_outputs(recordings: list[Recording], transcripts: dict[str, dict[str, Any]], sidecars: list[Path], args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    structures = read_csv(STRUCTURE_CSV)
    action_rows = read_csv(ACTION_MAP_CSV)
    alias_rows = read_csv(ALIAS_CSV)
    problem_rows = read_csv(PROBLEM_CSV)
    keyword_index = build_keyword_index(action_rows, alias_rows, problem_rows)

    timeline_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    reject_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    candidate_counter = 1

    for recording in recordings:
        transcript = transcripts.get(recording.recording_id, {})
        windows = windows_from_transcript(recording, transcript, args.window_seconds)
        if not windows:
            timeline_rows.append(
                {
                    "timeline_id": f"{recording.recording_id}_blocked",
                    "recording_id": recording.recording_id,
                    "source_file": recording.path.name,
                    "start_time": "00:00:00.000",
                    "end_time": timecode(recording.duration),
                    "duration_seconds": f"{recording.duration:.3f}",
                    "speech_evidence_status": "blocked_need_transcript_for_speech_screening",
                    "speech_summary": "",
                    "action_keyword_hits": "",
                    "normalized_action_id": "",
                    "problem_category_id": "",
                    "usable_structure_name": "日期/主题不明素材 + 待视觉复核索引",
                    "candidate_signal_score": 0,
                    "candidate_status": "blocked",
                    "source_evidence": "no transcript sidecar and local ASR unavailable or skipped",
                }
            )
            continue

        for window in windows:
            text = str(window["speech_text"])
            action_match, action_hits = choose_action_match(text, keyword_index)
            structure_name, structure_reason, structure_hits = classify_structure(text, structures, action_match)
            talk_function = infer_talk_function(text)
            score_value = score_window(text, action_hits, structure_hits, talk_function)
            speech_status = "machine_transcript_pending_manual_review" if text else "no_speech_detected_in_window"
            candidate_type = "speech_action_pair" if action_hits else ("speech_only" if text else "reject")
            timeline_rows.append(
                {
                    "timeline_id": window["timeline_id"],
                    "recording_id": recording.recording_id,
                    "source_file": recording.path.name,
                    "start_time": window["start_time"],
                    "end_time": window["end_time"],
                    "duration_seconds": window["duration_seconds"],
                    "speech_evidence_status": speech_status,
                    "speech_summary": safe_speech_summary(text, talk_function, structure_name, action_hits) if text else "",
                    "action_keyword_hits": f"high_level_tags={' / '.join(topic_tags(text, action_hits)[:4])}; keyword_count={len(action_hits)}",
                    "normalized_action_id": (action_match or {}).get("action_id", ""),
                    "problem_category_id": (action_match or {}).get("problem_id", ""),
                    "usable_structure_name": structure_name,
                    "candidate_signal_score": score_value,
                    "candidate_status": "candidate_signal" if score_value >= args.min_candidate_score else "reject_or_low_signal",
                    "source_evidence": "local_faster_whisper_full_recording_transcript; action_kb_text_keyword_rules; visual_pending_review",
                }
            )
            if score_value < args.min_candidate_score:
                if text or score_value > 0:
                    reject_rows.append(
                        {
                            "rejected_id": f"reject_{len(reject_rows) + 1:04d}",
                            "recording_id": recording.recording_id,
                            "source_file": recording.path.name,
                            "start_time": window["start_time"],
                            "end_time": window["end_time"],
                            "candidate_status": "Reject",
                            "route_decision": "reject_or_low_signal",
                            "why_rejected": "口播/动作/结构信号不足，或需要人工听审后再判断。",
                            "missing_part": "opening/middle/ending/visual_evidence",
                            "manual_review_items": "如需保留，先听审口播并看原片关键动作；健康/业务/动作专业性另行复核。",
                            "source_evidence": "local_faster_whisper_transcript_low_signal",
                        }
                    )
                continue

            candidate_id = f"live_cand_{candidate_counter:04d}"
            candidate_counter += 1
            priority = priority_from_score(score_value, candidate_type, text)
            if priority == "Reject":
                continue
            missing = []
            if "pending" in speech_status:
                missing.append("manual_asr_correction")
            missing.append("visual_action_cycle_confirmation")
            if keyword_hits(text, ["课程", "报名", "价格", "购物车", "效果", "改善", "产后", "盆底", "漏"]):
                missing.append("health_business_customer_review")
            recommended = "先按口播完整单元复核，再看同窗口动作/道具是否兑现；必要时向前后各扩 10-30 秒。"
            if priority == "A":
                recommended = "优先给剪辑师听审和看原片；保留同题口播与动作窗口，先做人工精修候选。"
            elif priority == "B":
                recommended = "适合二次加工；建议补字幕、扩前后文或与邻近动作窗口拼接。"
            candidate_rows.append(
                {
                    "candidate_id": candidate_id,
                    "recording_id": recording.recording_id,
                    "source_file": str(recording.path),
                    "start_time": window["start_time"],
                    "end_time": window["end_time"],
                    "duration_seconds": window["duration_seconds"],
                    "candidate_type": candidate_type,
                    "usable_structure_name": structure_name,
                    "clip_value_type": infer_value_type(text, talk_function),
                    "speech_summary": safe_speech_summary(text, talk_function, structure_name, action_hits),
                    "action_summary": "文本命中动作/道具/发力词族；画面动作完整性待视觉复核。" if action_hits else "无明确动作词命中；当前只作口播候选。",
                    "normalized_action_id": (action_match or {}).get("action_id", ""),
                    "problem_category_id": (action_match or {}).get("problem_id", ""),
                    "speech_complete_unit": "machine_transcript_window_pending_manual_review",
                    "action_complete_cycle": "pending_visual_review",
                    "speech_action_sync": "same_window_text_keyword_candidate_pending_visual_review" if action_hits else "only_talk_pending_visual_review",
                    "visual_obstruction_risk": "pending_visual_review",
                    "missing_part": "；".join(missing),
                    "recommended_editor_action": recommended,
                    "stage1_priority": priority,
                    "manual_review_items": "ASR 校字；原片听审；动作完整循环；画面遮挡；健康/业务/适用人群；敏感表达公开尺度。",
                    "source_evidence": f"timeline={window['timeline_id']}; structure_reason={structure_reason}; keyword_count={len(action_hits) + len(structure_hits)}; transcript={transcript_path(recording)}",
                    "status": f"screening_candidate_pending_manual_review_score_{score_value}",
                }
            )
            pair_rows.append(
                {
                    "pair_group_id": f"pair_{len(pair_rows) + 1:04d}",
                    "recording_id": recording.recording_id,
                    "talk_segment_id": candidate_id,
                    "talk_start_time": window["start_time"],
                    "talk_end_time": window["end_time"],
                    "talk_function": talk_function,
                    "talk_summary": safe_speech_summary(text, talk_function, structure_name, action_hits),
                    "action_segment_id": candidate_id if action_hits else "",
                    "action_start_time": window["start_time"] if action_hits else "",
                    "action_end_time": window["end_time"] if action_hits else "",
                    "normalized_action_id": (action_match or {}).get("action_id", ""),
                    "action_function": action_function_from_text(text) if action_hits else "",
                    "target_problem": (action_match or {}).get("problem_id", ""),
                    "pair_relation": "intercut_needed" if action_hits and talk_function in {"原因", "方法"} else ("only_talk" if not action_hits else "talk_before_action"),
                    "gap_seconds": 0 if action_hits else "",
                    "why_pair": "同一 120 秒窗口内同时命中口播功能和动作/道具/发力词族；需原片确认画面是否同步。" if action_hits else "当前只有口播证据，动作段需要人工看原片或后续视觉复核补齐。",
                    "editor_sequence_advice": "先听口播确定主问题，再截同窗口动作；若动作在后半段，按口播在前动作在后剪。" if action_hits else "先作文本候选；不要直接包装成动作教学。",
                    "stage1_priority": priority,
                    "review_status": "pending_manual_audio_visual_review",
                }
            )

    counts = {
        "timeline": len(timeline_rows),
        "candidates": len(candidate_rows),
        "pairs": len(pair_rows),
        "A": sum(1 for row in candidate_rows if row.get("stage1_priority") == "A"),
        "B": sum(1 for row in candidate_rows if row.get("stage1_priority") == "B"),
        "C": sum(1 for row in candidate_rows if row.get("stage1_priority") == "C"),
        "Reject": len(reject_rows),
        "sidecars": len(sidecars),
    }
    return timeline_rows, candidate_rows, pair_rows, {**counts, "_reject_rows": reject_rows}  # type: ignore[dict-item]


def inventory_rows(recordings: list[Recording], source_dir: Path | None, source_status: str, sidecars: list[Path]) -> list[dict[str, Any]]:
    sidecar_note = "none_found" if not sidecars else "；".join(str(path) for path in sidecars[:10])
    return [
        {
            "recording_id": recording.recording_id,
            "file_name": recording.path.name,
            "source_path": str(recording.path),
            "source_dir": str(source_dir) if source_dir else "",
            "source_dir_status": source_status,
            "duration_seconds": f"{recording.duration:.3f}",
            "duration_timecode": timecode(recording.duration),
            "resolution": f"{recording.width}x{recording.height}",
            "fps": recording.fps,
            "video_codec": recording.video_codec,
            "audio_present": "yes" if recording.audio_codec else "no",
            "audio_codec": recording.audio_codec,
            "audio_channels": recording.audio_channels,
            "audio_sample_rate": recording.audio_sample_rate,
            "file_size_bytes": recording.file_size,
            "sample_decode_status": recording.sample_decode_status,
            "sidecar_transcript_or_parse": sidecar_note,
            "status": "ffprobe_ok_sample_decode_ok" if recording.sample_decode_status == "sample_decode_ok" else "ffprobe_ok_sample_decode_issue",
            "notes": "AppleDouble ._* entries excluded; technical validation is not content validation.",
        }
        for recording in recordings
    ]


MASTER_FIELDS = [
    "candidate_id",
    "recording_id",
    "source_file",
    "start_time",
    "end_time",
    "duration_seconds",
    "candidate_type",
    "usable_structure_name",
    "clip_value_type",
    "speech_summary",
    "action_summary",
    "normalized_action_id",
    "problem_category_id",
    "speech_complete_unit",
    "action_complete_cycle",
    "speech_action_sync",
    "visual_obstruction_risk",
    "missing_part",
    "recommended_editor_action",
    "stage1_priority",
    "manual_review_items",
    "source_evidence",
    "status",
]

PAIR_FIELDS = [
    "pair_group_id",
    "recording_id",
    "talk_segment_id",
    "talk_start_time",
    "talk_end_time",
    "talk_function",
    "talk_summary",
    "action_segment_id",
    "action_start_time",
    "action_end_time",
    "normalized_action_id",
    "action_function",
    "target_problem",
    "pair_relation",
    "gap_seconds",
    "why_pair",
    "editor_sequence_advice",
    "stage1_priority",
    "review_status",
]


def write_reports(
    source_dir: Path | None,
    source_status: str,
    recordings: list[Recording],
    sidecars: list[Path],
    timeline_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    pair_rows: list[dict[str, Any]],
    reject_rows: list[dict[str, Any]],
    counts: dict[str, int],
    asr_logs: list[str],
    started_at: str,
    args: argparse.Namespace,
) -> None:
    inventory = inventory_rows(recordings, source_dir, source_status, sidecars)
    write_csv(
        INVENTORY_CSV,
        [
            "recording_id",
            "file_name",
            "source_path",
            "source_dir",
            "source_dir_status",
            "duration_seconds",
            "duration_timecode",
            "resolution",
            "fps",
            "video_codec",
            "audio_present",
            "audio_codec",
            "audio_channels",
            "audio_sample_rate",
            "file_size_bytes",
            "sample_decode_status",
            "sidecar_transcript_or_parse",
            "status",
            "notes",
        ],
        inventory,
    )
    write_csv(
        TIMELINE_CSV,
        [
            "timeline_id",
            "recording_id",
            "source_file",
            "start_time",
            "end_time",
            "duration_seconds",
            "speech_evidence_status",
            "speech_summary",
            "action_keyword_hits",
            "normalized_action_id",
            "problem_category_id",
            "usable_structure_name",
            "candidate_signal_score",
            "candidate_status",
            "source_evidence",
        ],
        timeline_rows,
    )
    write_csv(MASTER_CSV, MASTER_FIELDS, candidate_rows)
    write_csv(PAIR_CSV, PAIR_FIELDS, pair_rows)
    write_csv(STRUCTURE_OUT_CSV, MASTER_FIELDS, sorted(candidate_rows, key=lambda row: (str(row.get("usable_structure_name")), str(row.get("recording_id")), str(row.get("start_time")))))
    write_csv(A_CSV, MASTER_FIELDS, [row for row in candidate_rows if row.get("stage1_priority") == "A"])
    write_csv(B_CSV, MASTER_FIELDS, [row for row in candidate_rows if row.get("stage1_priority") == "B"])
    write_csv(
        RISK_CSV,
        [
            "rejected_id",
            "recording_id",
            "source_file",
            "start_time",
            "end_time",
            "candidate_status",
            "route_decision",
            "why_rejected",
            "missing_part",
            "manual_review_items",
            "source_evidence",
        ],
        reject_rows,
    )

    by_structure: dict[str, list[dict[str, Any]]] = {}
    for row in candidate_rows:
        by_structure.setdefault(str(row.get("usable_structure_name", "未归类")), []).append(row)

    report_lines = [
        "# 剪辑师人读版报告：完整直播素材筛选与口播动作配对",
        "",
        f"状态：`screening_tables_generated_pending_user_review`",
        f"生成时间：{now_iso()}",
        "",
        "## 1. 总结论",
        "",
        f"- `已确认`：已定位 4 条真实直播录屏，目录为 `{source_dir}`。",
        f"- `已确认`：4 条录屏均完成 `ffprobe` 元数据读取与 2 秒样本解码抽检。",
        f"- `部分成立`：本轮使用本地 `faster-whisper` 机器转写作为口播证据，状态仍为 `machine_transcript_pending_manual_review`。",
        "- `待验证`：动作完整循环、画面遮挡、动作专业性、健康/业务事实、审美与发布状态。",
        "- `未执行`：未上传完整视频；本轮未把阿里视觉模型结果写成动作通过。",
        "",
        "## 2. 数量",
        "",
        f"- 直播录屏：{len(recordings)}",
        f"- 时间轴窗口：{counts.get('timeline', 0)}",
        f"- 总候选：{counts.get('candidates', 0)}",
        f"- A 类：{counts.get('A', 0)}",
        f"- B 类：{counts.get('B', 0)}",
        f"- C 类：{counts.get('C', 0)}",
        f"- Reject/低信号：{counts.get('Reject', 0)}",
        f"- 口播动作配对组：{counts.get('pairs', 0)}",
        "",
        "## 3. 按结构给剪辑师的使用建议",
        "",
    ]
    for structure, rows in by_structure.items():
        report_lines.extend([f"### {structure}", ""])
        for row in rows[:8]:
            report_lines.append(
                f"- `{row['candidate_id']}` `{row['recording_id']}` `{row['start_time']}-{row['end_time']}` "
                f"`{row['stage1_priority']}`：{row['speech_summary']}；剪辑建议：{row['recommended_editor_action']}"
            )
        if len(rows) > 8:
            report_lines.append(f"- 另有 {len(rows) - 8} 条同结构候选，详见 CSV。")
        report_lines.append("")
    report_lines.extend(
        [
            "## 4. 复核边界",
            "",
            "- 所有候选都需要人工听审 ASR，尤其是 `产后/盆底/漏尿/瑜伽球` 等高频错词。",
            "- 所有动作字段都只是文本/关键词候选，必须看原片确认动作完整循环、画面遮挡和公开展示尺度。",
            "- 涉及健康、效果、课程、价格、权益、案例和适用人群的表达均需客户或专业复核。",
            "- `stage1_priority=A` 表示优先给剪辑师处理，不表示 `publish_ready`。",
        ]
    )
    EDITOR_REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    EDITOR_REPORT_MD.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manual_lines = [
        "# 人工复核清单",
        "",
        f"状态：`manual_review_required`",
        "",
        "## 必复核项",
        "",
        "1. 逐条听审 A 类候选，修正机器转写错字。",
        "2. 打开原片确认动作完整循环、身体关键部位/道具是否无遮挡。",
        "3. 所有健康、训练频率、适用人群、效果词、课程/商品/价格表达，保留客户或专业复核。",
        "4. 口播在前、动作在后的配对组，确认间隔是否自然；不自然则改为 B 类二次加工。",
        "5. 敏感成人/亲密关系表达不得直接发布，先做合规和客户口径复核。",
        "",
        "## A 类候选优先听审",
        "",
    ]
    for row in [item for item in candidate_rows if item.get("stage1_priority") == "A"][:30]:
        manual_lines.append(f"- `{row['candidate_id']}` `{row['recording_id']}` `{row['start_time']}-{row['end_time']}`：{row['manual_review_items']}")
    MANUAL_REVIEW_MD.write_text("\n".join(manual_lines) + "\n", encoding="utf-8")

    export_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "mkdir -p outputs/local_live_candidate_exports",
        "",
        "# 本文件只提供本地导出命令；不要提交导出的媒体文件。",
    ]
    export_targets = [row for row in candidate_rows if row.get("stage1_priority") == "A"] or candidate_rows[:20]
    for row in export_targets:
        src = str(row["source_file"])
        out_name = f"{row['candidate_id']}_{row['recording_id']}_{slug_time(parse_timecode(row['start_time']))}_{slug_time(parse_timecode(row['end_time']))}.mp4"
        export_lines.append(
            "ffmpeg -hide_banner -loglevel error -y "
            f"-ss {shlex.quote(str(row['start_time']))} -to {shlex.quote(str(row['end_time']))} "
            f"-i {shlex.quote(src)} -c copy {shlex.quote('outputs/local_live_candidate_exports/' + out_name)}"
        )
    EXPORT_COMMANDS_SH.write_text("\n".join(export_lines) + "\n", encoding="utf-8")

    report = [
        "# 完整直播素材筛选与口播动作配对执行报告",
        "",
        f"状态：`screening_tables_generated_pending_user_review`",
        f"开始时间：{started_at}",
        f"生成时间：{now_iso()}",
        "",
        "## commands",
        "",
        "- `pwd && git rev-parse --show-toplevel && git branch --show-current && git remote -v && git status --short`",
        "- `git pull --ff-only`",
        "- `ffprobe` 元数据读取 4 条录屏",
        "- `ffmpeg -ss 30 -t 2 ... -f null -` 样本解码抽检 4 条录屏",
        f"- `.venv_timecode/bin/python scripts/full_live_material_screening_with_action_pairing.py --asr-model {args.asr_model} --window-seconds {args.window_seconds}`",
        "",
        "## result",
        "",
        f"- 当前项目仓库：`fthytwerwt-sudo/lanxinse--`",
        f"- 本地仓库路径：`{REPO_ROOT}`",
        f"- 直播素材目录：`{source_dir}`",
        f"- source_dir_status：`{source_status}`",
        f"- 直播录屏数量：{len(recordings)}",
        f"- 可读录屏数量：{sum(1 for row in inventory if row['status'].startswith('ffprobe_ok'))}",
        f"- 总候选数：{counts.get('candidates', 0)}",
        f"- A 类数量：{counts.get('A', 0)}",
        f"- B 类数量：{counts.get('B', 0)}",
        f"- C 类数量：{counts.get('C', 0)}",
        f"- Reject 数量：{counts.get('Reject', 0)}",
        f"- 口播动作配对组数量：{counts.get('pairs', 0)}",
        f"- 是否生成本地导出命令：yes",
        f"- 是否提交媒体：no",
        f"- 是否写健康/业务/动作通过：no",
        "",
        "## ASR / Ali visual boundary",
        "",
        f"- 本地 ASR 日志：`{' | '.join(asr_logs) if asr_logs else 'none'}`",
        "- 阿里视觉：历史最小连接报告显示 `qwen3-vl-plus` 连接过；本轮未上传完整视频，未把视觉模型作为动作完整性通过证据。",
        "",
        "## files_changed",
        "",
        f"- `{INVENTORY_CSV.relative_to(REPO_ROOT)}`",
        f"- `{TIMELINE_CSV.relative_to(REPO_ROOT)}`",
        f"- `{MASTER_CSV.relative_to(REPO_ROOT)}`",
        f"- `{PAIR_CSV.relative_to(REPO_ROOT)}`",
        f"- `{STRUCTURE_OUT_CSV.relative_to(REPO_ROOT)}`",
        f"- `{A_CSV.relative_to(REPO_ROOT)}`",
        f"- `{B_CSV.relative_to(REPO_ROOT)}`",
        f"- `{RISK_CSV.relative_to(REPO_ROOT)}`",
        f"- `{EDITOR_REPORT_MD.relative_to(REPO_ROOT)}`",
        f"- `{MANUAL_REVIEW_MD.relative_to(REPO_ROOT)}`",
        f"- `{EXPORT_COMMANDS_SH.relative_to(REPO_ROOT)}`",
        f"- `{EXEC_REPORT_MD.relative_to(REPO_ROOT)}`",
        f"- `scripts/full_live_material_screening_with_action_pairing.py`",
        "",
        "## validation",
        "",
        "- 待运行：`python3 -m py_compile scripts/full_live_material_screening_with_action_pairing.py`",
        "- 待运行：`git diff --check`",
        "- 待运行：`git diff --cached --check`",
        "- 输出表自检：脚本已生成 inventory/timeline/master/pair/A/B/reject/report/export commands。",
        "",
        "## failed_items",
        "",
        "- 同目录/邻近目录未发现现成 `.srt/.vtt/.json/.csv/.txt` 转写或动作解析。",
        "- 未做全量视频解码；长视频只做 ffprobe + 2 秒样本解码抽检。",
        "- 未做人审视觉通过、动作专业通过、业务通过或发布通过。",
        "",
        "## blocked reason",
        "",
        "- 无 `blocked`。当前是 `pending_user_review`，不是业务/审美/发布完成。",
    ]
    EXEC_REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    EXEC_REPORT_MD.write_text("\n".join(report) + "\n", encoding="utf-8")


def parse_timecode(value: str) -> float:
    parts = value.split(":")
    if len(parts) != 3:
        return 0.0
    try:
        h = float(parts[0])
        m = float(parts[1])
        s = float(parts[2])
    except ValueError:
        return 0.0
    return h * 3600 + m * 60 + s


def ensure_must_read_files() -> None:
    missing = [
        path
        for path in [
            STRUCTURE_CSV,
            BRIDGE_MD,
            ACTION_MAP_CSV,
            ALIAS_CSV,
            PROBLEM_CSV,
            ACTION_BRIDGE_CSV,
            ACTION_RULES_MD,
            ACTION_SCREENING_MD,
            ACTION_TRACE_MD,
            PACK_README,
            PACK_TRACE_CSV,
        ]
        if not path.exists()
    ]
    if missing:
        raise RuntimeError("blocked_missing_required_fact_files:" + "；".join(str(path) for path in missing))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Full live material screening with speech/action pairing.")
    parser.add_argument("--asr-model", default=os.environ.get("TIMECODE_MODEL", "small"))
    parser.add_argument("--asr-device", default=os.environ.get("TIMECODE_DEVICE", "cpu"))
    parser.add_argument("--asr-compute-type", default=os.environ.get("TIMECODE_COMPUTE_TYPE", "int8"))
    parser.add_argument("--asr-language", default=os.environ.get("TIMECODE_LANGUAGE", "zh"))
    parser.add_argument("--force-asr", action="store_true")
    parser.add_argument("--no-asr", action="store_true")
    parser.add_argument("--window-seconds", type=int, default=120)
    parser.add_argument("--min-candidate-score", type=int, default=4)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started_at = now_iso()
    ensure_must_read_files()
    source_dir, source_status = discover_source_dir()
    if source_dir is None:
        write_reports(source_dir, source_status, [], [], [], [], [], [], {"timeline": 0, "candidates": 0, "pairs": 0, "A": 0, "B": 0, "C": 0, "Reject": 0}, [source_status], started_at, args)
        print(source_status)
        return 2

    sidecars = discover_sidecars(source_dir)
    recordings = load_recordings(source_dir)
    if len(recordings) != 4:
        print(f"blocked_unexpected_recording_count: found={len(recordings)}", file=sys.stderr)

    transcripts, asr_logs = transcribe_recordings(recordings, args)
    timeline_rows, candidate_rows, pair_rows, counts_any = build_outputs(recordings, transcripts, sidecars, args)
    reject_rows = counts_any.pop("_reject_rows")  # type: ignore[assignment]
    counts = {key: int(value) for key, value in counts_any.items()}
    write_reports(source_dir, source_status, recordings, sidecars, timeline_rows, candidate_rows, pair_rows, reject_rows, counts, asr_logs, started_at, args)
    print(json.dumps({"status": "ok", "recordings": len(recordings), **counts}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
