#!/usr/bin/env python3
"""Audit current finished videos against the structure formula library."""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
AUTHORIZED_ROOT = Path("/Volumes/WD_BLACK/澜心社剪辑")
MEDIA_CANDIDATES = [
    AUTHORIZED_ROOT / "剪辑解析数据/AI需要的成片",
    AUTHORIZED_ROOT / "剪辑解析数据-AI需要的成片",
]
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".mkv"}

ANALYSIS_DIR = REPO_ROOT / "素材解析_pipeline_material_analysis/09_current_finished_video_full_review"
FACT_DIR = REPO_ROOT / "项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video"
LOG_DIR = REPO_ROOT / "执行日志_codex_log"

INVENTORY_OUT = ANALYSIS_DIR / "当前成片素材清单_current_finished_video_inventory.csv"
MATRIX_OUT = ANALYSIS_DIR / "当前成片结构解析矩阵_current_finished_video_structure_matrix.csv"
FIT_SCORE_OUT = ANALYSIS_DIR / "结构公式适配评分表_structure_formula_fit_score_table.csv"
KEYFRAME_INDEX_OUT = ANALYSIS_DIR / "关键帧待人审索引_keyframe_manual_review_index.csv"

AUDIT_REPORT_OUT = FACT_DIR / "34_当前成片全量结构适配性复审报告_current_finished_video_structure_fit_audit.md"
REVISION_MAP_OUT = FACT_DIR / "35_结构公式修正映射表_structure_formula_revision_map.csv"
EDITOR_TABLE_OUT = FACT_DIR / "36_剪辑师可用结构表_editor_usable_structure_table.csv"
BRIDGE_REPORT_OUT = FACT_DIR / "37_成片结构到直播素材筛选桥接说明_finished_video_to_live_screening_bridge.md"
EXECUTION_REPORT_OUT = LOG_DIR / "116_当前成片全量结构适配性复审执行报告_current_finished_video_structure_fit_execution_report.md"

OLD_FORMULAS = [
    "人群点名 + 低门槛动作 + 坚持建议",
    "痛点可视化 + 解决方案 + 效果对比 + 行动指令",
    "人群点名 + 痛点放大 + 单动作演示 + 坚持建议",
    "痛点问题 + 原因解释 + 方法交付",
    "错误动作 + 正确动作 + 原因解释",
    "反面案例 + 原因解释 + 正确做法",
    "结果前置 + 操作过程 + 注意事项",
]

OLD_FORMULA_ACTIONS = {
    "人群点名 + 低门槛动作 + 坚持建议": {
        "action": "split",
        "new": "人群/年龄点名 + 同题动作证据 + 轻跟练收束",
        "problem": "旧公式过宽，把年龄、人群、结果承诺和低门槛动作混在一起；当前第一阶段需要拆出动作证据和禁用条件。",
        "why": "适合做第一阶段入口结构，但必须补动作完整循环、发力点、次数/方向/呼吸证据。",
    },
    "痛点可视化 + 解决方案 + 效果对比 + 行动指令": {
        "action": "rename",
        "new": "痛点/结果可视化 + 操作过程证据 + 低压行动",
        "problem": "旧公式中的效果对比容易被误写成业务效果成立；当前只能作为结构和证据要求。",
        "why": "可保留为高频剪辑结构，但要弱化效果承诺并强制人工复核健康/体型说法。",
    },
    "人群点名 + 痛点放大 + 单动作演示 + 坚持建议": {
        "action": "merge",
        "new": "痛点/人群点名 + 单动作完整循环 + 坚持建议",
        "problem": "与低门槛动作公式高度重叠；差异不在标签，而在痛点是否被动作同题兑现。",
        "why": "建议并入动作证据结构，剪辑师按痛点、动作完整性和结尾收束判断。",
    },
    "痛点问题 + 原因解释 + 方法交付": {
        "action": "keep",
        "new": "痛点问题 + 原因解释 + 方法交付",
        "problem": "适合直播素材筛选，但需要完整口播主语和原因链，不能只截问题句。",
        "why": "对长口播、问答和健康边界解释有用，可指导起止点。",
    },
    "错误动作 + 正确动作 + 原因解释": {
        "action": "keep",
        "new": "错误/误区先抛 + 正确动作对比 + 原因解释",
        "problem": "旧公式适配第一阶段，但必须看得出错在哪里、正确在哪里。",
        "why": "适合直播素材筛选，尤其适合从长录屏里抓误区纠正段。",
    },
    "反面案例 + 原因解释 + 正确做法": {
        "action": "merge",
        "new": "错误/误区先抛 + 正确动作对比 + 原因解释",
        "problem": "当前素材里反面案例与错误纠正边界重叠，单独保留会增加剪辑师判断成本。",
        "why": "并入错误纠正结构，保留反面案例作为开头证据形态。",
    },
    "结果前置 + 操作过程 + 注意事项": {
        "action": "keep",
        "new": "结果前置 + 操作过程 + 注意事项/风险边界",
        "problem": "适合短成片复盘，但直播素材筛选时需要额外确认注意事项和健康边界。",
        "why": "可保留，但第一阶段优先级低于痛点、误区和动作证据结构。",
    },
}

PAIN_PATTERNS = [
    ("漏尿漏水尴尬", r"漏尿|漏水|漏气|跑跳|咳嗽|失控|尴尬|漏氵"),
    ("盆底松弛无力", r"盆底|盆盆松|松弛|收紧|紧致|J致|致|八爪鱼|抓握力"),
    ("盆底高张疼痛", r"高张|疼痛|不舒服"),
    ("小腹凸/腹压/悬垂腹", r"小肚子|小腹|悬垂腹|腹内压|腹部|肚子|腹直肌"),
    ("臀凹陷/妈妈臀/扁平臀", r"妈妈臀|臀凹陷|扁平臀|蜜桃臀|臀饱满|臀翘|塌臀|臀部"),
    ("膨出脱垂/下垂", r"膨出|脱垂|下垂|宫下垂|Z宫|前壁|内脏下垂"),
    ("假胯宽/骨盆外翻/体态问题", r"假跨|假胯|骨盆|体态|背变厚|胯|腰细|腿细"),
    ("误区/练错动作", r"误区|别再|单纯|疯狂练|练错|瞎练|错误|错"),
]

RESULT_PATTERNS = [
    ("小腹平/肚子平", r"平了|小腹.*不见|凸出不见|肚子平|腹.*变小|少女腹|马甲线"),
    ("臀翘/臀饱满/蜜桃臀", r"臀翘|臀饱满|蜜桃臀|会跳舞的臀|臀部翘"),
    ("盆底紧致/八爪鱼/抓握力", r"紧|J致|八爪鱼|抓握力|越练越紧|Q弹"),
    ("漏尿漏水改善", r"告别.*漏|漏.*改善|漏.*改变|尴尬.*没有|不漏|改变.*漏"),
    ("腰细/胯小/腿细", r"腰细|收腰|胯.*小|收胯|腿细"),
    ("好状态/抗衰体态", r"好状态|抗衰|背.*薄|高段位|年轻"),
]

ACTION_PATTERNS = [
    ("单动作循环演示", r"一个动作|一招|这一式|每天|坚持|跟练|练习|动作"),
    ("多动作组合演示", r"两个动作|三个动作|四个动作|几个动作|五组|四组"),
    ("工具辅助动作", r"瑜伽球|小球|球|凯格尔|臀桥|蝴蝶|握力|开合"),
    ("分步口令/计数教学", r"分钟|100|十分钟|5分钟|10分钟|次数|组|吸气|呼气"),
    ("图解/解剖辅助说明", r"盆底肌|腹横肌|腹直肌|骨盆|内压力|发力"),
]

RISK_PATTERNS = [
    ("医学/健康边界风险", r"漏尿|漏水|脱垂|膨出|高张|疼痛|宫下垂|前壁|内脏|盆底|修复"),
    ("效果承诺风险", r"平了|翘了|紧了|瘦|改善|告别|修复|改变|搞定|不见了|越练越"),
    ("单一方法过度承诺", r"只需|一个动作|一个小球|搞定|每天100|不管生完多久"),
    ("高发误区/比例刺激", r"70%|中招|误区"),
]


@dataclass
class ProbeResult:
    path: Path
    current_video_id: str
    file_name: str
    relative_path: str
    file_size_bytes: int
    file_size_mb: str
    duration_seconds: str
    resolution: str
    aspect_ratio: str
    fps: str
    video_codec: str
    has_audio: str
    audio_codec: str
    video_read_status: str
    error_message: str
    possible_duplicate_group: str = ""
    first_frame_decode_status: str = "not_run"


def run_command(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )


def select_media_dir() -> Path:
    for candidate in MEDIA_CANDIDATES:
        if candidate.exists() and candidate.is_dir():
            return candidate

    matches = [
        path
        for path in AUTHORIZED_ROOT.rglob("*")
        if path.is_dir() and "剪辑解析数据" in path.name and "AI需要的成片" in path.name
    ]
    if matches:
        return sorted(matches)[0]
    raise FileNotFoundError("找不到当前素材目录：剪辑解析数据/AI需要的成片")


def gather_video_files(media_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in media_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    )


def ratio(width: int, height: int) -> str:
    if width <= 0 or height <= 0:
        return "pending"
    divisor = math.gcd(width, height)
    return f"{width // divisor}:{height // divisor}"


def parse_fps(value: str) -> str:
    if not value or value == "0/0":
        return "pending"
    if "/" not in value:
        return value
    numerator, denominator = value.split("/", 1)
    try:
        denominator_float = float(denominator)
        if denominator_float == 0:
            return "pending"
        return f"{float(numerator) / denominator_float:.3f}"
    except ValueError:
        return "pending"


def safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def probe_video(path: Path, media_dir: Path, index: int) -> ProbeResult:
    current_video_id = f"cfv_{index:04d}"
    file_size = path.stat().st_size
    base = ProbeResult(
        path=path,
        current_video_id=current_video_id,
        file_name=path.name,
        relative_path=str(path.relative_to(media_dir)),
        file_size_bytes=file_size,
        file_size_mb=f"{file_size / 1024 / 1024:.3f}",
        duration_seconds="pending",
        resolution="pending",
        aspect_ratio="pending",
        fps="pending",
        video_codec="pending",
        has_audio="false",
        audio_codec="",
        video_read_status="failed",
        error_message="pending",
    )
    if path.name.startswith("._"):
        base.error_message = "AppleDouble metadata file：文件名以 ._ 开头，不按正常视频解析"
        return base

    if shutil.which("ffprobe") is None:
        base.error_message = "ffprobe_not_available"
        return base

    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        timeout=40,
    )
    if result.returncode != 0:
        base.error_message = result.stderr.strip().replace("\n", " ")[:500] or "ffprobe_failed"
        return base

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        base.error_message = f"ffprobe_json_decode_failed: {exc}"
        return base

    streams = payload.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio_stream = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    duration = payload.get("format", {}).get("duration") or (video_stream or {}).get("duration")

    if not video_stream:
        base.error_message = "no_video_stream"
        return base

    width = int(video_stream.get("width") or 0)
    height = int(video_stream.get("height") or 0)
    base.duration_seconds = f"{float(duration):.3f}" if duration else "pending"
    base.resolution = f"{width}x{height}" if width and height else "pending"
    base.aspect_ratio = ratio(width, height)
    base.fps = parse_fps(video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate") or "")
    base.video_codec = video_stream.get("codec_name") or "pending"
    base.has_audio = "true" if audio_stream else "false"
    base.audio_codec = (audio_stream or {}).get("codec_name") or ""
    base.video_read_status = "success"
    base.error_message = ""
    return base


def check_first_frame(path: Path) -> tuple[str, str]:
    if shutil.which("ffmpeg") is None:
        return "not_run", "ffmpeg_not_available"
    result = run_command(
        ["ffmpeg", "-v", "error", "-ss", "0", "-i", str(path), "-frames:v", "1", "-f", "null", "-"],
        timeout=25,
    )
    if result.returncode == 0:
        return "success", ""
    return "failed", result.stderr.strip().replace("\n", " ")[:300] or "first_frame_decode_failed"


def normalize_title(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"^\._", "", stem)
    stem = re.sub(r"\d+月\d+日|\d+\.\d+|6\.\d+|\d+岁|\d+\+|\d+＋", "", stem)
    stem = re.sub(r"[\s()（）？?《》“”\"'、，,。._-]+", "", stem)
    return stem.lower()


def assign_duplicate_groups(results: list[ProbeResult]) -> None:
    groups: dict[str, list[ProbeResult]] = defaultdict(list)
    for item in results:
        duration_key = item.duration_seconds if item.duration_seconds != "pending" else "pending"
        duration_bucket = str(round(float(duration_key))) if duration_key != "pending" else "pending"
        key = f"{normalize_title(item.path)}|{item.file_size_bytes}|{duration_bucket}"
        groups[key].append(item)

    group_index = 1
    for members in groups.values():
        if len(members) < 2:
            continue
        group_id = f"dup_{group_index:03d}"
        for member in members:
            member.possible_duplicate_group = group_id
        group_index += 1


def first_match(patterns: list[tuple[str, str]], text: str, default: str) -> str:
    for label, pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return label
    return default


def all_matches(patterns: list[tuple[str, str]], text: str) -> list[str]:
    return [label for label, pattern in patterns if re.search(pattern, text, flags=re.IGNORECASE)]


def infer_old_formula(text: str, duration: float | None) -> str:
    if re.search(r"误区|别再|单纯|错|瞎练|疯狂练|越练越漏|错误", text):
        return "错误动作 + 正确动作 + 原因解释"
    if re.search(r"能.*吗|先.*还是|为什么|多久|多少次|怎么办|好吗|测试|及格", text):
        return "痛点问题 + 原因解释 + 方法交付"
    if re.search(r"只需|告别|不见|搞定|改变|改善|平了|翘了|紧了|瘦|收腰|收胯", text):
        return "痛点可视化 + 解决方案 + 效果对比 + 行动指令"
    if re.search(r"30|35|40|女性|姐妹|宝妈|产后|妈妈|高段位", text):
        return "人群点名 + 低门槛动作 + 坚持建议"
    if re.search(r"一个动作|两个动作|三个动作|四个动作|每天|坚持|练习|分钟|小球|瑜伽球|臀桥", text):
        return "人群点名 + 痛点放大 + 单动作演示 + 坚持建议"
    if duration and duration > 90:
        return "痛点问题 + 原因解释 + 方法交付"
    return "待视觉复核：文件名无足够结构信息"


def infer_new_formula(text: str, old_formula: str) -> str:
    pain = first_match(PAIN_PATTERNS, text, "泛身体状态/待视觉复核")
    action = first_match(ACTION_PATTERNS, text, "动作证据待视觉复核")
    if old_formula == "错误动作 + 正确动作 + 原因解释":
        return f"误区/错误先抛 + 正确动作对比 + 原因解释（{pain}）"
    if old_formula == "痛点问题 + 原因解释 + 方法交付":
        return f"问题问答 + 原因解释 + 方法边界（{pain}）"
    if old_formula == "痛点可视化 + 解决方案 + 效果对比 + 行动指令":
        return f"痛点/结果可视化 + {action} + 低压行动"
    if old_formula == "人群点名 + 低门槛动作 + 坚持建议":
        return f"人群/年龄点名 + {action} + 坚持建议"
    if old_formula == "人群点名 + 痛点放大 + 单动作演示 + 坚持建议":
        return f"痛点/人群点名 + {action} + 坚持建议"
    return "待视觉复核：需关键帧/人工判断后定公式"


def formula_action(old_formula: str) -> str:
    return OLD_FORMULA_ACTIONS.get(old_formula, {"action": "pending_visual_review"})["action"]


def score_editor(item: ProbeResult, text: str) -> int:
    if item.video_read_status != "success":
        return 1
    duration = safe_float(item.duration_seconds)
    signals = len(all_matches(PAIN_PATTERNS, text)) + len(all_matches(ACTION_PATTERNS, text))
    if duration and duration > 150:
        return 3
    if signals >= 2 and item.has_audio == "true" and item.aspect_ratio == "9:16":
        return 3
    if signals >= 1:
        return 3
    return 1


def score_live_transfer(item: ProbeResult, text: str, old_formula: str) -> int:
    if item.video_read_status != "success":
        return 1
    if old_formula in {"错误动作 + 正确动作 + 原因解释", "痛点问题 + 原因解释 + 方法交付"}:
        return 3
    if re.search(r"只需|搞定|不见了|平了|翘了|越练越|告别", text):
        return 1
    return 3 if len(all_matches(PAIN_PATTERNS, text)) >= 1 else 1


def missing_part(text: str, old_formula: str) -> str:
    missing = []
    if not all_matches(PAIN_PATTERNS, text) and not re.search(r"30|35|40|女性|产后|宝妈|妈妈", text):
        missing.append("缺开头人群/痛点")
    if not all_matches(ACTION_PATTERNS, text):
        missing.append("缺动作证据")
    if old_formula == "待视觉复核：文件名无足够结构信息":
        missing.append("缺视觉结构证据")
    if re.search(r"只需|搞定|平了|翘了|紧了|告别|改善|改变", text):
        missing.append("缺业务/健康事实确认")
    return "；".join(missing) if missing else "无明显缺失但需视觉人审"


def editor_action(editor_score: int, live_score: int, old_formula: str) -> str:
    if old_formula.startswith("待视觉复核"):
        return "只作灵感"
    if editor_score >= 3 and live_score >= 3:
        return "可二次加工"
    if editor_score >= 3:
        return "只作灵感"
    return "不建议当前阶段使用"


def priority(editor_score: int, live_score: int, text: str) -> str:
    if editor_score >= 3 and live_score >= 3 and re.search(r"误区|别再|能.*吗|为什么|漏尿|盆底|动作", text):
        return "A"
    if editor_score >= 3:
        return "B"
    return "C"


def inventory_row(item: ProbeResult) -> dict[str, str]:
    return {
        "current_video_id": item.current_video_id,
        "file_name": item.file_name,
        "source_path": str(item.path),
        "relative_path": item.relative_path,
        "file_size_mb": item.file_size_mb,
        "duration_seconds": item.duration_seconds,
        "resolution": item.resolution,
        "aspect_ratio": item.aspect_ratio,
        "fps": item.fps,
        "has_audio": item.has_audio,
        "video_codec": item.video_codec,
        "audio_codec": item.audio_codec,
        "video_read_status": item.video_read_status,
        "first_frame_decode_status": item.first_frame_decode_status,
        "error_message": item.error_message,
        "possible_duplicate_group": item.possible_duplicate_group,
        "notes": "AppleDouble 元数据噪音" if item.file_name.startswith("._") else "ffprobe 元数据 + 首帧解码探针",
    }


def matrix_row(item: ProbeResult) -> dict[str, str]:
    text = item.file_name + " " + item.relative_path
    duration = safe_float(item.duration_seconds)
    old_formula = infer_old_formula(text, duration)
    new_formula = infer_new_formula(text, old_formula)
    editor_score = score_editor(item, text)
    live_score = score_live_transfer(item, text, old_formula)
    pain = first_match(PAIN_PATTERNS, text, "待视觉复核")
    result = first_match(RESULT_PATTERNS, text, "待视觉复核")
    action = first_match(ACTION_PATTERNS, text, "待视觉复核")
    risks = all_matches(RISK_PATTERNS, text)
    analysis_status = "pending_visual_review" if item.video_read_status == "success" else "failed"
    if item.video_read_status != "success":
        old_formula = "failed_unreadable"
        new_formula = "failed_unreadable"

    return {
        "current_video_id": item.current_video_id,
        "file_name": item.file_name,
        "analysis_status": analysis_status,
        "old_structure_formula_match": old_formula,
        "new_structure_formula_candidate": new_formula,
        "formula_action": formula_action(old_formula),
        "editor_usable_score": str(editor_score),
        "live_screening_transfer_score": str(live_score),
        "opening_value": f"{pain}；基于标题/路径语义，待关键帧确认",
        "middle_delivery_value": f"{action}；需确认动作完整循环、发力点、方向/次数/呼吸",
        "ending_value": "轻跟练/收藏/风险提醒优先；强转化与效果承诺待人工删改",
        "action_visual_evidence": f"{action}；当前未调用视觉模型，动作画面证据待人审",
        "expression_or_emotion_evidence": "pending_visual_review：未做人脸/情绪视觉识别",
        "subtitle_or_text_evidence": "文件名/路径语义可辅助，不能替代字幕 OCR 或画面确认",
        "speech_action_sync": "pending_visual_review：未做 ASR/口播与动作同步验证",
        "missing_part": missing_part(text, old_formula),
        "recommended_editor_action": editor_action(editor_score, live_score, old_formula),
        "stage1_priority": priority(editor_score, live_score, text),
        "manual_review_items": "关键帧确认动作是否完整；字幕/口播是否同题兑现；健康/效果/价格/课程事实待客户确认",
        "risk_notes": "；".join(risks) if risks else "无明显标题风险，但仍需视觉和业务人审",
        "evidence_summary": f"元数据：{item.duration_seconds}s，{item.resolution}，{item.fps}fps，audio={item.has_audio}；标题锚点：{pain}/{result}/{action}",
    }


def keyframe_rows(results: list[ProbeResult]) -> list[dict[str, str]]:
    rows = []
    for item in results:
        if item.video_read_status != "success":
            continue
        duration = safe_float(item.duration_seconds) or 0
        if duration <= 0:
            timestamps = "pending"
        else:
            points = sorted({0, duration * 0.2, duration * 0.4, duration * 0.6, duration * 0.8, max(duration - 0.2, 0)})
            timestamps = "；".join(f"{point:.2f}s" for point in points)
        rows.append(
            {
                "current_video_id": item.current_video_id,
                "file_name": item.file_name,
                "source_path": str(item.path),
                "recommended_keyframe_timestamps": timestamps,
                "review_goal": "人工确认开头钩子、中段动作/解释、结尾收束是否同题连续",
                "local_media_generated": "no",
                "status": "pending_manual_visual_review",
            }
        )
    return rows


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key.replace("\ufeff", ""): value for key, value in row.items()} for row in csv.DictReader(handle)]


def average(values: list[int]) -> str:
    return f"{sum(values) / len(values):.2f}" if values else "0.00"


def build_fit_score_rows(matrix: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in matrix:
        formula = row["old_structure_formula_match"]
        if formula and formula != "failed_unreadable":
            grouped[formula].append(row)

    rows = []
    formula_id = 1
    for formula in OLD_FORMULAS + sorted(set(grouped) - set(OLD_FORMULAS)):
        members = grouped.get(formula, [])
        action = OLD_FORMULA_ACTIONS.get(formula, {"action": "pending_visual_review", "new": "待视觉复核", "problem": "当前命中不足或无法只靠元数据判断", "why": "需要关键帧或人工复核"})
        rows.append(
            {
                "formula_id": f"formula_{formula_id:03d}",
                "old_structure_formula": formula,
                "current_sample_count": str(len(members)),
                "editor_usable_score_avg": average([int(row["editor_usable_score"]) for row in members]),
                "live_screening_transfer_score_avg": average([int(row["live_screening_transfer_score"]) for row in members]),
                "main_problem": action["problem"],
                "recommended_action": action["action"],
                "new_formula_name": action["new"],
                "why": action["why"],
                "example_video_ids": "；".join(row["current_video_id"] for row in members[:8]),
                "manual_review_required": "yes",
            }
        )
        formula_id += 1

    new_candidates = Counter(row["new_structure_formula_candidate"] for row in matrix if row["analysis_status"] == "pending_visual_review")
    for formula, count in new_candidates.most_common():
        example_ids = [
            row["current_video_id"]
            for row in matrix
            if row["new_structure_formula_candidate"] == formula
        ][:12]
        rows.append(
            {
                "formula_id": f"new_{formula_id:03d}",
                "old_structure_formula": "new_candidate",
                "current_sample_count": str(count),
                "editor_usable_score_avg": "pending_visual_review",
                "live_screening_transfer_score_avg": "pending_visual_review",
                "main_problem": "这是当前素材标题/元数据触发的新候选结构，尚未通过关键帧视觉确认。",
                "recommended_action": "new",
                "new_formula_name": formula,
                "why": "用于提醒剪辑师本轮保留素材的真实主题更偏动作证据和直播筛选，而不是复用旧前100条标签。",
                "example_video_ids": "；".join(example_ids),
                "manual_review_required": "yes",
            }
        )
        formula_id += 1
    return rows


def build_revision_rows(fit_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for row in fit_rows:
        if row["old_structure_formula"] == "new_candidate":
            continue
        formula = row["old_structure_formula"]
        action = row["recommended_action"]
        rows.append(
            {
                "旧公式": formula,
                "当前问题": row["main_problem"],
                "建议动作": action,
                "新公式": row["new_formula_name"],
                "适用素材": "开头能点出人群/痛点/误区，且中段有同题动作、原因、图解或口令证据的素材",
                "不适用素材": "只有结果词、强承诺、日期文件名、缺动作过程、缺口播主语或需业务事实背书的素材",
                "起点建议": "从完整主语、痛点或错误动作出现前 1-3 秒开始，不能只截结果词。",
                "终点建议": "留到一次完整动作循环、原因解释或低压行动完整说完；风险提醒可向后多留 3-10 秒。",
                "需要的动作/画面证据": "动作完整循环；发力点/方向/次数/呼吸；错误与正确差异；字幕/口播同题兑现。",
                "缺什么就不能用": "缺动作证据、缺原因解释、缺同题衔接、缺健康/效果事实确认时不能直接剪成正向结论。",
                "是否适合直播素材筛选": "yes" if action in {"keep", "rename", "split", "merge"} else "pending",
                "是否适合剪辑师直接加工": "pending_user_review：只能作为筛选/加工表，不能写审美或业务通过。",
            }
        )
    return rows


def build_editor_rows(fit_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "usable_structure_name": "误区/错误先抛 + 正确动作对比 + 原因解释",
            "一句话说明": "先让观众看见错在哪里，再马上给正确做法和原因。",
            "适合什么素材": "误区、练错动作、越练越糟、凯格尔/盆底训练纠错类素材。",
            "开头从哪里切": "从错误动作、误区字幕或反常识问题完整出现处切。",
            "中段必须有什么": "同一个问题的正确动作、原因解释或对比画面。",
            "结尾切到哪里": "留到风险提醒或正确动作定型，不硬接新痛点。",
            "动作/画面必须看到什么": "错误和正确的差异；发力点、身体方向或图解说明。",
            "缺什么就不要直接剪": "看不出错与对的差异，或错误后没有原因/正确动作。",
            "适合做什么类型视频": "直播误区纠正、动作教学纠错、短成片复盘。",
            "剪辑师加工建议": "保留错误画面和正确画面的桥接，必要时加一条真实桥接字幕。",
            "第一阶段优先级": "A",
            "人工复核项": "动作专业性、健康边界、字幕是否夸大。",
        },
        {
            "usable_structure_name": "问题问答 + 原因解释 + 方法边界",
            "一句话说明": "用一个真实问题开头，中段讲原因，结尾给可执行但不夸大的方法。",
            "适合什么素材": "漏尿、盆底、修复顺序、训练频率、是否适合某动作等问答类素材。",
            "开头从哪里切": "从完整问题或二选一冲突句开始，保留主语。",
            "中段必须有什么": "原因链、分类判断、适用/不适用边界。",
            "结尾切到哪里": "留到方法边界或轻行动完整说完。",
            "动作/画面必须看到什么": "口播、字幕或图解必须承接同一个问题。",
            "缺什么就不要直接剪": "只剩问题，没有原因；或给出健康结论但缺业务复核。",
            "适合做什么类型视频": "直播答疑、知识讲解、候选片段筛选。",
            "剪辑师加工建议": "优先保留完整口播单元，少切碎半句话。",
            "第一阶段优先级": "A",
            "人工复核项": "医学/健康事实、课程效果和适用人群。",
        },
        {
            "usable_structure_name": "痛点/人群点名 + 单动作完整循环 + 坚持建议",
            "一句话说明": "先点中人群或痛点，再展示一次完整动作循环，最后低压跟练。",
            "适合什么素材": "产后、40+、盆底、臀部、小腹、骨盆等居家动作教学素材。",
            "开头从哪里切": "从人群/痛点和动作起势同时出现处切。",
            "中段必须有什么": "完整动作循环、发力点、方向、次数或呼吸。",
            "结尾切到哪里": "留到动作完成或坚持建议，不保留过强效果承诺。",
            "动作/画面必须看到什么": "人物、道具、关键身体部位和字幕口令同向。",
            "缺什么就不要直接剪": "缺发力点、动作被挡住、动作截在半程。",
            "适合做什么类型视频": "第一阶段动作素材筛选、剪辑师二次加工。",
            "剪辑师加工建议": "先按动作完整性选片，再决定是否补字幕解释。",
            "第一阶段优先级": "A",
            "人工复核项": "动作安全性、频次/次数是否适合泛人群。",
        },
        {
            "usable_structure_name": "痛点/结果可视化 + 操作过程证据 + 低压行动",
            "一句话说明": "结果或痛点可以做钩子，但必须用过程证据兑现。",
            "适合什么素材": "告别、改善、平了、翘了、紧了等结果表达较强的素材。",
            "开头从哪里切": "从结果词前的身体状态或动作起势开始，避免只截承诺。",
            "中段必须有什么": "操作过程、动作细节、图解、口令或对比证据。",
            "结尾切到哪里": "留到低压行动或注意事项，删除强卖和新承诺。",
            "动作/画面必须看到什么": "过程比结果更重要，至少能看见动作如何发生。",
            "缺什么就不要直接剪": "只有结果字幕，没有过程和证据。",
            "适合做什么类型视频": "成片结构复盘、可二次加工短视频。",
            "剪辑师加工建议": "把效果词降级成观看理由，不写业务事实成立。",
            "第一阶段优先级": "B",
            "人工复核项": "效果承诺、健康事实、是否过度营销。",
        },
        {
            "usable_structure_name": "工具/动作演示 + 发力口令 + 低压跟练收束",
            "一句话说明": "围绕小球、瑜伽球、臀桥等工具动作，保留口令和完整循环。",
            "适合什么素材": "工具辅助训练、口令教学、跟练片段。",
            "开头从哪里切": "从工具和动作目标同时出现处开始。",
            "中段必须有什么": "口令、发力方向、次数/组数、呼吸或注意点。",
            "结尾切到哪里": "留到最后一次完整动作或跟练提示。",
            "动作/画面必须看到什么": "工具位置、身体接触点、动作幅度清楚。",
            "缺什么就不要直接剪": "看不清工具位置或发力点。",
            "适合做什么类型视频": "动作素材筛选、剪辑师加工底稿。",
            "剪辑师加工建议": "优先选固定机位且口令清楚的素材。",
            "第一阶段优先级": "B",
            "人工复核项": "工具安全性、动作适用范围。",
        },
        {
            "usable_structure_name": "多动作组合 + 同一主题推进 + 轻跟练收束",
            "一句话说明": "多个动作可以保留，但必须服务同一个痛点或目标。",
            "适合什么素材": "两/三/四个动作组合、居家训练清单。",
            "开头从哪里切": "从组合目标或第一个动作起势前切。",
            "中段必须有什么": "动作顺序、每个动作的作用或至少清楚的动作段落。",
            "结尾切到哪里": "留到最后一个动作完成和轻行动出现。",
            "动作/画面必须看到什么": "动作切换有逻辑，不是无说明拼贴。",
            "缺什么就不要直接剪": "多个动作目标混乱，或缺动作之间的承接。",
            "适合做什么类型视频": "直播候选组合段、剪辑师二次加工。",
            "剪辑师加工建议": "必要时拆成单动作候选，不强行合成。",
            "第一阶段优先级": "B",
            "人工复核项": "动作顺序、安全性、字幕承接。",
        },
        {
            "usable_structure_name": "日期/主题不明素材 + 待视觉复核索引",
            "一句话说明": "文件名没有结构信息时，只进入人审索引，不直接归入公式。",
            "适合什么素材": "只有日期、编号或主题不明的可读视频。",
            "开头从哪里切": "待关键帧确认后再定。",
            "中段必须有什么": "待关键帧确认后再定。",
            "结尾切到哪里": "待关键帧确认后再定。",
            "动作/画面必须看到什么": "必须人工看原片或关键帧。",
            "缺什么就不要直接剪": "缺主题、缺动作、缺口播、缺视觉证据。",
            "适合做什么类型视频": "只适合素材清点和人审排队。",
            "剪辑师加工建议": "先看 `关键帧待人审索引`，确认后再归类。",
            "第一阶段优先级": "C",
            "人工复核项": "全部视觉结构字段。",
        },
    ]


def count_by(rows: list[dict[str, str]], field: str) -> Counter[str]:
    return Counter(row[field] for row in rows)


def md_table(counter: Counter[str], limit: int | None = None) -> str:
    items = counter.most_common(limit)
    if not items:
        return "| 项 | 数量 |\n|---|---:|\n"
    lines = ["| 项 | 数量 |", "|---|---:|"]
    lines += [f"| {key} | {value} |" for key, value in items]
    return "\n".join(lines) + "\n"


def write_reports(
    media_dir: Path,
    inventory: list[dict[str, str]],
    matrix: list[dict[str, str]],
    fit_rows: list[dict[str, str]],
    commands: list[str],
) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    total = len(inventory)
    readable = sum(1 for row in inventory if row["video_read_status"] == "success")
    failed = total - readable
    pending = sum(1 for row in matrix if row["analysis_status"] == "pending_visual_review")
    action_counts = count_by(matrix, "formula_action")
    priority_counts = count_by(matrix, "stage1_priority")
    formula_counts = count_by(matrix, "old_structure_formula_match")

    AUDIT_REPORT_OUT.write_text(
        f"""# 当前成片全量结构适配性复审报告

状态：`structure_fit_audit_generated_pending_user_visual_review`
生成时间：{now}

## 1. 本轮主结论

- `已确认`：本轮重新扫描当前素材目录 `{media_dir}`，当前匹配视频扩展名文件数为 `{total}`，不是旧 618 条，也不是旧前 100 条。
- `已确认`：本轮 `{readable}` 个文件可读并完成 ffprobe 元数据读取，`{failed}` 个文件失败或异常。
- `已确认`：本轮未上传完整视频，未调用外部视觉模型，未提交媒体、图片、contact sheet、API 原始输出或 `.env`。
- `部分成立`：旧 `structure_formula` 可继续作为第一阶段筛选参考，但需要重写成“剪辑师可用结构 + 动作/画面证据 + 人工复核项”。
- `待验证`：所有内容结构判断均为 `pending_visual_review`。当前矩阵只证明元数据可读、标题/路径语义可触发结构候选，不能证明审美通过、业务通过、动作专业性通过或批量稳定。

## 2. 当前素材数量

- 当前扫描文件数：{total}
- 可读视频数：{readable}
- 失败/异常文件数：{failed}
- pending 视觉复核数：{pending}

## 3. 旧结构公式适配性

{md_table(formula_counts)}

### 保留公式

- `痛点问题 + 原因解释 + 方法交付`：适合直播录屏里问答、原因解释、方法边界段。
- `错误动作 + 正确动作 + 原因解释`：适合误区纠正段，但必须看得出错和对的差异。
- `结果前置 + 操作过程 + 注意事项`：可保留，但第一阶段必须弱化效果承诺并补注意事项。

### 合并公式

- `人群点名 + 痛点放大 + 单动作演示 + 坚持建议` 建议并入“痛点/人群点名 + 单动作完整循环 + 坚持建议”。
- `反面案例 + 原因解释 + 正确做法` 建议并入“错误/误区先抛 + 正确动作对比 + 原因解释”。

### 拆分公式

- `人群点名 + 低门槛动作 + 坚持建议` 需要拆成年龄/身份触发、痛点触发、动作证据触发三层，否则剪辑师不知道按什么选起止点。

### 改名公式

- `痛点可视化 + 解决方案 + 效果对比 + 行动指令` 建议改为 `痛点/结果可视化 + 操作过程证据 + 低压行动`。

### 第一阶段暂不直接使用

- 文件名无结构信息、只有日期或 AppleDouble `._*` 异常文件，不进入第一阶段直接剪辑。
- 只有“只需/搞定/不见了/越练越”结果承诺但缺动作证据的素材，不能直接剪成正向结论。

### 建议新增公式

- `问题问答 + 原因解释 + 方法边界`
- `误区/错误先抛 + 正确动作对比 + 原因解释`
- `痛点/人群点名 + 单动作完整循环 + 坚持建议`
- `工具/动作演示 + 发力口令 + 低压跟练收束`

## 4. 除结构公式外发现的剪辑缺口

- 必须新增 `action_visual_evidence`、`speech_action_sync`、`missing_part`、`recommended_editor_action`、`stage1_priority`、`manual_review_items`。
- 必须把标题/字幕/口播里的健康、效果、课程、价格、权益、案例真实性统一标成 `待客户确认` 或人工复核。
- 对直播素材筛选来说，旧公式还缺 `起点建议`、`终点建议`、`缺什么就不要直接剪`、`能否迁移直播筛选`。
- 当前没有视觉模型复核，因此不能写 `content_validation=passed`。

## 5. 第一阶段直播素材筛选建议

优先筛选 A 类：

- 误区/错误纠正：有明确错误、原因和正确动作。
- 问题问答：有完整主语、原因链和方法边界。
- 单动作教学：能看到一次完整动作循环，并有发力点/方向/次数/呼吸。

谨慎筛选 B/C 类：

- 结果承诺强但缺动作过程的素材。
- 只有日期命名或主题不明的素材。
- 涉及健康/医学/体型效果强承诺的素材。

## 6. 风险与人工复核项

- `待验证`：关键帧视觉结构、字幕 OCR、ASR、说话动作同步。
- `待客户确认`：医学/健康效果、课程效果、价格权益、案例真实性、动作专业性。
- `pending_user_review`：剪辑师可用结构是否符合用户当前加工习惯。

## 7. 本轮不能确认

- 不确认审美通过。
- 不确认业务通过。
- 不确认动作专业性通过。
- 不确认批量自动剪辑稳定。
- 不确认旧 618 条或旧前 100 条结论仍适用。
""",
        encoding="utf-8",
    )

    BRIDGE_REPORT_OUT.write_text(
        f"""# 成片结构到直播素材筛选桥接说明

状态：`bridge_ready_pending_live_material_validation`
生成时间：{now}

## 1. 能迁移到直播素材筛选的结构

- `错误/误区先抛 + 正确动作对比 + 原因解释`：直播里常出现纠错和答疑，适合做候选片段。
- `痛点问题 + 原因解释 + 方法交付`：适合从完整直播中截取问题、原因、方法同题连续段。
- `痛点/人群点名 + 单动作完整循环 + 坚持建议`：适合筛选动作教学段，但必须保留完整动作循环。

## 2. 只适合成片复盘、不宜直接迁移的结构

- 只有强结果承诺的 `结果前置` 成片。
- 只有标题/字幕包装，缺少动作过程或原因解释的成片。
- 过度依赖成片包装、配乐、字幕节奏的结构；直播素材里未必有同样的视觉完成度。

## 3. 直播筛选额外需要字段

- `live_recording_id`、`start_time`、`end_time`、`duration_seconds`
- `speech_complete_unit`：口播是否为完整表达单元。
- `action_complete_cycle`：动作是否完成一次循环。
- `visual_obstruction_risk`：画面/字幕/贴纸是否挡住关键动作。
- `health_business_review_required`：健康、效果、课程、价格是否需业务复核。

## 4. 说话 + 动作 + 表情如何并入结构判断

第一阶段不只看公式名，而要看三条证据是否同向：

1. 说话：问题、原因、方法、结论是否主语完整。
2. 动作：动作起势、发力、回位或错误/正确对比是否完整。
3. 表情/画面：表情、身体部位、道具、图示是否服务同一个问题。

三条只要有一条断裂，就不能写 `publish_ready`，只能进入人工复核。

## 5. 剪辑人员如何使用

- 先看 `36_剪辑师可用结构表` 选结构。
- 再看矩阵里的 `stage1_priority` 和 `recommended_editor_action`。
- 最后人工看关键帧/原片，确认动作和字幕是否同题兑现。

## 6. 是否进入直播素材候选片段筛选

`部分成立`：可以进入“小批直播素材候选片段筛选 probe”，但不能直接进入完整自动剪辑系统。建议先用 A 类结构在 1-2 条直播录屏上做候选片段表。

## 7. 什么时候才需要 LangGraph / LangChain / runtime

只有当以下三件事完成后才需要：

- 剪辑师确认结构表可用。
- 真实直播素材候选片段筛选能稳定产出可复核候选。
- 字段、状态、人工复核闭环已经稳定。

本轮不进入 LangGraph / LangChain / runtime。
""",
        encoding="utf-8",
    )

    EXECUTION_REPORT_OUT.write_text(
        f"""# 当前成片全量结构适配性复审执行报告

状态：`generated_pending_git_closeout`
生成时间：{now}

## commands

{chr(10).join(f"- `{command}`" for command in commands)}

## result

- 当前项目仓库：`fthytwerwt-sudo/lanxinse--`
- 本地仓库路径：`{REPO_ROOT}`
- 当前素材目录：`{media_dir}`
- 当前视频扩展名匹配文件数：{total}
- 可读视频数：{readable}
- 失败视频数：{failed}
- pending 视频数：{pending}
- 是否使用视觉模型：no
- 是否上传完整视频：no
- 是否提交媒体：no
- 是否提交 API 原始输出：no
- 是否读取/提交 `.env`：no / no
- 是否写审美通过：no
- 是否写业务通过：no
- 是否写动作专业性通过：no
- 是否写批量稳定：no

## failed_items

- AppleDouble 或不可读视频文件数：{failed}
- 视觉模型/API 未使用：结构内容判断均标 `pending_visual_review`。

## files_changed

- `{INVENTORY_OUT.relative_to(REPO_ROOT)}`
- `{MATRIX_OUT.relative_to(REPO_ROOT)}`
- `{FIT_SCORE_OUT.relative_to(REPO_ROOT)}`
- `{KEYFRAME_INDEX_OUT.relative_to(REPO_ROOT)}`
- `{AUDIT_REPORT_OUT.relative_to(REPO_ROOT)}`
- `{REVISION_MAP_OUT.relative_to(REPO_ROOT)}`
- `{EDITOR_TABLE_OUT.relative_to(REPO_ROOT)}`
- `{BRIDGE_REPORT_OUT.relative_to(REPO_ROOT)}`
- `{EXECUTION_REPORT_OUT.relative_to(REPO_ROOT)}`
- `scripts/audit_current_finished_video_structure_fit.py`

## validation

- 脚本生成时完成：inventory rows={total}，matrix rows={len(matrix)}。
- 后续必须运行：`python3 -m py_compile scripts/audit_current_finished_video_structure_fit.py`
- 后续必须运行：`python3 scripts/check_ali_config_safety.py`
- 后续必须运行：`git diff --check`、`git diff --cached --check`
- 后续必须校验：CSV 表头、行数、状态字段、staged files 无媒体/secret/cache。

## commit / push / remote status

- commit：待本报告生成后执行。
- push：待本报告生成后执行。
- remote HEAD：待 push 后验证。
- 说明：commit hash 无法在被提交文件内自指记录，本轮最终 Git readback 以 Codex 最终回报为准。

## blocked reason

- 无 blocked。当前降级原因是未使用视觉模型，因此内容结构为 `pending_visual_review`，不是阻断。
""",
        encoding="utf-8",
    )


def validate_outputs(inventory: list[dict[str, str]], matrix: list[dict[str, str]]) -> None:
    if len(inventory) != len(matrix):
        raise RuntimeError(f"inventory/matrix row mismatch: {len(inventory)} vs {len(matrix)}")
    if any(not row["analysis_status"] for row in matrix):
        raise RuntimeError("matrix has empty analysis_status")
    for path in [INVENTORY_OUT, MATRIX_OUT, FIT_SCORE_OUT, REVISION_MAP_OUT, EDITOR_TABLE_OUT, KEYFRAME_INDEX_OUT]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            if not header:
                raise RuntimeError(f"CSV missing header: {path}")


def main() -> int:
    commands = [
        "git pull --ff-only",
        "读取 AGENTS.md、机制文件与旧结构事实文件",
        "ffprobe 当前素材目录全量视频扩展名文件",
        "ffmpeg 首帧解码探针（不生成媒体产物）",
        "生成 inventory/matrix/fit score/revision/editor/bridge/report",
    ]
    if not str(REPO_ROOT).startswith(str(AUTHORIZED_ROOT)):
        raise RuntimeError(f"blocked_wrong_workspace_root: {REPO_ROOT}")

    media_dir = select_media_dir()
    files = gather_video_files(media_dir)
    if not files:
        raise RuntimeError("blocked_no_current_finished_videos")

    results = [probe_video(path, media_dir, index) for index, path in enumerate(files, start=1)]
    for item in results:
        if item.video_read_status == "success":
            status, error = check_first_frame(item.path)
            item.first_frame_decode_status = status
            if status == "failed":
                item.video_read_status = "failed"
                item.error_message = error
    assign_duplicate_groups(results)

    inventory = [inventory_row(item) for item in results]
    matrix = [matrix_row(item) for item in results]
    fit_rows = build_fit_score_rows(matrix)
    revision_rows = build_revision_rows(fit_rows)
    editor_rows = build_editor_rows(fit_rows)
    keyframes = keyframe_rows(results)

    write_csv(INVENTORY_OUT, list(inventory[0].keys()), inventory)
    write_csv(MATRIX_OUT, list(matrix[0].keys()), matrix)
    write_csv(FIT_SCORE_OUT, list(fit_rows[0].keys()), fit_rows)
    write_csv(REVISION_MAP_OUT, list(revision_rows[0].keys()), revision_rows)
    write_csv(EDITOR_TABLE_OUT, list(editor_rows[0].keys()), editor_rows)
    write_csv(KEYFRAME_INDEX_OUT, list(keyframes[0].keys()), keyframes)
    write_reports(media_dir, inventory, matrix, fit_rows, commands)
    validate_outputs(inventory, matrix)

    print(f"media_dir={media_dir}")
    print(f"video_files={len(results)}")
    print(f"readable={sum(1 for row in inventory if row['video_read_status'] == 'success')}")
    print(f"failed={sum(1 for row in inventory if row['video_read_status'] != 'success')}")
    print(f"pending_visual_review={sum(1 for row in matrix if row['analysis_status'] == 'pending_visual_review')}")
    print(f"inventory={INVENTORY_OUT.relative_to(REPO_ROOT)}")
    print(f"matrix={MATRIX_OUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
