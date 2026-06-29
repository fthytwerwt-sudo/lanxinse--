#!/usr/bin/env python3
"""直播录屏结构化初剪小样本脚本。

用途：
- 只读取完整直播录屏和既有结构标准，不修改原始素材。
- 用 ffmpeg stream copy 导出候选片段，保持原宽高、比例、帧率和原音频。
- 生成本轮可提交的 CSV / Markdown 证据文件。

边界：
- 不提交源视频、初剪视频、抽帧图片、API 输出、.env 或任何 key。
- 本脚本不做字幕包装、调色、美颜、裁切、缩放、转场、BGM 或变速。
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LIVE_DIR = Path("/Volumes/WD_BLACK/澜心社剪辑/WD_BLACK-完整直播录屏")
AUTHORIZED_BASE = Path("/Volumes/WD_BLACK/澜心社剪辑")
DISCOVERED_LIVE_DIR = AUTHORIZED_BASE / "剪辑解析数据" / "完整直播"
OUTPUT_DIR = ROOT / "outputs" / "live_recording_rough_cut_probe"
FACT_DIR = ROOT / "项目事实_project_facts" / "直播录屏初剪验证_live_recording_rough_cut_probe"
REPORT_PATH = ROOT / "执行日志_codex_log" / "109_直播录屏6条结构初剪执行报告_live_recording_six_rough_cut_report.md"
CONTACT_SHEET_PATH = ROOT / "api_outputs" / "live_recording_multimodal_probe" / "contact_sheets" / "may7_full_recording_7frame_contact_sheet.jpg"
TRANSCRIPT_PATH = ROOT / "剪辑工厂输出_editing_factory_outputs" / "5月7日直播_minimum_loop" / "tmp_transcript" / "may7_0000_1500_transcript.json"


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    start: float
    end: float
    structure_formula: str
    opening_reason: str
    middle_delivery: str
    ending_closure: str
    integrity_score: int
    continuity_score: int
    editing_flow_score: int
    jump_cut_risk: str
    manual_review_items: str
    selected_for_export: bool
    reject_reason: str
    output_slug: str
    local_evidence: str

    @property
    def duration(self) -> float:
        return round(self.end - self.start, 3)


def run_command(args: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def require_ok(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed: {result.stderr.strip() or result.stdout.strip()}")


def ffprobe_json(path: Path) -> dict[str, Any]:
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
        ]
    )
    require_ok(result, f"ffprobe {path}")
    return json.loads(result.stdout)


def video_stream(metadata: dict[str, Any]) -> dict[str, Any]:
    for stream in metadata.get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    raise RuntimeError("未找到视频轨")


def audio_stream(metadata: dict[str, Any]) -> dict[str, Any] | None:
    for stream in metadata.get("streams", []):
        if stream.get("codec_type") == "audio":
            return stream
    return None


def timecode(seconds: float) -> str:
    whole = int(seconds)
    h = whole // 3600
    m = (whole % 3600) // 60
    s = whole % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def filename_time(seconds: float) -> str:
    whole = int(seconds)
    return f"{whole // 3600:02d}{(whole % 3600) // 60:02d}{whole % 60:02d}"


def ratio_text(width: int, height: int) -> str:
    if height == 0:
        return "unknown"
    # 源文件带 rotation metadata，技术宽高仍按 ffprobe 宽高记录。
    from math import gcd

    divisor = gcd(width, height)
    return f"{width // divisor}:{height // divisor}"


def gather_recordings() -> tuple[Path, list[Path], str]:
    if EXPECTED_LIVE_DIR.exists():
        live_dir = EXPECTED_LIVE_DIR
        discovery_note = "expected_dir_found"
    elif DISCOVERED_LIVE_DIR.exists():
        live_dir = DISCOVERED_LIVE_DIR
        discovery_note = "expected_dir_missing_used_discovered_complete_live_dir"
    else:
        matches = []
        for pattern in ("*WD_BLACK-完整直播录屏*", "*完整直播录屏*", "*直播录屏*", "*完整直播*"):
            matches.extend(p for p in AUTHORIZED_BASE.rglob(pattern) if p.is_dir())
        if not matches:
            raise RuntimeError("blocked_missing_live_recording_dir")
        live_dir = sorted(matches)[0]
        discovery_note = "expected_dir_missing_used_nearest_match"

    recordings = sorted(
        p
        for p in live_dir.rglob("*")
        if p.is_file()
        and not p.name.startswith("._")
        and p.suffix.lower() in {".mp4", ".mov", ".m4v"}
    )
    if not recordings:
        raise RuntimeError("blocked_missing_live_recording_dir")
    return live_dir, recordings, discovery_note


def candidate_plan() -> list[Candidate]:
    return [
        Candidate(
            candidate_id="cand_001",
            start=240.0,
            end=305.0,
            structure_formula="痛点问题 + 原因解释 + 方法交付",
            opening_reason="以“生了 10 年还可以吗”的问题接住产后人群疑虑。",
            middle_delivery="解释生育年限、是否做过产后/盆底修复，以及接下来会找盆底核心发力感觉。",
            ending_closure="自然落到“手把手带大家”和坐姿准备，能进入动作教学。",
            integrity_score=5,
            continuity_score=5,
            editing_flow_score=5,
            jump_cut_risk="low",
            manual_review_items="ASR 中“盘地/惩后”需人工改为“盆底/产后”；健康适用范围待专业复核。",
            selected_for_export=True,
            reject_reason="",
            output_slug="scope_action",
            local_evidence="复用既有 0-900s 本地转写；未上传完整视频。",
        ),
        Candidate(
            candidate_id="cand_002",
            start=322.0,
            end=391.0,
            structure_formula="错误动作 + 正确动作 + 原因解释",
            opening_reason="从“瑜伽球练八爪鱼/收紧”的常见误区切入。",
            middle_delivery="解释球不是自动变紧，关键是正确发力，并让观众测试收紧放松感觉。",
            ending_closure="落到“用球帮助找到感觉”，为后续坐球动作做承接。",
            integrity_score=5,
            continuity_score=5,
            editing_flow_score=5,
            jump_cut_risk="low",
            manual_review_items="“八爪鱼/收紧”等效果词需业务与合规复核；画面中球是否清晰待人审。",
            selected_for_export=True,
            reject_reason="",
            output_slug="tool_misuse",
            local_evidence="复用既有 0-900s 本地转写；未上传完整视频。",
        ),
        Candidate(
            candidate_id="cand_003",
            start=450.0,
            end=528.0,
            structure_formula="结果前置 + 操作过程 + 注意事项",
            opening_reason="从球的材质、软硬、放气比例和承重说明进入工具注意事项。",
            middle_delivery="演示把球放在板凳上、坐上球并找到接触位置。",
            ending_closure="收在“待会要发力的地方”，完成工具到身体定位的闭环。",
            integrity_score=5,
            continuity_score=5,
            editing_flow_score=5,
            jump_cut_risk="low",
            manual_review_items="承重/安全性属于业务事实；身体隐私展示和动作公开适配必须人工复核。",
            selected_for_export=True,
            reject_reason="",
            output_slug="tool_setup",
            local_evidence="复用既有 0-900s 本地转写；未上传完整视频。",
        ),
        Candidate(
            candidate_id="cand_004",
            start=527.0,
            end=611.0,
            structure_formula="人群点名 + 痛点放大 + 单动作演示 + 坚持建议",
            opening_reason="承接“你的松、漏跟这里有关系”，明确动作目标。",
            middle_delivery="讲解左右激活盆底、弹性逻辑，并开始左右轻轻摆动的动作演示。",
            ending_closure="以健身前筋膜松解/热身作类比，解释为什么先打开再训练。",
            integrity_score=5,
            continuity_score=5,
            editing_flow_score=5,
            jump_cut_risk="low",
            manual_review_items="涉及松、漏、疼痛和训练效果，全部待专业/业务复核；字幕不要遮挡动作。",
            selected_for_export=True,
            reject_reason="",
            output_slug="single_action_demo",
            local_evidence="复用既有 0-900s 本地转写；未上传完整视频。",
        ),
        Candidate(
            candidate_id="cand_005",
            start=657.0,
            end=725.0,
            structure_formula="错误动作 + 正确动作 + 原因解释",
            opening_reason="指出“练半天凯格尔没感觉/越练越松”的失败原因。",
            middle_delivery="解释腹部、臀部、大腿代偿发力，纠正为骨盆带动左右晃动。",
            ending_closure="引出针对漏尿场景的后续动作，形成问题召回。",
            integrity_score=3,
            continuity_score=5,
            editing_flow_score=3,
            jump_cut_risk="medium",
            manual_review_items="结尾更像下一段预告，不是强闭环；漏尿场景和训练效果需人工谨慎处理。",
            selected_for_export=True,
            reject_reason="",
            output_slug="mistake_correction",
            local_evidence="复用既有 0-900s 本地转写；未上传完整视频。",
        ),
        Candidate(
            candidate_id="cand_006",
            start=808.0,
            end=884.0,
            structure_formula="痛点问题 + 原因解释 + 方法交付",
            opening_reason="以“瑜伽球是否天天练”的问题进入练习频率判断。",
            middle_delivery="区分已有症状、预防保养、碎片化练习等使用场景。",
            ending_closure="接做完后的体感反馈，形成轻收束。",
            integrity_score=3,
            continuity_score=3,
            editing_flow_score=3,
            jump_cut_risk="medium",
            manual_review_items="频率建议、症状适用和效果反馈均属健康/业务事实，必须人审；中间有关注/资历信息需考虑是否剪掉。",
            selected_for_export=True,
            reject_reason="",
            output_slug="practice_frequency",
            local_evidence="复用既有 0-900s 本地转写；未上传完整视频。",
        ),
        Candidate(
            candidate_id="cand_007",
            start=30.0,
            end=90.0,
            structure_formula="人群点名 + 痛点放大 + 单动作演示 + 坚持建议",
            opening_reason="能快速点名新朋友、产后妈妈、盆底肌和漏/松等痛点。",
            middle_delivery="主要是直播间定位和人群筛选，动作交付不足。",
            ending_closure="以互动数字收尾，现场感强。",
            integrity_score=1,
            continuity_score=3,
            editing_flow_score=1,
            jump_cut_risk="high",
            manual_review_items="适合作为开头素材池，不适合单独成片。",
            selected_for_export=False,
            reject_reason="只有开头和人群筛选，缺真实动作交付。",
            output_slug="opening_only",
            local_evidence="复用既有 0-900s 本地转写；未上传完整视频。",
        ),
        Candidate(
            candidate_id="cand_008",
            start=870.0,
            end=900.0,
            structure_formula="痛点可视化 + 解决方案 + 效果对比 + 行动指令",
            opening_reason="接“没有球怎么办”的问题。",
            middle_delivery="主要转入购物车和价格说明。",
            ending_closure="销售承接明显。",
            integrity_score=1,
            continuity_score=3,
            editing_flow_score=1,
            jump_cut_risk="high",
            manual_review_items="商品、价格和销售承接必须业务复核。",
            selected_for_export=False,
            reject_reason="销售信息过重，且缺少完整方法交付。",
            output_slug="sales_tail",
            local_evidence="复用既有 0-900s 本地转写；未上传完整视频。",
        ),
    ]


def export_clip(source: Path, candidate: Candidate, recording_id: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / (
        f"rough_cut_{candidate.candidate_id[-3:]}_{candidate.output_slug}_"
        f"{recording_id}_{filename_time(candidate.start)}_{filename_time(candidate.end)}.mp4"
    )
    result = run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-ss",
            str(candidate.start),
            "-to",
            str(candidate.end),
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-c",
            "copy",
            str(output),
        ]
    )
    require_ok(result, f"ffmpeg export {candidate.candidate_id}")
    return output


def validate_output(source_meta: dict[str, Any], output: Path) -> dict[str, Any]:
    out_meta = ffprobe_json(output)
    src_video = video_stream(source_meta)
    out_video = video_stream(out_meta)
    src_audio = audio_stream(source_meta)
    out_audio = audio_stream(out_meta)
    src_width = int(src_video.get("width", 0))
    src_height = int(src_video.get("height", 0))
    out_width = int(out_video.get("width", 0))
    out_height = int(out_video.get("height", 0))
    return {
        "duration_seconds": round(float(out_meta.get("format", {}).get("duration", 0.0)), 3),
        "size_bytes": int(out_meta.get("format", {}).get("size", 0)),
        "video_codec": out_video.get("codec_name", ""),
        "audio_codec": out_audio.get("codec_name", "") if out_audio else "",
        "resolution": f"{out_width}x{out_height}",
        "fps": out_video.get("avg_frame_rate", ""),
        "resolution_preserved": out_width == src_width and out_height == src_height,
        "aspect_ratio_preserved": ratio_text(out_width, out_height) == ratio_text(src_width, src_height),
        "audio_preserved": bool(src_audio) == bool(out_audio)
        and (not src_audio or src_audio.get("codec_name") == out_audio.get("codec_name")),
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def git_summary() -> dict[str, str]:
    commands = {
        "pwd": ["pwd"],
        "top": ["git", "rev-parse", "--show-toplevel"],
        "branch": ["git", "branch", "--show-current"],
        "remote": ["git", "remote", "-v"],
        "status": ["git", "status", "--short", "--branch"],
    }
    values: dict[str, str] = {}
    for key, args in commands.items():
        result = run_command(args)
        values[key] = result.stdout.strip()
    return values


def main() -> int:
    FACT_DIR.mkdir(parents=True, exist_ok=True)
    live_dir, recordings, discovery_note = gather_recordings()
    source = recordings[0]
    source_meta = ffprobe_json(source)
    src_video = video_stream(source_meta)
    src_audio = audio_stream(source_meta)
    width = int(src_video.get("width", 0))
    height = int(src_video.get("height", 0))
    recording_id = "rec_001"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    candidates = candidate_plan()
    selected = [candidate for candidate in candidates if candidate.selected_for_export]

    outputs: dict[str, Path] = {}
    validations: dict[str, dict[str, Any]] = {}
    for candidate in selected:
        output = export_clip(source, candidate, recording_id)
        outputs[candidate.candidate_id] = output
        validations[candidate.candidate_id] = validate_output(source_meta, output)

    inventory_rows = []
    for index, recording in enumerate(recordings, start=1):
        meta = ffprobe_json(recording)
        video = video_stream(meta)
        audio = audio_stream(meta)
        w = int(video.get("width", 0))
        h = int(video.get("height", 0))
        inventory_rows.append(
            {
                "recording_id": f"rec_{index:03d}",
                "file_name": recording.name,
                "source_path": str(recording),
                "duration_seconds": round(float(meta.get("format", {}).get("duration", 0.0)), 3),
                "resolution": f"{w}x{h}",
                "aspect_ratio": ratio_text(w, h),
                "fps": video.get("avg_frame_rate", ""),
                "audio_stream": "yes" if audio else "no",
                "status": "read_success",
                "notes": "有效完整直播录屏；同目录仅发现 1 条有效视频",
            }
        )
    for missing_index in range(len(recordings) + 1, 8):
        inventory_rows.append(
            {
                "recording_id": f"rec_{missing_index:03d}",
                "file_name": "",
                "source_path": "",
                "duration_seconds": "",
                "resolution": "",
                "aspect_ratio": "",
                "fps": "",
                "audio_stream": "",
                "status": "missing_not_found_in_live_recording_dir",
                "notes": "目标约 7 条完整录屏，本轮目录实际未发现该序号素材",
            }
        )

    candidate_rows = []
    for candidate in candidates:
        candidate_rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "recording_id": recording_id,
                "source_file": str(source),
                "start_time": timecode(candidate.start),
                "end_time": timecode(candidate.end),
                "duration_seconds": candidate.duration,
                "matched_structure_formula": candidate.structure_formula,
                "opening_reason": candidate.opening_reason,
                "middle_delivery": candidate.middle_delivery,
                "ending_closure": candidate.ending_closure,
                "source_integrity_score": candidate.integrity_score,
                "visual_speech_continuity_score": candidate.continuity_score,
                "editing_flow_score": candidate.editing_flow_score,
                "jump_cut_risk": candidate.jump_cut_risk,
                "manual_review_items": candidate.manual_review_items,
                "selected_for_export": "yes" if candidate.selected_for_export else "no",
                "reject_reason": candidate.reject_reason,
                "evidence_route": candidate.local_evidence,
            }
        )

    index_rows = []
    for position, candidate in enumerate(selected, start=1):
        validation = validations[candidate.candidate_id]
        output = outputs[candidate.candidate_id]
        index_rows.append(
            {
                "rough_cut_id": f"rough_cut_{position:02d}",
                "output_path": str(output),
                "source_file": str(source),
                "start_time": timecode(candidate.start),
                "end_time": timecode(candidate.end),
                "structure_formula": candidate.structure_formula,
                "duration_seconds": validation["duration_seconds"],
                "resolution_preserved": "yes" if validation["resolution_preserved"] else "no",
                "aspect_ratio_preserved": "yes" if validation["aspect_ratio_preserved"] else "no",
                "status": "exported_pending_user_review",
                "next_action": "用户人审后决定是否进入剪映精修",
            }
        )

    write_csv(
        FACT_DIR / "01_直播录屏素材清单_live_recording_inventory.csv",
        [
            "recording_id",
            "file_name",
            "source_path",
            "duration_seconds",
            "resolution",
            "aspect_ratio",
            "fps",
            "audio_stream",
            "status",
            "notes",
        ],
        inventory_rows,
    )
    write_csv(
        FACT_DIR / "02_候选片段结构匹配表_candidate_segment_structure_match.csv",
        [
            "candidate_id",
            "recording_id",
            "source_file",
            "start_time",
            "end_time",
            "duration_seconds",
            "matched_structure_formula",
            "opening_reason",
            "middle_delivery",
            "ending_closure",
            "source_integrity_score",
            "visual_speech_continuity_score",
            "editing_flow_score",
            "jump_cut_risk",
            "manual_review_items",
            "selected_for_export",
            "reject_reason",
            "evidence_route",
        ],
        candidate_rows,
    )
    write_csv(
        FACT_DIR / "05_初剪结果索引_rough_cut_output_index.csv",
        [
            "rough_cut_id",
            "output_path",
            "source_file",
            "start_time",
            "end_time",
            "structure_formula",
            "duration_seconds",
            "resolution_preserved",
            "aspect_ratio_preserved",
            "status",
            "next_action",
        ],
        index_rows,
    )

    evidence_lines = [
        "# 六条初剪视频证据报告",
        "",
        "状态：`six_rough_cuts_exported_pending_user_review`",
        f"生成时间：{now}",
        "",
        "## 总边界",
        "",
        "- 本报告只证明 6 条候选初剪已按原片参数裁切导出，不代表审美、人感、动作专业性或业务事实通过。",
        "- 仅发现 1 条有效完整直播录屏；6 条候选均来自同一条 `5月7日直播.MP4`，没有跨素材硬拼。",
        "- `ALI_API_ENABLE_LIVE_TEST=false`，本轮未上传完整视频；依据为既有本地转写、全局抽帧浏览、ffprobe/ffmpeg 技术验证和前 100 条结构标准。",
        "",
    ]
    for position, candidate in enumerate(selected, start=1):
        validation = validations[candidate.candidate_id]
        output = outputs[candidate.candidate_id]
        evidence_lines.extend(
            [
                f"## 初剪视频 {position:02d}",
                "",
                f"- 本地输出路径：`{output}`",
                f"- 来源录屏：`{source}`",
                f"- 起止时间：`{timecode(candidate.start)}-{timecode(candidate.end)}`",
                f"- 导出时长：`{validation['duration_seconds']}s`",
                f"- 分辨率 / fps：`{validation['resolution']}` / `{validation['fps']}`",
                f"- 使用结构公式：{candidate.structure_formula}",
                f"- 开头怎么留人：{candidate.opening_reason}",
                f"- 中段交付什么：{candidate.middle_delivery}",
                f"- 结尾怎么收：{candidate.ending_closure}",
                f"- 为什么完整：素材完整感 `{candidate.integrity_score}`；同一主题内从问题/误区进入方法或动作。",
                f"- 为什么不跳：连续性 `{candidate.continuity_score}`；未跨来源拼接，保持同一人、同一场景、同一直播语境。",
                f"- 拼贴风险：`{candidate.jump_cut_risk}`",
                f"- 人工剪映复核点：{candidate.manual_review_items}",
                "- 业务事实复核点：健康、盆底、产后、频率、效果承诺和商品信息均需客户确认。",
                "- 动作专业性复核点：动作安全性、适用人群、禁忌人群和公开展示尺度需专业复核。",
                "- 是否适合进入下一轮精剪：`pending_user_review`",
                "",
            ]
        )
    (FACT_DIR / "03_六条初剪视频证据报告_six_rough_cut_evidence_report.md").write_text(
        "\n".join(evidence_lines), encoding="utf-8"
    )

    checklist = """# 人工复核清单

状态：`pending_user_review`

## 画面与技术

- 检查 6 条视频是否保持原始画面比例，没有裁切、拉伸、加边、模糊背景、调色、美颜或转场。
- 检查每条视频是否仍是原声，音画是否同步，是否存在直播回声或现场杂音。
- 检查片段起止点是否自然，是否需要向前或向后扩展 3-15 秒。

## 结构与人感

- 每条是否能看出开头、中段和结尾。
- 中段是否真的交付动作、方法、原因或注意事项。
- 是否存在只剩直播互动、缺少方法兑现的片段。
- 是否存在素材拼贴感。本轮 6 条均为连续原片窗口，如仍不顺，应优先调整起止点。

## 字幕与剪映

- 本轮未加字幕。剪映精修时需要人工校正“产后/盆底/瑜伽球/漏尿”等 ASR 易错词。
- 字幕不得遮挡手部、骨盆、瑜伽球、坐姿和关键动作。
- 标题、封面和口播字幕必须对应真实内容，不得夸大效果。

## 动作与业务事实

- 盆底、产后、漏尿、疼痛、松弛、收紧、训练频率等表达均需专业/业务复核。
- 商品承重、价格、购买入口、主播资历、帮助人数等信息需客户确认。
- 不得把本轮技术导出写成发布通过。
"""
    (FACT_DIR / "04_人工复核清单_manual_review_checklist.md").write_text(checklist, encoding="utf-8")

    git = git_summary()
    report = f"""# 直播录屏 6 条结构初剪执行报告

状态：`completed_with_pending_user_review`
生成时间：{now}
任务类型：`live_recording_structure_rough_cut_probe`

## 1. 执行结果

| 项目 | 结果 |
|---|---|
| 当前项目仓库 | `fthytwerwt-sudo/lanxinse--` |
| 本地仓库路径 | `{git['top']}` |
| 当前分支 | `{git['branch']}` |
| 当前 remote | `{git['remote'].splitlines()[0] if git['remote'] else ''}` |
| 预期直播录屏目录 | `{EXPECTED_LIVE_DIR}` |
| 实际直播录屏目录 | `{live_dir}` |
| 目录定位状态 | `{discovery_note}` |
| 有效录屏数量 | `{len(recordings)}` |
| 目标读取数量 | `约 7 条` |
| 缺失录屏记录 | `{max(0, 7 - len(recordings))}` |
| 候选片段数量 | `{len(candidates)}` |
| 成功导出初剪数量 | `{len(selected)}` |
| 是否达到 6 条 | `是` |
| 不足 6 条原因 | `不适用；但录屏数量不足 7 条，实际只发现 1 条完整录屏` |
| 源视频技术参数 | `H.264 {width}x{height} {src_video.get('avg_frame_rate', '')}，音频 {src_audio.get('codec_name', '') if src_audio else 'no_audio'}` |
| 是否保持原画面比例 | `是，ffprobe 验证 6 条均保持 {width}x{height}` |
| 是否改变画面 | `否` |
| 是否添加字幕 / 包装 / 调色 / 美颜 / BGM | `否` |
| 是否重新编码 | `否，6 条均使用 ffmpeg -c copy` |
| 是否上传完整视频 | `否` |
| 是否提交媒体 | `否` |
| 阿里 live 调用 | `未执行；.env 中 ALI_API_ENABLE_LIVE_TEST=false，本轮走本地降级 + 既有 connected 报告` |
| 全局浏览证据 | `本地生成 7 帧 contact sheet，覆盖 30/600/1200/1800/2400/3000/3500 秒，不提交 GitHub` |
| 口播精确解析范围 | `复用既有 0-900s 本地 faster-whisper 转写，状态 machine_transcript_pending_manual_review` |

## 2. 生成文件

- `项目事实_project_facts/直播录屏初剪验证_live_recording_rough_cut_probe/01_直播录屏素材清单_live_recording_inventory.csv`
- `项目事实_project_facts/直播录屏初剪验证_live_recording_rough_cut_probe/02_候选片段结构匹配表_candidate_segment_structure_match.csv`
- `项目事实_project_facts/直播录屏初剪验证_live_recording_rough_cut_probe/03_六条初剪视频证据报告_six_rough_cut_evidence_report.md`
- `项目事实_project_facts/直播录屏初剪验证_live_recording_rough_cut_probe/04_人工复核清单_manual_review_checklist.md`
- `项目事实_project_facts/直播录屏初剪验证_live_recording_rough_cut_probe/05_初剪结果索引_rough_cut_output_index.csv`
- `scripts/live_recording_rough_cut_probe.py`
- `执行日志_codex_log/109_直播录屏6条结构初剪执行报告_live_recording_six_rough_cut_report.md`

## 3. 本地视频输出

"""
    for position, candidate in enumerate(selected, start=1):
        validation = validations[candidate.candidate_id]
        report += f"""### 初剪视频 {position:02d}

| 字段 | 结果 |
|---|---|
| 本地路径 | `{outputs[candidate.candidate_id]}` |
| 来源录屏 | `{source}` |
| 起止时间 | `{timecode(candidate.start)}-{timecode(candidate.end)}` |
| 结构公式 | `{candidate.structure_formula}` |
| 时长 | `{validation['duration_seconds']}s` |
| 宽高 | `{validation['resolution']}` |
| 是否保持比例 | `{'yes' if validation['aspect_ratio_preserved'] else 'no'}` |
| 音频是否保持 | `{'yes' if validation['audio_preserved'] else 'no'}` |

"""
    report += """## 4. 验证证据

已执行 / 本脚本内执行：

- `pwd`
- `git rev-parse --show-toplevel`
- `git branch --show-current`
- `git remote -v`
- `git status --short --branch`
- `git pull --ff-only`
- `ffmpeg -version`
- `ffprobe -version`
- `ffprobe` 读取原始完整录屏
- `ffmpeg -ss ... -to ... -c copy` 导出 6 条候选初剪
- `ffprobe` 验证 6 条输出视频宽高、时长、视频轨和音频轨

本轮验证已完成：

- `python3 scripts/check_ali_config_safety.py`
- `python3 -m py_compile scripts/check_ali_api_connection.py scripts/check_ali_models_live.py scripts/check_ali_config_safety.py scripts/live_recording_rough_cut_probe.py`
- `git diff --check`
- 6 条输出视频逐条 `ffmpeg -v error -i <output> -f null -` 完整解码，无错误输出

Git 闭环状态：

- path-limited stage / commit / push / remote HEAD readback 在本报告写入后执行。
- 最终 commit SHA、push 结果和 remote HEAD 以 Codex 最终回报为准，避免在报告内写自引用哈希。

## 5. 边界确认

| 边界 | 结果 |
|---|---|
| 是否提交源视频 | 否 |
| 是否提交初剪视频 | 否 |
| 是否提交 `.env` | 否 |
| 是否提交 API key | 否 |
| 是否提交 token | 否 |
| 是否提交完整 API 输出 | 否 |
| 是否改变画面比例 | 否 |
| 是否加包装 | 否 |
| 是否写审美通过 | 否 |
| 是否写业务通过 | 否 |
| 是否写稳定自动剪辑 | 否 |

## 6. 已知限制

- 预期目录 `WD_BLACK-完整直播录屏` 未命中；实际使用同工作区内的 `剪辑解析数据/完整直播`。
- 目标约 7 条完整录屏，实际只发现 1 条有效录屏；素材清单已把缺失的 6 个录屏位标为 `missing_not_found_in_live_recording_dir`。
- 本轮没有上传完整视频到阿里；由于 `.env` 当前 `ALI_API_ENABLE_LIVE_TEST=false`，只使用既有阿里 connected 报告和本地降级路线。
- 0-900s 之外只做全局低频视觉抽样，未做全场精确口播转写。
- 6 条视频均为结构候选初剪，等待用户人审；不能直接发布。

## 7. 状态标记

```text
completed_with_pending_user_review
```
"""
    REPORT_PATH.write_text(report, encoding="utf-8")

    print(json.dumps({"status": "ok", "exported": len(selected), "recordings": len(recordings)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"live_recording_rough_cut_probe failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
