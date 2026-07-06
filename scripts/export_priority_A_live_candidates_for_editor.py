#!/usr/bin/env python3
"""Export priority A live-recording candidates into a local editor package."""

from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

A_LIST_CSV = REPO_ROOT / "项目事实_project_facts/直播素材筛选_live_material_screening/04_A类优先剪辑清单_priority_A_editor_pick_list.csv"
PAIRING_CSV = REPO_ROOT / "项目事实_project_facts/直播素材筛选_live_material_screening/02_口播动作配对表_speech_action_pairing_table.csv"
STRUCTURE_CSV = REPO_ROOT / "项目事实_project_facts/直播素材筛选_live_material_screening/03_按剪辑结构归类候选表_candidates_by_clip_structure.csv"
MASTER_CSV = REPO_ROOT / "项目事实_project_facts/直播素材筛选_live_material_screening/01_直播候选片段总表_live_candidate_segment_master.csv"

OUTPUT_ROOT = REPO_ROOT / "outputs/local_live_A_editor_package"
FACT_ROOT = REPO_ROOT / "项目事实_project_facts/直播素材筛选_live_material_screening"
ANALYSIS_ROOT = REPO_ROOT / "素材解析_pipeline_material_analysis/13_priority_A_editor_export"
LOG_ROOT = REPO_ROOT / "执行日志_codex_log"

MANIFEST_CSV = FACT_ROOT / "10_A类素材导出索引_A_class_export_manifest.csv"
PAIR_GUIDE_CSV = FACT_ROOT / "11_A类口播动作配对剪辑说明_A_class_pair_editing_guide.csv"
EDITOR_README_MD = FACT_ROOT / "12_A类剪辑师交付说明_A_class_editor_delivery_readme.md"
SECONDARY_NOTES_CSV = FACT_ROOT / "13_A类二次剪辑标注表_A_class_secondary_edit_notes.csv"
PROBE_CSV = ANALYSIS_ROOT / "01_A类导出探针_A_class_export_probe.csv"
VALIDATION_CSV = ANALYSIS_ROOT / "02_A类导出校验_A_class_export_validation.csv"
REPORT_MD = LOG_ROOT / "120_A类候选素材结构化导出执行报告_A_class_editor_export_report.md"

STRUCTURE_FOLDERS = {
    "误区/错误先抛 + 正确动作对比 + 原因解释": "01_误区错误纠正_错误动作正确动作原因解释",
    "问题问答 + 原因解释 + 方法边界": "02_问题问答_原因解释方法边界",
    "痛点/人群点名 + 单动作完整循环 + 坚持建议": "03_痛点人群点名_单动作完整循环坚持建议",
    "工具/动作演示 + 发力口令 + 低压跟练收束": "04_工具动作演示_发力口令低压跟练收束",
    "多动作组合 + 同一主题推进 + 轻跟练收束": "05_多动作组合_同一主题推进轻跟练收束",
    "结果前置 + 操作过程 + 注意事项/风险边界": "06_结果前置_操作过程注意事项风险边界",
    "痛点/结果可视化 + 操作过程证据 + 低压行动": "06_结果前置_操作过程注意事项风险边界",
}

ALL_STRUCTURE_DIRS = [
    "01_误区错误纠正_错误动作正确动作原因解释",
    "02_问题问答_原因解释方法边界",
    "03_痛点人群点名_单动作完整循环坚持建议",
    "04_工具动作演示_发力口令低压跟练收束",
    "05_多动作组合_同一主题推进轻跟练收束",
    "06_结果前置_操作过程注意事项风险边界",
    "07_待视觉复核_主题不明",
]

SPLIT_STATUS = "not_available_from_pair_table_same_time_range"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def abs_s(path: Path) -> str:
    return str(path.resolve())


def slug(value: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "_", value.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unknown"


def hms_to_seconds(value: str) -> float:
    parts = value.strip().split(":")
    if len(parts) != 3:
        raise ValueError(f"bad time value: {value}")
    hours, minutes, seconds = parts
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def seconds_text(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def ffprobe_json(path: Path) -> dict[str, Any]:
    proc = run([
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ])
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return json.loads(proc.stdout)


def media_probe(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "probe_status": "failed",
            "probe_note": "file_missing",
            "duration_seconds": "",
            "has_video": False,
            "has_audio": False,
            "width": "",
            "height": "",
            "video_codec": "",
            "audio_codec": "",
        }
    try:
        data = ffprobe_json(path)
    except Exception as exc:  # noqa: BLE001 - report exact ffprobe failure in CSV.
        return {
            "exists": True,
            "probe_status": "failed",
            "probe_note": str(exc),
            "duration_seconds": "",
            "has_video": False,
            "has_audio": False,
            "width": "",
            "height": "",
            "video_codec": "",
            "audio_codec": "",
        }
    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
    duration = data.get("format", {}).get("duration") or video_stream.get("duration") or ""
    try:
        duration_out = f"{float(duration):.3f}" if duration != "" else ""
    except ValueError:
        duration_out = ""
    return {
        "exists": True,
        "probe_status": "success",
        "probe_note": "ok",
        "duration_seconds": duration_out,
        "has_video": bool(video_stream),
        "has_audio": bool(audio_stream),
        "width": video_stream.get("width", ""),
        "height": video_stream.get("height", ""),
        "video_codec": video_stream.get("codec_name", ""),
        "audio_codec": audio_stream.get("codec_name", ""),
    }


def decode_check(path: Path) -> tuple[str, str]:
    proc = run(["ffmpeg", "-v", "error", "-t", "0.8", "-i", str(path), "-f", "null", "-"])
    if proc.returncode == 0:
        return "success", "ok"
    return "failed", (proc.stderr.strip() or proc.stdout.strip() or "ffmpeg_decode_failed")[:500]


def git_check_ignore(path: Path) -> str:
    proc = run(["git", "check-ignore", "-q", rel(path)])
    return "ignored" if proc.returncode == 0 else "not_ignored"


def structure_folder(name: str) -> str:
    if name in STRUCTURE_FOLDERS:
        return STRUCTURE_FOLDERS[name]
    if "结果" in name or "风险边界" in name:
        return "06_结果前置_操作过程注意事项风险边界"
    return "07_待视觉复核_主题不明"


def build_pair_index(pair_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for row in pair_rows:
        for key in ("talk_segment_id", "action_segment_id"):
            candidate_id = row.get(key, "")
            if candidate_id and candidate_id not in index:
                index[candidate_id] = row
    return index


def export_clip(source: Path, start_time: str, duration_seconds: float, output: Path) -> tuple[str, str]:
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(output.stem + ".__tmp__.mp4")
    for candidate in (tmp, output):
        if candidate.exists():
            candidate.unlink()

    common = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", start_time, "-t", seconds_text(duration_seconds), "-i", str(source)]
    copy_cmd = common + ["-map", "0:v:0", "-map", "0:a?", "-c", "copy", "-movflags", "+faststart", str(tmp)]
    copy_proc = run(copy_cmd)
    if copy_proc.returncode == 0:
        probe = media_probe(tmp)
        decode_status, decode_note = decode_check(tmp)
        if probe["probe_status"] == "success" and probe["has_video"] and decode_status == "success":
            tmp.replace(output)
            return "stream_copy", "ok"
        tmp.unlink(missing_ok=True)

    transcode_cmd = common + [
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-movflags",
        "+faststart",
        str(tmp),
    ]
    transcode_proc = run(transcode_cmd)
    if transcode_proc.returncode != 0:
        tmp.unlink(missing_ok=True)
        note = transcode_proc.stderr.strip() or copy_proc.stderr.strip() or "ffmpeg_export_failed"
        return "failed", note[:800]
    tmp.replace(output)
    return "transcode_fallback", "copy_failed_then_transcoded"


def local_group_readme(row: dict[str, str], pair: dict[str, str], output_file: Path, split_status: str) -> str:
    return f"""# A 类候选素材剪辑说明

- candidate_id: {row.get("candidate_id", "")}
- pair_group_id: {pair.get("pair_group_id", "missing_pair")}
- recording_id: {row.get("recording_id", "")}
- usable_structure_name: {row.get("usable_structure_name", "")}
- clip_value_type: {row.get("clip_value_type", "")}
- source_file: {row.get("source_file", "")}
- source_range: {row.get("start_time", "")} -> {row.get("end_time", "")}
- local_full_context: {output_file.name}
- front_back_split_status: {split_status}
- pair_relation: {pair.get("pair_relation", "")}
- editor_sequence_advice: {pair.get("editor_sequence_advice", "")}

## 口播摘要

{row.get("speech_summary", "")}

## 动作摘要

{row.get("action_summary", "")}

## 剪辑动作

{row.get("recommended_editor_action", "")}

## 必须人工复核

{row.get("manual_review_items", "")}

## 边界

本文件夹是 A 类候选素材包，不代表已通过健康、业务、动作规范、审美或发布验收。
配对表中口播段和动作段时间范围相同，因此本轮只导出完整上下文，不额外生成重复的前段/后段文件。
"""


def local_root_readme(counts: Counter[str], total: int) -> str:
    structure_lines = "\n".join(f"- {folder}: {counts.get(folder, 0)} 条" for folder in ALL_STRUCTURE_DIRS)
    return f"""# A 类直播候选素材本地交付包

- generated_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- package_path: {abs_s(OUTPUT_ROOT)}
- total_A_candidates: {total}
- export_mode: full_context_only
- front_back_split_status: {SPLIT_STATUS}

## 分组

{structure_lines}

## 使用方式

每个候选文件夹内包含 `03_完整上下文_full_context.mp4` 和 `00_本组剪辑说明.md`。
剪辑师先按结构文件夹进入，再按 `A序号_candidate_id_pair_group_id_recording_id` 定位素材。

## 边界

本包只完成候选素材导出和机器级技术校验，不代表内容已通过人工听审、视觉动作复核、健康/业务/客户审核、审美包装或发布验收。
"""


def structure_readme(folder: str, count: int) -> str:
    return f"""# {folder}

- candidate_count: {count}
- export_mode: full_context_only
- front_back_split_status: {SPLIT_STATUS}

本结构分组只表示上轮筛选的文本结构归类，仍需剪辑师人工听审、看原片和做二次包装判断。
"""


def clean_appledouble_files(root: Path) -> int:
    removed = 0
    for path in root.rglob("._*"):
        if path.is_file():
            path.unlink()
            removed += 1
    return removed


def editor_repo_readme(total: int, counts: Counter[str], failed: int) -> str:
    structure_lines = "\n".join(f"- {folder}: {counts.get(folder, 0)} 条" for folder in ALL_STRUCTURE_DIRS)
    return f"""# A 类剪辑师交付说明

已确认：本轮按上轮筛出的 A 类候选清单导出本地剪辑素材包。

- 本地素材包：`{abs_s(OUTPUT_ROOT)}`
- A 类候选数：{total}
- 导出失败数：{failed}
- 导出方式：每条候选导出 `03_完整上下文_full_context.mp4`
- 前后段拆分：`{SPLIT_STATUS}`，原因是配对表中口播段与动作段时间范围完全一致，拆分会制造重复文件并误导剪辑师。

## 结构分组

{structure_lines}

## 配套表

- `10_A类素材导出索引_A_class_export_manifest.csv`：候选到本地 mp4 的总索引。
- `11_A类口播动作配对剪辑说明_A_class_pair_editing_guide.csv`：口播/动作配对和剪辑顺序说明。
- `13_A类二次剪辑标注表_A_class_secondary_edit_notes.csv`：剪辑师复核和二次加工记录空表。
- `素材解析_pipeline_material_analysis/13_priority_A_editor_export/02_A类导出校验_A_class_export_validation.csv`：ffprobe/短解码校验结果。

## 未完成边界

本轮不代表健康/业务审核通过，不代表动作规范通过，不代表审美包装通过，不代表可发布。
"""


def report_text(
    total: int,
    counts: Counter[str],
    source_count: int,
    exported: int,
    failed: int,
    validation_success: int,
    validation_failed: int,
    probe_rows: list[dict[str, Any]],
) -> str:
    structure_lines = "\n".join(f"- {folder}: {counts.get(folder, 0)}" for folder in ALL_STRUCTURE_DIRS)
    failed_text = "无" if failed == 0 and validation_failed == 0 else "详见 02_A类导出校验_A_class_export_validation.csv"
    probe_lines = "\n".join(f"- {r['check_item']}: {r['status']} ({r['value']})" for r in probe_rows)
    return f"""# 120 A 类候选素材结构化导出执行报告

## 主结论

已确认：本轮没有重新筛选、没有重新 ASR、没有重建动作知识库；只基于上轮 A 类清单导出剪辑师本地素材包。

- 本地成片/素材包地址：`{abs_s(OUTPUT_ROOT)}`
- A 类候选总数：{total}
- 来源直播录屏数：{source_count}
- 实际导出 mp4 数：{exported}
- 导出失败数：{failed}
- 技术校验成功数：{validation_success}
- 技术校验失败数：{validation_failed}
- 前后段拆分状态：`{SPLIT_STATUS}`

## 结构分组

{structure_lines}

## 探针结果

{probe_lines}

## 生成文件

- `scripts/export_priority_A_live_candidates_for_editor.py`
- `项目事实_project_facts/直播素材筛选_live_material_screening/10_A类素材导出索引_A_class_export_manifest.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/11_A类口播动作配对剪辑说明_A_class_pair_editing_guide.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/12_A类剪辑师交付说明_A_class_editor_delivery_readme.md`
- `项目事实_project_facts/直播素材筛选_live_material_screening/13_A类二次剪辑标注表_A_class_secondary_edit_notes.csv`
- `素材解析_pipeline_material_analysis/13_priority_A_editor_export/01_A类导出探针_A_class_export_probe.csv`
- `素材解析_pipeline_material_analysis/13_priority_A_editor_export/02_A类导出校验_A_class_export_validation.csv`

## 失败项

{failed_text}

## 边界说明

本轮只完成本地素材导出与技术校验。A 类表示“优先给剪辑师处理的候选素材”，不等于健康审核通过、动作规范通过、业务通过、审美包装通过或发布可用。

## 媒体入库规则

`outputs/local_live_A_editor_package/` 已加入 `.gitignore`，本轮 mp4 和本地包说明不进入 Git；Git 只提交脚本、索引、说明、校验表和执行报告。
"""


def main() -> int:
    for path in (A_LIST_CSV, PAIRING_CSV, STRUCTURE_CSV, MASTER_CSV):
        if not path.exists():
            raise FileNotFoundError(path)

    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if not ffmpeg_path or not ffprobe_path:
        raise RuntimeError("ffmpeg and ffprobe are required")

    a_rows = read_csv(A_LIST_CSV)
    pair_rows = read_csv(PAIRING_CSV)
    structure_rows = read_csv(STRUCTURE_CSV)
    master_rows = read_csv(MASTER_CSV)
    pair_index = build_pair_index(pair_rows)

    if not a_rows:
        raise RuntimeError("A candidate list is empty")
    not_a = [row.get("candidate_id", "") for row in a_rows if row.get("stage1_priority") != "A"]
    if not_a:
        raise RuntimeError(f"non-A rows found in A list: {not_a[:5]}")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for folder in ALL_STRUCTURE_DIRS:
        (OUTPUT_ROOT / folder).mkdir(parents=True, exist_ok=True)

    sources = sorted({row.get("source_file", "") for row in a_rows})
    source_probes: dict[str, dict[str, Any]] = {}
    source_missing = []
    for source in sources:
        path = Path(source)
        if not path.exists():
            source_missing.append(source)
        source_probes[source] = media_probe(path)
    if source_missing:
        raise FileNotFoundError(f"source videos missing: {source_missing}")

    split_usable = 0
    for row in a_rows:
        pair = pair_index.get(row.get("candidate_id", ""), {})
        if not pair:
            continue
        talk_range = (pair.get("talk_start_time", ""), pair.get("talk_end_time", ""))
        action_range = (pair.get("action_start_time", ""), pair.get("action_end_time", ""))
        if talk_range != action_range and all(talk_range + action_range):
            split_usable += 1

    disk = shutil.disk_usage(OUTPUT_ROOT)
    output_ignore_status = git_check_ignore(OUTPUT_ROOT / "__probe__.mp4")
    probe_rows: list[dict[str, Any]] = [
        {"check_item": "a_candidate_rows", "value": len(a_rows), "status": "pass", "note": str(A_LIST_CSV)},
        {"check_item": "pair_rows", "value": len(pair_rows), "status": "pass", "note": str(PAIRING_CSV)},
        {"check_item": "structure_rows", "value": len(structure_rows), "status": "pass", "note": str(STRUCTURE_CSV)},
        {"check_item": "master_rows", "value": len(master_rows), "status": "pass", "note": str(MASTER_CSV)},
        {"check_item": "source_video_count", "value": len(sources), "status": "pass", "note": "all source files exist"},
        {"check_item": "ffmpeg_path", "value": ffmpeg_path, "status": "pass", "note": "found"},
        {"check_item": "ffprobe_path", "value": ffprobe_path, "status": "pass", "note": "found"},
        {"check_item": "disk_available_gib", "value": f"{disk.free / (1024 ** 3):.2f}", "status": "pass", "note": abs_s(OUTPUT_ROOT)},
        {"check_item": "front_back_split_usable_count", "value": split_usable, "status": "pass", "note": SPLIT_STATUS},
        {"check_item": "output_ignore_status", "value": output_ignore_status, "status": "pass" if output_ignore_status == "ignored" else "fail", "note": rel(OUTPUT_ROOT)},
    ]
    for source, probe in source_probes.items():
        probe_rows.append({
            "check_item": "source_probe",
            "value": probe.get("duration_seconds", ""),
            "status": "pass" if probe.get("probe_status") == "success" and probe.get("has_video") else "fail",
            "note": source,
        })

    write_csv(PROBE_CSV, probe_rows, ["check_item", "value", "status", "note"])
    if any(row["status"] == "fail" for row in probe_rows):
        raise RuntimeError("probe failed; see probe CSV")

    manifest_rows: list[dict[str, Any]] = []
    guide_rows: list[dict[str, Any]] = []
    secondary_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    structure_counts: Counter[str] = Counter()

    print(f"Exporting {len(a_rows)} A candidates to {OUTPUT_ROOT}")
    for index, row in enumerate(a_rows, start=1):
        candidate_id = row.get("candidate_id", "")
        pair = pair_index.get(candidate_id, {})
        pair_group_id = pair.get("pair_group_id", "missing_pair")
        folder = structure_folder(row.get("usable_structure_name", ""))
        structure_counts[folder] += 1
        candidate_folder = OUTPUT_ROOT / folder / f"A{index:03d}_{slug(candidate_id)}_{slug(pair_group_id)}_{slug(row.get('recording_id', ''))}"
        full_context = candidate_folder / "03_完整上下文_full_context.mp4"
        group_readme = candidate_folder / "00_本组剪辑说明.md"

        start = row.get("start_time", "")
        try:
            duration = float(row.get("duration_seconds", "") or (hms_to_seconds(row.get("end_time", "")) - hms_to_seconds(start)))
        except ValueError:
            duration = hms_to_seconds(row.get("end_time", "")) - hms_to_seconds(start)
        source = Path(row.get("source_file", ""))

        export_method, export_note = export_clip(source, start, duration, full_context)
        probe = media_probe(full_context)
        decode_status, decode_note = decode_check(full_context) if probe.get("probe_status") == "success" else ("failed", "probe_failed")
        try:
            probed_duration = float(probe.get("duration_seconds") or 0.0)
        except ValueError:
            probed_duration = 0.0
        duration_delta = abs(probed_duration - duration) if probed_duration else ""
        duration_ok = bool(probed_duration) and abs(probed_duration - duration) <= 2.5
        validation_status = (
            "success"
            if export_method != "failed" and probe.get("probe_status") == "success" and probe.get("has_video") and decode_status == "success" and duration_ok
            else "failed"
        )
        validation_note = "ok" if validation_status == "success" else f"export={export_note}; probe={probe.get('probe_note')}; decode={decode_note}"

        write_text(group_readme, local_group_readme(row, pair, full_context, SPLIT_STATUS))

        manifest_rows.append({
            "export_id": f"A{index:03d}",
            "candidate_id": candidate_id,
            "pair_group_id": pair_group_id,
            "recording_id": row.get("recording_id", ""),
            "usable_structure_name": row.get("usable_structure_name", ""),
            "structure_folder": folder,
            "candidate_folder": abs_s(candidate_folder),
            "source_file": row.get("source_file", ""),
            "start_time": start,
            "end_time": row.get("end_time", ""),
            "duration_seconds": row.get("duration_seconds", ""),
            "full_context_path": abs_s(full_context),
            "full_context_relpath": rel(full_context),
            "full_context_exists": str(full_context.exists()).lower(),
            "full_context_probe_status": probe.get("probe_status", ""),
            "full_context_duration_seconds": probe.get("duration_seconds", ""),
            "width": probe.get("width", ""),
            "height": probe.get("height", ""),
            "video_codec": probe.get("video_codec", ""),
            "audio_codec": probe.get("audio_codec", ""),
            "export_method": export_method,
            "front_clip_path": "",
            "action_clip_path": "",
            "front_back_split_status": SPLIT_STATUS,
            "clip_value_type": row.get("clip_value_type", ""),
            "recommended_editor_action": row.get("recommended_editor_action", ""),
            "manual_review_items": row.get("manual_review_items", ""),
            "status": "exported_pending_manual_review" if validation_status == "success" else "export_validation_failed",
        })

        guide_rows.append({
            "candidate_id": candidate_id,
            "pair_group_id": pair_group_id,
            "recording_id": row.get("recording_id", ""),
            "usable_structure_name": row.get("usable_structure_name", ""),
            "pair_relation": pair.get("pair_relation", ""),
            "talk_start_time": pair.get("talk_start_time", ""),
            "talk_end_time": pair.get("talk_end_time", ""),
            "talk_function": pair.get("talk_function", ""),
            "action_start_time": pair.get("action_start_time", ""),
            "action_end_time": pair.get("action_end_time", ""),
            "action_function": pair.get("action_function", ""),
            "target_problem": pair.get("target_problem", row.get("problem_category_id", "")),
            "why_pair": pair.get("why_pair", ""),
            "editor_sequence_advice": pair.get("editor_sequence_advice", ""),
            "front_back_split_status": SPLIT_STATUS,
            "editor_first_step": "先看完整上下文，人工确认主问题、动作完整循环和可剪切点。",
            "editor_note": "不做前后段自动拆分；如人工确认口播和动作确实分离，再由剪辑师在 full_context 内二次切点。",
        })

        secondary_rows.append({
            "export_id": f"A{index:03d}",
            "candidate_id": candidate_id,
            "pair_group_id": pair_group_id,
            "recording_id": row.get("recording_id", ""),
            "local_full_context_path": abs_s(full_context),
            "secondary_review_status": "pending_editor_review",
            "asr_correction_needed": "yes",
            "visual_action_cycle_needed": "yes",
            "health_business_customer_review_needed": "yes",
            "subtitle_packaging_needed": "pending",
            "risk_note": row.get("manual_review_items", ""),
            "reviewer_note": "",
            "decision": "",
        })

        validation_rows.append({
            "export_id": f"A{index:03d}",
            "candidate_id": candidate_id,
            "pair_group_id": pair_group_id,
            "output_path": abs_s(full_context),
            "expected_duration_seconds": f"{duration:.3f}",
            "ffprobe_duration_seconds": probe.get("duration_seconds", ""),
            "duration_delta_seconds": f"{duration_delta:.3f}" if isinstance(duration_delta, float) else "",
            "has_video": str(bool(probe.get("has_video"))).lower(),
            "has_audio": str(bool(probe.get("has_audio"))).lower(),
            "width": probe.get("width", ""),
            "height": probe.get("height", ""),
            "decode_check": decode_status,
            "export_method": export_method,
            "validation_status": validation_status,
            "validation_note": validation_note[:1000],
        })

        if index % 10 == 0 or index == len(a_rows):
            print(f"  exported {index}/{len(a_rows)}")

    for folder in ALL_STRUCTURE_DIRS:
        write_text(OUTPUT_ROOT / folder / "00_结构分组说明.md", structure_readme(folder, structure_counts.get(folder, 0)))
    write_text(OUTPUT_ROOT / "00_交付说明_editor_package_readme.md", local_root_readme(structure_counts, len(a_rows)))

    manifest_fields = [
        "export_id",
        "candidate_id",
        "pair_group_id",
        "recording_id",
        "usable_structure_name",
        "structure_folder",
        "candidate_folder",
        "source_file",
        "start_time",
        "end_time",
        "duration_seconds",
        "full_context_path",
        "full_context_relpath",
        "full_context_exists",
        "full_context_probe_status",
        "full_context_duration_seconds",
        "width",
        "height",
        "video_codec",
        "audio_codec",
        "export_method",
        "front_clip_path",
        "action_clip_path",
        "front_back_split_status",
        "clip_value_type",
        "recommended_editor_action",
        "manual_review_items",
        "status",
    ]
    guide_fields = [
        "candidate_id",
        "pair_group_id",
        "recording_id",
        "usable_structure_name",
        "pair_relation",
        "talk_start_time",
        "talk_end_time",
        "talk_function",
        "action_start_time",
        "action_end_time",
        "action_function",
        "target_problem",
        "why_pair",
        "editor_sequence_advice",
        "front_back_split_status",
        "editor_first_step",
        "editor_note",
    ]
    secondary_fields = [
        "export_id",
        "candidate_id",
        "pair_group_id",
        "recording_id",
        "local_full_context_path",
        "secondary_review_status",
        "asr_correction_needed",
        "visual_action_cycle_needed",
        "health_business_customer_review_needed",
        "subtitle_packaging_needed",
        "risk_note",
        "reviewer_note",
        "decision",
    ]
    validation_fields = [
        "export_id",
        "candidate_id",
        "pair_group_id",
        "output_path",
        "expected_duration_seconds",
        "ffprobe_duration_seconds",
        "duration_delta_seconds",
        "has_video",
        "has_audio",
        "width",
        "height",
        "decode_check",
        "export_method",
        "validation_status",
        "validation_note",
    ]

    write_csv(MANIFEST_CSV, manifest_rows, manifest_fields)
    write_csv(PAIR_GUIDE_CSV, guide_rows, guide_fields)
    write_csv(SECONDARY_NOTES_CSV, secondary_rows, secondary_fields)
    write_csv(VALIDATION_CSV, validation_rows, validation_fields)

    failed = sum(1 for row in manifest_rows if row["status"] == "export_validation_failed")
    validation_success = sum(1 for row in validation_rows if row["validation_status"] == "success")
    validation_failed = len(validation_rows) - validation_success
    write_text(EDITOR_README_MD, editor_repo_readme(len(a_rows), structure_counts, failed))
    write_text(
        REPORT_MD,
        report_text(
            total=len(a_rows),
            counts=structure_counts,
            source_count=len(sources),
            exported=sum(1 for row in manifest_rows if row["full_context_exists"] == "true"),
            failed=failed,
            validation_success=validation_success,
            validation_failed=validation_failed,
            probe_rows=probe_rows,
        ),
    )
    removed_appledouble = clean_appledouble_files(OUTPUT_ROOT)
    if removed_appledouble:
        print(f"Removed {removed_appledouble} AppleDouble metadata files from output package.")

    if failed or validation_failed:
        print(f"Completed with validation failures: export_failed={failed}, validation_failed={validation_failed}")
        return 2
    print(f"Completed: {len(a_rows)} clips exported and validated.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # noqa: BLE001 - show top-level task failure.
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
