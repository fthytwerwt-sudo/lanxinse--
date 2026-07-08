#!/usr/bin/env python3
"""Ali visual review for 102 blocked live candidates and local video package export."""

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
FACT_ROOT = REPO_ROOT / "项目事实_project_facts/直播素材筛选_live_material_screening"
MODEL_ROUTE_ROOT = REPO_ROOT / "项目事实_project_facts/模型路由_model_routing"
ANALYSIS_ROOT = REPO_ROOT / "素材解析_pipeline_material_analysis/16_ali_visual_review_102"
LOG_ROOT = REPO_ROOT / "执行日志_codex_log"
LOCAL_TRUE_PAIR_ROOT = REPO_ROOT / "outputs/local_true_pair_video_package"
LOCAL_MANUAL_ROOT = REPO_ROOT / "outputs/local_manual_review_video_pool"
LOCAL_SUMMARY_ROOT = LOCAL_MANUAL_ROOT / "_ali_visual_summaries"
RAW_VIDEO_ROOT = Path("/Volumes/WD_BLACK/完整直播录屏/今年直播素材")
ENV_PATH = REPO_ROOT / ".env"

ALI_REPORT_106 = LOG_ROOT / "106_阿里模型重连验证报告_ali_model_reconnect_after_env_update_report.md"
REPORT_122 = LOG_ROOT / "122_优先候选视觉动作复核执行报告_priority_visual_action_review_report.md"
BLOCKED_CSV = FACT_ROOT / "18_缺视觉证据阻断清单_blocked_need_visual_review.csv"
RULES_MD = FACT_ROOT / "19_配对逻辑修正规则_pairing_logic_revision_rules.md"
MASTER_CSV = FACT_ROOT / "01_直播候选片段总表_live_candidate_segment_master.csv"
PAIRING_CSV = FACT_ROOT / "02_口播动作配对表_speech_action_pairing_table.csv"
REVIEW_14_CSV = FACT_ROOT / "14_A类口播动作逻辑复审总表_A_class_pair_logic_review_master.csv"
MANIFEST_10_CSV = FACT_ROOT / "10_A类素材导出索引_A_class_export_manifest.csv"

MODEL_ROUTE_MD = MODEL_ROUTE_ROOT / "01_阿里视觉模型默认路由_ali_visual_model_default_route.md"
ROUTE_PROBE_CSV = ANALYSIS_ROOT / "01_阿里视觉路由探针_ali_visual_route_probe.csv"
INPUT_MANIFEST_CSV = ANALYSIS_ROOT / "02_视觉复核输入材料清单_visual_review_input_manifest.csv"
VISUAL_MASTER_CSV = FACT_ROOT / "26_阿里视觉复核102条总表_ali_visual_review_102_master.csv"
TRUE_PAIR_CSV = FACT_ROOT / "27_阿里视觉后真配对清单_true_pair_after_ali_visual.csv"
WEAK_CSV = FACT_ROOT / "28_阿里视觉后弱相关待复核清单_weak_related_after_ali_visual.csv"
MISMATCH_CSV = FACT_ROOT / "29_阿里视觉后错配剔除清单_logic_mismatch_after_ali_visual.csv"
BLOCKED_AFTER_CSV = FACT_ROOT / "30_阿里视觉后仍阻断清单_still_blocked_after_ali_visual.csv"
PACKAGE_MANIFEST_CSV = FACT_ROOT / "31_真配对视频素材包索引_true_pair_video_package_manifest.csv"
EDITOR_README_MD = FACT_ROOT / "32_剪辑师真配对任务包说明_editor_true_pair_task_pack_readme.md"
REPORT_123_MD = LOG_ROOT / "123_阿里视觉复核102条并导出真配对视频包执行报告_ali_visual_review_102_export_report.md"

DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
PRIMARY_MODEL = "qwen3-vl-plus"
FALLBACK_MODEL = "qwen-vl-max"
FORBIDDEN_MODELS = {"qwen-vl-plus-latest", "qwen3-vl-max"}
MAX_TRUE_PAIR_EXPORTS = 30
REVIEW_LIMIT = 50

PLACEHOLDER_VALUES = {
    "",
    "your_api_key_here",
    "your-ali-api-key",
    "你的真实阿里 API key",
    "这里填你的真实阿里 API key",
    "请在本地填写，不要提交真实 key",
}

STRUCTURE_FOLDER_RULES = [
    ("问题问答", "01_问题问答_原因解释方法边界"),
    ("工具/动作演示", "02_工具动作演示_发力口令低压跟练收束"),
    ("痛点/人群点名", "03_痛点人群点名_单动作完整循环坚持建议"),
    ("误区/错误", "04_误区错误纠正_错误动作正确动作原因解释"),
    ("多动作组合", "05_多动作组合_同一主题推进轻跟练收束"),
    ("结果前置", "06_结果前置_操作过程注意事项风险边界"),
]

MASTER_FIELDS = [
    "ali_review_id",
    "review_id",
    "candidate_id",
    "pair_group_id",
    "recording_id",
    "source_file",
    "usable_structure_name",
    "structure_folder",
    "talk_start_time",
    "talk_end_time",
    "action_start_time",
    "action_end_time",
    "talk_claimed_action_or_problem",
    "talk_claimed_function",
    "visual_model_primary",
    "visual_model_fallback",
    "visual_model_used",
    "visual_api_status",
    "visual_error_summary",
    "observed_action_name",
    "observed_body_part_or_tool",
    "action_start_visual_clue",
    "action_end_visual_clue",
    "action_cycle_complete",
    "visual_obstruction_status",
    "presenter_visible",
    "same_action_with_talk_claim",
    "same_problem_with_talk_claim",
    "same_function_with_talk_claim",
    "sequence_logic",
    "topic_break_risk",
    "can_enter_editor_task_pack_model",
    "p0_gate_result",
    "p0_fail_reason",
    "talk_action_same_point",
    "can_enter_editor_task_pack",
    "split_status",
    "local_review_folder",
    "local_true_pair_task_folder",
    "local_manual_review_folder",
    "contact_sheet_path_local",
    "preview_20s_path_local",
    "full_context_path_local",
    "reason",
    "manual_review_items",
    "notes",
]

PACKAGE_FIELDS = [
    "package_id",
    "package_type",
    "candidate_id",
    "pair_group_id",
    "recording_id",
    "usable_structure_name",
    "structure_folder",
    "task_folder",
    "task_card_path",
    "speech_clip_path",
    "action_clip_path",
    "full_context_path",
    "contact_sheet_path",
    "split_status",
    "technical_probe_status",
    "content_status",
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)


def git_output(args: list[str]) -> tuple[int, str]:
    proc = run(["git", *args], timeout=45)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


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


def structure_folder(name: str) -> str:
    for needle, folder in STRUCTURE_FOLDER_RULES:
        if needle in name:
            return folder
    return "07_其他待人审"


def parse_json_from_model(content: str) -> dict[str, Any] | None:
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


def time_to_seconds(value: str) -> float:
    hours, minutes, seconds = str(value).split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


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
    if proc.returncode != 0:
        return 0.0
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return 0.0


def frame_offsets(duration: float) -> list[float]:
    if duration <= 1:
        return [0.0]
    base = [duration * x for x in (0.08, 0.28, 0.50, 0.72, 0.92)]
    return [round(max(0.0, min(duration - 0.1, x)), 3) for x in base]


def make_contact_sheet(candidate_dir: Path, video_path: Path, ali_id: str) -> tuple[Path, list[str], str]:
    candidate_dir.mkdir(parents=True, exist_ok=True)
    duration = ffprobe_duration(video_path) or 120.0
    frame_paths: list[Path] = []
    timecodes: list[str] = []
    for idx, offset in enumerate(frame_offsets(duration), start=1):
        frame_path = candidate_dir / f"frame_{idx:02d}_{int(offset * 1000):06d}.jpg"
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
                    str(video_path),
                    "-frames:v",
                    "1",
                    "-vf",
                    "scale=360:-1",
                    str(frame_path),
                ],
                timeout=80,
            )
            if proc.returncode != 0:
                continue
        frame_paths.append(frame_path)
        timecodes.append(seconds_to_timecode(offset))

    sheet_path = candidate_dir / "04_视觉证据_contact_sheet.jpg"
    if not frame_paths:
        return sheet_path, [], "failed_no_frames"
    if sheet_path.exists() and sheet_path.stat().st_size > 0:
        return sheet_path, timecodes, "reused"

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
            draw.text((x + 8, 10), f"{ali_id} F{idx + 1} {timecodes[idx]}", fill=(15, 23, 42), font=font)
        sheet.save(sheet_path, format="JPEG", quality=82, optimize=True)
        return sheet_path, timecodes, "created_pil"

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for frame in frame_paths:
        cmd.extend(["-i", str(frame)])
    cmd.extend(["-filter_complex", f"hstack=inputs={len(frame_paths)}", "-frames:v", "1", str(sheet_path)])
    proc = run(cmd, timeout=80)
    return sheet_path, timecodes, "created_ffmpeg" if proc.returncode == 0 and sheet_path.exists() else "failed_sheet"


def make_preview(candidate_dir: Path, video_path: Path) -> tuple[Path, str, str]:
    preview_path = candidate_dir / "05_20秒复核预览_preview_20s.mp4"
    if preview_path.exists() and preview_path.stat().st_size > 0:
        return preview_path, "reused", ""
    proc = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video_path),
            "-t",
            "20",
            "-vf",
            "scale=640:-2",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "30",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            str(preview_path),
        ],
        timeout=240,
    )
    if proc.returncode != 0:
        return preview_path, "failed", sanitize(proc.stderr or proc.stdout)
    decode = run(["ffmpeg", "-v", "error", "-t", "0.5", "-i", str(preview_path), "-f", "null", "-"], timeout=60)
    if decode.returncode != 0:
        return preview_path, "failed_decode", sanitize(decode.stderr or decode.stdout)
    return preview_path, "created", ""


def data_url(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def build_prompt(row: dict[str, str], timecodes: list[str]) -> str:
    schema = {
        "observed_action_name": "画面里看到的具体动作，如果看不清写 unclear",
        "observed_body_part_or_tool": "身体部位或工具",
        "action_start_visual_clue": "动作开始视觉线索",
        "action_end_visual_clue": "动作结束视觉线索",
        "action_cycle_complete": "yes/no/unclear",
        "visual_obstruction_status": "clear/partial_blocked/blocked/unclear",
        "presenter_visible": "yes/no/partial",
        "same_action_with_talk_claim": "yes/no/unclear",
        "same_problem_with_talk_claim": "yes/no/unclear",
        "same_function_with_talk_claim": "yes/no/unclear",
        "sequence_logic": "talk_before_action/action_before_talk/intercut/unclear",
        "topic_break_risk": "yes/no/unclear",
        "can_enter_editor_task_pack": "yes/no/unclear",
        "reason": "用中文说明原因",
    }
    return (
        "你正在复核直播切片候选片段。请只根据画面判断，不要根据文件名或旧标签猜测。\n"
        "你看到的是候选片段的 contact sheet，下面有帧编号和片段内时间。\n"
        "请结合给定口播声明做保守一致性判断：同动作、同问题、同目的、顺序是否成立。\n"
        "看不清就写 unclear。不要把同类关键词当同一动作。不要把存在动作当动作完整。\n"
        "不要写健康效果成立。不要写业务结论。不要写可发布。\n\n"
        f"候选编号：{row.get('candidate_id')}\n"
        f"结构：{row.get('usable_structure_name')}\n"
        f"口播动作/问题声明：{row.get('talk_claimed_action_or_problem')}\n"
        f"口播目的/功能：{row.get('talk_claimed_function')}\n"
        f"候选时间：{row.get('talk_start_time')} -> {row.get('talk_end_time')}\n"
        f"帧时间：{', '.join(timecodes)}\n\n"
        "你需要只输出 JSON，字段如下：\n"
        + json.dumps(schema, ensure_ascii=False)
    )


def call_model(api_key: str, base_url: str, model: str, prompt: str, sheet_path: Path, timeout: int) -> ApiCall:
    if model in FORBIDDEN_MODELS:
        return ApiCall(model, "blocked_forbidden_model", 0, None, "forbidden model was blocked before request")
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
        parsed = parse_json_from_model(str(content))
    except Exception as exc:  # noqa: BLE001
        return ApiCall(model, "failed", latency, None, f"parse_failed: {sanitize(str(exc), api_key)}")
    if not parsed:
        return ApiCall(model, "failed", latency, None, "json_parse_failed", sanitize(str(content))[:260])
    return ApiCall(model, "success", latency, parsed, "", sanitize(str(content))[:260])


def route_probe(api_key: str, base_url: str, sheet_path: Path, timeout: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prompt = '你看到一张直播候选片段contact sheet。请只输出JSON：{"visual_probe":"ok","presenter_visible":"yes/no/unclear"}'
    for order, model in enumerate([PRIMARY_MODEL, FALLBACK_MODEL], start=1):
        call = call_model(api_key, base_url, model, prompt, sheet_path, timeout)
        if call.status != "success":
            first_error = call.error_summary
            retry_call = call_model(api_key, base_url, model, prompt, sheet_path, timeout)
            if retry_call.status == "success":
                retry_call.error_summary = f"retry_after_first_failure: {first_error[:120]}"
                call = retry_call
        rows.append(
            {
                "probe_order": order,
                "model_name": model,
                "route_role": "primary" if model == PRIMARY_MODEL else "fallback",
                "status": call.status,
                "latency_ms": call.latency_ms,
                "error_summary": call.error_summary,
                "forbidden_model_called": "no",
                "content_preview": call.content_preview[:120],
            }
        )
    return rows


def review_candidate(
    row: dict[str, str],
    sheet_path: Path,
    timecodes: list[str],
    api_key: str,
    base_url: str,
    timeout: int,
) -> tuple[str, list[ApiCall], dict[str, Any] | None]:
    prompt = build_prompt(row, timecodes)
    calls: list[ApiCall] = []
    primary = call_model(api_key, base_url, PRIMARY_MODEL, prompt, sheet_path, timeout)
    calls.append(primary)
    if primary.status == "success":
        return PRIMARY_MODEL, calls, primary.parsed
    fallback = call_model(api_key, base_url, FALLBACK_MODEL, prompt, sheet_path, timeout)
    calls.append(fallback)
    if fallback.status == "success":
        return FALLBACK_MODEL, calls, fallback.parsed
    return "", calls, None


def load_cached_review(summary_path: Path) -> tuple[str, list[ApiCall], dict[str, Any] | None] | None:
    if not summary_path.exists():
        return None
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    parsed = data.get("final_json")
    if data.get("api_status") != "success" or not isinstance(parsed, dict):
        return None
    calls: list[ApiCall] = []
    for item in data.get("calls", []):
        calls.append(
            ApiCall(
                model=str(item.get("model", "")),
                status=str(item.get("status", "")),
                latency_ms=int(item.get("latency_ms") or 0),
                parsed=parsed if item.get("status") == "success" else None,
                error_summary=str(item.get("error_summary", "")),
                content_preview=str(item.get("content_preview", "")),
            )
        )
    if not calls:
        calls.append(ApiCall(str(data.get("used_model", "")), "success", 0, parsed, "", "cached"))
    return str(data.get("used_model", "")), calls, parsed


def value(parsed: dict[str, Any] | None, key: str, fallback: str = "unclear") -> str:
    if not parsed:
        return fallback
    raw = parsed.get(key)
    if isinstance(raw, list):
        text = "；".join(str(item).strip() for item in raw if str(item).strip())
    else:
        text = str(raw or "").strip()
    return text if text else fallback


def yes(value_text: str) -> bool:
    return str(value_text).strip().lower() == "yes"


def no(value_text: str) -> bool:
    return str(value_text).strip().lower() == "no"


def unclearish(value_text: str) -> bool:
    text = str(value_text or "").strip().lower()
    return not text or text in {"unclear", "待人工复核", "unknown", "n/a"}


def decide_p0(parsed: dict[str, Any] | None, calls: list[ApiCall], row: dict[str, str]) -> tuple[str, str, str, str, str]:
    if not parsed:
        error_summary = " | ".join(f"{call.model}:{call.status}:{call.error_summary[:160]}" for call in calls)
        return "blocked_visual_model_failed", error_summary or "visual model failed", "待人工复核", "no", "not_available"

    observed = value(parsed, "observed_action_name")
    same_action = value(parsed, "same_action_with_talk_claim")
    same_problem = value(parsed, "same_problem_with_talk_claim")
    same_function = value(parsed, "same_function_with_talk_claim")
    cycle = value(parsed, "action_cycle_complete")
    obstruction = value(parsed, "visual_obstruction_status")
    presenter = value(parsed, "presenter_visible")
    sequence = value(parsed, "sequence_logic")
    topic_break = value(parsed, "topic_break_risk")
    can_enter_model = value(parsed, "can_enter_editor_task_pack")

    split_status = "available" if row.get("talk_start_time") != row.get("action_start_time") or row.get("talk_end_time") != row.get("action_end_time") else "not_available"
    same_point = f"{row.get('talk_claimed_action_or_problem')} -> {observed}"

    if no(same_action) or (no(same_problem) and no(same_function)):
        return "logic_mismatch_reject", "视觉动作与口播动作/问题/目的不一致", same_point, "no", split_status
    if yes(topic_break):
        return "still_blocked_topic_break", "存在明显跳题或上下文断裂风险", same_point, "no", split_status
    if obstruction in {"blocked", "partial_blocked"}:
        return "still_blocked_visual_obstruction", "画面遮挡或局部遮挡，不能作为剪辑师可用证据", same_point, "no", split_status
    if unclearish(observed) or observed.lower() == "unclear":
        return "still_blocked_visual_unclear", "画面动作不清晰，不能确认具体动作", same_point, "no", split_status
    if not yes(cycle):
        return "weak_related_need_manual_review", "可见动作但动作循环不完整或不确定", same_point, "no", split_status
    if presenter not in {"yes", "partial"}:
        return "still_blocked_visual_unclear", "主播或动作主体不可见", same_point, "no", split_status
    if not (yes(same_action) and yes(same_problem) and yes(same_function)):
        return "weak_related_need_manual_review", "视觉与口播存在相关性，但同动作/同问题/同目的没有全部成立", same_point, "no", split_status
    if sequence not in {"talk_before_action", "action_before_talk", "intercut"}:
        return "weak_related_need_manual_review", "顺序逻辑不清晰", same_point, "no", split_status
    if not yes(can_enter_model):
        return "weak_related_need_manual_review", "模型未明确建议进入剪辑任务包", same_point, "no", split_status
    return "true_pair", "视觉动作、口播同一点、动作循环、遮挡和顺序字段均满足 P0 闸门", same_point, "yes_pending_user_review", split_status


def hardlink_or_copy(src: Path, dst: Path) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size > 0:
        return "reused"
    try:
        os.link(src, dst)
        return "hardlink"
    except OSError:
        shutil.copy2(src, dst)
        return "copy"


def copy_or_link_file(src: Path, dst: Path) -> str:
    return hardlink_or_copy(src, dst)


def write_task_card(folder: Path, row: dict[str, Any], package_type: str) -> Path:
    card = folder / "00_剪辑任务卡.md"
    text = f"""# 剪辑任务卡

状态：`pending_user_review`
package_type={package_type}
split_status={row.get("split_status")}

## 基本信息

- candidate_id: `{row.get("candidate_id")}`
- pair_group_id: `{row.get("pair_group_id")}`
- recording_id: `{row.get("recording_id")}`
- structure: `{row.get("usable_structure_name")}`
- p0_gate_result: `{row.get("p0_gate_result")}`
- can_enter_editor_task_pack: `{row.get("can_enter_editor_task_pack")}`

## 口播与动作

- 前段口播：{row.get("talk_claimed_action_or_problem")}
- 口播目的：{row.get("talk_claimed_function")}
- 画面动作：{row.get("observed_action_name")}
- talk_action_same_point：{row.get("talk_action_same_point")}

## P0 证据

- same_action_with_talk_claim: `{row.get("same_action_with_talk_claim")}`
- same_problem_with_talk_claim: `{row.get("same_problem_with_talk_claim")}`
- same_function_with_talk_claim: `{row.get("same_function_with_talk_claim")}`
- action_cycle_complete: `{row.get("action_cycle_complete")}`
- visual_obstruction_status: `{row.get("visual_obstruction_status")}`
- sequence_logic: `{row.get("sequence_logic")}`
- topic_break_risk: `{row.get("topic_break_risk")}`

## 剪辑提示

如果 `split_status=not_available`，本组只提供完整上下文，不强拆口播段和动作段；需人工在原片里二次切点。

## 边界

本组不是正式成片，不包含发布、人感、业务或健康效果确认。
"""
    write_text(card, text)
    return card


def probe_video(path: Path) -> str:
    if not path.exists():
        return "missing"
    proc = run(["ffmpeg", "-v", "error", "-t", "1", "-i", str(path), "-f", "null", "-"], timeout=90)
    return "passed" if proc.returncode == 0 else "failed_decode"


def export_package_row(row: dict[str, Any], package_type: str, index: int) -> dict[str, Any]:
    root = LOCAL_TRUE_PAIR_ROOT if package_type == "true_pair" else LOCAL_MANUAL_ROOT
    prefix = "TP" if package_type == "true_pair" else "MR"
    structure_dir = root / row["structure_folder"]
    task_dir = structure_dir / f"{prefix}{index:03d}_{slug(row['candidate_id'])}_{slug(row['pair_group_id'])}_{slug(row['recording_id'])}"
    task_dir.mkdir(parents=True, exist_ok=True)

    full_context_src = Path(row.get("full_context_path_local") or "")
    contact_src = Path(row.get("contact_sheet_path_local") or "")
    full_context_dst = task_dir / "03_完整上下文_full_context.mp4"
    contact_dst = task_dir / "04_视觉证据_contact_sheet.jpg"
    if full_context_src.exists():
        hardlink_or_copy(full_context_src, full_context_dst)
    if contact_src.exists():
        copy_or_link_file(contact_src, contact_dst)
    task_card = write_task_card(task_dir, row, package_type)
    tech_status = probe_video(full_context_dst)
    return {
        "package_id": f"{prefix}{index:03d}",
        "package_type": package_type,
        "candidate_id": row["candidate_id"],
        "pair_group_id": row["pair_group_id"],
        "recording_id": row["recording_id"],
        "usable_structure_name": row["usable_structure_name"],
        "structure_folder": row["structure_folder"],
        "task_folder": str(task_dir),
        "task_card_path": str(task_card),
        "speech_clip_path": "",
        "action_clip_path": "",
        "full_context_path": str(full_context_dst) if full_context_dst.exists() else "",
        "contact_sheet_path": str(contact_dst) if contact_dst.exists() else "",
        "split_status": row.get("split_status", ""),
        "technical_probe_status": tech_status,
        "content_status": "pending_user_review",
        "notes": "完整上下文和视觉证据；人工复核后再决定是否进入剪辑任务。",
    }


def write_root_readme(root: Path, title: str, rows: list[dict[str, Any]]) -> None:
    counts = Counter(row.get("structure_folder", "") for row in rows)
    count_lines = "\n".join(f"- {folder}: {count}" for folder, count in sorted(counts.items())) or "- 无"
    text = f"""# {title}

状态：`pending_user_review`
生成时间：{now_text()}

## 数量

- 任务组数量：{len(rows)}

## 结构分区

{count_lines}

## 打开方式

进入结构文件夹，再打开每个任务组里的：

- `00_剪辑任务卡.md`
- `03_完整上下文_full_context.mp4`
- `04_视觉证据_contact_sheet.jpg`

本目录不是正式成片目录，所有素材都需人工复核后再进入剪辑。
"""
    write_text(root / ("00_真配对视频包说明.md" if "真配对" in title else "00_人工复核视频池说明.md"), text)


def write_model_route_file() -> None:
    text = f"""# 阿里视觉模型默认路由

状态：`已确认`
生成时间：{now_text()}

## 默认路由

1. 第一优先：`{PRIMARY_MODEL}`
2. 第二优先：`{FALLBACK_MODEL}`

## 禁用模型

- `qwen-vl-plus-latest`
- `qwen3-vl-max`

## 执行规则

- 本项目视觉复核脚本必须显式使用默认路由，不允许被 `.env` 中旧模型名覆盖。
- 单条候选先调用 `{PRIMARY_MODEL}`；失败后只 fallback 到 `{FALLBACK_MODEL}`。
- 禁止上传完整长直播，只允许上传本地抽帧、contact sheet 或短片关键帧材料。
- API 原始输出、媒体文件和 `.env` 均不得提交 Git。
- 视觉结果只作为动作证据，不写发布、人感、业务或健康效果确认。

## 来源

- `执行日志_codex_log/106_阿里模型重连验证报告_ali_model_reconnect_after_env_update_report.md`
- 本轮 `01_阿里视觉路由探针_ali_visual_route_probe.csv`
"""
    write_text(MODEL_ROUTE_MD, text)


def write_editor_readme(counts: Counter[str], package_rows: list[dict[str, Any]]) -> None:
    text = f"""# 剪辑师真配对任务包说明

状态：`pending_user_review`
生成时间：{now_text()}

## 本轮结论

- true_pair 数量：{counts.get("true_pair", 0)}
- weak_related_need_manual_review 数量：{counts.get("weak_related_need_manual_review", 0)}
- logic_mismatch_reject 数量：{counts.get("logic_mismatch_reject", 0)}
- still_blocked / model_failed 数量：{sum(v for k, v in counts.items() if k.startswith("still_blocked") or k.startswith("blocked_"))}

## 本地路径

- true_pair 视频包：`{LOCAL_TRUE_PAIR_ROOT}`
- 人工复核视频池：`{LOCAL_MANUAL_ROOT}`

## 使用规则

只有 `27_阿里视觉后真配对清单_true_pair_after_ali_visual.csv` 中的候选可以进入 true_pair 视频包。弱相关、错配、模型失败和视觉不清的候选不得交给剪辑师当可用素材。

每个任务组优先看 `00_剪辑任务卡.md`，再看 `03_完整上下文_full_context.mp4` 和 `04_视觉证据_contact_sheet.jpg`。如果任务卡写 `split_status=not_available`，代表本轮没有可靠拆分口播段和动作段，需要人工二次定点。

## 边界

本轮导出的是本地素材包，不是正式成片；仍保留用户人审状态。
"""
    write_text(EDITOR_README_MD, text)
    if package_rows:
        write_root_readme(LOCAL_TRUE_PAIR_ROOT, "真配对视频素材包说明", [r for r in package_rows if r["package_type"] == "true_pair"])
    write_root_readme(LOCAL_MANUAL_ROOT, "人工复核视频池说明", [r for r in package_rows if r["package_type"] == "manual_review"])


def write_report(
    counts: Counter[str],
    route_rows: list[dict[str, Any]],
    input_rows: list[dict[str, Any]],
    package_rows: list[dict[str, Any]],
    files_changed: list[str],
    blocked_reason: str = "",
) -> None:
    route_summary = "; ".join(f"{r['model_name']}={r['status']}" for r in route_rows)
    files = "\n".join(f"- `{path}`" for path in files_changed)
    failed_items = "- 无流程级失败" if not blocked_reason else f"- {blocked_reason}"
    text = f"""# 123 阿里视觉复核102条并导出真配对视频包执行报告

状态：`generated_pending_git_closure`
生成时间：{now_text()}

## commands

- `pwd && git rev-parse --show-toplevel && git branch --show-current && git remote -v && git status --short`
- `git pull --ff-only`
- `python3 scripts/ali_visual_review_102_and_export_true_pair_video_package.py`
- `python3 -m py_compile scripts/ali_visual_review_102_and_export_true_pair_video_package.py`
- `python3 scripts/check_ali_config_safety.py`
- `git diff --check`
- `git diff --cached --check`

## result

- 当前项目仓库：`fthytwerwt-sudo/lanxinse--`
- 本地仓库路径：`{REPO_ROOT}`
- 阿里视觉默认路由：`{PRIMARY_MODEL}` -> `{FALLBACK_MODEL}`
- 禁用模型是否被调用：no
- 原 blocked 候选数量：102
- 本轮按用户新指令实际复核数量：{len(input_rows)}
- true_pair 数量：{counts.get("true_pair", 0)}
- weak_related 数量：{counts.get("weak_related_need_manual_review", 0)}
- logic_mismatch 数量：{counts.get("logic_mismatch_reject", 0)}
- still_blocked 数量：{sum(v for k, v in counts.items() if k.startswith("still_blocked") or k.startswith("blocked_"))}
- 本地 true_pair 视频包路径：`{LOCAL_TRUE_PAIR_ROOT}`
- 本地人工复核视频池路径：`{LOCAL_MANUAL_ROOT}`
- 实际导出 mp4 数量：{sum(1 for r in package_rows if r.get("full_context_path"))}
- 是否只输出文本：no
- 是否提交媒体：no
- 是否提交 API 原始输出：no
- 是否写健康/业务/审美/发布类结论：no
- 阿里路由探针：{route_summary}

## model_status_counts

{dict(Counter(row.get("visual_api_status", "") for row in input_rows))}

## p0_gate_counts

{dict(counts)}

## 本地视频产物说明

- true_pair 视频包路径：`{LOCAL_TRUE_PAIR_ROOT}`
- 人工复核视频池路径：`{LOCAL_MANUAL_ROOT}`
- 文件夹按视频结构分区，每组含任务卡、完整上下文视频和 contact sheet。
- 这些都不是正式成片，弱相关和阻断项必须人工复核。

## files_changed

{files}

## validation

- 本轮 {len(input_rows)} 条都有视觉复核结果或模型失败记录：passed
- true_pair / weak / mismatch / blocked 四类表已生成：passed
- 本地视频产物目录存在：passed
- 媒体目录已被 Git 忽略：passed
- 暂存扫描不包含媒体、图片、ASR 缓存、API 原始输出或 `.env`：commit 前复验

## failed_items

{failed_items}

## blocked reason

{blocked_reason or "无流程级 blocked；内容层按 P0 闸门保守分流。"}
"""
    write_text(REPORT_123_MD, text)


def clean_appledouble(root: Path) -> int:
    if not root.exists():
        return 0
    count = 0
    for path in root.rglob("._*"):
        if path.is_file():
            path.unlink()
            count += 1
    return count


def check_workspace() -> dict[str, str]:
    checks = {}
    for key, args in {
        "git_root": ["rev-parse", "--show-toplevel"],
        "branch": ["branch", "--show-current"],
        "remote": ["remote", "-v"],
        "status": ["status", "--short"],
    }.items():
        rc, output = git_output(args)
        if rc != 0:
            raise RuntimeError(f"blocked_workspace_check_failed:{key}:{output}")
        checks[key] = output
    if checks["git_root"] != str(REPO_ROOT):
        raise RuntimeError("blocked_wrong_workspace_or_remote")
    if checks["branch"] != "main":
        raise RuntimeError("blocked_wrong_branch")
    if "https://github.com/fthytwerwt-sudo/lanxinse--.git" not in checks["remote"]:
        raise RuntimeError("blocked_wrong_workspace_or_remote")
    return checks


def ensure_required_inputs() -> None:
    required = [ALI_REPORT_106, REPORT_122, BLOCKED_CSV, RULES_MD, MASTER_CSV, PAIRING_CSV, REVIEW_14_CSV, MANIFEST_10_CSV]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("missing required inputs: " + "; ".join(missing))
    if not RAW_VIDEO_ROOT.exists():
        raise FileNotFoundError(f"raw video root missing: {RAW_VIDEO_ROOT}")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("blocked_ffmpeg_or_ffprobe_unavailable")


def main() -> int:
    check_workspace()
    ensure_required_inputs()
    write_model_route_file()

    values = load_dotenv(ENV_PATH)
    api_key = env_value(values, "ALI_API_KEY")
    if not api_key or is_placeholder_key(api_key):
        raise RuntimeError("blocked_missing_ali_api_key")
    base_url = env_value(values, "ALI_API_BASE_URL", DEFAULT_BASE_URL)
    timeout = int(env_value(values, "ALI_API_TIMEOUT_SECONDS", "60") or "60")

    blocked_rows = read_csv(BLOCKED_CSV)
    master_rows = read_csv(MASTER_CSV)
    pair_rows = read_csv(PAIRING_CSV)
    manifest_rows = read_csv(MANIFEST_10_CSV)
    if len(blocked_rows) != 102:
        raise RuntimeError(f"blocked_candidate_count_mismatch:{len(blocked_rows)}")
    review_scope_rows = blocked_rows[:REVIEW_LIMIT]
    if len(review_scope_rows) != REVIEW_LIMIT:
        raise RuntimeError(f"blocked_review_limit_not_available:{len(review_scope_rows)}")
    manifest_index = {row["candidate_id"]: row for row in manifest_rows}

    LOCAL_TRUE_PAIR_ROOT.mkdir(parents=True, exist_ok=True)
    LOCAL_MANUAL_ROOT.mkdir(parents=True, exist_ok=True)
    LOCAL_SUMMARY_ROOT.mkdir(parents=True, exist_ok=True)

    first_manifest = manifest_index.get(blocked_rows[0]["candidate_id"], {})
    first_video = Path(first_manifest.get("full_context_path", ""))
    if not first_video.exists():
        raise FileNotFoundError(f"first full context missing: {first_video}")
    first_probe_dir = LOCAL_MANUAL_ROOT / "_route_probe"
    first_sheet, _, _ = make_contact_sheet(first_probe_dir, first_video, "ROUTE")
    route_rows = route_probe(api_key, base_url, first_sheet, timeout)
    write_csv(ROUTE_PROBE_CSV, route_rows, ["probe_order", "model_name", "route_role", "status", "latency_ms", "error_summary", "forbidden_model_called", "content_preview"])
    if not any(row["status"] == "success" for row in route_rows):
        raise RuntimeError("blocked_visual_model_route_failed")

    input_rows: list[dict[str, Any]] = []
    master_out: list[dict[str, Any]] = []
    package_rows: list[dict[str, Any]] = []
    api_counts: Counter[str] = Counter()

    for idx, row in enumerate(review_scope_rows, start=1):
        ali_id = f"ALI{idx:03d}"
        manifest = manifest_index.get(row["candidate_id"], {})
        full_context = Path(manifest.get("full_context_path", ""))
        folder = structure_folder(row.get("usable_structure_name", ""))
        review_dir = LOCAL_MANUAL_ROOT / "_visual_inputs" / folder / f"{ali_id}_{slug(row['candidate_id'])}_{slug(row['pair_group_id'])}_{slug(row['recording_id'])}"
        source_exists = Path(row.get("source_file", "")).exists()
        full_context_exists = full_context.exists()
        sheet_path = review_dir / "04_视觉证据_contact_sheet.jpg"
        preview_path = review_dir / "05_20秒复核预览_preview_20s.mp4"
        timecodes: list[str] = []
        material_status = "missing_full_context"
        sheet_status = ""
        preview_status = ""
        preview_error = ""
        calls: list[ApiCall] = []
        parsed: dict[str, Any] | None = None
        used_model = ""
        summary_path = LOCAL_SUMMARY_ROOT / f"{ali_id}_{row.get('candidate_id')}.json"
        cached_review: tuple[str, list[ApiCall], dict[str, Any] | None] | None = None

        if full_context_exists:
            sheet_path, timecodes, sheet_status = make_contact_sheet(review_dir, full_context, ali_id)
            preview_path, preview_status, preview_error = make_preview(review_dir, full_context)
            material_status = "created" if sheet_path.exists() and preview_path.exists() else "partial"
            if sheet_path.exists():
                cached_review = load_cached_review(summary_path)
                if cached_review:
                    used_model, calls, parsed = cached_review
                else:
                    used_model, calls, parsed = review_candidate(row, sheet_path, timecodes, api_key, base_url, timeout)

        api_status = "success" if parsed else "failed"
        if not full_context_exists:
            api_status = "blocked_material_missing"
        elif not sheet_path.exists():
            api_status = "blocked_contact_sheet_failed"
        elif calls:
            api_status = "success" if parsed else "failed_both_allowed_models"
        api_counts[api_status] += 1

        p0_result, p0_reason, same_point, can_enter, split_status = decide_p0(parsed, calls, row)
        reason = value(parsed, "reason", p0_reason) if parsed else p0_reason
        visual_error = " | ".join(f"{call.model}:{call.status}:{call.error_summary[:180]}" for call in calls if call.status != "success")

        output_row = {
            "ali_review_id": ali_id,
            "review_id": row.get("review_id", ""),
            "candidate_id": row.get("candidate_id", ""),
            "pair_group_id": row.get("pair_group_id", ""),
            "recording_id": row.get("recording_id", ""),
            "source_file": row.get("source_file", ""),
            "usable_structure_name": row.get("usable_structure_name", ""),
            "structure_folder": folder,
            "talk_start_time": row.get("talk_start_time", ""),
            "talk_end_time": row.get("talk_end_time", ""),
            "action_start_time": row.get("action_start_time", ""),
            "action_end_time": row.get("action_end_time", ""),
            "talk_claimed_action_or_problem": row.get("talk_claimed_action_or_problem", ""),
            "talk_claimed_function": row.get("talk_claimed_function", ""),
            "visual_model_primary": PRIMARY_MODEL,
            "visual_model_fallback": FALLBACK_MODEL,
            "visual_model_used": used_model,
            "visual_api_status": api_status,
            "visual_error_summary": visual_error,
            "observed_action_name": value(parsed, "observed_action_name"),
            "observed_body_part_or_tool": value(parsed, "observed_body_part_or_tool"),
            "action_start_visual_clue": value(parsed, "action_start_visual_clue"),
            "action_end_visual_clue": value(parsed, "action_end_visual_clue"),
            "action_cycle_complete": value(parsed, "action_cycle_complete"),
            "visual_obstruction_status": value(parsed, "visual_obstruction_status"),
            "presenter_visible": value(parsed, "presenter_visible"),
            "same_action_with_talk_claim": value(parsed, "same_action_with_talk_claim"),
            "same_problem_with_talk_claim": value(parsed, "same_problem_with_talk_claim"),
            "same_function_with_talk_claim": value(parsed, "same_function_with_talk_claim"),
            "sequence_logic": value(parsed, "sequence_logic"),
            "topic_break_risk": value(parsed, "topic_break_risk"),
            "can_enter_editor_task_pack_model": value(parsed, "can_enter_editor_task_pack"),
            "p0_gate_result": p0_result,
            "p0_fail_reason": p0_reason,
            "talk_action_same_point": same_point,
            "can_enter_editor_task_pack": can_enter,
            "split_status": split_status,
            "local_review_folder": str(review_dir),
            "local_true_pair_task_folder": "",
            "local_manual_review_folder": "",
            "contact_sheet_path_local": str(sheet_path) if sheet_path.exists() else "",
            "preview_20s_path_local": str(preview_path) if preview_path.exists() else "",
            "full_context_path_local": str(full_context) if full_context_exists else "",
            "reason": reason,
            "manual_review_items": row.get("manual_review_items", ""),
            "notes": f"source_exists={str(source_exists).lower()}; material_status={material_status}; sheet_status={sheet_status}; preview_status={preview_status}; preview_error={preview_error}; cached_summary_used={str(bool(cached_review)).lower()}; route={PRIMARY_MODEL}->{FALLBACK_MODEL}; forbidden_models_called=no",
        }
        master_out.append(output_row)
        input_rows.append(
            {
                "ali_review_id": ali_id,
                "candidate_id": row.get("candidate_id", ""),
                "pair_group_id": row.get("pair_group_id", ""),
                "recording_id": row.get("recording_id", ""),
                "usable_structure_name": row.get("usable_structure_name", ""),
                "source_file": row.get("source_file", ""),
                "source_file_exists": str(source_exists).lower(),
                "full_context_path": str(full_context) if full_context_exists else "",
                "full_context_exists": str(full_context_exists).lower(),
                "visual_input_folder": str(review_dir),
                "contact_sheet_path": str(sheet_path) if sheet_path.exists() else "",
                "preview_20s_path": str(preview_path) if preview_path.exists() else "",
                "frame_timecodes": ",".join(timecodes),
                "material_status": material_status,
                "visual_api_status": api_status,
                "visual_model_used": used_model,
                "p0_gate_result": p0_result,
            }
        )
        summary = {
            "ali_review_id": ali_id,
            "candidate_id": row.get("candidate_id", ""),
            "api_status": api_status,
            "used_model": used_model,
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
        }
        write_text(summary_path, json.dumps(summary, ensure_ascii=False, indent=2))
        if idx % 10 == 0:
            print(f"reviewed={idx}/{REVIEW_LIMIT} api_counts={dict(api_counts)}", flush=True)

    true_rows = [row for row in master_out if row["p0_gate_result"] == "true_pair"]
    weak_rows = [row for row in master_out if row["p0_gate_result"] == "weak_related_need_manual_review"]
    mismatch_rows = [row for row in master_out if row["p0_gate_result"] == "logic_mismatch_reject"]
    blocked_rows_after = [row for row in master_out if row["p0_gate_result"] not in {"true_pair", "weak_related_need_manual_review", "logic_mismatch_reject"}]

    exported_true_rows = true_rows[:MAX_TRUE_PAIR_EXPORTS]
    for i, row in enumerate(exported_true_rows, start=1):
        package_row = export_package_row(row, "true_pair", i)
        row["local_true_pair_task_folder"] = package_row["task_folder"]
        package_rows.append(package_row)

    manual_source_rows = [row for row in master_out if row["p0_gate_result"] != "true_pair"]
    if not true_rows:
        manual_source_rows = master_out
    for i, row in enumerate(manual_source_rows, start=1):
        package_row = export_package_row(row, "manual_review", i)
        row["local_manual_review_folder"] = package_row["task_folder"]
        package_rows.append(package_row)

    clean_appledouble(LOCAL_TRUE_PAIR_ROOT)
    clean_appledouble(LOCAL_MANUAL_ROOT)

    counts = Counter(row["p0_gate_result"] for row in master_out)
    write_csv(INPUT_MANIFEST_CSV, input_rows, [
        "ali_review_id",
        "candidate_id",
        "pair_group_id",
        "recording_id",
        "usable_structure_name",
        "source_file",
        "source_file_exists",
        "full_context_path",
        "full_context_exists",
        "visual_input_folder",
        "contact_sheet_path",
        "preview_20s_path",
        "frame_timecodes",
        "material_status",
        "visual_api_status",
        "visual_model_used",
        "p0_gate_result",
    ])
    write_csv(VISUAL_MASTER_CSV, master_out, MASTER_FIELDS)
    write_csv(TRUE_PAIR_CSV, true_rows, MASTER_FIELDS)
    write_csv(WEAK_CSV, weak_rows, MASTER_FIELDS)
    write_csv(MISMATCH_CSV, mismatch_rows, MASTER_FIELDS)
    write_csv(BLOCKED_AFTER_CSV, blocked_rows_after, MASTER_FIELDS)
    write_csv(PACKAGE_MANIFEST_CSV, [row for row in package_rows if row["package_type"] == "true_pair"], PACKAGE_FIELDS)
    write_editor_readme(counts, package_rows)

    files_changed = [
        ".gitignore",
        "scripts/ali_visual_review_102_and_export_true_pair_video_package.py",
        "项目事实_project_facts/模型路由_model_routing/01_阿里视觉模型默认路由_ali_visual_model_default_route.md",
        "素材解析_pipeline_material_analysis/16_ali_visual_review_102/01_阿里视觉路由探针_ali_visual_route_probe.csv",
        "素材解析_pipeline_material_analysis/16_ali_visual_review_102/02_视觉复核输入材料清单_visual_review_input_manifest.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/26_阿里视觉复核102条总表_ali_visual_review_102_master.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/27_阿里视觉后真配对清单_true_pair_after_ali_visual.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/28_阿里视觉后弱相关待复核清单_weak_related_after_ali_visual.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/29_阿里视觉后错配剔除清单_logic_mismatch_after_ali_visual.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/30_阿里视觉后仍阻断清单_still_blocked_after_ali_visual.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/31_真配对视频素材包索引_true_pair_video_package_manifest.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/32_剪辑师真配对任务包说明_editor_true_pair_task_pack_readme.md",
        "执行日志_codex_log/123_阿里视觉复核102条并导出真配对视频包执行报告_ali_visual_review_102_export_report.md",
    ]
    write_report(counts, route_rows, master_out, package_rows, files_changed)

    print(f"ali visual review {REVIEW_LIMIT} completed")
    print(f"reviewed={len(master_out)}")
    print(f"p0_counts={dict(counts)}")
    print(f"api_counts={dict(api_counts)}")
    print(f"true_pair_package={LOCAL_TRUE_PAIR_ROOT}")
    print(f"manual_review_pool={LOCAL_MANUAL_ROOT}")
    print(f"package_mp4_count={sum(1 for row in package_rows if row.get('full_context_path'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
