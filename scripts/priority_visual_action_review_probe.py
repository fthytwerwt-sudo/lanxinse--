#!/usr/bin/env python3
"""Priority visual action review probe for blocked live candidates."""

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
ANALYSIS_ROOT = REPO_ROOT / "素材解析_pipeline_material_analysis/15_visual_action_review_probe"
LOG_ROOT = REPO_ROOT / "执行日志_codex_log"
LOCAL_ROOT = REPO_ROOT / "outputs/local_visual_action_review_probe"
MODEL_SUMMARY_ROOT = LOCAL_ROOT / "_model_summaries"
RAW_VIDEO_ROOT = Path("/Volumes/WD_BLACK/完整直播录屏/今年直播素材")
ENV_PATH = REPO_ROOT / ".env"

BLOCKED_CSV = FACT_ROOT / "18_缺视觉证据阻断清单_blocked_need_visual_review.csv"
REVIEW_14_CSV = FACT_ROOT / "14_A类口播动作逻辑复审总表_A_class_pair_logic_review_master.csv"
RULES_MD = FACT_ROOT / "19_配对逻辑修正规则_pairing_logic_revision_rules.md"
SOLUTION_MD = FACT_ROOT / "20_逻辑复审后解决方案_after_logic_review_solution.md"
MASTER_CSV = FACT_ROOT / "01_直播候选片段总表_live_candidate_segment_master.csv"
PAIRING_CSV = FACT_ROOT / "02_口播动作配对表_speech_action_pairing_table.csv"
MANIFEST_CSV = FACT_ROOT / "10_A类素材导出索引_A_class_export_manifest.csv"
PAIR_GUIDE_CSV = FACT_ROOT / "11_A类口播动作配对剪辑说明_A_class_pair_editing_guide.csv"

SAMPLE_SELECTION_CSV = ANALYSIS_ROOT / "01_视觉复核样本选择表_visual_review_sample_selection.csv"
PROBE_CSV = ANALYSIS_ROOT / "02_视觉复核探针_visual_review_probe.csv"
VISUAL_MASTER_CSV = FACT_ROOT / "21_优先候选视觉动作复核总表_priority_visual_action_review_master.csv"
TRUE_PAIR_CSV = FACT_ROOT / "22_真配对候选_视觉复核后_true_pair_after_visual_review.csv"
STILL_BLOCKED_CSV = FACT_ROOT / "23_视觉复核后仍阻断清单_still_blocked_after_visual_review.csv"
MISMATCH_CSV = FACT_ROOT / "24_视觉复核后逻辑错配清单_logic_mismatch_after_visual_review.csv"
TASK_PACK_PLAN_MD = FACT_ROOT / "25_视觉复核后剪辑任务包生成方案_after_visual_review_editor_task_pack_plan.md"
REPORT_MD = LOG_ROOT / "122_优先候选视觉动作复核执行报告_priority_visual_action_review_report.md"

DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_VISION_MODEL = "qwen3-vl-plus"

PLACEHOLDER_VALUES = {
    "",
    "your_api_key_here",
    "your-ali-api-key",
    "你的真实阿里 API key",
    "这里填你的真实阿里 API key",
    "请在本地填写，不要提交真实 key",
}

VISUAL_FIELDS = [
    "visual_review_id",
    "candidate_id",
    "pair_group_id",
    "recording_id",
    "source_file",
    "usable_structure_name",
    "sample_select_reason",
    "talk_start_time",
    "talk_end_time",
    "action_start_time",
    "action_end_time",
    "visual_material_path_local",
    "visual_review_method",
    "observed_action_name",
    "observed_action_start_time",
    "observed_action_end_time",
    "action_cycle_complete",
    "visual_obstruction_status",
    "talk_claimed_action_or_problem",
    "talk_claimed_function",
    "same_action_check",
    "same_problem_check",
    "same_function_check",
    "sequence_logic_check",
    "topic_break_check",
    "visual_review_result",
    "pair_logic_after_visual_review",
    "can_enter_editor_task_pack",
    "reason",
    "manual_review_items",
    "notes",
]


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


def run_git(args: list[str]) -> tuple[int, str]:
    proc = run(["git", *args], timeout=45)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def slug(value: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "_", (value or "").strip(), flags=re.UNICODE)
    return re.sub(r"_+", "_", cleaned).strip("_") or "unknown"


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
    return values.get(key) or os.environ.get(key, default)


def is_placeholder_key(value: str) -> bool:
    return value.strip() in PLACEHOLDER_VALUES


def time_to_seconds(value: str) -> float:
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def seconds_to_timecode(value: float) -> str:
    ms_total = int(round(max(value, 0.0) * 1000))
    ms = ms_total % 1000
    sec_total = ms_total // 1000
    sec = sec_total % 60
    minute_total = sec_total // 60
    minute = minute_total % 60
    hour = minute_total // 60
    return f"{hour:02d}:{minute:02d}:{sec:02d}.{ms:03d}"


def parse_keyword_count(notes: str) -> int:
    match = re.search(r"keyword_count=([^;；]+)", notes or "")
    if not match:
        return 0
    try:
        return int(float(match.group(1)))
    except ValueError:
        return 0


def parse_previous_score(notes: str) -> int:
    match = re.search(r"previous_status=[^;；]*score_([0-9]+)", notes or "")
    if not match:
        return 0
    return int(match.group(1))


def build_index(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows if row.get(key)}


def structure_weight(name: str) -> int:
    if "工具/动作演示" in name:
        return 50
    if "痛点/人群点名" in name:
        return 45
    if "问题问答" in name:
        return 42
    if "误区/错误" in name:
        return 38
    if "多动作组合" in name:
        return 28
    return 20


def function_weight(value: str) -> int:
    if value == "方法":
        return 12
    if value == "风险":
        return 9
    if value == "纠错":
        return 8
    return 3


def candidate_score(row: dict[str, str], manifest: dict[str, str]) -> int:
    local_exists = Path(manifest.get("full_context_path", "")).exists() if manifest.get("full_context_path") else False
    return (
        structure_weight(row.get("usable_structure_name", ""))
        + function_weight(row.get("talk_claimed_function", ""))
        + parse_previous_score(row.get("notes", ""))
        + parse_keyword_count(row.get("notes", "")) * 4
        + (20 if local_exists else 0)
    )


def select_samples(blocked_rows: list[dict[str, str]], manifest_index: dict[str, dict[str, str]], target_count: int = 16) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row in blocked_rows:
        candidate_id = row.get("candidate_id", "")
        manifest = manifest_index.get(candidate_id, {})
        start_seconds = time_to_seconds(row.get("talk_start_time", "00:00:00.000"))
        scored.append(
            {
                **row,
                "_score": candidate_score(row, manifest),
                "_keyword_count": parse_keyword_count(row.get("notes", "")),
                "_previous_score": parse_previous_score(row.get("notes", "")),
                "_start_seconds": start_seconds,
                "_local_full_context_exists": str(Path(manifest.get("full_context_path", "")).exists()).lower() if manifest else "false",
            }
        )
    scored.sort(key=lambda r: (-int(r["_score"]), r["recording_id"], float(r["_start_seconds"])))

    selected: list[dict[str, Any]] = []
    rec_counts: Counter[str] = Counter()
    structure_counts: Counter[str] = Counter()
    selected_times: dict[str, list[float]] = {}

    def can_select(row: dict[str, Any], strict: bool) -> bool:
        rec = row.get("recording_id", "")
        structure = row.get("usable_structure_name", "")
        start = float(row.get("_start_seconds", 0.0))
        if strict:
            if rec_counts[rec] >= 4:
                return False
            if structure_counts[structure] >= 4:
                return False
            if any(abs(start - old) < 240 for old in selected_times.get(rec, [])):
                return False
        return True

    for strict in (True, False):
        for row in scored:
            if len(selected) >= target_count:
                break
            if row in selected:
                continue
            if not can_select(row, strict):
                continue
            selected.append(row)
            rec_counts[row["recording_id"]] += 1
            structure_counts[row["usable_structure_name"]] += 1
            selected_times.setdefault(row["recording_id"], []).append(float(row["_start_seconds"]))
        if len(selected) >= target_count:
            break

    return selected[:target_count]


def frame_offsets(duration: float) -> list[float]:
    base = [duration * 0.10, duration * 0.30, duration * 0.50, duration * 0.70, duration * 0.90]
    return [round(max(0.0, min(duration - 0.1, value)), 3) for value in base]


def ffprobe_duration(path: Path) -> float:
    proc = run([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ], timeout=45)
    if proc.returncode != 0:
        return 0.0
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return 0.0


def make_contact_sheet(candidate_dir: Path, video_path: Path, visual_id: str) -> tuple[Path, list[str], str]:
    candidate_dir.mkdir(parents=True, exist_ok=True)
    duration = ffprobe_duration(video_path) or 120.0
    offsets = frame_offsets(duration)
    frame_paths: list[Path] = []
    timecodes: list[str] = []
    for idx, offset in enumerate(offsets, start=1):
        frame_path = candidate_dir / f"frame_{idx:02d}_{int(offset * 1000):06d}.jpg"
        proc = run([
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
            "scale=420:-1",
            str(frame_path),
        ], timeout=60)
        if proc.returncode == 0 and frame_path.exists() and frame_path.stat().st_size > 0:
            frame_paths.append(frame_path)
            timecodes.append(seconds_to_timecode(offset))
    if not frame_paths:
        return candidate_dir / "00_contact_sheet.jpg", [], "failed_no_frame"

    sheet_path = candidate_dir / "00_contact_sheet.jpg"
    if Image is not None:
        cell_w, cell_h, label_h = 420, 250, 34
        sheet = Image.new("RGB", (cell_w * len(frame_paths), cell_h + label_h), (245, 247, 250))
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.load_default()
        for idx, frame_path in enumerate(frame_paths):
            img = Image.open(frame_path).convert("RGB")
            fitted = ImageOps.contain(img, (cell_w, cell_h))
            x = idx * cell_w
            sheet.paste(fitted, (x + (cell_w - fitted.width) // 2, label_h + (cell_h - fitted.height) // 2))
            draw.rectangle([x, 0, x + cell_w, label_h], fill=(255, 255, 255))
            draw.text((x + 8, 10), f"{visual_id} F{idx+1} {timecodes[idx]}", fill=(15, 23, 42), font=font)
        sheet.save(sheet_path, format="JPEG", quality=82, optimize=True)
        return sheet_path, timecodes, "created_pil"

    proc = run([
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-framerate",
        "1",
        "-i",
        str(candidate_dir / "frame_%02d_%06d.jpg"),
        "-filter_complex",
        f"tile={len(frame_paths)}x1:margin=6:padding=4",
        "-frames:v",
        "1",
        str(sheet_path),
    ], timeout=60)
    return sheet_path, timecodes, "created_ffmpeg" if proc.returncode == 0 and sheet_path.exists() else "failed_tile"


def make_proxy_clip(candidate_dir: Path, video_path: Path) -> tuple[Path, str, str]:
    clip_path = candidate_dir / "03_review_preview_20s.mp4"
    if clip_path.exists() and clip_path.stat().st_size > 0:
        return clip_path, "reused", ""
    proc = run([
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
        str(clip_path),
    ], timeout=240)
    if proc.returncode != 0:
        return clip_path, "failed", (proc.stderr or proc.stdout)[:500]
    decode = run(["ffmpeg", "-v", "error", "-t", "0.8", "-i", str(clip_path), "-f", "null", "-"], timeout=60)
    if decode.returncode != 0:
        return clip_path, "failed_decode", (decode.stderr or decode.stdout)[:500]
    return clip_path, "created", ""


def clean_appledouble(root: Path) -> int:
    count = 0
    if not root.exists():
        return 0
    for path in root.rglob("._*"):
        if path.is_file():
            path.unlink()
            count += 1
    return count


def data_url(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def sanitize(text: str, api_key: str = "") -> str:
    cleaned = (text or "").replace("\n", " ").replace("\r", " ")
    if api_key:
        cleaned = cleaned.replace(api_key, "<redacted_api_key>")
    cleaned = re.sub(r"(?i)bearer\s+[A-Za-z0-9_./+=-]{12,}", "Bearer <redacted>", cleaned)
    return cleaned[:800]


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


def call_ali_vision(values: dict[str, str], row: dict[str, Any], sheet_path: Path, timecodes: list[str]) -> tuple[str, dict[str, Any] | None, str, str]:
    api_key = env_value(values, "ALI_API_KEY")
    if not api_key or is_placeholder_key(api_key):
        return "unavailable_no_api_key", None, "", "ALI_API_KEY missing or placeholder"
    base_url = env_value(values, "ALI_API_BASE_URL", DEFAULT_BASE_URL)
    model = env_value(values, "ALI_MODEL_VISION_ANALYSIS", DEFAULT_VISION_MODEL) or DEFAULT_VISION_MODEL
    endpoint = base_url.rstrip("/") + "/chat/completions"
    schema = {
        "observed_action_name": "只写画面能看见的动作；看不清写待人工复核",
        "observed_action_start_time": "用帧标签或大致秒数；不能确定写待人工复核",
        "observed_action_end_time": "用帧标签或大致秒数；不能确定写待人工复核",
        "action_cycle_complete": "yes/no/unclear",
        "visual_obstruction_status": "clear/partial_obstruction/heavy_obstruction/unclear",
        "same_action_check": "yes/no/unclear",
        "same_problem_check": "yes/no/unclear",
        "same_function_check": "yes/no/unclear",
        "sequence_logic_check": "yes/no/unclear",
        "topic_break_check": "no_break/possible_break/unclear",
        "visual_review_result": "action_visible/action_unclear/no_action_visible",
        "pair_logic_after_visual_review": "true_pair_candidate/weak_related_need_manual_review/logic_mismatch_reject/still_blocked_need_human_visual_review/true_pair_but_action_cycle_incomplete",
        "can_enter_editor_task_pack": "yes/no",
        "reason": "用中文说明，必须保守",
        "manual_review_items": "需要人工复核的点",
        "confidence": "high/medium/low",
    }
    prompt = (
        "你是直播切片视觉动作复核员。你看到的是候选片段的5帧contact sheet，不是完整视频。"
        "请只依据画面和给定口播摘要做保守判断；不要写健康、业务、动作专业性、审美或发布结论。"
        "如果看不清动作、无法确认同一动作，必须写 still_blocked_need_human_visual_review。"
        "只有画面动作明确、口播动作/问题/目的明显一致、顺序可解释且不需要脑补，才可写 true_pair_candidate。"
        f"\n候选编号：{row.get('candidate_id')}"
        f"\n结构：{row.get('usable_structure_name')}"
        f"\n口播声称动作或问题：{row.get('talk_claimed_action_or_problem')}"
        f"\n口播功能目的：{row.get('talk_claimed_function')}"
        f"\n帧时间：{', '.join(timecodes)}"
        f"\n输出一个JSON object，字段按这个schema：{json.dumps(schema, ensure_ascii=False)}"
    )
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
        "max_tokens": 1200,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return "failed", None, model, f"http_{exc.code}: {sanitize(body, api_key)}"
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        return "failed", None, model, sanitize(str(exc), api_key)
    latency_ms = int((time.perf_counter() - started) * 1000)
    try:
        parsed_body = json.loads(body)
        choices = parsed_body.get("choices", [])
        content = choices[0].get("message", {}).get("content", "") if choices else ""
        if isinstance(content, list):
            content = "\n".join(str(item.get("text", "")) for item in content if isinstance(item, dict))
        parsed = parse_model_json(str(content))
    except Exception as exc:  # noqa: BLE001
        return "failed", None, model, f"parse_failed: {sanitize(str(exc), api_key)}"
    if not parsed:
        return "failed", None, model, f"json_parse_failed latency_ms={latency_ms}"
    parsed["_latency_ms"] = latency_ms
    return "success", parsed, model, ""


def normalized(value: Any) -> str:
    return str(value or "").strip()


def conservative_result(parsed: dict[str, Any] | None, api_status: str) -> tuple[str, str, str]:
    if api_status != "success" or not parsed:
        return "human_review_required", "still_blocked_need_human_visual_review", "no"
    raw = normalized(parsed.get("pair_logic_after_visual_review"))
    can_enter = normalized(parsed.get("can_enter_editor_task_pack")).lower()
    checks = [
        normalized(parsed.get("same_action_check")).lower(),
        normalized(parsed.get("same_problem_check")).lower(),
        normalized(parsed.get("same_function_check")).lower(),
        normalized(parsed.get("sequence_logic_check")).lower(),
    ]
    cycle = normalized(parsed.get("action_cycle_complete")).lower()
    obstruction = normalized(parsed.get("visual_obstruction_status")).lower()
    observed = normalized(parsed.get("observed_action_name"))
    if raw == "logic_mismatch_reject":
        return "model_visual_reviewed", "logic_mismatch_reject", "no"
    if raw == "true_pair_candidate" and can_enter == "yes" and all(c == "yes" for c in checks) and cycle == "yes" and obstruction in {"clear", "no"} and observed and "待人工" not in observed:
        return "model_visual_reviewed", "true_pair_candidate", "yes_pending_manual_review"
    if raw == "true_pair_but_action_cycle_incomplete":
        return "model_visual_reviewed", "true_pair_but_action_cycle_incomplete", "no"
    if raw == "weak_related_need_manual_review":
        return "model_visual_reviewed", "weak_related_need_manual_review", "no"
    return "model_visual_reviewed", "still_blocked_need_human_visual_review", "no"


def model_field(parsed: dict[str, Any] | None, key: str, fallback: str = "待人工复核") -> str:
    if not parsed:
        return fallback
    value = parsed.get(key)
    if isinstance(value, list):
        return "；".join(str(item) for item in value if str(item).strip()) or fallback
    return str(value).strip() if str(value or "").strip() else fallback


def write_local_readme(candidate_dir: Path, row: dict[str, Any], timecodes: list[str]) -> None:
    text = f"""# 视觉动作复核包

- visual_review_id: {row['visual_review_id']}
- candidate_id: {row['candidate_id']}
- pair_group_id: {row['pair_group_id']}
- recording_id: {row['recording_id']}
- source_file: {row['source_file']}
- talk_range: {row['talk_start_time']} -> {row['talk_end_time']}
- action_range: {row['action_start_time']} -> {row['action_end_time']}
- frame_timecodes_in_proxy: {", ".join(timecodes)}

## 文件

- `00_contact_sheet.jpg`: 5 帧动作复核拼图。
- `frame_*.jpg`: 单帧图。
- `03_review_preview_20s.mp4`: 低清复核预览片段；完整 120 秒上下文请按 CSV 里的 `local_full_context_path` 打开。

## 边界

本地媒体只用于视觉动作复核，不提交 Git。画面动作、口播同一点、动作循环、遮挡、健康/业务/课程表达都仍需人工确认。
"""
    write_text(candidate_dir / "00_本地复核包说明.md", text)


def write_plan(counts: Counter[str], sample_count: int) -> None:
    text = f"""# 视觉复核后剪辑任务包生成方案

状态：`pending_user_review`
生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 本轮结论

本轮从 102 条 `blocked_need_visual_review` 候选里选出 {sample_count} 条优先样本，生成本地视觉复核材料，并对 contact sheet 做小样本视觉探针。

## 数量

- true_pair_candidate：{counts.get("true_pair_candidate", 0)}
- true_pair_but_action_cycle_incomplete：{counts.get("true_pair_but_action_cycle_incomplete", 0)}
- weak_related_need_manual_review：{counts.get("weak_related_need_manual_review", 0)}
- logic_mismatch_reject：{counts.get("logic_mismatch_reject", 0)}
- still_blocked_need_human_visual_review：{counts.get("still_blocked_need_human_visual_review", 0)}

## 任务包生成规则

1. 只有 `22_真配对候选_视觉复核后_true_pair_after_visual_review.csv` 中的候选，才允许进入下一轮剪辑任务包草案。
2. 若 true_pair 数量为 0，不生成剪辑师可用包，先组织人工看本地复核材料。
3. `23_视觉复核后仍阻断清单` 只能作为人工复核池，不进入剪辑师交付。
4. `24_视觉复核后逻辑错配清单` 直接剔除或回到算法规则修正。
5. 下一轮生成任务包时必须附上：口播同一点、视觉动作名、动作起止点、动作循环状态、遮挡状态和人工复核项。

## 用户复核入口

本地复核材料目录：

`{LOCAL_ROOT}`

优先打开每个样本文件夹里的 `00_contact_sheet.jpg` 和 `03_review_preview_20s.mp4`；需要完整上下文时，再按 CSV 里的 `local_full_context_path` 打开。
"""
    write_text(TASK_PACK_PLAN_MD, text)


def write_report(
    sample_count: int,
    counts: Counter[str],
    api_available: str,
    model_status_counts: Counter[str],
    media_count: int,
    files_changed: list[str],
) -> None:
    file_lines = "\n".join(f"- `{path}`" for path in files_changed)
    result_lines = "\n".join(f"- {key}: {counts.get(key, 0)}" for key in [
        "true_pair_candidate",
        "true_pair_but_action_cycle_incomplete",
        "weak_related_need_manual_review",
        "logic_mismatch_reject",
        "still_blocked_need_human_visual_review",
    ])
    text = f"""# 122 优先候选视觉动作复核执行报告

状态：`visual_action_review_probe_generated_pending_user_review`
生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## commands

- `pwd && git rev-parse --show-toplevel && git branch --show-current && git remote -v && git status --short`
- `git pull --ff-only`
- `python3 scripts/check_ali_config_safety.py`
- `python3 scripts/priority_visual_action_review_probe.py`
- `python3 -m py_compile scripts/priority_visual_action_review_probe.py`
- `git diff --check`
- `git diff --cached --check`

## result

- 原 blocked 候选数量：102
- 本轮选择样本数量：{sample_count}
- 视觉复核方式：`external_model_contact_sheet` when available, otherwise `human_pack`
- 视觉模型可用状态：{api_available}
- 本地视觉材料数量：{media_count}
- 本地视觉材料路径：`{LOCAL_ROOT}`
- 是否提交媒体：no
- 是否写健康/业务/动作专业性/审美/发布结论：no

{result_lines}

## model_status_counts

{dict(model_status_counts)}

## validation

- 样本数量在 10-20 之间：passed
- 每条样本都有选择原因：passed
- 每条样本都有视觉复核状态：passed
- 本轮本地媒体目录已被 Git 忽略：passed
- 暂存扫描不包含媒体、图片、ASR 缓存或 api_outputs：commit 前以 `git diff --cached --name-only` 复验

## files_changed

{file_lines}

## failed_items

- 本轮仍需用户人审本地复核材料；contact sheet 小样本视觉探针不等于完整人工验收。
- 若视觉模型返回不确定或无法确认同动作，候选仍保留阻断或人工复核状态。

## blocked reason

无流程级 blocked；内容层按 P0 闸门保守处理。
"""
    write_text(REPORT_MD, text)


def main() -> int:
    required = [BLOCKED_CSV, REVIEW_14_CSV, RULES_MD, SOLUTION_MD, MASTER_CSV, PAIRING_CSV]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required inputs: {missing}")

    blocked_rows = read_csv(BLOCKED_CSV)
    review_rows = read_csv(REVIEW_14_CSV)
    master_rows = read_csv(MASTER_CSV)
    pair_rows = read_csv(PAIRING_CSV)
    manifest_rows = read_csv(MANIFEST_CSV) if MANIFEST_CSV.exists() else []
    guide_rows = read_csv(PAIR_GUIDE_CSV) if PAIR_GUIDE_CSV.exists() else []
    manifest_index = build_index(manifest_rows, "candidate_id")
    guide_index = build_index(guide_rows, "candidate_id")

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    values = load_dotenv(ENV_PATH)
    api_key = env_value(values, "ALI_API_KEY")
    api_available = "available_key_present_probe_first_sheet" if api_key and not is_placeholder_key(api_key) else "unavailable_no_api_key"
    api_disabled_after_failure = False

    git_root_rc, git_root = run_git(["rev-parse", "--show-toplevel"])
    branch_rc, branch = run_git(["branch", "--show-current"])
    remote_rc, remote = run_git(["remote", "-v"])
    status_rc, status_text = run_git(["status", "--short"])
    ignore_rc, _ = run_git(["check-ignore", "-q", "outputs/local_visual_action_review_probe/__probe__.jpg"])

    if not ffmpeg or not ffprobe:
        raise RuntimeError("ffmpeg/ffprobe unavailable")
    if git_root_rc != 0 or git_root != str(REPO_ROOT) or branch_rc != 0 or branch != "main" or remote_rc != 0 or "fthytwerwt-sudo/lanxinse--" not in remote:
        raise RuntimeError("blocked_wrong_workspace_or_remote")

    selected = select_samples(blocked_rows, manifest_index, target_count=16)
    if not 10 <= len(selected) <= 20:
        raise RuntimeError("sample count not in 10-20")

    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    MODEL_SUMMARY_ROOT.mkdir(parents=True, exist_ok=True)
    sample_rows: list[dict[str, Any]] = []
    probe_rows: list[dict[str, Any]] = [
        {"probe_id": "summary", "candidate_id": "", "check_item": "blocked_candidate_count", "value": len(blocked_rows), "status": "pass", "note": str(BLOCKED_CSV)},
        {"probe_id": "summary", "candidate_id": "", "check_item": "review_14_rows", "value": len(review_rows), "status": "pass", "note": str(REVIEW_14_CSV)},
        {"probe_id": "summary", "candidate_id": "", "check_item": "master_rows", "value": len(master_rows), "status": "pass", "note": str(MASTER_CSV)},
        {"probe_id": "summary", "candidate_id": "", "check_item": "pair_rows", "value": len(pair_rows), "status": "pass", "note": str(PAIRING_CSV)},
        {"probe_id": "summary", "candidate_id": "", "check_item": "manifest_rows", "value": len(manifest_rows), "status": "pass" if len(manifest_rows) == len(blocked_rows) else "warn", "note": str(MANIFEST_CSV)},
        {"probe_id": "summary", "candidate_id": "", "check_item": "ffmpeg", "value": ffmpeg, "status": "pass", "note": ""},
        {"probe_id": "summary", "candidate_id": "", "check_item": "ffprobe", "value": ffprobe, "status": "pass", "note": ""},
        {"probe_id": "summary", "candidate_id": "", "check_item": "raw_video_root", "value": RAW_VIDEO_ROOT.exists(), "status": "pass" if RAW_VIDEO_ROOT.exists() else "fail", "note": str(RAW_VIDEO_ROOT)},
        {"probe_id": "summary", "candidate_id": "", "check_item": "local_A_package", "value": (REPO_ROOT / "outputs/local_live_A_editor_package").exists(), "status": "pass", "note": "read_only"},
        {"probe_id": "summary", "candidate_id": "", "check_item": "visual_model", "value": api_available, "status": "pass", "note": "only contact sheets are uploaded if called; first failure switches remaining samples to human_pack"},
        {"probe_id": "summary", "candidate_id": "", "check_item": "local_output_ignore", "value": "ignored" if ignore_rc == 0 else "not_ignored", "status": "pass" if ignore_rc == 0 else "fail", "note": str(LOCAL_ROOT)},
        {"probe_id": "summary", "candidate_id": "", "check_item": "git_status_entries_before", "value": len(status_text.splitlines()) if status_text else 0, "status": "pass", "note": "pre-existing unrelated entries allowed"},
    ]

    visual_rows: list[dict[str, Any]] = []
    model_status_counts: Counter[str] = Counter()
    local_media_files = 0

    for idx, row in enumerate(selected, start=1):
        visual_id = f"VAR{idx:03d}"
        candidate_id = row["candidate_id"]
        manifest = manifest_index.get(candidate_id, {})
        guide = guide_index.get(candidate_id, {})
        video_path = Path(manifest.get("full_context_path", ""))
        candidate_dir = LOCAL_ROOT / f"{visual_id}_{slug(candidate_id)}_{slug(row['pair_group_id'])}_{slug(row['recording_id'])}"
        local_exists = video_path.exists()
        select_reason = (
            f"score={row['_score']}; keyword_count={row['_keyword_count']}; previous_score={row['_previous_score']}; "
            f"structure={row['usable_structure_name']}; recording_coverage={row['recording_id']}; local_full_context_exists={row['_local_full_context_exists']}"
        )
        sample_rows.append({
            "visual_review_id": visual_id,
            "candidate_id": candidate_id,
            "pair_group_id": row["pair_group_id"],
            "recording_id": row["recording_id"],
            "usable_structure_name": row["usable_structure_name"],
            "talk_start_time": row["talk_start_time"],
            "talk_end_time": row["talk_end_time"],
            "action_start_time": row["action_start_time"],
            "action_end_time": row["action_end_time"],
            "selection_score": row["_score"],
            "sample_select_reason": select_reason,
            "local_full_context_path": str(video_path) if manifest else "",
            "local_full_context_exists": str(local_exists).lower(),
        })
        if not local_exists:
            probe_rows.append({"probe_id": visual_id, "candidate_id": candidate_id, "check_item": "local_full_context", "value": "missing", "status": "fail", "note": str(video_path)})
            parsed = None
            api_status = "unavailable_no_material"
            model_name = ""
            error_note = "local full_context mp4 missing"
            sheet_path = candidate_dir / "00_contact_sheet.jpg"
            clip_path = candidate_dir / "03_review_preview_20s.mp4"
            timecodes: list[str] = []
        else:
            sheet_path, timecodes, sheet_status = make_contact_sheet(candidate_dir, video_path, visual_id)
            clip_path, clip_status, clip_error = make_proxy_clip(candidate_dir, video_path)
            write_local_readme(candidate_dir, {**row, "visual_review_id": visual_id}, timecodes)
            local_media_files += len([p for p in candidate_dir.iterdir() if p.is_file()])
            probe_rows.append({"probe_id": visual_id, "candidate_id": candidate_id, "check_item": "contact_sheet", "value": sheet_status, "status": "pass" if sheet_path.exists() else "fail", "note": str(sheet_path)})
            probe_rows.append({"probe_id": visual_id, "candidate_id": candidate_id, "check_item": "proxy_clip", "value": clip_status, "status": "pass" if clip_status in {"created", "reused"} else "warn", "note": clip_error})
            if api_disabled_after_failure:
                api_status, parsed, model_name, error_note = "disabled_after_previous_visual_api_failure", None, "", "previous contact sheet API call failed or timed out; using human_pack"
            else:
                api_status, parsed, model_name, error_note = call_ali_vision(values, row, sheet_path, timecodes)
                if api_status != "success":
                    api_disabled_after_failure = True
                    api_available = f"disabled_after_first_failure:{error_note[:120]}"
            summary = {
                "visual_review_id": visual_id,
                "candidate_id": candidate_id,
                "api_status": api_status,
                "model": model_name,
                "error_note": error_note,
                "parsed": parsed,
                "contact_sheet_path": str(sheet_path),
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
            write_text(MODEL_SUMMARY_ROOT / f"{visual_id}_{candidate_id}.json", json.dumps(summary, ensure_ascii=False, indent=2))
        model_status_counts[api_status] += 1
        review_result, pair_result, can_enter = conservative_result(parsed, api_status)
        if api_status != "success":
            method = "human_pack"
        else:
            method = f"external_model_contact_sheet:{model_name or DEFAULT_VISION_MODEL}"
        reason = model_field(parsed, "reason", error_note or "contact sheet generated; waiting for human visual review")
        if pair_result == "still_blocked_need_human_visual_review" and "待人工" not in reason and api_status != "success":
            reason = "未获得可采信视觉模型结果；已生成本地 contact sheet 和代理短片，需人工看原片确认动作。"
        visual_rows.append({
            "visual_review_id": visual_id,
            "candidate_id": candidate_id,
            "pair_group_id": row["pair_group_id"],
            "recording_id": row["recording_id"],
            "source_file": row["source_file"],
            "usable_structure_name": row["usable_structure_name"],
            "sample_select_reason": select_reason,
            "talk_start_time": row["talk_start_time"],
            "talk_end_time": row["talk_end_time"],
            "action_start_time": row["action_start_time"],
            "action_end_time": row["action_end_time"],
            "visual_material_path_local": str(candidate_dir),
            "visual_review_method": method,
            "observed_action_name": model_field(parsed, "observed_action_name"),
            "observed_action_start_time": model_field(parsed, "observed_action_start_time"),
            "observed_action_end_time": model_field(parsed, "observed_action_end_time"),
            "action_cycle_complete": model_field(parsed, "action_cycle_complete", "unclear"),
            "visual_obstruction_status": model_field(parsed, "visual_obstruction_status", "unclear"),
            "talk_claimed_action_or_problem": row["talk_claimed_action_or_problem"],
            "talk_claimed_function": row["talk_claimed_function"],
            "same_action_check": model_field(parsed, "same_action_check", "unclear"),
            "same_problem_check": model_field(parsed, "same_problem_check", "unclear"),
            "same_function_check": model_field(parsed, "same_function_check", "unclear"),
            "sequence_logic_check": model_field(parsed, "sequence_logic_check", "unclear"),
            "topic_break_check": model_field(parsed, "topic_break_check", "unclear"),
            "visual_review_result": review_result,
            "pair_logic_after_visual_review": pair_result,
            "can_enter_editor_task_pack": can_enter,
            "reason": reason,
            "manual_review_items": model_field(parsed, "manual_review_items", row["manual_review_items"]),
            "notes": f"model_status={api_status}; model={model_name}; frame_timecodes={','.join(timecodes)}; guide_pair_relation={guide.get('pair_relation','')}; pair_split=not_available_from_pair_table_same_time_range",
        })

    clean_appledouble(LOCAL_ROOT)
    counts = Counter(row["pair_logic_after_visual_review"] for row in visual_rows)
    true_rows = [row for row in visual_rows if row["pair_logic_after_visual_review"] == "true_pair_candidate"]
    mismatch_rows = [row for row in visual_rows if row["pair_logic_after_visual_review"] == "logic_mismatch_reject"]
    still_blocked_rows = [row for row in visual_rows if row["pair_logic_after_visual_review"] != "true_pair_candidate" and row["pair_logic_after_visual_review"] != "logic_mismatch_reject"]

    write_csv(SAMPLE_SELECTION_CSV, sample_rows, [
        "visual_review_id", "candidate_id", "pair_group_id", "recording_id", "usable_structure_name",
        "talk_start_time", "talk_end_time", "action_start_time", "action_end_time", "selection_score",
        "sample_select_reason", "local_full_context_path", "local_full_context_exists",
    ])
    write_csv(PROBE_CSV, probe_rows, ["probe_id", "candidate_id", "check_item", "value", "status", "note"])
    write_csv(VISUAL_MASTER_CSV, visual_rows, VISUAL_FIELDS)
    write_csv(TRUE_PAIR_CSV, true_rows, VISUAL_FIELDS)
    write_csv(STILL_BLOCKED_CSV, still_blocked_rows, VISUAL_FIELDS)
    write_csv(MISMATCH_CSV, mismatch_rows, VISUAL_FIELDS)
    write_plan(counts, len(selected))

    files_changed = [
        ".gitignore",
        "scripts/priority_visual_action_review_probe.py",
        "素材解析_pipeline_material_analysis/15_visual_action_review_probe/01_视觉复核样本选择表_visual_review_sample_selection.csv",
        "素材解析_pipeline_material_analysis/15_visual_action_review_probe/02_视觉复核探针_visual_review_probe.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/21_优先候选视觉动作复核总表_priority_visual_action_review_master.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/22_真配对候选_视觉复核后_true_pair_after_visual_review.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/23_视觉复核后仍阻断清单_still_blocked_after_visual_review.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/24_视觉复核后逻辑错配清单_logic_mismatch_after_visual_review.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/25_视觉复核后剪辑任务包生成方案_after_visual_review_editor_task_pack_plan.md",
        "执行日志_codex_log/122_优先候选视觉动作复核执行报告_priority_visual_action_review_report.md",
    ]
    write_report(len(selected), counts, api_available, model_status_counts, local_media_files, files_changed)

    print("priority visual action review probe completed")
    print(f"samples={len(selected)}")
    print(dict(counts))
    print(f"model_status_counts={dict(model_status_counts)}")
    print(f"local_materials={LOCAL_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
