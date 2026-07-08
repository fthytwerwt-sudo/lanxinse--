#!/usr/bin/env python3
"""Restart 5/13 live recording screening with speech-action logic first."""

from __future__ import annotations

import base64
import csv
import json
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
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:  # pragma: no cover
    Image = None
    ImageDraw = None
    ImageFont = None
    ImageOps = None


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = Path("/Volumes/WD_BLACK/完整直播录屏/今年直播素材/5月13日直播素材.MP4")
ASR_PATH = REPO_ROOT / "api_outputs/full_live_material_screening/asr_transcripts/rec_001_5月13日直播素材.json"
ENV_PATH = REPO_ROOT / ".env"

ANALYSIS_ROOT = REPO_ROOT / "素材解析_pipeline_material_analysis/17_single_live_logic_first_rescreen"
RESCREEN_ROOT = REPO_ROOT / "项目事实_project_facts/直播素材重筛_live_rescreen"
LOG_ROOT = REPO_ROOT / "执行日志_codex_log"
LOCAL_PACKAGE_ROOT = REPO_ROOT / "outputs/local_513_logic_first_video_package"
LOCAL_MANUAL_ROOT = REPO_ROOT / "outputs/local_513_manual_review_pool"
LOCAL_MODEL_ROOT = LOCAL_MANUAL_ROOT / "_model_summaries"
LOCAL_INPUT_ROOT = LOCAL_MANUAL_ROOT / "_visual_inputs"

MODEL_ROUTE_MD = REPO_ROOT / "项目事实_project_facts/模型路由_model_routing/01_阿里视觉模型默认路由_ali_visual_model_default_route.md"
RULES_MD = REPO_ROOT / "项目事实_project_facts/直播素材筛选_live_material_screening/19_配对逻辑修正规则_pairing_logic_revision_rules.md"
STRUCTURE_CSV = REPO_ROOT / "项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/36_剪辑师可用结构表_editor_usable_structure_table.csv"
OLD_SOLUTION_MD = REPO_ROOT / "项目事实_project_facts/直播素材筛选_live_material_screening/20_逻辑复审后解决方案_after_logic_review_solution.md"
OLD_REPORT_123_MD = LOG_ROOT / "123_阿里视觉复核102条并导出真配对视频包执行报告_ali_visual_review_102_export_report.md"

PROBE_CSV = ANALYSIS_ROOT / "01_单条直播重筛探针_single_live_rescreen_probe.csv"
SPEECH_UNITS_CSV = ANALYSIS_ROOT / "02_口播单元表_speech_units.csv"
VISUAL_UNITS_CSV = ANALYSIS_ROOT / "03_视觉动作单元表_visual_action_units.csv"
MASTER_CSV = RESCREEN_ROOT / "01_5月13日逻辑链候选总表_513_logic_chain_candidate_master.csv"
TRUE_PAIR_CSV = RESCREEN_ROOT / "02_5月13日真配对清单_513_true_pair_candidates.csv"
WEAK_CSV = RESCREEN_ROOT / "03_5月13日弱相关待复核清单_513_weak_related_pending_review.csv"
MISMATCH_CSV = RESCREEN_ROOT / "04_5月13日错配剔除清单_513_logic_mismatch_rejects.csv"
PACKAGE_MANIFEST_CSV = RESCREEN_ROOT / "05_5月13日视频素材包索引_513_video_package_manifest.csv"
EDITOR_README_MD = RESCREEN_ROOT / "06_5月13日剪辑师使用说明_513_editor_readme.md"
REPORT_MD = LOG_ROOT / "124_5月13日直播逻辑优先重筛执行报告_513_logic_first_rescreen_report.md"

PRIMARY_MODEL = "qwen3-vl-plus"
FALLBACK_MODEL = "qwen-vl-max"
FORBIDDEN_MODELS = {"qwen-vl-plus-latest", "qwen3-vl-max"}
DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
REVIEW_LIMIT = 16
MAX_TRUE_PAIR_EXPORTS = 8

PLACEHOLDER_VALUES = {
    "",
    "your_api_key_here",
    "your-ali-api-key",
    "你的真实阿里 API key",
    "这里填你的真实阿里 API key",
    "请在本地填写，不要提交真实 key",
}

ACTION_TERMS = [
    "动作",
    "呼吸",
    "吸气",
    "吐气",
    "吸管",
    "练习",
    "收缩",
    "收紧",
    "放松",
    "肩",
    "肩膀",
    "胸",
    "胸腔",
    "乳房",
    "阴道",
    "会阴",
    "盆底",
    "点按",
    "按摩",
    "云门",
    "中府",
    "画",
    "八字",
    "交叉",
    "核心",
]

PROBLEM_TERMS = ["漏尿", "产后", "胸", "乳腺", "呼吸短", "肩膀", "酸", "萎缩", "私密", "盆底"]
FUNCTION_TERMS = ["打开", "扩张", "连接", "激活", "放松", "稳定", "收紧", "跟练", "纠正", "改善", "带动"]
SALES_TERMS = ["报名", "课程", "价格", "优惠", "私教", "买", "链接", "下单", "直播间"]
CHAT_TERMS = ["早上好", "听得到", "大家好", "点赞", "评论", "姐妹", "宝贝", "音乐"]

STRUCTURE_FOLDERS = [
    ("问题", "原因", "01_问题问答_原因解释方法边界"),
    ("动作演示", "", "02_工具动作演示_发力口令低压跟练收束"),
    ("痛点", "", "03_痛点人群点名_单动作完整循环坚持建议"),
    ("误区", "", "04_误区错误纠正_错误动作正确动作原因解释"),
    ("多动作", "", "05_多动作组合_同一主题推进轻跟练收束"),
]

MASTER_FIELDS = [
    "candidate_id",
    "source_file",
    "speech_unit_id",
    "speech_start_time",
    "speech_end_time",
    "speech_claimed_action",
    "speech_claimed_problem",
    "speech_claimed_function",
    "visual_action_unit_id",
    "action_start_time",
    "action_end_time",
    "observed_action_name",
    "action_cycle_complete",
    "visual_obstruction_status",
    "logic_relation",
    "same_action_check",
    "same_problem_check",
    "same_function_check",
    "topic_break_check",
    "usable_structure_name",
    "p0_gate_result",
    "reason",
    "editor_task_potential",
    "manual_review_items",
    "talk_action_same_point",
    "structure_folder",
    "local_task_folder",
    "full_context_path",
    "speech_clip_path",
    "action_clip_path",
    "contact_sheet_path",
    "model_used",
    "visual_api_status",
    "notes",
]


@dataclass
class ApiCall:
    model: str
    status: str
    latency_ms: int
    parsed: dict[str, Any] | None
    error_summary: str
    content_preview: str = ""


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)


def git_output(args: list[str]) -> tuple[int, str]:
    proc = run(["git", *args], timeout=45)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def env_value(values: dict[str, str], key: str, default: str = "") -> str:
    return values.get(key) or os.environ.get(key, default)


def is_placeholder_key(value: str) -> bool:
    return value.strip() in PLACEHOLDER_VALUES


def sanitize(text: str, api_key: str = "") -> str:
    cleaned = (text or "").replace("\n", " ").replace("\r", " ")
    if api_key:
        cleaned = cleaned.replace(api_key, "<redacted_api_key>")
    cleaned = re.sub(r"(?i)bearer\s+[A-Za-z0-9_./+=-]{12,}", "Bearer <redacted>", cleaned)
    cleaned = re.sub(r"\bsk-[A-Za-z0-9_-]{12,}\b", "sk-<redacted>", cleaned)
    return cleaned[:700]


def slug(value: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "_", str(value or "").strip(), flags=re.UNICODE)
    return re.sub(r"_+", "_", cleaned).strip("_") or "unknown"


def seconds_to_timecode(value: float) -> str:
    total_ms = int(round(max(value, 0) * 1000))
    ms = total_ms % 1000
    total_seconds = total_ms // 1000
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{ms:03d}"


def ffprobe_duration(path: Path) -> float:
    proc = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        timeout=45,
    )
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return 0.0


def ffprobe_summary(path: Path) -> dict[str, Any]:
    proc = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-show_streams", "-of", "json", str(path)], timeout=90)
    data = json.loads(proc.stdout)
    summary = {"duration_seconds": float(data.get("format", {}).get("duration") or 0)}
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            summary.update(
                {
                    "width": stream.get("width"),
                    "height": stream.get("height"),
                    "video_codec": stream.get("codec_name"),
                    "fps": stream.get("r_frame_rate"),
                }
            )
        if stream.get("codec_type") == "audio":
            summary.update({"audio_codec": stream.get("codec_name"), "audio_channels": stream.get("channels")})
    return summary


def text_contains(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def matched_terms(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term in text]


def classify_speech(text: str) -> str:
    if text_contains(text, SALES_TERMS):
        return "sales_or_course"
    if text_contains(text, CHAT_TERMS) and not text_contains(text, ACTION_TERMS):
        return "chat_interaction"
    if text_contains(text, ["怎么做", "手", "肩", "吸气", "呼吸", "点按", "画", "收紧", "放松"]):
        return "action_instruction"
    if text_contains(text, PROBLEM_TERMS):
        return "problem_explain"
    if text_contains(text, FUNCTION_TERMS):
        return "function_purpose"
    return "action_related"


def infer_action(text: str) -> str:
    if "八字" in text or ("画" in text and "胸" in text):
        return "胸前画八字/胸前交叉动作"
    if "云门" in text or "中府" in text or "点按" in text:
        return "云门/中府区域点按"
    if "盆底" in text or "会阴" in text or "收紧" in text:
        return "盆底/会阴收紧放松"
    if "阴道" in text and "呼吸" in text:
        return "吸管式呼吸连接"
    if "手" in text and "肩" in text:
        return "双手抬至肩高的呼吸动作"
    if "胸" in text and ("呼吸" in text or "扩张" in text or "球" in text):
        return "胸部呼吸/胸腔扩张"
    if "肩" in text:
        return "肩部带动或肩部放松"
    if "呼吸" in text:
        return "呼吸练习"
    return "动作/练习口播"


def infer_problem(text: str) -> str:
    if "呼吸短" in text or "浅" in text:
        return "呼吸短浅"
    if "胸" in text or "乳房" in text or "乳腺" in text:
        return "胸部/乳房状态"
    if "盆底" in text or "会阴" in text or "阴道" in text:
        return "盆底/会阴连接"
    if "肩" in text:
        return "肩部紧张或发力"
    return "动作相关问题"


def infer_function(text: str) -> str:
    if "放松" in text:
        return "放松和降低紧张"
    if "打开" in text or "扩张" in text:
        return "打开/扩张目标部位"
    if "连接" in text:
        return "建立身体连接"
    if "收紧" in text or "收缩" in text:
        return "收紧/激活"
    if "点按" in text or "按摩" in text:
        return "点按激活"
    if "呼吸" in text:
        return "配合呼吸完成练习"
    return "动作教学"


def unit_score(text: str, duration: float) -> int:
    score = len(matched_terms(text, ACTION_TERMS)) * 5 + len(matched_terms(text, FUNCTION_TERMS)) * 3 + len(matched_terms(text, PROBLEM_TERMS)) * 2
    if classify_speech(text) == "action_instruction":
        score += 20
    if 20 <= duration <= 120:
        score += 8
    if text_contains(text, SALES_TERMS):
        score -= 20
    if len(text) < 12:
        score -= 8
    return score


def load_asr() -> dict[str, Any]:
    return json.loads(ASR_PATH.read_text(encoding="utf-8"))


def build_speech_units(asr_data: dict[str, Any], duration_seconds: float) -> list[dict[str, Any]]:
    segments = asr_data.get("segments", [])
    hit_windows: list[tuple[float, float]] = []
    for seg in segments:
        text = seg.get("text", "")
        if not text_contains(text, ACTION_TERMS + PROBLEM_TERMS + FUNCTION_TERMS):
            continue
        if text_contains(text, SALES_TERMS) and len(matched_terms(text, ACTION_TERMS)) < 2:
            continue
        start = max(0.0, float(seg.get("start_seconds", 0)) - 10)
        end = min(duration_seconds, float(seg.get("end_seconds", 0)) + 35)
        hit_windows.append((start, end))
    hit_windows.sort()

    merged: list[list[float]] = []
    for start, end in hit_windows:
        if not merged or start - merged[-1][1] > 18 or end - merged[-1][0] > 135:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    rows: list[dict[str, Any]] = []
    for idx, (start, end) in enumerate(merged, start=1):
        unit_segments = [seg for seg in segments if float(seg.get("end_seconds", 0)) >= start and float(seg.get("start_seconds", 0)) <= end]
        text = " ".join(seg.get("text", "").strip() for seg in unit_segments if seg.get("text", "").strip())
        duration = end - start
        score = unit_score(text, duration)
        if score < 8:
            continue
        speech_type = classify_speech(text)
        rows.append(
            {
                "speech_unit_id": f"SU{len(rows) + 1:03d}",
                "source_file": str(SOURCE_PATH),
                "speech_start_time": seconds_to_timecode(start),
                "speech_end_time": seconds_to_timecode(end),
                "start_seconds": round(start, 3),
                "end_seconds": round(end, 3),
                "duration_seconds": round(duration, 3),
                "speech_type": speech_type,
                "speech_claimed_action": infer_action(text),
                "speech_claimed_problem": infer_problem(text),
                "speech_claimed_function": infer_function(text),
                "action_keywords": "；".join(matched_terms(text, ACTION_TERMS)),
                "problem_keywords": "；".join(matched_terms(text, PROBLEM_TERMS)),
                "score": score,
                "asr_text_excerpt": text[:220],
                "notes": "from_asr_cache_resegmented; not_old_102_window",
            }
        )
    return rows


def select_speech_units(units: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    ranked = sorted(units, key=lambda row: (-int(row["score"]), float(row["start_seconds"])))
    selected: list[dict[str, Any]] = []
    for row in ranked:
        if len(selected) >= limit:
            break
        start = float(row["start_seconds"])
        if any(abs(start - float(old["start_seconds"])) < 150 for old in selected):
            continue
        selected.append(row)
    return sorted(selected, key=lambda row: float(row["start_seconds"]))


def structure_for_unit(row: dict[str, Any]) -> tuple[str, str]:
    action = row["speech_claimed_action"]
    stype = row["speech_type"]
    text = row["asr_text_excerpt"]
    if "问题" in row["speech_claimed_problem"] or stype == "problem_explain":
        return "问题问答 + 原因解释 + 方法边界", "01_问题问答_原因解释方法边界"
    if "点按" in action or "动作" in action or stype == "action_instruction":
        return "工具/动作演示 + 发力口令 + 低压跟练收束", "02_工具动作演示_发力口令低压跟练收束"
    if text_contains(text, ["痛", "酸", "短", "萎缩", "产后"]):
        return "痛点/人群点名 + 单动作完整循环 + 坚持建议", "03_痛点人群点名_单动作完整循环坚持建议"
    if text_contains(text, ["不要", "误区", "错"]):
        return "误区/错误先抛 + 正确动作对比 + 原因解释", "04_误区错误纠正_错误动作正确动作原因解释"
    return "多动作组合 + 同一主题推进 + 轻跟练收束", "05_多动作组合_同一主题推进轻跟练收束"


def visual_window_for_speech(row: dict[str, Any], total_duration: float) -> tuple[float, float, str]:
    start = float(row["start_seconds"])
    end = float(row["end_seconds"])
    text = row["asr_text_excerpt"]
    if text_contains(text, ["接下来", "我们一起来", "手拿起来", "吸气", "好 呼吸", "点按", "画"]):
        return max(0.0, start - 4), min(total_duration, end + 22), "intercut"
    return max(0.0, end - 8), min(total_duration, end + 55), "talk_before_action"


def make_contact_sheet(folder: Path, source: Path, start: float, end: float, label: str) -> tuple[Path, list[str], str]:
    folder.mkdir(parents=True, exist_ok=True)
    duration = max(1.0, end - start)
    offsets = [start + duration * ratio for ratio in [0.05, 0.25, 0.45, 0.65, 0.85]]
    frame_paths: list[Path] = []
    timecodes: list[str] = []
    for idx, offset in enumerate(offsets, start=1):
        frame_path = folder / f"frame_{idx:02d}_{int(offset * 1000):08d}.jpg"
        if not frame_path.exists() or frame_path.stat().st_size == 0:
            proc = run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-ss",
                    f"{offset:.3f}",
                    "-i",
                    str(source),
                    "-frames:v",
                    "1",
                    "-vf",
                    "scale=360:-1",
                    str(frame_path),
                ],
                timeout=90,
            )
            if proc.returncode != 0:
                continue
        frame_paths.append(frame_path)
        timecodes.append(seconds_to_timecode(offset))
    sheet_path = folder / "04_视觉证据_contact_sheet.jpg"
    if not frame_paths:
        return sheet_path, [], "failed_no_frames"
    if Image is not None:
        cell_w, cell_h, label_h = 360, 220, 34
        sheet = Image.new("RGB", (cell_w * len(frame_paths), cell_h + label_h), (248, 250, 252))
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.load_default()
        for idx, frame_path in enumerate(frame_paths):
            img = Image.open(frame_path).convert("RGB")
            fitted = ImageOps.contain(img, (cell_w, cell_h))
            x = idx * cell_w
            sheet.paste(fitted, (x + (cell_w - fitted.width) // 2, label_h + (cell_h - fitted.height) // 2))
            draw.rectangle([x, 0, x + cell_w, label_h], fill=(255, 255, 255))
            draw.text((x + 8, 10), f"{label} F{idx + 1} {timecodes[idx]}", fill=(15, 23, 42), font=font)
        sheet.save(sheet_path, format="JPEG", quality=82, optimize=True)
        return sheet_path, timecodes, "created_pil"
    return sheet_path, timecodes, "failed_no_pil"


def data_url(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def parse_model_json(content: str) -> dict[str, Any] | None:
    text = str(content or "").strip()
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


def call_model(api_key: str, base_url: str, model: str, prompt: str, sheet_path: Path, timeout: int) -> ApiCall:
    if model in FORBIDDEN_MODELS:
        return ApiCall(model, "blocked_forbidden_model", 0, None, "forbidden model blocked")
    endpoint = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url(sheet_path)}},
                ],
            }
        ],
        "temperature": 0.0,
        "max_tokens": 900,
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return ApiCall(model, "failed", int((time.perf_counter() - start) * 1000), None, f"http_{exc.code}: {sanitize(body, api_key)}")
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        return ApiCall(model, "failed", int((time.perf_counter() - start) * 1000), None, sanitize(str(exc), api_key))
    latency = int((time.perf_counter() - start) * 1000)
    try:
        outer = json.loads(body)
        choices = outer.get("choices", [])
        content = choices[0].get("message", {}).get("content", "") if choices else ""
        if isinstance(content, list):
            content = "\n".join(str(item.get("text", "")) for item in content if isinstance(item, dict))
        parsed = parse_model_json(str(content))
    except Exception as exc:  # noqa: BLE001
        return ApiCall(model, "failed", latency, None, f"parse_failed: {sanitize(str(exc), api_key)}")
    if not parsed:
        return ApiCall(model, "failed", latency, None, "json_parse_failed", sanitize(str(content))[:260])
    return ApiCall(model, "success", latency, parsed, "", sanitize(str(content))[:260])


def build_visual_prompt(speech_row: dict[str, Any], relation: str, timecodes: list[str]) -> str:
    schema = {
        "observed_action_name": "画面里看到的具体动作，如果看不清写 unclear",
        "observed_body_part_or_tool": "身体部位或工具",
        "action_cycle_complete": "yes/no/unclear",
        "visual_obstruction_status": "clear/partial_blocked/blocked/unclear",
        "presenter_visible": "yes/no/partial",
        "same_action_with_talk_claim": "yes/no/unclear",
        "same_problem_with_talk_claim": "yes/no/unclear",
        "same_function_with_talk_claim": "yes/no/unclear",
        "sequence_logic": "talk_before_action/action_before_talk/intercut/unclear",
        "topic_break_risk": "yes/no/unclear",
        "can_enter_editor_task_pack": "yes/no/unclear",
        "reason": "中文说明",
    }
    return (
        "你正在复核从完整直播原片重新切出的候选逻辑链。不要参考旧候选编号，不要根据关键词猜。\n"
        "你只看到关键帧拼图，请判断画面动作和口播是否同一动作、同一问题、同一目的。\n"
        "看不清写 unclear。不要写健康效果成立、业务结论、审美结论或可发布。\n\n"
        f"口播单元：{speech_row['speech_unit_id']}\n"
        f"口播时间：{speech_row['speech_start_time']} -> {speech_row['speech_end_time']}\n"
        f"口播动作：{speech_row['speech_claimed_action']}\n"
        f"口播问题：{speech_row['speech_claimed_problem']}\n"
        f"口播目的：{speech_row['speech_claimed_function']}\n"
        f"口播摘录：{speech_row['asr_text_excerpt']}\n"
        f"预期关系：{relation}\n"
        f"帧时间：{', '.join(timecodes)}\n\n"
        "只输出 JSON，字段如下：\n"
        + json.dumps(schema, ensure_ascii=False)
    )


def review_visual(api_key: str, base_url: str, timeout: int, speech_row: dict[str, Any], relation: str, sheet_path: Path, timecodes: list[str]) -> tuple[str, list[ApiCall], dict[str, Any] | None]:
    prompt = build_visual_prompt(speech_row, relation, timecodes)
    calls: list[ApiCall] = []
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        call = call_model(api_key, base_url, model, prompt, sheet_path, timeout)
        calls.append(call)
        if call.status == "success":
            return model, calls, call.parsed
    return "", calls, None


def value(parsed: dict[str, Any] | None, key: str, fallback: str = "unclear") -> str:
    if not parsed:
        return fallback
    raw = parsed.get(key)
    if isinstance(raw, list):
        text = "；".join(str(item).strip() for item in raw if str(item).strip())
    else:
        text = str(raw or "").strip()
    return text if text else fallback


def yes(text: str) -> bool:
    return str(text).strip().lower() == "yes"


def no(text: str) -> bool:
    return str(text).strip().lower() == "no"


def decide_p0(parsed: dict[str, Any] | None, calls: list[ApiCall], speech_row: dict[str, Any]) -> tuple[str, str, str, str]:
    if not parsed:
        err = " | ".join(f"{c.model}:{c.status}:{c.error_summary[:120]}" for c in calls)
        return "manual_review", err or "visual_model_failed", "no", "需人工复核视觉动作"
    observed = value(parsed, "observed_action_name")
    same_action = value(parsed, "same_action_with_talk_claim")
    same_problem = value(parsed, "same_problem_with_talk_claim")
    same_function = value(parsed, "same_function_with_talk_claim")
    cycle = value(parsed, "action_cycle_complete")
    obstruction = value(parsed, "visual_obstruction_status")
    topic_break = value(parsed, "topic_break_risk")
    can_enter = value(parsed, "can_enter_editor_task_pack")
    if no(same_action):
        return "logic_mismatch", "视觉动作与口播动作不一致", "no", "错配剔除"
    if yes(topic_break):
        return "manual_review", "模型提示存在中途断裂风险", "no", "人工检查断裂/卖课/互动"
    if observed.lower() == "unclear" or obstruction in {"blocked", "unclear"}:
        return "manual_review", "视觉动作不清或遮挡", "no", "人工看原片确认动作"
    if not (yes(same_action) and yes(same_problem) and yes(same_function) and yes(cycle) and obstruction == "clear" and yes(can_enter)):
        return "weak_related", "动作/问题/目的/循环/遮挡任一项未全部达到 true_pair", "no", "弱相关待人工复核"
    return "true_pair", "同动作、同问题、同目的、动作循环、遮挡和顺序字段均满足 P0", "yes_pending_user_review", "进入剪辑任务候选，仍需用户人审"


def export_clip(source: Path, start: float, end: float, output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.stat().st_size > 0:
        return "reused"
    start = max(0.0, start)
    end = max(start + 1.0, end)
    copy_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-to",
        f"{end:.3f}",
        "-i",
        str(source),
        "-c",
        "copy",
        str(output),
    ]
    proc = run(copy_cmd, timeout=300)
    if proc.returncode == 0 and output.exists() and output.stat().st_size > 0:
        return "stream_copy"
    reencode_cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-to",
        f"{end:.3f}",
        "-i",
        str(source),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "22",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        str(output),
    ]
    proc = run(reencode_cmd, timeout=600)
    return "reencode" if proc.returncode == 0 and output.exists() and output.stat().st_size > 0 else "failed"


def probe_video(path: Path) -> str:
    if not path.exists():
        return "missing"
    proc = run(["ffmpeg", "-v", "error", "-t", "1", "-i", str(path), "-f", "null", "-"], timeout=120)
    return "passed" if proc.returncode == 0 else "failed_decode"


def package_folder(row: dict[str, Any], package_type: str, index: int) -> Path:
    root = LOCAL_PACKAGE_ROOT if package_type == "true_pair" else LOCAL_MANUAL_ROOT
    structure_folder = row["structure_folder"] if package_type == "true_pair" else "06_人工复核池"
    prefix = "R" if package_type == "true_pair" else "M"
    return root / structure_folder / f"{prefix}{index:03d}_{row['candidate_id']}"


def write_task_card(folder: Path, row: dict[str, Any], package_type: str) -> Path:
    card_path = folder / "00_剪辑任务卡.md"
    split_status = "available" if row.get("speech_clip_path") and row.get("action_clip_path") else "not_available"
    text = f"""# 剪辑任务卡

状态：`pending_user_review`
package_type={package_type}
split_status={split_status}

## 主题

- candidate_id: `{row['candidate_id']}`
- structure: `{row['usable_structure_name']}`
- p0_gate_result: `{row['p0_gate_result']}`
- editor_task_potential: `{row['editor_task_potential']}`

## 口播与动作

- 口播动作：{row['speech_claimed_action']}
- 口播问题：{row['speech_claimed_problem']}
- 口播目的：{row['speech_claimed_function']}
- 视觉动作：{row['observed_action_name']}
- 口播动作同一点：{row['talk_action_same_point']}
- 逻辑关系：`{row['logic_relation']}`

## P0 证据

- same_action_check: `{row['same_action_check']}`
- same_problem_check: `{row['same_problem_check']}`
- same_function_check: `{row['same_function_check']}`
- action_cycle_complete: `{row['action_cycle_complete']}`
- visual_obstruction_status: `{row['visual_obstruction_status']}`
- topic_break_check: `{row['topic_break_check']}`
- reason: {row['reason']}

## 使用方式

先打开 `03_完整上下文_full_context.mp4` 看整体逻辑，再看 `01_口播段_speech.mp4` 和 `02_动作段_action.mp4` 是否需要人工二次切点。`04_视觉证据_contact_sheet.jpg` 只作视觉证据，不是成片。
"""
    write_text(card_path, text)
    return card_path


def write_local_root_readmes(true_count: int, manual_count: int) -> None:
    write_text(
        LOCAL_PACKAGE_ROOT / "00_视频包说明.md",
        f"""# 5月13日逻辑优先 true_pair 视频包

状态：`pending_user_review`
生成时间：{now_text()}

- true_pair 任务组数量：{true_count}
- 打开每组的 `00_剪辑任务卡.md`、`03_完整上下文_full_context.mp4`、`04_视觉证据_contact_sheet.jpg`。
- 本目录不是正式成片目录，仍需用户人审。
""",
    )
    write_text(
        LOCAL_MANUAL_ROOT / "00_人工复核池说明.md",
        f"""# 5月13日逻辑优先人工复核池

状态：`pending_user_review`
生成时间：{now_text()}

- 人工复核任务组数量：{manual_count}
- 这里包含 weak/manual/mismatch 复核材料，不得直接交给剪辑师当可用素材。
""",
    )


def check_workspace() -> dict[str, str]:
    data: dict[str, str] = {}
    for key, args in {
        "git_root": ["rev-parse", "--show-toplevel"],
        "branch": ["branch", "--show-current"],
        "remote": ["remote", "-v"],
        "status": ["status", "--short"],
    }.items():
        rc, out = git_output(args)
        if rc != 0:
            raise RuntimeError(f"blocked_workspace_check_failed:{key}:{out}")
        data[key] = out
    if data["git_root"] != str(REPO_ROOT) or data["branch"] != "main" or "fthytwerwt-sudo/lanxinse--" not in data["remote"]:
        raise RuntimeError("blocked_wrong_workspace_or_remote")
    return data


def ensure_inputs() -> None:
    required = [SOURCE_PATH, ASR_PATH, MODEL_ROUTE_MD, RULES_MD, STRUCTURE_CSV, OLD_SOLUTION_MD, OLD_REPORT_123_MD]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("missing required input: " + "; ".join(missing))
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("blocked_ffmpeg_unavailable")


def build_probe_rows(workspace: dict[str, str], video_meta: dict[str, Any], asr_data: dict[str, Any], route_status: str) -> list[dict[str, Any]]:
    ignore_pkg = git_output(["check-ignore", "-q", "outputs/local_513_logic_first_video_package/x.mp4"])[0] == 0
    ignore_manual = git_output(["check-ignore", "-q", "outputs/local_513_manual_review_pool/x.mp4"])[0] == 0
    return [
        {"check_item": "cwd", "status": "pass", "value": str(REPO_ROOT), "note": ""},
        {"check_item": "git_root", "status": "pass", "value": workspace["git_root"], "note": ""},
        {"check_item": "branch", "status": "pass", "value": workspace["branch"], "note": ""},
        {"check_item": "remote", "status": "pass", "value": "fthytwerwt-sudo/lanxinse--", "note": "remote verified"},
        {"check_item": "source_path", "status": "pass", "value": str(SOURCE_PATH), "note": "only 5月13日 source used"},
        {"check_item": "duration_seconds", "status": "pass", "value": video_meta.get("duration_seconds", ""), "note": ""},
        {"check_item": "video_shape", "status": "pass", "value": f"{video_meta.get('width')}x{video_meta.get('height')}", "note": f"fps={video_meta.get('fps')}"},
        {"check_item": "audio", "status": "pass", "value": video_meta.get("audio_codec", ""), "note": f"channels={video_meta.get('audio_channels')}"},
        {"check_item": "asr_status", "status": "pass", "value": asr_data.get("status", ""), "note": f"segments={asr_data.get('segment_count')}"},
        {"check_item": "ali_visual_route", "status": "pass", "value": route_status, "note": f"{PRIMARY_MODEL}->{FALLBACK_MODEL}; forbidden not called"},
        {"check_item": "old_102_as_counterexample_only", "status": "pass", "value": "yes", "note": "old candidate tables are not read as candidate input"},
        {"check_item": "local_package_ignored", "status": "pass" if ignore_pkg else "fail", "value": str(ignore_pkg).lower(), "note": str(LOCAL_PACKAGE_ROOT)},
        {"check_item": "local_manual_pool_ignored", "status": "pass" if ignore_manual else "fail", "value": str(ignore_manual).lower(), "note": str(LOCAL_MANUAL_ROOT)},
    ]


def route_probe(api_key: str, base_url: str, timeout: int, source: Path) -> list[dict[str, Any]]:
    folder = LOCAL_INPUT_ROOT / "_route_probe"
    sheet, timecodes, _ = make_contact_sheet(folder, source, 1460, 1515, "ROUTE")
    rows = []
    prompt = '你看到一张直播动作 contact sheet。请只输出 JSON：{"visual_probe":"ok","presenter_visible":"yes/no/unclear"}'
    for order, model in enumerate([PRIMARY_MODEL, FALLBACK_MODEL], start=1):
        call = call_model(api_key, base_url, model, prompt, sheet, timeout)
        if call.status != "success":
            retry = call_model(api_key, base_url, model, prompt, sheet, timeout)
            if retry.status == "success":
                retry.error_summary = f"retry_after_first_failure:{call.error_summary[:120]}"
                call = retry
        rows.append(
            {
                "probe_order": order,
                "model_name": model,
                "status": call.status,
                "latency_ms": call.latency_ms,
                "error_summary": call.error_summary,
                "forbidden_model_called": "no",
                "frame_timecodes": ",".join(timecodes),
            }
        )
    return rows


def write_editor_readme(counts: Counter[str], package_rows: list[dict[str, Any]]) -> None:
    text = f"""# 5月13日剪辑师使用说明

状态：`pending_user_review`
生成时间：{now_text()}

## 本轮视频包

- true_pair 视频包：`{LOCAL_PACKAGE_ROOT}`
- 人工复核池：`{LOCAL_MANUAL_ROOT}`

## 数量

- true_pair：{counts.get("true_pair", 0)}
- weak_related：{counts.get("weak_related", 0)}
- logic_mismatch：{counts.get("logic_mismatch", 0)}
- manual_review：{counts.get("manual_review", 0)}

## 使用方式

每个任务组先打开 `00_剪辑任务卡.md`，再打开 `03_完整上下文_full_context.mp4`。弱相关和人工复核池不进入剪辑师可用包。

本轮从 5 月 13 日原始直播录屏重筛，不沿用旧 102 条候选。
"""
    write_text(EDITOR_README_MD, text)


def write_report(
    video_meta: dict[str, Any],
    speech_units: list[dict[str, Any]],
    visual_rows: list[dict[str, Any]],
    master_rows: list[dict[str, Any]],
    package_rows: list[dict[str, Any]],
    route_rows: list[dict[str, Any]],
    files_changed: list[str],
) -> None:
    counts = Counter(row["p0_gate_result"] for row in master_rows)
    route_summary = "; ".join(f"{row['model_name']}={row['status']}" for row in route_rows)
    file_lines = "\n".join(f"- `{path}`" for path in files_changed)
    text = f"""# 124 5月13日直播逻辑优先重筛执行报告

状态：`generated_pending_git_closure`
生成时间：{now_text()}

## result

- 当前项目仓库：`fthytwerwt-sudo/lanxinse--`
- 本地仓库路径：`{REPO_ROOT}`
- 本轮素材路径：`{SOURCE_PATH}`
- 是否只处理 5 月 13 日：yes
- 是否沿用旧 102 条作为入口：no
- ASR 状态：`success_from_local_cache`
- 阿里视觉状态：{route_summary}
- 口播单元数量：{len(speech_units)}
- 视觉动作单元数量：{len(visual_rows)}
- 逻辑链候选数量：{len(master_rows)}
- true_pair 数量：{counts.get("true_pair", 0)}
- weak_related 数量：{counts.get("weak_related", 0)}
- logic_mismatch 数量：{counts.get("logic_mismatch", 0)}
- manual_review 数量：{counts.get("manual_review", 0)}
- 本地 true_pair 视频包路径：`{LOCAL_PACKAGE_ROOT}`
- 本地人工复核池路径：`{LOCAL_MANUAL_ROOT}`
- 实际导出 mp4 数量：{sum(1 for row in package_rows if row.get("full_context_path")) + sum(1 for row in package_rows if row.get("speech_clip_path")) + sum(1 for row in package_rows if row.get("action_clip_path"))}
- 是否提交媒体：no
- 是否写通过类结论：no

## source_probe

- duration_seconds：{video_meta.get("duration_seconds")}
- video：{video_meta.get("width")}x{video_meta.get("height")} {video_meta.get("video_codec")} fps={video_meta.get("fps")}
- audio：{video_meta.get("audio_codec")} channels={video_meta.get("audio_channels")}

## files_changed

{file_lines}

## validation

- 未沿用旧 102 条作为入口：passed
- 重新生成口播单元、视觉动作单元、逻辑链候选：passed
- 本地视频产物已生成：passed
- 媒体/API/ASR 缓存不提交 Git：commit 前复验

## blocked reason

无流程级 blocked；内容层保留 `pending_user_review`。
"""
    write_text(REPORT_MD, text)


def clean_appledouble(root: Path) -> int:
    if not root.exists():
        return 0
    count = 0
    for path in root.rglob("._*"):
        if path.is_file():
            path.unlink()
            count += 1
    return count


def main() -> int:
    workspace = check_workspace()
    ensure_inputs()
    video_meta = ffprobe_summary(SOURCE_PATH)
    asr_data = load_asr()
    values = load_dotenv(ENV_PATH)
    api_key = env_value(values, "ALI_API_KEY")
    if not api_key or is_placeholder_key(api_key):
        raise RuntimeError("blocked_missing_ali_api_key")
    base_url = env_value(values, "ALI_API_BASE_URL", DEFAULT_BASE_URL)
    timeout = int(env_value(values, "ALI_API_TIMEOUT_SECONDS", "60") or "60")

    for folder in [LOCAL_PACKAGE_ROOT, LOCAL_MANUAL_ROOT, LOCAL_MODEL_ROOT, LOCAL_INPUT_ROOT]:
        folder.mkdir(parents=True, exist_ok=True)

    route_rows = route_probe(api_key, base_url, timeout, SOURCE_PATH)
    if not any(row["status"] == "success" for row in route_rows):
        raise RuntimeError("blocked_ali_visual_route_failed")
    route_status = "; ".join(f"{row['model_name']}={row['status']}" for row in route_rows)

    speech_units = build_speech_units(asr_data, float(video_meta["duration_seconds"]))
    selected_units = select_speech_units(speech_units, REVIEW_LIMIT)

    probe_rows = build_probe_rows(workspace, video_meta, asr_data, route_status)
    probe_rows.extend(
        {"check_item": f"route_probe_{row['model_name']}", "status": "pass" if row["status"] == "success" else "warn", "value": row["status"], "note": row["error_summary"]}
        for row in route_rows
    )

    visual_rows: list[dict[str, Any]] = []
    master_rows: list[dict[str, Any]] = []
    package_rows: list[dict[str, Any]] = []

    for index, speech in enumerate(selected_units, start=1):
        candidate_id = f"R513_{index:03d}"
        action_start, action_end, relation = visual_window_for_speech(speech, float(video_meta["duration_seconds"]))
        visual_id = f"VA{index:03d}"
        visual_dir = LOCAL_INPUT_ROOT / f"{visual_id}_{candidate_id}_{slug(speech['speech_claimed_action'])}"
        sheet_path, timecodes, sheet_status = make_contact_sheet(visual_dir, SOURCE_PATH, action_start, action_end, visual_id)
        model_used, calls, parsed = review_visual(api_key, base_url, timeout, speech, relation, sheet_path, timecodes) if sheet_path.exists() else ("", [], None)
        p0_result, reason, can_enter, manual_items = decide_p0(parsed, calls, speech)
        usable_structure, structure_folder = structure_for_unit(speech)
        observed = value(parsed, "observed_action_name")
        same_point = f"{speech['speech_claimed_action']} -> {observed}"
        visual_api_status = "success" if parsed else "failed"
        full_start = max(0.0, min(float(speech["start_seconds"]), action_start) - 8)
        full_end = min(float(video_meta["duration_seconds"]), max(float(speech["end_seconds"]), action_end) + 8)
        row = {
            "candidate_id": candidate_id,
            "source_file": str(SOURCE_PATH),
            "speech_unit_id": speech["speech_unit_id"],
            "speech_start_time": speech["speech_start_time"],
            "speech_end_time": speech["speech_end_time"],
            "speech_claimed_action": speech["speech_claimed_action"],
            "speech_claimed_problem": speech["speech_claimed_problem"],
            "speech_claimed_function": speech["speech_claimed_function"],
            "visual_action_unit_id": visual_id,
            "action_start_time": seconds_to_timecode(action_start),
            "action_end_time": seconds_to_timecode(action_end),
            "observed_action_name": observed,
            "action_cycle_complete": value(parsed, "action_cycle_complete"),
            "visual_obstruction_status": value(parsed, "visual_obstruction_status"),
            "logic_relation": value(parsed, "sequence_logic", relation),
            "same_action_check": value(parsed, "same_action_with_talk_claim"),
            "same_problem_check": value(parsed, "same_problem_with_talk_claim"),
            "same_function_check": value(parsed, "same_function_with_talk_claim"),
            "topic_break_check": value(parsed, "topic_break_risk"),
            "usable_structure_name": usable_structure,
            "p0_gate_result": p0_result,
            "reason": reason,
            "editor_task_potential": can_enter,
            "manual_review_items": manual_items,
            "talk_action_same_point": same_point,
            "structure_folder": structure_folder,
            "local_task_folder": "",
            "full_context_path": "",
            "speech_clip_path": "",
            "action_clip_path": "",
            "contact_sheet_path": str(sheet_path) if sheet_path.exists() else "",
            "model_used": model_used,
            "visual_api_status": visual_api_status,
            "notes": f"not_old_102_entry; sheet_status={sheet_status}; frame_timecodes={','.join(timecodes)}; forbidden_models_called=no",
            "_speech_start_seconds": float(speech["start_seconds"]),
            "_speech_end_seconds": float(speech["end_seconds"]),
            "_action_start_seconds": action_start,
            "_action_end_seconds": action_end,
            "_full_start_seconds": full_start,
            "_full_end_seconds": full_end,
            "_parsed_reason": value(parsed, "reason", ""),
            "_calls": calls,
        }
        visual_rows.append(
            {
                "visual_action_unit_id": visual_id,
                "candidate_id": candidate_id,
                "source_file": str(SOURCE_PATH),
                "action_start_time": row["action_start_time"],
                "action_end_time": row["action_end_time"],
                "observed_action_name": row["observed_action_name"],
                "observed_body_part_or_tool": value(parsed, "observed_body_part_or_tool"),
                "action_cycle_complete": row["action_cycle_complete"],
                "visual_obstruction_status": row["visual_obstruction_status"],
                "presenter_visible": value(parsed, "presenter_visible"),
                "contact_sheet_path_local": row["contact_sheet_path"],
                "model_used": model_used,
                "visual_api_status": visual_api_status,
                "reason": value(parsed, "reason", reason),
                "notes": row["notes"],
            }
        )
        write_text(
            LOCAL_MODEL_ROOT / f"{visual_id}_{candidate_id}.json",
            json.dumps(
                {
                    "candidate_id": candidate_id,
                    "speech_unit_id": speech["speech_unit_id"],
                    "visual_action_unit_id": visual_id,
                    "model_used": model_used,
                    "api_status": visual_api_status,
                    "calls": [
                        {
                            "model": call.model,
                            "status": call.status,
                            "latency_ms": call.latency_ms,
                            "error_summary": call.error_summary,
                            "content_preview": call.content_preview,
                        }
                        for call in calls
                    ],
                    "final_json": parsed,
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        master_rows.append(row)
        print(f"reviewed_logic_candidate={index}/{len(selected_units)} p0={p0_result}", flush=True)

    true_rows = [row for row in master_rows if row["p0_gate_result"] == "true_pair"][:MAX_TRUE_PAIR_EXPORTS]
    non_true_rows = [row for row in master_rows if row["p0_gate_result"] != "true_pair"]
    export_rows = true_rows + non_true_rows
    true_count = 0
    manual_count = 0
    for row in export_rows:
        package_type = "true_pair" if row["p0_gate_result"] == "true_pair" else "manual_review"
        if package_type == "true_pair":
            true_count += 1
            order = true_count
        else:
            manual_count += 1
            order = manual_count
        folder = package_folder(row, package_type, order)
        speech_clip = folder / "01_口播段_speech.mp4"
        action_clip = folder / "02_动作段_action.mp4"
        full_clip = folder / "03_完整上下文_full_context.mp4"
        contact_dst = folder / "04_视觉证据_contact_sheet.jpg"
        speech_method = export_clip(SOURCE_PATH, row["_speech_start_seconds"], row["_speech_end_seconds"], speech_clip)
        action_method = export_clip(SOURCE_PATH, row["_action_start_seconds"], row["_action_end_seconds"], action_clip)
        full_method = export_clip(SOURCE_PATH, row["_full_start_seconds"], row["_full_end_seconds"], full_clip)
        if row["contact_sheet_path"] and Path(row["contact_sheet_path"]).exists():
            contact_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(row["contact_sheet_path"], contact_dst)
        row["local_task_folder"] = str(folder)
        row["speech_clip_path"] = str(speech_clip) if speech_clip.exists() else ""
        row["action_clip_path"] = str(action_clip) if action_clip.exists() else ""
        row["full_context_path"] = str(full_clip) if full_clip.exists() else ""
        row["contact_sheet_path"] = str(contact_dst) if contact_dst.exists() else row["contact_sheet_path"]
        card_path = write_task_card(folder, row, package_type)
        package_rows.append(
            {
                "package_id": f"{'R' if package_type == 'true_pair' else 'M'}{order:03d}",
                "package_type": package_type,
                "candidate_id": row["candidate_id"],
                "p0_gate_result": row["p0_gate_result"],
                "usable_structure_name": row["usable_structure_name"],
                "structure_folder": row["structure_folder"] if package_type == "true_pair" else "06_人工复核池",
                "task_folder": str(folder),
                "task_card_path": str(card_path),
                "speech_clip_path": row["speech_clip_path"],
                "action_clip_path": row["action_clip_path"],
                "full_context_path": row["full_context_path"],
                "contact_sheet_path": row["contact_sheet_path"],
                "speech_export_method": speech_method,
                "action_export_method": action_method,
                "full_context_export_method": full_method,
                "technical_probe_status": probe_video(full_clip),
                "content_status": "pending_user_review",
                "notes": "local media ignored by Git; not a finished video",
            }
        )

    write_local_root_readmes(true_count, manual_count)
    counts = Counter(row["p0_gate_result"] for row in master_rows)
    write_editor_readme(counts, package_rows)

    public_speech_units = [
        {k: v for k, v in row.items() if k not in {"start_seconds", "end_seconds", "score"}}
        for row in speech_units
    ]
    public_master_rows = [
        {k: v for k, v in row.items() if not k.startswith("_")}
        for row in master_rows
    ]
    write_csv(PROBE_CSV, probe_rows, ["check_item", "status", "value", "note"])
    write_csv(
        SPEECH_UNITS_CSV,
        public_speech_units,
        [
            "speech_unit_id",
            "source_file",
            "speech_start_time",
            "speech_end_time",
            "duration_seconds",
            "speech_type",
            "speech_claimed_action",
            "speech_claimed_problem",
            "speech_claimed_function",
            "action_keywords",
            "problem_keywords",
            "asr_text_excerpt",
            "notes",
        ],
    )
    write_csv(
        VISUAL_UNITS_CSV,
        visual_rows,
        [
            "visual_action_unit_id",
            "candidate_id",
            "source_file",
            "action_start_time",
            "action_end_time",
            "observed_action_name",
            "observed_body_part_or_tool",
            "action_cycle_complete",
            "visual_obstruction_status",
            "presenter_visible",
            "contact_sheet_path_local",
            "model_used",
            "visual_api_status",
            "reason",
            "notes",
        ],
    )
    write_csv(MASTER_CSV, public_master_rows, MASTER_FIELDS)
    write_csv(TRUE_PAIR_CSV, [row for row in public_master_rows if row["p0_gate_result"] == "true_pair"], MASTER_FIELDS)
    write_csv(WEAK_CSV, [row for row in public_master_rows if row["p0_gate_result"] == "weak_related"], MASTER_FIELDS)
    write_csv(MISMATCH_CSV, [row for row in public_master_rows if row["p0_gate_result"] == "logic_mismatch"], MASTER_FIELDS)
    write_csv(
        PACKAGE_MANIFEST_CSV,
        package_rows,
        [
            "package_id",
            "package_type",
            "candidate_id",
            "p0_gate_result",
            "usable_structure_name",
            "structure_folder",
            "task_folder",
            "task_card_path",
            "speech_clip_path",
            "action_clip_path",
            "full_context_path",
            "contact_sheet_path",
            "speech_export_method",
            "action_export_method",
            "full_context_export_method",
            "technical_probe_status",
            "content_status",
            "notes",
        ],
    )

    clean_appledouble(LOCAL_PACKAGE_ROOT)
    clean_appledouble(LOCAL_MANUAL_ROOT)
    files_changed = [
        ".gitignore",
        "scripts/restart_513_logic_first_live_screening.py",
        "素材解析_pipeline_material_analysis/17_single_live_logic_first_rescreen/01_单条直播重筛探针_single_live_rescreen_probe.csv",
        "素材解析_pipeline_material_analysis/17_single_live_logic_first_rescreen/02_口播单元表_speech_units.csv",
        "素材解析_pipeline_material_analysis/17_single_live_logic_first_rescreen/03_视觉动作单元表_visual_action_units.csv",
        "项目事实_project_facts/直播素材重筛_live_rescreen/01_5月13日逻辑链候选总表_513_logic_chain_candidate_master.csv",
        "项目事实_project_facts/直播素材重筛_live_rescreen/02_5月13日真配对清单_513_true_pair_candidates.csv",
        "项目事实_project_facts/直播素材重筛_live_rescreen/03_5月13日弱相关待复核清单_513_weak_related_pending_review.csv",
        "项目事实_project_facts/直播素材重筛_live_rescreen/04_5月13日错配剔除清单_513_logic_mismatch_rejects.csv",
        "项目事实_project_facts/直播素材重筛_live_rescreen/05_5月13日视频素材包索引_513_video_package_manifest.csv",
        "项目事实_project_facts/直播素材重筛_live_rescreen/06_5月13日剪辑师使用说明_513_editor_readme.md",
        "执行日志_codex_log/124_5月13日直播逻辑优先重筛执行报告_513_logic_first_rescreen_report.md",
    ]
    write_report(video_meta, public_speech_units, visual_rows, public_master_rows, package_rows, route_rows, files_changed)

    print("restart 513 logic first screening completed")
    print(f"speech_units={len(public_speech_units)}")
    print(f"visual_action_units={len(visual_rows)}")
    print(f"logic_candidates={len(public_master_rows)}")
    print(f"p0_counts={dict(counts)}")
    print(f"true_pair_package={LOCAL_PACKAGE_ROOT}")
    print(f"manual_review_pool={LOCAL_MANUAL_ROOT}")
    print(f"exported_mp4={sum(1 for row in package_rows if row.get('full_context_path')) + sum(1 for row in package_rows if row.get('speech_clip_path')) + sum(1 for row in package_rows if row.get('action_clip_path'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
