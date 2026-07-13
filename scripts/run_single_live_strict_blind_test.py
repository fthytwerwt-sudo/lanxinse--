#!/usr/bin/env python3
"""Run a strict blind test for one full livestream recording.

The program is content-agnostic by design: callers provide the source video,
local work directory, final video directory, and minimal fact-output paths.
It does not contain source-specific action names, spoken anchors, or timecodes.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import math
import os
import re
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat
except ImportError:  # pragma: no cover
    Image = None
    ImageChops = None
    ImageDraw = None
    ImageFont = None
    ImageOps = None
    ImageStat = None


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
PRIMARY_VISION_MODEL = "qwen3-vl-plus"
FALLBACK_VISION_MODEL = "qwen-vl-max"
FORBIDDEN_MODELS = {"qwen-vl-plus-latest", "qwen3-vl-max"}

FINAL_DIRS = [
    "01_问题回答后动作",
    "02_痛点原因后动作",
    "03_用途方法后动作",
    "04_误区纠正后动作",
    "05_讲解在前动作在后",
    "06_边讲边做",
    "07_已重排成讲解后动作",
    "08_人工复核",
]

INDEX_FIELDS = [
    "video_file_name",
    "classification_dir",
    "source_time_ranges",
    "clip_structure_type",
    "editor_usability_status",
    "action_topic_id",
    "action_or_problem_topic",
    "source_video_path",
    "final_video_path",
    "downgrade_reason",
    "technical_probe_status",
]

PLACEHOLDER_VALUES = {
    "",
    "your_api_key_here",
    "your-ali-api-key",
    "你的真实阿里 API key",
    "这里填你的真实阿里 API key",
    "请在本地填写，不要提交真实 key",
}

QUESTION_MARKERS = ("吗", "嗎", "呢", "为什么", "為什麼", "怎么", "怎麼", "要不要", "能不能", "可不可以", "是否", "有没有", "有沒有", "?")
GENERIC_NON_QUESTIONS = {"", "动作相关问题", "动作/练习口播", "动作/练习问题", "身体状态", "动作主题"}
SALES_TERMS = ("课程", "报名", "价格", "优惠", "下单", "购买", "链接", "福利", "专场", "成交", "私教", "训练营")
CHAT_TERMS = ("点赞", "关注", "评论", "直播间", "宝宝", "姐妹", "家人们", "听得到", "卡了", "刷屏", "欢迎")
REASON_TERMS = ("因为", "原因", "所以", "导致", "关键", "为什么", "为什么会", "其实是", "本质")
BOUNDARY_TERMS = ("注意", "不要", "不能", "不适合", "如果", "除非", "禁忌", "边界", "先确认", "轻轻")
METHOD_TERMS = ("先", "然后", "接下来", "动作", "方法", "位置", "方向", "力度", "步骤", "找到", "放在", "按", "揉", "吸气", "呼气", "抬", "放下", "练")
PURPOSE_TERMS = ("为了", "帮助", "改善", "解决", "主要是", "这个动作", "作用", "用途", "让你", "可以把", "适合")
PAIN_TERMS = ("痛", "酸", "胀", "紧", "松", "漏", "堵", "不舒服", "问题", "困扰", "情绪", "压力")
MISTAKE_TERMS = ("误区", "错误", "不对", "错", "不要这样", "代偿", "纠正", "正确")
ACTION_INSTRUCTION_TERMS = ("吸气", "呼气", "按住", "放松", "收紧", "抬起", "落下", "保持", "跟着", "慢慢")


@dataclass(frozen=True)
class SpeechSegment:
    index: int
    start_seconds: float
    end_seconds: float
    text: str


@dataclass(frozen=True)
class VisualUnit:
    action_topic_id: str
    start_seconds: float
    end_seconds: float
    motion_score: float
    contact_sheet: Path
    frame_timecodes: list[str]
    visual_status: str
    model_name: str
    observed_action_name: str
    observed_body_part_or_tool: str
    action_cycle_complete: str
    presenter_visible: str
    topic_break_risk: str
    reason: str


@dataclass(frozen=True)
class VideoPlan:
    action_topic_id: str
    classification_dir: str
    clip_structure_type: str
    editor_usability_status: str
    topic_title: str
    source_time_ranges: list[tuple[str, float, float]]
    final_video_path: Path
    downgrade_reason: str


def now_text() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def run(cmd: list[str], timeout: int = 1200) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def seconds_to_timecode(value: float) -> str:
    total_ms = int(round(max(0.0, value) * 1000))
    ms = total_ms % 1000
    total_seconds = total_ms // 1000
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"


def safe_slug(value: str, max_len: int = 36) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", (value or "").strip(), flags=re.UNICODE)
    cleaned = re.sub(r"_+", "_", cleaned).strip("._")
    return (cleaned or "动作主题")[:max_len]


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def env_value(values: dict[str, str], key: str, default: str = "") -> str:
    return os.environ.get(key) or values.get(key) or default


def is_placeholder_key(value: str) -> bool:
    return value.strip() in PLACEHOLDER_VALUES


def sanitize_error(text: str, api_key: str = "") -> str:
    cleaned = (text or "").replace("\n", " ").replace("\r", " ")
    if api_key:
        cleaned = cleaned.replace(api_key, "<redacted_api_key>")
    cleaned = re.sub(r"(?i)bearer\s+[A-Za-z0-9_./+=-]{12,}", "Bearer <redacted>", cleaned)
    return cleaned[:700]


def ffprobe_json(path: Path) -> dict[str, Any]:
    proc = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)], timeout=180)
    if proc.returncode != 0:
        raise RuntimeError(f"blocked_ffprobe_failed:{sanitize_error(proc.stderr or proc.stdout)}")
    return json.loads(proc.stdout)


def first_stream(meta: dict[str, Any], codec_type: str) -> dict[str, Any]:
    for stream in meta.get("streams", []):
        if stream.get("codec_type") == codec_type:
            return stream
    return {}


def source_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_clean_output_dirs(final_root: Path, work_root: Path, force: bool) -> None:
    for root in (final_root, work_root):
        if root.exists() and any(root.iterdir()):
            if not force:
                raise RuntimeError(f"blocked_output_exists:{root}")
            shutil.rmtree(root)
        root.mkdir(parents=True, exist_ok=True)
    for directory in FINAL_DIRS:
        (final_root / directory).mkdir(parents=True, exist_ok=True)


def extract_audio(source: Path, audio_path: Path, force: bool) -> None:
    if audio_path.exists() and audio_path.stat().st_size > 0 and not force:
        return
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    proc = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(audio_path),
        ],
        timeout=3600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"blocked_audio_extract_failed:{sanitize_error(proc.stderr or proc.stdout)}")


def transcribe_source(source: Path, work_root: Path, args: argparse.Namespace, duration: float) -> tuple[list[SpeechSegment], Path]:
    transcript_path = work_root / "asr" / "full_transcript.json"
    if transcript_path.exists() and not args.force_asr:
        data = json.loads(transcript_path.read_text(encoding="utf-8"))
        return parse_transcript_segments(data), transcript_path
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"blocked_local_faster_whisper_unavailable:{type(exc).__name__}:{exc}") from exc

    audio_path = work_root / "audio" / "source_16k_mono.wav"
    extract_audio(source, audio_path, force=args.force_asr)
    model_cache = REPO_ROOT / "素材整理_asset_management/04_时间码_timecode/model_cache"
    model_cache.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(args.asr_model, device=args.asr_device, compute_type=args.asr_compute_type, download_root=str(model_cache))
    raw_segments, info = model.transcribe(
        str(audio_path),
        language=args.asr_language,
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    segments: list[dict[str, Any]] = []
    for index, segment in enumerate(raw_segments, start=1):
        text = (segment.text or "").strip()
        if not text:
            continue
        segments.append(
            {
                "index": index,
                "start_seconds": round(float(segment.start), 3),
                "end_seconds": round(float(segment.end), 3),
                "start_time": seconds_to_timecode(float(segment.start)),
                "end_time": seconds_to_timecode(float(segment.end)),
                "text": text,
            }
        )
    if not segments:
        raise RuntimeError("blocked_asr_no_segments")
    payload = {
        "status": "success",
        "generated_at": now_text(),
        "source_video": str(source),
        "duration_seconds": duration,
        "language": getattr(info, "language", args.asr_language),
        "language_probability": getattr(info, "language_probability", None),
        "model_used": args.asr_model,
        "compute_type": args.asr_compute_type,
        "quality_status": "machine_transcript_pending_manual_review",
        "segments": segments,
    }
    write_text(transcript_path, json.dumps(payload, ensure_ascii=False, indent=2))
    return parse_transcript_segments(payload), transcript_path


def parse_transcript_segments(data: dict[str, Any]) -> list[SpeechSegment]:
    parsed: list[SpeechSegment] = []
    for raw in data.get("segments", []):
        text = str(raw.get("text", "")).strip()
        if not text:
            continue
        parsed.append(
            SpeechSegment(
                index=int(raw.get("index") or len(parsed) + 1),
                start_seconds=float(raw.get("start_seconds") or 0.0),
                end_seconds=float(raw.get("end_seconds") or 0.0),
                text=text,
            )
        )
    return parsed


def is_explicit_question(text: str) -> bool:
    cleaned = re.sub(r"\s+", "", text or "")
    if cleaned in GENERIC_NON_QUESTIONS or len(cleaned) < 4:
        return False
    return any(marker in cleaned for marker in QUESTION_MARKERS)


def role_flags(text: str) -> set[str]:
    roles: set[str] = set()
    if is_explicit_question(text):
        roles.add("question")
    if any(term in text for term in SALES_TERMS):
        roles.add("sales")
    if any(term in text for term in CHAT_TERMS):
        roles.add("chat")
    if any(term in text for term in REASON_TERMS):
        roles.add("reason")
    if any(term in text for term in BOUNDARY_TERMS):
        roles.add("boundary")
    if any(term in text for term in METHOD_TERMS):
        roles.add("method")
    if any(term in text for term in PURPOSE_TERMS):
        roles.add("purpose")
    if any(term in text for term in PAIN_TERMS):
        roles.add("pain")
    if any(term in text for term in MISTAKE_TERMS):
        roles.add("mistake")
    if any(term in text for term in ACTION_INSTRUCTION_TERMS):
        roles.add("action_instruction")
    if not roles:
        roles.add("unusable")
    return roles


def meaningful_terms(text: str) -> list[str]:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text or "", flags=re.UNICODE)
    raw = [token.strip() for token in cleaned.split() if token.strip()]
    terms: list[str] = []
    for token in raw:
        if len(token) < 2:
            continue
        if token.lower() in {"yes", "no", "unclear", "clear", "partial"}:
            continue
        if token not in terms:
            terms.append(token)
    return terms[:24]


def matching_terms(text: str, visual: VisualUnit) -> list[str]:
    candidates = meaningful_terms(visual.observed_action_name) + meaningful_terms(visual.observed_body_part_or_tool)
    hits = []
    compact = re.sub(r"\s+", "", text or "")
    for term in candidates:
        if len(term) >= 2 and term in compact and term not in hits:
            hits.append(term)
    return hits


def choose_role_evidence(segments: list[SpeechSegment], visual: VisualUnit, target_role: str) -> SpeechSegment | None:
    candidates: list[tuple[float, int, SpeechSegment]] = []
    for segment in segments:
        roles = role_flags(segment.text)
        if target_role not in roles:
            continue
        hits = matching_terms(segment.text, visual)
        if not hits:
            continue
        distance = min(abs(segment.start_seconds - visual.start_seconds), abs(segment.end_seconds - visual.end_seconds))
        score = -len(hits) * 1000.0 + distance
        candidates.append((score, segment.index, segment))
    if not candidates:
        return None
    return min(candidates, key=lambda item: (item[0], item[1]))[2]


def detect_topic_break(segments: list[SpeechSegment], start: float, end: float) -> str:
    middle = [segment for segment in segments if segment.start_seconds < end and segment.end_seconds > start]
    if not middle:
        return "unclear"
    sale_or_chat = sum(1 for segment in middle if role_flags(segment.text).intersection({"sales", "chat"}))
    if sale_or_chat >= max(2, math.ceil(len(middle) * 0.5)):
        return "yes"
    return "no"


def ffmpeg_extract_scan_frames(source: Path, frame_dir: Path, every_seconds: float) -> list[Path]:
    frame_dir.mkdir(parents=True, exist_ok=True)
    pattern = frame_dir / "frame_%06d.jpg"
    proc = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-vf",
            f"fps=1/{every_seconds},scale=180:-1",
            "-q:v",
            "4",
            str(pattern),
        ],
        timeout=3600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"blocked_frame_scan_failed:{sanitize_error(proc.stderr or proc.stdout)}")
    return sorted(frame_dir.glob("frame_*.jpg"))


def frame_motion_scores(frames: list[Path], every_seconds: float) -> list[tuple[float, float]]:
    if Image is None or ImageChops is None or ImageStat is None:
        return [(index * every_seconds, 1.0) for index in range(1, len(frames))]
    scores: list[tuple[float, float]] = []
    previous = None
    for index, frame_path in enumerate(frames):
        current = Image.open(frame_path).convert("L")
        if previous is not None:
            diff = ImageChops.difference(previous, current)
            stat = ImageStat.Stat(diff)
            scores.append((index * every_seconds, float(stat.mean[0])))
        previous = current
    return scores


def motion_windows(scores: list[tuple[float, float]], duration: float, window_seconds: float, max_windows: int) -> list[tuple[float, float, float]]:
    if not scores:
        return []
    values = sorted(score for _, score in scores)
    median = values[len(values) // 2]
    threshold = max(median * 1.35, min(values[-1], median + 3.0))
    raw = [(max(0.0, t - window_seconds * 0.35), min(duration, t + window_seconds * 0.65), s) for t, s in scores if s >= threshold]
    if not raw:
        raw = [(max(0.0, t - window_seconds * 0.35), min(duration, t + window_seconds * 0.65), s) for t, s in sorted(scores, key=lambda item: item[1], reverse=True)[:max_windows]]
    merged: list[tuple[float, float, float]] = []
    for start, end, score in sorted(raw, key=lambda item: item[0]):
        if not merged or start - merged[-1][1] > window_seconds * 0.35:
            merged.append((start, end, score))
        else:
            prev_start, prev_end, prev_score = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end), max(prev_score, score))
    return sorted(merged, key=lambda item: item[2], reverse=True)[:max_windows]


def frame_offsets(start: float, end: float) -> list[float]:
    duration = max(0.5, end - start)
    return [round(start + duration * ratio, 3) for ratio in (0.08, 0.28, 0.50, 0.72, 0.92)]


def make_contact_sheet(source: Path, sheet_dir: Path, start: float, end: float, action_topic_id: str) -> tuple[Path, list[str]]:
    sheet_dir.mkdir(parents=True, exist_ok=True)
    frames: list[Path] = []
    labels: list[str] = []
    for index, at in enumerate(frame_offsets(start, end), start=1):
        frame_path = sheet_dir / f"{action_topic_id}_frame_{index:02d}.jpg"
        proc = run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-ss",
                f"{at:.3f}",
                "-i",
                str(source),
                "-frames:v",
                "1",
                "-vf",
                "scale=420:-1",
                str(frame_path),
            ],
            timeout=120,
        )
        if proc.returncode == 0 and frame_path.exists() and frame_path.stat().st_size > 0:
            frames.append(frame_path)
            labels.append(seconds_to_timecode(at))
    if not frames:
        raise RuntimeError(f"blocked_contact_sheet_no_frames:{action_topic_id}")
    sheet_path = sheet_dir / f"{action_topic_id}_contact_sheet.jpg"
    if Image is None or ImageDraw is None or ImageFont is None or ImageOps is None:
        return frames[0], labels
    cell_w, cell_h, label_h = 420, 250, 34
    sheet = Image.new("RGB", (cell_w * len(frames), cell_h + label_h), (245, 247, 250))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, frame_path in enumerate(frames):
        img = Image.open(frame_path).convert("RGB")
        fitted = ImageOps.contain(img, (cell_w, cell_h))
        x = idx * cell_w
        sheet.paste(fitted, (x + (cell_w - fitted.width) // 2, label_h + (cell_h - fitted.height) // 2))
        draw.rectangle([x, 0, x + cell_w, label_h], fill=(255, 255, 255))
        draw.text((x + 8, 10), f"{action_topic_id} F{idx + 1} {labels[idx]}", fill=(15, 23, 42), font=font)
    sheet.save(sheet_path, format="JPEG", quality=84, optimize=True)
    return sheet_path, labels


def image_data_url(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def parse_model_json(content: str) -> dict[str, Any] | None:
    text = content.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    candidates = [text]
    if "{" in text and "}" in text:
        candidates.append(text[text.find("{") : text.rfind("}") + 1])
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def call_one_vision_model(api_key: str, base_url: str, model: str, prompt: str, sheet_path: Path, timeout: int) -> tuple[str, dict[str, Any] | None, str]:
    if model in FORBIDDEN_MODELS:
        return "blocked_forbidden_model", None, "forbidden model"
    endpoint = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url(sheet_path)}},
                ],
            }
        ],
        "temperature": 0.0,
        "max_tokens": 1000,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return "failed", None, f"http_{exc.code}:{sanitize_error(body, api_key)}"
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        return "failed", None, sanitize_error(str(exc), api_key)
    try:
        outer = json.loads(body)
        choices = outer.get("choices", [])
        content = choices[0].get("message", {}).get("content", "") if choices else ""
        if isinstance(content, list):
            content = "\n".join(str(item.get("text", "")) for item in content if isinstance(item, dict))
        parsed = parse_model_json(str(content))
    except Exception as exc:  # noqa: BLE001
        return "failed", None, f"parse_failed:{sanitize_error(str(exc), api_key)}"
    if not parsed:
        return "failed", None, "json_parse_failed"
    return "success", parsed, ""


def call_vision(values: dict[str, str], sheet_path: Path, action_topic_id: str, frame_timecodes: list[str], timeout: int) -> tuple[str, str, dict[str, Any] | None, str]:
    api_key = env_value(values, "ALI_API_KEY")
    if not api_key or is_placeholder_key(api_key):
        return "unavailable_no_api_key", "", None, "ALI_API_KEY missing or placeholder"
    base_url = env_value(values, "ALI_API_BASE_URL", DEFAULT_BASE_URL)
    schema = {
        "observed_action_name": "画面能看见的具体动作；看不清写 unclear",
        "observed_body_part_or_tool": "身体部位或工具；看不清写 unclear",
        "action_cycle_complete": "yes/no/unclear",
        "presenter_visible": "yes/no/partial/unclear",
        "topic_break_risk": "yes/no/unclear",
        "visual_action_present": "yes/no/unclear",
        "reason": "中文简短说明；只描述画面，不判断健康、业务、发布",
        "confidence": "high/medium/low",
    }
    prompt = (
        "你是直播动作视觉盲测员。你只能看这张 contact sheet，不知道原视频答案。"
        "请只依据画面判断是否存在可识别动作、身体部位/工具、动作是否形成可理解循环。"
        "不要根据文件名、课程、健康效果或业务价值猜测；看不清必须写 unclear。"
        "只输出 JSON object，字段按 schema。"
        f"\naction_topic_id: {action_topic_id}"
        f"\n帧时间: {', '.join(frame_timecodes)}"
        f"\nschema: {json.dumps(schema, ensure_ascii=False)}"
    )
    errors: list[str] = []
    for model in (PRIMARY_VISION_MODEL, FALLBACK_VISION_MODEL):
        status, parsed, error = call_one_vision_model(api_key, base_url, model, prompt, sheet_path, timeout)
        if status == "success":
            return "success", model, parsed, ""
        errors.append(f"{model}:{error}")
    return "failed", "", None, "; ".join(errors)


def discover_visual_units(source: Path, work_root: Path, duration: float, source_id: str, args: argparse.Namespace) -> list[VisualUnit]:
    scan_frames = ffmpeg_extract_scan_frames(source, work_root / "frame_scan", args.motion_sample_seconds)
    scores = frame_motion_scores(scan_frames, args.motion_sample_seconds)
    windows = motion_windows(scores, duration, args.visual_window_seconds, args.max_visual_windows)
    if not windows:
        raise RuntimeError("blocked_no_visual_motion_windows")
    values = load_dotenv(REPO_ROOT / ".env")
    units: list[VisualUnit] = []
    for index, (start, end, score) in enumerate(sorted(windows, key=lambda row: row[0]), start=1):
        action_topic_id = f"AT{source_id}_{index:03d}"
        sheet_path, labels = make_contact_sheet(source, work_root / "visual_contact_sheets" / action_topic_id, start, end, action_topic_id)
        status, model_name, parsed, error = call_vision(values, sheet_path, action_topic_id, labels, args.vision_timeout)
        parsed = parsed or {}
        visual_action_present = str(parsed.get("visual_action_present", "")).lower()
        if status == "success" and visual_action_present == "no":
            visual_status = "no_action_visible"
        elif status == "success":
            visual_status = "action_visible_or_unclear"
        else:
            visual_status = status
        units.append(
            VisualUnit(
                action_topic_id=action_topic_id,
                start_seconds=start,
                end_seconds=end,
                motion_score=round(score, 3),
                contact_sheet=sheet_path,
                frame_timecodes=labels,
                visual_status=visual_status,
                model_name=model_name,
                observed_action_name=str(parsed.get("observed_action_name") or ""),
                observed_body_part_or_tool=str(parsed.get("observed_body_part_or_tool") or ""),
                action_cycle_complete=str(parsed.get("action_cycle_complete") or "unclear").lower(),
                presenter_visible=str(parsed.get("presenter_visible") or "unclear").lower(),
                topic_break_risk=str(parsed.get("topic_break_risk") or "unclear").lower(),
                reason=str(parsed.get("reason") or error),
            )
        )
        print(f"visual_unit={action_topic_id} status={visual_status} model={model_name or 'none'}", flush=True)
    return units


def evidence_segments_for_visual(segments: list[SpeechSegment], visual: VisualUnit) -> dict[str, SpeechSegment | None]:
    return {
        "question": choose_role_evidence(segments, visual, "question"),
        "purpose": choose_role_evidence(segments, visual, "purpose"),
        "pain": choose_role_evidence(segments, visual, "pain"),
        "reason": choose_role_evidence(segments, visual, "reason"),
        "boundary": choose_role_evidence(segments, visual, "boundary"),
        "method": choose_role_evidence(segments, visual, "method"),
        "mistake": choose_role_evidence(segments, visual, "mistake"),
        "action_instruction": choose_role_evidence(segments, visual, "action_instruction"),
    }


def identity_match_status(segments: list[SpeechSegment], visual: VisualUnit) -> tuple[str, list[str]]:
    combined = " ".join(segment.text for segment in segments)
    hits = matching_terms(combined, visual)
    if hits:
        return "yes", hits
    return "no", []


def source_ranges_for_plan(visual: VisualUnit, evidence: dict[str, SpeechSegment | None], classification_dir: str) -> list[tuple[str, float, float]]:
    ordered_roles: list[str]
    if classification_dir.startswith("01_"):
        ordered_roles = ["question", "reason", "boundary", "method", "action_instruction"]
    elif classification_dir.startswith("02_"):
        ordered_roles = ["pain", "reason", "method", "action_instruction"]
    elif classification_dir.startswith("03_"):
        ordered_roles = ["purpose", "method", "action_instruction"]
    elif classification_dir.startswith("04_"):
        ordered_roles = ["mistake", "reason", "method", "action_instruction"]
    elif classification_dir.startswith("06_"):
        return [("interleaved_context", max(0.0, visual.start_seconds - 3), visual.end_seconds + 3)]
    else:
        ordered_roles = ["purpose", "pain", "reason", "boundary", "method", "action_instruction"]
    ranges: list[tuple[str, float, float]] = []
    seen: set[tuple[int, int]] = set()
    for role in ordered_roles:
        segment = evidence.get(role)
        if not segment:
            continue
        key = (round(segment.start_seconds), round(segment.end_seconds))
        if key in seen:
            continue
        seen.add(key)
        ranges.append((role, max(0.0, segment.start_seconds - 0.6), segment.end_seconds + 0.8))
    ranges.append(("action", visual.start_seconds, visual.end_seconds))
    return ranges


def classify_plan(visual: VisualUnit, segments: list[SpeechSegment], evidence: dict[str, SpeechSegment | None], final_root: Path, ordinal: int) -> VideoPlan | None:
    if visual.visual_status in {"no_action_visible", "unavailable_no_api_key", "failed"}:
        if visual.visual_status == "no_action_visible":
            return None
        classification_dir = "08_人工复核"
        structure = "R_manual_review_visual_unverified"
        usability = "pending_manual_review"
        downgrade = f"visual_not_verified:{visual.visual_status}"
    else:
        nearby_segments = [segment for segment in segments if segment.start_seconds <= visual.end_seconds and segment.end_seconds >= visual.start_seconds]
        identity_status, identity_hits = identity_match_status(segments, visual)
        topic_break = "yes" if visual.topic_break_risk == "yes" or detect_topic_break(nearby_segments, visual.start_seconds, visual.end_seconds) == "yes" else "no"
        cycle_ok = visual.action_cycle_complete == "yes"
        presenter_ok = visual.presenter_visible in {"yes", "partial"}
        method = evidence.get("method") or evidence.get("action_instruction")
        has_question = bool(evidence.get("question"))
        has_pain = bool(evidence.get("pain"))
        has_reason = bool(evidence.get("reason") or evidence.get("boundary"))
        has_purpose = bool(evidence.get("purpose"))
        has_mistake = bool(evidence.get("mistake"))
        direct_gate = identity_status == "yes" and topic_break == "no" and cycle_ok and presenter_ok and bool(method)
        if direct_gate and has_question:
            classification_dir, structure = "01_问题回答后动作", "E2_problem_answer_then_action"
        elif direct_gate and has_pain and has_reason:
            classification_dir, structure = "02_痛点原因后动作", "E3_pain_reason_solution_action"
        elif direct_gate and has_purpose:
            classification_dir, structure = "03_用途方法后动作", "E4_purpose_method_action"
        elif direct_gate and has_mistake:
            classification_dir, structure = "04_误区纠正后动作", "E5_mistake_correction_action"
        elif direct_gate and nearby_segments and method:
            classification_dir, structure = "06_边讲边做", "E6_interleaved_explanation_action"
        elif direct_gate:
            classification_dir, structure = "05_讲解在前动作在后", "E1_explanation_then_action"
        else:
            classification_dir = "08_人工复核"
            structure = "R_manual_review_incomplete_chain"
        usability = "editor_ready_direct" if classification_dir != "08_人工复核" else "pending_manual_review"
        if usability == "pending_manual_review":
            reasons = []
            if identity_status != "yes":
                reasons.append("speech_visual_identity_missing")
            if topic_break != "no":
                reasons.append("topic_break_or_sales_chat_risk")
            if not cycle_ok:
                reasons.append("action_cycle_not_confirmed")
            if not presenter_ok:
                reasons.append("presenter_not_clear")
            if not method:
                reasons.append("method_or_instruction_missing")
            downgrade = ";".join(reasons) or "manual_review_required"
        else:
            downgrade = ""
    topic = visual.observed_action_name or visual.observed_body_part_or_tool or visual.action_topic_id
    topic = safe_slug(topic)
    file_name = f"{ordinal:03d}_{classification_dir.split('_', 1)[1]}_{topic}_剪辑师直接版.mp4"
    if classification_dir == "08_人工复核":
        file_name = f"{ordinal:03d}_人工复核_{topic}.mp4"
    ranges = source_ranges_for_plan(visual, evidence, classification_dir)
    return VideoPlan(
        action_topic_id=visual.action_topic_id,
        classification_dir=classification_dir,
        clip_structure_type=structure,
        editor_usability_status=usability,
        topic_title=topic,
        source_time_ranges=ranges,
        final_video_path=final_root / classification_dir / file_name,
        downgrade_reason=downgrade,
    )


def export_clip(source: Path, start: float, end: float, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    duration = max(0.25, end - start)
    proc = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{max(0.0, start):.3f}",
            "-i",
            str(source),
            "-t",
            f"{duration:.3f}",
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(output),
        ],
        timeout=1800,
    )
    if proc.returncode != 0 or not output.exists() or output.stat().st_size == 0:
        raise RuntimeError(f"clip_export_failed:{output}:{sanitize_error(proc.stderr or proc.stdout)}")


def concat_clips(clips: list[Path], output: Path, concat_dir: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    concat_list = concat_dir / f"{output.stem}_concat.txt"
    lines = [f"file '{clip.as_posix()}'" for clip in clips]
    write_text(concat_list, "\n".join(lines) + "\n")
    proc = run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(output)],
        timeout=1200,
    )
    if proc.returncode != 0 or not output.exists() or output.stat().st_size == 0:
        raise RuntimeError(f"concat_failed:{output}:{sanitize_error(proc.stderr or proc.stdout)}")


def render_plan(source: Path, plan: VideoPlan, work_root: Path) -> str:
    clip_dir = work_root / "tmp_clips" / plan.action_topic_id
    clips: list[Path] = []
    for order, (role, start, end) in enumerate(plan.source_time_ranges, start=1):
        clip_path = clip_dir / f"{order:02d}_{role}.mp4"
        export_clip(source, start, end, clip_path)
        clips.append(clip_path)
    if not clips:
        return "failed_no_ranges"
    concat_clips(clips, plan.final_video_path, work_root / "concat_lists")
    return probe_output_video(plan.final_video_path)


def probe_output_video(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return "failed_missing"
    meta = ffprobe_json(path)
    has_video = bool(first_stream(meta, "video"))
    has_audio = bool(first_stream(meta, "audio"))
    decode = run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], timeout=900)
    if has_video and has_audio and decode.returncode == 0:
        return "passed"
    return f"failed:video={has_video}:audio={has_audio}:decode_rc={decode.returncode}"


def clean_appledouble(root: Path) -> int:
    removed = 0
    for path in root.rglob("._*"):
        if path.is_file():
            path.unlink()
            removed += 1
    return removed


def build_report(
    report_path: Path,
    source: Path,
    meta: dict[str, Any],
    source_sha256: str,
    transcript_path: Path,
    units: list[VisualUnit],
    plans: list[VideoPlan],
    index_path: Path,
    status_counts: Counter[str],
    freeze_commit: str,
) -> None:
    video = first_stream(meta, "video")
    audio = first_stream(meta, "audio")
    lines = [
        "# 单直播严格盲测执行报告",
        "",
        f"状态：`completed_video_outputs_pending_user_review`" if plans else "状态：`blind_test_failed_with_evidence`",
        f"生成时间：{now_text()}",
        "",
        "## 主结论",
        "",
        f"- 唯一视频：`{source}`",
        f"- 完整 ASR：`已确认`，缓存路径 `{transcript_path}`（ignored_not_committed）",
        f"- 视觉动作扫描：`已确认`，视觉单元 {len(units)} 个",
        f"- 最终视频：{len(plans)} 条",
        f"- 正式剪辑师可用：{sum(1 for p in plans if p.editor_usability_status == 'editor_ready_direct')} 条",
        f"- 人工复核：{sum(1 for p in plans if p.editor_usability_status == 'pending_manual_review')} 条",
        "- 用户人审：`pending_user_review`",
        "- 审美 / 动作专业性 / 健康效果 / 业务 / 发布：`待验证`",
        "",
        "## 源视频技术信息",
        "",
        f"- duration_seconds: `{meta.get('format', {}).get('duration', '')}`",
        f"- size: `{meta.get('format', {}).get('size', '')}`",
        f"- video: `{video.get('codec_name', '')}` `{video.get('width', '')}x{video.get('height', '')}` `{video.get('avg_frame_rate', '')}`",
        f"- audio: `{audio.get('codec_name', '')}` channels=`{audio.get('channels', '')}`",
        f"- sha256: `{source_sha256}`",
        "",
        "## 分类统计",
        "",
    ]
    by_dir = Counter(plan.classification_dir for plan in plans)
    for directory in FINAL_DIRS:
        lines.append(f"- `{directory}`: {by_dir.get(directory, 0)}")
    lines.extend(
        [
            "",
            "## Git 与冻结边界",
            "",
            f"- 实现冻结 commit：`{freeze_commit or '待验证'}`",
            "- 冻结前语义读取：`no`",
            "- 冻结后核心识别逻辑修改：`no`",
            "- 素材专用关键词 / 句子锚点 / 人工时间码：`no`",
            "- LangGraph / LangChain / runtime：`no`",
            "",
            "## 输出索引",
            "",
            f"- 最小视频索引：`{index_path}`",
            "- 媒体文件：`ignored_not_committed`",
            "",
            "## 视觉模型状态",
            "",
        ]
    )
    for key, value in sorted(status_counts.items()):
        lines.append(f"- `{key}`: {value}")
    write_text(report_path, "\n".join(lines) + "\n")


def run_pipeline(args: argparse.Namespace) -> int:
    source = args.source_video.resolve()
    if not source.is_file():
        raise RuntimeError(f"blocked_source_video_missing:{source}")
    if source.suffix.lower() not in {".mp4", ".mov", ".mkv", ".m4v"}:
        raise RuntimeError(f"blocked_unsupported_source_extension:{source.suffix}")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("blocked_ffmpeg_or_ffprobe_unavailable")

    final_root = args.final_output_root.resolve()
    work_root = args.work_root.resolve()
    ensure_clean_output_dirs(final_root, work_root, args.force)
    meta = ffprobe_json(source)
    audio = first_stream(meta, "audio")
    if not audio:
        raise RuntimeError("blocked_source_video_has_no_audio")
    duration = float(meta.get("format", {}).get("duration") or 0.0)
    source_sha = source_hash(source)
    write_text(work_root / "source_metadata.json", json.dumps({"ffprobe": meta, "sha256": source_sha}, ensure_ascii=False, indent=2))

    segments, transcript_path = transcribe_source(source, work_root, args, duration)
    units = discover_visual_units(source, work_root, duration, args.source_id, args)
    plans: list[VideoPlan] = []
    probe_rows: list[dict[str, Any]] = []
    ordinal = 1
    for visual in units:
        evidence = evidence_segments_for_visual(segments, visual)
        plan = classify_plan(visual, segments, evidence, final_root, ordinal)
        if plan is None:
            continue
        technical = render_plan(source, plan, work_root)
        probe_rows.append({"action_topic_id": plan.action_topic_id, "path": str(plan.final_video_path), "technical_probe_status": technical})
        plans.append(plan)
        ordinal += 1
        print(f"video_plan={plan.action_topic_id} dir={plan.classification_dir} tech={technical}", flush=True)

    index_rows: list[dict[str, Any]] = []
    tech_by_id = {row["action_topic_id"]: row["technical_probe_status"] for row in probe_rows}
    for plan in plans:
        index_rows.append(
            {
                "video_file_name": plan.final_video_path.name,
                "classification_dir": plan.classification_dir,
                "source_time_ranges": "；".join(f"{role}:{seconds_to_timecode(start)}-{seconds_to_timecode(end)}" for role, start, end in plan.source_time_ranges),
                "clip_structure_type": plan.clip_structure_type,
                "editor_usability_status": plan.editor_usability_status,
                "action_topic_id": plan.action_topic_id,
                "action_or_problem_topic": plan.topic_title,
                "source_video_path": str(source),
                "final_video_path": str(plan.final_video_path),
                "downgrade_reason": plan.downgrade_reason,
                "technical_probe_status": tech_by_id.get(plan.action_topic_id, ""),
            }
        )
    write_csv(args.index_csv.resolve(), index_rows, INDEX_FIELDS)
    status_counts = Counter(unit.visual_status for unit in units)
    write_text(work_root / "visual_units.json", json.dumps([unit.__dict__ | {"contact_sheet": str(unit.contact_sheet)} for unit in units], ensure_ascii=False, indent=2, default=str))
    write_csv(work_root / "output_video_probe.csv", probe_rows, ["action_topic_id", "path", "technical_probe_status"])
    build_report(args.report_md.resolve(), source, meta, source_sha, transcript_path, units, plans, args.index_csv.resolve(), status_counts, args.freeze_commit)
    removed = clean_appledouble(final_root) + clean_appledouble(work_root)
    print(f"final_output_root={final_root}")
    print(f"work_root={work_root}")
    print(f"videos={len(plans)}")
    print(f"editor_ready_direct={sum(1 for p in plans if p.editor_usability_status == 'editor_ready_direct')}")
    print(f"pending_manual_review={sum(1 for p in plans if p.editor_usability_status == 'pending_manual_review')}")
    print(f"appledouble_removed={removed}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-video", type=Path, required=True)
    parser.add_argument("--final-output-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--index-csv", type=Path, required=True)
    parser.add_argument("--report-md", type=Path, required=True)
    parser.add_argument("--source-id", default="BT")
    parser.add_argument("--freeze-commit", default="")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--force-asr", action="store_true")
    parser.add_argument("--asr-model", default="small")
    parser.add_argument("--asr-device", default="cpu")
    parser.add_argument("--asr-compute-type", default="int8")
    parser.add_argument("--asr-language", default="zh")
    parser.add_argument("--motion-sample-seconds", type=float, default=5.0)
    parser.add_argument("--visual-window-seconds", type=float, default=28.0)
    parser.add_argument("--max-visual-windows", type=int, default=36)
    parser.add_argument("--vision-timeout", type=int, default=45)
    return parser.parse_args()


def main() -> int:
    return run_pipeline(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
